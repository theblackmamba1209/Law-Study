import json, re, difflib
dl = json.load(open('/home/claude/work/deleon/deleon_index.json'))['codal']
cc = json.load(open('/home/claude/site/data/codes/civil.json'))
lp = {p.get('n'): ' '.join(x for x in p['p'] if isinstance(x, str)) for p in cc['provisions']}
def norm(s):
    s = s.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'").replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    s = re.sub(r'\s+', ' ', s)
    return re.findall(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]", s)
out = []
for n, d in sorted(dl.items(), key=lambda x: int(x[0])):
    if n not in lp: out.append((n, 'MISSING IN LAWPHIL', d['t'][:150])); continue
    a, b = norm(lp[n]), norm(d['t'])
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diffs = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal': continue
        A, B = ' '.join(a[a1:a2]), ' '.join(b[b1:b2])
        if set(A + B) <= set('.,;:()"\' '): continue
        diffs.append((op, A, B, ' '.join(a[max(0,a1-5):a1])))
    if diffs: out.append((n, d['page'], diffs))
json.dump(out, open('/home/claude/work/deleon/xcheck.json', 'w'), ensure_ascii=False, indent=0)
print(len(out), 'articles with differences of', len(dl))
for x in out: print(x)
