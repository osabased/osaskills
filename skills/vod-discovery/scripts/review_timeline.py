"""Build a Premiere discovery timeline from factual markers and local POV anchors.

The ordered main sources stay complete, cut and labeled at moment boundaries.
Alternate excerpts are disabled by
default, without retiming. The plan is authored from reviewed evidence, not
inferred automatically from marker boundaries.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as ET

from premiere_xml import build_xml, element, frame_rate, organize_project, rate
from vod import export_events, number, probe, read, text


MOMENT_LABEL = 'Mango'
FOOTAGE_LABEL = 'Iris'


def main_segments(master):
    """Partition a source once at every validated, frame-quantized marker edge.

    Count active ranges so overlapping/nested moments retain every boundary
    without duplicating footage. Unmarked intervals remain ordinary footage;
    they are not asserted to be reviewed or uninteresting.
    """
    changes = {0: 0, int(master.findtext('duration')): 0}
    for marker in master.findall('marker'):
        start, end = int(marker.findtext('in')), int(marker.findtext('out'))
        changes[start] = changes.get(start, 0) + 1
        changes[end] = changes.get(end, 0) - 1
    boundaries = sorted(changes)
    active = 0
    for start, end in zip(boundaries, boundaries[1:]):
        active += changes[start]
        yield start, end, MOMENT_LABEL if active else FOOTAGE_LABEL


def build_review(markers, probes, plan):
    root = ET.fromstring(build_xml(markers, probes, plan['title'], organize=False))
    children = root.find('./project/children')
    sources = {s['id']: s for s in markers['sources']}
    masters = dict(zip(sources, children.findall('clip')))
    mains = plan['main_sources']
    if not mains or len(set(mains)) != len(mains) or any(s not in sources for s in mains):
        raise ValueError('Main sources must be a nonempty ordered list of unique source IDs')
    first = masters[mains[0]]
    first_video = next(s for s in probes[mains[0]]['streams'] if s['codec_type'] == 'video')
    base, ntsc, fps = frame_rate(first_video)
    frame = lambda x: round(Fraction(str(x)) * fps)
    origins, cursor = {}, 0
    for sid in mains:
        video = next(s for s in probes[sid]['streams'] if s['codec_type'] == 'video')
        if frame_rate(video)[2] != fps:
            raise ValueError('Main parts must have the same nominal frame rate')
        origins[sid] = cursor
        cursor += int(masters[sid].findtext('duration'))
    sequence = element(children, 'sequence', id='vod-review-sequence', explodedTracks='true')
    element(sequence, 'name', text(plan['title'], 'timeline title'))
    element(sequence, 'duration', cursor)
    rate(sequence, base, ntsc)
    media = element(sequence, 'media')
    video = element(media, 'video')
    fmt = element(video, 'format')
    fmt.append(deepcopy(first.find('./media/video/track/clipitem/file/media/video/samplecharacteristics')))
    audio = element(media, 'audio')
    element(audio, 'numOutputChannels', 2)
    ac = element(element(audio, 'format'), 'samplecharacteristics')
    element(ac, 'depth', 16)
    element(ac, 'samplerate', 48000)
    entries = []
    for sid in mains:
        for start, end, label in main_segments(masters[sid]):
            entries.append(dict(source_id=sid, source_in=start, source_out=end,
                                start=origins[sid]+start, end=origins[sid]+end,
                                layer=0, enabled=True, label=label,
                                name=Path(sources[sid]['path']).name))
    alternative_sources = []
    occupied = {}
    for alt in plan.get('alternates', []):
        sid, main = alt['source_id'], alt['main_source_id']
        if sid not in sources or sid in mains or main not in origins:
            raise ValueError('Alternate must reference an alternate source and an ordered main source')
        start = number(alt['source_start_sec'], 'alternate source start')
        end = number(alt['source_end_sec'], 'alternate source end')
        anchor = number(alt['source_anchor_sec'], 'alternate anchor')
        main_anchor = number(alt['main_anchor_sec'], 'main anchor')
        uncertainty = number(alt['uncertainty_sec'], 'alignment uncertainty')
        text(alt['evidence'], 'local anchor evidence')
        if not 0 <= start <= anchor < end <= sources[sid]['duration_sec']:
            raise ValueError('Alternate range or local anchor is outside source')
        if main_anchor >= sources[main]['duration_sec']:
            raise ValueError('Main anchor is outside source')
        # Only a local translation: never stretch to fit two approximate boundaries.
        offset = Fraction(str(main_anchor)) - Fraction(str(anchor))
        timeline_start = origins[main] + frame(Fraction(str(start)) + offset)
        timeline_end = origins[main] + frame(Fraction(str(end)) + offset)
        main_end = origins[main] + int(masters[main].findtext('duration'))
        if not origins[main] <= timeline_start < timeline_end <= main_end:
            raise ValueError('Alternate placement exceeds its main part')
        if sid not in alternative_sources:
            alternative_sources.append(sid)
        layer = alternative_sources.index(sid) + 1
        for a, b in occupied.setdefault(layer, []):
            if timeline_start < b and timeline_end > a:
                raise ValueError('Alternate excerpts overlap; merge or trim their source ranges explicitly')
        occupied[layer].append((timeline_start, timeline_end))
        # Premiere reads sequence clipitem In/Out in the sequence frame rate,
        # including mixed-rate sources. The master/file retains its native rate.
        entries.append(dict(source_id=sid, source_in=frame(start),
                            source_out=frame(end),
                            start=timeline_start, end=timeline_end, layer=layer, enabled=False,
                            label=MOMENT_LABEL,
                            name=f"{text(alt['name'], 'alternate name')} | sync +/-{uncertainty:g}s"))
    vtracks, atracks, audio_indices = {}, {}, {}
    audio_track_count = 0
    for layer in range(len(alternative_sources) + 1):
        vtracks[layer] = element(video, 'track')
        layer_entries = [e for e in entries if e['layer'] == layer]
        counts = {len(masters[e['source_id']].findall('./media/audio/track')) for e in layer_entries}
        if len(counts) != 1:
            raise ValueError('Parts on one timeline layer must share an audio channel layout')
        channels = counts.pop()
        atracks[layer] = []
        for channel in range(channels):
            track = element(audio, 'track', currentExplodedTrackIndex=str(channel),
                            totalExplodedTrackCount=str(channels),
                            premiereTrackType='Stereo' if channels == 2 else 'Mono')
            atracks[layer].append(track)
        audio_indices[layer] = audio_track_count
        audio_track_count += channels
    clip_counts = {}
    for index, entry in enumerate(sorted(entries, key=lambda e:(e['layer'],e['start']))):
        sid, layer = entry['source_id'], entry['layer']
        master = masters[sid]
        clip_counts[layer] = clip_counts.get(layer, 0) + 1
        items = []
        for kind, tracks in [('video', [vtracks[layer]]), ('audio', atracks[layer])]:
            for channel, track in enumerate(tracks, 1):
                template = master.findall(f'./media/{kind}/track/clipitem')[channel-1]
                item = deepcopy(template)
                item.set('id', f'review-{index}-{kind}-{channel}')
                for link in list(item.findall('link')):
                    item.remove(link)
                item.find('name').text = entry['name']
                item.find('enabled').text = str(entry['enabled']).upper()
                item.find('in').text = str(entry['source_in'])
                item.find('out').text = str(entry['source_out'])
                item.find('duration').text = str(frame(sources[sid]['duration_sec']))
                item.find('rate/timebase').text = str(base)
                item.find('rate/ntsc').text = str(ntsc).upper()
                element(item, 'start', entry['start'])
                element(item, 'end', entry['end'])
                # Per-instance labels: never recolor the shared source master.
                element(element(item, 'labels'), 'label2', entry['label'])
                # The master owns the complete file declaration and source markers.
                file = item.find('file')
                fileid = file.get('id')
                file.clear()
                file.set('id', fileid)
                track.append(item)
                track_index = layer + 1 if kind == 'video' else audio_indices[layer] + channel
                items.append((item, kind, track_index))
        for item, _, _ in items:
            for other, kind, track_index in items:
                link = element(item, 'link')
                element(link, 'linkclipref', other.get('id'))
                element(link, 'mediatype', kind)
                element(link, 'trackindex', track_index)
                element(link, 'clipindex', clip_counts[layer])
                if kind == 'audio':
                    element(link, 'groupindex', 1)
    # A short sequence marker communicates the bounded review without labelling
    # the uninspected remainder as empty or suggesting it has been reviewed.
    if plan.get('coverage_note'):
        marker = element(sequence, 'marker')
        element(marker, 'name', 'Review coverage')
        element(marker, 'comment', text(plan['coverage_note'], 'coverage note'))
        element(marker, 'in', 0)
        element(marker, 'out', 1)
    organize_project(root, markers['sources'])
    ET.indent(root)
    return '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE xmeml>\n'+ET.tostring(root,encoding='unicode')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    data, plan = read(args.events), read(args.plan)
    markers = export_events(data)
    # Full main parts with no reviewed events are still required in the timeline.
    present = {s['id'] for s in markers['sources']}
    for source in data['sources']:
        if source['id'] in plan['main_sources'] and source['id'] not in present:
            markers['sources'].append(dict(source, markers=[]))
    probes = {}
    for source in markers['sources']:
        metadata, duration = probe(Path(source['path']).resolve(strict=True))
        if abs(duration-source['duration_sec']) > .1:
            raise ValueError('Source duration changed; review source mapping')
        probes[source['id']] = metadata
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_review(markers, probes, plan), encoding='utf-8')
    print(f'Wrote {out}; {len(plan["alternates"])} disabled alternate excerpts')


if __name__ == '__main__':
    main()
