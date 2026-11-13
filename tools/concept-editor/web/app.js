import { DATASETS, DATASET_ORDER, REFERENCES } from './schemas.js';
import { renderTreeGraph, renderClimateChart, renderAgeTimeline } from './views.js';

// ---------- State ----------

const state = {
  data: {},          // dataset name → whole file object (as saved on disk)
  saved: {},         // dataset name → JSON string of last saved/loaded version
  current: 'ages',
  selected: 0,       // index into the current dataset's array
  view: {},          // dataset name → active view
  filter: '',
  undo: {},          // dataset name → [JSON snapshots]
  redo: {},
  lastSnapshotAt: 0,
};

const $ = (sel, el = document) => el.querySelector(sel);
const h = (tag, attrs = {}, ...children) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined && c !== false) el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return el;
};

const def = (name = state.current) => DATASETS[name];
export const items = (name = state.current) => {
  const d = state.data[name];
  if (!d) return [];
  return d[def(name).arrayKey] ||= [];
};
const isDirty = (name) => state.data[name] && JSON.stringify(state.data[name]) !== state.saved[name];

// ---------- Loading & saving ----------

async function loadAll() {
  for (const name of DATASET_ORDER) {
    const res = await fetch(`/api/data/${name}`);
    if (res.ok) state.data[name] = await res.json();
    else if (res.status === 404) state.data[name] = { [DATASETS[name].arrayKey]: [] };
    else {
      const err = await res.json().catch(() => ({}));
      toast(`Could not load ${name}: ${err.error || res.status}`, 'error');
      state.data[name] = { [DATASETS[name].arrayKey]: [] };
      continue;
    }
    state.saved[name] = res.ok ? JSON.stringify(state.data[name]) : '';
    state.undo[name] = [];
    state.redo[name] = [];
  }
}

async function save(name) {
  const d = def(name);
  const body = structuredClone(state.data[name]);
  if (d.sortOnSave) body[d.arrayKey].sort(d.sortOnSave);
  const res = await fetch(`/api/data/${name}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const out = await res.json().catch(() => ({}));
  if (!res.ok) { toast(`Save failed for ${d.title}: ${out.error || res.status}`, 'error'); return false; }
  // Keep the selection on the same item after sorting
  if (d.sortOnSave && name === state.current) {
    const sel = items(name)[state.selected];
    state.data[name] = body;
    state.selected = Math.max(0, body[d.arrayKey].indexOf(body[d.arrayKey].find(x => JSON.stringify(x) === JSON.stringify(sel))));
  } else {
    state.data[name] = body;
  }
  state.saved[name] = JSON.stringify(body);
  return true;
}

async function saveAll() {
  const dirty = DATASET_ORDER.filter(isDirty);
  if (!dirty.length) { toast('Nothing to save'); return; }
  const errors = allProblems().filter(p => p.level === 'error' && dirty.includes(p.dataset));
  if (errors.length && !confirm(`${errors.length} error(s) in the data. Save anyway?`)) return;
  let ok = 0;
  for (const name of dirty) if (await save(name)) ok++;
  toast(`Saved ${ok} file(s) to Assets/Resources/Data. Switch to Unity to reimport.`, 'ok');
  renderAll();
}

// ---------- Undo ----------

// Called before every edit. Typing within 800 ms coalesces into one undo step.
function snapshot(name = state.current, coalesce = false) {
  const now = Date.now();
  if (coalesce && now - state.lastSnapshotAt < 800 && state.undo[name].length) { state.lastSnapshotAt = now; return; }
  state.lastSnapshotAt = now;
  state.undo[name].push(JSON.stringify(state.data[name]));
  if (state.undo[name].length > 200) state.undo[name].shift();
  state.redo[name] = [];
}

function undo(redo = false) {
  const name = state.current;
  const from = redo ? state.redo[name] : state.undo[name];
  const to = redo ? state.undo[name] : state.redo[name];
  if (!from.length) return;
  to.push(JSON.stringify(state.data[name]));
  state.data[name] = JSON.parse(from.pop());
  state.selected = Math.min(state.selected, items().length - 1);
  renderAll();
}

// ---------- Edits ----------

export function selectItem(index) {
  state.selected = index;
  renderList();
  renderForm();
  renderView();
}

export function changed({ structural = false } = {}) {
  renderList();
  renderProblems();
  renderSidebar();
  if (structural) renderForm();
  renderView();
}

export function mutate(fn, { coalesce = false, structural = false } = {}) {
  snapshot(state.current, coalesce);
  fn();
  changed({ structural });
}

function addItem() {
  const d = def();
  const list = items();
  const item = d.newItem(list, list[state.selected]);
  if (d.idField) item[d.idField] = uniqueId(item[d.idField], list.map(x => x[d.idField]));
  mutate(() => list.splice(state.selected + 1, 0, item));
  selectItem(Math.min(state.selected + 1, list.length - 1));
}

export function addItemAt(props) {
  const d = def();
  const list = items();
  const item = { ...d.newItem(list), ...props };
  if (d.idField) item[d.idField] = uniqueId(item[d.idField], list.map(x => x[d.idField]));
  mutate(() => list.push(item));
  selectItem(list.length - 1);
}

function duplicateItem() {
  const d = def();
  const list = items();
  const src = list[state.selected];
  if (!src) return;
  const copy = structuredClone(src);
  if (d.idField) copy[d.idField] = uniqueId(`${src[d.idField]}_copy`, list.map(x => x[d.idField]));
  if ('displayName' in copy) copy.displayName += ' (copy)';
  if ('commonName' in copy) copy.commonName += ' (copy)';
  if (d.arrayKey === 'keyframes') copy.ma = +(copy.ma - 0.5).toFixed(3);
  mutate(() => list.splice(state.selected + 1, 0, copy));
  selectItem(state.selected + 1);
}

function deleteItem() {
  const d = def();
  const list = items();
  const item = list[state.selected];
  if (!item) return;
  const refs = d.idField ? findReferences(state.current, item[d.idField]) : [];
  const msg = `Delete "${d.label(item)}"?` + (refs.length ? `\n\nIt is referenced by ${refs.length} item(s); those references will be removed.` : '');
  if (!confirm(msg)) return;
  mutate(() => {
    if (d.idField) removeReferences(state.current, item[d.idField]);
    list.splice(state.selected, 1);
  });
  selectItem(Math.max(0, Math.min(state.selected, list.length - 1)));
}

function moveItem(delta) {
  const list = items();
  const i = state.selected, j = i + delta;
  if (j < 0 || j >= list.length) return;
  mutate(() => [list[i], list[j]] = [list[j], list[i]]);
  selectItem(j);
}

function uniqueId(base, existing) {
  const set = new Set(existing);
  if (!set.has(base)) return base;
  let n = 2;
  while (set.has(`${base}_${n}`)) n++;
  return `${base}_${n}`;
}

// ---------- References ----------

function refsTo(target) { return REFERENCES.filter(r => r.to === target); }

function findReferences(target, id) {
  const hits = [];
  for (const r of refsTo(target)) {
    items(r.from).forEach((it, i) => {
      const v = it[r.field];
      const hit = r.kind === 'value' ? v === id : r.kind === 'array' ? (v || []).includes(id) : (v || []).some(row => row[r.column] === id);
      if (hit) hits.push({ dataset: r.from, index: i });
    });
  }
  return hits;
}

// Renames an id everywhere it is referenced (marks those datasets dirty too)
function renameReferences(target, oldId, newId) {
  let count = 0;
  for (const r of refsTo(target)) {
    if (r.from !== state.current) snapshot(r.from);
    for (const it of items(r.from)) {
      if (r.kind === 'value' && it[r.field] === oldId) { it[r.field] = newId; count++; }
      if (r.kind === 'array' && it[r.field]) it[r.field] = it[r.field].map(v => (v === oldId ? (count++, newId) : v));
      if (r.kind === 'table') for (const row of it[r.field] || []) if (row[r.column] === oldId) { row[r.column] = newId; count++; }
    }
  }
  return count;
}

function removeReferences(target, id) {
  for (const r of refsTo(target)) {
    if (r.from !== state.current) snapshot(r.from);
    for (const it of items(r.from)) {
      if (r.kind === 'array' && it[r.field]) it[r.field] = it[r.field].filter(v => v !== id);
      if (r.kind === 'table' && it[r.field]) it[r.field] = it[r.field].filter(row => row[r.column] !== id);
      if (r.kind === 'value' && it[r.field] === id) it[r.field] = '';
    }
  }
}

// ---------- Validation ----------

function problemsFor(name) {
  const d = def(name);
  const list = items(name);
  const out = [];
  if (d.idField) {
    const seen = new Map();
    list.forEach((it, i) => {
      const id = it[d.idField];
      if (!id) out.push({ index: i, level: 'error', msg: 'missing id' });
      else if (seen.has(id)) out.push({ index: i, level: 'error', msg: `duplicate id "${id}"` });
      else seen.set(id, i);
    });
  }
  for (const r of REFERENCES.filter(r => r.from === name)) {
    const valid = new Set(items(r.to).map(x => x[def(r.to).idField]));
    list.forEach((it, i) => {
      const v = it[r.field];
      const vals = r.kind === 'value' ? [v] : r.kind === 'array' ? (v || []) : (v || []).map(row => row[r.column]);
      for (const x of vals) {
        if (x === '' || x === undefined || x === null) { if (r.kind === 'value' && !r.optional) out.push({ index: i, level: 'error', msg: `${r.field} is empty` }); continue; }
        if (!valid.has(x)) out.push({ index: i, level: 'error', msg: `${r.field}: unknown ${def(r.to).title.toLowerCase()} id "${x}"` });
      }
    });
  }
  if (d.validate) out.push(...d.validate(list, state.data));
  return out.map(p => ({ ...p, dataset: name }));
}

function allProblems() { return DATASET_ORDER.flatMap(problemsFor); }

// ---------- Rendering ----------

function renderAll() {
  renderSidebar();
  renderToolbar();
  renderList();
  renderForm();
  renderView();
  renderProblems();
}

function renderSidebar() {
  const nav = $('#datasets');
  nav.replaceChildren(...DATASET_ORDER.map(name => {
    const d = def(name);
    const errs = problemsFor(name).filter(p => p.level === 'error').length;
    return h('button', {
      class: `dataset ${name === state.current ? 'active' : ''}`,
      onclick: () => { state.current = name; state.selected = 0; state.filter = ''; $('#search').value = ''; renderAll(); },
    },
      h('span', { class: 'icon' }, d.icon),
      h('span', { class: 'name' }, d.title),
      h('span', { class: 'count' }, items(name).length),
      errs ? h('span', { class: 'badge error', title: `${errs} error(s)` }, errs) : null,
      isDirty(name) ? h('span', { class: 'dirty', title: 'Unsaved changes' }, '●') : null);
  }));
  const anyDirty = DATASET_ORDER.some(isDirty);
  $('#save-all').disabled = !anyDirty;
  document.title = `${anyDirty ? '● ' : ''}Natural History · Concept Editor`;
}

function renderToolbar() {
  const d = def();
  const views = d.views;
  const active = state.view[state.current] || views[0];
  $('#view-tabs').replaceChildren(...(views.length > 1 ? views.map(v => h('button', {
    class: `tab ${v === active ? 'active' : ''}`,
    onclick: () => { state.view[state.current] = v; renderToolbar(); renderView(); applyLayout(); },
  }, { form: 'List', graph: 'Tree graph', chart: 'Chart', timeline: 'Timeline' }[v])) : []));
  $('#dataset-title').textContent = `${d.icon} ${d.title}`;
  applyLayout();
}

function applyLayout() {
  const active = state.view[state.current] || def().views[0];
  document.body.dataset.view = active;
}

function renderList() {
  const d = def();
  const list = items();
  const problems = problemsFor(state.current);
  const filter = state.filter.toLowerCase();
  const rows = [];
  let lastGroup;
  list.forEach((it, i) => {
    const text = `${d.label(it)} ${d.sub ? d.sub(it) : ''} ${d.idField ? it[d.idField] : ''}`.toLowerCase();
    if (filter && !text.includes(filter)) return;
    if (d.groupBy && !filter) {
      const g = d.groupBy(it) || '—';
      if (g !== lastGroup) { rows.push(h('div', { class: 'group' }, g)); lastGroup = g; }
    }
    const errs = problems.filter(p => p.index === i);
    const level = errs.some(p => p.level === 'error') ? 'error' : errs.length ? 'warn' : '';
    rows.push(h('div', {
      class: `item ${i === state.selected ? 'selected' : ''}`,
      onclick: () => selectItem(i),
      title: errs.map(p => p.msg).join('\n'),
    },
      h('div', { class: 'item-label' }, d.label(it), level ? h('span', { class: `dot ${level}` }) : null),
      d.sub ? h('div', { class: 'item-sub' }, d.sub(it)) : null));
  });
  $('#list').replaceChildren(...rows);
  $('#list .selected')?.scrollIntoView({ block: 'nearest' });
}

function renderForm() {
  const d = def();
  const item = items()[state.selected];
  const form = $('#form');
  if (!item) { form.replaceChildren(h('p', { class: 'empty' }, 'Nothing selected. Use "+ Add" to create an entry.')); return; }
  const problems = problemsFor(state.current).filter(p => p.index === state.selected);
  form.replaceChildren(...[
    h('h2', {}, d.label(item)),
    problems.length ? h('ul', { class: 'item-problems' }, problems.map(p => h('li', { class: p.level }, p.msg))) : null,
    ...d.fields.map(f => fieldRow(f, item, item)),
  ].filter(Boolean));
}

// One labelled field. `owner` is the object holding the value (item, or a nested object).
function fieldRow(f, owner, item) {
  const id = `f-${f.key}`;
  return h('div', { class: `field type-${f.type}` },
    h('label', { for: id }, f.label),
    fieldInput(f, owner, item, id),
    f.help ? h('div', { class: 'help' }, f.help) : null);
}

function options(f, item) {
  return typeof f.options === 'function' ? f.options(state.data, item) : f.options || [];
}

function fieldInput(f, owner, item, id) {
  const set = (v, opts) => mutate(() => { owner[f.key] = v; }, opts);
  const val = owner[f.key];

  switch (f.type) {
    case 'id': {
      let before = val;
      return h('input', {
        id, value: val ?? '', spellcheck: 'false',
        onfocus: () => { before = owner[f.key]; },
        oninput: e => set(e.target.value, { coalesce: true }),
        onchange: e => {
          const after = e.target.value;
          if (before && after && before !== after) {
            const n = renameReferences(state.current, before, after);
            if (n) toast(`Updated ${n} reference(s) from "${before}" to "${after}"`, 'ok');
            changed();
          }
          before = after;
        },
      });
    }
    case 'string':
      return h('input', { id, value: val ?? '', class: f.italic ? 'italic' : '', oninput: e => set(e.target.value, { coalesce: true }) });
    case 'text':
      return h('textarea', { id, rows: 4, oninput: e => set(e.target.value, { coalesce: true }) }, val ?? '');
    case 'number':
    case 'int': {
      const parse = v => (f.type === 'int' ? parseInt(v, 10) : parseFloat(v));
      const input = h('input', {
        id, type: 'number', value: val ?? 0, step: f.step ?? (f.type === 'int' ? 1 : 'any'), min: f.min, max: f.max,
        oninput: e => { const v = parse(e.target.value); if (!Number.isNaN(v)) { set(v, { coalesce: true }); if (slider) slider.value = v; } },
      });
      const slider = f.slider ? h('input', { type: 'range', min: f.min, max: f.max, step: f.step, value: val ?? 0,
        oninput: e => { const v = parse(e.target.value); input.value = v; set(v, { coalesce: true }); } }) : null;
      return slider ? h('div', { class: 'with-slider' }, slider, input) : input;
    }
    case 'bool':
      return h('input', { id, type: 'checkbox', checked: !!val, onchange: e => set(e.target.checked) });
    case 'color': {
      const text = h('input', { id, value: val ?? '', oninput: e => { set(e.target.value, { coalesce: true }); if (/^#[0-9a-f]{6}$/i.test(e.target.value)) picker.value = e.target.value; } });
      const picker = h('input', { type: 'color', value: val || '#888888',
        oninput: e => { text.value = e.target.value.toUpperCase(); set(text.value, { coalesce: true }); } });
      return h('div', { class: 'with-slider' }, picker, text);
    }
    case 'enum': {
      const opts = options(f, item);
      const known = opts.some(o => o.value === (val ?? ''));
      return h('select', { id, onchange: e => set(e.target.value) },
        !known ? h('option', { value: val ?? '', selected: true }, `${val ?? ''} (unknown)`) : null,
        opts.map(o => h('option', { value: o.value, selected: o.value === (val ?? '') }, o.label)));
    }
    case 'multienum':
    case 'refs': {
      const current = new Set(val || []);
      const opts = options(f, item);
      const unknown = [...current].filter(v => !opts.some(o => o.value === v));
      const chips = h('div', { class: 'chips' },
        opts.map(o => h('button', {
          type: 'button', class: `chip ${current.has(o.value) ? 'on' : ''}`, title: o.value,
          onclick: () => {
            mutate(() => {
              const arr = owner[f.key] ||= [];
              const k = arr.indexOf(o.value);
              if (k >= 0) arr.splice(k, 1); else arr.push(o.value);
            }, { structural: true });
          },
        }, o.label)),
        unknown.map(v => h('button', { type: 'button', class: 'chip on unknown', title: 'Unknown id — click to remove',
          onclick: () => mutate(() => { owner[f.key] = owner[f.key].filter(x => x !== v); }, { structural: true }) }, `${v} ✕`)));
      return chips;
    }
    case 'list':
      return h('textarea', {
        id, rows: Math.max(3, (val || []).length + 1),
        oninput: e => set(e.target.value.split('\n').map(s => s.trim()).filter(Boolean), { coalesce: true }),
      }, (val || []).join('\n'));
    case 'object': {
      const obj = owner[f.key] ||= {};
      return h('div', { class: 'object' }, f.fields.map(sub => fieldRow(sub, obj, item)));
    }
    case 'table': {
      const rows = owner[f.key] ||= [];
      return h('div', { class: 'table' },
        h('div', { class: 'table-row head' }, f.columns.map(c => h('span', {}, c.label)), h('span')),
        rows.map((row, r) => h('div', { class: 'table-row' },
          f.columns.map(c => fieldInput(c, row, item, `${id}-${r}-${c.key}`)),
          h('button', { type: 'button', class: 'icon-btn', title: 'Remove row',
            onclick: () => mutate(() => rows.splice(r, 1), { structural: true }) }, '✕'))),
        h('button', { type: 'button', class: 'small', onclick: () => mutate(() => rows.push(f.newRow()), { structural: true }) }, '+ Add row'));
    }
  }
  return h('span', {}, `Unsupported field type ${f.type}`);
}

function renderView() {
  const active = state.view[state.current] || def().views[0];
  const host = $('#view');
  const ctx = { state, items: items(), selected: state.selected, selectItem, mutate, addItemAt, all: state.data };
  if (active === 'graph') renderTreeGraph(host, ctx);
  else if (active === 'chart') renderClimateChart(host, ctx);
  else if (active === 'timeline') renderAgeTimeline(host, ctx);
  else host.replaceChildren();
}

function renderProblems() {
  const problems = allProblems();
  const errors = problems.filter(p => p.level === 'error').length;
  const warns = problems.length - errors;
  $('#problems-summary').textContent = problems.length ? `${errors} error(s), ${warns} warning(s)` : 'No problems';
  $('#problems-summary').className = errors ? 'error' : warns ? 'warn' : 'ok';
  $('#problems-list').replaceChildren(...problems.map(p => {
    const d = def(p.dataset);
    const it = items(p.dataset)[p.index];
    return h('li', {
      class: p.level,
      onclick: () => { state.current = p.dataset; state.selected = Math.max(0, p.index); renderAll(); },
    }, h('b', {}, `${d.title}${it ? ' › ' + d.label(it) : ''}: `), p.msg);
  }));
}

// ---------- Misc ----------

let toastTimer;
function toast(msg, kind = '') {
  const el = $('#toast');
  el.textContent = msg;
  el.className = `show ${kind}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.className = ''), 3500);
}

function wire() {
  $('#save-all').onclick = saveAll;
  $('#add').onclick = addItem;
  $('#duplicate').onclick = duplicateItem;
  $('#delete').onclick = deleteItem;
  $('#up').onclick = () => moveItem(-1);
  $('#down').onclick = () => moveItem(1);
  $('#reload').onclick = async () => {
    if (DATASET_ORDER.some(isDirty) && !confirm('Discard unsaved changes and reload from disk?')) return;
    await loadAll();
    renderAll();
    toast('Reloaded from disk');
  };
  $('#search').oninput = e => { state.filter = e.target.value; renderList(); };
  $('#problems-summary').onclick = () => $('#problems').classList.toggle('open');

  document.addEventListener('keydown', e => {
    const mod = e.metaKey || e.ctrlKey;
    if (mod && e.key.toLowerCase() === 's') { e.preventDefault(); saveAll(); }
    if (mod && e.key.toLowerCase() === 'z' && !isTyping(e)) { e.preventDefault(); undo(e.shiftKey); }
  });
  window.addEventListener('beforeunload', e => { if (DATASET_ORDER.some(isDirty)) { e.preventDefault(); e.returnValue = ''; } });
}

const isTyping = (e) => ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName);

wire();
loadAll().then(renderAll);
