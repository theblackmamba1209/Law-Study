"""File 2023–2025 Supreme Court decisions under the CPRA sections they apply.

Input: decision texts (as published on LawPhil) in a public corpus, github.com/GabLettub/ph-jurisprudence-chatbot,
read as data only. For each decision that cites the CPRA we extract, mechanically: the parties, docket, date, division,
ponente, the CPRA sections cited, and the penalty in the dispositive portion. Nothing is paraphrased from the opinion;
the one-line summary is assembled from those facts.

Output: tools/cpra_cases.json, merged into data/recent.json by recent_data.py.
Run with:  python3 -I cpra_cases.py
"""
import re, os, json, glob

CORPUS = '/home/claude/gablettub/ph-jurisprudence-chatbot/2020-2025'
OUT = '/home/claude/tools/cpra_cases.json'
CPRA = json.load(open('/home/claude/site/data/codes/cpra.json'))
PIDS = {p['i'] for p in CPRA['provisions']}
ROM = {'I': 'i', 'II': 'ii', 'III': 'iii', 'IV': 'iv', 'V': 'v', 'VI': 'vi'}
NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12}


def title_case(s):
    s = s.replace('*', '')
    small = {'and', 'of', 'the', 'in', 're:', 'for', 'de', 'del', 'dela', 'la'}
    out = []
    for w in s.split():
        lw = w.lower()
        out.append(lw if lw in small and out else (w if re.match(r'^[A-Z]\.$|^[IVX]+,?$|^(Jr|Sr)\.?,?$', w) else '-'.join(x[:1].upper() + x[1:].lower() for x in w.split('-'))))
    return ' '.join(out).replace(' Vs. ', ' v. ').replace(' vs. ', ' v. ')


def parties(line):
    line = re.sub(r'\s+', ' ', line).strip()
    m = re.match(r'^(.*?),\s*(?:COMPLAINANTS?|PETITIONERS?)\b.*?\b(?:VS?\.|VERSUS)\s*(.*?),\s*(?:RESPONDENTS?)\b', line)
    if not m:
        return title_case(line[:120])
    a, b = m.group(1), m.group(2)
    a = re.split(r',| AND ', a)[0]
    if re.search(r'\bATTY\.', b):
        b = 'Atty. ' + b.split('ATTY.')[1].split(',')[0].strip()
    else:
        b = re.split(r',| AND ', b)[0]
    return f'{title_case(a.strip())} v. {title_case(b.strip()).replace("Atty. Atty.", "Atty.")}'


def cited(text):
    hits = set()
    for m in re.finditer(r'Sections?\s+((?:\d+(?:\s*\([a-z]\))?(?:\s*,\s*|\s+and\s+|\s*&\s*)?)+)\s*(?:,|of)\s*Canon\s+(I{1,3}|IV|VI?|V)\b', text):
        for n in re.findall(r'\d+', m.group(1)):
            hits.add((m.group(2), n))
    for m in re.finditer(r'Canon\s+(I{1,3}|IV|VI?|V)\s*,?\s*Sections?\s+(\d+)', text):
        hits.add((m.group(1), m.group(2)))
    out = []
    for c, n in sorted(hits, key=lambda x: (list(ROM).index(x[0]), int(x[1]))):
        pid = f'canon-{ROM[c]}-sec-{n}'
        if pid in PIDS:
            out.append((pid, f'Canon {c}, Sec. {n}'))
    return out


def disposition(text):
    k = text.rfind('WHEREFORE')
    if k < 0:
        k = text.rfind('ACCORDINGLY')
    if k < 0:
        return ''
    d = re.sub(r'\s+', ' ', text[k:k + 2500])
    d = d.split('SO ORDERED')[0]
    if re.search(r'\bDISBARRED\b|\bDISBARMENT\b', d) and not re.search(r'dismiss(ed)? the (complaint|petition) for disbarment', d, re.I):
        out = 'Disbarred'
    else:
        m = re.search(r'SUSPENDED from the practice of law for (?:a period of )?(\w+)\s*(?:\((\d+)\))?\s*(years?|months?)', d, re.I)
        if m:
            n = m.group(2) or str(NUMW.get(m.group(1).lower(), m.group(1)))
            out = f'Suspended from practice for {n} {m.group(3).lower()}'
        elif re.search(r'\bFINED?\b|\bfine of\b', d, re.I):
            m = re.search(r'(?:\bFINED?\b|\bfine of\b)[^.]{0,80}?(?:PHP|P|₱)\s?([\d,]{4,})', d, re.I)
            out = f'Fined PHP {m.group(1)}' if m else 'Fined'
        elif re.search(r'\bREPRIMANDED?\b', d, re.I):
            out = 'Reprimanded'
        elif re.search(r'\bADMONISHED\b|\bWARNED\b|\bSTERNLY WARNED\b', d, re.I):
            out = 'Admonished or warned'
        elif re.search(r'\bDISMISSED\b', d):
            out = 'Complaint dismissed'
        else:
            out = ''
    extras = []
    if re.search(r'revok', d, re.I) and re.search(r'notarial commission', d, re.I):
        extras.append('notarial commission revoked')
    if re.search(r'disqualified from being commissioned', d, re.I):
        extras.append('barred from notarial commission')
    if re.search(r'(return|restitute|pay).{0,80}(complainant)', d, re.I):
        extras.append('ordered to return money to the complainant')
    return out + ('; ' + ', '.join(extras) if extras and out else (', '.join(extras).capitalize() if extras else ''))


def main():
    rows = []
    for f in sorted(glob.glob(CORPUS + '/202[3-5]/*.txt')):
        t = open(f, encoding='utf-8', errors='ignore').read()
        t = re.sub(r'([a-z,.])([A-Z]{3,})', r'\1 \2', t)
        t = re.sub(r'([A-Z]{3,})([a-z])', lambda m: m.group(1) + ' ' + m.group(2) if m.group(1) not in ('ATTY', 'SPS') else m.group(0), t)
        if 'Code of Professional Responsibility and Accountability' not in t and 'CPRA' not in t:
            continue
        cits = cited(t)
        if not cits:
            continue
        head = t[:6000]
        url = (re.search(r'^URL:\s*(\S+)', head, re.M) or [None, ''])[1]
        date = (re.search(r'^Date:\s*(.+)$', head, re.M) or [None, ''])[1].strip()
        docket = (re.search(r'^Title:\s*(.+)$', head, re.M) or [None, ''])[1].strip()
        lines = head.split('\n')
        bi = next((i for i, x in enumerate(lines) if x.startswith('[') and re.search(r'\d{4}\s*\]\s*$', x)), None)
        div = (re.search(r'^(EN BANC|FIRST DIVISION|SECOND DIVISION|THIRD DIVISION)\s*$', head, re.M) or [None, ''])[1]
        pon = re.search(r'^([A-Z][A-Z\-Ñ .]+?),\s*(?:C\.?\s*)?J\.?\s*:', head, re.M)
        pon = title_case(pon.group(1).strip()) + ', J.' if pon else ('Per curiam' if 'PER CURIAM' in head.upper() else '')
        pl = next((x for x in lines[bi + 1:bi + 4] if x.strip()), '') if bi is not None else ''
        name = parties(pl) if pl else docket
        name = re.sub(r',?\s*Represented By [^,]+,?\s*Complainants?,\s*', ' v. ', name)
        name = re.sub(r',\s*Complainants?,\s*', ' v. ', name)
        if not name.strip(' v.'):
            name = title_case(re.sub(r'\s+', ' ', pl)[:110]) or docket
        disp = disposition(t)
        rows.append({'n': name, 'g': docket, 'd': date, 'ct': ' · '.join(x for x in ['Supreme Court ' + div.title() if div else 'Supreme Court', pon] if x),
                     'disp': disp, 'cits': cits, 'u': url})
    by = {}
    for r in rows:
        labels = [l for _, l in r['cits']]
        for pid, lab in r['cits']:
            others = [l for l in labels if l != lab]
            h = ('Outcome: ' + r['disp'] + '.') if r['disp'] else 'Outcome: see the dispositive portion of the decision.'
            rel = f'Applies {lab} of the CPRA' + (f', with {", ".join(others[:4])}' + (' and others' if len(others) > 4 else '') if others else '') + '.'
            by.setdefault('cpra|' + pid, []).append({'n': r['n'], 'g': r['g'], 'd': r['d'], 'ct': r['ct'], 'h': h, 'rel': rel, 'st': 'decision',
                                                     'src': [{'t': 'Full text (LawPhil)', 'u': r['u']}] if r['u'] else [], 'tags': ['CPRA', 'ethics']})
    import datetime

    def key(e):
        try:
            return datetime.datetime.strptime(e['d'].replace('  ', ' '), '%B %d, %Y')
        except Exception:
            return datetime.datetime(2000, 1, 1)
    for k in by:
        by[k].sort(key=key, reverse=True)
        by[k] = by[k][:8]
    json.dump(by, open(OUT, 'w'), ensure_ascii=False, indent=0)
    print('decisions applying the CPRA:', len(rows), '| sections with cases:', len(by))
    from collections import Counter
    print(Counter(r['disp'].split(';')[0] for r in rows).most_common())
    for r in rows[:6]:
        print(' ', r['n'], '|', r['g'], '|', r['d'], '|', r['ct'], '|', r['disp'], '|', [l for _, l in r['cits']][:5])


if __name__ == '__main__':
    main()
