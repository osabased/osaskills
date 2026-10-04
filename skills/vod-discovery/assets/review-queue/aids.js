/* Cached peaks and frame maps. No browser audio decoding or source-video scrubbing. */
(function (root) {
  'use strict';
  function thumbnailAt(data, source) {
    const frames = data?.thumbnails?.frames || [];
    let frame = frames[0];
    for (const candidate of frames) {
      if (candidate.source_sec > source) break;
      frame = candidate;
    }
    return frame || null;
  }
  function peaksIn(data, start, end, count) {
    const wave = data?.waveform;
    if (!wave?.peaks?.length || !(wave.step_sec > 0) || !(end > start)) return [];
    return Array.from({length:count}, (_, i) => {
      const left=start+(end-start)*i/count,right=start+(end-start)*(i+1)/count;
      if(right<=data.preview_start_sec||left>=data.preview_end_sec)return 0;
      const a = Math.max(0, Math.floor((start + (end-start)*i/count - data.preview_start_sec) / wave.step_sec));
      const b = Math.min(wave.peaks.length, Math.max(a+1, Math.ceil((start + (end-start)*(i+1)/count - data.preview_start_sec) / wave.step_sec)));
      let peak = 0;
      for (let n=a; n<b; n++) peak = Math.max(peak, wave.peaks[n]);
      return peak;
    });
  }
  async function navigationCall(path, body, token) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(path, body ? {method:'POST', signal:controller.signal,
        headers:{'Content-Type':'application/json','X-Review-Token':token},body:JSON.stringify(body)} : {signal:controller.signal});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Preview navigation failed');
      return data;
    } catch (error) {
      if (controller.signal.aborted) throw new Error('Preview preparation did not respond. Retry.');
      throw error;
    } finally {clearTimeout(timer);}
  }
  async function prepared(path, body, token) {
    let job = await navigationCall(path, body, token), wait = 800;
    while (job.status === 'pending') {
      await new Promise(resolve => setTimeout(resolve, wait));
      wait = Math.min(2000, wait + 400);
      job = await navigationCall('/api/navigation/'+job.id, null, token);
    }
    if (job.status !== 'ready') throw new Error(job.error || 'Could not prepare preview navigation');
    return job.result;
  }
  class Scrub {
    constructor(context, seek, clock, token, changed) {
      this.context=context; this.seek=seek; this.clock=clock; this.token=token; this.changed=changed;
      this.svg=document.getElementById('waveform'); this.tooltip=document.getElementById('hover-frame');
      this.status=document.getElementById('aids-status'); this.data=null; this.generation=0;
      this.cache=new Map(); this.promises=new Map();
      this.svg.onpointermove=e=>this.hover(this.sourceAt(e),e,this.data);
      this.svg.onpointerleave=()=>this.hide();
      this.svg.onclick=e=> { const source=this.sourceAt(e); if(source!==null) this.seek(source); };
      this.svg.onkeydown=e=> {
        if (!['ArrowLeft','ArrowRight','Home','End'].includes(e.code)) return;
        e.preventDefault(); e.stopPropagation();
        const c=this.context(); if (!c) return;
        const v=c.view, source=e.code==='Home'?v.preview_start_sec:e.code==='End'?v.preview_end_sec-.05:
          v.preview_start_sec+c.position+(e.code==='ArrowRight'?1:-1)*(e.shiftKey?5:1);
        this.seek(Math.max(v.preview_start_sec,Math.min(v.preview_end_sec-.05,source)));
      };
      new ResizeObserver(()=>this.draw()).observe(this.svg);
      document.getElementById('retry-aids').onclick=()=>this.load(true);
    }
    element(tag,attrs={}) {
      const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
      for(const [key,value] of Object.entries(attrs)) e.setAttribute(key,value);
      return e;
    }
    key(c) { return c? [c.event_id,c.index,c.view.file,c.view.preview_start_sec,c.view.preview_end_sec].join(':'):''; }
    async get(c,retry=false) {
      const key=this.key(c);
      if(retry) this.cache.delete(key);
      if(this.cache.has(key)) return this.cache.get(key);
      if(this.promises.has(key)) return this.promises.get(key);
      const body=c.view.excerpt_id?{excerpt_id:c.view.excerpt_id}:{event_id:c.event_id,view:c.index};
      const promise=prepared('/api/aids',body,this.token).then(data=>{this.cache.set(key,data);return data;})
        .finally(()=>this.promises.delete(key));
      this.promises.set(key,promise);return promise;
    }
    async load(retry=false) {
      const c=this.context(), generation=++this.generation;
      this.data=null; this.hide(); this.draw();
      document.getElementById('retry-aids').hidden=true;
      if(!c) {this.status.textContent='';return;}
      this.status.textContent='Preparing waveform and thumbnails…';
      try {
        const data=await this.get(c,retry);
        if(generation!==this.generation||this.key(c)!==this.key(this.context())) return;
        this.data=data;
        this.status.textContent=data.waveform.status==='no_audio'?'No audio stream · thumbnails ready':'';
        this.draw(); this.changed?.(c,data);
      } catch(error) {
        if(generation!==this.generation) return;
        this.status.textContent='Navigation aids unavailable';this.status.title=error.message;
        document.getElementById('retry-aids').hidden=false;
      }
    }
    sourceAt(e) {
      const c=this.context(); if(!c) return null;
      const box=this.svg.getBoundingClientRect(), fraction=Math.max(0,Math.min(1,(e.clientX-box.left)/box.width));
      return c.view.preview_start_sec+fraction*(c.view.preview_end_sec-c.view.preview_start_sec);
    }
    draw() {
      const c=this.context(), width=this.svg.getBoundingClientRect().width;
      this.svg.replaceChildren();if(!c||width<10)return;
      const v=c.view,start=v.preview_start_sec,end=v.preview_end_sec;
      this.svg.setAttribute('viewBox',`0 0 ${width} 36`);
      this.svg.setAttribute('aria-valuemin',start);this.svg.setAttribute('aria-valuemax',end);
      this.svg.setAttribute('aria-label',v.label+' preview source time');
      this.svg.append(this.element('line',{x1:0,x2:width,y1:18,y2:18,class:'wave-baseline'}));
      if(Number.isFinite(v.start_sec))this.svg.append(this.element('rect',{x:Math.max(0,(v.start_sec-start)/(end-start)*width),y:1,
        width:Math.min(width,(v.end_sec-v.start_sec)/(end-start)*width),height:34,class:'wave-moment'}));
      const peaks=peaksIn(this.data,start,end,Math.max(1,Math.round(width/2)));
      if(peaks.length){
        const top=peaks.map((p,i)=>`${i/(peaks.length-1||1)*width},${18-p*15}`).join(' ');
        const bottom=peaks.map((p,i)=>`${i/(peaks.length-1||1)*width},${18+p*15}`).reverse().join(' ');
        this.svg.append(this.element('polygon',{points:top+' '+bottom,class:'wave-peaks'}));
      }
      this.tick();
    }
    tick() {
      const c=this.context();if(!c)return;
      const source=c.view.preview_start_sec+c.position,width=this.svg.getBoundingClientRect().width;
      this.svg.querySelectorAll('.wave-cursor').forEach(e=>e.remove());
      const x=(source-c.view.preview_start_sec)/(c.view.preview_end_sec-c.view.preview_start_sec)*width;
      this.svg.append(this.element('line',{x1:x,x2:x,y1:0,y2:36,class:'wave-cursor'}));
      this.svg.setAttribute('aria-valuenow',source);this.svg.setAttribute('aria-valuetext',this.clock(source,true));
      document.getElementById('wave-start').textContent=this.clock(c.view.preview_start_sec);
      document.getElementById('wave-end').textContent=this.clock(c.view.preview_end_sec);
    }
    hover(source,e,data=null,label=this.context()?.view.label) {
      if(source===null)return;
      const frame=thumbnailAt(data,source), thumb=document.getElementById('hover-image');
      thumb.hidden=!frame;
      if(frame){
        thumb.style.backgroundImage=`url(/navigation/${data.thumbnails.file})`;
        thumb.style.backgroundPosition=`-${frame.x}px -${frame.y}px`;
      }
      document.getElementById('hover-time').textContent=label+' '+this.clock(source,true);
      document.getElementById('hover-sample').textContent=frame?'Frame '+this.clock(frame.source_sec,true):'Thumbnail not prepared';
      this.tooltip.hidden=false;
      const width=this.tooltip.getBoundingClientRect().width||180;
      this.tooltip.style.left=Math.max(6,Math.min(innerWidth-width-6,e.clientX-width/2))+'px';
      this.tooltip.style.top=Math.max(6,e.clientY-(frame?140:48))+'px';
    }
    hide(){this.tooltip.hidden=true;}
  }
  const api={thumbnailAt,peaksIn,prepared,Scrub};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.VODAids=api;
})(globalThis);
