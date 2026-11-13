// Field definitions for every dataset the editor knows about.
// Field types: id, string, text, number, int, bool, enum, multienum, refs, list, color, object, table
// Keep in sync with Assets/Scripts/Data/DataModels.cs (C# reads these files with JsonUtility,
// so field names must match exactly).

// Must match the GeologicalAge enum in Assets/Scripts/Core/AgeManager.cs
export const AGE_IDS = ['Cambrian', 'Ordovician', 'Silurian', 'Devonian', 'Carboniferous', 'Permian',
  'Triassic', 'Jurassic', 'Cretaceous', 'Paleogene', 'Neogene', 'Quaternary'];
// TerrainKind enum (Assets/Scripts/World/TerrainType.cs)
export const TERRAINS = ['SaltWater', 'FreshWater', 'Plain', 'Hill', 'Mountain', 'Desert', 'Wetland', 'Tundra', 'IceSheet'];
// GeneCategory enum (Assets/Scripts/Biology/GeneMap.cs)
export const GENE_CATEGORIES = ['Locomotion', 'Diet', 'Reproduction', 'Defense', 'Perception', 'Thermoregulation'];
export const KINGDOMS = ['Animalia', 'Plantae', 'Fungi'];
export const DIETS = ['Carnivore', 'Herbivore', 'Omnivore', 'Filter feeder', 'Detritivore', 'Photosynthetic'];
export const ERAS = ['Paleozoic', 'Mesozoic', 'Cenozoic'];

// Option helpers: ids (with labels) from another dataset
const idsOf = (dataset, labelKey) => (all) =>
  ((all[dataset] && all[dataset][DATASETS[dataset].arrayKey]) || []).map(x => ({ value: x.id, label: x[labelKey] || x.id }));
const ageOptions = (all) => {
  const ages = idsOf('ages', 'displayName')(all);
  return ages.length ? ages : AGE_IDS.map(a => ({ value: a, label: a }));
};

const treeFields = (treeName) => [
  { key: 'id', label: 'ID', type: 'id', help: 'Stable identifier (snake_case). Renaming updates prerequisites that point at it.' },
  { key: 'displayName', label: 'Name', type: 'string' },
  { key: 'tier', label: 'Column (tier)', type: 'int', min: 0, help: 'Left → right position. Prerequisites should be in earlier columns.' },
  { key: 'row', label: 'Row', type: 'int', min: 0 },
  { key: 'cost', label: 'Cost (EP)', type: 'int', min: 0, help: '0 with no prerequisites = known from the start.' },
  { key: 'age', label: 'Available from', type: 'enum', options: ageOptions },
  { key: 'prerequisites', label: 'Prerequisites', type: 'refs', options: (all, item) => idsOf(treeName, 'displayName')(all).filter(o => o.value !== item.id) },
  { key: 'unlocksGenes', label: 'Unlocks genes', type: 'refs', options: idsOf('genes', 'displayName') },
  { key: 'description', label: 'Description', type: 'text' },
];

const treeValidate = (treeName) => (items) => {
  const out = [];
  const byId = new Map(items.map(n => [n.id, n]));
  const cells = new Map();
  items.forEach((n, i) => {
    for (const p of n.prerequisites || []) {
      const pre = byId.get(p);
      if (pre && pre.tier >= n.tier) out.push({ index: i, level: 'warn', msg: `prerequisite "${pre.displayName || p}" is not in an earlier column` });
    }
    const key = `${n.tier},${n.row}`;
    if (cells.has(key)) out.push({ index: i, level: 'warn', msg: `same position as "${cells.get(key)}"` });
    else cells.set(key, n.displayName || n.id);
    if (AGE_IDS.indexOf(n.age) >= 0) {
      for (const p of n.prerequisites || []) {
        const pre = byId.get(p);
        if (pre && AGE_IDS.indexOf(pre.age) > AGE_IDS.indexOf(n.age))
          out.push({ index: i, level: 'warn', msg: `prerequisite "${pre.displayName}" becomes available later (${pre.age})` });
      }
    }
  });
  // Cycles
  const state = new Map();
  const visit = (id, path) => {
    if (state.get(id) === 1) { out.push({ index: items.findIndex(n => n.id === id), level: 'error', msg: `prerequisite cycle: ${[...path, id].join(' → ')}` }); return; }
    if (state.get(id) === 2) return;
    state.set(id, 1);
    for (const p of (byId.get(id)?.prerequisites || [])) if (byId.has(p)) visit(p, [...path, id]);
    state.set(id, 2);
  };
  items.forEach(n => visit(n.id, []));
  return out;
};

export const DATASETS = {
  ages: {
    title: 'Ages', icon: '⏳', arrayKey: 'ages', idField: 'id',
    label: a => a.displayName || a.id,
    sub: a => `${a.era || ''} · ${a.startMillionYearsAgo}–${a.endMillionYearsAgo} Ma · ${a.turns || 0} turns`,
    views: ['form', 'timeline'],
    fixedIds: true,
    newItem: () => ({ id: 'NewAge', displayName: 'New Age', era: 'Paleozoic', startMillionYearsAgo: 0, endMillionYearsAgo: 0, turns: 20,
      description: '', keyEvents: [], vegetation: '', environmentalConditions: { globalTemp: '', seaLevel: '', oxygenLevel: '', landCoverage: '' },
      slotExpansionAmount: 0, availableTerrains: [] }),
    fields: [
      { key: 'id', label: 'ID', type: 'id', help: 'Must match a GeologicalAge enum value in AgeManager.cs. Adding a new period also needs a code change.' },
      { key: 'displayName', label: 'Name', type: 'string' },
      { key: 'era', label: 'Era', type: 'enum', options: ERAS.map(e => ({ value: e, label: e })) },
      { key: 'startMillionYearsAgo', label: 'Starts (Ma)', type: 'number', step: 0.01 },
      { key: 'endMillionYearsAgo', label: 'Ends (Ma)', type: 'number', step: 0.01 },
      { key: 'turns', label: 'Turns', type: 'int', min: 1, help: 'Game turns spent in this period; the date advances evenly through it.' },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'keyEvents', label: 'Key events', type: 'list', help: 'One per line.' },
      { key: 'vegetation', label: 'Vegetation', type: 'string' },
      { key: 'environmentalConditions', label: 'Environment', type: 'object', fields: [
        { key: 'globalTemp', label: 'Climate', type: 'string' },
        { key: 'seaLevel', label: 'Sea level', type: 'string' },
        { key: 'oxygenLevel', label: 'Oxygen', type: 'string' },
        { key: 'landCoverage', label: 'Continents', type: 'string' },
      ] },
      { key: 'slotExpansionAmount', label: 'Slot expansion', type: 'int', min: 0 },
      { key: 'availableTerrains', label: 'Available terrains', type: 'multienum', options: TERRAINS.map(t => ({ value: t, label: t })) },
    ],
    validate: (items) => {
      const out = [];
      items.forEach((a, i) => {
        if (!AGE_IDS.includes(a.id)) out.push({ index: i, level: 'error', msg: `id "${a.id}" is not a GeologicalAge enum value` });
        if (a.startMillionYearsAgo <= a.endMillionYearsAgo) out.push({ index: i, level: 'error', msg: 'start must be older (larger Ma) than end' });
        if (!(a.turns >= 1)) out.push({ index: i, level: 'error', msg: 'needs at least 1 turn' });
        const next = items[i + 1];
        if (next && Math.abs(a.endMillionYearsAgo - next.startMillionYearsAgo) > 1e-6)
          out.push({ index: i, level: 'warn', msg: `ends at ${a.endMillionYearsAgo} Ma but ${next.displayName} starts at ${next.startMillionYearsAgo} Ma` });
      });
      AGE_IDS.forEach((id, k) => {
        const at = items.findIndex(a => a.id === id);
        if (at < 0) out.push({ index: -1, level: 'error', msg: `missing period ${id}` });
        else if (at !== k) out.push({ index: at, level: 'warn', msg: `should be at position ${k + 1} (oldest first)` });
      });
      return out;
    },
  },

  climate_history: {
    title: 'Climate history', icon: '🌡️', arrayKey: 'keyframes', idField: null,
    label: k => `${k.ma} Ma`,
    sub: k => `${k.temperatureC} °C · ${k.co2ppm} ppm · ${k.note || ''}`,
    views: ['form', 'chart'],
    sortOnSave: (a, b) => b.ma - a.ma,
    newItem: (items, sel) => {
      const base = sel || items[items.length - 1] || {};
      return { ma: Math.max(0, (base.ma || 1) - 1), temperatureC: base.temperatureC ?? 14, co2ppm: base.co2ppm ?? 280,
        o2Percent: base.o2Percent ?? 21, seaLevelM: base.seaLevelM ?? 0, humidityOffset: 0, note: '' };
    },
    fields: [
      { key: 'ma', label: 'Date (Ma)', type: 'number', step: 0.001, help: 'Millions of years ago. Keyframes are sorted oldest first on save.' },
      { key: 'temperatureC', label: 'Global mean temperature (°C)', type: 'number', step: 0.1 },
      { key: 'co2ppm', label: 'CO2 (ppm)', type: 'number', step: 10 },
      { key: 'o2Percent', label: 'O2 (%)', type: 'number', step: 0.1 },
      { key: 'seaLevelM', label: 'Sea level vs today (m)', type: 'number', step: 1 },
      { key: 'humidityOffset', label: 'Humidity offset (pp)', type: 'number', step: 0.5, help: 'Game-only aridity nudge for dry/wet intervals.' },
      { key: 'note', label: 'Note / event', type: 'string' },
    ],
    validate: (items) => {
      const out = [];
      const seen = new Map();
      items.forEach((k, i) => {
        if (seen.has(k.ma)) out.push({ index: i, level: 'error', msg: `duplicate date ${k.ma} Ma` });
        seen.set(k.ma, i);
        if (k.ma < 0 || k.ma > 541) out.push({ index: i, level: 'warn', msg: 'date outside the Phanerozoic (0–538.8 Ma)' });
        if (k.co2ppm <= 0) out.push({ index: i, level: 'error', msg: 'CO2 must be positive' });
        if (k.o2Percent < 5 || k.o2Percent > 40) out.push({ index: i, level: 'warn', msg: 'O2 outside 5–40%' });
      });
      return out;
    },
  },

  genes: {
    title: 'Genes', icon: '🧬', arrayKey: 'genes', idField: 'id',
    label: g => g.displayName || g.id,
    sub: g => `${g.category} · from ${g.unlockAge}`,
    views: ['form'],
    groupBy: g => g.category,
    newItem: () => ({ id: 'new_gene', displayName: 'New Gene', category: 'Locomotion', defaultExpression: 0, description: '', unlockAge: 'Cambrian' }),
    fields: [
      { key: 'id', label: 'ID', type: 'id', help: 'Renaming updates trees and species that reference it.' },
      { key: 'displayName', label: 'Name', type: 'string' },
      { key: 'category', label: 'Category', type: 'enum', options: GENE_CATEGORIES.map(c => ({ value: c, label: c })) },
      { key: 'defaultExpression', label: 'Default expression', type: 'number', min: 0, max: 1, step: 0.05, slider: true },
      { key: 'unlockAge', label: 'Unlocks in', type: 'enum', options: ageOptions },
      { key: 'description', label: 'Description', type: 'text' },
    ],
  },

  morphology: {
    title: 'Morphology tree', icon: '🦴', arrayKey: 'nodes', idField: 'id',
    label: n => n.displayName || n.id,
    sub: n => `col ${n.tier} · ${n.cost} EP · ${n.age}`,
    views: ['graph', 'form'],
    newItem: () => ({ id: 'new_trait', displayName: 'New Trait', tier: 0, row: 0, cost: 10, age: 'Cambrian', prerequisites: [], unlocksGenes: [], description: '' }),
    fields: treeFields('morphology'),
    validate: treeValidate('morphology'),
  },

  ethology: {
    title: 'Ethology tree', icon: '🐾', arrayKey: 'nodes', idField: 'id',
    label: n => n.displayName || n.id,
    sub: n => `col ${n.tier} · ${n.cost} EP · ${n.age}`,
    views: ['graph', 'form'],
    newItem: () => ({ id: 'new_behavior', displayName: 'New Behavior', tier: 0, row: 0, cost: 10, age: 'Cambrian', prerequisites: [], unlocksGenes: [], description: '' }),
    fields: treeFields('ethology'),
    validate: treeValidate('ethology'),
  },

  species: {
    title: 'Species', icon: '🦕', arrayKey: 'species', idField: 'id',
    label: s => s.commonName || s.id,
    sub: s => `${s.group || s.kingdom} · ${s.firstAge}${s.lastAge && s.lastAge !== s.firstAge ? '–' + s.lastAge : ''}${s.lastAge ? '' : '–today'}`,
    views: ['form'],
    groupBy: s => s.firstAge,
    newItem: () => ({ id: 'new_species', commonName: 'New Species', scientificName: '', kingdom: 'Animalia', group: '', firstAge: 'Cambrian', lastAge: '',
      habitats: ['SaltWater'], diet: 'Detritivore', sizeCm: 5, startingPopulation: 100, playable: false, genes: [], description: '' }),
    fields: [
      { key: 'id', label: 'ID', type: 'id' },
      { key: 'commonName', label: 'Common name', type: 'string' },
      { key: 'scientificName', label: 'Scientific name', type: 'string', italic: true },
      { key: 'kingdom', label: 'Kingdom', type: 'enum', options: KINGDOMS.map(k => ({ value: k, label: k })) },
      { key: 'group', label: 'Group', type: 'string', help: 'e.g. Arthropod, Chordate, Nautiloid cephalopod' },
      { key: 'firstAge', label: 'First appears', type: 'enum', options: ageOptions },
      { key: 'lastAge', label: 'Last appears', type: 'enum', options: (all) => [{ value: '', label: '— still alive today —' }, ...ageOptions(all)] },
      { key: 'habitats', label: 'Habitats', type: 'multienum', options: TERRAINS.map(t => ({ value: t, label: t })) },
      { key: 'diet', label: 'Diet', type: 'enum', options: DIETS.map(d => ({ value: d, label: d })) },
      { key: 'sizeCm', label: 'Body length (cm)', type: 'number', min: 0, step: 0.5 },
      { key: 'startingPopulation', label: 'Starting population', type: 'int', min: 0 },
      { key: 'playable', label: 'Playable', type: 'bool' },
      { key: 'genes', label: 'Starting genes', type: 'table', newRow: () => ({ gene: '', expression: 0.5 }), columns: [
        { key: 'gene', label: 'Gene', type: 'enum', options: (all) => [{ value: '', label: '—' }, ...idsOf('genes', 'displayName')(all)] },
        { key: 'expression', label: 'Expression', type: 'number', min: 0, max: 1, step: 0.05 },
      ] },
      { key: 'description', label: 'Description', type: 'text' },
    ],
    validate: (items) => {
      const out = [];
      items.forEach((s, i) => {
        if (s.lastAge && AGE_IDS.indexOf(s.lastAge) < AGE_IDS.indexOf(s.firstAge)) out.push({ index: i, level: 'error', msg: 'last age is before first age' });
        const genes = (s.genes || []).map(g => g.gene);
        if (new Set(genes).size !== genes.length) out.push({ index: i, level: 'warn', msg: 'a gene is listed twice' });
        if ((s.genes || []).some(g => !g.gene)) out.push({ index: i, level: 'warn', msg: 'a starting gene row has no gene' });
      });
      return out;
    },
  },

  realms: {
    title: 'Bio-realms', icon: '🗺️', arrayKey: 'realms', idField: 'id',
    label: r => r.displayName || r.id,
    sub: r => `${r.type}${r.thermalZone ? ' · ' + r.thermalZone : ''} · ${r.startingSlots} slots`,
    views: ['form'],
    groupBy: r => r.type,
    newItem: () => ({ id: 'new_realm', displayName: 'New Realm', type: 'Land', description: '', subrealms: [], dominantTerrains: [], startingSlots: 3, color: '#888888' }),
    fields: [
      { key: 'id', label: 'ID', type: 'id' },
      { key: 'displayName', label: 'Name', type: 'string' },
      { key: 'type', label: 'Type', type: 'enum', options: [{ value: 'Land', label: 'Land' }, { value: 'Marine', label: 'Marine' }] },
      { key: 'thermalZone', label: 'Thermal zone (marine)', type: 'enum', optional: true,
        options: [{ value: '', label: '—' }, ...['Polar', 'Temperate', 'Tropical'].map(z => ({ value: z, label: z }))] },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'subrealms', label: 'Subrealms', type: 'list', help: 'One per line.' },
      { key: 'dominantTerrains', label: 'Dominant terrains', type: 'multienum', options: TERRAINS.map(t => ({ value: t, label: t })) },
      { key: 'startingSlots', label: 'Starting slots', type: 'int', min: 0 },
      { key: 'color', label: 'Map color', type: 'color' },
    ],
  },
};

export const DATASET_ORDER = ['ages', 'climate_history', 'morphology', 'ethology', 'species', 'genes', 'realms'];

// Cross-dataset references: used for validation and to update references when an id is renamed.
// kind: 'value' = field holds one id, 'array' = list of ids, 'table' = list of rows, `column` holds the id
export const REFERENCES = [
  { from: 'morphology', field: 'prerequisites', kind: 'array', to: 'morphology' },
  { from: 'ethology', field: 'prerequisites', kind: 'array', to: 'ethology' },
  { from: 'morphology', field: 'unlocksGenes', kind: 'array', to: 'genes' },
  { from: 'ethology', field: 'unlocksGenes', kind: 'array', to: 'genes' },
  { from: 'species', field: 'genes', kind: 'table', column: 'gene', to: 'genes' },
  { from: 'genes', field: 'unlockAge', kind: 'value', to: 'ages' },
  { from: 'morphology', field: 'age', kind: 'value', to: 'ages' },
  { from: 'ethology', field: 'age', kind: 'value', to: 'ages' },
  { from: 'species', field: 'firstAge', kind: 'value', to: 'ages' },
  { from: 'species', field: 'lastAge', kind: 'value', to: 'ages', optional: true },
];
