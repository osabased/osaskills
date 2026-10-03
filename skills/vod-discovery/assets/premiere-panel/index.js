const ppro = require("premierepro");
const fs = require("uxp").storage.localFileSystem;
const {normalize, validate, plan} = require("./logic.js");
let data = null;
let busy = false;
const status = document.getElementById("status");
function message(value) { status.textContent = value; }
function buttons() {
  document.getElementById("load").disabled = busy;
  document.getElementById("check").disabled = busy || !data;
  document.getElementById("apply").disabled = busy || !data;
}
async function guarded(fn) {
  if (busy) return;
  busy = true; buttons();
  try { await fn(); } catch (error) { message(`Error: ${error.message || error}`); }
  finally { busy = false; buttons(); }
}
async function prepare() {
  validate(data);
  const project = await ppro.Project.getActiveProject();
  if (!project) throw Error("Open a project first");
  const selection = await ppro.ProjectUtils.getSelection(project);
  const items = await selection.getItems();
  const selected = new Map();
  for (const item of items) {
    let clip;
    try { clip = ppro.ClipProjectItem.cast(item); } catch (_) { continue; }
    if (!clip || await clip.isSequence() || await clip.isMergedClip() || await clip.isMulticamClip()) continue;
    const path = normalize(await clip.getMediaFilePath());
    if (!selected.has(path)) selected.set(path, []);
    selected.get(path).push(clip);
  }
  const plans = [];
  for (const source of data.sources) {
    const matches = selected.get(normalize(source.path)) || [];
    if (matches.length !== 1) throw Error(`${source.path}: select exactly one matching original source clip (${matches.length} selected)`);
    const markers = await ppro.Markers.getMarkers(matches[0]);
    const existing = markers.getMarkers().map(m => ({name: m.getName(), comments: m.getComments(),
      start_sec: m.getStart().seconds, end_sec: m.getStart().seconds + m.getDuration().seconds}));
    plans.push({source, markers, ...plan(source, existing)});
  }
  return {project, plans};
}
function describe(plans) {
  return plans.map(p => `${p.source.path}\n  ${p.add.length} new, ${p.skipped} already present`).join("\n");
}
document.getElementById("load").addEventListener("click", () => guarded(async () => {
  const file = await fs.getFileForOpening({types: ["json"]});
  if (!file) return;
  data = null;
  data = validate(JSON.parse((await file.read()).replace(/^\uFEFF/, "")));
  message(`Loaded ${data.sources.length} sources. Check selected source clips before adding markers.`);
}));
document.getElementById("check").addEventListener("click", () => guarded(async () => {
  const {plans} = await prepare();
  message(describe(plans));
}));
document.getElementById("apply").addEventListener("click", () => guarded(async () => {
  // Recheck selection and existing markers immediately before the transaction.
  const {project, plans} = await prepare();
  const count = plans.reduce((n, p) => n + p.add.length, 0);
  if (!count) { message(`No new markers.\n${describe(plans)}`); return; }
  let success = false;
  project.lockedAccess(() => {
    success = project.executeTransaction(compound => {
      for (const p of plans) for (const marker of p.add) {
        compound.addAction(p.markers.createAddMarkerAction(marker.name, ppro.Marker.MARKER_TYPE_COMMENT,
          ppro.TickTime.createWithSeconds(marker.start_sec),
          ppro.TickTime.createWithSeconds(marker.end_sec - marker.start_sec), marker.comments));
      }
    }, "Add VOD source suggestions");
  });
  if (!success) throw Error("Premiere did not confirm the marker transaction; inspect the project before retrying");
  message(`Added ${count} source clip markers. Verify them in the Source Monitor, then save.\nUndo reverses this batch.`);
}));
