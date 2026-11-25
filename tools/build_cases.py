"""Case indexes: every case a textbook cites, filed under the provision the book is discussing,
with the book's page. Only case names, citations and page numbers are kept — not the authors' text."""
import re, json, glob, collections, os

SITE = '/home/claude/site/data'
OUT = SITE + '/cases'
os.makedirs(OUT, exist_ok=True)

MONTHS = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
CITE = (r'(?:G\.\s?R\.\s?Nos?\.\s?(?:[A-Z]{1,2}\s?-?\s?)?\d[\d\-–]*(?:\s*(?:,|&|and)\s*(?:[A-Z]-?)?\d[\d\-–]*)*(?:,?\s*' + MONTHS + r'\s*\d{1,2},?\s*\d{4})?'
        r'|A\.\s?M\.\s?No\.\s?[\w\-–.]+(?:,\s*' + MONTHS + r'\s*\d{1,2},?\s*\d{4})?'
        r'|\d{1,4}\s+(?:SCRA|Phil\.?|O\.\s?G\.|Off\.\s?Gaz\.|U\.S\.|SCAD)\s+\d{1,5}(?:\s*[\[(]\d{4}[\])])?)')
NAME = r"((?:[A-Z][\w.,&'’\-]*\s?(?:(?:de|del|dela|de la|of|the|and|y|v\.|vs\.|San|Sta\.|Sto\.|et|al\.|Inc\.|Co\.|Corp\.|[A-Z][\w.,&'’\-]*)\s?){0,9}?)\s(?:vs?\.|versus)\s(?:[A-Z][\w.,&'’\-()]*\s?(?:(?:de|del|dela|of|the|and|y|for|on|in|Inc\.|Co\.|Corp\.|et|al\.|[A-Z][\w.,&'’\-()]*)\s?){0,10}?))"
RX = re.compile(NAME + r',?\s*(' + CITE + r')')
RX_INRE = re.compile(r'(In\s+(?:re|the\s+Matter\s+of)[:\s][^,;()]{3,90}?),\s*(' + CITE + ')')
NOISE_START = re.compile(r'^(?:See|see|Also|also|cf\.|Cf\.|In|Thus|Hence|But|And|The|In the case of|As held in|citing|Citing|quoting|In People|Id\.|Ibid\.)\s+')


def clean_name(n):
    n = re.sub(r'\s+', ' ', n).strip(' ,;:(')
    for _ in range(3):
        n = NOISE_START.sub('', n)
    n = re.sub(r'^(?:the case of|case of)\s+', '', n, flags=re.I)
    n = n.replace(' vs ', ' vs. ').replace(' v ', ' v. ')
    return n.strip()


CITE_RX = re.compile(CITE)
CONNECT = re.compile(r"^(?:vs?\.|versus|v|de|del|dela|de la|la|las|los|of|the|and|y|for|on|in|et|al\.|&|Inc\.?|Co\.?|Corp\.?|Jr\.?|Sr\.?|Sps\.|Spouses|Heirs|Estate|People|Republic|City|Municipality|Province|Mun\.|Bros\.|Cía|Cia\.?|Ltd\.?|No\.|Phil\.|Phils\.|Intermediate|Appellate)$")
VS = re.compile(r'\s(?:vs?\.|versus)\s')


def extract(text):
    """Find citation anchors, then read the case name backwards from each anchor."""
    t = re.sub(r'-\n\s*', '', text)
    t = re.sub(r'\s+', ' ', t)
    out = []
    for m in CITE_RX.finditer(t):
        start = m.start()
        window = t[max(0, start - 200):start].rstrip(' ,;:(')
        toks = window.split(' ')
        keep = []
        for tok in reversed(toks):
            core = tok.strip('“”"‘’()[],;:*')
            if not core:
                if keep: break
                continue
            if CONNECT.match(core) or re.match(r"^[A-Z][\w.&'’\-]*,?$", core) or re.match(r'^[A-Z]\.?[A-Z]?\.?,?$', core):
                keep.append(tok)
                continue
            # a glued footnote number or OCR mark before a capitalised word: keep the word part
            mm = re.match(r"^[\d‘’'*?!;:~”“]+([A-Z][\w.&'’\-]*,?)$", core)
            if mm:
                keep.append(mm.group(1))
            break
        name = ' '.join(reversed(keep)).strip(' ,;:(“”"')
        name = re.sub(r'^(?:[A-Z]{1,2}(?=[A-Z][a-z]))', '', name)   # OCR'd footnote mark: "IMactan" -> "Mactan"
        name = clean_name(name)
        # drop leading words until the name starts at a capitalised word
        if not (VS.search(' ' + name + ' ') or re.match(r'In (?:re|the Matter)', name)):
            continue
        # trim leading generic words that precede the first party
        name = re.sub(r'^(?:Section|Article|Art\.|Sec\.|Constitution|Court|Supreme|Justice|Chief|Judge|Bill|Rights|Case|Cases|The|In|See|Also|Thus|But|Ruling|Held|Facts|Issue)\s+(?=[A-Z])', '', name)
        if len(name) < 6 or len(name) > 150 or len(name.split()) > 20 or not re.match(r'^[A-Z]', name):
            continue
        cite = re.sub(r'\s+', ' ', m.group(0)).strip(' ,.')
        out.append((start, name, cite))
    return out


def norm_key(name):
    k = name.lower()
    k = re.sub(r'\b(vs?\.|versus)\b', 'v', k)
    k = re.sub(r'[^a-z0-9 ]', '', k)
    k = re.sub(r'\b(court of appeals|ca)\b', 'ca', k)
    return re.sub(r'\s+', ' ', k).strip()


def tidy(name):
    segs = [x.strip() for x in re.split(r'[;“‘*”]', name) if x.strip()]
    vs = [x for x in segs if re.search(r'\s(?:vs?\.|versus)\s', ' ' + x + ' ') or x.startswith('In re')]
    name = vs[-1] if vs else name
    name = re.sub(r'^(?:This|That|These|Rules on Criminal Procedure|Constitution\.|Filipino\.|Ibid\.?|Id\.|Ed\.\]?|Manresa|Cooley|Labor Code)\s+', '', name)
    return name.strip(" ,.:'’")


def add(index, pid, name, cite, book, page):
    name = tidy(name)
    if len(name) < 6:
        return
    lst = index.setdefault(pid, [])
    k = norm_key(name)
    for c in lst:
        if c['b'] == book and norm_key(c['n']) == k:
            return
    lst.append({'n': name, 'c': cite, 'b': book, 'pg': page})


def code_lookup(cid):
    d = json.load(open(f'{SITE}/codes/{cid}.json'))
    return d, {p.get('n'): p['i'] for p in d['provisions']}, {p['l']: p['i'] for p in d['provisions']}


def book_page(text, fallback):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    cand = lines[:3] + lines[-3:]
    for l in cand:
        m = re.match(r'^(\d{1,4})\b', l) or re.search(r'\b(\d{1,4})$', l)
        if m and 0 < int(m.group(1)) < 1300 and len(l) < 70:
            return m.group(1)
    return fallback


# ------------------------------------------------------------------ De Leon (Civil Code 1156–1430s)
def deleon():
    dl = json.load(open('/home/claude/work/deleon/deleon_index.json'))
    d, bynum, _ = code_lookup('civil')
    idx = {}
    book = 'De Leon, Obligations and Contracts'
    pages = open('/home/claude/work/deleon/deleon.txt').read().split('\f')
    cur = '1156'
    for pi, pg in enumerate(pages):
        flat = pg
        arts = [(m.start(), m.group(1)) for m in re.finditer(r'\bART\.\s*(\d{3,4})\.', flat)]
        for pos, name, cite in extract(flat):
            # article in force at this position: last ART heading before it on the page, else carried over
            before = [a for p, a in arts if p <= pos]
            art = before[-1] if before else cur
            # map character position from flattened text approx: extract() flattens whitespace; use ratio
            pid = bynum.get(art)
            if pid:
                add(idx, pid, name, cite, book, str(pi + 1))
        if arts:
            cur = arts[-1][1]
    return idx


# ------------------------------------------------------------------ Duka (Bill of Rights)
DUKA_MAP = {4: ['1'], 5: ['2'], 6: ['3'], 7: ['4'], 8: ['5'], 9: ['6'], 10: ['7'], 11: ['8'], 12: ['10'], 13: ['11'], 14: ['12'],
            15: ['13'], 16: ['14'], 17: ['15'], 18: ['16'], 19: ['17'], 20: ['18'], 21: ['19'], 22: ['20'], 23: ['21'], 24: ['22']}


def duka():
    d, bynum, bylabel = code_lookup('const1987')
    idx = {}
    book = 'Duka, Constitutional Law 2 (2025)'
    halves = []
    for f in sorted(glob.glob('/home/claude/work/ocr/duka/p*.txt')):
        pn = int(re.search(r'p(\d+)\.txt', f).group(1))
        for h, t in enumerate(open(f).read().split('\n\f\n')):
            halves.append((pn, h, t))
    cur = None
    sub = None  # within chapter 3: taxation / police power / eminent domain
    for pn, h, t in halves:
        head = '\n'.join(t.split('\n')[:4])
        m = re.search(r'\bCHAPTER\s*(\d{1,2})\b', head, re.I)
        if m and 1 <= int(m.group(1)) <= 25:
            cur = int(m.group(1))
        if cur == 3:
            for l in t.split('\n'):
                L = l.strip().upper()
                if re.match(r'^(THE )?POWER OF EMINENT DOMAIN|^EMINENT DOMAIN\b', L): sub = 'ed'
                elif re.match(r'^(THE )?POWER OF TAXATION|^TAXATION\b', L): sub = 'tax'
                elif re.match(r'^(THE )?POLICE POWER\b', L): sub = 'pp'
        if cur in DUKA_MAP:
            targets = [bylabel.get(f'Art. III, Sec. {s}') for s in DUKA_MAP[cur]]
        elif cur == 3:
            targets = [bylabel.get('Art. III, Sec. 9')] if sub == 'ed' else [bylabel.get('Art. VI, Sec. 28')] if sub == 'tax' else [bylabel.get('Art. III, Sec. 1')]
        elif cur == 25:
            targets = [bylabel.get('Art. IV, Sec. 1')]
        elif cur == 2:
            targets = [bylabel.get('Art. III, Sec. 1')]
        else:
            targets = []
        targets = [x for x in targets if x]
        if not targets:
            continue
        pg = book_page(t, f'scan {pn}')
        for _, name, cite in extract(t):
            for pid in targets:
                add(idx, pid, name, cite, book, pg)
    return idx


# ------------------------------------------------------------------ Sta. Maria (Persons; Family Code)
def stamaria():
    files = sorted(glob.glob('/home/claude/work/ocr/stamaria/p*.txt'))
    if not files:
        return {}, {}
    civ, civnum, _ = code_lookup('civil')
    fam, famnum, _ = code_lookup('family')
    book = 'Sta. Maria, Persons and Family Relations Law (2025)'
    icv, ifm = {}, {}
    code = 'civil'
    last = 0
    for f in files:
        pn = int(re.search(r'p(\d+)\.txt', f).group(1))
        for h, t in enumerate(open(f).read().split('\n\f\n')):
            head = ' '.join(t.split('\n')[:3])
            m = re.search(r'\bArts?\.\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?', head)
            if m:
                a = int(m.group(1))
                if re.search(r'FAMILY CODE', ' '.join(t.split('\n')[:2]).upper()) or (last > 40 and a < last - 30 and code == 'civil'):
                    code = 'family'
                last = a
            if not last:
                continue
            art = str(last)
            pg = book_page(t, f'scan {pn}')
            for _, name, cite in extract(t):
                if code == 'civil' and art in civnum:
                    add(icv, civnum[art], name, cite, book, pg)
                elif code == 'family' and art in famnum:
                    add(ifm, famnum[art], name, cite, book, pg)
    return icv, ifm


# ------------------------------------------------------------------ Azucena (Labor Code, old numbering)
def azucena():
    files = sorted(glob.glob('/home/claude/work/ocr/azucena/p*.txt'))
    if not files:
        return {}
    lab, labnum, _ = code_lookup('labor')
    old2new = {}
    for p in lab['provisions']:
        if p.get('o'):
            for o in re.split(r'[,\s]+', p['o']):
                if o.strip(): old2new.setdefault(o.strip(), p['i'])
        elif p.get('n') and int(re.match(r'\d+', p['n']).group()) < 130:
            old2new.setdefault(p['n'], p['i'])   # Arts. 1–129 kept their numbers
    book = 'Azucena, Everyone’s Labor Code'
    idx = {}
    last = None
    for f in files:
        pn = int(re.search(r'p(\d+)\.txt', f).group(1))
        for h, t in enumerate(open(f).read().split('\n\f\n')):
            for m in re.finditer(r'(?m)^\s*ART(?:ICLE)?\.?\s*(\d{1,3}(?:-[A-Z])?)\s*(\[\s*\d{1,3}(?:-[A-Z])?\s*\])?\s*\.\s+[A-Z]', t):
                last = ('new', m.group(1)) if m.group(2) else ('old', m.group(1))
            if not last:
                continue
            pid = labnum.get(last[1]) if last[0] == 'new' else old2new.get(last[1])
            if not pid:
                continue
            pg = book_page(t, f'scan {pn}')
            head = ' '.join(t.split('\n')[:2])
            hm = re.search(r'\bArts?\.\s*(\d{1,3})', head)
            hpid = labnum.get(hm.group(1)) if hm else None
            for _, name, cite in extract(t):
                add(idx, pid, name, cite, book, pg)
            # Azucena's short citations: "(See Maranaw Hotel, November 6, 1992; Ferrer, July 5, 1993.)"
            flat = re.sub(r'\s+', ' ', re.sub(r'-\n\s*', '', t))
            for grp in re.findall(r'\(([^()]{8,400})\)', flat):
                for part in re.split(r';', grp):
                    mm = re.match(r'^\s*(?:See|see|Also|also|Cf\.|cf\.|citing)?\s*([A-Z][\w.&\'’\- ]{2,70}?),\s*(' + MONTHS + r'\s*\d{1,2},\s*\d{4})\.?\s*$', part)
                    if mm and not re.search(r'\b(Art|Sec|Section|Article|Rule|Book|Title|Department|Order|Circular|R\.A|P\.D|E\.O)\b', mm.group(1)):
                        add(idx, hpid or pid, mm.group(1).strip(), mm.group(2), book, pg)
    return idx


def merge(*idxs):
    out = {}
    for ix in idxs:
        for k, v in ix.items():
            out.setdefault(k, []).extend(v)
    return out


if __name__ == '__main__':
    civ_dl = deleon()
    cons = duka()
    civ_sm, fam_sm = stamaria()
    lab = azucena()
    res = {'civil': merge(civ_dl, civ_sm), 'const1987': cons, 'family': fam_sm, 'labor': lab}
    for cid, ix in res.items():
        if not ix:
            continue
        json.dump(ix, open(f'{OUT}/{cid}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
        n = sum(len(v) for v in ix.values())
        print(cid, 'provisions with cases:', len(ix), 'citations:', n)
    json.dump({k: bool(v) for k, v in res.items()}, open('/home/claude/work/cases_status.json', 'w'))
