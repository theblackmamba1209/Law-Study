"""Is every amendment reflected in the study texts?
For each core code, take every later law that (per the statute graph) amended it, pull out the replacement text the
amending law prescribes ("Article N ... is hereby amended to read as follows: <text>"), and compare it with the text
the app shows as in force. Group by provision; only the latest amendment of each provision matters.
Output: work/audit/stale.json with, per provision, the latest amending law, the similarity, and both texts."""
import json, gzip, base64, re, difflib, os, sys
D = '/home/claude/site/data'
idx = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/idx.txt').read())))
rows = {r[0]: r for r in idx['rows']}
cache = {}
def rec(lid):
    c = rows[lid][6]
    if c not in cache:
        cache[c] = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/c{c:03d}.txt').read())))
    return cache[c][lid]
cat = json.load(open(f'{D}/catalog.json'))
CORE = [c['id'] for c in cat['codes'] if c.get('core')] + ['act496', 'ca613', 'pd603', 'carl', 'ra8042', 'ra9160', 'ra9208', 'ra8353', 'ra7659']

def plain(x):
    if isinstance(x, dict):
        return ' '.join(' '.join(r) for r in x.get('rows', []))
    return re.sub(r'⟨\d+⟩', '', str(x))
def toks(t):
    return re.findall(r'[a-z0-9]+', t.lower())
def sim(a, b):
    A, B = toks(a)[:400], toks(b)[:400]
    if not A or not B: return 0.0
    return difflib.SequenceMatcher(None, A, B, autojunk=False).ratio()

PROV = re.compile(r'^[\s>*_"“]*(?:Art(?:icle)?\.?|Sec(?:tion)?\.?)\s*(\d+(?:\s*-\s*[A-Za-z])?)\s*[.\-–—:]', re.I)
AMS = re.compile(r'(?:Articles?|Arts?\.|Sections?|Secs?\.)\s+(\d+(?:\s*-\s*[A-Za-z])?)[^.;]{0,300}?\b(?:is|are)\s+(?:hereby\s+)?(?:further\s+)?amended\s+(?:to\s+read|as\s+follows)', re.I)
HEAD = re.compile(r'^#{1,6}\s')

def blocks(body):
    """[(provision number, replacement text)] from an amending law."""
    out = []
    lines = body.split('\n')
    i = 0
    while i < len(lines):
        L = lines[i]
        m = AMS.search(re.sub(r'\s+', ' ', L))
        if not m:
            i += 1; continue
        # collect until the next heading of the amending law
        j, buf = i + 1, []
        while j < len(lines) and not HEAD.match(lines[j]):
            buf.append(lines[j]); j += 1
        # split the collected text at quoted provision starts
        cur_n, cur = None, []
        for b in buf:
            pm = PROV.match(b)
            if pm:
                if cur_n and cur: out.append((cur_n, ' '.join(cur)))
                cur_n, cur = re.sub(r'\s+', '', pm.group(1)).lower(), [b]
            elif cur_n:
                cur.append(b)
        if cur_n and cur: out.append((cur_n, ' '.join(cur)))
        elif buf and not cur_n:   # the sentence named the provision; the text follows without its number
            out.append((re.sub(r'\s+', '', m.group(1)).lower(), ' '.join(buf)))
        i = j
    return out

def current(p):
    a = p.get('a') or []
    if a:
        last = a[-1]
        return ' '.join(plain(x) for x in (last.get('p') or [])), last.get('by', '')
    return ' '.join(plain(x) for x in p['p']), 'as enacted'

res = {}
for cid in CORE:
    lid = cat['lawmap'].get(cid)
    if not lid or lid not in rows: continue
    d = json.load(open(f'{D}/codes/{cid}.json'))
    bynum, byold = {}, {}
    for p in d['provisions']:
        if p.get('n'):
            bynum.setdefault(str(p['n']).lower().replace(' ', ''), p)
        if p.get('o'):
            byold.setdefault(str(p['o']).lower().replace(' ', ''), p)
    latest = {}
    for src, kind, how, ev in rec(lid)['in']:
        if kind != 'a' or src not in rows: continue
        date = rows[src][4] or rows[src][3]
        for n, txt in blocks(rec(src)['b']):
            n = n.replace('–', '-')
            # renumbered codes (Labor Code, 2015): laws before the renumbering cite the old numbers
            table = byold if (byold and date < '2015-07-21') else bynum
            p = table.get(n)
            if not p or not txt.strip(): continue
            k = p['i']
            if k not in latest or date > latest[k][0]:
                latest[k] = (date, src, txt, n, p)
    out = []
    for k, (date, src, txt, n, p) in latest.items():
        if p.get('st'): continue
        cur, by = current(p)
        s = sim(txt, cur)
        out.append({'n': n, 'i': p['i'], 'src': src, 'date': date, 'sim': round(s, 3), 'by': by,
                    'new': re.sub(r'\s+', ' ', txt)[:1500], 'cur': cur[:1500]})
    res[cid] = sorted(out, key=lambda x: x['sim'])
os.makedirs('/home/claude/work/audit', exist_ok=True)
json.dump(res, open('/home/claude/work/audit/stale.json', 'w'), ensure_ascii=False, indent=1)
for cid, out in res.items():
    low = [x for x in out if x['sim'] < 0.85]
    if out:
        print(f"{cid:10} amended provisions found {len(out):3}  match {len(out) - len(low):3}  differ {len(low):3}")
