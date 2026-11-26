import sys, re, glob
sys.path.insert(0, '/home/claude/tools'); import parse_md as P
files = [l.strip() for l in open('/home/claude/work/special_list.txt')] + sorted(glob.glob('codes/*.md')) + ['constitution/1987-constitution.md']
for f in files:
    try:
        m, t, pre, d, p = P.parse(f, 'x')
    except Exception as e:
        print('ERR', f, e); continue
    n = len(p); dt = sum(1 for x in p if x['kind'] == 'division-text')
    ch = sum(len(q) for x in p for q in x['paras'] if isinstance(q, str))
    kinds = {}
    for x in p: kinds[x['kind']] = kinds.get(x['kind'], 0) + 1
    print(f"{n:5d} dt{dt:3d} {ch:8d} | {m.get('identifier','')[:28]:28s} | {(m.get('title') or '')[:60]:60s} | {f[:70]} {kinds}")
