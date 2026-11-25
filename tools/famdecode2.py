import pdfplumber, json, collections, re
pdf = pdfplumber.open('/home/claude/src/zip/Exec. Order 2009 - The Family Code.pdf')
m = json.load(open('/home/claude/work/fam_map.json'))['JVPJFK']
cnt = collections.Counter(); ctx = collections.defaultdict(list)
for pn, p in enumerate(pdf.pages):
    s = ''.join(c['text'] for c in p.chars)
    for i, ch in enumerate(s):
        if ch not in m:
            cnt[ch] += 1
            if len(ctx[ch]) < 4:
                ctx[ch].append(''.join(m.get(x, '¤') for x in s[max(0, i-25):i+15]))
for ch, n in cnt.most_common():
    print(repr(ch), n, ctx[ch])
