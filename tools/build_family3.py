import json, re
lines = json.load(open('/home/claude/work/fam_lines.json'))
# drop running footers like "Executive Order No. 209 ... page N"
paras, buf = [], []
def flush():
    if buf:
        paras.append(('P', re.sub(r'\s+', ' ', ' '.join(buf)).strip())); buf.clear()
for pn, x0, bold, s in lines:
    t = s.strip()
    if re.match(r'^Executive Order No\. 209\s+page \d+$', t, re.I) or re.match(r'^page \d+$', t, re.I):
        continue
    if not t:
        flush(); continue
    if bold:
        flush(); paras.append(('H', re.sub(r'\s+', ' ', t))); continue
    buf.append(t)
flush()
# merge consecutive heading lines (TITLE I + MARRIAGE)
divisions, provisions, stack, cur, pre, closing = [], [], [], None, [], []
LV = lambda h: 0 if re.match(r'^TITLE\b', h) else 1 if re.match(r'^Chapter\b', h, re.I) else 2 if re.match(r'^Section\b', h, re.I) else 3
i = 0
started = False
while i < len(paras):
    k, t = paras[i]
    if k == 'H':
        if not started and not re.match(r'^(TITLE|Chapter)', t):
            i += 1; continue
        started = True
        if re.match(r'^TITLE\s+[IVXL]+$', t) and i + 1 < len(paras) and paras[i+1][0] == 'H':
            t = t + ' — ' + paras[i+1][1]; i += 1
        while i + 1 < len(paras) and paras[i+1][0] == 'H' and not re.match(r'^(TITLE|Chapter|Section)\b', paras[i+1][1], re.I):
            t = t + ' ' + paras[i+1][1]; i += 1
        lvl = LV(t)
        while stack and divisions[stack[-1]]['lvl'] >= lvl: stack.pop()
        divisions.append({'t': t, 'lvl': lvl, 'parent': stack[-1] if stack else None})
        stack.append(len(divisions) - 1); i += 1; continue
    m = re.match(r'^Art\.\s*(\d+)\.?\s+(.*)$', t)
    if m:
        started = True
        cur = {'kind': 'article', 'n': m.group(1), 'div': stack[-1] if stack else None, 'paras': [m.group(2)]}
        provisions.append(cur)
    elif not started:
        pre.append(t)
    elif cur:
        if re.match(r'^(Done in|DONE in|By the President|\(Sgd\.\))', t):
            closing.append(t); cur = None
        else:
            cur['paras'].append(t)
    else:
        closing.append(t)
    i += 1
nums = [int(p['n']) for p in provisions]
print('divisions', len(divisions), 'provisions', len(provisions), 'missing', [n for n in range(1, max(nums)+1) if n not in nums], 'dups', sorted({n for n in nums if nums.count(n) > 1}))
for d in divisions: print(d['lvl'], d['t'])
json.dump({'meta': {}, 'title': 'The Family Code of the Philippines', 'pre': pre, 'divisions': divisions, 'provisions': provisions, 'closing': closing},
          open('/home/claude/work/family/family.json', 'w'), ensure_ascii=False, indent=1)
print(pre); print(closing[:5])
