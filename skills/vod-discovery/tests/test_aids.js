const assert=require('node:assert/strict');
const {thumbnailAt,peaksIn}=require('../assets/review-queue/aids.js');
const data={preview_start_sec:100,preview_end_sec:104,waveform:{step_sec:1,peaks:[.1,.9,.2,.4]},
  thumbnails:{frames:[{source_sec:100,x:0,y:0},{source_sec:102,x:160,y:0}]}};
assert.equal(thumbnailAt(data,101.9).source_sec,100);
assert.equal(thumbnailAt(data,102).source_sec,102);
assert.equal(thumbnailAt(data,400).source_sec,102);
assert.equal(thumbnailAt({},100),null);
assert.deepEqual(peaksIn(data,100,104,2),[.9,.4]);
assert.deepEqual(peaksIn(data,101,103,2),[.9,.2]);
assert.deepEqual(peaksIn(data,99,101,2),[0,.1]);
assert.deepEqual(peaksIn({},100,104,2),[]);
console.log('Navigation aid checks passed: exact source frame clocks, peak aggregation and missing audio.');
