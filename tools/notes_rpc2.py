"""Revised Penal Code, Book Two: study notes in our own words, merged into data/notes/rpc.json.

Accuracy check: 'chk' lists words that must appear in the TEXT IN FORCE of the article (the latest amendment
shown in full, or its consolidated text; otherwise the text as enacted). A note that quotes a superseded number
or penalty therefore cannot be published. Repealed articles are checked against their last text.
The notes are split by Title into rpc2_*.py modules; each defines add(n).
"""
import json, re, importlib

SITE = '/home/claude/site/data'
N = {}


def n(a, x, k=None, t=None, w=None, d=None, i=None, q=None, chk=()):
    e = {'x': x}
    for key, v in (('k', k), ('t', t), ('w', w), ('d', d), ('i', i), ('q', q)):
        if v:
            e[key] = v
    N[f'article-{str(a).lower()}'] = (e, chk)


def inforce(p):
    a = (p.get('a') or [None])[-1]
    if a:
        src = a.get('cons') or a['p']
        if a.get('cons') or not re.search(r'\bx\s*x\s*x\b', ' '.join(src), re.I):
            return ' '.join(x for x in src if isinstance(x, str))
        return ' '.join(x for x in p['p'] if isinstance(x, str)) + ' ' + ' '.join(src)
    return ' '.join(x for x in p['p'] if isinstance(x, str))


def main():
    for m in ('rpc2_t1', 'rpc2_t4', 'rpc2_t7', 'rpc2_t8', 'rpc2_t10', 'rpc2_t11'):
        try:
            importlib.import_module(m).add(n)
        except ModuleNotFoundError as ex:
            if ex.name != m:
                raise
    d = json.load(open(f'{SITE}/codes/rpc.json'))
    by = {p['i']: p for p in d['provisions']}
    norm = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')).lower()
    errs = []
    for pid, (e, chk) in N.items():
        if pid not in by:
            errs.append('no such provision ' + pid); continue
        text = norm(inforce(by[pid]))
        for c in chk:
            if norm(c) not in text:
                errs.append(f'{pid}: “{c}” not in the text in force')
    if errs:
        raise SystemExit('\n'.join(errs))
    cur = json.load(open(f'{SITE}/notes/rpc.json'))
    for pid, (e, _) in N.items():
        cur[pid] = {**cur.get(pid, {}), **e}
    json.dump(cur, open(f'{SITE}/notes/rpc.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    ids = [p['i'] for p in d['provisions'] if p['l'].startswith('Article')]
    k = ids.index('article-114')
    print('RPC Book Two notes:', len(N), '| Book Two annotated:', sum(1 for i in ids[k:] if i in cur), 'of', len(ids[k:]), '| rpc notes total:', len(cur))


if __name__ == '__main__':
    main()
