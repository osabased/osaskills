# Premiere delivery

Three routes write Premiere material from a validated `events.json`:

- `premiere_xml.py`: new source clips with markers, for a new review project. No sequence.
- `review_timeline.py`: the layered review timeline; see [timeline](timeline.md).
- `vod.py export` plus the UXP panel: markers on clips already in a project.

The review queue's exports use the timeline route. Author the marker copy first per [events](events.md).

## Source-marker XML

```sh
"$PY" <skill>/scripts/premiere_xml.py --events outputs/events.json --out outputs/source-markers.xml
```

The editor creates a separate review project, imports the XML with File > Import, opens a clip in the Source Monitor, checks the Markers panel, and saves the `.prproj`. No plugin is needed. The output uses [FCP7 master-clip media tracks](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html); a bare file element was silently ignored by Premiere 2026.

- This imports **new** source clip items with duration markers and POV references in their comments. It makes no sequence or cuts.
- Reimport is not an update. It can create duplicate items, does not attach markers to existing items, and does not rename markers in a saved project. For revised copy, use a new review project or the panel.
- `--out` must not exist; pass `--force` to replace it. `review_timeline.py` behaves the same way.

## Supported media

The exporter probes each source and checks its duration against `events.json`. It accepts:

- one progressive, square-pixel video stream at a nominal integer or 1000/1001 frame rate;
- at most one mono or stereo audio stream (a stereo stream becomes one grouped stereo track with both channels);
- no nonzero embedded timecode.

Other layouts fail explicitly. For several audio streams, import the originals natively and use the panel; never discard streams. Marker seconds round to the nearest nominal frame, so check VFR media and custom interpretation in Premiere.

## Bins

Both XML exporters organize the project into `01 Media/<POV>` (one bin per source `pov`, falling back to its `label`) and `02 Sequences` for review timelines. Give all parts of one POV the same `pov`; filenames and per-file markers stay intact. Only populated bins are created. A timeline references the same source masters, never a second media copy. Bins are Premiere project folders; files on disk do not move.

## After import

Show the Project panel with **Shift+1** and expand the imported bin (or `02 Sequences` for a timeline). An empty Markers panel or "no sequences" does not mean the import failed: the Project panel may be hidden or the sequence unopened. Check this before regenerating XML or asking for another import.

Then verify resolved media paths, short marker names and comments, and source times near the beginning and end of each source and at an overlapping moment. Bounded historical checks covered 60 and 30 fps media in Premiere 2026; other rates have adapter tests only. The Markers panel sometimes shows one frame below an exact whole-second time; check the stored time before compensating. Premiere strips literal newlines from comments, so XML comments use ` / ` separators. Do not author or patch `.prproj` internals; saved-project XML may be read to confirm host state.

## Media paths and VMs

Windows paths are written in Premiere's own form, `file://localhost/C%3a/...`. A bare `file:///C:/...` was read as a UNC path, and automatic relinking of nearby files can hide that fault, so verify absolute paths in the saved project. macOS and Linux paths use `file:///...`; that form has not been host-tested on macOS.

When the scripts see the media through a different mount than Premiere will (a Cowork VM's `$HOME/mnt/<folder>`, a network share), probe through the local path and write the editor's path:

```sh
"$PY" <skill>/scripts/premiere_xml.py --events outputs/events.json --out outputs/source-markers.xml \
  --path-map "$HOME/mnt/VODs=D:/VODs"
```

`--path-map LOCAL=HOST` is repeatable; the longest matching prefix wins, and the match must end at a path separator. Matching is against the paths as written in `events.json`. Every source must match a prefix, so no VM path leaks into the XML. The same option exists on `review_timeline.py`, `vod.py export` (for the panel's path matching) and `review_queue.py serve`/`export`.

## UXP panel for existing project items

Requires Premiere Pro 25.6 or newer and the editor's own computer. The editor installs Adobe's free UXP Developer Tool through Creative Cloud if needed, enables Premiere's UXP developer mode per Adobe's [first-plugin guide](https://developer.adobe.com/premiere-pro/uxp/plugins/), and adds `assets/premiere-panel/manifest.json` in UDT while Premiere is running. Do not change developer settings silently. No build step or paid extension is needed.

```sh
"$PY" <skill>/scripts/vod.py export --events outputs/events.json --out outputs/markers.json
```

1. Import the original VODs into Premiere if they are not already there.
2. In the Project panel, select one original clip per source in `markers.json`. Avoid duplicates, subclips and multicam or merged items.
3. Open the **VOD suggestions** panel and choose `markers.json`.
4. Click **Check selected sources** to see matches and marker counts, then **Add source markers**.
5. Open a marked clip in the Source Monitor and check a known event near the beginning and the end. Undo reverses the batch. Save the project afterwards; the panel does not save.

The panel matches clips by full media path, adds comment markers in one undoable transaction, and skips suggestions that already exist. It refuses missing or ambiguous matches, and refuses a changed suggestion under an existing ID so a rerun never overrides the editor's review. It never updates or removes the editor's markers. It uses Adobe's documented [Markers API](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/markers/) and is original code, not a fork of Adobe's samples. It is a development panel, not a signed package, and it has only mock tests: try a few known timestamps in a test project before a full batch, because source timecode, interpretation and XMP metadata preferences can change host behavior.
