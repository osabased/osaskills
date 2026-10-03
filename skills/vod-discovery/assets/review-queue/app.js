'use strict';
const $ = id => document.getElementById(id);
const labels = {unreviewed:'Not reviewed',keep:'Keep',later:'Later',skip:'Skip'};
let queue, state, token, current, viewIndex=0, chain=Promise.resolve(), broken=false, busy=false, timer, lastTick=0;
const video=$('video');
function clock(seconds){const n=Math.floor(seconds);return `${Math.floor(n/3600)?`${Math.floor(n/3600)}:`:''}${String(Math.floor(n/60)%60).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;}
function fail(error){broken=true;video.pause();$('saved').textContent='Not saved';$('error').hidden=false;$('error').textContent=error.message+' Your last confirmed choices remain saved. ';const b=document.createElement('button');b.textContent='Reload saved choices';b.onclick=()=>location.reload();$('error').append(b);document.querySelectorAll('main button,main select,main textarea,#export').forEach(b=>b.disabled=true);}
async function post(path,body){const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Review-Token':token},body:JSON.stringify({...body,revision:state.revision}),keepalive:true});const data=await response.json();if(!response.ok)throw new Error(data.error||'Could not save');return data;}
function enqueue(fn){chain=chain.then(async()=>{if(broken)return;return fn();}).catch(fail);return chain;}
function snapshot(extra={}){return {event_id:current.id,note:$('note').value,view:viewIndex,position_sec:Number.isFinite(video.currentTime)?video.currentTime:0,...extra};}
function save(patch){
  $('saved').textContent='Saving…';
  return enqueue(async()=>{
    const item=state.decisions[patch.event_id], view=patch.view??item.view;
    const changed=state.current_id!==patch.event_id||
      ['decision','note','view'].some(key=>key in patch&&patch[key]!==item[key])||
      ('position_sec' in patch&&Math.abs(patch.position_sec-(item.positions[String(view)]||0))>.05);
    if(changed)state=await post('/api/save',patch);
    $('saved').textContent='Saved on this computer';renderList();$('undo').disabled=!state.history.length;
  });
}
function flush(extra={}){clearTimeout(timer);return save(snapshot(extra));}
function filtered(){return queue.cards.filter(c=>$('filter').value==='all'||state.decisions[c.id].decision===$('filter').value);}
function renderList(){const decided=queue.cards.filter(c=>state.decisions[c.id].decision!=='unreviewed').length;$('count').textContent=`${decided} / ${queue.cards.length} reviewed`;$('list').replaceChildren();for(const card of filtered()){const b=document.createElement('button');b.dataset.id=card.id;b.setAttribute('aria-current',String(card.id===current?.id));const dot=document.createElement('span');dot.className='dot '+state.decisions[card.id].decision;dot.textContent=state.decisions[card.id].decision==='unreviewed'?'•':labels[state.decisions[card.id].decision];const title=document.createElement('strong');title.textContent=card.title;const meta=document.createElement('small');meta.textContent=`${card.views[0].label} · ${clock(card.views[0].start_sec)}`;b.append(dot,title,meta);b.onclick=()=>navigate(card.id);$('list').append(b);}if(!$('list').children.length){const p=document.createElement('p');p.textContent='No moments in this group.';$('list').append(p);}$('export').disabled=!queue.cards.some(c=>state.decisions[c.id].decision==='keep');}
function display(id){current=queue.cards.find(c=>c.id===id);viewIndex=state.decisions[id].view;$('note').value=state.decisions[id].note;$('decision').textContent=labels[state.decisions[id].decision];$('check').hidden=!current.check;$('check').textContent=current.check?`Check: ${current.check}`:'';$('done').hidden=true;renderView();renderList();$('undo').disabled=!state.history.length;$('related').replaceChildren();for(const relation of current.related){const related=queue.cards.find(c=>c.id===relation.event_id);if(!related)continue;const b=document.createElement('button');b.textContent=`${relation.relationship}: ${related.title}`;b.title='Related moment; not simultaneous coverage';b.onclick=()=>navigate(related.id);$('related').append(b);}}
function renderView(){const view=current.views[viewIndex];$('title').textContent=view.title;$('summary').textContent=view.summary;$('clock').textContent=`${view.label} · ${clock(view.start_sec)}–${clock(view.end_sec)}`;$('views').replaceChildren();current.views.forEach((v,i)=>{const b=document.createElement('button');b.textContent=v.label;b.setAttribute('aria-pressed',String(i===viewIndex));b.onclick=()=>switchView(i);$('views').append(b);});$('preview-meta').textContent=`Preview: ${clock(view.preview_start_sec)}–${clock(view.preview_end_sec)} · ${view.label} audio${view.uncertainty_sec?` · timing ±${view.uncertainty_sec}s`:''}. Views play separately.`;video.pause();video.src='/previews/'+view.file;video.onloadedmetadata=()=>{video.currentTime=Math.min(state.decisions[current.id].positions[String(viewIndex)]||0,Math.max(0,video.duration-.05));video.playbackRate=Number($('speed').value);};}
async function navigate(id){if(busy||broken||id===current.id)return;busy=true;video.pause();await flush();if(!broken){display(id);await save({event_id:id});}busy=false;}
async function switchView(index){if(busy||broken||index===viewIndex)return;busy=true;video.pause();await flush();if(!broken){viewIndex=index;renderView();await save({event_id:current.id,view:viewIndex});}busy=false;}
async function decide(decision){
  if(busy||broken)return;
  busy=true;video.pause();await flush({decision});
  if(!broken){
    $('decision').textContent=labels[decision];
    const candidates=filtered(), pos=queue.cards.indexOf(current);
    const pending=candidates.filter(c=>c.id!==current.id&&(['all','unreviewed'].includes($('filter').value)?state.decisions[c.id].decision==='unreviewed':true));
    const next=pending.find(c=>queue.cards.indexOf(c)>pos)||pending[0];
    if(next){display(next.id);await save({event_id:next.id});}
    else{$('done').hidden=false;$('done').textContent='You’re through this group. Stop here, revisit Later, or export what you kept.';}
  }
  busy=false;
}
for(const decision of ['keep','later','skip'])$(decision).onclick=()=>decide(decision);
$('undo').onclick=async()=>{if(busy||broken)return;busy=true;video.pause();await flush();await enqueue(async()=>{state=await post('/api/undo',{});display(state.current_id);$('saved').textContent='Saved on this computer';});busy=false;};
$('note').addEventListener('input',()=>{clearTimeout(timer);$('saved').textContent='Saving…';timer=setTimeout(()=>flush(),400);});
$('note').addEventListener('blur',()=>{if(!busy&&!broken)flush();});
$('filter').onchange=()=>renderList();
$('speed').onchange=()=>{video.playbackRate=Number($('speed').value);};
function step(delta){const cards=filtered();let i=cards.findIndex(c=>c.id===current.id);if(i<0)i=delta>0?-1:cards.length;const c=cards[i+delta];if(c)navigate(c.id);}
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
video.addEventListener('timeupdate',()=>{if(current&&!busy&&!broken&&!video.paused&&video.readyState>=1&&Date.now()-lastTick>5000){lastTick=Date.now();flush();}});
video.addEventListener('pause',()=>{if(current&&!busy&&!broken&&video.readyState>=1)flush();});
video.addEventListener('error',()=>{if(current)fail(new Error('Preview could not load. Restart the local server if it stopped.'));});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&current&&!broken)flush();});
window.addEventListener('beforeunload',()=>{if(current&&!broken)flush();});
document.addEventListener('keydown',e=>{if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.ctrlKey||e.metaKey||e.altKey||e.repeat||broken)return;if(['1','2','3'].includes(e.key)){e.preventDefault();decide({'1':'keep','2':'later','3':'skip'}[e.key]);}else if(e.key.toLowerCase()==='u'){e.preventDefault();$('undo').click();}else if(e.code==='Space'&&e.target.tagName!=='BUTTON'){e.preventDefault();video.paused?video.play().catch(fail):video.pause();}else if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();video.currentTime=Math.max(0,Math.min(video.duration||0,video.currentTime+(e.key==='ArrowRight'?5:-5)));}});
async function exportQueue(mode){if(busy||broken)return;busy=true;video.pause();await flush();await enqueue(async()=>{try{const result=await post('/api/export',{mode});$('export-result').replaceChildren();const a=document.createElement('a');a.href=result.url;a.textContent=`Download Premiere XML · ${result.count} moments`;a.download='Moment-Review.xml';const p=document.createElement('span');p.textContent='  Saved at '+result.path;$('export-result').append(a,p);}catch(error){$('export-result').textContent='Export failed: '+error.message;}});busy=false;}
$('export').onclick=()=>exportQueue('keep');$('export-all').onclick=()=>exportQueue('all');
fetch('/api/queue').then(async response=>{const data=await response.json();if(!response.ok)throw new Error(data.error);queue=data.queue;state=data.state;token=data.token;$('coverage').textContent=queue.coverage;display(state.current_id);$('saved').textContent='Saved on this computer';}).catch(fail);
