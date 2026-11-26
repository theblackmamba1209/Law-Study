"""Proofreading sweep over the study texts: find words that look like transcription errors.
A token is suspect if it is not in the English word list (hunspell en_US stems with simple inflections) and is rare
in the whole statute corpus, and a frequent known word lies one edit away. Also flags known OCR patterns.
Writes work/audit/proof_candidates.json for review; nothing is changed automatically."""
import json, os, re, gzip, base64, collections
D = '/home/claude/site/data'
# 1. vocabulary: hunspell stems + simple inflections
stems = set()
for line in open('/usr/share/hunspell/en_US.dic', encoding='utf-8', errors='ignore').read().split('\n')[1:]:
    w, _, flags = line.partition('/')
    w = w.strip().lower()
    if not w: continue
    stems.add(w)
    for suf in ('s', 'es', 'ed', 'd', 'ing', 'ly', 'er', 'ers', 'ment', 'ments', 'ness', 'ion', 'ions', "'s"):
        stems.add(w + suf)
    if w.endswith('e'):
        stems.update({w[:-1] + 'ing', w[:-1] + 'ion', w[:-1] + 'ions'})
    if w.endswith('y'):
        stems.update({w[:-1] + 'ies', w[:-1] + 'ied'})
# 2. corpus frequencies (statute library) — legal and Philippine vocabulary
idx = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/idx.txt').read())))
freq = collections.Counter()
for f in sorted(os.listdir(f'{D}/statutes')):
    if not f.startswith('c'): continue
    ch = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/{f}').read())))
    for rec in ch.values():
        freq.update(re.findall(r"[a-z]+", rec['b'].lower()))
known = lambda w: w in stems or freq[w] >= 6
# 3. study texts
def texts(p):
    out = []
    for x in p.get('p', []):
        if isinstance(x, str): out.append(('p', x))
    for a in p.get('a', []):
        for x in a.get('p', []):
            if isinstance(x, str): out.append(('a', x))
    if p.get('c'): out.append(('c', p['c']))
    return out
alpha = 'abcdefghijklmnopqrstuvwxyz'
def edits1(w):
    s = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    return {a + b[1:] for a, b in s if b} | {a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1} | \
           {a + c + b[1:] for a, b in s if b for c in alpha} | {a + c + b for a, b in s for c in alpha}
PAT = [(re.compile(r'\b(\w+)\s+\1\b', re.I), 'repeated word'),
       (re.compile(r'[a-z]\.\s+[a-z]{2,}\b(?<!\be\.g)(?<!\bi\.e)'), 'period then lower case'),
       (re.compile(r'\b(tbe|tlie|lhe|ihe|thc|aud|aml|ot the|io the|rnay|rnust|rnore|frorn|frorn|cornpany|rnade|tirne|norn|tho|wbich|whicb|sball|sliall|shali|shail)\b', re.I), 'OCR confusion'),
       (re.compile(r'\b\w*[a-z][0-9][a-z]\w*\b', re.I), 'digit inside a word'),
       (re.compile(r'[a-z]{3,}[A-Z][a-z]{2,}'), 'missing space')]
out = []
for f in sorted(os.listdir(f'{D}/codes')):
    if not f.endswith('.json'): continue
    d = json.load(open(f'{D}/codes/{f}'))
    for p in d['provisions']:
        for kind, t in texts(p):
            for m in re.finditer(r"[A-Za-z]+", t):
                w = m.group(0); lw = w.lower()
                if len(lw) < 4 or known(lw) or w.isupper():
                    continue
                cands = [c for c in edits1(lw) if (c in stems and freq[c] >= 20) or freq[c] >= 200]
                if cands:
                    best = max(cands, key=lambda c: freq[c])
                    out.append({'code': d['id'], 'i': p['i'], 'kind': kind, 'word': w, 'fix': best, 'f': freq[lw], 'ctx': t[max(0, m.start() - 50):m.end() + 50]})
            for rx, why in PAT:
                for m in rx.finditer(t):
                    if why == 'repeated word' and m.group(1).lower() in ('that', 'had', 'is', 'x'):
                        continue
                    if why == 'period then lower case' and re.search(r'\b(No|Nos|Sec|Secs|Art|Arts|par|pars|vs|v|Inc|Co|Corp|Jr|Sr|St|Atty|Dr|Mr|Mrs|Gen|Hon|Rep|Blg|i\.e|e\.g|et al|cf|viz|etc|p|pp|s|ed|Vol|R\.A|P\.D|B\.P|C\.A|E\.O)\.\s+[a-z]', t[max(0, m.start() - 8):m.end() + 1]):
                        continue
                    out.append({'code': d['id'], 'i': p['i'], 'kind': kind, 'pattern': why, 'match': m.group(0), 'ctx': t[max(0, m.start() - 50):m.end() + 50]})
os.makedirs('/home/claude/work/audit', exist_ok=True)
json.dump(out, open('/home/claude/work/audit/proof_candidates.json', 'w'), ensure_ascii=False, indent=0)
c = collections.Counter(x.get('pattern', 'near-word') for x in out)
print(len(out), dict(c))
print(collections.Counter(x['code'] for x in out).most_common(25))
