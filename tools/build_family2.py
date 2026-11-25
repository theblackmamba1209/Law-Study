import pdfplumber, difflib, collections, json, re, glob
PDF = '/home/claude/src/zip/Exec. Order 2009 - The Family Code.pdf'
pdf = pdfplumber.open(PDF)
OCR = {int(re.search(r'p(\d+)\.txt', f).group(1)): open(f).read() for f in glob.glob('/home/claude/work/ocr/famfull/p*.txt')}
maps = json.load(open('/home/claude/work/fam_maps_all.json'))
REG = 'JVPJFK'
fontkey = lambda fn: next((x for x in ['JVPJFK', 'VJQSRV', 'ZHEWHQ'] if x in fn), None)

def page_lines(p):
    rows = collections.defaultdict(list)
    for c in p.chars:
        rows[round(c['top'] / 3)].append(c)
    out = []
    for key in sorted(rows):
        cs = sorted(rows[key], key=lambda c: c['x0'])
        seq = []  # (font, glyph or ' ')
        prev = None
        for c in cs:
            if prev is not None and c['x0'] - prev['x1'] > 0.22 * c['size']:
                seq.append((None, ' '))
            seq.append((fontkey(c['fontname']), c['text']))
            prev = c
        out.append((cs[0]['x0'], seq, any('Bold' in c['fontname'] for c in cs)))
    return out

def decode(seq, m):
    return ''.join(g if f is None else m[f].get(g, '\x00') for f, g in seq)

votes = {f: collections.defaultdict(collections.Counter) for f in ['VJQSRV', 'ZHEWHQ']}
m = {'JVPJFK': maps['JVPJFK'], 'VJQSRV': {}, 'ZHEWHQ': {}}
for it in range(3):
    for f in votes: votes[f].clear()
    for pn, p in enumerate(pdf.pages, 1):
        lines = page_lines(p)
        seqs = [s for _, s, _ in lines]
        flat = []
        for s in seqs:
            flat += s + [(None, ' ')]
        dec = decode(flat, m)
        dec_n = re.sub(' +', ' ', dec)
        # keep a mapping from dec_n index to flat index
        idx = []; outc = []; last_space = False
        for i, ch in enumerate(dec):
            if ch == ' ':
                if last_space: continue
                last_space = True
            else: last_space = False
            idx.append(i); outc.append(ch)
        ocr = re.sub(r'\s+', ' ', OCR.get(pn, ''))
        sm = difflib.SequenceMatcher(None, ''.join(outc), ocr, autojunk=False)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op in ('replace', 'equal'):
                A = [flat[idx[k]] for k in range(a1, a2)]
                B = ocr[b1:b2]
                Ag = [x for x in A if x[0] in votes]
                if not Ag: continue
                if len(A) == len(B):
                    for (f, g), o in zip(A, B):
                        if f in votes: votes[f][g][o] += 1
                else:
                    # compare ignoring spaces
                    A2 = [x for x in A if x[1] != ' ' or x[0] is not None]
                    B2 = B.replace(' ', '')
                    A3 = [x for x in A2 if not (x[0] is None)]
                    if len(A3) == len(B2):
                        for (f, g), o in zip(A3, B2):
                            if f in votes: votes[f][g][o] += 1
    for f in votes:
        m[f] = {g: c.most_common(1)[0][0] for g, c in votes[f].items()}
json.dump(m, open('/home/claude/work/fam_maps_all.json', 'w'), ensure_ascii=False)
for f in votes:
    print(f, len(m[f]), {g: c.most_common(2) for g, c in votes[f].items() if c.most_common(1)[0][1] < 3})
# decode all
unk = collections.Counter(); out = []
for pn, p in enumerate(pdf.pages, 1):
    for x0, seq, bold in page_lines(p):
        s = ''
        for f, g in seq:
            if f is None: s += g; continue
            ch = m[f].get(g)
            if ch is None: unk[(f, g)] += 1; ch = '⁇'
            s += ch
        out.append((pn, round(x0), bold, s.rstrip()))
print('unknown', unk.most_common())
json.dump(out, open('/home/claude/work/fam_lines.json', 'w'), ensure_ascii=False)
for l in out[:40]: print(l)
