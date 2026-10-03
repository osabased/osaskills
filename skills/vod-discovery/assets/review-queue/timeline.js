'use strict';
// Source seconds and main-timeline seconds stay separate. Only local anchors map POVs.
window.VODTimeline = class {
  constructor(data, context, jump, clock) {
    this.data = data; this.context = context; this.jump = jump; this.clock = clock;
    this.start = 0; this.span = Math.min(300, data.total); this.browse = null;
    this.svg = document.getElementById('stacked'); this.overview = document.getElementById('overview');
    this.pan = document.getElementById('pan');
    this.svg.style.height = Math.max(155, 38 * data.lanes.length + 42) + 'px';
    this.svg.onclick = e => this.seek(this.pointer(this.svg, e, this.start, this.span));
    this.overview.onclick = e => { const time = this.pointer(this.overview, e, 0, data.total); this.fit(time); this.draw(); this.seek(time); };
    this.pan.oninput = () => { this.start = Number(this.pan.value); this.draw(); };
    document.getElementById('zoom-in').onclick = () => this.zoom(.5);
    document.getElementById('zoom-out').onclick = () => this.zoom(2);
    document.getElementById('full-session').onclick = () => { this.start = 0; this.span = data.total; this.draw(); };
    document.getElementById('current-moment').onclick = () => { this.span = Math.min(90, data.total); this.fit(this.time() ?? this.start); this.draw(); };
    this.resize = new ResizeObserver(() => this.draw()); this.resize.observe(this.svg);
  }
  element(tag, attrs = {}, text = '') {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,v);
    e.textContent = text; return e;
  }
  time() {
    if (this.browse !== null) return this.browse;
    const {card, index, position} = this.context();
    if (!card) return null;
    const view = card.views[index], source = view.preview_start_sec + position;
    const part = this.data.parts.find(p => p.id === view.source_id);
    if (part) return part.start + source;
    const link = (card.sync_links || []).find(l => l.source_id === view.source_id &&
      source >= l.source_start_sec && source < l.source_end_sec);
    if (!link) return null;
    return this.data.parts.find(p => p.id === link.main_source_id).start + source - link.offset_sec;
  }
  fit(time) { this.start = Math.max(0, Math.min(this.data.total - this.span, time - this.span / 2)); }
  zoom(factor) { const time = this.time() ?? this.start + this.span / 2;
    this.span = Math.min(this.data.total, Math.max(25, this.span * factor)); this.fit(time); this.draw(); }
  changed() {
    this.browse = null;
    const time = this.time();
    if (time !== null && (time < this.start || time > this.start + this.span)) this.fit(time);
    this.draw();
  }
  x(time, start, span) { return 60 + (time - start) / span * (this.width - 68); }
  pointer(svg, event, start, span) {
    const box = svg.getBoundingClientRect();
    return Math.max(start, Math.min(start + span, start + (event.clientX - box.left - 60) / (box.width - 68) * span));
  }
  seek(time, segment) {
    const {card} = this.context();
    const candidates = this.data.segments.filter(s => s.lane === 'main' && time >= s.start && time < s.end);
    segment = segment || candidates.find(s => s.eid === card?.id) || candidates[0];
    this.jump(time, segment);
  }
  draw() {
    const {svg, overview, data} = this;
    this.width = svg.getBoundingClientRect().width;
    if (this.width < 80) return;
    const height = svg.getBoundingClientRect().height, smallHeight = overview.getBoundingClientRect().height;
    svg.setAttribute('viewBox', `0 0 ${this.width} ${height}`);
    overview.setAttribute('viewBox', `0 0 ${this.width} ${smallHeight}`);
    svg.replaceChildren(); overview.replaceChildren();
    this.pan.max = Math.max(0, data.total - this.span); this.pan.value = this.start;
    document.getElementById('range-label').textContent = this.clock(this.start) + '–' + this.clock(this.start + this.span);
    const steps = this.width < 500 ? 3 : 5;
    for (let i = 0; i <= steps; i++) {
      const time = this.start + this.span * i / steps, x = this.x(time, this.start, this.span);
      svg.append(this.element('line', {x1:x,x2:x,y1:20,y2:height-14,class:'gridline'}),
        this.element('text', {x,y:15,'text-anchor':i === steps ? 'end' : 'start',class:'ruler-text'}, this.clock(time)));
    }
    const ys = {}, step = (height-42) / data.lanes.length, rowHeight = Math.min(65, step-7);
    data.lanes.forEach((lane, i) => {
      const y = 26+i*step; ys[lane.id] = y;
      const label = this.element('text', {x:4,y:y+rowHeight/2+4,class:'lane-label'}, lane.label.length > 8 ? lane.label.slice(0,7)+'…' : lane.label);
      label.append(this.element('title', {}, lane.label));
      svg.append(label, this.element('rect', {x:60,y,width:this.width-68,height:rowHeight,rx:4,class:'lane-bg'}));
    });
    for (const part of data.parts) {
      const x = Math.max(60,this.x(part.start,this.start,this.span)), right = Math.min(this.width-8,this.x(part.end,this.start,this.span));
      if (right <= x) continue;
      svg.append(this.element('rect', {x,y:ys.main,width:right-x,height:rowHeight,class:'base-part'}));
      if (right-x > 140) svg.append(this.element('text', {x:x+8,y:ys.main+rowHeight/2+4,class:'part-name'},part.label));
      if (part.start > this.start) svg.append(this.element('line', {x1:x,x2:x,y1:ys.main,y2:ys.main+rowHeight,class:'part-boundary'}));
    }
    const {card,index} = this.context();
    for (const seg of data.segments) {
      const x = Math.max(60,this.x(seg.start,this.start,this.span)), right = Math.min(this.width-8,this.x(seg.end,this.start,this.span));
      if (right <= x) continue;
      const active = seg.eid === card?.id, chosen = active && seg.view === index;
      const lane = data.lanes.find(l => l.id === seg.lane).label;
      const label = `${seg.label} · ${lane} · ${this.clock(seg.start)}–${this.clock(seg.end)}` + (seg.uncertainty ? ` · sync ±${seg.uncertainty}s` : '');
      const group = this.element('g', {class:'segment '+(seg.lane === 'main' ? 'main-segment' : 'alt-segment')+(active?' current':'')+(chosen?' chosen':''),
        tabindex:0,role:'button','aria-label':label,'data-event':seg.eid,'data-view':seg.view});
      group.append(this.element('rect', {x,y:ys[seg.lane]+2,width:Math.max(.8,right-x),height:rowHeight-4,rx:3}),this.element('title',{},label));
      if (right-x > Math.max(45,seg.label.length*5.5+8)) group.append(this.element('text',{x:x+5,y:ys[seg.lane]+rowHeight/2+4,class:'segment-label'},seg.label));
      group.onclick = e => { e.stopPropagation(); this.seek(Math.max(seg.start,Math.min(seg.end-.001,this.pointer(svg,e,this.start,this.span))),seg); };
      group.onkeydown = e => { if (['Enter','Space'].includes(e.code)) { e.preventDefault(); e.stopPropagation(); this.seek(seg.start,seg); } };
      svg.append(group);
    }
    svg.append(this.element('text',{x:60,y:height-2,class:'ruler-text'},'Alternates above · main below'));
    overview.append(this.element('rect',{x:60,y:9,width:this.width-68,height:12,rx:3,class:'overview-bg'}));
    for (const part of data.parts) {
      const x = this.x(part.start,0,data.total);
      overview.append(this.element('line',{x1:x,x2:x,y1:9,y2:21,class:'part-boundary'}));
      if (part.end-part.start > data.total*.2) overview.append(this.element('text',{x:x+5,y:18,class:'overview-part'},part.label));
    }
    for (const seg of data.segments.filter(s => s.lane === 'main')) overview.append(this.element('rect',{
      x:this.x(seg.start,0,data.total),y:9,width:Math.max(.7,(seg.end-seg.start)/data.total*(this.width-68)),height:12,class:'overview-moment'}));
    overview.append(this.element('rect',{x:this.x(this.start,0,data.total),y:5,width:Math.max(2,this.span/data.total*(this.width-68)),height:20,rx:2,class:'view-window'}),
      this.element('text',{x:0,y:19,class:'lane-label'},'Full VOD'),this.element('text',{x:60,y:smallHeight-2,class:'ruler-text'},'00:00'),
      this.element('text',{x:this.width-8,y:smallHeight-2,'text-anchor':'end',class:'ruler-text'},this.clock(data.total)));
    this.tick();
  }
  tick() {
    const cursor = this.time(), total = this.data.total;
    for (const svg of [this.svg,this.overview]) svg.querySelectorAll('.playhead,.playhead-head').forEach(e => e.remove());
    if (this.width >= 80 && cursor !== null) {
      const ox = this.x(cursor,0,total);
      this.overview.append(this.element('line',{x1:ox,x2:ox,y1:3,y2:28,class:'playhead'}));
      if (cursor >= this.start && cursor <= this.start+this.span) {
        const x = this.x(cursor,this.start,this.span);
        this.svg.append(this.element('line',{x1:x,x2:x,y1:23,y2:this.svg.getBoundingClientRect().height-17,class:'playhead'}),
          this.element('path',{d:`M ${x-4} 22 L ${x+4} 22 L ${x} 28 Z`,class:'playhead-head'}));
      }
    }
    document.getElementById('timeline-clock').textContent = cursor === null ? 'No main-timeline anchor' : this.clock(cursor,true)+' / '+this.clock(total);
    document.getElementById('timeline-position').textContent = cursor === null ? 'Independent POV' : (cursor/total*100).toFixed(1)+'% through';
  }
};
