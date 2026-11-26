"""Amendments that came after a study text's source edition (found by audit_stale.py and the statute graph).
Each entry's text is taken verbatim from the amending law in the LawCodex corpus; this script writes them
into errata.json (idempotent: entries it wrote before carry 'late': True and are replaced)."""
import json, gzip, base64, re, sys
D = '/home/claude/site/data'
idx = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/idx.txt').read())))
rows = {r[0]: r for r in idx['rows']}
_cache = {}
def body(lid):
    c = rows[lid][6]
    if c not in _cache:
        _cache[c] = json.loads(gzip.decompress(base64.b64decode(open(f'{D}/statutes/c{c:03d}.txt').read())))
    return _cache[c][lid]['b']

def clean(line):
    line = re.sub(r'^#+\s*', '', line.strip())
    line = re.sub(r'^[“"”]+\s*|\s*[“"”]+$', '', line)
    line = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', line).replace('\\-', '-').replace('\\', '')
    line = re.sub(r'\*\*', '', line)
    return line.strip()

LABEL = re.compile(r'^(?:Section|SECTION|SEC[.,]|Sec[.,]|Article|ARTICLE|Art\.|ART\.)\s*(\d+(?:-[A-Z])?)\s*(?:[.,\-–—:]\s*|$)', re.I)
def replacement(lid, intro, n, whole=False, raw=False):
    """Text of provision n as restated in law lid, after the sentence matching intro."""
    b = body(lid)
    m = re.search(intro, b, re.I)
    if not m:
        raise SystemExit(f'{lid}: intro not found: {intro}')
    rest = b[m.end():]
    stop = re.search(r'\n#{2,4}\s+Section\s+\d+\s*\n', rest)
    block = rest[:stop.start()] if stop else rest
    paras = [clean(x) for x in re.split(r'\n\s*\n', block) if clean(x)]
    paras = [p for p in paras if p not in ('.',)]
    def tab(p):
        if '<table' not in p:
            return p
        rows_ = [[re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)] for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', p, re.S)]
        return {'t': 'table', 'rows': [r for r in rows_ if any(r)]}
    paras = [tab(p) for p in paras]
    if raw:     # the restated text carries no label of its own
        out = []
        for p in paras:
            if re.match(r'^(?:\d+\.\s+This (?:Decree|Act)|Done in|Approved|This Act shall take effect)', p): break
            out.append(re.sub(r'^\.?["“]', '', p).strip())
        return out
    if whole:   # the law restates one paragraph without the provision's label
        return ['x x x'] + [re.sub(r'^\.?["“]', '', p).strip() for p in paras] + ['x x x']
    # keep only the restated provision n (an amending section may restate several)
    out, on = [], False
    for p in paras:
        lm = LABEL.match(p) if isinstance(p, str) else None
        if lm:
            on = lm.group(1).lower() == str(n).lower()
            if on:
                p = p[lm.end():]
        if on:
            out.append(p)
    if not out:
        raise SystemExit(f'{lid}: provision {n} not found after intro')
    # tidy stray quote marks the transcription leaves mid-line ('."x x x')
    out = [re.sub(r"^\.?[\"“]|'$", '', p).strip() if isinstance(p, str) else p for p in out]
    return [p for p in out if p]

def lab(r):
    return {'ra': 'RA', 'pd': 'PD', 'bp': 'BP', 'ca': 'CA', 'act': 'Act', 'eo': 'EO'}[r.split('-')[0]] + ' ' + r.split('-')[1].upper()

def year(lid):
    return (rows[lid][4] or rows[lid][3] or '')[:4]

E = []
def amend(code, n, lid, sec, intro, note, partial=False, id_=None, whole=False, raw=False):
    paras = replacement(lid, intro, n, whole, raw)
    e = {'op': 'amend', 'by': lab(lid), 'sec': sec, 'y': year(lid), 'paras': paras, 'late': True,
         'basis': 'Text verbatim from the amending law (LawPhil transcription, via LawCodex).',
         'note': note + (' It restates only part of the provision (“x x x” marks the parts left as they were): read it with the earlier text.' if partial or any('x x x' in p for p in paras) else '')}
    if id_: e['id'] = id_
    else: e['n'] = str(n)
    E.append((code, e))

def status(code, n, note, basis, st=None, id_=None):
    e = {'op': 'note', 'note': note, 'basis': basis, 'late': True}
    if st: e['st'] = st
    if id_: e['id'] = id_
    else: e['n'] = str(n)
    E.append((code, e))


def labeled(block_paras):
    """[(n, paras)] for every provision restated in a block, in order."""
    out, cur = [], None
    for p in block_paras:
        lm = LABEL.match(p) if isinstance(p, str) else None
        if lm:
            cur = (lm.group(1).upper() if '-' in lm.group(1) else lm.group(1), [p[lm.end():]] if p[lm.end():].strip() else [])
            out.append(cur)
        elif cur:
            cur[1].append(p)
    return [(n, [re.sub(r"^\.?[\"“]|'$", '', x).strip() if isinstance(x, str) else x for x in ps if x]) for n, ps in out]

def block_after(lid, m_end):
    b = body(lid); rest = b[m_end:]
    stop = re.search(r'\n#{2,4}\s+Section\s+\d+\s*\n', rest)
    block = rest[:stop.start()] if stop else rest
    return [clean(x) for x in re.split(r'\n\s*\n', block) if clean(x)]

def auto(code, lid, target, have, why, topic):
    """Every 'Section N of <target> ... is hereby (further) amended to read as follows' and every inserted section in law lid."""
    b = body(lid)
    for m in re.finditer(r'(?:Section|Sec\.)\s*(\d+(?:-[A-Z])?)(\s*,\s*[Pp]aragraph\s*\(?(\w+)\)?)?(?:\s*,?\s*of\s+(?:the\s+same\s+(?:law|Act)|' + target + r')[^\n]*?)?\s+(?:is|are)\s+hereby\s+(?:further\s+)?amended\s+(?:to\s+read\s+)?as\s+follows:', b):
        n, part, which = m.group(1), bool(m.group(2)), m.group(3)
        if re.search(r'title\s+of\s*$', b[max(0, m.start() - 20):m.start()], re.I):
            continue   # only the section's title was changed
        paras = block_after(lid, m.end())
        if part:
            got = dict(labeled(paras)).get(n)
            body_ps = got if got else [re.sub(r"^\.?[\"“]", '', p).strip() for p in paras]
            if which in ('1', 'a'):
                ps = body_ps + ['x x x']
            elif body_ps and len(body_ps[0]) < 60 and re.search(r'[-–—:]\s*$', body_ps[0]):   # keep the caption on top
                ps = [body_ps[0], 'x x x'] + body_ps[1:] + ['x x x']
            else:
                ps = ['x x x'] + body_ps + ['x x x']
        else:
            got = dict(labeled(paras))
            ps = got.get(n)
            if not ps:
                print('   skip (not found)', lid, n); continue
        if n not in have:
            print('   skip (no such provision)', lid, n); continue
        e = {'op': 'amend', 'n': n, 'by': lab(lid), 'sec': '', 'y': year(lid), 'paras': ps, 'late': True,
             'basis': 'Text verbatim from the amending law (LawPhil transcription, via LawCodex).',
             'note': f'{lab(lid)} ({year(lid)}) {why}' + (' It restates only part of the section (“x x x” marks the parts left as they were).' if any(isinstance(p, str) and 'x x x' in p for p in ps) else '')}
        E.append((code, e))
    for m in re.finditer(r'(?:There shall be incorporated after|by adding)\s+(?:a new\s+)?(?:Section\s+(\d+)\s+of\s+' + target + r'[^\n]*?|' + r'Section\s+(\d+(?:-[A-Z])?)\s+)[^\n]*?to read as follows:', b):
        after = m.group(1)
        paras = block_after(lid, m.end())
        for n, ps in labeled(paras):
            if n in have or not re.match(r'\d+-[A-Z]$', n):
                continue
            a = after or re.match(r'\d+', n).group(0)
            E.append((code, {'op': 'insert', 'after': a, 'n': n, 'kind': 'section', 'paras': ps, 'late': True,
                             'basis': 'Text verbatim from the amending law (LawPhil transcription, via LawCodex).',
                             'note': f'Inserted by {lab(lid)} ({year(lid)}), {topic}.'}))
            have.add(n); after = n

# --- land registration: RA 11573 (2021) rewrote PD 1529 Sec. 14
amend('pd1529', 14, 'ra-11573', '6', r'Section 14 of Presidential Decree No\. 1529 is hereby amended to read as follows:',
      'RA 11573 (approved July 16, 2021) rewrote Section 14. Judicial confirmation now needs at least twenty years of open, continuous, exclusive and notorious possession of alienable and disposable land immediately before filing, instead of possession since June 12, 1945 or earlier; it caps the area at twelve hectares and lets the application be filed “at any time”. Its Section 7 makes a DENR geodetic engineer’s certification on the survey plan sufficient proof that the land is alienable and disposable.')

# --- RA 7610 as amended by RA 11648 (2022): age 16 for statutory rape and related offences
for n, what in ((5, 'raised to sixteen the age below which the offender is prosecuted for rape or lascivious conduct under the Revised Penal Code'),
                (7, 'made the penalty for child trafficking maximum when the victim is under sixteen'),
                (9, 'restated the penalty for using children in obscene publications and indecent shows'),
                (10, 'raised to sixteen the age in paragraph (b), keeping a minor in one’s company in certain places')):
    amend('ra7610', n, 'ra-11648', '3', r'Sections 5\(b\), 7, 9, and 10\(b\) of Republic Act No\. 7610[^\n]*?amended to read as follows:',
          f'RA 11648 (approved March 4, 2022) {what}.', partial=True)

# --- Cybercrime: RA 11930 (2022) repealed Sec. 4(c)(1) (child pornography)
status('ra10175', 4, 'Paragraph (c)(1), child pornography, was repealed by RA 11930 (approved July 30, 2022), the Anti-OSAEC and Anti-CSAEM Act, which now punishes those acts; the rest of Section 4 stands.',
       'RA 11930, Repealing Clause, verbatim in LawCodex: “Republic Act No. 9775 and Section 4 (c) (1) of Republic Act No. 10175 … are hereby repealed.”')

# --- Firearms: RA 11766 (2022) changed licence validity periods
amend('ra10591', 7, 'ra-11766', '1', r'Section 7 of Republic Act No\. 10591 is hereby amended to read as follows:',
      'RA 11766 (approved May 6, 2022) restated this section: a permit to carry is now valid for two years from approval of the application, and the threat assessment rules and exempt professions are spelled out.')
amend('ra10591', 19, 'ra-11766', '2', r'Section 19 of Republic Act No\. 10591 is hereby amended to read as follows:',
      'RA 11766 (approved May 6, 2022) made licences to possess and firearm registrations renewable every five or ten years, at the licensee’s option, reckoned from the licensee’s birthdate.')

# --- Muslim personal laws: RA 12018 (2024) new Shari'a districts and circuit courts
for n in (138, 147, 150):
    amend('pd1083', n, 'ra-12018', '', rf'Article {n} of Presidential Decree No\. 1083[^\n]*?is hereby amended (?:to read )?as follows:',
          'RA 12018 (approved August 12, 2024) created three more Shari’a judicial districts and twelve more Shari’a circuit courts; this article is restated accordingly.', id_=None)

# --- LGC: RA 11535 (2021) cooperatives development officer mandatory
for n, sec in ((443, '1'), (454, '2'), (463, '3'), (487, '4')):
    amend('lgc', n, 'ra-11535', sec, rf'Section {n},? (?:of )?Book III[^\n]*?Republic Act No\. 7160,? is hereby amended (?:to read as follows|and shall now read as follows):',
          'RA 11535 (approved April 9, 2021) made the cooperatives development officer a mandatory position in municipalities, cities and provinces.')

# --- DILG / PNP: RA 11200 (2019) rank classification; RA 11549 (2021) height
amend('ra6975', 28, 'ra-11200', '1', r'Section 28 of Republic Act No\. 6975[^\n]*?is hereby amended to read as follows:',
      'RA 11200 (approved February 8, 2019) replaced the PNP rank titles with military-style ranks (e.g., Police General, Police Colonel, Police Executive Master Sergeant).')
amend('ra6975', 30, 'ra-11549', '1', r'Section 30 of Republic Act No\. 6975, as amended, is further amended to read as follows:',
      'RA 11549 (approved May 26, 2021) lowered the minimum height for PNP applicants to 1.57 m (men) and 1.52 m (women).')

# --- Migrant workers: RA 11299 (2019) social welfare attaché
amend('ra8042', 2, 'ra-11299', '', r'Section 2, paragraph \(b\) of Republic Act No\. 8042, as amended, is hereby amended to read as follows:',
      'RA 11299 (approved April 17, 2019) restated paragraph (b) of the declaration of policies.', whole=True)

# --- SSS: RA 11548 (2021) power to defer contribution increases
amend('ra11199', 4, 'ra-11548', '1', r'Section 4\(a\)\(9\) of Republic Act No\. 11199[^\n]*?is hereby amended to read as follows:',
      'RA 11548 (approved May 26, 2021) let the President defer the scheduled increase in SSS contributions for the duration of the COVID-19 state of calamity under Proclamation No. 929, s. 2020; the other scheduled rates stay.', partial=True)

# --- Consumer Act: RA 11765 (2022) repealed Arts. 131-147 (consumer credit transactions)
for n in range(131, 148):
    status('ra7394', n, 'Repealed by RA 11765 (approved May 6, 2022), the Financial Products and Services Consumer Protection Act, which now governs consumer credit and financial products.',
           'RA 11765, Repealing Clause, verbatim in LawCodex: “Articles 131 to 147 of Title IV of Republic Act No. 7394 are hereby repealed.”', st='repealed')

# --- Labor Code: RA 12063 (approved November 7, 2024), the EBET Framework Act, repealed Book Two, Title II, Chapters 1-2
for n in range(57, 78):
    status('labor', n, 'Repealed by RA 12063 (approved November 7, 2024), the Enterprise-Based Education and Training (EBET) Framework Act, which repealed Book Two, Title II, Chapters 1 and 2 (apprentices and learners) and now governs apprenticeship and learnership under one TESDA-run framework.',
           'RA 12063, Repealing Clause, verbatim in LawCodex: “… Book Two, Title II, Chapters 1 and 2 of Presidential Decree No. 442 or the “Labor Code of the Philippines” … are hereby repealed.”', st='repealed', id_=f'article-{n}')

# --- Civil Code Art. 1146: PD 1755 (1980) added a one-year period for martial-law claims against public officers
amend('civil', 1146, 'pd-1755', '1', r'Article 1146 of the Civil Code of the Philippines is hereby amended to read as follows:',
      'PD 1755 (December 24, 1980) restated Article 1146 and added a one-year period for actions arising from acts of public officers under martial law (arrest, detention or trial of the plaintiff). The four-year periods for injury to rights and quasi-delict are unchanged.', raw=True)

# --- CARL: the study text is RA 6657 as enacted; bring in the later amendments in order
_carl = {p['n'] for p in json.load(open(f'{D}/codes/carl.json'))['provisions']
         if p.get('n') and not any(str(x.get('t', '')).startswith('Inserted by') for x in p.get('e', []))}   # not our own inserts
auto('carl', 'ra-7881', r'Republic Act No\. 6657', _carl, 'amended this section (fishponds, prawn farms and commercial farms).', 'the law on fishponds, prawn farms and commercial farms')
auto('carl', 'ra-7905', r'Republic Act No\. 6657', _carl, 'amended this section (support services and implementation).', 'the law strengthening support services and implementation')
auto('carl', 'ra-8532', r'Republic Act No\. 6657', _carl, 'amended this section (funding of the CARP).', 'the law extending CARP funding')
auto('carl', 'ra-9700', r'Republic Act (?:No|So)\. 6657', _carl, 'is the CARPER law: it extended land acquisition and distribution to June 30, 2014 and rewrote this section.', 'the CARPER law, which extended land acquisition and distribution to June 30, 2014')

if __name__ == '__main__':
    er = json.load(open('errata.json'))
    for code in er:
        er[code] = [e for e in er[code] if not e.get('late')]
    for code, e in E:
        er.setdefault(code, []).append(e)
    json.dump(er, open('errata.json', 'w'), ensure_ascii=False, indent=1)
    print('late errata', len(E))
    for code, e in E:
        if e['op'] == 'amend':
            print(' ', code, e.get('n') or e.get('id'), e['by'], '|', str(e['paras'][0])[:110], len(e['paras']))
