'use strict';
const $ = id => document.getElementById(id);
const {mapSwitch, nextView, rebasePosition, resumePosition} = VODPlayback;
const labels = {unreviewed:'Not reviewed', keep:'Keep', later:'Later', skip:'Skip'};
const video = $('video');
let queue, state, token, current, timeline, keys, scrub, detached = null, viewIndex = 0;
let transcriptSerial = 0, transcriptTimer, transcriptOffset = 0, transcriptRows = [];
let cardsById, cardOrder, listedIds = null, listedCurrentId;
const listRows = new Map();
const contextRequests = new Map();
let chain = Promise.resolve(), broken = false, busy = true, timer, lastTick = 0, autoMuted = false;
function clock(seconds, decimals = false) {
  const n = Math.max(0, seconds), whole = Math.floor(n);
  return (whole >= 3600 ? Math.floor(whole / 3600) + ':' : '') +
    String(Math.floor(whole / 60) % 60).padStart(2,'0') + ':' +
    String(whole % 60).padStart(2,'0') + (decimals ? '.' + String(Math.floor((n % 1) * 10)) : '');
}
function notice(message) { $('notice').textContent = message; }
function fail(error) {
  broken = true; video.pause(); $('saved').textContent = 'Not saved';
  $('error').hidden = false;
  $('error').textContent = error.message + ' Your confirmed choices remain saved. ';
  const button = document.createElement('button');
  button.textContent = 'Reload saved choices'; button.onclick = () => location.reload();
  $('error').append(button);
  document.querySelectorAll('main button, main select, main textarea, #export').forEach(b => b.disabled = true);
}
async function post(path, body) {
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {method:'POST',signal:controller.signal,
      headers:{'Content-Type':'application/json','X-Review-Token':token},
      body:JSON.stringify({...body, revision:state.revision}), keepalive:true});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not save');
    return data;
  } catch (error) {
    if (controller.signal.aborted) throw new Error('The local server did not respond. Check it before reloading saved choices.');
    throw error;
  } finally {clearTimeout(timeout);}
}
function enqueue(fn) {
  chain = chain.then(async () => { if (!broken) return fn(); }).catch(fail);
  return chain;
}
function snapshot(extra = {}) {
  const patch = {event_id:current.id, note:$('note').value, view:viewIndex, ...extra};
  if (video.readyState >= 1 && !detached && $('unavailable').hidden) patch.source_position_sec = current.views[viewIndex].preview_start_sec + video.currentTime;
  return patch;
}
function save(patch) {
  $('saved').textContent = 'Saving…';
  return enqueue(async () => {
    const item = state.decisions[patch.event_id], view = patch.view ?? item.view;
    const decisionChanged = 'decision' in patch && patch.decision !== item.decision;
    const changed = state.current_id !== patch.event_id ||
      ['decision','note','view'].some(key => key in patch && patch[key] !== item[key]) ||
      ('source_position_sec' in patch && Math.abs(patch.source_position_sec -
        (item.source_positions?.[String(view)] ?? (cardsById.get(patch.event_id).views[view].base_preview_start_sec ??
          cardsById.get(patch.event_id).views[view].preview_start_sec) + (item.positions[String(view)] || 0))) > .05) ||
      ('position_sec' in patch && Math.abs(patch.position_sec - (item.positions[String(view)] || 0)) > .05);
    if (changed) state = await post('/api/save', patch);
    $('saved').textContent = 'Saved';
    // Position and note saves do not change the list. Keep focus and scroll intact.
    if (decisionChanged) renderList();
    $('undo').disabled = !state.history.length;
  });
}
function flush(extra = {}) { clearTimeout(timer); return save(snapshot(extra)); }
function filtered() {
  const selection = $('group-filter').value || 'all';
  const groups = queue.related_groups;
  const ids = selection === 'ungrouped' ? groups?.ungrouped_ids : groups?.groups.find(g => g.id === selection)?.event_ids;
  return queue.cards.filter(c => (!ids || ids.includes(c.id)) &&
    ($('filter').value === 'all' || state.decisions[c.id].decision === $('filter').value));
}
function groupControls() {
  const target=$('group-filter');
  target.replaceChildren();
  for(const [value,text] of [['all','All connections'],['ungrouped','Ungrouped moments'],
    ...(queue.related_groups?.groups || []).map((g,i)=>[g.id,'Related '+(i+1)+' · '+g.title+' ('+g.event_ids.length+')'])]) {
    const option=document.createElement('option');option.value=value;option.textContent=text;target.append(option);
  }
  target.value='all';target.onchange=renderList;
}
function showConnections() {
  const group=queue.related_groups?.groups.find(g=>g.event_ids.includes(current.id)), panel=$('connections');
  panel.hidden=!group;
  if(!group)return;
  $('connections-label').textContent='Related · '+group.event_ids.length+' moments';
  $('connections-body').replaceChildren();
  for(const id of group.event_ids){
    const card=cardsById.get(id),button=document.createElement('button');
    button.textContent=card.title+' · '+card.views[0].label+' '+clock(card.views[0].start_sec);
    button.dataset.id=id;button.setAttribute('aria-current',String(id===current.id));
    button.onclick=()=>navigate(id);$('connections-body').append(button);
  }
  for(const link of group.links){
    const p=document.createElement('p'),source=queue.cards.flatMap(c=>c.views).find(v=>v.source_id===link.source_id);
    p.textContent=cardsById.get(link.event_id).title+' → '+link.relationship+': '+cardsById.get(link.related_event_id).title+
      ' · '+(source?.label||link.source_id);
    $('connections-body').append(p);
  }
}
function renderList() {
  const decided = queue.cards.filter(c => state.decisions[c.id].decision !== 'unreviewed').length;
  $('count').textContent = decided + ' / ' + queue.cards.length + ' reviewed';
  const cards = filtered();
  for (const card of cards) {
    let row = listRows.get(card.id);
    if (!row) {
      const button = document.createElement('button');
      button.dataset.id = card.id; button.setAttribute('aria-current', 'false');
      const dot = document.createElement('span');
      const title = document.createElement('strong'); title.textContent = card.title;
      const meta = document.createElement('small');
      meta.textContent = card.views[0].label + ' · ' + clock(card.views[0].start_sec);
      button.append(dot, title, meta); button.onclick = () => navigate(card.id);
      row = {button, dot}; listRows.set(card.id, row);
    }
    const decision = state.decisions[card.id].decision;
    if (row.decision !== decision) {
      row.dot.className = 'dot ' + decision;
      row.dot.textContent = decision === 'unreviewed' ? '•' : labels[decision];
      row.decision = decision;
    }
  }
  if (!listedIds || cards.length !== listedIds.length || cards.some((c,i) => c.id !== listedIds[i])) {
    const fragment = document.createDocumentFragment();
    for (const card of cards) fragment.append(listRows.get(card.id).button);
    if (!cards.length) {
      const p = document.createElement('p'); p.textContent = 'No moments in this group.'; fragment.append(p);
    }
    $('list').replaceChildren(fragment);
    listedIds = cards.map(c => c.id);
  }
  if (listedCurrentId !== current?.id) {
    listRows.get(listedCurrentId)?.button.setAttribute('aria-current', 'false');
    listedCurrentId = current?.id;
  }
  // A row may just have become visible after changing filters.
  if (listedCurrentId) {
    listRows.get(listedCurrentId)?.button.setAttribute('aria-current', 'true');
  }
  $('export').disabled = !queue.cards.some(c => state.decisions[c.id].decision === 'keep');
  updateNav();
}
function updateNav() {
  if (!current) return;
  const cards = filtered(), index = cards.findIndex(c => c.id === current.id);
  $('previous').disabled = !cards.length || index === 0;
  $('next').disabled = !cards.length || index === cards.length - 1;
}
function refreshTime() {
  if (!current || video.readyState < 1) return;
  const view = detached || current.views[viewIndex];
  $('source-clock').textContent = view.label + ' ' + clock(view.preview_start_sec + video.currentTime, true);
  const uncertainties = [];
  for (const [index, button] of [...$('views').children].entries()) {
    if (detached) { button.disabled=true; continue; }
    const active = index === viewIndex;
    const mapping = active ? null : mapSwitch(current, viewIndex, index, video.currentTime);
    if (mapping) uncertainties.push(mapping.uncertainty_sec);
    button.disabled = !active && !mapping;
    button.title = active ? 'Current POV' : mapping ?
      'Same moment · sync ±' + mapping.uncertainty_sec + 's (' + (keys?.label('pov') || '') + ')' : 'No aligned coverage at this time';
  }
  if (!detached && current.views.length > 1) $('sync-status').textContent = uncertainties.length ?
    'Local sync ±' + Math.max(...uncertainties) + 's' :
    (current.sync_links?.length ? 'No alternate here' : 'No verified sync');
  timeline?.tick();
  scrub?.tick(); transcriptTick();
  contextControls();
}
async function autoplay() {
  try { await video.play(); }
  catch (error) {
    if (error.name === 'AbortError') return;
    if (error.name !== 'NotAllowedError') throw error;
    video.muted = true; autoMuted = true; $('enable-audio').hidden = false;
    try { await video.play(); }
    catch (second) {
      if (second.name === 'NotAllowedError') notice('Press Play to start.');
      else if (second.name !== 'AbortError') throw second;
    }
  }
}
function activateSound() {
  if (!autoMuted || !current || busy || broken) return;
  autoMuted = false; video.muted = false; $('enable-audio').hidden = true;
  if (!video.paused) video.play().catch(error => { if (error.name !== 'AbortError') notice('Press Play to enable sound.'); });
}
async function loadView(position, play = true) {
  detached=null;
  $('return-moment').hidden=true;
  $('unavailable').hidden = true;
  $('toggle-notes').disabled=false;
  $('check').hidden=!current.check;$('check').textContent=current.check?'Check: '+current.check:'';
  migrationStatus();
  for (const choice of ['keep','later','skip']) $(choice).disabled = false;
  $('decision').textContent=labels[state.decisions[current.id].decision];
  const view = current.views[viewIndex];
  $('title').textContent = view.title; $('summary').textContent = view.summary;
  $('clock').textContent = view.label + ' · ' + clock(view.start_sec) + '–' + clock(view.end_sec);
  $('position').textContent = (cardOrder.get(current.id) + 1) + ' / ' + queue.cards.length;
  $('preview-meta').textContent = view.label + ' audio';
  const links = current.sync_links || [];
  $('sync-status').textContent = current.views.length < 2 ? '' : links.length ?
    'Local sync ±' + Math.max(...links.map(l => l.uncertainty_sec)) + 's' : 'No verified sync';
  $('views').replaceChildren();
  current.views.forEach((v, index) => {
    const button = document.createElement('button'); button.textContent = v.label;
    button.setAttribute('aria-pressed', String(index === viewIndex));
    button.disabled = index !== viewIndex;
    button.onclick = () => switchView(index); $('views').append(button);
  });
  await loadMedia(view,position);
  refreshTime();
  timeline?.changed();
  scrub?.load();
  if(!$('transcript-panel').hidden) loadTranscript();
  if (play) await autoplay();
}
async function loadMedia(view,position) {
  video.pause();
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Preview took too long to load. Reload to retry.')), 20000);
    const done = () => { clearTimeout(timeout); resolve(); };
    video.onloadedmetadata = () => {
      const target = Math.min(position, Math.max(0, video.duration - .05));
      video.playbackRate = Number($('speed').value);
      if (Math.abs(video.currentTime - target) > .01) {
        video.addEventListener('seeked', done, {once:true}); video.currentTime = target;
      } else done();
    };
    video.onerror = () => { clearTimeout(timeout); reject(new Error('Preview could not load. Check the local server.')); };
    video.src = '/previews/' + view.file;
    video.load();
  });
}
async function display(id) {
  current = cardsById.get(id);
  viewIndex = state.decisions[id].view;
  $('note').value = state.decisions[id].note;
  $('toggle-notes').textContent = state.decisions[id].note ? 'Note •' : 'Note';
  $('decision').textContent = labels[state.decisions[id].decision];
  $('check').hidden = !current.check; $('check').textContent = current.check ? 'Check: ' + current.check : '';
  migrationStatus();
  showConnections();
  $('done').hidden = true; notice('');
  $('related').replaceChildren();
  for (const relation of current.related) {
    const related = cardsById.get(relation.event_id);
    if (!related) continue;
    const button = document.createElement('button'); button.textContent = relation.relationship + ': ' + related.title;
    button.title = 'Related moment; not simultaneous coverage'; button.onclick = () => navigate(related.id);
    $('related').append(button);
  }
  renderList(); $('undo').disabled = !state.history.length;
  await loadView(resumePosition(state.decisions[id], viewIndex, current.views[viewIndex]));
}
async function action(fn) {
  if (busy || broken) return;
  busy = true;
  try { await fn(); } catch (error) { fail(error); } finally { busy = false; }
}
function navigate(id) {
  if (id === current.id) {
    if (detached || !$('unavailable').hidden) return action(async () => {
      await loadView(detached?resumePosition(state.decisions[id],viewIndex,current.views[viewIndex]):video.currentTime);notice(''); });
    return;
  }
  return action(async () => {
    video.pause(); await flush();
    if (broken) return;
    await display(id); await save({event_id:id, view:viewIndex});
    closeMobileTimeline();
  });
}
function switchView(index) {
  if (detached) { notice('Choose a moment for aligned POV switching.'); return; }
  if (index === viewIndex) return;
  return action(async () => {
    const mapping = mapSwitch(current, viewIndex, index, video.currentTime);
    if (!mapping) { notice('No aligned coverage at this time.'); return; }
    video.pause(); await flush();
    if (broken) return;
    viewIndex = index;
    await loadView(mapping.position_sec);
    await save({event_id:current.id, view:viewIndex, source_position_sec:mapping.source_sec});
    notice('');
  });
}
function cyclePOV(direction = 1) {
  if (!current || busy || broken) return;
  if (detached) { notice('Transcript excerpts use their own source clock.'); return; }
  const result = nextView(current, viewIndex, video.currentTime, direction);
  if (result) switchView(result.index); else notice('No alternate coverage at this time.');
}
function migrationStatus() {
  const migration = current?.migration, target = $('migration-status');
  target.hidden = !migration || !['changed','new','ambiguous'].includes(migration.status);
  if (target.hidden) return;
  if (migration.status === 'changed') {
    const prefix = state.decisions[current.id].decision === 'unreviewed' ? 'Reconsider' : 'Revised moment';
    target.textContent = prefix+' · Previously '+labels[migration.previous_decision]+'. '+migration.reasons.join('; ')+'.';
  } else target.textContent = migration.status === 'ambiguous' ?
    'New review required · Prior matches are ambiguous; no choice was transferred.' : 'New moment · No prior choice transferred.';
}
function contextControls() {
  if (!current) return;
  const view = current.views[viewIndex], request = contextRequests.get(current.id+':'+viewIndex);
  const pending = request?.status === 'pending';
  $('extend-before').disabled = broken || !!detached || pending || !$('unavailable').hidden || view.preview_start_sec <= 0;
  $('extend-after').disabled = broken || !!detached || pending || !$('unavailable').hidden || view.preview_end_sec >= view.source_duration_sec;
  $('context-status').textContent = pending ? 'Preparing context…' : request?.status === 'error' ? 'Context failed · retry the arrow' : '';
  $('context-status').title = request?.error || '';
}
async function contextCall(path, request) {
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, request ? {method:'POST',signal:controller.signal,
      headers:{'Content-Type':'application/json','X-Review-Token':token},body:JSON.stringify(request)} : {signal:controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not extend this preview');
    return data;
  } catch (error) {
    if (controller.signal.aborted) throw new Error('Context request timed out. Retry the arrow.');
    throw error;
  } finally {clearTimeout(timeout);}
}
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function applyContext(card, index, preview) {
  while (busy && !broken) await delay(100);
  if (broken) return;
  if (detached || current.id !== card.id || viewIndex !== index) { card.views[index] = preview; return; }
  busy = true;
  const old = card.views[index], position = video.currentTime, play = !video.paused;
  const browse = timeline?.browse, unavailable = !$('unavailable').hidden;
  try {
    video.pause(); await flush();
    if (broken) return;
    const rebased = rebasePosition(old, preview, position);
    if (rebased === null) throw new Error('New context does not contain the current source time');
    card.views[index] = preview;
    try { await loadView(rebased, play && !unavailable); }
    catch (error) {
      card.views[index] = old;
      await loadView(position, play && !unavailable);
      throw error;
    }
    await flush();
  } finally {
    if (unavailable) {
      $('unavailable').hidden = false;
      for (const choice of ['keep','later','skip']) $(choice).disabled = true;
      if (timeline) { timeline.browse = browse; timeline.tick(); }
    }
    busy = false;
  }
}
async function extendContext(direction) {
  if (busy || broken || detached || !current || !$('unavailable').hidden) return;
  const card = current, index = viewIndex, key = card.id+':'+index, view = card.views[index];
  const previous = contextRequests.get(key);
  if (previous?.status === 'pending') return;
  const request = previous?.status === 'error' && previous.request.direction === direction ? previous.request :
    {event_id:card.id,view:index,direction,preview_start_sec:view.preview_start_sec,preview_end_sec:view.preview_end_sec};
  const task = {status:'pending',request}; contextRequests.set(key,task); contextControls();
  try {
    await flush();
    if (broken) return;
    let result = await contextCall('/api/context',request);
    while (result.status === 'pending') {
      await delay(750);
      try { result = await contextCall('/api/context/'+result.id); }
      catch (error) { result = await contextCall('/api/context',request); }
    }
    if (result.status !== 'ready') throw new Error(result.error || 'Preview context was not prepared');
    await applyContext(card,index,result.preview);
    contextRequests.delete(key);
  } catch (error) { task.status = 'error'; task.error = error.message; }
  finally { contextControls(); }
}
$('extend-before').onclick = () => extendContext('before');
$('extend-after').onclick = () => extendContext('after');
function closeMobileTimeline() {
  $('queue-panel').classList.remove('mobile-open'); $('toggle-queue').setAttribute('aria-expanded','false');
}
function playbackContext() {
  if(!current || !$('unavailable').hidden || video.readyState<1)return null;
  return {event_id:detached?'transcript':current.id,index:detached?detached.excerpt_id:viewIndex,
    view:detached||current.views[viewIndex],position:video.currentTime};
}
function sourceSeek(source) {
  if(busy||broken)return;
  const c=playbackContext();if(!c)return;
  video.currentTime=Math.max(0,Math.min(video.duration-.05,source-c.view.preview_start_sec));
  flush();
}
function transcriptTick() {
  if(!current||$('transcript-panel').hidden||video.readyState<1)return;
  const view=detached||current.views[viewIndex],time=view.preview_start_sec+video.currentTime;
  for(const item of transcriptRows) item.button.setAttribute('aria-current',String(
    $('unavailable').hidden&&item.row.source_id===view.source_id&&time>=item.row.start_sec&&time<item.row.end_sec));
}
function speechRanges(ranges) {
  const spans=[];
  for(const [start,end] of [...ranges].sort((a,b)=>a[0]-b[0])){
    const last=spans.at(-1);
    if(last&&start<=last[1]+.000001)last[1]=Math.max(last[1],end);
    else spans.push([start,end]);
  }
  return spans.map(([a,b])=>clock(a)+'–'+clock(b)).join(', ');
}
async function loadTranscript(append=false) {
  if(!current||$('transcript-panel').hidden)return;
  const serial=++transcriptSerial,scope=$('transcript-scope').value,view=detached||current.views[viewIndex];
  if(!append){transcriptOffset=0;transcriptRows=[];$('transcript-lines').replaceChildren();}
  const params=new URLSearchParams({q:$('transcript-query').value,offset:String(transcriptOffset),current_id:current.id});
  if(scope!=='all')params.set('source_id',view.source_id);
  if(scope==='preview'){params.set('start',String(view.preview_start_sec));params.set('end',String(view.preview_end_sec));}
  $('transcript-status').textContent='Loading transcript…';$('transcript-more').hidden=true;
  try{
    const response=await fetch('/api/transcript?'+params),result=await response.json();
    if(serial!==transcriptSerial)return;
    if(!response.ok)throw new Error(result.error||'Could not load transcript');
    if(result.status!=='ready'){
      $('transcript-status').textContent=result.status==='error'?'Transcript unavailable: '+result.error:'No transcript attached.';
      $('transcript-coverage').textContent=result.limitations||'Saved choices and video previews remain available.';return;
    }
    $('transcript-status').textContent=result.total+' matching lines'+(result.more?' · showing '+(result.offset+result.hits.length):'');
    const sources=new Map(queue.cards.flatMap(c=>c.views).map(v=>[v.source_id,v.label]));
    $('transcript-coverage').textContent='Rough speech · '+result.coverage.map(c=>(sources.get(c.source_id)||c.source_id)+' '+
      speechRanges(c.core_ranges_sec)).join(' · ')+
      (result.excluded_invalid_segments?' · '+result.excluded_invalid_segments+' invalid segments excluded':'')+
      (result.unmapped_sources.length?' · '+result.unmapped_sources.length+' unmapped sources':'');
    for(const row of result.hits){
      const button=document.createElement('button');button.className='transcript-line';button.dataset.line=row.id;
      button.setAttribute('aria-current','false');
      const meta=document.createElement('small');meta.textContent=row.label+' '+clock(row.start_sec,true)+' · stream '+row.audio_stream+
        (row.target?'':' · 30s excerpt');
      const text=document.createElement('span');text.textContent=row.text;
      button.title='Rough transcript · '+row.source+' · '+row.refs.map(r=>r.transcript_file+' #'+r.segment_index).join('; ');
      button.append(meta,text);button.onclick=()=>jumpTranscript(row);
      $('transcript-lines').append(button);transcriptRows.push({row,button});
    }
    if(!result.total){const p=document.createElement('p');p.textContent='No matching speech in this scope. Missing speech is inconclusive.';$('transcript-lines').append(p);}
    transcriptOffset=result.offset+result.hits.length;$('transcript-more').hidden=!result.more;transcriptTick();
  }catch(error){if(serial===transcriptSerial)$('transcript-status').textContent=error.message;}
}
function jumpTranscript(row) {
  return action(async()=>{
    video.pause();await flush();if(broken)return;
    if(row.target){
      const target=row.target,card=cardsById.get(target.event_id);
      await save({event_id:card.id,view:target.view,source_position_sec:row.start_sec});
      if(!broken)await display(card.id);
      notice('Transcript · '+row.label+' '+clock(row.start_sec,true));return;
    }
    $('unavailable').hidden=false;
    for(const name of ['keep','later','skip'])$(name).disabled=true;
    $('transcript-status').textContent='Preparing '+row.label+' '+clock(row.start_sec)+' excerpt…';
    let preview;
    try{preview=await VODAids.prepared('/api/transcript-preview',{line_id:row.id},token);}
    catch(error){$('transcript-status').textContent=error.message;notice('Excerpt unavailable. Return to a moment to continue.');return;}
    detached=preview;$('unavailable').hidden=true;$('notes').hidden=true;
    $('toggle-notes').disabled=true;$('toggle-notes').setAttribute('aria-expanded','false');
    $('decision').textContent='Transcript excerpt';$('position').textContent='30s excerpt';
    $('title').textContent='Transcript · '+row.label;$('summary').textContent=row.text;
    $('clock').textContent=row.label+' · '+clock(preview.preview_start_sec)+'–'+clock(preview.preview_end_sec);
    $('preview-meta').textContent='Stream '+row.audio_stream+' · rough speech';$('sync-status').textContent='Independent source clock';
    $('check').hidden=true;$('migration-status').hidden=true;$('views').replaceChildren();
    const label=document.createElement('button');label.textContent=row.label;label.disabled=true;$('views').append(label);
    await loadMedia(preview,row.start_sec-preview.preview_start_sec);
    $('return-moment').hidden=false;refreshTime();timeline.changed();scrub.load();await autoplay();
    $('transcript-status').textContent='Transcript excerpt · review choices apply to moments';
    notice('Choose a moment to resume review.');
    if($('transcript-scope').value==='preview')loadTranscript();
  });
}
$('show-moments').onclick=()=>{$('transcript-panel').hidden=true;$('moment-panel').hidden=false;
  $('show-moments').setAttribute('aria-pressed','true');$('show-transcript').setAttribute('aria-pressed','false');};
$('show-transcript').onclick=()=>{$('transcript-panel').hidden=false;$('moment-panel').hidden=true;
  $('show-moments').setAttribute('aria-pressed','false');$('show-transcript').setAttribute('aria-pressed','true');loadTranscript();};
$('transcript-query').addEventListener('input',()=>{clearTimeout(transcriptTimer);transcriptTimer=setTimeout(()=>loadTranscript(),250);});
$('transcript-scope').onchange=()=>loadTranscript();$('transcript-more').onclick=()=>loadTranscript(true);
$('return-moment').onclick=()=>navigate(current.id);
function timelineJump(time, segment) {
  return action(async () => {
    video.pause(); await flush();
    if (broken) return;
    if (!segment) {
      timeline.browse = time; timeline.tick(); $('unavailable').hidden = false;
      for (const choice of ['keep','later','skip']) $(choice).disabled = true;
      notice('Choose a shaded moment to preview.'); return;
    }
    const card = cardsById.get(segment.eid), view = card.views[segment.view];
    const position = time - segment.origin + segment.offset - view.preview_start_sec;
    if (position < 0 || position >= view.preview_end_sec - view.preview_start_sec) {
      notice('No prepared preview at this time.'); return;
    }
    await save({event_id:card.id,view:segment.view,source_position_sec:view.preview_start_sec+position});
    if (!broken) await display(card.id);
    closeMobileTimeline();
  });
}
$('return-preview').onclick = () => action(async () => {
  await loadView(detached?resumePosition(state.decisions[current.id],viewIndex,current.views[viewIndex]):video.currentTime);notice(''); });
function updateKeyHints() {
  if (!keys?.profile) return;
  for (const name of ['keep','later','skip']) $(name).querySelector('kbd').textContent = keys.label(name);
  for (const name of ['previous','next','undo']) $(name).title = VODKeys.labels[name]+' ('+keys.label(name)+')';
  $('extend-before').title = 'More context before · 15s ('+keys.label('extendBack')+')';
  $('extend-after').title = 'More context after · 15s ('+keys.label('extendForward')+')';
  $('key-hints').textContent = keys.label('previous')+' / '+keys.label('next')+' moments · '+keys.label('pov')+' POV · '+keys.label('play')+' play';
  refreshTime();
}
function step(delta) {
  if (!current) return;
  const cards = filtered(); let index = cards.findIndex(c => c.id === current.id);
  if (index < 0) index = delta > 0 ? -1 : cards.length;
  if (cards[index + delta]) navigate(cards[index + delta].id);
}
function decide(decision) {
  if (detached || !$('unavailable').hidden) return;
  return action(async () => {
    video.pause(); await flush({decision});
    if (broken) return;
    $('decision').textContent = labels[decision];
    migrationStatus();
    const pos = cardOrder.get(current.id);
    const pending = filtered().filter(c => c.id !== current.id &&
      (['all','unreviewed'].includes($('filter').value) ? state.decisions[c.id].decision === 'unreviewed' : true));
    const next = pending.find(c => cardOrder.get(c.id) > pos) || pending[0];
    if (next) { await display(next.id); await save({event_id:next.id, view:viewIndex}); }
    else { $('done').hidden = false; $('done').textContent = 'Group reviewed. Revisit Later or export your choices.'; }
  });
}
for (const choice of ['keep','later','skip']) $(choice).onclick = () => decide(choice);
$('undo').onclick = () => action(async () => {
  video.pause(); await flush();
  await enqueue(async () => { state = await post('/api/undo', {}); });
  if (!broken) { await display(state.current_id); $('saved').textContent = 'Saved'; }
});
$('note').addEventListener('input', () => {
  clearTimeout(timer); $('saved').textContent = 'Saving…';
  $('toggle-notes').textContent = $('note').value ? 'Note •' : 'Note';
  timer = setTimeout(() => { if (!busy) flush(); }, 400);
});
$('note').addEventListener('blur', () => { if (!busy && !broken) flush(); });
$('filter').onchange = renderList;
$('speed').onchange = () => { video.playbackRate = Number($('speed').value); };
$('previous').onclick = () => step(-1); $('next').onclick = () => step(1);
$('toggle-queue').onclick = () => {
  const shown = $('queue-panel').classList.toggle('mobile-open');
  $('toggle-queue').setAttribute('aria-expanded',String(shown)); timeline?.draw();
};
for (const [button, panel] of [['toggle-info','info'],['toggle-notes','notes']]) {
  $(button).onclick = () => { $(panel).hidden = !$(panel).hidden; $(button).setAttribute('aria-expanded', String(!$(panel).hidden)); };
}
video.addEventListener('timeupdate', () => {
  refreshTime();
  if (current && !busy && !broken && !video.paused && video.readyState >= 1 && Date.now() - lastTick > 5000) {
    lastTick = Date.now(); flush();
  }
});
video.addEventListener('seeked', refreshTime);
video.addEventListener('pause', () => { if (current && !busy && !broken && video.readyState >= 1) flush(); });
video.addEventListener('volumechange', () => { if (!video.muted) { autoMuted = false; $('enable-audio').hidden = true; } });
$('enable-audio').onclick = () => { activateSound(); autoplay().catch(fail); };
document.addEventListener('pointerdown', activateSound, true);
document.addEventListener('visibilitychange', () => { if (document.hidden && current && !busy && !broken) flush(); });
window.addEventListener('beforeunload', () => { if (current && !busy && !broken) flush(); });
document.addEventListener('keydown', event => {
  if (/INPUT|TEXTAREA|SELECT/.test(event.target.tagName) || event.target.isContentEditable ||
      $('keys-dialog').open || event.target.closest?.('.segment,.transcript-line,#waveform') || event.repeat || broken || !current) return;
  activateSound();
  if (event.key === 'Escape') {
    $('info').hidden = true; $('toggle-info').setAttribute('aria-expanded','false');
    closeMobileTimeline(); return;
  }
  const command = keys?.match(event);
  if (!command) return;
  event.preventDefault();
  if (busy) return;
  if (['keep','later','skip'].includes(command)) decide(command);
  else if (command === 'undo') $('undo').click();
  else if (command === 'pov' || command === 'povBack') cyclePOV(command === 'pov' ? 1 : -1);
  else if (command === 'previous' || command === 'next') step(command === 'next' ? 1 : -1);
  else if (!$('unavailable').hidden) notice('Return to a prepared moment to play or seek.');
  else if (command === 'play') video.paused ? autoplay().catch(fail) : video.pause();
  else if (command === 'extendBack' || command === 'extendForward') extendContext(command === 'extendBack' ? 'before' : 'after');
  else video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + (command === 'forward' ? 5 : -5)));
}, true);
function exportQueue(mode) {
  return action(async () => {
    video.pause(); await flush();
    await enqueue(async () => {
      try {
        const result = await post('/api/export', {mode});
        $('export-result').replaceChildren();
        const a = document.createElement('a'); a.href = result.url;
        a.textContent = 'Download XML · ' + result.count + ' moments'; a.download = 'Moment-Review.xml';
        a.title = 'Saved at ' + result.path; $('export-result').append(a);
      } catch (error) { $('export-result').textContent = 'Export failed: ' + error.message; }
    });
  });
}
$('export').onclick = () => exportQueue('keep'); $('export-all').onclick = () => exportQueue('all');
(async () => {
  try {
    const response = await fetch('/api/queue'), data = await response.json();
    if (!response.ok) throw new Error(data.error);
    queue = data.queue; state = data.state; token = data.token;
    cardsById = new Map(queue.cards.map(c => [c.id, c]));
    cardOrder = new Map(queue.cards.map((c,i) => [c.id, i]));
    groupControls();
    keys = new VODKeys(token,updateKeyHints,() => video.pause());
    await keys.load();
    scrub = new VODAids.Scrub(playbackContext,sourceSeek,clock,token,(c,data)=>timeline?.setAids(c,data));
    timeline = new VODTimeline(queue.timeline,() => ({card:detached?null:current,index:viewIndex,position:video.currentTime,
      detached:detached?{source_id:detached.source_id,source_sec:detached.preview_start_sec+video.currentTime}:null}),timelineJump,clock,scrub,queue.cards);
    $('coverage').textContent = queue.coverage;
    await display(state.current_id); $('saved').textContent = 'Saved';
  } catch (error) { fail(error); } finally { busy = false; }
})();
