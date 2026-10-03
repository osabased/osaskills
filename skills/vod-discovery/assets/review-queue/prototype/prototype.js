// THROWAWAY: three layouts of stacked timeline + global hotkeys on /?variant=A|B|C.
// Decisions live in the prototype server's memory; hotkeys live in this page.
const variants = {A:'Player first', B:'Timeline sidebar', C:'Timeline first'};
let variant = new URLSearchParams(location.search).get('variant') || 'A';
if (!variants[variant]) variant = 'A';
const defaults = {
  previous:{label:'Previous moment',key:'ArrowLeft'}, next:{label:'Next moment',key:'ArrowRight'},
  pov:{label:'Next POV',key:'KeyP'}, povBack:{label:'Previous POV',key:'Shift+KeyP'},
  play:{label:'Play / pause',key:'Space'}, back:{label:'Seek back 5s',key:'Shift+ArrowLeft'},
  forward:{label:'Seek forward 5s',key:'Shift+ArrowRight'},
  keep:{label:'Keep',key:'Digit1'}, later:{label:'Later',key:'Digit2'},
  skip:{label:'Skip',key:'Digit3'}, undo:{label:'Undo',key:'KeyU'}
};
let bindings = structuredClone(defaults), capturing = null;
let rangeStart = 0, rangeSpan = 300, total = 0, parts = [], segments = [], browseCursor = null;
let prototypeReady = false;
let timelineWidth = 1000;
const svgNS = 'http://www.w3.org/2000/svg';
function el(tag, attrs = {}, text = '') {
  const node = document.createElementNS(svgNS, tag);
  for (const [key,value] of Object.entries(attrs)) node.setAttribute(key,value);
  if (text) node.textContent = text;
  return node;
}
function pretty(key) {
  return key.replaceAll('Key','').replaceAll('Digit','').replace('ArrowLeft','←').replace('ArrowRight','→')
    .replace('ArrowUp','↑').replace('ArrowDown','↓').replace('Space','Space').split('+').join(' + ');
}
function pressed(event) {
  return [event.ctrlKey?'Ctrl':null,event.altKey?'Alt':null,event.shiftKey?'Shift':null,event.metaKey?'Meta':null,event.code].filter(Boolean).join('+');
}
function mainTime() {
  if (browseCursor !== null) return browseCursor;
  if (!current || !parts.length) return null;
  const view = current.views[viewIndex], source = view.preview_start_sec + video.currentTime;
  const part = parts.find(p => p.id === view.source_id);
  if (part) return part.start + source;
  const link = (current.sync_links || []).find(l => l.source_id === view.source_id &&
    source >= l.source_start_sec && source < l.source_end_sec);
  if (!link) return null;
  return parts.find(p => p.id === link.main_source_id).start + source - link.offset_sec;
}
function buildTimelineData() {
  const data = queue.timeline_data, sourceMap = Object.fromEntries(data.sources.map(s => [s.id,s]));
  total = 0;
  parts = data.plan.main_sources.map(id => {
    const s = sourceMap[id], part = {id,start:total,end:total+s.duration_sec,label:s.label};
    total = part.end; return part;
  });
  segments = [];
  for (const card of queue.cards) {
    for (const [i,view] of card.views.entries()) {
      const main = parts.find(p => p.id === view.source_id);
      if (main) segments.push({eid:card.id,view:i,lane:'Johan',start:main.start+view.start_sec,end:main.start+view.end_sec,
        origin:main.start,offset:0,label:view.title,uncertainty:0});
    }
  }
  for (const a of data.plan.alternates) {
    const card = queue.cards.find(c => c.id === a.event_id), index = card.views.findIndex(v => v.source_id === a.source_id);
    const origin = parts.find(p => p.id === a.main_source_id).start;
    const offset = a.source_anchor_sec - a.main_anchor_sec;
    segments.push({eid:card.id,view:index,lane:sourceMap[a.source_id].label,start:origin+a.source_start_sec-offset,
      end:origin+a.source_end_sec-offset,origin,offset,label:card.views[index].title,uncertainty:a.uncertainty_sec});
  }
}
function fitRange(time) {
  rangeSpan = Math.min(rangeSpan,total);
  rangeStart = Math.max(0,Math.min(total-rangeSpan,time-rangeSpan/2));
}
function rangeChange() {
  $('pan').max = Math.max(0,total-rangeSpan);
  $('pan').value = rangeStart;
  $('range-label').textContent = clock(rangeStart)+'–'+clock(rangeStart+rangeSpan);
  drawTimeline(); surfaceState();
}
function zoom(factor) {
  const at=mainTime() ?? rangeStart+rangeSpan/2;
  rangeSpan=Math.min(total,Math.max(25,rangeSpan*factor));
  fitRange(at); rangeChange();
}
function xAt(time, start, span) { return 60+(time-start)/span*(timelineWidth-68); }
function svgClock(svg, start, span, y) {
  const steps=timelineWidth<500?3:5;
  for (let i=0;i<=steps;i++) {
    const time=start+span*i/steps, x=xAt(time,start,span);
    svg.append(el('line',{x1:x,x2:x,y1:y+5,y2:Number(svg.getAttribute('height'))-14,class:'gridline'}));
    svg.append(el('text',{x,y,'text-anchor':i===steps?'end':'start',class:'ruler-text'},clock(time)));
  }
}
function drawTimeline() {
  if (!prototypeReady) return;
  const svg=$('stacked'), overview=$('overview');
  timelineWidth=svg.getBoundingClientRect().width;
  const height=svg.getBoundingClientRect().height, overviewHeight=overview.getBoundingClientRect().height;
  svg.setAttribute('viewBox','0 0 '+timelineWidth+' '+height);svg.setAttribute('height',height);
  overview.setAttribute('viewBox','0 0 '+timelineWidth+' '+overviewHeight);
  svg.replaceChildren(); overview.replaceChildren();
  svgClock(svg,rangeStart,rangeSpan,15);
  const lanes=[...new Set(segments.filter(s=>s.lane!=='Johan').map(s=>s.lane)),'Johan'];
  const laneYs={}, step=(height-42)/lanes.length, rowHeight=Math.min(65,Math.max(18,step-7));
  lanes.forEach((lane,i)=>{
    const y=26+i*step;laneYs[lane]=y;
    svg.append(el('text',{x:4,y:y+rowHeight/2+4,class:'lane-label'},lane));
    svg.append(el('rect',{x:60,y,width:timelineWidth-68,height:rowHeight,rx:4,class:'lane-bg'}));
  });
  for (const p of parts) {
    const x=Math.max(60,xAt(p.start,rangeStart,rangeSpan)), right=Math.min(timelineWidth-8,xAt(p.end,rangeStart,rangeSpan));
    if(right<=x)continue;
    svg.append(el('rect',{x,y:laneYs.Johan,width:right-x,height:rowHeight,class:'base-part'}));
    if(right-x>140)svg.append(el('text',{x:x+8,y:laneYs.Johan+rowHeight/2+4,class:'part-name'},p.label));
    if(p.start>rangeStart&&p.start<rangeStart+rangeSpan)svg.append(el('line',{x1:x,x2:x,y1:laneYs.Johan,y2:laneYs.Johan+rowHeight,class:'part-boundary'}));
  }
  for(const seg of segments) {
    const x=Math.max(60,xAt(seg.start,rangeStart,rangeSpan)), right=Math.min(timelineWidth-8,xAt(seg.end,rangeStart,rangeSpan));
    if(right<=x)continue;
    const active=seg.eid===current.id, chosen=active&&seg.view===viewIndex;
    const group=el('g',{class:'segment '+(seg.lane==='Johan'?'main-segment':'alt-segment')+(active?' current':'')+(chosen?' chosen':'')});
    const rect=el('rect',{x,y:laneYs[seg.lane]+2,width:Math.max(.8,right-x),height:rowHeight-4,rx:3});
    group.append(rect,el('title',{},seg.label+' · '+seg.lane+' · '+clock(seg.start)+'–'+clock(seg.end)+(seg.uncertainty?' · ±'+seg.uncertainty+'s':'')));
    if(right-x>Math.max(45,seg.label.length*5.5+8))group.append(el('text',{x:x+5,y:laneYs[seg.lane]+rowHeight/2+4,class:'segment-label'},seg.label));
    group.addEventListener('click',event=>{event.stopPropagation();const time=timeFromPointer(svg,event,rangeStart,rangeSpan);jump(time,seg);});
    svg.append(group);
  }
  const cursor=mainTime();
  if(cursor!==null&&cursor>=rangeStart&&cursor<=rangeStart+rangeSpan) {
    const x=xAt(cursor,rangeStart,rangeSpan);
    svg.append(el('line',{x1:x,x2:x,y1:23,y2:height-17,class:'playhead'}),el('path',{d:'M '+(x-4)+' 22 L '+(x+4)+' 22 L '+x+' 28 Z',class:'playhead-head'}));
  }
  svg.append(el('text',{x:60,y:height-2,class:'ruler-text'},'Click a clip to seek + switch POV'));
  // The overview always retains the full main chronology, even when detail is zoomed.
  overview.append(el('rect',{x:60,y:9,width:timelineWidth-68,height:12,rx:3,class:'overview-bg'}));
  for(const p of parts) {
    const x=xAt(p.start,0,total);
    overview.append(el('line',{x1:x,x2:x,y1:9,y2:21,class:'part-boundary'}));
    if(p.end-p.start>total*.2)overview.append(el('text',{x:x+5,y:18,class:'overview-part'},p.label));
  }
  for(const seg of segments.filter(s=>s.lane==='Johan'))overview.append(el('rect',{x:xAt(seg.start,0,total),y:9,width:Math.max(.7,(seg.end-seg.start)/total*(timelineWidth-68)),height:12,class:'overview-moment'}));
  overview.append(el('rect',{x:xAt(rangeStart,0,total),y:5,width:Math.max(2,rangeSpan/total*(timelineWidth-68)),height:20,rx:2,class:'view-window'}));
  if(cursor!==null)overview.append(el('line',{x1:xAt(cursor,0,total),x2:xAt(cursor,0,total),y1:3,y2:28,class:'playhead'}));
  overview.append(el('text',{x:0,y:19,class:'lane-label'},'Full VOD'),el('text',{x:60,y:overviewHeight-2,class:'ruler-text'},'00:00'),
    el('text',{x:timelineWidth-8,y:overviewHeight-2,'text-anchor':'end',class:'ruler-text'},clock(total)));
  $('timeline-clock').textContent=cursor===null?'No main-timeline anchor':clock(cursor,true)+' / '+clock(total);
  $('timeline-position').textContent=cursor===null?'Independent POV moment':((cursor/total)*100).toFixed(1)+'% through Johan';
}
function timeFromPointer(svg,event,start,span) {
  const box=svg.getBoundingClientRect(), x=event.clientX-box.left;
  return Math.max(start,Math.min(start+span,start+(x-60)/(box.width-68)*span));
}
async function jump(time, segment=null) {
  let seg=segment;
  if(!seg)seg=segments.find(s=>s.lane==='Johan'&&s.eid===current.id&&time>=s.start&&time<s.end)||
    segments.find(s=>s.lane==='Johan'&&time>=s.start&&time<s.end);
  if(!seg) {
    browseCursor=time;video.pause();$('prototype-unavailable').hidden=false;
    $('prototype-unavailable').textContent=clock(time)+' · Outside this pilot’s preview ranges';
    notice('Full session shown for position. Preview coverage is limited to the opening five minutes.');
    drawTimeline();surfaceState();return;
  }
  const card=queue.cards.find(c=>c.id===seg.eid), view=card.views[seg.view], source=time-seg.origin+seg.offset;
  const position=source-view.preview_start_sec;
  if(position<0||source>=view.preview_end_sec)return;
  await action(async()=>{
    video.pause();await flush();
    await save({event_id:card.id,view:seg.view,position_sec:position});
    await display(card.id);
  });
  drawTimeline();surfaceState();
}
function renderMomentList() {
  $('nearby-list').replaceChildren();
  for(const seg of segments.filter(s=>s.lane==='Johan')) {
    const b=document.createElement('button');b.className='nearby-moment'+(seg.eid===current.id?' selected':'');
    b.textContent=clock(seg.start)+'  '+seg.label;b.onclick=()=>jump((seg.start+seg.end)/2,seg);
    $('nearby-list').append(b);
  }
}
function surfaceState() {
  if(!prototypeReady)return;
  const value={prototype:true,variant:variant+' — '+variants[variant],shared_keybind_scope:'all projects (in-memory preview)',
    timeline_seconds:mainTime(),visible_range_seconds:[rangeStart,rangeStart+rangeSpan],full_duration_seconds:total,
    moment:current.id,pov:current.views[viewIndex].label,keybindings:bindings,review_choices:state.decisions};
  $('prototype-state').textContent=JSON.stringify(value,null,2);
}
function setVariant(key) {
  variant=key;document.body.dataset.variant=key;
  const url=new URL(location);url.searchParams.set('variant',key);history.replaceState({},'',url);
  $('variant-label').textContent=key+' · '+variants[key];
  for(const b of document.querySelectorAll('#prototype-switcher [data-variant]'))b.setAttribute('aria-pressed',String(b.dataset.variant===key));
  $('variant-intent').textContent={
    A:'A · Keep the player large, with an overview and compact track strip below.',
    B:'B · Browse timeline and moments beside the player.',
    C:'C · Give the timeline more room, with a compact player above.'
  }[key];
  if($('keys-panel').open){$('keys-panel').close();openKeys();}
  drawTimeline();surfaceState();
  console.log('Prototype variant state',JSON.parse($('prototype-state').textContent));
}
function cycleVariant(direction) {
  const keys=Object.keys(variants);setVariant(keys[(keys.indexOf(variant)+direction+3)%3]);
}
function drawKeys() {
  $('key-rows').replaceChildren();
  for(const [id,item] of Object.entries(bindings)) {
    const row=document.createElement('div');row.className='key-row';
    const label=document.createElement('span');label.textContent=item.label;
    const button=document.createElement('button');button.dataset.action=id;
    button.textContent=capturing===id?'Press a key…':pretty(item.key);
    if(capturing===id)button.className='listening';
    button.onclick=()=>{capturing=id;$('key-message').textContent='Press a key combination. Escape cancels.';drawKeys();};
    row.append(label,button);$('key-rows').append(row);
  }
}
function openKeys() {
  drawKeys();$('keys-panel').showModal();
  $('key-message').textContent='Click an action’s key, then press a new combination.';
}
function updateHints() {
  for(const id of ['keep','later','skip'])$(id).querySelector('kbd').textContent=pretty(bindings[id].key);
  $('previous').title='Previous moment ('+pretty(bindings.previous.key)+')';
  $('next').title='Next moment ('+pretty(bindings.next.key)+')';
  document.querySelector('.bottom-line > span').textContent=pretty(bindings.previous.key)+' / '+pretty(bindings.next.key)+' moments · '+pretty(bindings.pov.key)+' POV · '+pretty(bindings.play.key)+' play';
}
function keyAction(id) {
  if(id==='previous')step(-1);else if(id==='next')step(1);
  else if(id==='pov')cyclePOV(1);else if(id==='povBack')cyclePOV(-1);
  else if(id==='play'){if(!busy)video.paused?autoplay():video.pause();}
  else if(id==='back'||id==='forward'){if(!busy)video.currentTime=Math.max(0,Math.min(video.duration,video.currentTime+(id==='back'?-5:5)));}
  else if(id==='undo')$('undo').click();else decide(id);
}
document.addEventListener('keydown',event=>{
  if(!prototypeReady)return;
  if(capturing) {
    event.preventDefault();event.stopImmediatePropagation();
    if(event.code==='Escape'){capturing=null;drawKeys();return;}
    if(['ShiftLeft','ShiftRight','ControlLeft','ControlRight','AltLeft','AltRight','MetaLeft','MetaRight'].includes(event.code))return;
    const key=pressed(event), duplicate=Object.entries(bindings).find(([id,b])=>id!==capturing&&b.key===key);
    if(duplicate){$('key-message').textContent='Already used by '+duplicate[1].label+'. Choose another key.';return;}
    if(['Tab','F5','Alt+F4','Ctrl+KeyR','Ctrl+KeyW','Ctrl+KeyT'].includes(key)){$('key-message').textContent='That key is used by the browser. Try another.';return;}
    bindings[capturing].key=key;capturing=null;drawKeys();updateHints();surfaceState();
    $('key-message').textContent='Applied to every moment and layout in this preview.';return;
  }
  if($('keys-panel').open)return;
  if(event.target.closest('#prototype-switcher')&&['ArrowLeft','ArrowRight'].includes(event.key)) {
    event.preventDefault();cycleVariant(event.key==='ArrowRight'?1:-1);return;
  }
  if(/INPUT|TEXTAREA|SELECT/.test(event.target.tagName)||event.target.isContentEditable||event.repeat)return;
  const match=Object.entries(bindings).find(([,b])=>b.key===pressed(event));
  if(match){event.preventDefault();activateSound();keyAction(match[0]);}
},true);
function mountPrototype() {
  const stage=document.createElement('section');stage.id='prototype-stage';
  for(const selector of ['.moment-heading','#summary','.view-bar','.player','.transport','#check'])stage.append(document.querySelector(selector));
  const inspector=document.createElement('section');inspector.id='prototype-inspector';
  for(const selector of ['.actions','#notes','.bottom-line','#done','#export-result'])inspector.append(document.querySelector(selector));
  const timeline=document.createElement('section');timeline.id='prototype-timeline';
  timeline.innerHTML=[
    '<div class="timeline-heading"><strong>Timeline</strong><span id="timeline-clock"></span></div>',
    '<p id="timeline-position"></p>',
    '<svg id="overview" viewBox="0 0 1000 54" aria-label="Full Johan timeline"></svg>',
    '<div class="timeline-tools"><button id="show-full">Full session</button><button id="show-current">Current moment</button><span id="range-label"></span><button id="zoom-out" aria-label="Zoom out">−</button><button id="zoom-in" aria-label="Zoom in">+</button></div>',
    '<svg id="stacked" viewBox="0 0 1000 165" aria-label="Stacked POV timeline"></svg>',
    '<input id="pan" type="range" min="0" step="1" value="0" aria-label="Pan visible timeline">',
    '<p class="timeline-caption">Opening 5 min reviewed · alternatives aligned locally, ±1–5s</p>',
    '<div id="nearby"><h2>Moments in this pilot</h2><div id="nearby-list"></div></div>'
  ].join('');
  $('review').append(stage,timeline,inspector);
  const cover=document.createElement('div');cover.id='prototype-unavailable';cover.hidden=true;document.querySelector('.player').append(cover);
  const keyButton=document.createElement('button');keyButton.id='open-keys';keyButton.textContent='Keybinds';
  keyButton.onclick=openKeys;document.querySelector('.header-right').prepend(keyButton);
  $('export').textContent='Prototype';$('export').disabled=true;$('export-all').disabled=true;
  const dialog=document.createElement('dialog');dialog.id='keys-panel';
  dialog.innerHTML='<div class="keys-heading"><div><h2>Keybinds</h2><p>One profile for all projects</p></div><button id="close-keys" aria-label="Close keybinds">×</button></div><div id="key-rows"></div><p id="key-message"></p><div class="keys-footer"><button id="reset-keys">Restore defaults</button><span>Temporary prototype settings</span></div>';
  document.body.append(dialog);
  $('close-keys').onclick=()=>{capturing=null;dialog.close();};
  $('reset-keys').onclick=()=>{bindings=structuredClone(defaults);capturing=null;drawKeys();updateHints();surfaceState();};
  const bar=document.createElement('aside');bar.id='prototype-switcher';
  bar.innerHTML='<span class="prototype-tag">PROTOTYPE</span><button id="variant-prev" aria-label="Previous layout">←</button><strong id="variant-label"></strong><button id="variant-next" aria-label="Next layout">→</button><div class="variant-buttons"><button data-variant="A">A</button><button data-variant="B">B</button><button data-variant="C">C</button></div><details><summary>State</summary><pre id="prototype-state"></pre></details><span id="variant-intent"></span>';
  document.body.append(bar);
  $('variant-prev').onclick=()=>cycleVariant(-1);$('variant-next').onclick=()=>cycleVariant(1);
  for(const button of bar.querySelectorAll('[data-variant]'))button.onclick=()=>setVariant(button.dataset.variant);
  $('show-full').onclick=()=>{rangeStart=0;rangeSpan=total;rangeChange();};
  $('show-current').onclick=()=>{rangeSpan=90;fitRange(mainTime()??110);rangeChange();};
  $('zoom-in').onclick=()=>zoom(.5);$('zoom-out').onclick=()=>zoom(2);
  $('pan').oninput=()=>{rangeStart=Number($('pan').value);rangeChange();};
  $('overview').onclick=event=>{const time=timeFromPointer($('overview'),event,0,total);fitRange(time);rangeChange();jump(time);};
  $('stacked').onclick=event=>jump(timeFromPointer($('stacked'),event,rangeStart,rangeSpan));
  const originalDisplay=display;
  display=async function(id) {
    browseCursor=null;$('prototype-unavailable').hidden=true;
    await originalDisplay(id);
    const t=mainTime();
    if(t!==null&&(t<rangeStart||t>rangeStart+rangeSpan))fitRange(t);
    rangeChange();renderMomentList();
  };
  prototypeReady=true;buildTimelineData();renderMomentList();rangeChange();setVariant(variant);updateHints();
  video.addEventListener('timeupdate',()=>{drawTimeline();});
  video.addEventListener('seeked',()=>{drawTimeline();surfaceState();});
  window.addEventListener('resize',drawTimeline);
}
const prototypeBoot=setInterval(()=>{
  if(typeof queue!=='undefined'&&queue&&typeof current!=='undefined'&&current&&!busy) {
    clearInterval(prototypeBoot);mountPrototype();
  }
},80);
