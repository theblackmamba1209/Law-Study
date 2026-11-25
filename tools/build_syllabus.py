"""Parse the user's law-school syllabi and file every case under the provision it is taught with.

Output:
  data/syllabus.json        – each course as an outline (topics, provision references, cases)
  data/syllabus_index.json  – "code|provision-id" -> list of syllabus cases filed there
Rules for filing a case:
  1. the provision references in the same outline topic (e.g. "a 3, RPC", "s 21, a III 1987 Constitution",
     "Section 4." headings in the CL2 syllabus);
  2. if that topic has no references at all, the nearest ancestor topic's references;
  3. if none, a default for that part of the outline (listed in DEFAULTS), chosen from what the topic covers;
  4. otherwise the case stays in the syllabus outline only.
"""
import json, re, os, sys, glob, unicodedata

SYL = '/home/claude/syl/txt'
SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site/data'
CAT = json.load(open(SITE + '/catalog.json'))
CODES = {c['id']: json.load(open(f"{SITE}/codes/{c['id']}.json")) for c in CAT['codes']}
BYNUM = {cid: {} for cid in CODES}
BYLABEL = {cid: {} for cid in CODES}
for cid, d in CODES.items():
    for p in d['provisions']:
        if p.get('n') is not None and str(p['n']) not in BYNUM[cid]:
            BYNUM[cid][str(p['n'])] = p['i']
        BYLABEL[cid][p['l']] = p['i']

# citation -> code id, e.g. "RA 9160" -> ra9160
CITEMAP = {}
for c in CAT['codes']:
    for m in re.finditer(r'(Republic Act|Presidential Decree|Batas Pambansa Blg\.|Executive Order|Commonwealth Act|Act)\s+No\.?\s*(\d+)', c['citation']):
        k = {'Republic Act': 'RA', 'Presidential Decree': 'PD', 'Batas Pambansa Blg.': 'BP', 'Executive Order': 'EO', 'Commonwealth Act': 'CA', 'Act': 'ACT'}[m.group(1)]
        CITEMAP.setdefault(f'{k} {m.group(2)}', c['id'])
CITEMAP['ACT 3815'] = 'rpc'
CITEMAP['RA 386'] = 'civil'
CITEMAP['BP 881'] = 'oec'

ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV', 16: 'XVI', 17: 'XVII', 18: 'XVIII'}


def clean(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[​-‏‪-‮⁠﻿]', '', s)
    s = s.replace('', '').replace('�', '–')
    return re.sub(r'\s+', ' ', s).strip()


def link(cid, num=None, art=None, sec=None):
    if cid not in CODES:
        return None
    if cid == 'const1987':
        lab = f'Art. {art}, Sec. {sec}' if sec else f'Art. {art}'
        pid = BYLABEL[cid].get(lab)
        return {'c': cid, 'i': pid, 'l': lab} if pid else None
    if num is None:
        return {'c': cid}
    pid = BYNUM[cid].get(str(num))
    return {'c': cid, 'i': pid, 'l': CODES[cid]['provisions'][[p['i'] for p in CODES[cid]['provisions']].index(pid)]['l']} if pid else {'c': cid}


def nums(spec):
    """'246, 248 – 251' -> ['246','248','249','250','251'] (ranges up to 12 long)"""
    out = []
    for part in re.split(r',|&|and', spec):
        part = part.strip()
        m = re.match(r'^(\d+)(?:-([A-Z]))?\s*[-–—]\s*(\d+)(?:-([A-Z]))?$', part)
        if m and not m.group(2) and not m.group(4):
            a, b = int(m.group(1)), int(m.group(3))
            if 0 < b - a <= 12:
                out += [str(x) for x in range(a, b + 1)]
            else:
                out += [str(a), str(b)]
        else:
            m = re.match(r'^(\d+(?:-[A-Z])?)', part)
            if m:
                out.append(m.group(1))
    return out


def refs(text, default='rpc'):
    """Find provision references in a line of a syllabus."""
    t = clean(text)
    out = []
    # Constitution: "s 21, a III 1987 Constitution", "a 6, s 11, 1987 Constitution", "Art 4, S3-5", "Art. 8, Sec.5(5)", "Sec. 13, Article III, Constitution"
    if re.search(r'Constitution', t, re.I) or re.search(r'\bArt\.?\s*\d+\s*,\s*S(?:ec)?\.?\s*\d', t):
        for m in re.finditer(r'\bs(?:ec(?:tion)?)?\.?\s*(\d+)(?:\s*[-–]\s*(\d+))?[^,]{0,8},\s*a(?:rt(?:icle)?)?\.?\s*([IVXL]+|\d+)', t, re.I):
            art = m.group(3); art = ROMAN.get(int(art), art) if art.isdigit() else art.upper()
            for s in range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1):
                out.append(link('const1987', art=art, sec=s))
        for m in re.finditer(r'\ba(?:rt(?:icle)?)?\.?\s*([IVXL]+|\d+)\s*,\s*S(?:ec(?:tion)?)?\.?\s*(\d+)(?:\s*[-–]\s*(\d+))?', t, re.I):
            art = m.group(1); art = ROMAN.get(int(art), art) if art.isdigit() else art.upper()
            for s in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                out.append(link('const1987', art=art, sec=s))
        return [x for x in out if x]
    # special laws: "s 4(f), RA 9160", "Section 26 (R.A. 9262)", "Republic Act No. 10173", "P.D. 1829", "RA 9995"
    law = re.search(r'\b(R\.?\s?A\.?|Republic Act(?: No\.)?|P\.?\s?D\.?|Presidential Decree(?: No\.)?|B\.?\s?P\.?(?: Blg\.)?|Batas Pambansa(?: Blg\.)?|E\.?\s?O\.?|Executive Order(?: No\.)?|C\.?\s?A\.?|Commonwealth Act(?: No\.)?|Act(?: No\.)?)\s*(\d{2,5})\b', t)
    if law and not re.search(r'\bRPC\b|Revised Penal Code', t[:law.start()]):
        k = law.group(1).replace('.', '').replace(' ', '').upper()
        k = {'REPUBLICACT': 'RA', 'REPUBLICACTNO': 'RA', 'PRESIDENTIALDECREE': 'PD', 'PRESIDENTIALDECREENO': 'PD', 'BPBLG': 'BP', 'BATASPAMBANSA': 'BP', 'BATASPAMBANSABLG': 'BP',
             'EXECUTIVEORDER': 'EO', 'EXECUTIVEORDERNO': 'EO', 'COMMONWEALTHACT': 'CA', 'COMMONWEALTHACTNO': 'CA', 'ACTNO': 'ACT'}.get(k, k)
        cid = CITEMAP.get(f'{k} {law.group(2)}')
        if cid:
            sec = re.search(r'\b(?:s|sec(?:tion)?\.?|ss)\s*(\d+(?:-[A-Z])?)', t[:law.start()], re.I)
            out.append(link(cid, sec.group(1) if sec else None))
            return [x for x in out if x]
        return []
    if re.search(r'Civil Code', t, re.I):
        for m in re.finditer(r'\ba(?:rt(?:icle)?)?\.?\s*(\d+)', t, re.I):
            out.append(link('civil', m.group(1)))
        return [x for x in out if x]
    if re.search(r'Family Code', t, re.I):
        for m in re.finditer(r'\ba(?:rt(?:icle)?)?\.?\s*(\d+)', t, re.I):
            out.append(link('family', m.group(1)))
        return [x for x in out if x]
    # RPC articles: "a 3, RPC", "a 4, p 2, RPC", "a 19 & a 20", "Article 6 (RPC)", "Articles 246, 248 – 251", "Art 124 (RPC)"
    for m in re.finditer(r'\b(?:a|arts?\.?|articles?)\s*((?:\d+(?:-[A-Z])?)(?:\s*(?:,|&|and|[-–—])\s*(?:a\s*)?\d+(?:-[A-Z])?)*)', t, re.I):
        spec = re.sub(r'\ba\s*', '', m.group(1))
        spec = re.sub(r',\s*p\s*\d+', '', spec)
        for n in nums(spec):
            out.append(link(default, n))
    return [x for x in out if x and x.get('i')]


CASE_HINT = re.compile(r'\b(vs?\.?|versus)\s|^In [Rr]e\b|^Re:|^In the Matter|^People v|\bG\.?\s?R\.?\s|\bGR\b|\bSCRA\b|\bSRCA\b|\bPhil\.?\b|\bPHIL\b|\bA\.?\s?C\.?\s?No|\bA\.?\s?M\.?\s?No|\bI\.?C\.?J\.?|U\.S\. v')
CITE_START = re.compile(r',?\s*(?:\[|\()?(?=(?:G\.?\s?R\.?|GR\b|A\.?\s?C\.?\s?No|A\.?\s?M\.?|AM\s|AC\s|\d{1,4}\s*(?:SCRA|SRCA|Phil\.?|PHIL|P\b|O\.G\.)|No[s]?\.\s*L?-?\d|L-\d|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d))')


MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sept?\.?|Oct\.?|Nov\.?|Dec\.?)'
OPEN_END = re.compile(r'(?:G\.?\s?R\.?\s*(?:Nos?\.?)?|\bNos?\.|\bL-|,|&|\band|' + MONTHS + r'|' + MONTHS + r'\s+\d{1,2},?|\b\d{1,2}\s+' + MONTHS + r'|\bG\.R)\s*$')
CONT_START = re.compile(r'^(?:\d{4}\)?[.;,]?\s*$|\d{4}\)|\d{1,2},\s*\d{4}|\d{5,6}\b|\d{3,6},\s|[a-z(]|' + MONTHS + r'\s+\d)')


def join_wrapped(lines):
    """Re-join citations the syllabus wrapped onto the next line (e.g. '…, 16 March' + '2021)')."""
    out = []
    for l in lines:
        if out and l and out[-1] and CASE_HINT.search(out[-1]) and (OPEN_END.search(out[-1]) or CONT_START.match(l)) \
                and not re.match(r'^(Section|Sec\.|Art\.|Article|ARTICLE|Canon|Rule|PART)\b', l):
            out[-1] = out[-1] + ' ' + l
        else:
            out.append(l)
    return out


# known slips in the syllabus text itself: (name, cite as printed) -> (corrected cite, note shown to the student)
SYL_ERRATA = {
    ('DOH v. Philip Morris Philippines Manufacturing, Inc', 'G.R. No. 202943, March 25, 201'):
        ('G.R. No. 202943, March 25, 2015', 'syllabus prints “201”; the decision is dated March 25, 2015'),
}


def split_case(line):
    s = clean(line)
    s = re.sub(r'^[-–•*⁃◦▪●]+\s*', '', s)
    s = re.sub(r'^\d{1,3}\s?[.)]\s*', '', s)
    s = re.sub(r'^[-–•*⁃◦▪●]+\s*', '', s)
    # outline markers such as "a.", "iv.", "v." (the roman five, not "v." for versus) before a case name
    m = re.match(r'^(?:[ivxlc]{1,5}|[a-hj-z])[.)]\s+(?=[A-Z])', s)
    if m and (re.search(r'\sv(?:s|ersus)?\.?\s|Advisory Opinion|\bCase\b', s[m.end():]) or re.match(r'^(In re|Re:|In the Matter)', s[m.end():])):
        s = s[m.end():]
    note = ''
    m = re.search(r'\s[-–]\s(?=[a-z])|:\s', s)
    if m and m.group(0).startswith(':') and not re.search(r'\sv(?:s|ersus)?\.?\s', s[:m.start()]) and re.search(r'\sv(?:s|ersus)?\.?\s', s[m.end():]):
        note, s = s[:m.start()].strip(), s[m.end():]          # "Murder: ICC, … Prosecutor v. Katanga" -> topic first
    elif m and m.start() > 15:
        note, s = s[m.end():].strip(), s[:m.start()]
    mm = CITE_START.search(s)
    if mm and mm.start() > 3:
        name, cite = s[:mm.start()], s[mm.end():]
    else:
        name, cite = s, ''
    pm = re.search(r'\(([^()]{3,80})\)\s*$', cite or name)
    if pm and not re.search(r'\d{4}', pm.group(1)):
        note = (pm.group(1) + ('; ' + note if note else '')).strip()
        if cite:
            cite = cite[:pm.start()]
        else:
            name = name[:pm.start()]
    name = name.strip(' ,;.-–')
    cite = cite.strip(' ,;')
    if cite.endswith(')') and cite.count(')') > cite.count('('):
        cite = cite[:-1].rstrip()
    fix = SYL_ERRATA.get((name, cite))
    if fix:
        cite, note = fix[0], (fix[1] + ('; ' + note if note else ''))
    return name, cite, note[:220]


CONCEPT_PAIR = re.compile(r'\b(Incorporation|Transformation|Horizontal|Vertical|Monism|Dualism)\b\s+vs?\.?\s+\b(Incorporation|Transformation|Horizontal|Vertical|Monism|Dualism)\b', re.I)


def is_case(line):
    t = clean(line)
    t = re.sub(r'^(?:[ivxlc]{1,6}|[a-zA-Z]|\d{1,3})[.)]\s+', '', t)
    if len(t) < 6 or CONCEPT_PAIR.search(t):
        return False
    # a heading such as "Pacta Sunt Servanda:" or "Statute of the ICJ" with no party names and no citation
    if not re.search(r'\w\s+(vs?\.?|versus)\s|^In [Rr]e\b|^Re:|^In the Matter|G\.?\s?R\.?\s|\bGR\b|\bGRN\b|SCRA|\d\s*Phil\.?\b|\d\s*PHIL\b|A\.?\s?C\.?\s?No|A\.?\s?M\.?\s?No|\bCase\b|Advisory Opinion|U\.S\. v', t):
        return False
    if re.match(r'^(Section|Sec\.|Art\.|Article|Articles|Rule|Canon|ARTICLE|A\.M\. No\. \d+-\d+-\d+-SC\s*$)', t):
        return False
    return bool(CASE_HINT.search(t)) and bool(re.search(r'[A-Z][a-z]', t))


# ------------------------------------------------------------------ CL2 (Constitutional Law 2)
def parse_cl2():
    lines = join_wrapped([clean(l) for l in open(f'{SYL}/2023 CL2 Syllabus.txt').read().split('\n')])
    items = []
    art, sec, topic = None, None, None
    for l in lines:
        if not l:
            continue
        m = re.match(r'^ARTICLE\s+([IVXL]+)\s*[-–—]\s*(.*)$', l)
        if m:
            art, sec = m.group(1), None
            items.append({'t': 'h', 'lvl': 0, 'x': l, 'links': [x for x in [link('const1987', art=art)] if x]})
            continue
        m = re.match(r'^Section\s+(\d+)\.\s+(?:\(\d\)\s*)?[A-Z“"]', l)
        if m and art and len(l) > 40 and not re.match(r'^Section\s+\d+\.\s+(Cases?|Case)\b', l):
            sec = int(m.group(1))
            lk = link('const1987', art=art, sec=sec)
            items.append({'t': 'h', 'lvl': 1, 'x': f'Art. {art}, Sec. {sec}', 'q': l[len(m.group(0)) - 1:][:400], 'links': [lk] if lk else []})
            topic = None
            continue
        if re.match(r'^Cases?:?$', l):
            continue
        if is_case(l):
            name, cite, note = split_case(l)
            lk = link('const1987', art=art, sec=sec) if art and sec else (link('const1987', art=art) if art else None)
            items.append({'t': 'c', 'n': name, 'c': cite, 'note': note, 'topic': topic, 'links': [lk] if lk else []})
            continue
        r = refs(l, 'rpc') if re.search(r'\b(R\.?A\.?|Republic Act|P\.?D\.?|Constitution|Civil Code|Art(icle)?\.?\s*\d)', l) else []
        if len(l) < 140:
            topic = l
            items.append({'t': 'h', 'lvl': 2, 'x': l, 'links': r})
        else:
            items.append({'t': 'n', 'x': l[:600], 'links': r})
    return {'id': 'cl2', 'title': 'Constitutional Law 2 (Bill of Rights, Citizenship, Suffrage, Social Justice, Education)', 'teacher': 'Judge Edilwasif T. Baddiri', 'items': items}


# ------------------------------------------------------------------ Crim 1 (outline with references)
CRIM1_DEFAULTS = [
    (r'^II\b|^2\.', [('rpc', '3')]), (r'^III\b|^3\.(1|3|4|5)', [('rpc', '3')]), (r'^3\.2', [('rpc', '4')]),
    (r'^4\.1', [('rpc', '8')]), (r'^4\.2', [('rpc', '6')]), (r'^4\.3', [('rpc', '4')]),
    (r'^5\.1', [('rpc', '17')]), (r'^5\.2', [('rpc', '18')]), (r'^5\.3', [('rpc', '19')]), (r'^5\.6', [('pd1612', '2')]),
    (r'^VI\b|^6\.', [('rpc', '11')]), (r'^VII\b|^7\.[1-5]', [('rpc', '12')]), (r'^7\.6', [('ra9344', '6')]),
    (r'^9\.1|^9\.2', [('rpc', '25')]), (r'^9\.3', [('rpc', '46')]),
    (r'^10\.1', [('rpc', '13')]), (r'^10\.2', [('rpc', '14')]), (r'^10\.3', [('rpc', '15')]),
    (r'^XI\b|^11\.', [('isl', '1')]), (r'^13\.1', [('rpc', '78')]), (r'^13\.2', [('rpc', '29')]), (r'^13\.3', [('rpc', '89')]),
    (r'^13\.4', [('rpc', '38')]), (r'^13\.5', [('rpc', '39')]), (r'^XIV\b|^14\.', [('rpc', '100')]), (r'^XV\b|^15\.', [('rpc', '10')]),
]


def parse_crim1():
    raw = open(f'{SYL}/R A ABITRIA CRIM 1 SYLLABUS.txt').read().split('\n')
    lines = []
    for l in raw:
        c = clean(l)
        if not c or re.match(r'^(R A ABITRIA CRIM 1 SYLLABUS|\d{1,3})$', c):
            continue
        lines.append((len(l) - len(l.lstrip()), c))
    # join wrapped lines: a line that does not start a new numbered item continues the previous one
    merged = []
    for ind, c in lines:
        if merged and not re.match(r'^(\d+(\.\d+)*\.|[IVX]+\.)\s', c) and not re.match(r'^[A-Z][A-Z ]{6,}$', c):
            merged[-1] = (merged[-1][0], merged[-1][1] + ' ' + c)
        else:
            merged.append((ind, c))
    nodes = [{'key': 'root', 'title': 'Criminal Law 1', 'refs': [], 'kids': [], 'items': [], 'parent': None}]
    stack = [nodes[0]]
    items = []
    for ind, c in merged:
        m = re.match(r'^((?:\d+\.)+\d*\.?|[IVX]+\.)\s+(.*)$', c)
        if m and (re.match(r'^[IVX]+\.$', m.group(1)) or m.group(1).count('.') >= 2):
            key = m.group(1).rstrip('.')
            depth = 0 if re.match(r'^[IVX]+$', key) else key.count('.') + 1
            while len(stack) > depth + 1:
                stack.pop()
            node = {'key': key, 'title': m.group(2), 'refs': refs(m.group(2)), 'kids': [], 'items': [], 'parent': stack[-1]}
            stack[-1]['kids'].append(node); nodes.append(node); stack.append(node)
            items.append({'t': 'h', 'lvl': min(depth, 4), 'x': f"{key}. {m.group(2)}", 'links': node['refs'], 'node': node})
            continue
        m = re.match(r'^(\d+)\.\s+(.*)$', c)
        body = m.group(2) if m else c
        if is_case(body):
            name, cite, note = split_case(body)
            it = {'t': 'c', 'n': name, 'c': cite, 'note': note, 'node': stack[-1], 'links': []}
            stack[-1]['items'].append(it); items.append(it)
        else:
            r = refs(body)
            stack[-1]['refs'] += r
            items.append({'t': 'r', 'x': body, 'links': r, 'node': stack[-1]})
    # assign cases
    for it in items:
        if it['t'] != 'c':
            continue
        node = it['node']
        tgt = node['refs']
        hop = node
        steps = 0
        while not tgt and hop['parent'] is not None and steps < 2 and not any(i['t'] == 'r' for i in items if i.get('node') is hop):
            hop = hop['parent']; tgt = hop['refs']; steps += 1
        if not tgt:
            k = node['key']
            for rx, lst in CRIM1_DEFAULTS:
                if re.match(rx, k):
                    tgt = [x for x in (link(c, n) for c, n in lst) if x]; it['default'] = True
                    break
        it['links'] = [x for x in tgt if x and x.get('i')][:6]
        it['topic'] = f"{node['key']}. {node['title']}" if node['key'] != 'root' else ''
    for it in items:
        it.pop('node', None)
    return {'id': 'crim1', 'title': 'Criminal Law 1', 'teacher': 'Prof. Rommel Alim Abitria', 'items': items}


# ------------------------------------------------------------------ Crim 2 modules (hand-filed from the module outlines)
def R(*ns):
    return [('rpc', n) for n in ns]


CRIM2 = [
 ('Module 1 — Destroying life; physical injuries; hazing; child abuse; threats; coercion; VAWC', [
  ('Articles 246, 248–251 (Parricide, Murder, Homicide); Articles 255–259 (Infants & Abortion)', R('246', '255', '256', '257', '258', '259'), [
    ('People v. Paycana', 'G.R. No. 179035, April 16, 2008', '')]),
  ('Article 4, par. 2 (Impossible crimes)', R('4'), [('Intod v. Court of Appeals', 'G.R. No. 103119, October 21, 1992, 215 SCRA 53', '')]),
  ('Articles 262–266 (Physical injuries); homicide or murder in the attempted or frustrated stage', R('249', '6', '262', '263', '265', '266'), [
    ('Giovanni Serrano v. People', 'G.R. No. 175023, July 5, 2010', 'intent to kill; compare the RTC and CA rulings'),
    ('Manalo v. People', 'G.R. No. 243805, September 16, 2020', 'optional reading'),
    ('People v. Orlito Villacorta', 'G.R. No. 186412, September 7, 2011', ''),
    ('Ruego v. People', 'G.R. No. 226745, May 3, 2021', '')]),
  ('Anti-Hazing Law (RA 8049, as amended by RA 11053)', [('ra11053', '14')], [('Fuertes v. Senate', 'G.R. No. 208162, January 7, 2020', '')]),
  ('Child abuse (RA 7610)', [('ra7610', '10')], [
    ('Sanchez v. People', 'G.R. No. 179090, June 5, 2009', 'read the information and both versions of the facts'),
    ('Bongalon v. People', 'G.R. No. 169533, March 20, 2013', ''),
    ('Patulot v. People', 'G.R. No. 235071, January 7, 2019', ''),
    ('Talocod v. People', 'G.R. No. 250671, October 7, 2020', ''),
    ('Pascua v. People', 'G.R. No. 240883, April 26, 2023', 'optional reading')]),
  ('Articles 282–285 (Threats)', R('282', '283', '285'), [
    ('Caluag v. People', 'G.R. No. 171511, March 4, 2009', ''), ('Paera v. People', 'G.R. No. 181626, May 30, 2011', '')]),
  ('Articles 286–289 (Coercions)', R('286', '287'), [
    ('People v. Santos', 'G.R. No. 140074, February 27, 2002', 'kidnapping v. coercion'),
    ('People v. Villamar', 'G.R. No. 121175, November 4, 1998', ''), ('People v. Astorga', 'G.R. No. 110097, December 22, 1997', '')]),
  ('RA 9262 — Violence Against Women and Their Children', [('ra9262', '5')], [
    ('Garcia v. RTC Bacolod (Garcia v. Drilon)', 'G.R. No. 179267, June 25, 2013', 'optional reading'),
    ('Melgar v. People', 'G.R. No. 223477, February 14, 2018', '')]),
 ]),
 ('Module 2 — National security; public order; persons in authority; arson; malicious mischief; reckless imprudence', [
  ('Articles 114–121 (Treason, espionage)', R('114', '115', '116', '117'), [
    ('U.S. v. Lagnason', 'G.R. No. 1582, March 28, 1904', ''), ('Laurel v. Misa', 'G.R. No. L-409, January 30, 1947', 'read the dissenting and concurring opinions'),
    ('People v. Adlawan', 'G.R. No. L-456, March 29, 1949, 83 Phil 194', 'complex crimes in the context of treason')]),
  ('Articles 134–142 (Rebellion, insurrection, coup d’état, sedition)', R('134', '134-A', '135', '139', '142'), [
    ('People v. Lovedioro', 'G.R. No. 112235, November 29, 1995', ''),
    ('Gonzales v. Abaya', 'G.R. No. 164007, August 10, 2006', 'gravamen of coup d’état (Callejo concurrence)'),
    ('Espuelas y Mendoza v. People', 'G.R. No. L-2290, December 17, 1951, 90 Phil 524', ''),
    ('People v. Perez', 'G.R. No. 21049, December 22, 1923', ''), ('People v. Umali', 'G.R. No. L-5803, November 29, 1954, 96 Phil 185', '')]),
  ('Articles 146–147 (Illegal assemblies and associations)', R('146', '147'), [
    ('People v. Liwanag', 'G.R. No. L-27683, October 19, 1976', 'subversion'),
    ('Bayan v. Ermita', 'G.R. Nos. 169838, 169848 & 169881', 'optional; compare BP 880 and Art. 131')]),
  ('Articles 143–145 (Crimes against Congress)', R('145'), [('People v. Jalosjos', 'G.R. Nos. 132875-76, February 3, 2000', '')]),
  ('Articles 148–152 (Crimes against persons in authority)', R('148', '152'), [
    ('People v. Recto', 'G.R. No. 129069, October 17, 2001', 'direct assault, first form'),
    ('People v. Uayan', 'G.R. No. 229678, June 20, 2018', 'optional; direct assault with murder'),
    ('Gelig v. People', 'G.R. No. 173150, July 28, 2010', ''), ('Mallari v. People', 'G.R. No. 224679, February 12, 2020', '')]),
  ('Arson (PD 1613, PD 1744), malicious mischief (Arts. 327–331), reckless imprudence (Art. 365)', [('pd1613', '1'), ('rpc', '327'), ('rpc', '365')], [
    ('People v. Bueno', 'G.R. No. L-10849, April 30, 1958', ''), ('Buebos v. People', 'G.R. No. 163938, March 28, 2008', ''),
    ('People v. Gutierrez', 'G.R. No. 100699, July 5, 1996', ''), ('Taguinod v. People', 'G.R. No. 185833, October 12, 2011', 'malicious mischief')]),
 ]),
 ('Module 3 — Crimes by public officers; crimes against constitutional rights', [
  ('Articles 124–127 (arbitrary detention, expulsion); compare Art. 267 (kidnapping) and Art. 269 (unlawful arrest)', R('124', '125', '267', '269'), [
    ('Astorga v. People', 'G.R. No. 154130, October 1, 2003', 'kidnapping v. arbitrary detention'),
    ('Duropan v. People', 'G.R. No. 230825, June 10, 2020', '')]),
  ('Articles 131–133 (peaceful meetings; religious worship)', R('131', '132', '133'), [
    ('People v. Reyes', 'G.R. No. 40577, August 23, 1934, 60 Phil 369', ''),
    ('Celdran v. People', 'G.R. No. 220127, November 21, 2018', 'offending religious feelings'),
    ('People v. Nosce', 'G.R. No. 41757, November 13, 1934', '')]),
  ('Articles 203–245 (crimes in the performance of public functions) and RA 3019', R('203', '210', '217'), [
    ('Guerrero & Carlos v. Judge Villamor', 'A.M. No. RTJ-90-483, September 25, 1998', ''),
    ('Cantos v. People', 'G.R. No. 184908, July 3, 2013', ''),
    ('Tetangco v. Ombudsman', 'G.R. No. 156427, January 20, 2006', ''),
    ('Merencillo v. People', 'G.R. Nos. 142369-70, April 13, 2007', '')]),
  ('RA 3019, Sec. 3(e) and 3(h)', [('ra3019', '3')], [
    ('Feliciano v. People', 'G.R. Nos. 219681-82, March 18, 2021', 'evident bad faith'),
    ('Fuentes v. People', 'G.R. No. 186421, April 17, 2017', 'manifest partiality'),
    ('Cabrera v. People', 'G.R. Nos. 191611-14, July 29, 2019', 'unwarranted advantage'),
    ('Teves v. Sandiganbayan', 'G.R. No. 154182, December 17, 2004', 'prohibited pecuniary interest')]),
 ]),
 ('Module 4 — Taking things: theft, robbery, piracy, trespass to dwelling', [
  ('Theft (Arts. 308–311), carnapping, fencing; robbery (Arts. 293–305); piracy (Arts. 122–123); brigandage (Arts. 306–307)', R('293', '294', '299', '302', '308', '310', '122', '306'), [
    ('People v. Jaranilla', 'G.R. No. L-28547, February 22, 1974', 'casa habitada o lugar no habitado'),
    ('Marquez v. People', 'G.R. No. 181138, December 3, 2012', 'places entered: Arts. 299 and 302'),
    ('People v. Conception', 'G.R. No. 200922, July 18, 2012', 'name as spelled in the syllabus'),
    ('People v. Bustinera', 'G.R. No. 148233, June 8, 2004', ''),
    ('People v. Laurente', 'G.R. No. 116734, March 29, 1996', ''), ('People v. Puno', 'G.R. No. 97471, February 17, 1993', ''),
    ('Viray v. People', 'G.R. No. 205180, November 11, 2013', ''), ('Quinao v. People', 'G.R. No. 139603, July 14, 2000', ''),
    ('People v. Tulin', 'G.R. No. 111709, August 30, 2001', 'piracy: gravamen, territoriality, persons liable'),
    ('People v. Catantan', 'G.R. No. 118075, September 5, 1997', 'piracy; why not grave coercion'),
    ('Sy v. Secretary of Justice', 'G.R. No. 171579, November 14, 2012', ''), ('People v. Tan', 'G.R. No. 135904, January 21, 2000', '')]),
  ('Trespass to dwelling (Arts. 280–281)', R('280', '281'), [
    ('People v. Lamahang', 'G.R. No. 43530, August 3, 1935, 61 Phil 703', ''), ('People v. Tayag', 'G.R. No. L-40512, March 3, 1934', '')]),
 ]),
 ('Module 5 — Honor; decency; adultery and concubinage; illegal marriages', [
  ('Crimes against honor (Arts. 353–362, 364); cyberlibel (RA 10175)', R('353', '354', '355', '358', '360'), [
    ('Guingguing v. Court of Appeals', 'G.R. No. 128959, September 30, 2005', ''), ('Sazon v. Court of Appeals', 'G.R. No. 120715, March 29, 1996', ''),
    ('Fermin v. People', 'G.R. No. 157643, March 28, 2008', ''), ('Alonzo v. Court of Appeals', 'G.R. No. 110088, February 1, 1995', ''),
    ('De Leon v. People', 'G.R. No. 212623, January 11, 2016', ''), ('Villanueva v. People', 'G.R. No. 160351, April 10, 2006', ''),
    ('Trillanes v. Castillo-Marigomen', 'G.R. No. 223451, March 14, 2018', 'libel and parliamentary immunity')]),
 ]),
 ('Module 6 — Rape; acts of lasciviousness; seduction; abduction; trafficking', [
  ('Rape (Art. 266-A; RA 8353; RA 11648)', R('266-A', '266-B'), [
    ('People v. Orita', 'G.R. No. 88724, April 3, 1990, 184 SCRA 105', 'carnal knowledge'),
    ('People v. Jumawan', 'G.R. No. 187495, April 21, 2014', 'marital rape'),
    ('Perez y Agustin v. Court of Appeals', 'G.R. No. 143838, May 9, 2002', 'rape v. acts of lasciviousness'),
    ('People v. Velasquez', 'G.R. No. L-35241, February 28, 1983', 'why the Court ruled “no rape”')]),
  ('Acts of lasciviousness (Art. 336); RA 7610', R('336'), [('De Vera v. People', 'G.R. No. 246231, January 20, 2021', 'lascivious conduct v. unjust vexation; RA 7610')]),
  ('Seduction; abduction (Arts. 337–343)', R('337', '342', '343'), [
    ('People v. Egan', 'G.R. No. 139338, May 28, 2002', 'forcible abduction'), ('People v. Sabredo', 'G.R. No. 126114, May 11, 2000', 'abduction and rape'),
    ('Babanto v. Zosa', 'G.R. No. L-32895, February 28, 1983', 'rape v. seduction')]),
  ('Sexual harassment (RA 7877); Safe Spaces Act (RA 11313)', [('ra7877', '3')], [('Escandor v. People', 'G.R. No. 211962, July 6, 2020', 'sexual harassment')]),
  ('White slave trade (Art. 341); trafficking (RA 9208)', R('341'), [
    ('People v. Estonillo', 'G.R. No. 248694, October 14, 2020', 'trafficking'), ('People v. Nuevas', 'G.R. No. L-154, March 18, 1946', 'white slave trade')]),
  ('Grave scandal (Art. 200); immoral doctrines, obscene publications (Art. 201)', R('200', '201'), [('Madrilejos v. Gatdula', 'G.R. No. 184389, September 24, 2019', '')]),
 ]),
 ('Module 7 — Detention; abandonment; crimes by prisoners', [
  ('Arts. 267–274 (illegal detention)', R('267', '268'), [('People v. Pagalasan', 'G.R. Nos. 131926 & 138991, June 18, 2003', 'serious v. slight illegal detention')]),
  ('Arts. 275–279 (abandonment); compare RA 7610 and PD 603', R('277'), [('De Guzman v. Secretary of Justice', 'G.R. No. 156013, July 25, 2006', '')]),
 ]),
 ('Module 8 — Forgeries; falsification; perjury; estafa; fraudulent insolvency', [
  ('Usurpation of name (CA 142, RA 6085); simulation of birth (Arts. 347–348)', R('178', '347'), [
    ('Ursua v. Court of Appeals', 'G.R. No. 112170, April 10, 1996', 'alias law'), ('Limson v. Gonzales', 'G.R. No. 162205, March 31, 2014', '')]),
  ('Falsification (Arts. 169–172)', R('171', '172'), [
    ('Dava v. People', 'G.R. No. 73905, September 30, 1991', 'public document'),
    ('Layno v. People', 'G.R. No. 93842, September 7, 1992', 'public document; good faith'),
    ('Layug v. Sandiganbayan', 'G.R. Nos. 121047-57, August 16, 2000', 'good faith'),
    ('People v. Po Giok To', 'G.R. No. L-7236, April 30, 1955', 'public v. private document'),
    ('Batulanon v. People', 'G.R. No. 139857, September 15, 2006', 'estafa v. falsification; private document'),
    ('Domingo v. People', 'G.R. No. 186101, October 12, 2009', 'estafa through falsification'),
    ('Fullero v. People', 'G.R. No. 170583, September 12, 2007', 'how falsification was proved'),
    ('Del Prado v. People', 'G.R. No. 186030, March 21, 2012', 'notarized: became a public document')]),
  ('Perjury (Art. 183)', R('183'), [('Union Bank v. People', 'G.R. No. 192565, February 28, 2012', 'perjury')]),
  ('Estafa (Art. 315); BP 22', R('315'), [
    ('Franco v. People', 'G.R. Nos. 171328 & 171335, February 16, 2011', 'estafa'), ('Pamintuan v. People', 'G.R. No. 172820, June 23, 2010', 'estafa'),
    ('Llamas v. Court of Appeals', 'G.R. No. 149588, August 16, 2010', 'estafa'), ('Guinhawa v. People', 'G.R. No. 162822, August 25, 2005', ''),
    ('Galvez v. Court of Appeals', 'G.R. Nos. 187919, 187979 & 188030, February 20, 2013', 'syndicated estafa'),
    ('Ricaforte v. Jurado', 'G.R. No. 154438, September 5, 2007', 'BP 22'), ('People v. Montaner', 'G.R. No. 184053, August 31, 2011', 'estafa through a check')]),
 ]),
]


def crim2():
    items = []
    for mod, topics in CRIM2:
        items.append({'t': 'h', 'lvl': 0, 'x': mod, 'links': []})
        for topic, tg, cases in topics:
            lks = [x for x in (link(c, n) for c, n in tg) if x]
            items.append({'t': 'h', 'lvl': 1, 'x': topic, 'links': lks})
            for n, c, note in cases:
                items.append({'t': 'c', 'n': n, 'c': c, 'note': note, 'topic': topic, 'links': [x for x in lks if x.get('i')]})
    return {'id': 'crim2', 'title': 'Criminal Law 2 (Modules 1–9)', 'teacher': 'Atty. J. M. Pabiton', 'items': items}


# ------------------------------------------------------------------ Ethics and PIL (outline; provision links where the syllabus cites one)
MARKER = re.compile(r'^(?:[ivxlc]{1,6}|[a-zA-Z]|\d{1,3})[.)]\s+|^[-–•*⁃◦▪●]\s*|^(?:PART|Part|Chapter|CHAPTER|Canon|CANON|Section|SECTION|Rule|RULE)\b')


def join_paragraph_lines(raw):
    """For outlines laid out as indented paragraphs: a line that has no outline marker and follows a non-blank
    line continues that line (the PDF wrapped it)."""
    out, prev_blank = [], True
    for l in raw:
        c = clean(l)
        if not c:
            prev_blank = True
            continue
        if out and not prev_blank and not MARKER.match(c):
            out[-1] = out[-1] + ' ' + c
        else:
            out.append(c)
        prev_blank = False
    return out


def parse_plain(fname, cid, title, teacher, default_code='rpc', paragraphs=False):
    raw = open(f'{SYL}/{fname}').read().split('\n')
    lines = join_paragraph_lines(raw) if paragraphs else join_wrapped([clean(l) for l in raw])
    items, topic = [], None
    for l in lines:
        if not l or re.match(r'^(Cases?:?|Other Cases:?)$', l):
            continue
        l2 = re.sub(r'^[-–•]\s*', '', l)
        if is_case(l2) and not re.match(r'^(Canon|Section|Rule)\b', l2):
            name, cite, note = split_case(l2)
            items.append({'t': 'c', 'n': name, 'c': cite, 'note': note, 'topic': topic, 'links': []})
        else:
            r = refs(l2, default_code) if re.search(r'Constitution|Const\.?|R\.?A\.?|Republic Act|Art\.?\s*\d+\s*,\s*S', l2) else []
            lvl = 0 if re.match(r'^(Canon|[A-Z]\.\s|PART|LEGAL ETHICS|JUDICIAL ETHICS|PREAMBLE)', l2) else 1 if re.match(r'^Section\s+\d+', l2) else 2
            items.append({'t': 'h', 'lvl': lvl, 'x': l2[:300], 'links': r})
            topic = l2[:160]
            if r:
                for it in reversed(items[:-1]):
                    if it['t'] == 'h':
                        break
    # cases inherit links of the nearest heading that has links, within the same level-0 block
    cur = []
    for it in items:
        if it['t'] == 'h':
            if it['lvl'] == 0:
                cur = it['links']
            elif it['links']:
                cur = it['links']
        elif it['t'] == 'c' and cur:
            it['links'] = [x for x in cur if x.get('i')]
    return {'id': cid, 'title': title, 'teacher': teacher, 'items': items}


# Cases whose syllabus topic carries no codal reference, filed by what the case actually decides.
# (pattern on the case name, list of targets). Constitution targets use labels ("Art. VII, Sec. 21").
CASE_LINKS = [
    (r'Kuroda', [('const1987', 'Art. II, Sec. 2')]),
    (r'Lantion', [('const1987', 'Art. III, Sec. 1'), ('const1987', 'Art. II, Sec. 2')]),
    (r'Ichong', [('const1987', 'Art. II, Sec. 2')]),
    (r'Pharmaceutical and Health Care Ass', [('const1987', 'Art. II, Sec. 2'), ('milk', '6')]),
    (r'Vinuya', [('const1987', 'Art. II, Sec. 2')]),
    (r'Ta[nñ]ada v\.? Angara', [('const1987', 'Art. II, Sec. 2'), ('const1987', 'Art. VII, Sec. 21')]),
    (r'Pangilinan v\.? Cayetano', [('const1987', 'Art. VII, Sec. 21')]),
    (r'Saguisag', [('const1987', 'Art. XVIII, Sec. 25'), ('const1987', 'Art. VII, Sec. 21')]),
    (r'Bayan v\.? Zamora', [('const1987', 'Art. XVIII, Sec. 25'), ('const1987', 'Art. VII, Sec. 21')]),
    (r'Magallona', [('const1987', 'Art. I')]),
    (r'Philippines v\.? (People.s Republic of )?China', [('const1987', 'Art. I')]),
    (r'Arigo v\.? Swift', [('const1987', 'Art. XVI, Sec. 3')]),
    (r'David v\.? Senate Electoral', [('const1987', 'Art. IV, Sec. 1'), ('const1987', 'Art. IV, Sec. 2')]),
    (r'Poe|^Commission on Elections$', [('const1987', 'Art. IV, Sec. 1'), ('const1987', 'Art. IV, Sec. 2')]),
    (r'Republic v\.? Sandiganbayan', [('const1987', 'Art. III, Sec. 2')]),
    (r'Almonte v\.? People', [('const1987', 'Art. III, Sec. 13')]),
    (r'Calleja v\.? Executive Secretary', [('ra11479', '4'), ('ra11479', '25')]),
    (r'Greenpeace', [('const1987', 'Art. II, Sec. 16')]),
    (r'Southeast Asian Fisheries', [('const1987', 'Art. XVI, Sec. 3')]),
]


# Cases the syllabus files under one section whose doctrine also belongs under another (added, never replacing).
ALSO_LINKS = [
    (r'^Cagang v\.? Sandiganbayan', [('const1987', 'Art. III, Sec. 16')]),
]


def apply_case_links(courses):
    for co in courses:
        for it in co['items']:
            if it['t'] == 'c':
                for rx, tg in ALSO_LINKS:
                    if re.search(rx, it['n']):
                        for c, x in tg:
                            pid = BYLABEL[c].get(x) if c == 'const1987' else (link(c, x) or {}).get('i')
                            if pid and not any(l.get('i') == pid for l in it.get('links', [])):
                                it.setdefault('links', []).append({'c': c, 'i': pid, 'l': x})
    for co in courses:
        for it in co['items']:
            if it['t'] != 'c' or any(lk.get('i') for lk in it.get('links', [])):
                continue
            for rx, tg in CASE_LINKS:
                if re.search(rx, it['n']):
                    lks = []
                    for c, x in tg:
                        if c == 'const1987':
                            pid = BYLABEL[c].get(x)
                            if pid:
                                lks.append({'c': c, 'i': pid, 'l': x})
                        else:
                            lk = link(c, x)
                            if lk and lk.get('i'):
                                lks.append(lk)
                    if lks:
                        it['links'] = lks; it['hand'] = True
                    break


def main():
    courses = [parse_cl2(), parse_crim1(), crim2(),
               parse_plain('2023 Legal and Judicial Ethics Syllabus CPRA.txt', 'ethics', 'Legal and Judicial Ethics (CPRA)', ''),
               parse_plain('public international law.txt', 'pil', 'Public International Law', 'Judge Mary Rocelyn P. Lim-Guillano', paragraphs=True)]
    apply_case_links(courses)
    index = {}
    stats = {}
    for c in courses:
        n = linked = 0
        for it in c['items']:
            if it['t'] != 'c':
                continue
            n += 1
            seen = set(); uniq = []
            for lk in it.get('links', []):
                key = (lk.get('c'), lk.get('i'))
                if key not in seen:
                    seen.add(key); uniq.append(lk)
            it['links'] = uniq
            for lk in it.get('links', []):
                if lk.get('i'):
                    index.setdefault(f"{lk['c']}|{lk['i']}", []).append({'k': c['id'], 'n': it['n'], 'c': it['c'], 'note': it.get('note', ''), 'topic': it.get('topic') or '', 'd': it.get('default', False)})
            if any(lk.get('i') for lk in it.get('links', [])):
                linked += 1
        stats[c['id']] = (n, linked)
    for k in index:
        merged = {}
        for e in index[k]:
            kk = (e['k'], re.sub(r'\W+', '', e['n'].lower()), re.sub(r'\D+', '', e['c'])[:6])
            if kk in merged:
                if e['topic'] and e['topic'] not in merged[kk]['topic']:
                    merged[kk]['topic'] = (merged[kk]['topic'] + ' · ' + e['topic']).strip(' ·')
                merged[kk]['d'] = merged[kk]['d'] and e['d']
            else:
                merged[kk] = dict(e)
        index[k] = list(merged.values())
    json.dump({'courses': courses}, open(f'{SITE}/syllabus.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(index, open(f'{SITE}/syllabus_index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    for k, (n, l) in stats.items():
        print(f'{k}: {n} cases, {l} filed under a provision')
    print('provisions with syllabus cases:', len(index))


if __name__ == '__main__':
    main()
