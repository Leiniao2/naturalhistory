// Visual views: tree graph (Morphology / Ethology), climate chart, ages timeline.
// Each render function rebuilds its view inside `host` from ctx:
//   { items, selected, selectItem(i), mutate(fn, opts), addItemAt(props), all }

const SVG_NS = 'http://www.w3.org/2000/svg';
const s = (tag, attrs = {}, ...children) => {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null) continue;
    if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined) el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return el;
};
const div = (cls, ...children) => { const d = document.createElement('div'); d.className = cls; d.append(...children); return d; };

const ERA_COLORS = { Paleozoic: '#5c9a9e', Mesozoic: '#66a85c', Cenozoic: '#e6c04d' };

// Keeps the scroll position when a view is rebuilt
function rebuild(host, build) {
  const { scrollLeft, scrollTop } = host;
  host.replaceChildren(...build());
  host.scrollLeft = scrollLeft;
  host.scrollTop = scrollTop;
}

// ---------- Tree graph ----------

const COL = 230, ROW = 88, NW = 186, NH = 60, PAD = 36;

export function renderTreeGraph(host, ctx) {
  const nodes = ctx.items;
  const sel = nodes[ctx.selected];
  const maxTier = Math.max(0, ...nodes.map(n => n.tier || 0)) + 1;
  const maxRow = Math.max(0, ...nodes.map(n => n.row || 0)) + 1;
  const width = PAD * 2 + maxTier * COL + NW;
  const height = PAD * 2 + 20 + maxRow * ROW + NH;
  const pos = n => ({ x: PAD + (n.tier || 0) * COL, y: PAD + 20 + (n.row || 0) * ROW });
  const byId = new Map(nodes.map(n => [n.id, n]));

  const svg = s('svg', { width, height, class: 'graph' });

  // Empty grid cells: double-click to add a node there
  for (let t = 0; t <= maxTier; t++) {
    svg.append(s('text', { x: PAD + t * COL + NW / 2, y: PAD, class: 'col-label', 'text-anchor': 'middle' }, `Column ${t}`));
    for (let r = 0; r <= maxRow; r++) {
      svg.append(s('rect', {
        x: PAD + t * COL, y: PAD + 20 + r * ROW, width: NW, height: NH, rx: 8, class: 'cell',
        ondblclick: () => ctx.addItemAt({ tier: t, row: r }),
      }));
    }
  }

  // Prerequisite edges
  const edges = s('g');
  const edgeFor = (pre, node) => {
    const a = pos(pre), b = pos(node);
    const x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2;
    const bend = Math.max(40, (x2 - x1) / 2);
    const bad = (pre.tier || 0) >= (node.tier || 0);
    const hot = sel && (node === sel || pre === sel);
    return s('path', {
      d: `M${x1},${y1} C${x1 + bend},${y1} ${x2 - bend},${y2} ${x2},${y2}`,
      class: `edge ${bad ? 'bad' : ''} ${hot ? 'hot' : ''}`, 'marker-end': 'url(#arrow)',
    });
  };
  for (const n of nodes) for (const p of n.prerequisites || []) if (byId.has(p)) edges.append(edgeFor(byId.get(p), n));
  svg.append(s('defs', {}, s('marker', { id: 'arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' },
    s('path', { d: 'M0,0 L10,5 L0,10 z', class: 'arrow' }))));
  svg.append(edges);

  // Nodes
  nodes.forEach((n, i) => {
    const p = pos(n);
    const isPrereqOfSel = sel && (sel.prerequisites || []).includes(n.id);
    const g = s('g', { class: `node ${i === ctx.selected ? 'selected' : ''} ${isPrereqOfSel ? 'prereq' : ''} ${n.cost === 0 && !(n.prerequisites || []).length ? 'root' : ''}`,
      transform: `translate(${p.x},${p.y})` },
      s('rect', { width: NW, height: NH, rx: 8 }),
      s('text', { x: 10, y: 24, class: 'node-name' }, truncate(n.displayName || n.id, 22)),
      s('text', { x: 10, y: 44, class: 'node-sub' }, `${n.cost ?? 0} EP · ${n.age || '?'}${(n.unlocksGenes || []).length ? ` · ${(n.unlocksGenes || []).length} gene(s)` : ''}`),
      s('title', {}, `${n.displayName}\n${n.description || ''}`));
    enableNodeDrag(g, n, i, p, ctx, svg);
    svg.append(g);
  });

  rebuild(host, () => [
    div('view-hint', 'Drag nodes to move them · Double-click an empty slot to add · Shift+click a node to toggle it as a prerequisite of the selected node'),
    svg,
  ]);
}

function enableNodeDrag(g, node, index, start, ctx, svg) {
  let drag = null;
  g.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    g.setPointerCapture(e.pointerId);
    const pt = svgPoint(svg, e);
    drag = { dx: pt.x - start.x, dy: pt.y - start.y, sx: e.clientX, sy: e.clientY, moved: false };
  });
  g.addEventListener('pointermove', e => {
    if (!drag) return;
    if (Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) > 4) drag.moved = true;
    if (!drag.moved) return;
    const pt = svgPoint(svg, e);
    g.setAttribute('transform', `translate(${pt.x - drag.dx},${pt.y - drag.dy})`);
    g.classList.add('dragging');
  });
  g.addEventListener('pointerup', e => {
    if (!drag) return;
    const d = drag;
    drag = null;
    if (!d.moved) {
      const sel = ctx.items[ctx.selected];
      if ((e.shiftKey || e.altKey) && sel && sel !== node) {
        // Toggle `node` as a prerequisite of the selected node
        ctx.mutate(() => {
          const pre = sel.prerequisites ||= [];
          const k = pre.indexOf(node.id);
          if (k >= 0) pre.splice(k, 1); else pre.push(node.id);
        }, { structural: true });
      } else {
        ctx.selectItem(index);
      }
      return;
    }
    const pt = svgPoint(svg, e);
    const tier = Math.max(0, Math.round((pt.x - d.dx - PAD) / COL));
    const row = Math.max(0, Math.round((pt.y - d.dy - PAD - 20) / ROW));
    if (tier === node.tier && row === node.row) { ctx.selectItem(index); return; }
    ctx.mutate(() => { node.tier = tier; node.row = row; }, { structural: true });
    ctx.selectItem(index);
  });
}

function svgPoint(svg, e) {
  const r = svg.getBoundingClientRect();
  return { x: e.clientX - r.left, y: e.clientY - r.top };
}

const truncate = (t, n) => (t.length > n ? t.slice(0, n - 1) + '…' : t);

// ---------- Climate chart ----------

const SERIES = [
  { key: 'temperatureC', label: 'Global temperature (°C)', min: 0, max: 35, color: '#e8835a', fmt: v => v.toFixed(1) },
  { key: 'co2ppm', label: 'CO2 (ppm, log scale)', min: 100, max: 8000, log: true, color: '#c9c9c9', fmt: v => Math.round(v) },
  { key: 'o2Percent', label: 'O2 (%)', min: 10, max: 36, color: '#6fb6e8', fmt: v => v.toFixed(1) },
  { key: 'seaLevelM', label: 'Sea level vs today (m)', min: -150, max: 300, color: '#5c8fd6', fmt: v => Math.round(v) },
  { key: 'humidityOffset', label: 'Humidity offset (pp)', min: -8, max: 8, color: '#8fcf8a', fmt: v => v.toFixed(1) },
];
let logTime = false;

export function renderClimateChart(host, ctx) {
  const keys = ctx.items;
  const ages = (ctx.all.ages && ctx.all.ages.ages) || [];
  const W = Math.max(700, host.clientWidth - 30);
  const L = 70, R = 20, PH = 130, GAP = 26, TOP = 34;
  const H = TOP + SERIES.length * (PH + GAP);
  const maxMa = 540;
  const lo = Math.log10(0.01), hi = Math.log10(maxMa + 0.01);
  const xOf = ma => L + (W - L - R) * (logTime ? 1 - (Math.log10(ma + 0.01) - lo) / (hi - lo) : 1 - ma / maxMa);
  const svg = s('svg', { width: W, height: H, class: 'chart' });

  // Period bands
  ages.forEach((a, i) => {
    const x1 = xOf(a.startMillionYearsAgo), x2 = xOf(a.endMillionYearsAgo);
    svg.append(s('rect', { x: x1, y: TOP - 4, width: Math.max(1, x2 - x1), height: H - TOP, class: `band ${i % 2 ? 'odd' : ''}` }));
    svg.append(s('rect', { x: x1, y: 4, width: Math.max(1, x2 - x1), height: 18, fill: ERA_COLORS[a.era] || '#888', opacity: 0.85 }));
    if (x2 - x1 > 28) svg.append(s('text', { x: (x1 + x2) / 2, y: 17, class: 'band-label', 'text-anchor': 'middle' }, truncate(a.displayName, Math.floor((x2 - x1) / 7))));
  });

  const sorted = keys.map((k, i) => ({ k, i })).sort((a, b) => b.k.ma - a.k.ma);

  SERIES.forEach((ser, si) => {
    const y0 = TOP + si * (PH + GAP);
    const yOf = v => {
      const t = ser.log ? (Math.log(Math.max(v, 1)) - Math.log(ser.min)) / (Math.log(ser.max) - Math.log(ser.min)) : (v - ser.min) / (ser.max - ser.min);
      return y0 + PH * (1 - Math.min(1.05, Math.max(-0.05, t)));
    };
    const vOf = y => {
      const t = 1 - (y - y0) / PH;
      return ser.log ? Math.exp(Math.log(ser.min) + t * (Math.log(ser.max) - Math.log(ser.min))) : ser.min + t * (ser.max - ser.min);
    };

    svg.append(s('rect', { x: L, y: y0, width: W - L - R, height: PH, class: 'panel' }));
    svg.append(s('text', { x: L + 6, y: y0 + 14, class: 'panel-label' }, ser.label));
    for (const t of [0, 0.5, 1]) {
      const v = vOf(y0 + PH * (1 - t));
      svg.append(s('text', { x: L - 6, y: y0 + PH * (1 - t) + 4, class: 'axis', 'text-anchor': 'end' }, ser.fmt(v)));
    }

    const line = s('polyline', { class: 'series', stroke: ser.color, points: sorted.map(({ k }) => `${xOf(k.ma)},${yOf(k[ser.key] ?? 0)}`).join(' ') });
    svg.append(line);

    sorted.forEach(({ k, i }) => {
      const c = s('circle', { cx: xOf(k.ma), cy: yOf(k[ser.key] ?? 0), r: i === ctx.selected ? 6 : 4, fill: ser.color,
        class: `point ${i === ctx.selected ? 'selected' : ''}` },
        s('title', {}, `${k.ma} Ma — ${k.note || ''}\n${ser.label}: ${ser.fmt(k[ser.key] ?? 0)}\nDrag up/down to edit`));
      enablePointDrag(c, k, i, ser, yOf, vOf, ctx, line, sorted, xOf);
      svg.append(c);
    });
  });

  // Time axis
  const ticks = logTime ? [500, 200, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.1, 0.02] : [500, 400, 300, 200, 100, 0];
  for (const t of ticks) svg.append(s('text', { x: xOf(t), y: H - 6, class: 'axis', 'text-anchor': 'middle' }, `${t} Ma`));

  const toggle = document.createElement('label');
  toggle.className = 'view-hint';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = logTime;
  cb.onchange = () => { logTime = cb.checked; renderClimateChart(host, ctx); };
  toggle.append(cb, ' Logarithmic time axis (expands the Cenozoic and Quaternary) · Click a point to select it, drag up/down to change its value');

  rebuild(host, () => [toggle, svg]);
}

function enablePointDrag(c, key, index, ser, yOf, vOf, ctx, line, sorted, xOf) {
  let drag = null;
  c.addEventListener('pointerdown', e => {
    c.setPointerCapture(e.pointerId);
    drag = { original: key[ser.key], startY: e.clientY, moved: false, cy: +c.getAttribute('cy') };
  });
  c.addEventListener('pointermove', e => {
    if (!drag) return;
    const dy = e.clientY - drag.startY;
    if (Math.abs(dy) > 3) drag.moved = true;
    if (!drag.moved) return;
    const cy = drag.cy + dy;
    c.setAttribute('cy', cy);
    key[ser.key] = round(vOf(cy), ser);
    line.setAttribute('points', sorted.map(({ k }) => `${xOf(k.ma)},${yOf(k[ser.key] ?? 0)}`).join(' '));
  });
  c.addEventListener('pointerup', () => {
    if (!drag) return;
    const d = drag;
    drag = null;
    if (!d.moved) { ctx.selectItem(index); return; }
    const value = key[ser.key];
    key[ser.key] = d.original; // restore so the undo snapshot holds the old value
    ctx.mutate(() => { key[ser.key] = value; }, { structural: true });
    ctx.selectItem(index);
  });
}

function round(v, ser) {
  if (ser.key === 'co2ppm') return Math.round(v / 10) * 10;
  if (ser.key === 'seaLevelM') return Math.round(v);
  return Math.round(v * 10) / 10;
}

// ---------- Ages timeline ----------

export function renderAgeTimeline(host, ctx) {
  const ages = ctx.items;
  const W = Math.max(700, host.clientWidth - 30);
  const L = 150, R = 20;
  const totalMy = ages.reduce((a, x) => a + Math.max(0, x.startMillionYearsAgo - x.endMillionYearsAgo), 0) || 1;
  const totalTurns = ages.reduce((a, x) => a + (x.turns || 0), 0) || 1;
  const svg = s('svg', { width: W, height: 230, class: 'chart timeline' });

  const bar = (y, label, share) => {
    svg.append(s('text', { x: L - 10, y: y + 26, class: 'panel-label', 'text-anchor': 'end' }, label));
    let x = L;
    ages.forEach((a, i) => {
      const w = (W - L - R) * share(a);
      const g = s('g', { class: `seg ${i === ctx.selected ? 'selected' : ''}`, onclick: () => ctx.selectItem(i) },
        s('rect', { x, y, width: Math.max(1, w - 1), height: 40, fill: ERA_COLORS[a.era] || '#888', opacity: i % 2 ? 0.75 : 0.95 }),
        w > 34 ? s('text', { x: x + w / 2, y: y + 25, 'text-anchor': 'middle', class: 'seg-label' }, truncate(a.displayName, Math.floor(w / 7))) : null,
        s('title', {}, `${a.displayName}: ${a.startMillionYearsAgo}–${a.endMillionYearsAgo} Ma, ${a.turns} turns ` +
          `(${((a.startMillionYearsAgo - a.endMillionYearsAgo) / Math.max(1, a.turns)).toFixed(2)} My per turn)`));
      svg.append(g);
      x += w;
    });
  };
  bar(30, 'Real duration', a => Math.max(0, a.startMillionYearsAgo - a.endMillionYearsAgo) / totalMy);
  bar(100, 'Game turns', a => (a.turns || 0) / totalTurns);

  const sel = ages[ctx.selected];
  const info = sel
    ? `${sel.displayName}: ${(sel.startMillionYearsAgo - sel.endMillionYearsAgo).toFixed(2)} million years over ${sel.turns} turns = ` +
      `${((sel.startMillionYearsAgo - sel.endMillionYearsAgo) / Math.max(1, sel.turns)).toFixed(2)} My per turn`
    : '';
  svg.append(s('text', { x: L, y: 175, class: 'panel-label' }, `Total: ${totalTurns} turns covering ${totalMy.toFixed(1)} million years`));
  svg.append(s('text', { x: L, y: 200, class: 'axis' }, info));

  rebuild(host, () => [div('view-hint', 'Top: periods at true length · Bottom: share of game turns. Edit turns in the form to rebalance pacing.'), svg]);
}
