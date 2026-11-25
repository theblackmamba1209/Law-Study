import pdfplumber, difflib, collections, json, re, sys
pdf = pdfplumber.open('/home/claude/src/zip/Exec. Order 2009 - The Family Code.pdf')
seed = {')':'a','A':'b','4':'c','2':'d','3':'e','/':'f','?':'g','5':'h','8':'i','O':'j','Y':'k','*':'l','+':'m','9':'n',',':'o','7':'p','C':'q','1':'r','-':'s','.':'t','0':'u','6':'v','>':'w','=':'x','@':'y','U':'z','!':' ','&':'A','I':'.','M':'1','N':'M'}
def page_cipher(pn, font='JVPJFK'):
    p = pdf.pages[pn]
    return ''.join(c['text'] for c in p.chars if font in c['fontname'])
maps = {}
for font in ['JVPJFK', 'VJQSRV', 'ZHEWHQ']:
    votes = collections.defaultdict(collections.Counter)
    m = dict(seed)
    for it in range(3):
        for pn in [1, 2, 3, 10, 15, 25, 30, 45, 58, 59]:
            ocr = open(f'/home/claude/work/ocr/fam/p{pn}.txt').read()
            ocr = re.sub(r'\s+', ' ', ocr)
            ci = page_cipher(pn - 1, font)
            if not ci: continue
            dec = ''.join(m.get(ch, '\x00') for ch in ci)
            sm = difflib.SequenceMatcher(None, dec, ocr, autojunk=False)
            for op, a1, a2, b1, b2 in sm.get_opcodes():
                if op == 'equal':
                    for k in range(a2 - a1): votes[ci[a1 + k]][ocr[b1 + k]] += 1
                elif op == 'replace' and a2 - a1 == b2 - b1:
                    for k in range(a2 - a1): votes[ci[a1 + k]][ocr[b1 + k]] += 1
        m = {k: v.most_common(1)[0][0] for k, v in votes.items()}
        m.update({k: v for k, v in seed.items() if k not in m})
    maps[font] = {k: (v.most_common(3)) for k, v in votes.items()}
json.dump({f: {k: v[0][0] for k, v in mm.items()} for f, mm in maps.items()}, open('/home/claude/work/fam_map.json', 'w'), ensure_ascii=False, indent=0)
for f, mm in maps.items():
    print(f, len(mm))
    print(' '.join(f"{k}>{v[0][0]}({v[0][1]}{'|'+v[1][0]+str(v[1][1]) if len(v)>1 else ''})" for k, v in sorted(mm.items())))
