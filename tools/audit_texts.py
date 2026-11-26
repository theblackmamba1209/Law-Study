"""Compare each article of a library code (its latest amended text, if any) with Justitia's consolidated text.
Run with: python3 -I audit_texts.py CODE JUSTITIA_FILE ARTICLE_WORD   -> writes /home/claude/work/audit/CODE.json"""
import re, json, sys, html, difflib
code, jf, word = sys.argv[1], sys.argv[2], sys.argv[3]
t = open('/home/claude/limnestor/justitia/' + jf, encoding='utf-8', errors='ignore').read()
x = re.sub(r'<[^>]+>', ' ', t); x = html.unescape(x); x = re.sub(r'\s+', ' ', x)
parts = re.split(r'(?:ARTICLE|Article|Art\.)\s+(\d{1,4}(?:-[A-Z])?)\s*\.\s*', x) if word == 'art' else re.split(r'(?:SECTION|Section|Sec\.)\s+(\d{1,4}(?:-[A-Z])?)\s*\.\s*', x)
J = {}
for i in range(1, len(parts) - 1, 2):
    n = parts[i]
    if n not in J:  # first occurrence is the article itself in the body
        J[n] = parts[i + 1]
def norm(s):
    s = s.lower().replace('ó', 'o').replace('ñ', 'n')
    s = re.sub(r'\((?:\d+[a-z]?|n)(?:,\s*(?:\d+[a-z]?|n))*\)', ' ', s)
    return re.findall(r'[a-z0-9]+', s)
d = json.load(open(f'/home/claude/site/data/codes/{code}.json'))
out = []
for p in d['provisions']:
    n = p.get('n')
    if n not in J:
        continue
    cur = p['a'][-1]['p'] if p.get('a') else p['p']
    lib = norm(' '.join(([p.get('c') or ''] if not p.get('a') else []) + [q for q in cur if isinstance(q, str)]))
    jt = norm(J[n])[:len(lib) + 60]
    if not lib or not jt:
        continue
    sm = difflib.SequenceMatcher(None, lib, jt, autojunk=False)
    r = sm.ratio()
    if r < 0.86:
        ops = [(o, ' '.join(lib[a:b])[:90], ' '.join(jt[c:e])[:90]) for o, a, b, c, e in sm.get_opcodes() if o != 'equal']
        out.append({'n': n, 'i': p['i'], 'r': round(r, 3), 'lib': len(lib), 'jus': len(norm(J[n])), 'ops': ops[:5]})
json.dump(out, open(f'/home/claude/work/audit/{code}.json', 'w'), ensure_ascii=False, indent=1)
print(code, 'compared', sum(1 for p in d['provisions'] if p.get('n') in J), 'flagged', len(out))
