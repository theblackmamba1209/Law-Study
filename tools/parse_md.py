"""Parse LawCodex Markdown (LawPhil transcriptions) into provision-level JSON.

Text is kept verbatim. Only Markdown syntax is removed (escapes, emphasis markers,
hard-break spaces) and the caption dash is normalised for display.
"""
import re, json, sys, html

PROV_RE = re.compile(
    r'^(?P<kind>Article|ARTICLE|Art\.|ART\.|Section|SECTION|Sec\.|SEC\.|Rule|RULE)\s+'
    r'(?P<num>[0-9]+(?:\s*-\s*[A-Za-z0-9]+)?(?:\.[0-9]+)?[A-Za-z]?|[IVXLC]+(?:-[A-Z])?)\.?\s*$')
HEAD_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
FRONT_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)


def unmd(s):
    s = s.replace(' ', ' ')
    s = re.sub(r'\\([\\`*_{}\[\]()#+\-.!|>~"\'])', r'\1', s)
    s = re.sub(r'(?<![\w*])\*\*(.+?)\*\*(?![\w*])', r'\1', s)
    s = re.sub(r'(?<![\w_])__(.+?)__(?![\w_])', r'\1', s)
    s = re.sub(r'(?<![\w_])_(\S(?:.*?\S)?)_(?![\w_])', r'\1', s)
    s = re.sub(r'(?<![\w*])\*(\S(?:.*?\S)?)\*(?![\w*])', r'\1', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def parse_front(src):
    m = FRONT_RE.match(src)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip().strip('"')
        src = src[m.end():]
    return meta, src


def table_from_md(lines):
    rows = []
    for l in lines:
        l = l.strip()
        if re.match(r'^\|?\s*:?-{2,}', l):
            continue
        cells = [unmd(c) for c in l.strip('|').split('|')]
        rows.append(cells)
    return {'t': 'table', 'rows': rows}


def table_from_html(block):
    rows = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', block, re.S | re.I):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S | re.I)
        rows.append([unmd(html.unescape(re.sub(r'<[^>]+>', ' ', c))) for c in cells])
    return {'t': 'table', 'rows': rows}


def blocks(body_lines):
    """Split body lines into paragraphs and tables."""
    out, buf, i = [], [], 0
    def flush():
        if buf:
            t = unmd(' '.join(x.rstrip() for x in buf))
            if t:
                out.append(t)
            buf.clear()
    while i < len(body_lines):
        l = body_lines[i]
        if l.strip().lower().startswith('<table'):
            flush(); blk = []
            while i < len(body_lines):
                blk.append(body_lines[i])
                if '</table>' in body_lines[i].lower():
                    break
                i += 1
            out.append(table_from_html('\n'.join(blk))); i += 1; continue
        if l.strip().startswith('|') and l.strip().count('|') >= 2:
            flush(); blk = []
            while i < len(body_lines) and body_lines[i].strip().startswith('|'):
                blk.append(body_lines[i]); i += 1
            out.append(table_from_md(blk)); continue
        if not l.strip():
            flush()
        elif l.endswith('  ') or l.endswith('\\'):
            buf.append(l.rstrip('\\ ')); flush()
        else:
            buf.append(l)
        i += 1
    flush()
    return out


CAP_RE = re.compile(r'^(?P<cap>[A-Z“"\'(][^.\n]{1,160}?(?:\.[^.\n—–-]{0,40}?)?)\.\s*(?:[-—–]+|\.-)\s*(?P<rest>\S.*)$', re.S)


def split_caption(first):
    m = CAP_RE.match(first)
    if not m:
        return None, first
    cap = m.group('cap').strip()
    if len(cap.split()) > 18 or cap.lower().startswith(('if ', 'when ', 'the ', 'a ', 'an ', 'any ')) and len(cap.split()) > 8:
        return None, first
    return cap, m.group('rest').strip()


def norm_num(kind, num):
    num = re.sub(r'\s*-\s*', '-', num.strip())
    k = kind.lower().rstrip('.')
    k = {'art': 'article', 'sec': 'section'}.get(k, k)
    return k, num


def parse(path, code_id):
    src = open(path, encoding='utf-8').read()
    meta, src = parse_front(src)
    lines = src.split('\n')
    divisions, provisions, preamble = [], [], []
    stack = []  # (level, div_index)
    cur = None
    cur_lines = []
    title = None

    def close():
        nonlocal cur, cur_lines
        if cur is not None:
            cur['paras'] = blocks(cur_lines)
            provisions.append(cur)
        cur, cur_lines = None, []

    pending_div_text = []
    for raw in lines:
        hm = HEAD_RE.match(raw)
        if hm:
            lvl, text = len(hm.group(1)), unmd(hm.group(2))
            if lvl == 1 and title is None:
                title = text; continue
            pm = PROV_RE.match(text)
            if pm:
                close()
                kind, num = norm_num(pm.group('kind'), pm.group('num'))
                cur = {'kind': kind, 'n': num, 'div': stack[-1][1] if stack else None}
                cur_lines = []
                continue
            # heading that carries its own text (e.g. "PRELIMINARY ARTICLE.-This law ...")
            if re.search(r'\.\s*[-—–]+\s*\S', text) and len(text) > 50 and re.match(r'^[A-Z ]+\.', text):
                close()
                cap, rest = text.split('.', 1)
                cur = {'kind': 'article', 'n': cap.strip().title(), 'div': stack[-1][1] if stack else None,
                       'label': cap.strip().title()}
                cur_lines = [cap.strip() + '.' + rest]
                continue
            close()
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            parent = stack[-1][1] if stack else None
            divisions.append({'t': text, 'lvl': len(stack), 'parent': parent})
            stack.append((lvl, len(divisions) - 1))
            continue
        if cur is not None:
            cur_lines.append(raw)
        elif stack:
            # text directly under a division with no provision heading
            cur = {'kind': 'division-text', 'n': None, 'div': stack[-1][1]}
            cur_lines = [raw]
        else:
            preamble.append(raw)
    close()
    # drop empty division-text provisions
    provisions = [p for p in provisions if p['paras'] or p['kind'] != 'division-text']
    pre = blocks(preamble)
    return meta, title, pre, divisions, provisions


if __name__ == '__main__':
    meta, title, pre, divs, provs = parse(sys.argv[1], 'x')
    print(title, len(divs), len(provs))
    for p in provs[:5]:
        print(json.dumps(p, ensure_ascii=False)[:400])
