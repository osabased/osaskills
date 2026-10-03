'use strict';
window.VODKeys = class {
  static labels = {previous:'Previous moment',next:'Next moment',pov:'Next POV',povBack:'Previous POV',
    play:'Play / pause',back:'Seek back 5s',forward:'Seek forward 5s',keep:'Keep',later:'Later',skip:'Skip',undo:'Undo'};
  static pressed(event) {
    return [event.ctrlKey?'Ctrl':null,event.altKey?'Alt':null,event.shiftKey?'Shift':null,event.metaKey?'Meta':null,event.code].filter(Boolean).join('+');
  }
  static pretty(key) {
    return key.replace(/Key|Digit/g,'').replace('ArrowLeft','←').replace('ArrowRight','→')
      .replace('ArrowUp','↑').replace('ArrowDown','↓').split('+').join(' + ');
  }
  constructor(token, changed, opened) {
    this.token = token; this.changed = changed; this.opened = opened;
    this.dialog = document.getElementById('keys-dialog'); this.capture = null; this.saving = false;
    this.message = document.getElementById('key-message');
    document.getElementById('toggle-keys').onclick = () => this.open();
    document.getElementById('close-keys').onclick = () => { this.capture = null; this.dialog.close(); };
    document.getElementById('reset-keys').onclick = () => this.save({...this.defaults});
    this.dialog.addEventListener('cancel', e => {
      if (this.capture) { e.preventDefault(); this.capture = null; this.render(); this.message.textContent = 'Shortcut change cancelled.'; }
    });
    this.dialog.addEventListener('close', () => { this.capture = null; });
    document.addEventListener('keydown', e => this.record(e), true);
    window.addEventListener('focus', () => {
      if (!this.dialog.open && !this.saving) this.load().catch(() => {});
    });
  }
  async load() {
    const response = await fetch('/api/keys'), data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not load keyboard settings');
    this.profile = data.profile; this.defaults = data.defaults; this.codes = data.codes;
    this.changed();
  }
  label(action) { return VODKeys.pretty(this.profile?.keys[action] || ''); }
  match(event) { return Object.entries(this.profile?.keys || {}).find(([,key]) => key === VODKeys.pressed(event))?.[0]; }
  async open() {
    this.opened(); this.capture = null; this.dialog.showModal();
    this.message.textContent = 'Loading keyboard settings…';
    try { await this.load(); this.render(); this.message.textContent = 'Click a shortcut to change it.'; }
    catch (error) { this.message.textContent = error.message; }
  }
  render() {
    const rows = document.getElementById('key-rows'); rows.replaceChildren();
    for (const [action,label] of Object.entries(VODKeys.labels)) {
      const row = document.createElement('div'); row.className = 'key-row';
      const name = document.createElement('span'); name.textContent = label;
      const button = document.createElement('button'); button.dataset.action = action;
      button.textContent = this.capture === action ? 'Press a key…' : this.label(action);
      button.className = this.capture === action ? 'capturing' : '';
      button.disabled = this.saving; button.setAttribute('aria-label','Change '+label);
      button.onclick = () => { this.capture = action; this.render();
        rows.querySelector(`[data-action="${action}"]`).focus();
        this.message.textContent = 'Press a key, optionally with Shift. Esc cancels.'; };
      row.append(name,button); rows.append(row);
    }
    document.getElementById('reset-keys').disabled = this.saving || !this.profile;
  }
  record(event) {
    if (!this.dialog.open || !this.capture || event.code === 'Escape') return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (event.repeat || /^(Shift|Control|Alt|Meta)(Left|Right)$/.test(event.code)) return;
    const key = VODKeys.pressed(event);
    if (event.ctrlKey || event.altKey || event.metaKey || !this.codes.includes(event.code)) {
      this.message.textContent = 'Use a letter, number, navigation or punctuation key, optionally with Shift.'; return;
    }
    const duplicate = Object.entries(this.profile.keys).find(([a,k]) => a !== this.capture && k === key);
    if (duplicate) { this.message.textContent = `Already assigned to ${VODKeys.labels[duplicate[0]]}. Choose another key.`; return; }
    const keys = {...this.profile.keys,[this.capture]:key}; this.capture = null; this.save(keys);
  }
  async save(keys) {
    if (this.saving || !this.profile) return;
    this.capture = null; this.saving = true; this.render(); this.message.textContent = 'Saving…';
    try {
      const response = await fetch('/api/keys',{method:'POST',headers:{'Content-Type':'application/json','X-Review-Token':this.token},
        body:JSON.stringify({revision:this.profile.revision,keys})});
      const value = await response.json();
      if (!response.ok) {
        if (response.status === 409) await this.load();
        throw new Error(value.error || 'Keyboard settings were not saved');
      }
      this.profile = value; this.changed(); this.message.textContent = 'Saved for all projects.';
    } catch (error) { this.message.textContent = error.message; }
    finally { this.saving = false; this.render(); }
  }
};
