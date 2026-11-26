"""Whole-word corrections of transcription slips (tools/spellfix.json), shared by build_data.py and build_scrules.py."""
import json, os, re

SF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spellfix.json')))


def apply(cid, divisions, provs, log):
    """Correct the text, captions, amendment texts, consolidated texts, table cells and headings of one code.
    Every entry is logged; one that finds nothing is logged as not applied, so stale entries show up."""
    for e in SF.get(cid, []):
        rx = re.compile(r'(?<![A-Za-z0-9])' + re.escape(e['f']) + r'(?![A-Za-z0-9])')
        n = 0
        def fix(s):
            nonlocal n
            if not isinstance(s, str): return s
            t, k = rx.subn(lambda m: e['t'], s); n += k
            return t
        def fixlist(ps):
            for j, x in enumerate(ps):
                if isinstance(x, str): ps[j] = fix(x)
                elif isinstance(x, dict) and x.get('rows'):
                    x['rows'] = [[fix(c) for c in r] for r in x['rows']]
        for d in divisions:
            d['t'] = fix(d['t'])
        for p in provs:
            before = n
            fixlist(p['p'])
            if p.get('c'): p['c'] = fix(p['c'])
            for a in p.get('a', []):
                fixlist(a.get('p', []))
                if a.get('cons'): fixlist(a['cons'])
            if n > before:
                p.setdefault('sf', []).append(f'“{e["f"]}” → “{e["t"]}”')
        log.append({'code': cid, 'n': '', 'op': 'spelling', 'applied': n > 0, 'note': f'“{e["f"]}” → “{e["t"]}” ({n}×)'})
    for p in provs:
        if p.get('sf'):
            p.setdefault('e', []).append({'t': 'Transcription slip(s) in the source text corrected: ' + '; '.join(p.pop('sf')) + '.', 'b': 'Proofreading'})


MARK = re.compile(r'^(?:[a-z]{1,2}[.)]\s|[ivx]{1,5}[.)](?:\s|$)|x x x|[a-z]\.\)\s|[a-z]{1,4}[.)]$|[a-z] [A-Z]|[a-z]\.\d)')


def join_broken(cid, provs, log):
    """Rejoin a paragraph the source broke in mid-sentence: the first part ends in a lower-case word or a comma, the
    second begins in lower case and is not a list marker. List items ending "; and" are left alone."""
    n = 0
    for p in provs:
        for lst in [p['p']] + [a['p'] for a in p.get('a', [])]:
            j = 0
            while j < len(lst) - 1:
                a, b = lst[j], lst[j + 1]
                if (isinstance(a, str) and isinstance(b, str) and re.search(r'[a-z,]$', a) and re.match(r'^[a-z]', b)
                        and not MARK.match(b) and not re.search(r'(?:x x x|[;,] (?:and|or)|No\. of Months)$', a)):
                    lst[j] = a + ' ' + b; del lst[j + 1]; n += 1
                    continue
                j += 1
    if n:
        log.append({'code': cid, 'n': '', 'op': 'rejoin', 'applied': True, 'note': f'{n} paragraph(s) the source broke in mid-sentence rejoined'})
