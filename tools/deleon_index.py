"""De Leon, Obligations and Contracts: (1) the codal text it prints, for cross-checking the Civil Code;
(2) an index of every case it cites, keyed to the article under discussion, with the book page."""
import re, json, difflib
pages = open('/home/claude/work/deleon/deleon.txt').read().split('\f')
ART = re.compile(r'^\s{4,}ART(?:ICLE)?\.\s*(\d{3,4})\.\s*(.*)$')
codal = {}
cases = []
cur_art = None
CITE = re.compile(r'([A-Z][A-Za-z0-9.,&\'’\- ]{2,80}?\s+(?:vs\.|v\.)\s+[A-Za-z0-9.,&\'’\-() ]{2,90}?),\s*((?:G\.R\.\s*No[s]?\.\s*[\dL\-–, &]+(?:,\s*[A-Z][a-z]+\.?\s*\d{1,2},\s*\d{4})?)|(?:\d{1,4}\s+(?:SCRA|Phil\.|O\.G\.|Phil)\s+\d{1,5}(?:\s*\[\d{4}\])?))')
for pi, pg in enumerate(pages):
    lines = pg.split('\n')
    i = 0
    while i < len(lines):
        m = ART.match(lines[i])
        if m and len(lines[i]) - len(lines[i].lstrip()) >= 6:
            n = m.group(1); buf = [m.group(2)]
            j = i + 1
            while j < len(lines) and lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) >= 4:
                buf.append(lines[j].strip()); j += 1
            txt = ' '.join(buf)
            txt = re.sub(r'(\w)- (\w)', r'\1\2', txt)
            if n not in codal: codal[n] = {'t': txt, 'page': pi + 1}
            cur_art = n; i = j; continue
        i += 1
    if cur_art is None: continue
    flat = re.sub(r'-\n\s*', '', pg)
    flat = re.sub(r'\s+', ' ', flat)
    # track article boundaries inside the page
    pos_art = [(m.start(), m.group(1)) for m in re.finditer(r'ART\.\s*(\d{3,4})\.', flat)]
    for m in CITE.finditer(flat):
        art = cur_art
        before = [a for p, a in pos_art if p < m.start()]
        if before: art = before[-1]
        else:
            # first ART on this page may come later; the page belongs to previous article
            pass
        name = re.sub(r'^(?:See|see|In|in|Thus,|also|Also|cf\.|and)\s+', '', m.group(1).strip(' (;'))
        name = re.sub(r'^.*?\(\s*', '', name) if '(' in name[:5] else name
        cases.append({'art': art, 'name': name.strip(), 'cite': m.group(2).strip(), 'page': pi + 1})
json.dump({'codal': codal, 'cases': cases}, open('/home/claude/work/deleon/deleon_index.json', 'w'), ensure_ascii=False, indent=0)
print('codal articles', len(codal), 'case cites', len(cases), 'unique', len({c['name'] for c in cases}))
print(sorted(codal, key=int)[:5], sorted(codal, key=int)[-5:])
for c in cases[:15]: print(c)
