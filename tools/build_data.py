"""Build the app's data files (catalogue + one JSON file per code) from the verbatim sources.

Only typographic normalisation is applied to source text (whitespace, the dash after a
caption, stray spaces before closing quotes). Word-level changes come only from
errata.json, and every one is recorded on the provision it touches.
"""
import json, re, os, sys, glob, hashlib, datetime
sys.path.insert(0, os.path.dirname(__file__))
import parse_md as P
from catalog_config import CODES, SUBJECTS, MISSING, LC

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site/data'
os.makedirs(OUT + '/codes', exist_ok=True)
ERRATA = json.load(open(os.path.join(os.path.dirname(__file__), 'errata.json')))
WORK = '/home/claude/work'

EMBED_HEAD = re.compile(r'^(SUBSECTION\s+\d+\.?.*|Subsection\s+\d+\.?.*|SECTION\s+\d+\.?\s*[-—–]?\s*[A-Z][^.]{0,80}|Section\s+\d+\.\s*[-—–]?\s*[A-Z][a-z][^.]{0,80}|Provisions Common to[^.]{0,80}|TRANSITIONAL PROVISIONS|GENERAL PROVISIONS|FINAL PROVISIONS)$')
CLOSING = re.compile(r'^(Approved|Done|Signed|Enacted|Lapsed into law|DONE)\b.{0,160}$')


def resolve(path):
    full = LC + path
    if os.path.exists(full):
        return full
    hits = sorted(glob.glob(full[:-3] + '*' if full.endswith('.md') else full + '*'))
    if not hits:
        raise FileNotFoundError(path)
    return hits[0]


def typo_norm(s):
    if not isinstance(s, str):
        return s
    s = s.replace(' ', ' ').replace(' ', ' ').replace(' ', ' ')
    s = re.sub(r'[ \t]+', ' ', s).strip()
    s = re.sub(r'([.,;:!?]) (["”’])(?=\s|$)', r'\1\2', s)   # "Code. " -> "Code."
    s = re.sub(r'\s+([,;:])(?=\s)', r'\1', s)                  # "word , word" -> "word, word"
    return s


def split_embedded_headings(divisions, provisions):
    """Headings that the source left inside the text of the preceding provision
    (e.g. 'SUBSECTION 2. Testamentary Capacity and Intent') become divisions."""
    extra = {}  # provision index -> list of heading strings to open after it
    closing = []
    for i, p in enumerate(provisions):
        paras = p['paras']
        while paras and isinstance(paras[-1], str) and (EMBED_HEAD.match(paras[-1]) or CLOSING.match(paras[-1])) and len(paras) > 1:
            h = paras.pop()
            if CLOSING.match(h) and i == len(provisions) - 1:
                closing.insert(0, h)
            elif not CLOSING.match(h):
                extra.setdefault(i, []).insert(0, h)
            else:
                paras.append(h); break
    if not extra:
        return closing
    cur_override, cur_base = None, None
    for i, p in enumerate(provisions):
        if p['div'] != cur_base:
            cur_base, cur_override = p['div'], None
        if cur_override is not None:
            p['div'] = cur_override
        if i in extra:
            for h in extra[i]:
                base = provisions[i]['div'] if cur_override is None else divisions[cur_override]['parent']
                lvl = (divisions[base]['lvl'] + 1) if base is not None else 0
                divisions.append({'t': h, 'lvl': lvl, 'parent': base})
                cur_override = len(divisions) - 1
    return closing


INLINE = re.compile(r'(?:(?<=[.;:)\]"”])\s+|^)(?:ARTICLE|Article|ART\.|Art\.|SECTION|Section|SEC\.|Sec\.)\s+(\d{1,4}(?:-[A-Z])?)\.?\s+(?=[A-Z“"(])')


def split_runons(provisions, log, cid):
    """The source sometimes runs the next article into the text of the previous one
    ("… (n) ARTICLE 437. The owner of a parcel …"). Split them back out, keeping the source's own words."""
    out = []
    for p in provisions:
        queue = [p]
        while queue:
            cur = queue.pop(0)
            out.append(cur)
            m_n = re.match(r'^(\d+)$', str(cur.get('n') or ''))
            if not m_n or cur['kind'] not in ('article', 'section'):
                continue
            nxt = str(int(m_n.group(1)) + 1)
            done = False
            for j, para in enumerate(cur['paras']):
                if not isinstance(para, str):
                    continue
                for m in INLINE.finditer(para):
                    if m.group(1) != nxt or (j == 0 and m.start() == 0):
                        continue
                    before, after = para[:m.start()].rstrip(), para[m.end():]
                    new = {'kind': cur['kind'], 'n': nxt, 'div': cur['div'], 'paras': [after] + cur['paras'][j + 1:],
                           'e': [{'t': f'The source ran {cur["kind"].title()} {nxt} into the end of {cur["kind"].title()} {cur["n"]}; it has been separated. The words are the source’s own.', 'b': 'Structural check (numbering gap)'}]}
                    cur['paras'] = cur['paras'][:j] + ([before] if before else [])
                    log.append({'code': cid, 'n': nxt, 'op': 'split', 'applied': True, 'note': f'Separated from {cur["kind"]} {cur["n"]}'})
                    queue.insert(0, new)
                    done = True
                    break
                if done:
                    break
    return out


def caption_split(p):
    if p.get('cap') is not None or not p['paras'] or not isinstance(p['paras'][0], str):
        return
    cap, rest = P.split_caption(p['paras'][0])
    if cap and rest:
        p['cap'] = cap.strip(' _')
        p['paras'][0] = rest


KIND_LABEL = {'article': 'Article', 'section': 'Section', 'rule': 'Rule'}


SPLITLOG = []


def load_md(src, cid=''):
    meta, title, pre, divisions, provisions = P.parse(resolve(src), 'x')
    provisions = split_runons(provisions, SPLITLOG, cid)
    closing = split_embedded_headings(divisions, provisions)
    for p in provisions:
        caption_split(p)
    return dict(meta=meta, title=title, pre=pre, divisions=divisions, provisions=provisions, closing=closing)


def load_labor():
    d = json.load(open(WORK + '/labor/labor.json'))
    return dict(meta={'source': 'DOLE (2022), The Labor Code of the Philippines, Renumbered', 'source_format': 'pdf-text'},
                title='Labor Code of the Philippines', pre=[], divisions=d['divisions'], provisions=d['provisions'], closing=[])


def load_json_src(name):
    d = json.load(open(WORK + f'/{name}/{name}.json'))
    return dict(meta=d.get('meta', {}), title=d.get('title'), pre=d.get('pre', []), divisions=d['divisions'],
                provisions=d['provisions'], closing=d.get('closing', []))


def load_ins10607():
    """RA 10607 Sec. 1 restates PD 612 in full; parse the quoted Code text into provisions."""
    path = resolve('codes/insurance-code-amended-2013.md')
    src = open(path, encoding='utf-8').read()
    meta, body = P.parse_front(src)
    start = body.index('### Section 1')
    body = body[start:]
    lines = body.split('\n')[1:]
    paras = P.blocks(lines)
    # stop at the RA's own Section 2 etc.
    divisions, provisions, cur = [], [], None
    stack = []
    HEADK = re.compile(r'^(TITLE|Title|CHAPTER|Chapter|SUBTITLE)\s+([0-9IVXLC]+(?:-[A-Z])?)\.?\s*(.*)$')
    LV = {'title': 1, 'subtitle': 2, 'chapter': 0}
    pending_head = None
    tail = []
    for para in paras:
        if not isinstance(para, str):
            if cur: cur['paras'].append(para)
            continue
        s = para.strip()
        if re.match(r'^Section\s+\d+\.\s', s) and not s.startswith('"') and provisions and re.search(r'(Separability|Repealing|Effectivity|Transitory|Implementing)', s[:80]):
            tail.append(s); cur = None; continue
        if tail:
            tail.append(s); continue
        s = s.lstrip('"“').rstrip()
        s = re.sub(r'"\s*$', '', s) if s.count('"') % 2 == 1 else s
        hm = HEADK.match(s)
        if hm and len(s) < 140 and not re.match(r'^(CHAPTER|Chapter|TITLE|Title)\s+\S+\s+(of|shall|is)\b', s):
            kind = hm.group(1).lower()
            lvl = LV.get(kind, 1)
            while stack and divisions[stack[-1]]['lvl'] >= lvl:
                stack.pop()
            divisions.append({'t': s, 'lvl': lvl, 'parent': stack[-1] if stack else None})
            stack.append(len(divisions) - 1); pending_head = len(divisions) - 1
            continue
        if pending_head is not None and s.isupper() and len(s) < 120 and not re.match(r'^SECTION', s):
            divisions[pending_head]['t'] += ' — ' + s
            continue
        pending_head = None
        m = re.match(r'^(?:SECTION|Section|SEC\.|Sec\.)\s+(\d+(?:-[A-Z])?)\.\s*(.*)$', s)
        if m:
            cur = {'kind': 'section', 'n': m.group(1), 'div': stack[-1] if stack else None, 'paras': [m.group(2)]}
            provisions.append(cur)
            continue
        if s.isupper() and len(s) < 120:
            divisions.append({'t': s, 'lvl': (divisions[stack[-1]]['lvl'] + 1) if stack else 0, 'parent': stack[-1] if stack else None})
            if stack and divisions[stack[-1]]['lvl'] + 1 > 2:
                pass
            stack.append(len(divisions) - 1)
            continue
        if cur:
            cur['paras'].append(s)
    for p in provisions:
        caption_split(p)
    meta = dict(meta)
    return dict(meta=meta, title='The Insurance Code (as amended by RA 10607)', pre=[], divisions=divisions,
                provisions=provisions, closing=tail)


# ---------------------------------------------------------------- amendments overlay
AMENDERS = {
    'rpc': [('ra10951', r'Act No\. 3815|Revised Penal Code|same Act'), ('ra10592', r'Act No\. 3815|Revised Penal Code|same Act'),
            ('ra7659', r'Revised Penal Code|Act No\. 3815|same Code|same Act'), ('ra8353', r'Act No\. 3815|Revised Penal Code'),
            ('ra11648', r'Act No\. 3815|Revised Penal Code|same Act')],
    'nirc': [('ra10963', r'National Internal Revenue Code|same Code'), ('ra11534', r'National Internal Revenue Code|same Code')],
    'ra8042': [('ra10022', r'Republic Act No\. 8042|same Act')],
    'ra9208': [('ra10364', r'Republic Act No\. 9208|same Act'), ('ra11862', r'Republic Act No\. 9208|same Act')],
    'ra9184': [],
}
AMEND_REF = re.compile(r'(?:Article|Articles|Section|Sections|Sec\.|Secs\.)\s+((?:\d+(?:-[A-Z])?(?:\s*(?:,|and|&)\s*)?)+)')
QUOTE_START = re.compile(r'^["“]?\s*(?:Art\.|ART\.|Article|ARTICLE|SEC\.|Sec\.|SECTION|Section)\s+(\d+(?:\s*-\s*[A-Z])?)\.?\s*(.*)$')


def amendment_overlays(target, amender_doc, pattern, by_label):
    """Return {number: [{'by', 'sec', 'paras'}]} parsed from the amending act's quoted text."""
    out = {}
    for sp in amender_doc['provisions']:
        paras = [x for x in sp['paras'] if isinstance(x, str)]
        if not paras:
            continue
        lead = paras[0]
        if not re.search(r'amended|inserted|added|read as follows', lead, re.I) or not re.search(pattern, lead):
            continue
        cur_n, buf = None, []
        def flush():
            if cur_n and buf:
                out.setdefault(cur_n, []).append({'by': by_label, 'sec': sp['n'], 'p': list(buf)})
        for para in paras[1:]:
            q = para.strip()
            m = QUOTE_START.match(q)
            if m and q[:1] in '"“':
                flush(); buf = []
                cur_n = re.sub(r'\s+', '', m.group(1))
            if cur_n:
                t = q.lstrip('"“').strip()
                t = re.sub(r'["”]\s*$', '', t) if t.count('"') % 2 == 1 or t.endswith('”') else t
                buf.append(t)
        flush()
    return out


# ---------------------------------------------------------------- anomaly scan (proofreading aids)
DOUBLE = re.compile(r'\b(\w{2,})\s+\1\b', re.I)
LEGIT_DOUBLE = {'that', 'had', 'is', 'in'}


def anomalies(text):
    out = []
    for m in DOUBLE.finditer(text):
        if m.group(1).lower() not in LEGIT_DOUBLE and not m.group(1).isdigit():
            out.append('repeated word “%s”' % m.group(0))
    if text.count('(') != text.count(')') and not re.search(r'^\(?[a-z0-9]+\)', text):
        out.append('unbalanced parentheses')
    if re.search(r'[a-z]\.[A-Z][a-z]', text) and not re.search(r'(R\.A|P\.D|B\.P|E\.O|C\.A|U\.S|No\.)', text):
        out.append('missing space after period')
    if re.search(r'\b(\w+)- (\w+)\b', text) and not re.search(r'\b(pre|non|sub|co|self|anti|quasi|semi|ex|re|multi|inter)- ', text):
        out.append('possible broken hyphenation')
    return out


# ---------------------------------------------------------------- per-code assembly
def roman_short(t):
    m = re.match(r'^((?:ARTICLE|Article|BOOK|Book|TITLE|Title|SUBTITLE|Subtitle|PART|Part|CHAPTER|Chapter)\s+(?:[0-9IVXLC]+|[A-H])(?:-[A-Z])?)\b', t)
    if not m: return None
    w, n = m.group(1).split(None, 1)
    return {'article': 'Art.', 'book': 'Book', 'title': 'Title', 'subtitle': 'Subtitle', 'part': 'Part', 'chapter': 'Ch.'}[w.lower()] + ' ' + n.upper()


def assemble(cid, doc, code_cfg):
    divisions, provisions = doc['divisions'], doc['provisions']
    for d in divisions:
        d['t'] = typo_norm(d['t'])
    nums = {}
    for p in provisions:
        nums[p.get('n')] = nums.get(p.get('n'), 0) + 1
    dup = {k for k, v in nums.items() if v > 1}
    # top-level ancestor for labels
    def top(di):
        while di is not None and divisions[di]['parent'] is not None:
            di = divisions[di]['parent']
        return di
    def chain(di):
        c = []
        while di is not None:
            c.insert(0, di); di = divisions[di]['parent']
        return c
    def prefix(p, depth):
        parts = []
        for di in chain(p['div'])[:depth]:
            r = roman_short(divisions[di]['t'])
            if r: parts.append(r)
        return ', '.join(parts)
    # for each repeated number, use the shallowest heading prefix that makes the label unique
    from collections import Counter
    cnt = {d_: Counter((prefix(p, d_), p.get('n')) for p in provisions if p['kind'] != 'division-text') for d_ in (1, 2, 3, 4)}
    def best_prefix(p):
        for d_ in (1, 2, 3, 4):
            if cnt[d_][(prefix(p, d_), p.get('n'))] == 1:
                return prefix(p, d_)
        return prefix(p, 4)
    out = []
    seen = set()
    for idx, p in enumerate(provisions):
        kind = p['kind']
        if kind == 'division-text':
            dt = divisions[p['div']]['t'] if p['div'] is not None else 'Text'
            label = roman_short(dt) or dt.split(' — ')[0].title()
            num = None
        else:
            num = p['n']
            kl = KIND_LABEL.get(kind, kind.title())
            label = p.get('label') or f"{kl} {num}"
            if num in dup:
                pre = best_prefix(p)
                if pre:
                    label = f"{pre}, {('Sec.' if kind == 'section' else 'Art.')} {num}"
        pid = re.sub(r'[^A-Za-z0-9]+', '-', label.lower()).strip('-')
        base = pid; k = 2
        while pid in seen:
            pid = f"{base}-{k}"; k += 1
        seen.add(pid)
        paras = [typo_norm(x) if isinstance(x, str) else x for x in p['paras']]
        paras = [x for x in paras if x != '']
        rec = {'i': pid, 'l': label, 'd': p['div'], 'p': paras}
        if num is not None: rec['n'] = num
        if p.get('cap'): rec['c'] = typo_norm(p['cap'])
        if p.get('old'): rec['o'] = p['old']
        if p.get('fn'): rec['f'] = p['fn']
        if p.get('v'): rec['v'] = p['v']
        if p.get('unk'): rec['u'] = p['unk']
        if p.get('page'): rec['pg'] = p['page']
        if p.get('e'): rec['e'] = list(p['e'])
        out.append(rec)
    return out


def apply_errata(cid, provs, divisions, log):
    for e in ERRATA.get(cid, []):
        if e['op'] == 'replace':
            hit = [p for p in provs if p.get('n') == e['n'] or p['i'] == e.get('id')]
            ok = False
            for p in hit:
                for j, para in enumerate(p['p']):
                    if isinstance(para, str) and e['find'] in para:
                        p['p'][j] = para.replace(e['find'], e['replace'], 1); ok = True
                        p.setdefault('e', []).append({'t': e['note'], 'b': e.get('basis', '')})
                        break
                if ok: break
            log.append({'code': cid, 'n': e['n'], 'op': 'replace', 'applied': ok, 'note': e['note']})
        elif e['op'] == 'insert':
            # insert a provision missing from the source, after provision n=e['after']
            pos = next((k for k, p in enumerate(provs) if p.get('n') == e['after']), None)
            ok = pos is not None and not any(p.get('n') == e['n'] for p in provs)
            if ok:
                prev = provs[pos]
                ok = True
                moved = []
                if e.get('move_from_prefix'):
                    # paragraphs that belong to the missing article were attached to the previous one
                    k = next((j for j, x in enumerate(prev['p']) if isinstance(x, str) and x.startswith(e['move_from_prefix'])), None)
                    if k is None:
                        ok = False
                    else:
                        moved = prev['p'][k:]
                        prev['p'] = prev['p'][:k]
                rec = {'i': re.sub(r'[^a-z0-9]+', '-', ('article ' if e.get('kind', 'article') == 'article' else 'section ') + e['n']).strip('-'),
                       'l': ('Article ' if e.get('kind', 'article') == 'article' else 'Section ') + e['n'], 'n': e['n'], 'd': prev['d'],
                       'p': e['paras'] + moved, 'e': [{'t': e['note'], 'b': e.get('basis', '')}]}
                if ok: provs.insert(pos + 1, rec)
            log.append({'code': cid, 'n': e['n'], 'op': 'insert', 'applied': ok, 'note': e['note']})
        elif e['op'] == 'note':
            for p in provs:
                if p.get('n') == e['n']:
                    p.setdefault('e', []).append({'t': e['note'], 'b': e.get('basis', '')})
            log.append({'code': cid, 'n': e['n'], 'op': 'note', 'applied': True, 'note': e['note']})


_DIC = None
def _dic():
    global _DIC
    if _DIC is None:
        d = set()
        for line in open('/usr/share/hunspell/en_US.dic', encoding='latin-1').read().split('\n')[1:]:
            w = line.split('/')[0].strip().lower()
            if w: d.add(w)
        _DIC = d
    return _DIC
PROTECT = {'de', 'la', 'del', 'los', 'las', 'y', 'san', 'sta', 'sto', 'el', 'da', 'di', 'du', 'van', 'von', 'mc', 'mac', 'st', 'no', 'nos', 'co', 'inc'}


def split_word_pass(assembled, report):
    """Rejoin words broken by a stray space in the source transcription (e.g. "inj uries")."""
    from collections import Counter
    vocab = Counter()
    for cid, (doc, provs) in assembled.items():
        for p in provs:
            for x in p['p']:
                if isinstance(x, str):
                    vocab.update(w.lower() for w in re.findall(r"[A-Za-z]+", x))
    dic = _dic()
    def isword(w):
        lw = w.lower()
        return lw in dic or vocab[lw] >= 4 or (lw.endswith('s') and lw[:-1] in dic) or (lw.endswith('ed') and (lw[:-2] in dic or lw[:-1] in dic)) or (lw.endswith('ing') and (lw[:-3] in dic or lw[:-3] + 'e' in dic))
    fixes = Counter()
    for cid, (doc, provs) in assembled.items():
        for p in provs:
            for j, x in enumerate(p['p']):
                if not isinstance(x, str):
                    continue
                def rep(m):
                    a, b = m.group(1), m.group(2)
                    if a.lower() in PROTECT or b.lower() in PROTECT or a.isupper() and len(a) > 1 or len(a + b) < 6:
                        return m.group(0)
                    joined = (a + b).lower()
                    if vocab[joined] >= 3 and joined in dic | set(k for k, v in vocab.items() if v >= 8) and (not isword(a) or not isword(b)):
                        fixes[(cid, a + ' ' + b)] += 1
                        p.setdefault('e', [])
                        note = f'Transcription artifact corrected: “{a} {b}” → “{a + b}”.'
                        if not any(e['t'] == note for e in p['e']):
                            p['e'].append({'t': note, 'b': 'Word split by a stray space in the source'})
                        return a + b
                    return m.group(0)
                p['p'][j] = re.sub(r"\b([A-Za-z]{1,12}) ([a-z]{1,12})\b", rep, x)
    for (cid, pair), n in fixes.items():
        report['errata'].append({'code': cid, 'n': '(auto)', 'op': 'rejoin', 'applied': True, 'note': f'“{pair}” rejoined ({n}×)'})
    return fixes


def numbering_check(provs):
    """Gaps and duplicates within each run of plain integer numbers."""
    issues = []
    prev = None
    for p in provs:
        m = re.match(r'^(\d+)$', str(p.get('n', '')))
        if not m:
            continue
        n = int(m.group(1))
        if prev is not None:
            if n == prev:
                issues.append(f'duplicate number {n}')
            elif prev < n <= prev + 25 and n != prev + 1:
                issues.append(f'gap: {prev} → {n}' + (f' (missing {prev+1}–{n-1})' if n - prev > 2 else f' (missing {prev+1})'))
        prev = n
    return issues


def main():
    raw = {}
    for (cid, short, title, cit, subj, src, core, note) in CODES:
        if src.startswith('md:'):
            raw[cid] = load_md(src[3:], cid)
        elif src == 'labor':
            raw[cid] = load_labor()
        elif src in ('family', 'admin'):
            p = WORK + f'/{src}/{src}.json'
            if not os.path.exists(p):
                print('skip (not built yet)', cid); continue
            raw[cid] = load_json_src(src)
        elif src == 'ins10607':
            raw[cid] = load_ins10607()
    catalog = {'built': datetime.date.today().isoformat(), 'subjects': [{'id': s, 'name': n} for s, n in SUBJECTS], 'codes': [], 'missing': []}
    report = {'errata': list(SPLITLOG), 'numbering': {}, 'anomalies': {}}
    total = 0
    assembled = {}
    for (cid, short, title, cit, subj, src, core, note) in CODES:
        if cid not in raw:
            continue
        doc = raw[cid]
        provs = assemble(cid, doc, None)
        apply_errata(cid, provs, doc['divisions'], report['errata'])
        if cid == 'civil' and os.path.exists(WORK + '/deleon/deleon_index.json'):
            chk = set(json.load(open(WORK + '/deleon/deleon_index.json'))['codal'])
            for p in provs:
                if p.get('n') in chk:
                    p['xc'] = 'Compared word by word with the codal text printed in De Leon, Obligations and Contracts'
        assembled[cid] = (doc, provs)
    fx = split_word_pass(assembled, report)
    print('split-word fixes', sum(fx.values()), 'distinct', len(fx))
    # amendment overlays (after all are assembled)
    for target, lst in AMENDERS.items():
        if target not in assembled:
            continue
        doc, provs = assembled[target]
        bynum = {}
        for p in provs:
            bynum.setdefault(str(p.get('n')), []).append(p)
        for amender, pattern in lst:
            if amender not in raw:
                continue
            label = next(c[3] for c in CODES if c[0] == amender)
            label = re.sub(r'^Republic Act No\. (\d+).*$', r'RA \1', label)
            ov = amendment_overlays(target, raw[amender], pattern, label)
            for n, items in ov.items():
                if n not in bynum and re.match(r'^\d+-[A-Z]$', n):
                    # article added by the amending law (e.g. RPC Arts. 266-A to 266-D by RA 8353)
                    base = n.split('-')[0]
                    after = [k for k, p in enumerate(provs) if str(p.get('n', '')).split('-')[0] == base]
                    if after:
                        pos = after[-1] + 1
                        it = items[0]
                        paras = list(it['p'])
                        m0 = re.match(r'^(?:Art\.|Article|ARTICLE)\s+' + re.escape(n.replace('-', '-?\\s*')) + r'\.?\s*', paras[0]) if paras else None
                        first = re.sub(r'^(?:Art\.|Article|ARTICLE|ART\.)\s+\d+\s*-\s*[A-Z]\.?\s*', '', paras[0]) if paras else ''
                        dvi = provs[after[-1]]['d']
                        if target == 'rpc' and amender == 'ra8353' and base == '266':
                            # RA 8353, Sec. 2: rape becomes a crime against persons, as a new Chapter Three of Title Eight
                            divs = doc['divisions']
                            want = 'CHAPTER THREE — RAPE'
                            hit = [k for k, v in enumerate(divs) if v['t'] == want]
                            if hit:
                                dvi = hit[0]
                            else:
                                par = divs[dvi]['parent'] if dvi is not None else None
                                divs.append({'t': want, 'lvl': divs[dvi]['lvl'] if dvi is not None else 2, 'parent': par})
                                dvi = len(divs) - 1
                        rec = {'i': 'article-' + n.lower(), 'l': 'Article ' + n, 'n': n, 'd': dvi, 'p': [first] + paras[1:],
                               'e': [{'t': f'Article {n} was added by {label} (Sec. {it["sec"]}). Its text here is taken verbatim from that law.', 'b': label}]}
                        cap, rest = P.split_caption(rec['p'][0])
                        if cap and rest: rec['c'] = cap.strip(' _'); rec['p'][0] = rest
                        provs.insert(pos, rec)
                        bynum[n] = [rec]
                        items = items[1:]
                for p in bynum.get(n, [])[:1]:
                    for it in items:
                        it['ref'] = amender
                        p.setdefault('a', []).append(it)
    for (cid, short, title, cit, subj, src, core, note) in CODES:
        if cid not in assembled:
            continue
        doc, provs = assembled[cid]
        an = {}
        for p in provs:
            txt = ' '.join(x for x in p['p'] if isinstance(x, str))
            a = anomalies(txt)
            if a:
                an[p['l']] = a
                p['x'] = a
        report['anomalies'][cid] = an
        report['numbering'][cid] = numbering_check(provs)
        meta = doc['meta']
        srcinfo = {
            'md': ('The LawPhil Project (Arellano Law Foundation), via LawCodex', meta.get('source', '')),
            'labor': ('DOLE, Labor Code of the Philippines, Renumbered (2022 ed.) — your PDF', ''),
            'family': ('Executive Order No. 209 — your PDF (text layer decoded and checked against OCR)', ''),
            'admin': ('Executive Order No. 292 — your scanned PDF (OCR)', ''),
            'ins10607': ('The LawPhil Project, RA 10607 Sec. 1 (consolidated Insurance Code)', meta.get('source', '')),
        }[src.split(':')[0]]
        data = {
            'id': cid, 'short': short, 'title': title, 'citation': cit, 'subject': subj, 'note': note,
            'source': {'name': srcinfo[0], 'url': srcinfo[1]},
            'preamble': [typo_norm(x) for x in doc.get('pre', []) if isinstance(x, str)][:12],
            'closing': [typo_norm(x) for x in doc.get('closing', [])],
            'divisions': [{'t': d['t'], 'l': d['lvl'], 'p': d['parent'], **({'f': d['fn']} if d.get('fn') else {})} for d in doc['divisions']],
            'provisions': provs,
        }
        js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        open(f'{OUT}/codes/{cid}.json', 'w').write(js)
        h = hashlib.sha1(js.encode()).hexdigest()[:10]
        words = sum(len(x.split()) for p in provs for x in p['p'] if isinstance(x, str))
        catalog['codes'].append({'id': cid, 'short': short, 'title': title, 'citation': cit, 'subject': subj, 'core': core,
                                 'note': note, 'count': len(provs), 'words': words, 'hash': h, 'bytes': len(js),
                                 'kind': src.split(':')[0]})
        total += len(provs)
    for (t, cit, subj, why) in MISSING:
        catalog['missing'].append({'title': t, 'citation': cit, 'subject': subj, 'why': why})
    catalog['total'] = total
    for c in catalog['codes']:
        cf, nf = f"{OUT}/cases/{c['id']}.json", f"{OUT}/notes/{c['id']}.json"
        if os.path.exists(cf):
            c['cases'] = True
            c['hash'] = hashlib.sha1((c['hash'] + str(os.path.getmtime(cf)) + str(os.path.getsize(cf))).encode()).hexdigest()[:10]
        if os.path.exists(nf):
            c['notes'] = True
            c['nhash'] = hashlib.sha1(open(nf, 'rb').read()).hexdigest()[:10]
    xc = json.load(open(WORK + '/deleon/xcheck.json')) if os.path.exists(WORK + '/deleon/xcheck.json') else []
    proof = {'errata': report['errata'], 'numbering': {k: v for k, v in report['numbering'].items() if v},
             'flags': {k: len(v) for k, v in report['anomalies'].items() if v},
             'crosscheck': {'civil_vs_deleon': {'articles': 274, 'with_differences': len(xc)}}}
    json.dump(proof, open(f'{OUT}/proofreading.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    for key, fn in (('shash', 'syllabus_index.json'), ('rhash', 'recent.json')):
        if os.path.exists(f'{OUT}/{fn}'):
            catalog[key] = hashlib.md5(open(f'{OUT}/{fn}', 'rb').read() + (open(f'{OUT}/syllabus.json', 'rb').read() if key == 'shash' and os.path.exists(f'{OUT}/syllabus.json') else b'')).hexdigest()[:10]
    json.dump(catalog, open(f'{OUT}/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(report, open(f'{WORK}/proofread_report.json', 'w'), ensure_ascii=False, indent=1)
    print('codes', len(catalog['codes']), 'provisions', total)
    print('errata', sum(1 for e in report['errata'] if e['applied']), '/', len(report['errata']))


if __name__ == '__main__':
    main()
