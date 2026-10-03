/* Translate source clocks only within authored local anchor windows. */
(function (root) {
  'use strict';
  function mapSwitch(card, fromIndex, toIndex, position) {
    const from = card.views[fromIndex], to = card.views[toIndex];
    if (!from || !to || !Number.isFinite(position) || position < 0) return null;
    const sourceTime = from.preview_start_sec + position;
    if (sourceTime >= from.preview_end_sec) return null;
    if (fromIndex === toIndex) return {position_sec: position, source_sec: sourceTime, uncertainty_sec: 0};
    const edges = [];
    for (const link of card.sync_links || []) {
      edges.push({from: link.main_source_id, to: link.source_id,
        offset: link.offset_sec, start: link.source_start_sec - link.offset_sec,
        end: link.source_end_sec - link.offset_sec, uncertainty: link.uncertainty_sec});
      edges.push({from: link.source_id, to: link.main_source_id,
        offset: -link.offset_sec, start: link.source_start_sec,
        end: link.source_end_sec, uncertainty: link.uncertainty_sec});
    }
    const pending = [{source: from.source_id, time: sourceTime, uncertainty: 0, visited: [from.source_id]}];
    while (pending.length) {
      const node = pending.shift();
      for (const edge of edges) {
        if (edge.from !== node.source || node.visited.includes(edge.to) || node.time < edge.start || node.time >= edge.end) continue;
        const time = node.time + edge.offset, uncertainty = node.uncertainty + edge.uncertainty;
        if (edge.to === to.source_id && time >= to.preview_start_sec && time < to.preview_end_sec) {
          return {position_sec: time - to.preview_start_sec, source_sec: time, uncertainty_sec: uncertainty};
        }
        pending.push({source: edge.to, time, uncertainty, visited: [...node.visited, edge.to]});
      }
    }
    // No anchor/current overlap: do not clamp or use a stale saved position.
    return null;
  }
  function nextView(card, fromIndex, position, direction = 1) {
    for (let n = 1; n < card.views.length; n++) {
      const index = (fromIndex + direction * n + card.views.length) % card.views.length;
      const mapped = mapSwitch(card, fromIndex, index, position);
      if (mapped) return {index, ...mapped};
    }
    return null;
  }
  const api = {mapSwitch, nextView};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.VODPlayback = api;
})(globalThis);
