"""Labor Code (PD 442, as amended and renumbered) from the DOLE 2022 edition PDF.
Body text, footnote markers and footnotes are separated by font size (see extract_labor.py).
Paragraphs are detected by first-line indentation."""
import json, re

d = json.load(open('/home/claude/work/labor/pages.json'))
HEAD = re.compile(r'^(PRELIMINARY\s+TITLE|(?:Book|BOOK)\s+(?:One|Two|Three|Four|Five|Six|Seven|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN)|(?:Title|TITLE)\s+[IVX]+(?:-A)?|(?:Chapter|CHAPTER)\s+[IVX]+)(?:⟨\d+⟩|\d{1,3})?\s*(?:[-–]\s*[A-Z][A-Z ,\-’]*(?:⟨\d+⟩|\d{1,3})?)?$')
PROV = re.compile(r'^ART\.\s*(\d+(?:-[A-Z])?)\.\s*(?:\[([\d\-A-Za-z, ]+)\]\s*)?(.*)$')
FN = re.compile(r'⟪(\d+)⟫\s*')

def clean(s):
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s

# footnotes
footnotes = {}
for ft in d['fn']:
    ft = ft.replace('\n', ' ')
    parts = FN.split(ft)
    for i in range(1, len(parts) - 1, 2):
        footnotes[int(parts[i])] = clean(parts[i + 1])

# body lines from page 12 (index) onwards
lines = []
for pi in range(12, len(d['body'])):
    for raw in d['body'][pi].split('\n'):
        if not raw.strip():
            continue
        lead = len(raw) - len(raw.lstrip(' '))
        lines.append((lead, raw.rstrip(), pi + 1))

paras = []  # (kind, text, page)
for lead, raw, pg in lines:
    s = clean(raw)
    if HEAD.match(s) and not PROV.match(s) and len(s) < 140:
        paras.append(['H', s, pg]); continue
    if paras and paras[-1][0] == 'H' and re.sub(r'⟨\d+⟩|\d', '', s).isupper() and not PROV.match(s) and len(s) < 90:
        paras[-1][1] += ' ' + s; continue   # wrapped heading
    if lead >= 2 or not paras or paras[-1][0] == 'H':
        paras.append(['P', s, pg])
    else:
        prev = paras[-1][1]
        if prev.endswith('-') and not prev.endswith(' -') and re.search(r'[a-z]-$', prev) and s[:1].islower():
            paras[-1][1] = prev + s   # hyphenated line break inside a word? keep hyphen (compound words are common)
            paras[-1][1] = prev + s
        else:
            paras[-1][1] = prev + ' ' + s

LEVEL = {'preliminary': 1, 'book': 0, 'title': 1, 'chapter': 2}
divisions, provisions = [], []
stack = []
cur = None
for kind, text, pg in paras:
    if kind == 'H':
        hfn = [int(x) for x in re.findall(r'⟨(\d+)⟩', text)]
        mm = re.search(r'(?<=[A-Z])(\d{1,3})$', text)
        if mm and int(mm.group(1)) in footnotes:
            hfn.append(int(mm.group(1))); text = text[:mm.start()]
        text = re.sub(r'⟨\d+⟩', '', text)
        t = re.sub(r'\s+[-–]\s+', ' — ', text, count=1)
        key = text.split()[0].lower()
        lvl = LEVEL.get(key, 2)
        while stack and divisions[stack[-1]]['lvl'] >= lvl:
            stack.pop()
        divisions.append({'t': t.upper() if key in ('book', 'title', 'preliminary') else t, 'lvl': lvl,
                          'parent': stack[-1] if stack else None})
        if hfn: divisions[-1]['fn'] = [{'n': n, 't': footnotes[n]} for n in hfn if n in footnotes]
        stack.append(len(divisions) - 1)
        continue
    m = PROV.match(text)
    if m:
        cur = {'kind': 'article', 'n': m.group(1), 'old': m.group(2), 'div': stack[-1] if stack else None,
               'paras': [m.group(3)], 'page': pg}
        provisions.append(cur)
    elif cur is not None:
        cur['paras'].append(text)

# attach footnotes
for p in provisions:
    fns = []
    newp = []
    for para in p['paras']:
        for m in re.finditer(r'⟨(\d+)⟩', para):
            n = int(m.group(1))
            if n in footnotes:
                fns.append({'n': n, 't': footnotes[n]})
        newp.append(re.sub(r'\s*⟨(\d+)⟩', lambda m: '⟨' + m.group(1) + '⟩', para))
    p['paras'] = newp
    if fns:
        p['fn'] = fns

# caption split: "Name of Decree. – This decree ..."
for p in provisions:
    first = p['paras'][0]
    m = re.match(r'^(.{2,180}?)\.(⟨\d+⟩)?\s+[–—-]\s+(.*)$', first)
    if m:
        p['cap'] = m.group(1).strip()
        p['capfn'] = m.group(2)
        p['paras'][0] = m.group(3)

out = {'divisions': divisions, 'provisions': provisions, 'footnotes_total': len(footnotes)}
json.dump(out, open('/home/claude/work/labor/labor.json', 'w'), ensure_ascii=False, indent=1)
nums = [int(re.match(r'\d+', p['n']).group()) for p in provisions]
missing = [i for i in range(1, max(nums) + 1) if i not in nums]
print('divisions', len(divisions), 'provisions', len(provisions), 'max', max(nums), 'missing', missing,
      'dups', [n for n in set(nums) if nums.count(n) > 1], 'footnotes', len(footnotes),
      'attached', sum(len(p.get('fn', [])) for p in provisions))
