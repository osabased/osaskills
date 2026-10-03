/* Verify host integration planning with a strict mock; not a live Premiere test. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const panel = path.join(__dirname, "../assets/premiere-panel");
const logic = require(path.join(panel, "logic.js"));
const marker = {key: "e1", name: "Boss Defeated", comments: "Alice defeats the boss.\nRef [VOD:e1]",
  start_sec: 3600.125, end_sec: 3620.25};
const source = {path: "D:/VODs/a.mp4", duration_sec: 7200, markers: [marker]};
const data = {schema: "vod-source-markers/v1", sources: [source]};
logic.validate(data);
assert.equal(logic.plan(source, []).add.length, 1);
assert.equal(logic.plan(source, [marker]).skipped, 1);
assert.throws(() => logic.plan(source, [{...marker, comments: "Editor's changes"}]));
assert.equal(logic.plan(source, [{...marker, comments: marker.comments.replace(/\n/g, ' / ')}]).skipped, 1);
for (const name of ['[VOD:e1] Boss (candidate; action)', 'Boss defeated [VOD:e1]']) {
  const legacy = {...marker, name, comments: 'Legacy description'};
  assert.throws(() => logic.plan(source, [legacy]), /changed or was edited/);
  assert.throws(() => logic.validate({...data, sources: [{...source, markers: [legacy]}]}));
}
assert.throws(() => logic.plan(source, [marker, marker]), /Duplicate existing key/);
assert.equal(logic.plan(source, [{...marker, comments: 'Ref [VOD:e10]'}]).add.length, 1);
for (const change of [{name: 'A very long description of action'}, {name: 'Boss…'},
                      {comments: 'No reference'}, {comments: 'Ref [VOD:e2]'},
                      {comments: 'Ref [VOD:e1] [VOD:e1]'}]) {
  assert.throws(() => logic.validate({...data, sources: [{...source, markers: [{...marker, ...change}]}]}));
}
assert.throws(() => logic.validate({...data, sources: [{...source, markers: [{...marker, start_sec: NaN}]}]}));
let locked = false, transactions = 0, selectedPath = source.path;
let stored = [];
const collection = {
  getMarkers: () => stored.map(m => ({getName: () => m.name, getComments: () => m.comments,
    getStart: () => ({seconds: m.start_sec}), getDuration: () => ({seconds: m.end_sec - m.start_sec})})),
  createAddMarkerAction(name, type, start, duration, comments) {
    assert(locked); assert.equal(type, "Comment");
    return {name, comments, start_sec: start.seconds, end_sec: start.seconds + duration.seconds};
  }
};
const clip = {isSequence: async () => false, isMergedClip: async () => false, isMulticamClip: async () => false,
  getMediaFilePath: async () => selectedPath};
const project = {
  lockedAccess(fn) { locked = true; try { fn(); } finally { locked = false; } },
  executeTransaction(fn) { assert(locked); const actions = []; fn({addAction: x => actions.push(x)});
    stored.push(...actions); transactions++; return true; }
};
const ppro = {Project: {getActiveProject: async () => project},
  ProjectUtils: {getSelection: async () => ({getItems: async () => [clip]})},
  ClipProjectItem: {cast: x => x}, Markers: {getMarkers: async owner => {assert.equal(owner, clip); return collection;}},
  Marker: {MARKER_TYPE_COMMENT: "Comment"}, TickTime: {createWithSeconds: seconds => ({seconds})}};
const elements = {};
for (const id of ["load", "check", "apply", "status"]) elements[id] = {addEventListener(_, fn) {this.click = fn;}};
const context = {require: name => name === "premierepro" ? ppro : name === "uxp" ?
  {storage: {localFileSystem: {getFileForOpening: async () => ({read: async () => JSON.stringify(data)})}}} : logic,
  document: {getElementById: id => elements[id]}, console};
vm.runInNewContext(fs.readFileSync(path.join(panel, "index.js"), "utf8"), context);
(async () => {
  await elements.load.click();
  selectedPath = "D:/wrong.mp4";
  await elements.apply.click();
  assert.equal(transactions, 0); assert.match(elements.status.textContent, /exactly one/);
  selectedPath = source.path;
  await elements.apply.click();
  assert.equal(stored.length, 1); assert.equal(stored[0].start_sec, 3600.125);
  await elements.apply.click();
  assert.equal(transactions, 1); assert.equal(stored.length, 1);
  stored[0].comments = "Human edit";
  await elements.apply.click();
  assert.equal(transactions, 1); assert.match(elements.status.textContent, /changed or was edited/);
  console.log("Panel checks passed: source matching, transactions, exact times, repeat import, human edits, validation.");
})().catch(error => {console.error(error); process.exitCode = 1;});
