"""Administrative Code of 1987 (EO 292) from OCR of the user's scanned copy.

Clean-up is conservative: OCR noise lines are dropped, words broken across lines are rejoined
only when the joined form is a known word, and a non-word is replaced only when exactly one
known word lies one edit away and that word is common in the statute corpus. Every section that
still contains an unknown word is marked for checking against the scan."""
import glob, re, json, collections, os

OCR = '/home/claude/work/ocr/admin'
pages = []
for f in sorted(glob.glob(OCR + '/p*.txt')):
    pn = int(re.search(r'p(\d+)\.txt', f).group(1))
    for half, txt in enumerate(open(f).read().split('\n\f\n')):
        pages.append((pn, half, txt))

# ---- vocabulary: hunspell list + statute corpus from the other codes
vocab = collections.Counter()
for f in [x for x in glob.glob('/home/claude/site/data/codes/*.json') if not x.endswith('admincode.json')]:
    d = json.load(open(f))
    for p in d['provisions']:
        for x in p['p']:
            if isinstance(x, str):
                for w in re.findall(r"[A-Za-z]+", x):
                    vocab[w.lower()] += 1
dic = set()
for line in open('/usr/share/hunspell/en_US.dic', encoding='latin-1').read().split('\n')[1:]:
    w = line.split('/')[0].strip()
    if w:
        dic.add(w.lower())
        flags = line.split('/')[1] if '/' in line else ''
        lw = w.lower()
        if 'S' in flags: dic.add(lw + 's'); dic.add(lw + 'es')
        if 'D' in flags: dic.add(lw + 'ed'); dic.add(lw + 'd')
        if 'G' in flags: dic.add(lw + 'ing'); dic.add(lw[:-1] + 'ing' if lw.endswith('e') else lw + 'ing')
        if 'Y' in flags: dic.add(lw + 'ly')
        if 'M' in flags: dic.add(lw + "'s")
def _base(w):
    return w.lower() in dic or vocab[w.lower()] >= 2
def known(w):
    lw = w.lower()
    if len(w) <= 2 or _base(lw): return True
    for suf, rep in (('ies', 'y'), ('ied', 'y'), ('ier', 'y'), ('iest', 'y'), ('ily', 'y'), ('s', ''), ('es', ''), ('ed', ''), ('ed', 'e'), ('ing', ''), ('ing', 'e'), ('er', ''), ('er', 'e'), ('ers', ''), ('ers', 'e'), ('ly', ''), ('ment', ''), ('ments', ''), ('ness', ''), ('al', ''), ('ally', ''), ('ship', ''), ('ize', ''), ('ized', ''), ('ization', 'ize'), ('ity', ''), ('ive', 'e'), ('ions', ''), ('ion', 'e'), ('ions', 'e')):
        if lw.endswith(suf) and len(lw) - len(suf) >= 3 and _base(lw[: len(lw) - len(suf)] + rep):
            return True
    if lw.startswith(('un', 're', 'non', 'in', 'sub', 'inter', 'pre', 'co', 'dis', 'mis')):
        for pre in ('un', 're', 'non', 'in', 'sub', 'inter', 'pre', 'co', 'dis', 'mis'):
            if lw.startswith(pre) and len(lw) > len(pre) + 3 and known(lw[len(pre):]): return True
    return vocab[lw] >= 1

def edits1(w):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    s = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    return set([a + b[1:] for a, b in s if b] + [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1] +
               [a + c + b[1:] for a, b in s if b for c in letters] + [a + c + b for a, b in s for c in letters])

fixes = collections.Counter()
HEADMODE = [False]
unknown_left = collections.Counter()
def fix_word(m):
    w = m.group(0)
    if known(w) or w.isupper() and len(w) <= 4:
        return w
    lw = w.lower()
    if lw.endswith(('s', 'ed', 'ing', 'ers', 'er', 'ly', 'ies', 'ied')) and len(lw) > 6:
        unknown_left[w] += 1
        return w
    cands = [c for c in edits1(lw) if vocab[c] >= 5]
    if len(cands) == 1 or (cands and sorted(cands, key=lambda c: -vocab[c])[0] and len(cands) > 1 and vocab[sorted(cands, key=lambda c: -vocab[c])[0]] > 20 * vocab[sorted(cands, key=lambda c: -vocab[c])[1]]):
        c = sorted(cands, key=lambda c: -vocab[c])[0]
        out = c.capitalize() if w[0].isupper() else c
        if w.isupper(): out = c.upper()
        fixes[(w, out)] += 1
        return out
    unknown_left[w] += 1
    return w

HEADS = [
    (re.compile(r'^(?:B[oO0][oO0][kKsS]|BOOK)\s+([IVXL]+)\s*[—–-]+\s*(.*)$'), 0, 'BOOK'),
    (re.compile(r'^(?:T[iI1l]t[lI1]e|TITLE|T[iI]TLE|Timez?|Trrue|Trrne|Tittz|Tite)\s+([IVXL]+(?:-[A-Z])?)\s*[—–-]+\s*(.*)$'), 1, 'Title'),
    (re.compile(r'^(?:Subtitle|SUBTITLE|Sustitie|Susrirte)\s+([A-Z])\s*[—–-]+\s*(.*)$'), 2, 'Subtitle'),
    (re.compile(r'^(?:C[hn]?[auo]p?[pt]?[eEr]?[rRn]?|CHAPTER|Cuaprer|Cuarren|CHarren|CHarteR|Cnarrer|Craprern|Cuaprre|CuaprerR|CHaPren|Carter|Cuarrer|Cuapter|Cuaprer|Cuaptsr|Cuarter|Cuarpter|Chapter)\s+(\d+)\s*[—–-]+\s*(.*)$'), 3, 'Chapter'),
]
INTRO = re.compile(r'^INTRODUCTORY PROVISIONS')
SEC = re.compile(r'^(?:S[Ee][Cc][Tt][Ii][Oo][Nn]|Sec|Src|Szc|Sxc|SEc|Smc|Snc|Seo|Sre|Bec|Sco|S8c|Ssc|8ec|Sue|Suc|SEC|Sc(?=,))[.,]?\s*(\d{1,3})(?:[.,]\s*|\s+(?=[A-Z][a-z]+ [A-Za-z]))(.*)$')
NOISE = re.compile(r'^[\W\d_]{0,4}$|^[a-zA-Z]{1,2}$')

import difflib
KW = [('BOOK', 0), ('TITLE', 1), ('SUBTITLE', 2), ('CHAPTER', 3)]
ROMAN = re.compile(r'^[IVXLl1|\[\]{}!]+$')
def roman_fix(t):
    t = t.replace('l', 'I').replace('1', 'I').replace('|', 'I').replace('[', 'I').replace(']', 'I').replace('{', 'I').replace('}', 'I').replace('!', 'I')
    return t
TITLE_NAMES = {'POWERS OF THE PRESIDENT': 'I', 'ORGANIZATION': 'II', 'FUNCTIONS': 'III', 'FOREIGN AFFAIRS': 'I', 'FINANCE': 'II', 'JUSTICE': 'III',
    'AGRICULTURE': 'IV', 'PUBLIC WORKS AND HIGHWAYS': 'V', 'EDUCATION, CULTURE AND SPORTS': 'VI', 'LABOR AND EMPLOYMENT': 'VII', 'NATIONAL DEFENSE': 'VIII',
    'HEALTH': 'IX', 'TRADE AND INDUSTRY': 'X', 'AGRARIAN REFORM': 'XI', 'LOCAL GOVERNMENT': 'XII', 'TOURISM': 'XIII', 'ENVIRONMENT AND NATURAL RESOURCES': 'XIV',
    'TRANSPORTATION AND COMMUNICATIONS': 'XV', 'SOCIAL WELFARE AND DEVELOPMENT': 'XVI', 'BUDGET AND MANAGEMENT': 'XVII', 'SCIENCE AND TECHNOLOGY': 'XVIII',
    'CONSTITUTIONAL COMMISSIONS': 'I', 'OTHER BODIES': 'II'}
def fuzzy_head(l):
    if re.match(r'^BOOK\s+\S{1,4}$', l): return (0, 'BOOK', 'X', '')
    m = re.match(r'^([A-Za-z]{3,9})[.,]?\s+([IVXLlI1|\[\]{}!TJN]{1,6}|\d{1,2}|[A-H])(?:\s*[—–~\-]+\s*(.*)|\s*)$', l)
    if not m: return None
    # Title numerals the OCR garbled ("TitLe ITJ—JUSTICE", "Tirte ITX—HEALTH"): the title's name fixes its number
    nm = re.sub(r'[^A-Z ,]', '', (m.group(3) or '').upper()).strip(' ,')
    if nm in TITLE_NAMES and difflib.SequenceMatcher(None, m.group(1).upper(), 'TITLE').ratio() >= 0.55:
        return (1, 'Title', TITLE_NAMES[nm], m.group(3).strip())
    word = m.group(1).upper()
    best = max(KW, key=lambda k: difflib.SequenceMatcher(None, word, k[0]).ratio())
    r = difflib.SequenceMatcher(None, word, best[0]).ratio()
    if r < 0.55: return None
    if word in ('SUBJECT', 'SECTION', 'BOOKS', 'TITLES', 'CHAPTERS'): return None
    num = m.group(2)
    if best[0] == 'CHAPTER':
        num = num if num.isdigit() else {'I': '1', 'l': '1', 'I1': '2', 'II': '2', 'Il': '2', '1I': '2', 'III': '3'}.get(num)
        if num is None: return None
    elif best[0] == 'SUBTITLE':
        num = num if re.match(r'^[A-H]$', num) else roman_fix(num)
    else:
        if not ROMAN.match(num): return None
        num = roman_fix(num)
    rest = (m.group(3) or '').strip()
    if best[0] in ('BOOK', 'TITLE') and not rest and len(l) > 14: return None
    kwname = {'BOOK': 'BOOK', 'TITLE': 'Title', 'SUBTITLE': 'Subtitle', 'CHAPTER': 'Chapter'}[best[0]]
    return (best[1], kwname, num, rest)

lines = []
start = False
for pn, half, txt in pages:
    for raw in txt.split('\n'):
        l = raw.strip().strip('|').strip()
        l = re.sub(r'^[;:’‘\'.,|]+\s*', '', l)
        l = re.sub(r'^[*)(\-–—•»«~_]+\s*(?=(?:S[Ee][Cc][Tt][Ii][Oo][Nn]|SEC|Sec|Src|Szc|Sxc|SEc|Smc|Snc|Seo|Sre|Bec|Sco|S8c|Ssc|8ec|Sue|Suc|Sc(?=,))[.,]?\s*\d)', '', l)
        if not start:
            if INTRO.match(l) and pn > 4:
                start = True
            else:
                continue
        if re.fullmatch(r'\d{1,3}', l) or NOISE.match(l):
            lines.append(''); continue
        lines.append(l)

# join hyphenated words across lines when the join is a word
out = []
for l in lines:
    if out and out[-1].endswith('-') and l and l[0].islower():
        head = re.search(r'([A-Za-z]+)-$', out[-1])
        tail = re.match(r'([A-Za-z]+)', l)
        if head and tail and known(head.group(1) + tail.group(1)):
            out[-1] = out[-1][:-1] + l; continue
        out[-1] = out[-1] + l; continue
    out.append(l)

divisions, provisions, stack, cur = [], [], [], None
DROPPED = []
pending = None
paras = []
def flush_para():
    global paras
for l in out:
    if not l:
        if cur and cur['paras'] and cur['paras'][-1] != '':
            cur['paras'].append('')
        continue
    l2 = re.sub(r'\s+', ' ', l)
    hm = fuzzy_head(l2)
    if INTRO.match(l2):
        hm = (0, 'INTRODUCTORY PROVISIONS', '', '')
    if hm and len(l2) < 130:
        lvl, kw, num, rest = hm
        title = (f'{kw} {num} — {rest}'.strip(' —') if num else kw)
        while stack and divisions[stack[-1]]['lvl'] >= lvl:
            stack.pop()
        divisions.append({'t': title, 'lvl': lvl, 'parent': stack[-1] if stack else None})
        stack.append(len(divisions) - 1); pending = len(divisions) - 1; cur = None
        continue
    letters = [c for c in l2 if c.isalpha()]
    if pending is not None and cur is None and letters and sum(c.isupper() for c in letters) / len(letters) > 0.6 and len(l2) < 80 and not SEC.match(l2):
        divisions[pending]['t'] += (' — ' if divisions[pending]['t'].count('—') == 0 and divisions[pending]['lvl'] <= 2 else ' ') + l2.upper(); continue
    # lettered sub-heads inside chapters (A—..., B—...)
    m = re.match(r'^([A-H])\s*[—–-]+\s*([A-Z][A-Za-z ,]+)$', l2)
    if m and len(l2) < 70:
        lvl = (divisions[stack[-1]]['lvl'] + 1) if stack else 4
        while stack and divisions[stack[-1]]['lvl'] >= lvl:
            stack.pop()
        divisions.append({'t': f'{m.group(1)} — {m.group(2)}', 'lvl': lvl, 'parent': stack[-1] if stack else None})
        stack.append(len(divisions) - 1); cur = None; continue
    sm = SEC.match(l2)
    if sm and sm.group(2) and sm.group(2)[0].islower():
        sm = None   # "Section 46, for appropriate action": a cross-reference at the start of a line, not a new section
    if not sm:
        # the shaded inner margin cut "Sec." down to "¢." or "ic." on a few pages (e.g. Book IV, Title XII, Secs. 15-16)
        tm = re.match(r'^(?:¢|c|ic|ec|Ec)[.,]\s*(\d{1,3})\.\s*([A-Z][a-z]+(?: [A-Za-z]+){0,6}\.\s*[—–-].*)$', l2)
        if tm: sm = tm
    if sm:
        pending = None
        cur = {'kind': 'section', 'n': sm.group(1), 'div': stack[-1] if stack else None, 'paras': [sm.group(2)]}
        provisions.append(cur)
        continue
    if cur is None:
        if pending is not None and len(l2) < 70 and not re.search(r'[.;:]$', l2):
            # second line of a heading set in italics ("Chapter 7—Regular Holidays and Nationwide / Special Days")
            divisions[pending]['t'] += ' ' + l2.rstrip(' :.’\'Nl').strip()
            continue
        DROPPED.append(l2)
        continue
    if re.match(r'^\(?\d{1,2}\)|^\([a-z]\)', l2) and cur['paras'] and cur['paras'][-1] != '':
        cur['paras'].append('')
    if cur['paras'] and cur['paras'][-1] != '':
        cur['paras'][-1] += ' ' + l2
    else:
        if cur['paras'] and cur['paras'][-1] == '':
            cur['paras'][-1] = l2
        else:
            cur['paras'].append(l2)

RUNON = re.compile(r'(?:^|\s)[^\w\s]{0,2}\d?,?\s*(?:S[eEgcm][ecCo][.,:°]?|Sc[.,]|Sgc[.,]|SEC[.,]?)\s*°?\s*(\d{1,3})\s*[.,:]\s*(?=[A-Z])')
def split_runons(provs):
    out = []
    for p0 in provs:
        q = [p0]
        while q:
            cur = q.pop(0); out.append(cur)
            if not str(cur['n']).isdigit(): continue
            nxt = str(int(cur['n']) + 1)
            done = False
            for j, para in enumerate(cur['paras']):
                for m in RUNON.finditer(para):
                    if m.group(1) != nxt or (j == 0 and m.start() < 3): continue
                    new = {'kind': 'section', 'n': nxt, 'div': cur['div'], 'paras': [para[m.end():]] + cur['paras'][j + 1:]}
                    cur['paras'] = cur['paras'][:j] + [para[:m.start()].rstrip(' _-~é;:,')]
                    q.insert(0, new); done = True; break
                if done: break
    return out
before = len(provisions)
provisions = split_runons(provisions)
print('runon splits', len(provisions) - before)
flagged = 0
for p in provisions:
    ps = []
    for x in p['paras']:
        x = x.strip()
        if not x: continue
        x = re.sub(r'\s+([,.;:])', r'\1', x)
        x = re.sub(r',(?=[a-z])', ', ', x)
        x = re.sub(r'\.—|\.\s*[-–]{1,2}\s*|\.\s—\s?', '.— ', x, count=1) if not ps else x
        before = sum(unknown_left.values())
        x = re.sub(r"[A-Za-z]{3,}", fix_word, x)
        ps.append(x)
    p['paras'] = ps
    txt = ' '.join(ps)
    unk = [w for w in re.findall(r"[A-Za-z]{3,}", txt) if not known(w) and not (w.isupper() and len(w) <= 4)]
    p['v'] = 'check' if unk else 'ok'
    if unk:
        p['unk'] = sorted(set(unk))[:12]; flagged += 1
    m = re.match(r'^([A-Z][^—]{1,160}?)\s*[.,]?\s*[-–]*—[-–—]*\s*(\S.*)$', ps[0]) if ps else None
    if m and '. ' in m.group(1): m = None
    if m:
        p['cap'] = m.group(1).strip(); p['paras'][0] = m.group(2)

BOOKT = {1: 'SOVEREIGNTY AND GENERAL ADMINISTRATION', 2: 'DISTRIBUTION OF POWERS OF GOVERNMENT', 3: 'OFFICE OF THE PRESIDENT', 4: 'THE EXECUTIVE BRANCH', 6: 'NATIONAL GOVERNMENT BUDGETING', 7: 'ADMINISTRATIVE PROCEDURE'}
ROM = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
bk = 0
HEADMODE[0] = True
for dv in divisions:
    if dv['lvl'] == 0 and dv['t'].startswith('BOOK'):
        bk += 1
        dv['t'] = f"BOOK {ROM[bk]}" + (f" — {BOOKT[bk]}" if bk in BOOKT else '')
        continue
    t = dv['t']
    head, _, rest = t.partition(' — ')
    rest = re.sub(r"[A-Za-z]{3,}", fix_word, rest.upper()) if rest else rest
    rest = rest.upper() if dv['lvl'] <= 2 else rest
    if dv['lvl'] > 2 and rest:
        rest = ' '.join(w.capitalize() if w.lower() not in ('of', 'and', 'the', 'in', 'on', 'for', 'to', 'or', 'with', 'among', 'under', 'by') else w.lower() for w in rest.lower().split())
        rest = rest[0].upper() + rest[1:]
    for a, b in (('CIVIT', 'CIVIL'), ('TUHE', 'THE'), ('TUE ', 'THE '), ('ORRICE', 'OFFICE'), (' ANP ', ' AND '), ('DEPARTMENT OR', 'DEPARTMENT OF'), ('OFFICE OR THE', 'OFFICE OF THE'), ('MNATIONAL', 'NATIONAL')):
        rest = rest.replace(a, b)
    dv['t'] = head + (' — ' + rest if rest else '')
HEADMODE[0] = False
print('books', bk)
print('dropped lines (no section open):', len(DROPPED))
json.dump(DROPPED, open('/home/claude/work/admin/dropped.json', 'w'), ensure_ascii=False, indent=0)
# label scopes: section numbers restart within titles of Books IV and V
json.dump({'meta': {}, 'title': 'Administrative Code of 1987', 'pre': [], 'divisions': divisions, 'provisions': provisions, 'closing': []},
          open('/home/claude/work/admin/admin.json', 'w'), ensure_ascii=False, indent=1)
print('divisions', len(divisions), 'sections', len(provisions), 'flagged', flagged, 'fixes', sum(fixes.values()))
print('top fixes', fixes.most_common(40))
print('unknown', unknown_left.most_common(60))
