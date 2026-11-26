"""How many provisions in force have at least one case attached, per core code.
Counts textbook citations, digests, syllabus cases, recent rulings, doctrinal shifts and enforcement moves.
Written into catalog.json as 'cov': {code: [in force, with a case]}. Run after every other data step."""
import json, os
D = '/home/claude/site/data'
cat = json.load(open(f'{D}/catalog.json'))
syx = json.load(open(f'{D}/syllabus_index.json')) if os.path.exists(f'{D}/syllabus_index.json') else {}
rec = json.load(open(f'{D}/recent.json')).get('by', {}) if os.path.exists(f'{D}/recent.json') else {}
linked = set()
for s in json.load(open(f'{D}/shifts.json'))['shifts']:
    linked.update(s['links'])
for m in json.load(open(f'{D}/enforce.json'))['moves']:
    linked.update(f"{b['c']}|{b['i']}" for b in m['basis'] if 'c' in b)
cov = {}
for c in cat['codes']:
    if not c.get('core'):
        continue
    cid = c['id']
    d = json.load(open(f'{D}/codes/{cid}.json'))
    live = [p for p in d['provisions'] if not p.get('st')]
    cs = json.load(open(f'{D}/cases/{cid}.json')) if os.path.exists(f'{D}/cases/{cid}.json') else {}
    nt = json.load(open(f'{D}/notes/{cid}.json')) if os.path.exists(f'{D}/notes/{cid}.json') else {}
    n = 0
    for p in live:
        k = f"{cid}|{p['i']}"
        if cs.get(p['i']) or (nt.get(p['i']) or {}).get('d') or k in syx or k in rec or k in linked:
            n += 1
    cov[cid] = [len(live), n]
cat['cov'] = cov
json.dump(cat, open(f'{D}/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
tl = sum(v[0] for v in cov.values()); tn = sum(v[1] for v in cov.values())
print(f'coverage: {tn}/{tl} provisions in force in core codes have a case ({tn / tl * 100:.1f}%)')
