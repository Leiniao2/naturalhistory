"""
Checks that every evolution link's required Functions and Behaviors (evolution.json) can be had by
the species it starts from, following the game's rules: a species starts with the free root items
its body plan allows (trait_rules.json tags), inherits everything from the species it evolved from
plus the link's grants, and can acquire any item its body plan allows once the item's prerequisites
are had; a prerequisite its body plan can never have doesn't hold it back (EvolutionData.Blocks).
Periods and EP are left out. Run from the repository root:

    python3 tools/evolution/check_requirements.py
"""
import json
D='Assets/Resources/Data/'
sp={s['id']:s for s in (lambda d: d['species'] if isinstance(d,dict) else d)(json.load(open(D+'species.json')))}
links=json.load(open(D+'evolution.json'))['links']
rules=json.load(open(D+'trait_rules.json'))
gt={g['group']:set(g['tags']) for g in rules['groups']}
ft={r['item']:set(r['tags']) for r in rules['functions']}
bt={r['item']:set(r['tags']) for r in rules['behaviors']}
trees={'f':{n['id']:n for n in json.load(open(D+'morphology.json'))['nodes']},'b':{n['id']:n for n in json.load(open(D+'ethology.json'))['nodes']}}
def tags(s): return gt.get(sp[s].get('group'),{'Animal'})
def can(s,k,n): need=(ft if k=='f' else bt).get(n,{'Animal'}); return bool(need & tags(s))
def closure(s,seed):
    r={'f':set(seed['f']),'b':set(seed['b'])}
    ch=True
    while ch:
        ch=False
        for k in 'fb':
            for n,d in trees[k].items():
                if n not in r[k] and can(s,k,n) and all(p in r[k] or not can(s,k,p) for p in d["prerequisites"]):
                    r[k].add(n); ch=True
    return r
reach={}
preds={}
for l in links: preds.setdefault(l['to'],[]).append(l)
def R(s,stack=()):
    if s in reach: return reach[s]
    if s in stack: return {'f':set(),'b':set()}
    seed={'f':{n for n,d in trees['f'].items() if d['cost']<=0 and not d['prerequisites'] and can(s,'f',n)},
          'b':{n for n,d in trees['b'].items() if d['cost']<=0 and not d['prerequisites'] and can(s,'b',n)}}
    for l in preds.get(s,[]):
        p=R(l['from'],stack+(s,))
        seed['f']|=p['f']|set(l.get('grantFunctions',[])); seed['b']|=p['b']|set(l.get('grantBehaviors',[]))
    reach[s]=closure(s,seed); return reach[s]
bad=[]
for l in links:
    if l['from'] not in sp: continue
    r=R(l['from'])
    for k,key in (('f','functions'),('b','behaviors')):
        for n in l.get(key,[]):
            if n not in r[k]:
                d=trees[k].get(n)
                why='unknown item' if d is None else ('body plan' if not can(l['from'],k,n) else 'prereq '+','.join(p for p in d['prerequisites'] if p not in r[k]))
                bad.append((l['from'],l['to'],k,n,why))
print(len(links),'links;',len(bad),'impossible requirements in',len({(b[0],b[1]) for b in bad}),'links')
from collections import Counter
print(Counter(b[4].split(' ')[0] for b in bad))
for b in bad[:40]: print(b)
