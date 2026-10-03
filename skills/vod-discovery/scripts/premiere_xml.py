"""Export validated discoveries as new Premiere source clips via FCP7 XML.

This creates new project items. It does not update existing clips or deduplicate
imports. Source times are quantized to the nearest nominal source frame.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

from vod import export_events, probe, read, text, validate_marker_presentation


def element(parent, tag, value=None, **attrs):
    child = ET.SubElement(parent, tag, attrs)
    if value is not None:
        child.text = str(value)
    return child


def frame_rate(stream):
    fps = Fraction(stream['r_frame_rate'])
    for base in (24, 25, 30, 48, 50, 60, 120):
        for ntsc in (False, True):
            candidate = Fraction(base * 1000, 1001) if ntsc else Fraction(base)
            if fps == candidate:
                return base, ntsc, fps
    raise ValueError(f'Unsupported nominal rate {fps}; use the marker panel or validate another rate')


def rate(parent, base, ntsc):
    r = element(parent, 'rate')
    element(r, 'timebase', base)
    element(r, 'ntsc', str(ntsc).upper())


def media_url(path):
    # Match Premiere's own FCP XML export. Bare file:///C:/ was interpreted as
    # a UNC path; adjacent pilot files masked the fault through auto-relinking.
    if path.drive and not path.drive.startswith('\\\\'):
        return 'file://localhost/' + quote(path.as_posix(), safe='/').replace('%3A', '%3a')
    return path.as_uri()


def bin_children(parent, name, bin_id):
    folder = element(parent, 'bin', id=bin_id)
    element(folder, 'name', name)
    return element(folder, 'children')


def organize_project(root, sources):
    """Move existing master clips and sequences into bins without copying them.

    Organize after timeline construction: grouping interleaved POVs changes
    document order, which must not change master/source identity or references.
    """
    children = root.find('./project/children')
    masters = {clip.get('id'): clip for clip in children.findall('clip')}
    if len(masters) != len(sources):
        raise ValueError('Organization requires one ungrouped master clip per source')
    if sources:
        media = bin_children(children, '01 Media', 'vod-bin-media')
        folders = {}
        for index, source in enumerate(sources):
            label = text(source.get('pov', source.get('label', 'Other')), 'source POV bin').strip()
            if label not in folders:
                folders[label] = bin_children(media, label, f'vod-bin-pov-{len(folders)}')
            clip = masters[f'vod-master-{index}']
            children.remove(clip)
            folders[label].append(clip)
    sequences = children.findall('sequence')
    if sequences:
        timelines = bin_children(children, '02 Sequences', 'vod-bin-sequences')
        for sequence in sequences:
            children.remove(sequence)
            timelines.append(sequence)


def build_xml(markers, probes, title='VOD discovery', *, organize=True):
    root = ET.Element('xmeml', version='5')
    project = element(root, 'project')
    element(project, 'name', title)
    children = element(project, 'children')
    for index, source in enumerate(markers['sources']):
        metadata = probes[source['id']]
        videos = [s for s in metadata['streams'] if s['codec_type'] == 'video']
        audios = [s for s in metadata['streams'] if s['codec_type'] == 'audio']
        if len(videos) != 1 or len(audios) > 1:
            raise ValueError('XML route validated for one video and at most one audio stream; use panel for other layouts')
        for item in [metadata.get('format', {}), *metadata['streams']]:
            tc = item.get('tags', {}).get('timecode')
            if tc and tc not in ('00:00:00:00', '00:00:00;00'):
                raise ValueError('Nonzero embedded timecode needs live validation; use the marker panel')
        video = videos[0]
        base, ntsc, fps = frame_rate(video)
        frames = lambda seconds: round(Fraction(str(seconds)) * fps)
        duration = frames(source['duration_sec'])
        path = Path(source['path']).resolve()
        name = path.name
        masterid, fileid = f'vod-master-{index}', f'vod-file-{index}'
        clip = element(children, 'clip', id=masterid, explodedTracks='true')
        element(clip, 'name', name)
        element(clip, 'duration', duration)
        rate(clip, base, ntsc)
        element(clip, 'masterclipid', masterid)
        element(clip, 'ismasterclip', 'TRUE')
        element(clip, 'in', -1)
        element(clip, 'out', -1)
        file = ET.Element('file', id=fileid)
        element(file, 'name', name)
        element(file, 'pathurl', media_url(path))
        rate(file, base, ntsc)
        element(file, 'duration', duration)
        filemedia = element(file, 'media')
        filevideo = element(filemedia, 'video')
        element(filevideo, 'duration', duration)
        characteristics = element(filevideo, 'samplecharacteristics')
        rate(characteristics, base, ntsc)
        for key in ('width', 'height'):
            element(characteristics, key, video[key])
        if video.get('sample_aspect_ratio', '1:1') not in ('1:1', '0:1', 'N/A'):
            raise ValueError('Non-square pixels need separate XML validation')
        if video.get('field_order', 'progressive') not in ('progressive', 'unknown'):
            raise ValueError('Interlaced footage needs separate XML validation')
        element(characteristics, 'pixelaspectratio', 'square')
        element(characteristics, 'fielddominance', 'none')
        channels = 0
        if audios:
            audio = audios[0]
            channels = int(audio['channels'])
            if channels not in (1, 2):
                raise ValueError('XML audio route is restricted to mono/stereo; use panel for other layouts')
            fileaudio = element(filemedia, 'audio')
            element(fileaudio, 'channelcount', channels)
            characteristics = element(fileaudio, 'samplecharacteristics')
            element(characteristics, 'depth', 16)
            element(characteristics, 'samplerate', audio['sample_rate'])
        media = element(clip, 'media')
        for kind, count in [('video', 1), ('audio', channels)]:
            if not count:
                continue
            medium = element(media, kind)
            for channel in range(1, count + 1):
                track = element(medium, 'track')
                item = element(track, 'clipitem', id=f'item-{index}-{kind}-{channel}')
                if kind == 'audio':
                    # FCP serializes stereo as two channel records. Premiere must
                    # group those records into one stereo source/timeline track.
                    track.attrib.update(currentExplodedTrackIndex=str(channel - 1),
                                        totalExplodedTrackCount=str(channels),
                                        premiereTrackType='Stereo' if channels == 2 else 'Mono')
                    item.set('premiereChannelType', 'stereo' if channels == 2 else 'mono')
                for tag in ('name', 'duration', 'rate', 'masterclipid'):
                    item.append(deepcopy(clip.find(tag)))
                element(item, 'enabled', 'TRUE')
                element(item, 'in', 0)
                element(item, 'out', duration)
                if kind == 'video':
                    item.append(file)
                else:
                    element(item, 'file', id=fileid)
                source_track = element(item, 'sourcetrack')
                element(source_track, 'mediatype', kind)
                element(source_track, 'trackindex', channel)
        items = [(item, kind, ch) for kind, count in [('video', 1), ('audio', channels)]
                 for ch, item in enumerate(media.findall(f'./{kind}/track/clipitem'), 1)]
        for item, _, _ in items:
            for other, kind, ch in items:
                link = element(item, 'link')
                element(link, 'linkclipref', other.get('id'))
                element(link, 'mediatype', kind)
                element(link, 'trackindex', ch)
                element(link, 'clipindex', 1)
                if kind == 'audio':
                    element(link, 'groupindex', 1)
        for marker in source['markers']:
            validate_marker_presentation(marker)
            start, end = frames(marker['start_sec']), frames(marker['end_sec'])
            if not 0 <= start < end <= duration:
                raise ValueError('Marker collapses or exceeds source after frame quantization')
            m = element(clip, 'marker')
            element(m, 'name', marker['name'])
            # Premiere strips literal XML newlines; explicit separators stay readable.
            element(m, 'comment', ' / '.join(marker['comments'].splitlines()))
            element(m, 'in', start)
            element(m, 'out', end)
    if organize:
        organize_project(root, markers['sources'])
    ET.indent(root)
    return '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE xmeml>\n' + ET.tostring(root, encoding='unicode')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--title', default='VOD discovery')
    args = parser.parse_args()
    markers = export_events(read(args.events))
    probes = {}
    for source in markers['sources']:
        metadata, duration = probe(Path(source['path']).resolve(strict=True))
        if abs(duration - source['duration_sec']) > .1:
            raise ValueError('Source duration changed; review source mapping before export')
        probes[source['id']] = metadata
    result = build_xml(markers, probes, args.title)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result, encoding='utf-8')
    print(f"Wrote {out}: {len(markers['sources'])} source clips, "
          f"{sum(len(s['markers']) for s in markers['sources'])} markers")


if __name__ == '__main__':
    main()
