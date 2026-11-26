"""Supreme Court issuances added to the library: the CPRA (with the Revised Lawyer's Oath),
the 2004 Rules on Notarial Practice, and the 2020 Rules on Remote Notarization.
(Rule 140 is left out: the only transcription found mixes the rule with a transcriber's case annotations.)

Source: the transcriptions published by Justitia, the law journal of the University of Makati School of Law
(github.com/limnestor/justitia), which reproduce the Supreme Court's PDFs. The texts are works of the Government
(RA 8293, Sec. 176.1). OCR slips in those transcriptions are corrected here word by word, and every correction is logged
in data/proofreading.json.

Run after build_data.py (it rewrites the catalog); build_data.py calls this at the end.
"""
import re, json, html, hashlib, os, sys

SRC = '/home/claude/limnestor/justitia'
OUT = '/home/claude/site/data'
WORDS = set()


def dic():
    if WORDS:
        return WORDS
    for line in open('/usr/share/hunspell/en_US.dic', encoding='latin-1').read().split('\n')[1:]:
        w = line.split('/')[0].strip().lower()
        if w:
            WORDS.add(w)
    for f in os.listdir(OUT + '/codes'):
        if f in ('cpra.json', 'notarial.json', 'remotenot.json', 'rule140.json'):
            continue
        d = json.load(open(OUT + '/codes/' + f))
        for p in d['provisions']:
            for x in p['p']:
                if isinstance(x, str):
                    for w in re.findall(r"[A-Za-z]+", x):
                        WORDS.add(w.lower())
    WORDS.update({'disbar', 'disbarred', 'disbarment', 'videoconference', 'videoconferences', 'reproof', 'lalamove', 'cpra', 'ibp', 'mcle', 'ulas', 'pao', 'cle', 'cjca', 'jib', 'oca', 'odesc', 'efiling', 'videoconferencing',
                  'lifelong', 'paralegal', 'paralegals', 'notarial', 'notarized', 'notarization', 'notary', 'notaries', 'proforma',
                  'pro', 'bono', 'gender-fair', 'harassment', 'online', 'email', 'emails', 'social', 'media', 'deepfake'})
    return WORDS


def paras(fn):
    t = open(f'{SRC}/{fn}', encoding='utf-8').read()
    b = t[t.find('<body'):]
    out = []
    for m in re.finditer(r'<(p|h[1-6]|li|td)\b[^>]*>(.*?)</\1>', b, re.S):
        inner = m.group(2)
        x = re.sub(r'<[^>]+>', '', inner)
        x = html.unescape(x).replace(' ', ' ')
        x = re.sub(r'\s+', ' ', x).strip()
        if x:
            out.append((m.group(1), '<b' in inner, x))
    # drop the journal's footer
    for k, (tag, bo, x) in enumerate(out):
        if x.startswith('Justitia is the official law journal'):
            out = out[:k]
            break
    return out


def paras_lines(fn):
    """Line-based reader for pages whose sections are not wrapped in <p>: block ends and <br> become line breaks,
    and a line is split again wherever an upper-case SECTION/SEC. heading starts inside it."""
    t = open(f'{SRC}/{fn}', encoding='utf-8').read()
    b = t[t.find('<body'):]
    b = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b)
    b = re.sub(r'(?i)<br\s*/?>', '\n', b)
    b = re.sub(r'(?i)</(p|div|h[1-6]|li|tr|td|blockquote)>', '\n', b)
    b = html.unescape(re.sub(r'<[^>]+>', ' ', b)).replace('\u00a0', ' ')
    pieces = []
    for line in b.split('\n'):
        line = re.sub(r'\s+', ' ', line).strip()
        if not line:
            continue
        if line.startswith('Justitia is the official law journal'):
            break
        for piece in re.split(r'(?<=\S)\s+(?=(?:SECTION|SEC\.)\s*\d+\s*\.)', line):
            if piece.strip():
                pieces.append(piece.strip())
    # rejoin visual line-wraps: start a new paragraph only at structure
    STRUCT = re.compile(r'^(?:SECTION|SEC\.|Section|Sec\.)\s*\d+\s*\.|^(?:BOOK|RULE|TITLE|CHAPTER|PART|ARTICLE)\b|^\(?[a-z0-9]{1,3}[.)]\s|^\([ivx]+\)\s')
    out, buf = [], ''
    for x in pieces:
        if not buf or STRUCT.match(x) or (x.isupper() and len(x) < 120) or (buf.isupper() and len(buf) < 120):
            if buf:
                out.append(('p', buf.isupper(), buf))
            buf = x
        else:
            buf += ' ' + x
    if buf:
        out.append(('p', buf.isupper(), buf))
    return out


LOG = []


def fix_words(x, where):
    """Correct OCR slips: run-together words, rn/m confusions, a space before an apostrophe, a hyphen for a space."""
    W = dic()
    orig = x
    x = re.sub(r"(\w) 's\b", r"\1's", x)
    x = re.sub(r'^\((l l|ll)\)', '(11)', x)
    x = re.sub(r'^\(l\)', '(1)', x)
    x = re.sub(r'\bj ust\b', 'just', x)
    x = re.sub(r'\b(one|One) \(l\)', r'\1 (1)', x)
    x = x.replace('govemment', 'government').replace('Govemment', 'Government')

    GLUE = ('of', 'for', 'the', 'and')
    HYPH = ('self', 'non', 'anti', 'award', 'fact', 'lawyer', 'cross')
    SUFW = {'ship', 'hood', 'ness', 'less', 'ment', 'able', 'wide', 'like', 'work', 'side', 'ward', 'wise', 'fold', 'ing', 'ings'}
    FIX = {'urisprudence': 'jurisprudence', 'anewspaper': 'a newspaper', 'tlae': 'the', 'statenwnts': 'statements', 'ofthe': 'of the', 'offees': 'of fees', 'ofprivileged': 'of privileged'}

    def known(lw):
        if lw in W:
            return True
        for suf in ('s', 'es', 'ed', 'd', 'ing', 'ings', 'ly', 'ies', 'ment', 'ments', 'ation', 'er', 'ers'):
            if lw.endswith(suf) and len(lw) - len(suf) >= 4 and (lw[:-len(suf)] in W or lw[:-len(suf)] + 'e' in W or lw[:-len(suf)] + 'y' in W):
                return True
        return False

    def split_tok(m):
        w = m.group(0)
        lw = w.lower()
        if lw in FIX:
            return FIX[lw] if w.islower() else FIX[lw].capitalize()
        if lw in FIX:
            return FIX[lw] if w[0].islower() else FIX[lw][0].upper() + FIX[lw][1:]
        if known(lw) or len(w) < 5:
            return w
        if 'vv' in lw and known(lw.replace('vv', 'w')):
            return w.replace('vv', 'w')
        if 'rn' in lw and known(lw.replace('rn', 'm')):
            return w.replace('rn', 'm')
        camel = bool(re.search(r'[a-z][A-Z]', w))
        for g in GLUE:   # "ofjustice", "Remedyfor"
            if lw.startswith(g) and len(lw) - len(g) >= 3 and known(lw[len(g):]):
                return w[:len(g)] + ' ' + w[len(g):]
            if lw.endswith(g) and len(lw) - len(g) >= 4 and known(lw[:-len(g)]):
                return w[:-len(g)] + ' ' + w[-len(g):]
        for h in HYPH:   # a dropped hyphen: "selfaggrandizement", "factfinding"
            if lw.startswith(h) and len(lw) - len(h) >= 4 and known(lw[len(h):]):
                return w[:len(h)] + '-' + w[len(h):]
        for k in range(4, len(w) - 3):   # two content words run together: "basedpractice"
            if camel:
                break
            a, b = lw[:k], lw[k:]
            if known(a) and known(b) and b not in SUFW and a not in ('dis', 'non', 'over', 'under', 'inter', 'counter'):
                return w[:k] + ' ' + w[k:]
        return w
    x = re.sub(r'[A-Za-z]+', split_tok, x)
    x = re.sub(r'\bwith-(\w+)', r'with \1', x)
    if x != orig:
        LOG.append({'code': where[0], 'n': where[1], 'note': 'OCR correction: ' + '; '.join(diffwords(orig, x)), 'applied': True})
    return x


def diffwords(a, b):
    import difflib
    aw, bw = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw).get_opcodes():
        if op != 'equal':
            out.append(f"“{' '.join(aw[i1:i2])}” → “{' '.join(bw[j1:j2])}”")
    return out[:6]


SEC = re.compile(r'^SECTION\s+(\d+)\s*\.\s*(.*)$')


def split_caption(rest):
    m = re.match(r'^(.{3,420}?)\.\s*-\s+(.*)$', rest) or re.match(r'^(.{3,420}?)\.-\s*(.*)$', rest)
    if m and not re.search(r'\b(shall|may|must)\b', m.group(1)):
        return m.group(1).strip(), m.group(2)
    m = re.match(r'^(.{3,220}?)\s*[—–]\s*(.*)$', rest)
    if m and not re.search(r'\b(shall|may|must)\b', m.group(1)):
        return m.group(1).rstrip('. '), m.group(2)
    m = re.match(r'^(.{3,160}?\.)\s+(.*)$', rest)
    if m and not re.search(r'\b(shall|may|must)\b', m.group(1)):
        return m.group(1).rstrip('. '), m.group(2)
    return '', rest


ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6}


def build_cpra():
    P = paras('cpra.html')
    divisions, provs = [], []
    cur_div, cur_canon, prov = None, None, None
    k = 0
    pre = []
    # preamble
    while k < len(P) and not P[k][2].startswith('CANON'):
        tag, bo, x = P[k]
        if x not in ('A.M. No. 22-09-01-SC', 'CODE OF PROFESSIONAL RESPONSIBILITY AND ACCOUNTABILITY', 'PREAMBLE'):
            pre.append(fix_words(x, ('cpra', 'Preamble')))
        k += 1
    divisions.append({'t': 'PREAMBLE', 'l': 0, 'p': None})
    provs.append({'i': 'preamble', 'l': 'Preamble', 'n': 'P', 'd': 0, 'p': pre})
    while k < len(P):
        tag, bo, x = P[k]
        m = re.match(r'^CANON\s+([IVX]+)\s*(.*)$', x)
        if m and bo:
            cur_canon = m.group(1)
            title = m.group(2).strip()
            if not title and k + 1 < len(P) and P[k + 1][0].startswith('h'):
                title = P[k + 1][2]
                k += 1
            divisions.append({'t': f'CANON {cur_canon} — {title}', 'l': 0, 'p': None})
            cur_div = len(divisions) - 1
            # the canon's own statement
            intro = []
            k += 1
            while k < len(P) and not SEC.match(P[k][2]):
                intro.append(fix_words(P[k][2], ('cpra', f'Canon {cur_canon}')))
                k += 1
            provs.append({'i': f'canon-{cur_canon.lower()}', 'l': f'Canon {cur_canon}', 'n': f'C{ROMAN[cur_canon]}', 'd': cur_div, 'c': title.title().replace(' And ', ' and '), 'p': intro})
            continue
        if x == "REVISED LAWYER'S OATH":
            divisions.append({'t': "REVISED LAWYER'S OATH", 'l': 0, 'p': None})
            cur_div = len(divisions) - 1
            body = []
            k += 1
            while k < len(P) and not P[k][0].startswith('h'):
                body.append(fix_words(P[k][2], ('cpra', 'Oath')))
                k += 1
            provs.append({'i': 'lawyers-oath', 'l': "Lawyer's Oath", 'n': 'Oath', 'd': cur_div, 'c': "Revised Lawyer's Oath", 'p': body})
            continue
        if x == 'GENERAL PROVISIONS':
            divisions.append({'t': 'GENERAL PROVISIONS', 'l': 0, 'p': None})
            cur_div = len(divisions) - 1
            cur_canon = 'GP'
            k += 1
            continue
        ms = SEC.match(x)
        if ms:
            n, rest = ms.group(1), ms.group(2)
            cap, body = split_caption(rest)
            pref = f'canon-{cur_canon.lower()}' if cur_canon != 'GP' else 'gp'
            lab = f'Canon {cur_canon}, Sec. {n}' if cur_canon != 'GP' else f'Gen. Prov., Sec. {n}'
            where = ('cpra', lab)
            if not cap and len(body) < 110 and body.endswith('.') and not re.search(r'\b(shall|may|must)\b', body):
                cap, body = body.rstrip('.'), ''
            prov = {'i': f'{pref}-sec-{n}', 'l': lab, 'n': f'{cur_canon}-{n}', 'd': cur_div, 'c': fix_words(cap, where), 'p': [fix_words(body, where)] if body else []}
            provs.append(prov)
            k += 1
            continue
        if prov is not None:
            prov['p'].append(fix_words(x, ('cpra', prov['l'])))
        k += 1
    # known gaps in the transcription, restored from the official text
    for p in provs:
        for j, x in enumerate(p['p']):
            if x == 'Acting and being commissioned as a Notary Public.' and j and p['p'][j - 1].startswith('(f)'):
                p['p'][j] = '(g) Acting and being commissioned as a Notary Public.'
                LOG.append({'code': 'cpra', 'n': p['l'], 'note': 'Item letter “(g)” restored before “Acting and being commissioned as a Notary Public”; the transcription dropped it.', 'applied': True})
    # more OCR slips: "Canon 111"/"Canon Ill" for Canon III, "often (10)" for "of ten (10)", a stray quote,
    # a dropped capital "A" at the start of a section, and a sentence split across two paragraphs
    for p in provs:
        ps = p['p']
        for j, x in enumerate(ps):
            y = re.sub(r'\bCanon (?:111|Ill|lll)\b', 'Canon III', x)
            y = y.replace('often (10)', 'of ten (10)').replace(", 'the Investigating", ', the Investigating')
            y = y.replace('proceed exparte', 'proceed ex parte').replace('a nonextendible period', 'a non-extendible period')
            y = y.replace('Investigating Commissioner. shall form part', 'Investigating Commissioner. It shall form part')
            y = y.replace('the law and j jurisprudence', 'the law and jurisprudence')
            y = re.sub(r"(\w)['’] s\b", r"\1’s", y)
            if y.endswith('legal aid clinics in their jurisdiction,'):
                y = y[:-1] + '.'
            if j == 0 and y.startswith('lawyer shall'):
                y = 'A ' + y
            if y != x:
                LOG.append({'code': 'cpra', 'n': p['l'], 'note': 'OCR correction: ' + '; '.join(diffwords(x, y)), 'applied': True})
                ps[j] = y
        j = 0
        while j < len(ps) - 1:
            if re.search(r'\b(the|a|an|of|to|by|for|in|with)$', ps[j]) and ps[j + 1][:1].isupper():
                LOG.append({'code': 'cpra', 'n': p['l'], 'note': 'A sentence split across two paragraphs by the transcription was rejoined.', 'applied': True})
                ps[j] = ps[j] + ' ' + ps[j + 1]
                del ps[j + 1]
            else:
                j += 1
    # two list items the transcription ran together (Canon VI, Sec. 33(s) and (t))
    for p in provs:
        ps = p['p']
        for j, x in enumerate(ps):
            if x == '(s) Unlawful discrimination under Canon V; and' and j + 1 < len(ps) and ps[j + 1].startswith('Sale, distribution'):
                ps[j + 1] = '(t) ' + ps[j + 1]
                LOG.append({'code': 'cpra', 'n': p['l'], 'note': 'Item letter “(t)” restored; the transcription dropped it.', 'applied': True})
                break
    # "(1)" read for "(l)" inside a lettered list
    for p in provs:
        ps = p['p']
        for j in range(1, len(ps)):
            if ps[j].startswith('(1) ') and ps[j - 1].startswith('(k) '):
                ps[j] = '(l) ' + ps[j][4:]
                LOG.append({'code': 'cpra', 'n': p['l'], 'note': 'OCR correction: “(1)” → “(l)” (item between (k) and (m)).', 'applied': True})
    # item letters the transcription dropped: a bare paragraph between (d) and (f) is (e); a bare closing line after (f) is (g)
    for p in provs:
        ps = p['p']
        for j in range(1, len(ps)):
            m0 = re.match(r'^\(([a-z])\)', ps[j - 1])
            if m0 and not re.match(r'^\(', ps[j]) and ps[j][:1].isalpha():
                nxt = re.match(r'^\(([a-z])\)', ps[j + 1]) if j + 1 < len(ps) else None
                want = chr(ord(m0.group(1)) + 1)
                last = not nxt and (re.match(r'^(Other (similar|analogous)|Such other)', ps[j]) or re.search(r'; (and|or)$', ps[j - 1]))
                if (nxt and ord(nxt.group(1)) == ord(want) + 1) or last:
                    ps[j] = f'({want}) ' + ps[j]
                    LOG.append({'code': 'cpra', 'n': p['l'], 'note': f'Item letter “({want})” restored; the transcription dropped it.', 'applied': True})
    CR = 'ChanRobles Virtual Law Library transcription'
    note = {'t': 'The primary transcription omits a page here (Canon VI, Section 38(b)(2) to Section 45(a)). This text is taken from a second transcription, the ' + CR + ', and should be checked against the official PDF.', 'b': CR}
    k38 = next(k for k, p in enumerate(provs) if p['l'] == 'Canon VI, Sec. 38')
    p38 = provs[k38]
    cut = next(j for j, x in enumerate(p38['p']) if x.startswith('(b) Aggravating'))
    p38['p'] = p38['p'][:cut + 1] + [
        '(1) Finding of previous administrative liability where a penalty is imposed, regardless of nature or gravity;', '(2) Age;',
        '(3) Number of years in the practice of law;', '(4) Employment of fraudulent means to conceal the offense;',
        '(5) Respondent’s act or omission was tainted with bad faith or malice, except when it is an element of the offense;',
        '(6) Lack of remorse;', '(7) Failure to comply with the orders of the Court and the IBP in relation to an administrative case;',
        '(8) Other analogous circumstances.']
    p38['e'] = [note]
    d6 = p38['d']
    add = [
        ('39', 'Manner of imposition', ['If one (1) or more aggravating circumstances and no mitigating circumstances are present, the Supreme Court may impose the penalties of suspension or fine for a period or amount not exceeding double of the maximum prescribed under this Rule. The Supreme Court may, in its discretion, impose the penalty of disbarment depending on the number and gravity of the aggravating circumstances.',
                                        'If one (1) or more mitigating circumstances and no aggravating circumstances are present, the Supreme Court may impose the penalties of suspension or fine for a period or amount not less than half of the minimum prescribed under the CPRA.',
                                        'If there are both aggravating and mitigating circumstances present, the Supreme Court may offset each other.']),
        ('40', 'Penalty for multiple offenses', ['If the respondent is found liable for more than one (1) offense arising from separate acts or omissions in a single administrative proceeding, the Court shall impose separate penalties for each offense. Should the aggregate of the imposed penalties exceed five (5) years of suspension from the practice of law or P1,000,000.00 in fines, the respondent may, in the discretion of the Supreme Court, be meted with the penalty of disbarment.',
                                             'If a single act or omission gives rise to more than one (1) offense, the respondent shall still be found liable for all such offenses, but shall, nonetheless, only be meted with the appropriate penalty for the most serious offense.']),
        ('41', 'Payment of fines and return of client’s money and property', ['When the penalty imposed is a fine or the respondent is ordered to return the client’s money or property, the respondent shall pay or return it within a period not exceeding three (3) months from receipt of the decision or resolution. If unpaid or unreturned, the Court may cite the respondent in indirect contempt.']),
        ('42', 'Penalty when the respondent has been previously disbarred', ['When the respondent has been previously disbarred and is subsequently found guilty of a new charge, the Court may impose a fine or order the disbarred lawyer to return the money or property to the client, when proper. If the new charge deserves the penalty of a disbarment or suspension from the practice of law, it shall not be imposed but the penalty shall be recorded in the personal file of the disbarred lawyer in the Office of the Bar Confidant or other office designated for the purpose. In the event that the disbarred lawyer applies for judicial clemency, the penalty so recorded shall be considered in the resolution of the same.']),
        ('43', 'Immediately executory; furnished copies', ['The decision or resolution pronouncing the respondent’s administrative liability is immediately executory. The copies of the decision or resolution shall be furnished to the Office of the Bar Confidant, the Integrated Bar of the Philippines National Office and local chapter to which the respondent belongs, and the Office of the Court Administrator for circulation to all the courts.']),
        ('44', 'Confidentiality', ['Proceedings against lawyers shall be confidential. However, the final order of the Supreme Court shall be published like its decisions in other cases.']),
        ('45', 'Sworn statement after service of suspension', ['Upon the expiration of the period of suspension from the practice of law, the lawyer shall file a Sworn Statement with the Supreme Court, through the Office of the Bar Confidant, to show that the petitioner, during the period of suspension:',
                                                           '(a) has not appeared before any court, tribunal or other government agency, whether in respect of current, former or prospective clients;',
                                                           '(b) has not signed or filed any pleading or other court submission;',
                                                           '(c) has duly informed his or her clients, law firm, law school where the lawyer is teaching, legal clinic, or other legal service organization of which he or she is a member, regarding the suspension; and',
                                                           '(d) has not otherwise performed any act, directly or indirectly, that amounts to the practice of law.',
                                                           'The Sworn Statement shall state the date of the lawyer’s receipt of the order, decision or resolution imposing the penalty of suspension, as well as a list of the lawyer’s engagements affected by the suspension, indicating the relevant court, tribunal or other government agency, if any.',
                                                           'Copies of the Sworn Statement shall be furnished to the Local Chapter of the IBP, to the Executive Judge of the courts where the suspended lawyer has pending cases handled by him or her, and/or where he or she has appeared as counsel.']),
    ]
    for j, (n, cap, body) in enumerate(add):
        provs.insert(k38 + 1 + j, {'i': f'canon-vi-sec-{n}', 'l': f'Canon VI, Sec. {n}', 'n': f'VI-{n}', 'd': d6, 'c': cap, 'p': body, 'e': [note]})
    LOG.append({'code': 'cpra', 'n': 'Canon VI, Secs. 38–45', 'note': 'Section 38(b)(2)–(8) and Sections 39–45 restored from the ChanRobles transcription; the primary transcription omits that page and had moved part of Section 45 under Section 38.', 'applied': True})
    for p in provs:
        if p['l'] in ('Canon III, Sec. 22', 'Canon II, Sec. 34', 'Canon II, Sec. 17'):
            p['xc'] = 'Compared word by word with a second transcription (ChanRobles Virtual Law Library): identical.'
    return {
        'id': 'cpra', 'short': 'CPRA (A.M. 22-09-01-SC)', 'title': 'Code of Professional Responsibility and Accountability',
        'citation': 'A.M. No. 22-09-01-SC (April 11, 2023; in force May 29, 2023)', 'subject': 'eth',
        'note': 'Supersedes the 1988 Code of Professional Responsibility, Sections 20 to 37 of Rule 138 and Rule 139-B of the Rules of Court, and the old Lawyer’s Oath (General Provisions, Sec. 2).',
        'source': {'name': 'Justitia (University of Makati School of Law), transcription of the Supreme Court’s text; OCR slips corrected', 'url': 'https://sc.judiciary.gov.ph/wp-content/uploads/2023/05/22-09-01-SC-FINAL.pdf'},
        'preamble': [], 'closing': [], 'divisions': divisions, 'provisions': provs,
    }


def build_rules(fn, cid, short, title, cit, note, url, start_pat=r'^(RULE|PART|CHAPTER|ARTICLE)\b', lines=False):
    """Generic: RULE headings become divisions; SECTION n. lines become provisions."""
    P = paras_lines(fn) if lines else paras(fn)
    divisions, provs = [], []
    cur_div, prov, rule, book, kw = None, None, '', '', 'Rule'
    BOOKN = {'ONE': 'I', 'TWO': 'II', 'THREE': 'III', 'FOUR': 'IV', 'FIVE': 'V', 'SIX': 'VI', 'SEVEN': 'VII'}
    seen = set()
    started = False
    pending = None
    for tag, bo, x in P:
        mb = re.match(r'^BOOK\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|[IVX]+)\b\.?\s*[—–-]?\s*(.*)$', x)
        if mb and (bo or tag.startswith('h') or x.isupper()):
            book = BOOKN.get(mb.group(1), mb.group(1)); rule = ''
            continue
        m = re.match(r'^(RULE|PART|CHAPTER|ARTICLE)\s+([IVXLC\d]+(?:\s*-\s*[A-Z]\b)?)\.?\s*[—–-]?\s*(.*)$', x)
        if m and (bo or tag.startswith('h') or x.isupper()):
            started = True
            rule = re.sub(r'\s+', '', m.group(2)); kw = m.group(1).title()
            t = (f'BOOK {book} · ' if book else '') + f'{m.group(1)} {m.group(2)}' + (f' — {m.group(3).strip()}' if m.group(3).strip() else '')
            if divisions and divisions[-1]['t'] == t:
                continue
            divisions.append({'t': t, 'l': 0, 'p': None})
            cur_div = len(divisions) - 1
            pending = cur_div if not m.group(3).strip() else None
            prov = None
            continue
        if pending is not None and (x.isupper() or bo) and not SEC.match(x) and not re.match(r'^SEC(TION)?\.?\s*\d', x):
            divisions[pending]['t'] += ' — ' + x.strip()
            pending = None
            continue
        pending = None
        ms = re.match(r'^(?:SECTION|SEC\.|Section|Sec\.)\s*(\d+)\s*\.\s*(.*)$', x)
        if ms:
            started = True
            n, rest = ms.group(1), ms.group(2)
            cap, body = split_caption(rest)
            lab = (f'Book {book}, ' if book else '') + (f'{kw} {rule}, Sec. {n}' if rule else f'Section {n}')
            pid = (f'b{book.lower()}-' if book else '') + (f'{kw.lower()}-{rule.lower()}-sec-{n}' if rule else f'section-{n}')
            while pid in seen:
                pid += 'x'
            seen.add(pid)
            body = re.sub(r'^-\s*', '', body)
            if not cap and len(body) < 110 and body.endswith('.') and not re.search(r'\b(shall|may|must)\b', body):
                cap, body = body.rstrip('.'), ''
            prov = {'i': pid, 'l': lab, 'n': f'{rule}-{n}' if rule else n, 'd': cur_div, 'c': fix_words(cap, (cid, lab)), 'p': [fix_words(body, (cid, lab))] if body else []}
            provs.append(prov)
            continue
        if prov is not None and started:
            if re.match(r'^(Promulgated|Footnotes|SO ORDERED|Adopted)\b', x):
                prov = None
                continue
            if re.match(r'^NOTES?:', x):
                LOG.append({'code': cid, 'n': prov['l'], 'note': 'A transcriber’s note (not part of the rule) was left out.', 'applied': True})
                continue
            if not prov['c'] and not prov['p'] and len(x) < 110 and x.endswith('.') and x[0].isupper() and not re.search(r'\b(shall|may|must)\b', x):
                prov['c'] = x.rstrip('.')
                continue
            prov['p'].append(fix_words(x, (cid, prov['l'])))
    for pr in provs:   # a caption left on the first line
        if not pr.get('c') and len(pr['p']) > 1 and len(pr['p'][0]) < 260 and not re.search(r'\b(shall|may|must|is|are)\b', pr['p'][0]):
            pr['c'] = pr['p'][0].rstrip('. ')
            pr['p'] = pr['p'][1:]
    return {'id': cid, 'short': short, 'title': title, 'citation': cit, 'subject': 'eth', 'note': note,
            'source': {'name': 'Justitia (University of Makati School of Law), transcription of the Supreme Court’s text; OCR slips corrected', 'url': url},
            'preamble': [], 'closing': [], 'divisions': divisions, 'provisions': provs}


def register(docs):
    cat = json.load(open(f'{OUT}/catalog.json'))
    ids = {d['id'] for d in docs}
    cat['codes'] = [c for c in cat['codes'] if c['id'] not in ids]
    import spellfix_lib
    for d in docs:
        spellfix_lib.join_broken(d['id'], d['provisions'], LOG)
        spellfix_lib.apply(d['id'], d['divisions'], d['provisions'], LOG)
        used = sorted({p['d'] for p in d['provisions'] if p['d'] is not None})
        remap = {o: k for k, o in enumerate(used)}
        d['divisions'] = [d['divisions'][o] for o in used]
        for p in d['provisions']:
            p['d'] = remap.get(p['d'])
        js = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
        open(f'{OUT}/codes/{d["id"]}.json', 'w').write(js)
        h = hashlib.sha1(js.encode()).hexdigest()[:10]
        words = sum(len(x.split()) for p in d['provisions'] for x in p['p'] if isinstance(x, str))
        subj = {'irrlabor': 'lab', 'do174': 'lab', 'irr9165': 'crim', 'pb2018': 'crim'}.get(d['id'], d['subject'])
        d['subject'] = subj
        e = {'id': d['id'], 'short': d['short'], 'title': d['title'], 'citation': d['citation'], 'subject': subj, 'core': d['id'] in ('cpra',),
             'note': d['note'], 'count': len(d['provisions']), 'words': words, 'hash': h, 'bytes': len(js), 'kind': 'sc'}
        for kind, folder in (('cases', 'cases'), ('notes', 'notes')):
            f = f'{OUT}/{folder}/{d["id"]}.json'
            if os.path.exists(f):
                e[kind] = True
                if kind == 'notes':
                    e['nhash'] = hashlib.sha1(open(f, 'rb').read()).hexdigest()[:10]
                else:
                    e['hash'] = hashlib.sha1((h + str(os.path.getsize(f)) + str(os.path.getmtime(f))).encode()).hexdigest()[:10]
        cat['codes'].append(e)
    cat['missing'] = [m for m in cat['missing'] if 'Professional Responsibility and Accountability' not in m['title']]
    cat['total'] = sum(c['count'] for c in cat['codes'])
    json.dump(cat, open(f'{OUT}/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    pr = json.load(open(f'{OUT}/proofreading.json'))
    pr['errata'] = [e for e in pr['errata'] if e['code'] not in ids] + LOG
    json.dump(pr, open(f'{OUT}/proofreading.json', 'w'), ensure_ascii=False, separators=(',', ':'))


def main():
    docs = [build_cpra()]
    docs.append(build_rules('notary.html', 'notarial', '2004 Notarial Rules', 'Rules on Notarial Practice',
                            'A.M. No. 02-8-13-SC (2004), as amended', 'Who may be commissioned as a notary public, what a notary may and may not do, the notarial register, and sanctions. Read with the 2020 Rules on Remote Notarization.',
                            'https://lawphil.net/courts/supreme/am/am_02-8-13-sc_2004.html'))
    docs.append(build_rules('am200704sc.html', 'remotenot', '2020 Remote Notarization', 'Interim Rules on Remote Notarization of Paper Documents',
                            'A.M. No. 20-07-04-SC (2020)', 'Notarization by videoconference, allowed under strict conditions.',
                            'https://sc.judiciary.gov.ph/'))
    docs.append(build_rules('irrlabor.html', 'irrlabor', 'Omnibus Rules (Labor Code IRR)', 'Omnibus Rules Implementing the Labor Code',
                            'Rules and Regulations Implementing the Labor Code (1989 compilation, as amended)', 'Parts have been amended or replaced by later department orders — e.g., D.O. 40-03 (Book V, labor relations), D.O. 147-15 (Book VI, termination), D.O. 174-17 (contracting). Check the current order before citing.',
                            'https://www.dole.gov.ph/', lines=True))
    docs.append(build_rules('doledo174s2017.html', 'do174', 'DOLE D.O. 174-17 (Contracting)', 'Rules Implementing Articles 106 to 109 of the Labor Code, as Amended',
                            'DOLE Department Order No. 174, Series of 2017', 'Legitimate contracting and subcontracting; labor-only contracting; registration of contractors; rights of contractors’ employees.', 'https://www.dole.gov.ph/', lines=True))
    docs.append(build_rules('irrra9165.html', 'irr9165', 'IRR of RA 9165', 'Implementing Rules and Regulations of the Comprehensive Dangerous Drugs Act of 2002',
                            'IRR of Republic Act No. 9165 (2002), as amended', 'Includes the rules on custody and disposition of seized drugs (Sec. 21), read with RA 10640 (2014) on the chain of custody.', 'https://pdea.gov.ph/'))
    register(docs)
    for d in docs:
        caps = sum(1 for p in d['provisions'] if p.get('c'))
        print(d['id'], len(d['divisions']), 'divisions', len(d['provisions']), 'provisions', caps, 'captions')
    print('OCR corrections', len(LOG))


if __name__ == '__main__':
    main()
