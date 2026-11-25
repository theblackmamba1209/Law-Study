"""Family Code from the user's PDF. The PDF's fonts carry a scrambled character map, so the
text layer is decoded with a per-font substitution table learned by aligning it to OCR of the
same pages. Decoding is exact wherever the table is complete; any glyph without a mapping is
reported. Paragraph structure comes from the decoded lines."""
import pdfplumber, difflib, collections, json, re, glob, os
PDF = '/home/claude/src/zip/Exec. Order 2009 - The Family Code.pdf'
pdf = pdfplumber.open(PDF)
OCR = {int(re.search(r'p(\d+)\.txt', f).group(1)): open(f).read() for f in glob.glob('/home/claude/work/ocr/famfull/p*.txt')}
fonts = ['JVPJFK', 'VJQSRV', 'ZHEWHQ']
seed = json.load(open('/home/claude/work/fam_map.json'))['JVPJFK']
maps = {}
for font in fonts:
    m = dict(seed)
    for it in range(4):
        votes = collections.defaultdict(collections.Counter)
        for pn, p in enumerate(pdf.pages, 1):
            ocr = re.sub(r'\s+', ' ', OCR.get(pn, ''))
            ci = ''.join(c['text'] for c in p.chars if font in c['fontname'])
            if not ci or not ocr: continue
            dec = ''.join(m.get(ch, '\x00') for ch in ci)
            sm = difflib.SequenceMatcher(None, dec, ocr, autojunk=False)
            for op, a1, a2, b1, b2 in sm.get_opcodes():
                if op in ('equal', 'replace') and a2 - a1 == b2 - b1:
                    for k in range(a2 - a1):
                        votes[ci[a1 + k]][ocr[b1 + k]] += 1
        m = {k: v.most_common(1)[0][0] for k, v in votes.items() if v}
        if font == 'JVPJFK':
            for k, v in seed.items(): m.setdefault(k, v)
    maps[font] = m
json.dump(maps, open('/home/claude/work/fam_maps_all.json', 'w'), ensure_ascii=False, indent=0)
# decode, line by line with x positions
unk = collections.Counter()
lines = []
for pn, p in enumerate(pdf.pages, 1):
    chars = sorted(p.chars, key=lambda c: (round(c['top']), c['x0']))
    rows = collections.OrderedDict()
    for c in chars:
        key = round(c['top'] / 3)
        rows.setdefault(key, []).append(c)
    for key in sorted(rows):
        cs = sorted(rows[key], key=lambda c: c['x0'])
        s = ''
        for c in cs:
            f = next((x for x in fonts if x in c['fontname']), None)
            ch = maps.get(f, {}).get(c['text'])
            if ch is None:
                unk[(f, c['text'])] += 1; ch = '⁇'
            s += ch
        lines.append((pn, cs[0]['x0'], s, any('Bold' in c['fontname'] for c in cs)))
print('unknown glyphs', unk.most_common(20))
json.dump(lines, open('/home/claude/work/fam_lines.json', 'w'), ensure_ascii=False)
for l in lines[:60]: print(l[0], round(l[1]), l[3], l[2][:110])
