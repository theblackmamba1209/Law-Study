"""Every Philippine statute, as enacted, with the amendment and repeal history detected from the laws' own text.

Source: LawCodex (github.com/LawCodex/ph), a Markdown transcription of The LawPhil Project's statute pages:
Acts of the Philippine Commission and Legislature, Commonwealth Acts, Republic Acts, Presidential Decrees,
Batas Pambansa, Executive Orders and the six constitutions. Texts are as enacted; nothing is consolidated.

The history ("evolution") of each law is built from two kinds of evidence, both shown to the learner:
  1. a later law's title that says it amends, expands, revises or repeals this one;
  2. a sentence in a later law's body saying a provision of this law "is hereby amended" or "repealed".
Each edge keeps the sentence it came from, so every claim can be checked against the text.

Output (gzip JSON stored as base64 text, decoded in the browser):
  data/statutes/idx.txt  one row per instrument + the study-library map
  data/statutes/cNNN.txt bodies and histories, about 2.5 MB of text per chunk
"""
import os, re, json, gzip, sys
ROOT = '/home/claude/ext/lawcodex'
OUT = '/home/claude/site/data/statutes'
SER = {'republic-acts': 'ra', 'commonwealth-acts': 'ca', 'batas-pambansa': 'bp', 'presidential-decrees': 'pd',
       'executive-orders': 'eo', 'acts': 'act', 'constitution': 'const'}
ORDER = ['const', 'act', 'ca', 'ra', 'pd', 'bp', 'eo']

def fm(text):
    if not text.startswith('---'):
        return {}, text
    end = text.index('\n---', 3)
    meta = {}
    for line in text[3:end].strip().split('\n'):
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        meta[k.strip()] = v
    return meta, text[end + 4:].lstrip('\n')

laws = {}
for d, s in SER.items():
    for root, _, files in os.walk(os.path.join(ROOT, d)):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            meta, body = fm(open(os.path.join(root, fn), encoding='utf-8').read())
            date = meta.get('date', '') if re.match(r'\d{4}-\d\d-\d\d', meta.get('date', '')) else ''
            year = date[:4] or (os.path.basename(root) if os.path.basename(root).isdigit() else '')
            if s == 'const':
                num = fn[:4]; year = year or num
            else:
                num = meta.get('number', '').strip().lower()
                if not num:
                    m = re.match(r'[a-z]+-([0-9]+(?:-[a-z])?)', fn); num = m.group(1) if m else fn
            lid = f'{s}-{num}' + (f'-{year}' if s == 'eo' else '')
            while lid in laws:
                lid += 'x'
            title = meta.get('title', '')
            if ' — ' in title:
                title = title.split(' — ', 1)[1]
            laws[lid] = dict(id=lid, s=s, n=num, y=year, d=date, t=title, ident=meta.get('identifier', ''),
                             src=meta.get('source', ''), note=meta.get('note', ''), body=body)
print('instruments', len(laws))

# ------------------------------------------------------------------ references
NUM = r'(\d{1,5}(?:-[A-Za-z])?)'
PATS = [
    ('ra', re.compile(r'\b(?:Republic\s+Acts?|Rep\.\s*Act|R\.\s*A\.|RA)\s*(?:No\.|Nos\.|Number|Numbered|No)?\s*' + NUM, re.I)),
    ('ca', re.compile(r'\b(?:Commonwealth\s+Acts?|C\.\s*A\.|CA)\s*(?:No\.|Nos\.|Numbered|No)?\s*' + NUM)),
    ('bp', re.compile(r'\b(?:Batas\s+Pambansa|B\.\s*P\.|BP)\s*(?:Blg\.|Bilang|Blg|No\.|Nos\.)?\s*' + NUM, re.I)),
    ('pd', re.compile(r'\b(?:Presidential\s+Decrees?|P\.\s*D\.|PD)\s*(?:No\.|Nos\.|Numbered|No)?\s*' + NUM, re.I)),
    ('eo', re.compile(r'\b(?:Executive\s+Orders?|E\.\s*O\.|EO)\s*(?:No\.|Nos\.|No)?\s*' + NUM, re.I)),
    ('act', re.compile(r'\bActs?\s+(?:No\.|Nos\.|Numbered)\s*' + NUM)),
]
LIST = re.compile(r'\s*(?:,|and|&)\s*(?:No\.\s*)?(\d{1,5}(?:-[A-Za-z])?)')
ALIASES = {  # unambiguous names used without a number
    'revised penal code': 'act-3815', 'civil code of the philippines': 'ra-386', 'labor code of the philippines': 'pd-442',
    'family code of the philippines': 'eo-209-1987', 'local government code of 1991': 'ra-7160', 'omnibus election code': 'bp-881',
    'administrative code of 1987': 'eo-292-1987', 'national internal revenue code of 1997': 'ra-8424', 'revised corporation code': 'ra-11232',
    'intellectual property code of the philippines': 'ra-8293', 'child and youth welfare code': 'pd-603', 'property registration decree': 'pd-1529',
    'comprehensive dangerous drugs act of 2002': 'ra-9165', 'anti-graft and corrupt practices act': 'ra-3019', 'tariff and customs code of the philippines': 'pd-1464',
}
DATED = {
    'revised administrative code': [('1987-07-25', 'act-2711')],
    'code of civil procedure': [('1940-07-01', 'act-190')],
    'corporation law': [('1980-05-01', 'act-1459')],
    'national internal revenue code': [('1977-06-03', 'ca-466'), ('1998-01-01', 'pd-1158'), ('9999', 'ra-8424')],
    'revised election code': [('1971-12-31', 'ra-180')],
}
ALIASES_ALL = list(ALIASES) + list(DATED)
ALIAS_RE = re.compile('|'.join(re.escape(k) for k in sorted(ALIASES_ALL, key=len, reverse=True)), re.I)
eo_by_num = {}
for l in laws.values():
    if l['s'] == 'eo':
        eo_by_num.setdefault(l['n'], []).append(l)

def resolve(series, num, ctx, citer):
    num = num.lower()
    if series != 'eo':
        lid = f'{series}-{num}'
        return lid if lid in laws else None
    cands = eo_by_num.get(num, [])
    m = re.search(r'(?:s\.|series\s+of|dated[^.;]{0,40}?)\s*(\d{4})', ctx[:80], re.I)
    if m:
        c = [x for x in cands if x['y'] == m.group(1)]
        return c[0]['id'] if len(c) == 1 else None
    c = [x for x in cands if not citer['d'] or not x['d'] or x['d'] <= citer['d']]
    return c[0]['id'] if len(c) == 1 else None

def refs(text, citer):
    """[(id, start, end)] for every resolvable reference, skipping the citing law itself."""
    out = []
    for series, pat in PATS:
        for m in pat.finditer(text):
            if series == 'act':
                pre = text[max(0, m.start() - 16):m.start()].lower()
                if re.search(r'(republic|commonwealth|rep\.)\s*$', pre):
                    continue
            nums = [(m.group(1), m.end())]
            if re.search(r'Nos\.|Numbered', m.group(0)):
                pos = m.end()
                while True:
                    lm = LIST.match(text, pos)
                    if not lm:
                        break
                    nums.append((lm.group(1), lm.end())); pos = lm.end()
            for n, e in nums:
                lid = resolve(series, n, text[e:e + 80], citer)
                if lid and lid != citer['id']:
                    out.append((lid, m.start(), e))
    for m in ALIAS_RE.finditer(text):
        k = m.group(0).lower()
        if k in ALIASES:
            lid = ALIASES[k]
        else:
            d = citer['d'] or (citer['y'] + '-06-30' if citer['y'] else '')
            lid = next((x for lim, x in DATED[k] if d and d < lim), None)
        if lid and lid in laws and lid != citer['id']:
            out.append((lid, m.start(), m.end()))
    return sorted(out, key=lambda x: x[1])

# numbers written in words ("Act Numbered Fourteen Hundred and Fifty-Nine")
UNITS = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split())}
TENS = {w: 10 * (i + 2) for i, w in enumerate('twenty thirty forty fifty sixty seventy eighty ninety'.split())}
NW = r'(?:' + '|'.join(sorted(list(UNITS) + list(TENS) + ['hundred', 'thousand'], key=len, reverse=True)) + r')'
PHRASE = re.compile(r'\b(Numbered|Nos?\.|Number)\s+(' + NW + r'(?:[\s\-]+(?:and\s+)?' + NW + r')*)\b', re.I)
def words2num(ws):
    total = cur = 0
    for w in ws:
        w = w.lower()
        if w in UNITS: cur += UNITS[w]
        elif w in TENS: cur += TENS[w]
        elif w == 'hundred': cur = (cur or 1) * 100
        elif w == 'thousand': total += (cur or 1) * 1000; cur = 0
    return total + cur
def norm(text):
    """Rewrite number words after 'Numbered'/'No.' into digits; split lists at 'and' unless it follows hundred/thousand."""
    def sub(m):
        toks = re.findall(r'[A-Za-z]+', m.group(2))
        groups, cur = [], []
        for i, t in enumerate(toks):
            if t.lower() == 'and':
                if cur and cur[-1].lower() in ('hundred', 'thousand'):
                    continue
                groups.append(cur); cur = []; continue
            cur.append(t)
        groups.append(cur)
        nums = [str(words2num(g)) for g in groups if g]
        return m.group(1) + ' ' + ' and '.join(nums) if len(nums) == 1 else 'Nos. ' + ', '.join(nums)
    return PHRASE.sub(sub, text)

ABBR = set('no nos sec secs art arts blg rep pres gen hon inc co corp jr sr atty dr mr mrs ms st ph vs s par pars cf ibid etc a b c d e f g h i j k l m n o p q r t u v w x y z'.split())
def sentences(par):
    out, start = [], 0
    for m in re.finditer(r'[.;:]\s+(?=[A-Z“"(\[])', par):
        w = re.search(r'([A-Za-z]+)$', par[start:m.start()])
        if m.group(0)[0] == '.' and w and w.group(1).lower() in ABBR:
            continue
        out.append(par[start:m.start() + 1]); start = m.end()
    out.append(par[start:])
    return out

AMEND_S = re.compile(r'\b(?:hereby\s+(?:further\s+)?amended|(?:is|are)\s+(?:hereby\s+)?(?:further\s+)?amended\s+to\s+read|amended\s+as\s+follows)', re.I)
REPEAL_S = re.compile(r'\b(?:hereby\s+)?(?:expressly\s+)?repealed\b', re.I)
# a sentence that says a law is NOT repealed, or stays in force
NEG = re.compile(r'\bnot\s+(?:be\s+)?(?:deemed\s+|construed\s+(?:as\s+)?)?(?:to\s+)?(?:have\s+)?repeal|shall\s+not\s+be\s+construed|nothing\s+in\s+this'
                 r'|\bnot\s+in\s+any\s+(?:way|manner)|\bin\s+no\s+case\b|shall\s+not\s+(?:in\s+any\s+way\s+)?be\s+(?:\w+\s+(?:or|and/or)\s+)?repealed'
                 r'|\b(?:shall\s+)?remain\s+(?:in\s+(?:full\s+)?force|applicable|valid|effective|operative)'
                 r'|\bunless\s+[^.;]{0,80}?repealed|\bif\s+[^.;]{0,40}?(?:is|are)\s+repealed|\bin\s+case\s+[^.;]{0,60}?repealed', re.I)
# words before a reference that make it a piece of the law, not the whole law
PIECE_W = re.compile(r'\b(?:Sections?|Secs?\.|Articles?|Arts?\.|(?:sub-?)?paragraphs?|pars?\.|items?|Titles?|Chapters?|Books?|Parts?|portions?|provisions?|so\s+much|pertinent|appropriations?|Special\s+Provisions?|crimes?\s+of|annex(?:es)?|schedules?|subsections?)\b', re.I)
DISTRIB = re.compile(r'\b(?:provisions?|portions?|parts?|pertinent|so\s+much|such)\b', re.I)
# words between the reference and the verb (or right after the verb) that limit the repeal
PARTIAL = re.compile(r'insofar|in\s+so\s+far|inconsistent|in\s+conflict|contrary|modified|partially|in\s+part|so\s+much\s+of|portion|provisions?\s+of|\bexcept\b|to\s+the\s+extent|thereof|particularly|specifically|pertinent|relating\s+to|relative\s+to|which\s+(?:are|is|may)', re.I)
TAIL = re.compile(r'^\W*(?:insofar|in\s+so\s+far|to\s+the\s+extent|as\s+far\s+as|only|except|with\s+respect|as\s+regards|(?:,?\s*(?:or|and/or|and)\s+)?(?:modified|amended|superseded)|accordingly)', re.I)
GENERAL = re.compile(r'\b(?:and|as\s+well\s+as|together\s+with|including)\s+(?:all|any|other|the\s+other)\b', re.I)
TITLE_VERB = re.compile(r'\b(amend(?:ing|s|atory)?\b|expand\w*|strengthen\w*|revis\w*|modif\w*|adjust\w*|increas\w*|extend\w*|repeal(?:ing|s)?\b|supersed(?:ing|es?)\b|reviv\w*|reconstitut\w*)', re.I)
TITLE_TAIL = re.compile(r'^[^;]{0,120}?\b(?:so\s+far\s+as|insofar|in\s+so\s+far|as\s+regards|with\s+respect\s+to|in\s+its\s+application|to\s+the\s+extent)', re.I)
# known errors in the source titles (a misprinted number would point at the wrong law)
DROP = {('ra-11930', 'ra-977')}
NOTE = re.compile(r'^[\s*_(\[]*(?:as\s+)?(amended|repealed|superseded|modified)\s+by\s+(.+?)[)\]_*\s]*$', re.I)

QUOTED = re.compile(r'[“"][^”"]{3,900}[”"]')
PRIOR = re.compile(r'\b(?:as\s+)?(?:amended|revised|modified|repealed|supplemented|superseded)\s+by\b', re.I)
GOVERN = re.compile(r'\b(?:is|are)\s+(?:hereby\s+)?(?:further\s+)?(?:amended|repealed)|\bhereby\b|\bamending\b|\brepealing\b|\bexpanding\b|\bstrengthening\b|\brevising\b', re.I)
# a reference that is only mentioned: the law something was done under, the standard of comparison, or an exception
MENTION = re.compile(r'(?:pursuant\s+to|under|in\s+accordance\s+with|provided\s+(?:for\s+)?(?:in|by|under)|created\s+(?:by|under)|mandated\s+by|authorized\s+(?:by|under)|granted\s+(?:by|under)|in\s+relation\s+to|referred\s+to\s+in'
                     r'|by\s+virtue\s+(?:of|by)|conform(?:ity)?\s+with|consistent\s+with|inconsistent\s+with|contrary\s+to|in\s+conflict\s+with|repugnant\s+to'
                     r'|except|other\s+than|excluding|exception\s+of)\s+(?:(?:the|said)\s+)?(?:(?:the\s+)?provisions?\s+of\s+(?:the\s+|this\s+Act\s+(?:and|or)\s+)?)?(?:(?:Sections?|Sec\.|Articles?|Art\.)\s+[\w\-,()\s]{0,40}?\s+of\s+(?:the\s+)?)?$', re.I)
# a second name for the law just cited ("..., otherwise known as the Labor Code"): the first reference decides
ALIAS_OF = re.compile(r'(?:otherwise|also)\s+known\s+as\s+(?:the\s+)?$|\bor\s+the\s+$|\bentitled\s+$', re.I)
def mask(text):
    """Blank out quoted titles (their references belong to the quoted law) and the lists after 'as amended by'
    up to the governing verb, keeping positions so evidence lines up."""
    t = QUOTED.sub(lambda m: ' ' * len(m.group(0)), text)
    # a quoted title left open (truncated source): its words belong to the quoted law, so blank to the end
    u = re.search(r'\b(?:entitled|known\s+as)[,:]?\s*[“"]', t, re.I)
    if u and not re.search(r'[”"]', t[u.end():]):
        t = t[:u.end()] + ' ' * (len(t) - u.end())
    out = list(t)
    for m in PRIOR.finditer(t):
        g = GOVERN.search(t, m.end())
        end = g.start() if g else len(t)
        for i in range(m.end(), end):
            out[i] = ' '
    return ''.join(out)
WEAK = ('expand', 'strengthen', 'revis', 'modif', 'adjust', 'increas', 'extend', 'reviv', 'reconstitut')

def partial_repeal(sent, a, b, prev_end, vr):
    """Is this a repeal of part of the law only? Conservative: anything short of a clean
    'Law X [, as amended / otherwise known as ...] is hereby repealed' counts as partial."""
    before = sent[prev_end:a] if prev_end <= a else ''
    before = re.sub(r'^.*?(?:Clauses?|Repeals?|Repealed)[._\s]*[\-–—:]+\s*', '', before)    # drop a 'Repealing Clause. —' heading
    if PIECE_W.search(before):
        return True
    first = next((m.start() for m in re.finditer(r'\b(?:Republic|Commonwealth|Act|Acts|Presidential|Batas|Executive|P\.D\.|R\.A\.|B\.P\.|E\.O\.|C\.A\.)\b', sent)), a)
    if DISTRIB.search(re.sub(r'^.*?(?:Clauses?|Repeals?)[._\s]*[\-–—:]+\s*', '', sent[:min(first, a)])):
        return True
    between = sent[b:vr.start()]
    g = GENERAL.search(between)
    if g:
        between = between[:g.start()]
    if PARTIAL.search(between):
        return True
    return bool(TAIL.search(sent[vr.end():vr.end() + 60]))

edges = {}  # (src, dst, kind) -> evidence
def add(src, dst, kind, ev, how):
    if (src, dst) in DROP:
        return
    k = (src, dst, kind)
    if k not in edges:
        edges[k] = (ev.strip()[:320], how)

for l in laws.values():
    if l['s'] == 'const':
        continue
    # 1. the title
    t0 = norm(l['t']); t = mask(t0)
    prev_end = 0
    for lid, a, b in refs(t, l):
        pe, prev_end = prev_end, b
        pre = t[max(0, a - 90):a]
        if MENTION.search(pre) or ALIAS_OF.search(pre):
            continue
        verbs = [m for m in TITLE_VERB.finditer(t[:a])]
        if not verbs:
            continue
        v = verbs[-1].group(1).lower()
        if v.startswith(WEAK) and a - verbs[-1].end() > 80:
            continue
        kind = 'a'
        if v.startswith(('repeal', 'supersed')):
            # 'Repealing Section 5 of ...', 'Repealing the Crime of ... under Article 351 of ...' repeal a piece
            kind = 'rp' if (PIECE_W.search(t[max(verbs[-1].end(), pe):a]) or TITLE_TAIL.search(t[b:])) else 'r'
        add(l['id'], lid, kind, l['t'], 'title')
    # 2. the body, sentence by sentence
    body = l['body']
    for par in re.split(r'\n\s*\n', body):
        if 'amended' not in par and 'repealed' not in par:
            continue
        flat = norm(re.sub(r'\s+', ' ', re.sub(r'[_*]+|\\(?=[\-–—])', '', par)))   # markdown emphasis off
        for sent0 in sentences(flat):
            sent = mask(sent0)
            am, rp = AMEND_S.search(sent), REPEAL_S.search(sent)
            if not (am or rp):
                continue
            prev_end = 0
            for lid, a, b in refs(sent, l):
                pe, prev_end = prev_end, b
                pre = sent[max(0, a - 90):a]
                if MENTION.search(pre) or ALIAS_OF.search(pre):
                    continue
                # the verb that governs a reference is the nearest one after it
                va = next((m for m in AMEND_S.finditer(sent) if m.start() > a - 40), None)
                vr = next((m for m in REPEAL_S.finditer(sent) if m.start() > a), None)
                if vr and (not va or vr.start() < va.start()):
                    if NEG.search(sent):
                        continue
                    add(l['id'], lid, 'rp' if partial_repeal(sent, a, b, pe, vr) else 'r', sent0, 'text')
                elif va:
                    add(l['id'], lid, 'a', sent0, 'text')
    # 3. LawPhil's own notes on this page ("Amended by RA 8533")
    for line in body.split('\n')[:40]:
        m = NOTE.match(line.strip())
        if m:
            for lid, a, b in refs(norm(m.group(2)), l):
                kind = {'amended': 'a', 'modified': 'a', 'repealed': 'r', 'superseded': 'r'}[m.group(1).lower()]
                add(lid, l['id'], kind, line.strip(), 'note')

# a whole repeal and a partial one by the same law: keep the partial (the safer reading)
for (src, dst, kind) in list(edges):
    if kind == 'r' and (src, dst, 'rp') in edges:
        del edges[(src, dst, 'r')]

# keep only edges where the source is not older than the target (a law cannot amend a later law)
def dkey(l): return l['d'] or (l['y'] + '-00-00' if l['y'] else '')
clean = {}
for (src, dst, kind), ev in edges.items():
    a, b = laws[src], laws[dst]
    if dkey(a) and dkey(b) and dkey(a) < dkey(b):
        continue
    clean[(src, dst, kind)] = ev
edges = clean
json.dump([[k[0], k[1], k[2], v[1], v[0]] for k, v in edges.items()], open('/tmp/edges_all.json', 'w'))
print('edges', len(edges), {k: sum(1 for e in edges if e[2] == k) for k in ('a', 'r', 'rp')})

inc, outg = {}, {}
for (src, dst, kind), (ev, how) in edges.items():
    inc.setdefault(dst, []).append([src, kind, how, ev])
    outg.setdefault(src, []).append([dst, kind, how, ev])

# ------------------------------------------------------------------ the study library
cat = json.load(open('/home/claude/site/data/catalog.json'))
study = {}
SER_OF = [('Republic Act', 'ra'), ('Commonwealth Act', 'ca'), ('Batas Pambansa', 'bp'), ('Presidential Decree', 'pd'), ('Executive Order', 'eo'), ('Act No', 'act')]
for c in cat['codes']:
    cit = c.get('citation', '')
    if c['id'] == 'const1987':
        study['const-1987'] = c['id']; continue
    for name, s in SER_OF:
        m = re.search(re.escape(name) + r'[^0-9]{0,12}?(\d{1,5}(?:-[A-Z])?)', cit)
        if m:
            n = m.group(1).lower()
            if s == 'eo':
                y = re.search(r'(19|20)\d\d', cit)
                lid = f'eo-{n}-{y.group(0)}' if y else None
            else:
                lid = f'{s}-{n}'
            if lid and lid in laws and lid not in study:
                study[lid] = c['id']
            break
print('study library linked', len(study))

# ------------------------------------------------------------------ write
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
def numkey(l):
    m = re.match(r'(\d+)', l['n'] or '0'); return (int(m.group(1)) if m else 0, l['n'], l['id'])
import base64
def write_z(path, obj):
    # gzip, then base64 so the file is plain text the host will serve (.txt); the browser reverses both steps
    raw = gzip.compress(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)
    open(path, 'w').write(base64.b64encode(raw).decode('ascii'))
def read_z(path):
    return json.loads(gzip.decompress(base64.b64decode(open(path).read())))
rows, chunk, size, ci = [], {}, 0, 0
def flush():
    global chunk, size, ci
    if chunk:
        write_z(f'{OUT}/c{ci:03d}.txt', chunk)
        ci += 1; chunk = {}; size = 0
for s in ORDER:
    for l in sorted((x for x in laws.values() if x['s'] == s), key=(lambda x: (x['y'], numkey(x))) if s == 'eo' else numkey):
        body = l['body']
        chunk[l['id']] = {'b': body, 'in': inc.get(l['id'], []), 'out': outg.get(l['id'], []), 'src': l['src'], 'note': l['note']}
        rep = any(k == 'r' for _, k, _, _ in inc.get(l['id'], []))
        rows.append([l['id'], s, l['n'], l['y'], l['d'], l['t'][:300], ci, len(inc.get(l['id'], [])), 1 if rep else 0, len(outg.get(l['id'], []))])
        size += len(body)
        if size > 2_500_000:
            flush()
flush()
write_z(f'{OUT}/idx.txt', {'rows': rows, 'study': study, 'built': 'LawCodex ' + os.popen(f'git -C {ROOT} log -1 --format=%cs').read().strip(),
               'counts': {s: sum(1 for r in rows if r[1] == s) for s in ORDER}})
tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print(f'chunks {ci} · index rows {len(rows)} · {tot / 1e6:.1f} MB gzip')
# catalog hash for cache busting
import hashlib
cat['lhash'] = hashlib.md5(open(f'{OUT}/idx.txt', 'rb').read()).hexdigest()[:10]
cat['laws'] = {s: sum(1 for r in rows if r[1] == s) for s in ORDER}
cat['lawmap'] = {v: k for k, v in study.items()}
# gaps in each numbered series, so the coverage page can say exactly what is missing
gaps = {}
for s in ('act', 'ca', 'ra', 'pd', 'bp'):
    nums = sorted({int(re.match(r'\d+', r[2]).group(0)) for r in rows if r[1] == s and re.match(r'\d+', r[2] or '')})
    if nums:
        have = set(nums); lo, hi = nums[0], nums[-1]
        miss = [n for n in range(1, hi + 1) if n not in have]
        gaps[s] = {'lo': lo, 'hi': hi, 'missing': len(miss), 'first_missing': miss[:12]}
cat['lawgaps'] = gaps
json.dump(cat, open('/home/claude/site/data/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
