import pdfplumber, re, json, sys
pdf = pdfplumber.open('/home/claude/src/zip/Labor Code renumbered.pdf')
body_pages, fn_pages = [], []
def mark(objs, kind):
    out = []
    for c in objs:
        c = dict(c)
        s = c.get('size', 0)
        if kind == 'body' and 5.8 <= s <= 7.0 and c['text'].strip():
            c['text'] = '⟨' + c['text'] + '⟩'
        if kind == 'fn' and s < 4.5 and c['text'].strip():
            c['text'] = '⟪' + c['text'] + '⟫'
        out.append(c)
    return out
for i, p in enumerate(pdf.pages):
    chars = p.chars
    body = [c for c in chars if c['size'] >= 8.9 or (5.8 <= c['size'] <= 7.0)]
    fn = [c for c in chars if 3.0 <= c['size'] < 5.8]
    # page numbers at 8.0 are excluded (size<8.9)
    from pdfplumber.utils import extract_text
    bt = extract_text(mark(body, "body"), layout=True, x_density=5.5, y_density=13, x_tolerance=1.5, y_tolerance=3, layout_width_chars=200, layout_height=0)
    ft = extract_text(mark(fn, 'fn'), layout=False, x_tolerance=1.0, y_tolerance=2)
    bt = bt.replace('⟩⟨', '')
    ft = ft.replace('⟫⟪', '')
    body_pages.append(bt); fn_pages.append(ft)
json.dump({'body': body_pages, 'fn': fn_pages}, open('/home/claude/work/labor/pages.json', 'w'))
print(len(body_pages))
