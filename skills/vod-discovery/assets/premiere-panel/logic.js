/* Pure validation and planning; host operations live in index.js. */
function normalize(path) {
  return path.replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
}
function required(value, label) {
  if (typeof value !== "string" || !value.trim()) throw Error(`Missing ${label}`);
}
function validate(data) {
  if (!data || data.schema !== "vod-source-markers/v1" || !Array.isArray(data.sources)) throw Error("Unsupported marker file");
  const paths = new Set();
  for (const source of data.sources) {
    required(source.path, "source path");
    if (!/^([A-Za-z]:[\\/]|\/|\\\\)/.test(source.path)) throw Error("Source path must be absolute");
    const path = normalize(source.path);
    if (paths.has(path)) throw Error("Duplicate source path");
    paths.add(path);
    if (!Number.isFinite(source.duration_sec) || source.duration_sec <= 0 || !Array.isArray(source.markers)) throw Error("Invalid source duration/markers");
    const keys = new Set();
    for (const marker of source.markers) {
      required(marker.key, "marker key"); required(marker.name, "marker name"); required(marker.comments, "marker evidence");
      if (/[\[\]\r\n]/.test(marker.key) || keys.has(marker.key)) throw Error("Invalid or duplicate marker key");
      keys.add(marker.key);
      if (marker.name.trim().split(/\s+/).length > 4 || marker.name !== marker.name.trim().split(/\s+/).join(" ") ||
          /[\[\]|\r\n]|\.\.\.|…/.test(marker.name)) {
        throw Error("Use a clean 1–4-word marker name; re-export legacy marker files with IDs in comments");
      }
      const refs = [...marker.comments.matchAll(/\[VOD:([^\[\]\r\n]+)\]/g)].map(x => x[1]);
      if (refs.length !== 1 || refs[0] !== marker.key) throw Error("Marker comments do not match its key");
      if (!Number.isFinite(marker.start_sec) || !Number.isFinite(marker.end_sec) || marker.start_sec < 0 ||
          marker.end_sec <= marker.start_sec || marker.end_sec > source.duration_sec) throw Error("Marker outside source duration");
    }
  }
  return data;
}
function plan(source, existing) {
  const add = [];
  let skipped = 0;
  for (const marker of source.markers) {
    const token = `[VOD:${marker.key}]`;
    // Recognize historical name tokens too, so a label migration cannot add a
    // duplicate or silently overwrite an existing/editor-modified suggestion.
    const matches = existing.filter(x => x.name.includes(token) || (x.comments || "").includes(token));
    if (!matches.length && existing.some(x => x.name === marker.name &&
        !/\[VOD:[^\[\]\r\n]+\]/.test((x.comments || "") + x.name) &&
        Math.abs(x.start_sec - marker.start_sec) <= 0.00001 && Math.abs(x.end_sec - marker.end_sec) <= 0.00001)) {
      throw Error(`Suggestion ${marker.key} changed or was edited: matching label/range has no reference. Existing markers were preserved.`);
    }
    if (matches.length) {
      if (matches.length !== 1) throw Error(`Duplicate existing key ${marker.key}; resolve in Premiere`);
      const old = matches[0];
      // XML flattens comment lines into visible separators; identity and repeat
      // imports must also work when those markers are read through the panel.
      const commentText = s => s.replace(/\r?\n/g, " / ");
      if (old.name !== marker.name || commentText(old.comments) !== commentText(marker.comments) ||
          Math.abs(old.start_sec - marker.start_sec) > 0.00001 || Math.abs(old.end_sec - marker.end_sec) > 0.00001) {
        throw Error(`Suggestion ${marker.key} changed or was edited. Existing markers were preserved. Resolve this key before importing.`);
      }
      skipped++;
    } else add.push(marker);
  }
  return {add, skipped};
}
module.exports = {normalize, validate, plan};
