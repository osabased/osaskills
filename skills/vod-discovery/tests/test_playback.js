const assert = require('node:assert/strict');
const {mapSwitch, nextView} = require('../assets/review-queue/playback.js');
const card = {
  views:[
    {source_id:'main',preview_start_sec:68,preview_end_sec:105},
    {source_id:'other',preview_start_sec:147,preview_end_sec:187},
    {source_id:'third',preview_start_sec:31,preview_end_sec:58},
    {source_id:'unlinked',preview_start_sec:0,preview_end_sec:100}
  ],
  sync_links:[
    {main_source_id:'main',source_id:'other',offset_sec:82.91,source_start_sec:150,source_end_sec:184,uncertainty_sec:3},
    {main_source_id:'main',source_id:'third',offset_sec:-40,source_start_sec:34,source_end_sec:55,uncertainty_sec:1}
  ]
};
function near(a,b){assert(Math.abs(a-b)<1e-8, a+' differs from '+b);}
const mapped=mapSwitch(card,0,1,12); // main source 80 -> alternate source 162.91.
near(mapped.source_sec,162.91);near(mapped.position_sec,15.91);assert.equal(mapped.uncertainty_sec,3);
near(mapSwitch(card,1,0,mapped.position_sec).position_sec,12);
near(mapSwitch(card,0,2,12).source_sec,40);
near(mapSwitch(card,1,2,15.91).position_sec,9);
assert.equal(mapSwitch(card,1,2,15.91).uncertainty_sec,4);
assert.equal(mapSwitch(card,0,1,36),null); // Outside the locally supported alternate excerpt.
assert.equal(mapSwitch(card,0,2,1),null);
assert.equal(mapSwitch(card,0,3,12),null); // Related/unknown POV is never synchronized by range start.
assert.equal(mapSwitch({...card,sync_links:[]},0,1,12),null);
assert.equal(mapSwitch(card,0,1,NaN),null);
assert.equal(mapSwitch(card,0,1,-1),null);
const cropped=structuredClone(card);cropped.views[1].preview_start_sec=170;
assert.equal(mapSwitch(cropped,0,1,12),null); // No clamp to another moment.
assert.equal(nextView(card,0,12).index,1);
assert.equal(nextView(card,0,12,-1).index,2);
assert.equal(nextView(card,0,36),null);
const drift=structuredClone(card);drift.sync_links[0].offset_sec=80;
near(mapSwitch(drift,0,1,12).source_sec,160); // A different event uses its own offset.
assert.equal(card.sync_links[0].offset_sec,82.91);
console.log('Playback checks passed: reversible clocks, per-event offsets, bounded coverage, missing anchors and POV cycling.');
