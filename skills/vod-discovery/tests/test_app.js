/* Exercise the real queue UI against a small DOM harness; no editor profile or media. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

let created = 0;
const elements = new Map();
class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase(); this.children = []; this.attributes = {};
    this.dataset = {}; this.style = {}; this.value = ''; this.hidden = false;
    this.classList = {remove(){}, toggle(){return false;}};
    this.listeners = {}; this.replacements = 0; created++;
  }
  append(...nodes) {
    for (const node of nodes) {
      if (node.tagName === '#FRAGMENT') { this.append(...[...node.children]); continue; }
      if (node.parent) node.parent.children.splice(node.parent.children.indexOf(node), 1);
      node.parent = this; this.children.push(node);
    }
  }
  replaceChildren(...nodes) {
    this.replacements++;
    for (const child of this.children) child.parent = null;
    this.children = []; this.append(...nodes);
  }
  setAttribute(key, value) { this.attributes[key] = value; }
  getAttribute(key) { return this.attributes[key]; }
  addEventListener(key, callback) { this.listeners[key] = callback; }
  focus() { document.activeElement = this; }
}
const document = {
  activeElement: null,
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, new Element('div'));
    return elements.get(id);
  },
  createElement: tag => new Element(tag),
  createDocumentFragment: () => new Element('#fragment'),
  addEventListener(){}, querySelectorAll(){return [];}
};
const cards = Array.from({length:500}, (_, i) => ({id:'e'+i, title:'Moment '+i,
  summary:'Observed moment', check:'', related:[], views:[{label:'Main', start_sec:i * 10}]}));
const initial = {revision:0, current_id:'e0', history:[],
  decisions:Object.fromEntries(cards.map(c => [c.id, {decision:'unreviewed', note:'', view:0, positions:{}}]))};
let persisted = structuredClone(initial);
let requests = 0;
let unanswered = false;
document.getElementById('video').pause = () => {};
const context = vm.createContext({document, window:{addEventListener(){}},
  setTimeout:(fn,ms) => setTimeout(fn,unanswered ? 1 : ms),clearTimeout,AbortController,
  VODPlayback:require('../assets/review-queue/playback.js'), fixture:{cards, state:initial},
  fetch:async (url, options) => {
    // Let tests supply the fixture directly rather than running the browser startup.
    if (url === '/api/queue') return new Promise(() => {});
    if (unanswered) return new Promise((resolve,reject) =>
      options.signal.addEventListener('abort',() => reject(new Error('Aborted')),{once:true}));
    assert.equal(url, '/api/save'); requests++;
    const patch = JSON.parse(options.body);
    assert.equal(patch.revision, persisted.revision);
    const item = persisted.decisions[patch.event_id];
    if ('decision' in patch && patch.decision !== item.decision) {
      persisted.history.push({id:patch.event_id, decision:item.decision});
    }
    for (const key of ['decision','note','view']) if (key in patch) item[key] = patch[key];
    if ('position_sec' in patch) item.positions[String(patch.view ?? item.view)] = patch.position_sec;
    persisted.current_id = patch.event_id; persisted.revision++;
    return {ok:true, json:async () => structuredClone(persisted)};
  }});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/review-queue/app.js'), 'utf8'), context);
vm.runInContext(`queue = {cards:fixture.cards}; state = fixture.state; current = queue.cards[0];
  cardsById = new Map(queue.cards.map(c => [c.id,c]));
  cardOrder = new Map(queue.cards.map((c,i) => [c.id,i]));
  document.getElementById('filter').value = 'all'; renderList();`, context);

(async () => {
  const list = elements.get('list'), originalRows = [...list.children];
  assert.equal(list.children.length, 500);
  assert.equal(originalRows[0].getAttribute('aria-current'), 'true');
  originalRows[250].focus();
  document.getElementById('saved');
  const initialCreated = created, initialReplacements = list.replacements;
  for (const position of [5,10,15]) {
    await vm.runInContext(`save({event_id:'e0', position_sec:${position}})`, context);
  }
  await vm.runInContext("save({event_id:'e0', note:'Saved note'})", context);
  assert.equal(persisted.decisions.e0.note, 'Saved note');
  assert.equal(persisted.decisions.e0.positions['0'], 15);
  assert.equal(created, initialCreated, 'Autosave must not allocate new list nodes');
  assert.equal(list.replacements, initialReplacements, 'Autosave must not replace the list');
  assert.equal(document.activeElement, originalRows[250]);

  vm.runInContext('current = queue.cards[250]; renderList();', context);
  assert.equal(created, initialCreated, 'Navigation must reuse rows');
  assert.equal(list.replacements, initialReplacements);
  assert.equal(originalRows[0].getAttribute('aria-current'), 'false');
  assert.equal(originalRows[250].getAttribute('aria-current'), 'true');
  await vm.runInContext("save({event_id:'e250', decision:'keep'})", context);
  assert.equal(list.children[250], originalRows[250]);
  assert.equal(originalRows[250].children[0].textContent, 'Keep');
  assert.equal(elements.get('count').textContent, '1 / 500 reviewed');
  assert.equal(elements.get('export').disabled, false);

  elements.get('filter').value = 'keep'; context.renderList();
  assert.deepEqual(list.children, [originalRows[250]]);
  elements.get('filter').value = 'later'; context.renderList();
  assert.equal(list.children[0].textContent, 'No moments in this group.');
  elements.get('filter').value = 'all'; context.renderList();
  assert.deepEqual(list.children, originalRows);
  const beforeNoop = requests;
  await vm.runInContext("save({event_id:'e250', decision:'keep'})", context);
  assert.equal(requests, beforeNoop, 'An unchanged choice must not save again');
  // Undo/reload replaces the state object; cached rows must reflect its restored choices.
  vm.runInContext("state = {...state, decisions:{...state.decisions, e250:{...state.decisions.e250, decision:'unreviewed'}}}; renderList();", context);
  assert.equal(originalRows[250].children[0].textContent, '•');
  assert.equal(elements.get('count').textContent, '0 / 500 reviewed');
  assert.equal(elements.get('export').disabled, true);
  const confirmed = structuredClone(persisted);
  unanswered = true;
  await vm.runInContext("save({event_id:'e250', note:'Unconfirmed note'})",context);
  assert.deepEqual(persisted,confirmed,'An unanswered save must retain the last confirmed state');
  assert(vm.runInContext('broken',context));
  assert.equal(elements.get('saved').textContent,'Not saved');
  assert.equal(elements.get('error').hidden,false);
  assert(elements.get('error').textContent.includes('server did not respond'));
  console.log('Queue UI checks passed: stable rows/focus, autosave, decisions, filters, restored state and unanswered-save recovery.');
})().catch(error => {console.error(error); process.exitCode = 1;});
