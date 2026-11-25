"""The curriculum: how the library is presented to a student.

Eight fields. Inside each field a short path: Start here -> Core -> Go deeper.
A path is made of codes, short lessons (our own words), study sets (small ordered lists of
provisions drawn from several codes) and the student's syllabus.

Every code in the catalogue must have exactly one home (an item without "x": cross-listings carry x=1).
Inline provision links in lesson text are written {code:provision-id} and are checked against the data.

Output: data/curriculum.json ; data/catalog.json gets "chash".
"""
import json, re, sys, hashlib

SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site/data'
CAT = json.load(open(f'{SITE}/catalog.json'))
CODES = {c['id']: c for c in CAT['codes']}
PROV = {}


def prov(cid, pid):
    if cid not in PROV:
        PROV[cid] = {p['i']: p for p in json.load(open(f'{SITE}/codes/{cid}.json'))['provisions']}
    if pid not in PROV[cid]:
        raise SystemExit(f'unknown provision {cid}:{pid}')
    return PROV[cid][pid]


ABBR = {'const1987': 'Const.', 'civil': 'Civil Code', 'rpc': 'RPC', 'labor': 'Labor Code', 'admincode': 'Admin. Code', 'family': 'Family Code'}


def plabel(cid, pid):
    p = prov(cid, pid)
    lab = p['l'].replace('Article ', 'Art. ').replace('Section ', 'Sec. ')
    return f"{ABBR.get(cid, CODES[cid]['short'])}, {lab}"


def C(cid, x=0, note=''):
    assert cid in CODES, cid
    d = {'t': 'code', 'id': cid}
    if x: d['x'] = 1
    if note: d['note'] = note
    return d


def L(lid): return {'t': 'lesson', 'id': lid}
def S(sid): return {'t': 'set', 'id': sid}
def Y(cid, title): return {'t': 'syl', 'id': cid, 'title': title}
def M(title, cit, why, url=''): return {'t': 'missing', 'title': title, 'citation': cit, 'why': why, 'url': url}


FIELDS = [
 {'id': 'pol', 'name': 'Political Law', 'q': 'Who holds power, and what may the State not do to you?', 'tracks': [
   {'tier': 'start', 'name': 'The Constitution', 'why': 'Everything else in public law is measured against it. Begin with Article III.',
    'items': [C('const1987'), Y('cl2', 'Your Constitutional Law 2 syllabus')]},
   {'tier': 'core', 'name': 'How government is organised', 'why': 'National administration, then local governments and the police power they exercise.',
    'items': [C('admincode'), C('lgc'), C('ra6975'), C('ra8551')]},
   {'tier': 'core', 'name': 'Elections and direct democracy', 'why': 'How power is given and taken back.',
    'items': [C('oec'), C('ra6735')]},
   {'tier': 'deep', 'name': 'Citizenship and immigration', 'why': '', 'items': [C('ca63'), C('ra9225'), C('ca613')]},
   {'tier': 'deep', 'name': 'Accountability and clean government', 'why': '',
    'items': [C('ra6770'), C('ra12009'), C('ra9184'), C('ra11032'), C('ra9485'), C('ra6713', 1), C('ra3019', 1)]},
   {'tier': 'deep', 'name': 'Land, patrimony and indigenous peoples', 'why': '', 'items': [C('carl'), C('alrc'), C('ra8371'), C('mining'), C('forestry'), C('fisheries'), C('water')]},
   {'tier': 'deep', 'name': 'Environment and public safety', 'why': '',
    'items': [C('pd1152'), C('ra8749'), C('ra9275'), C('ra9003'), C('fire'),
              M('National Building Code', 'Presidential Decree No. 1096 (1977)', 'No verbatim source was available for this build. Send a PDF of PD 1096 and it will be added.')]},
 ]},
 {'id': 'civ', 'name': 'Civil Law', 'q': 'What do private persons owe one another, in family, property and contract?', 'tracks': [
   {'tier': 'start', 'name': 'The Civil Code', 'why': 'Start with Articles 1 to 36, then Obligations (Art. 1156 onward). The rest builds on those two.',
    'items': [C('civil')]},
   {'tier': 'core', 'name': 'Persons and family', 'why': 'The Family Code replaced most of Book I of the Civil Code.',
    'items': [C('family'), C('ra11642'), C('ra9048'), C('pd603'), C('pd1083')]},
   {'tier': 'core', 'name': 'Land titles', 'why': '', 'items': [C('pd1529'), C('act496')]},
   {'tier': 'deep', 'name': 'Sales, housing and security', 'why': '', 'items': [C('ra6552'), C('pd957'), C('ra9653'), C('act3135'), C('act1508', 1)]},
   {'tier': 'deep', 'name': 'Contracts made electronically', 'why': '', 'items': [C('ra8792')]},
 ]},
 {'id': 'lab', 'name': 'Labor and Social Legislation', 'q': 'How does the law protect people who work, and people in need?', 'tracks': [
   {'tier': 'start', 'name': 'The Labor Code', 'why': 'Read Articles 3 and 4 first: they tell you how every other article is to be read.',
    'items': [C('labor')]},
   {'tier': 'core', 'name': 'Pay and leave', 'why': '', 'items': [C('pd851'), C('ra11210'), C('ra8187'), C('ra11165')]},
   {'tier': 'core', 'name': 'Workers the law singles out', 'why': 'Domestic workers, migrant workers, and protection from harassment.',
    'items': [C('ra10361'), C('ra8042'), C('ra10022'), C('ra7877'), C('ra11313'), C('ra9710')]},
   {'tier': 'deep', 'name': 'Social insurance, health and welfare', 'why': '',
    'items': [C('ra11199'), C('ra11223'), C('ra11036'), C('ra10354'), C('milk'), C('sanitation'), C('ra10931')]},
 ]},
 {'id': 'crim', 'name': 'Criminal Law', 'q': 'When may the State punish, for what, and how much?', 'tracks': [
   {'tier': 'start', 'name': 'The Revised Penal Code', 'why': 'Book One (Arts. 1 to 113) is the grammar of every crime. Learn it before Book Two.',
    'items': [C('rpc'), {'t': 'b2', 'id': 'book2', 'title': 'Book Two Studio'}, Y('crim1', 'Your Criminal Law 1 syllabus'), Y('crim2', 'Your Criminal Law 2 syllabus')]},
   {'tier': 'core', 'name': 'Computing and serving penalties', 'why': 'Read with Arts. 21 to 99 of the Code.',
    'items': [C('isl'), C('ra10951'), C('ra10592'), C('ra9346'), C('ra7659'), C('act3326')]},
   {'tier': 'core', 'name': 'Sexual offences and violence against women', 'why': '', 'items': [C('ra8353'), C('ra11648'), C('ra9262'), C('ra9995'), C('ra7877', 1)]},
   {'tier': 'core', 'name': 'Children', 'why': '', 'items': [C('ra7610'), C('ra9344'), C('ra11930')]},
   {'tier': 'core', 'name': 'Drugs and firearms', 'why': '', 'items': [C('ra9165'), C('ra10591')]},
   {'tier': 'deep', 'name': 'Public officers and corruption', 'why': '', 'items': [C('ra3019'), C('ra7080'), C('pd1829')]},
   {'tier': 'deep', 'name': 'Trafficking and hazing', 'why': '', 'items': [C('ra9208'), C('ra10364'), C('ra11862'), C('ra11053')]},
   {'tier': 'deep', 'name': 'Property and fraud', 'why': '',
    'items': [C('pd1612'), C('pd1613'), C('ra10883'),
              M('Bouncing Checks Law', 'Batas Pambansa Blg. 22 (1979)', 'Not in the statute source used for this build. Send a PDF and it will be added.')]},
   {'tier': 'deep', 'name': 'Privacy, cybercrime and security', 'why': '', 'items': [C('ra10175'), C('ra4200'), C('ra11479'), C('ra9851', 1)]},
 ]},
 {'id': 'com', 'name': 'Commercial Law and Taxation', 'q': 'How is business organised, financed and taxed?', 'tracks': [
   {'tier': 'start', 'name': 'The corporation', 'why': '', 'items': [C('rcc')]},
   {'tier': 'core', 'name': 'Instruments, insurance and securities', 'why': '', 'items': [C('nil'), C('insurance'), C('src')]},
   {'tier': 'core', 'name': 'Taxation', 'why': 'The 1997 Code is shown as enacted. TRAIN and CREATE rewrote many sections, so study them together.',
    'items': [C('nirc'), C('ra10963'), C('ra11534'), C('cmta'), C('ra9282')]},
   {'tier': 'deep', 'name': 'Banking, credit and insolvency', 'why': '', 'items': [C('ra8791'), C('ra10142'), C('act1508'), C('act2137'), C('ra9160')]},
   {'tier': 'deep', 'name': 'Ideas, data, markets and consumers', 'why': '',
    'items': [C('ipcode'), C('ra10173'), C('ra10667'), C('ra7394'), C('ra9829'), C('coop'),
              M('Code of Commerce', 'Royal Decree of August 6, 1888', 'No reliable transcription was available for this build.')]},
 ]},
 {'id': 'intl', 'name': 'International Law', 'q': 'How do rules made among states bind a Philippine court?', 'tracks': [
   {'tier': 'start', 'name': 'From the world into Philippine law', 'why': 'International law reaches our courts through a few clauses of the Constitution. Learn those first.',
    'items': [L('intl-map'), S('intl-const'), Y('pil', 'Your Public International Law syllabus')]},
   {'tier': 'core', 'name': 'International crimes and human rights, at home', 'why': 'Philippine statutes that carry out treaty obligations.',
    'items': [C('ra9851'), C('ra9208', 1), C('ra11479', 1)]},
   {'tier': 'core', 'name': 'People across borders', 'why': '', 'items': [C('ca613', 1), C('ra9225', 1), C('ca63', 1), C('ra8042', 1)]},
   {'tier': 'deep', 'name': 'Treaty texts', 'why': '',
    'items': [M('UN Charter, Vienna Convention on the Law of Treaties, UNCLOS, Rome Statute', 'Treaties', 'Treaty texts are not in this library yet. Your syllabus lists the cases; send the texts you are assigned and they will be added verbatim.')]},
 ]},
 {'id': 'craft', 'name': 'The Lawyer’s Craft', 'q': 'How do you read a statute, digest a case, and write an argument?', 'tracks': [
   {'tier': 'start', 'name': 'Read a provision', 'why': 'Ten minutes here makes every other field easier.',
    'items': [L('read-provision'), L('law-takes-effect'), S('statcon-effect')]},
   {'tier': 'core', 'name': 'Statutory construction', 'why': 'The canons, and the tie-breakers each field of law uses.',
    'items': [L('canons'), L('tie-breakers'), S('statcon-meaning')]},
   {'tier': 'core', 'name': 'Cases and legal reasoning', 'why': '', 'items': [L('digest'), L('reasoning')]},
   {'tier': 'core', 'name': 'Research and thesis writing', 'why': '', 'items': [L('research'), L('thesis')]},
   {'tier': 'deep', 'name': 'Courts and procedure', 'why': 'Which court hears what.',
    'items': [C('bp129'), C('ra11576'), C('ra10660'), C('ra9282', 1), C('ra9285'), C('ra876'),
              M('Rules of Court', '1997 Rules of Civil Procedure as amended; Revised Rules on Evidence', 'Supreme Court rules are not in the statute source used. Send PDFs and they will be added verbatim.')]},
 ]},
 {'id': 'eth', 'name': 'Legal and Judicial Ethics', 'q': 'What does the profession owe the court, the client and the public?', 'tracks': [
   {'tier': 'start', 'name': 'Why lawyers owe more', 'why': 'Ethics makes sense once you see whom each duty protects.',
    'items': [L('eth-frame'), Y('ethics', 'Your Legal and Judicial Ethics syllabus')]},
   {'tier': 'core', 'name': 'The lawyer', 'why': '',
    'items': [L('eth-cpra'), S('eth-profession'),
              M('Code of Professional Responsibility and Accountability', 'A.M. No. 22-09-01-SC (2023)', 'A Supreme Court issuance, not yet in the library verbatim. Read the official text; send the PDF and it will be added provision by provision.',
                'https://sc.judiciary.gov.ph/wp-content/uploads/2023/05/22-09-01-SC-FINAL.pdf')]},
   {'tier': 'core', 'name': 'The judge', 'why': '',
    'items': [L('eth-judge'), S('eth-judiciary'),
              M('2025 Code of Judicial Conduct and Accountability', 'A.M. No. 25-04-04-SC (in force December 21, 2025)', 'A Supreme Court issuance, not yet in the library verbatim.',
                'https://sc.judiciary.gov.ph/wp-content/uploads/2025/12/A.M.-NO.-25-04-04-SC.pdf')]},
   {'tier': 'core', 'name': 'The public officer', 'why': '', 'items': [L('eth-public'), S('eth-accountability'), C('ra6713'), C('ra3019', 1), C('ra7080', 1), C('ra6770', 1)]},
 ]},
]

# --------------------------------------------------------------------------- study sets
SETS = {
 'statcon-effect': {'title': 'When a law binds: the codal rules', 'blurb': 'Thirteen short provisions on effectivity, ignorance, prospectivity and repeal. Read them once in this order.', 'items': [
   ('civil', 'article-2', 'Effectivity after publication'), ('admincode', 'book-i-sec-18', 'The same rule, restated in 1987'),
   ('civil', 'article-3', 'Ignorance of the law'), ('admincode', 'book-i-sec-23', 'Ignorance, restated'),
   ('civil', 'article-4', 'Laws look forward'), ('admincode', 'book-i-sec-19', 'Prospectivity, restated'),
   ('rpc', 'article-21', 'No penalty without a prior law'), ('rpc', 'article-22', 'The exception: penal laws favourable to the accused'),
   ('const1987', 'art-iii-sec-22', 'No ex post facto law'),
   ('civil', 'article-7', 'Repeal, and the supremacy of the Constitution'), ('admincode', 'book-i-sec-21', 'Express repeal: no revival'),
   ('admincode', 'book-i-sec-22', 'Implied repeal: revival'), ('civil', 'article-13', 'Counting years, months and days'), ('admincode', 'book-i-sec-31', 'Legal periods, restated in 1987')]},
 'statcon-meaning': {'title': 'Finding meaning: the codal rules', 'blurb': 'What the codes themselves say about interpretation and doubt.', 'items': [
   ('civil', 'article-8', 'Decisions form part of the legal system'), ('civil', 'article-9', 'A judge may not decline to decide'),
   ('civil', 'article-10', 'In doubt, right and justice'), ('admincode', 'book-i-sec-20', 'The same presumption for administrative issuances'),
   ('civil', 'article-11', 'Customs'), ('civil', 'article-12', 'Proving a custom'),
   ('rpc', 'article-10', 'The Code supplements special laws'), ('labor', 'article-4', 'Doubts in favour of labor'),
   ('civil', 'article-1702', 'Labor contracts'), ('civil', 'article-1370', 'Clear contracts: the literal meaning'),
   ('civil', 'article-1377', 'Obscurity against the party who caused it'), ('const1987', 'art-vi-sec-26', 'One subject, one title; three readings')]},
 'intl-const': {'title': 'The Constitution’s doors to international law', 'blurb': 'Six provisions. Every PIL problem in a Philippine court passes through one of them.', 'items': [
   ('const1987', 'art-ii-sec-2', 'Incorporation: generally accepted principles are part of the law of the land'),
   ('const1987', 'art-vii-sec-21', 'Treaties need the Senate'), ('const1987', 'art-xviii-sec-25', 'Foreign military bases, troops and facilities'),
   ('const1987', 'art-i', 'The national territory'), ('const1987', 'art-ii-sec-7', 'An independent foreign policy'), ('const1987', 'art-ii-sec-8', 'Freedom from nuclear weapons')]},
 'eth-profession': {'title': 'The Constitution on the legal profession', 'blurb': 'Where the Supreme Court’s power over lawyers comes from.', 'items': [
   ('const1987', 'art-viii-sec-5', 'Rule-making power: admission to the practice of law, the Integrated Bar, legal assistance'),
   ('const1987', 'art-viii-sec-7', 'Who may be a judge: competence, integrity, probity, independence'),
   ('const1987', 'art-viii-sec-11', 'The Court disciplines judges'), ('const1987', 'art-xi-sec-1', 'Public office is a public trust')]},
 'eth-judiciary': {'title': 'The Constitution on judges', 'blurb': 'Independence on one side, duties and deadlines on the other.', 'items': [
   ('const1987', 'art-viii-sec-1', 'Judicial power and the duty to decide'), ('const1987', 'art-viii-sec-4', 'En banc and divisions'),
   ('const1987', 'art-viii-sec-7', 'Qualifications'), ('const1987', 'art-viii-sec-11', 'Tenure and discipline'),
   ('const1987', 'art-viii-sec-12', 'No non-judicial assignments'), ('const1987', 'art-viii-sec-14', 'Decisions must state the facts and the law'),
   ('const1987', 'art-viii-sec-15', 'Periods to decide')]},
 'eth-accountability': {'title': 'Accountability of public officers', 'blurb': 'The trust, the norms, the disclosures and the remedy.', 'items': [
   ('const1987', 'art-xi-sec-1', 'Public office is a public trust'), ('const1987', 'art-xi-sec-2', 'Who may be impeached, and for what'),
   ('const1987', 'art-xi-sec-3', 'How impeachment is initiated; the one-year bar'), ('const1987', 'art-xi-sec-17', 'Statement of assets, liabilities and net worth'),
   ('ra6713', 'section-4', 'Norms of conduct'), ('ra6713', 'section-7', 'Prohibited acts and transactions'),
   ('ra6713', 'section-8', 'Statements and disclosure'), ('ra3019', 'section-3', 'Corrupt practices of public officers')]},
}

# --------------------------------------------------------------------------- lessons (our own words)
LESSONS = {
 'read-provision': {'title': 'Read a provision the way a lawyer does', 'mins': 6,
  'lead': 'A provision is a small machine. Someone must, may or must not do something, when certain facts exist, unless an exception applies, and then a consequence follows. Find those parts before you memorise a word.',
  'sections': [
   {'h': 'Four questions to ask every time', 'l': [
     'Who is covered? Name the person or thing the provision speaks to.',
     'What is commanded, allowed or forbidden? Look for shall, may, must not, cannot.',
     'When? These are the conditions: if, when, in case, provided that.',
     'Unless what, and then what? Exceptions narrow the rule; consequences are the penalty, the nullity, the liability or the right that results.']},
   {'h': 'Small words that decide cases', 'l': [
     '“Shall” is ordinarily mandatory and “may” permissive.',
     '“And” joins requirements that must all be present; “or” offers alternatives.',
     '“Unless” and “except” open an exception, and exceptions are read narrowly.',
     'A proviso ordinarily limits only the clause it is attached to.',
     'Every number and period is examinable: write it down with what happens when it runs out.']},
   {'h': 'Try it on one sentence', 'p': [
     'Open {civil:article-1159}. Who is covered? The contracting parties. What must they do? Comply with the obligation. By what standard? Good faith. With what force? That of law between them. Four answers, one sentence, and you can now rebuild the article from memory.']},
   {'h': 'How this app helps', 'p': [
     'On every provision the Highlights colour these same parts: duties and powers, conditions, exceptions, numbers, penalties and definitions. The Understand step sorts each sentence under the four questions for you. Do it yourself first, then compare.']}],
  'try': ['Pick a provision you opened today. Write the four answers under My notes in two minutes, without looking at the Understand step.']},

 'law-takes-effect': {'title': 'When does a law bind you?', 'mins': 7,
  'lead': 'Before asking what a law means, ask whether it is in force, for whom, and from when. Five short rules answer that.',
  'sections': [
   {'h': '1. Publication comes first', 'p': [
     'Under {civil:article-2}, a law takes effect after fifteen days following the completion of its publication, unless it is otherwise provided. The Supreme Court read “unless otherwise provided” as referring to the fifteen-day period, not to publication itself: a law may shorten or lengthen the period, but it cannot dispense with publication (Tañada v. Tuvera, G.R. No. L-63915, decision of April 24, 1985 and resolution of December 29, 1986).',
     'Executive Order No. 200 (1987) later allowed publication either in the Official Gazette or in a newspaper of general circulation. The Administrative Code restates the rule in {admincode:book-i-sec-18}.']},
   {'h': '2. Ignorance excuses no one', 'p': ['{civil:article-3} and {admincode:book-i-sec-23}. This is why publication matters: the law may presume you know only what you could have read.']},
   {'h': '3. Laws look forward', 'p': [
     '{civil:article-4} and {admincode:book-i-sec-19}: no retroactive effect unless the law says so. Penal law adds its own rules. No act is punished by a penalty not prescribed before it was committed ({rpc:article-21}), the Constitution forbids ex post facto laws ({const1987:art-iii-sec-22}), and a penal law that favours the accused does reach back, on the terms of {rpc:article-22}.']},
   {'h': '4. Only a later law repeals', 'p': [
     '{civil:article-7}: disuse, custom or contrary practice does not repeal a law, and a law or administrative act contrary to the Constitution is void. Courts do not favour implied repeals; they first try to give effect to both laws.',
     'If the repealing law is itself repealed, does the first law return? It depends on how it was repealed: see {admincode:book-i-sec-21} for express repeals and {admincode:book-i-sec-22} for implied ones.']},
   {'h': '5. Count time the way the law does', 'p': [
     '{civil:article-13} defines years, months, days and nights and tells you to exclude the first day and include the last. The Administrative Code has its own definition of legal periods in {admincode:book-i-sec-31}. Read the two side by side and note how each defines a year; the Supreme Court has applied the later Administrative Code definition (Commissioner of Internal Revenue v. Primetown Property Group, G.R. No. 162155, August 28, 2007).']}],
  'try': ['Without looking, state the five rules in one line each, with the article number.', 'A statute says it “takes effect immediately upon approval.” Is that valid? What may not be skipped?']},

 'canons': {'title': 'The canons: how courts find meaning', 'mins': 8,
  'lead': 'Statutory construction begins only when the text is unclear. Until then, the court applies the words. The canons below are aids to finding what the legislature meant; none of them is a rule that overrides clear intent.',
  'sections': [
   {'h': 'First the words, then the reason', 'l': [
     'Verba legis. Where the words are plain, apply them as written. There is no room for construction.',
     'Ratio legis. Where the words are doubtful, read them by the purpose the law serves and the mischief it was passed to cure.',
     'Read the whole. Give effect to every part; an interpretation that leaves a clause with nothing to do is suspect (ut res magis valeat quam pereat).']},
   {'h': 'Tools for a doubtful word or list', 'l': [
     'Noscitur a sociis. A word is known by the company it keeps.',
     'Ejusdem generis. General words that follow a list of particular things cover only things of the same kind.',
     'Expressio unius est exclusio alterius. Naming one thing implies leaving out the others.',
     'Casus omissus. What the law left out, the court does not supply.']},
   {'h': 'Tools for two laws that seem to collide', 'l': [
     'Harmonise first. Read the two so that both can stand.',
     'The special law prevails over the general one on the matter it covers.',
     'The later law prevails over the earlier, but implied repeal is the last resort.',
     'A law is presumed constitutional; between two readings, prefer the one that keeps it valid.']},
   {'h': 'The Constitution is read the same way', 'p': [
     'In Francisco v. House of Representatives (G.R. No. 160261, November 10, 2003) the Court set the order out: the words in their ordinary meaning, then the intent of the framers where the words are ambiguous, and always the instrument as a whole.']},
   {'h': 'What the codes themselves say', 'p': [
     'When doubt remains, the lawmaking body is presumed to have intended right and justice to prevail: {civil:article-10}, restated for laws and administrative issuances in {admincode:book-i-sec-20}. And a judge may not refuse to decide because the law is silent or obscure: {civil:article-9}.']}],
  'try': ['A city ordinance bans “cars, trucks, motorcycles and other vehicles” from a park. Does it cover a bicycle? An ambulance on call? Argue each side, and name the canon you used.']},

 'tie-breakers': {'title': 'In doubt, which way do you lean?', 'mins': 6,
  'lead': 'Each field of law has a rule for the case where doubt survives a careful reading. They are tie-breakers: they apply only after the text and purpose have been tried.',
  'sections': [
   {'h': 'By field', 'l': [
     'Criminal law. Penal statutes are read strictly against the State and liberally in favour of the accused; a favourable penal law applies retroactively under {rpc:article-22}.',
     'Labor law. Doubts in implementing and interpreting the Code are resolved in favour of labor: {labor:article-4}. For labor contracts and legislation, see also {civil:article-1702}.',
     'Taxation. A tax is not presumed: the law imposing it is read strictly against the government. An exemption is the reverse: it is read strictly against the taxpayer who claims it.',
     'Social legislation. Read liberally in favour of the people it was passed to protect.',
     'Contracts. Clear terms control in their literal sense ({civil:article-1370}); an obscure term is read against the party who caused the obscurity ({civil:article-1377}).',
     'Every field. The lawmaking body is presumed to have intended right and justice to prevail: {civil:article-10}.']},
   {'h': 'A caution', 'p': ['These rules do not invite the court to rewrite the law for the favoured side. If the text is clear against the worker, the accused or the taxpayer, the text governs.']}],
  'try': ['For each of your subjects this semester, write its tie-breaker in one line and the provision that states it, if a provision does.']},

 'digest': {'title': 'Digest a case in five moves', 'mins': 7,
  'lead': 'A digest is your own compression of a decision. Writing it is retrieval practice; copying someone else’s is not. Keep it to what the provision needs.',
  'sections': [
   {'h': 'The five moves', 'l': [
     'Provision. Which article or section is the Court construing? File the case there. A case with three doctrines belongs under three provisions.',
     'Facts that matter. Only the facts the ruling turns on, plus one line on how the case reached the Court.',
     'Issue. One question, answerable yes or no, that names the provision.',
     'Ruling. The answer, and what the Court ordered.',
     'Doctrine. The rule in one sentence, without the parties’ names, that you could apply to new facts. Add a line on why it matters for this provision.']},
   {'h': 'Check your own digest', 'l': [
     'Could a classmate predict the result from your facts alone?',
     'Is your doctrine a rule, or only a description of what happened?',
     'Did you separate what the Court had to decide (the ratio) from what it said in passing (obiter)?']},
   {'h': 'Weigh the source', 'p': [
     'Decisions applying or interpreting the laws form part of the legal system: {civil:article-8}. A doctrine laid down en banc or in division may be changed only by the Court en banc: {const1987:art-viii-sec-4}. A decision must state clearly the facts and the law on which it rests: {const1987:art-viii-sec-14}. So note the date, and whether the ruling is en banc, before you rely on it.']},
   {'h': 'In this app', 'p': ['Each provision’s Cases step lists recent rulings, the cases your syllabus assigns, and the cases your textbooks discuss, with the page. Write your digest under My notes on the provision the case construes.']}],
  'try': ['Take one case from your syllabus this week. Write the five moves in no more than 120 words.']},

 'reasoning': {'title': 'Answer like a lawyer', 'mins': 6,
  'lead': 'Legal analysis has one shape. Learn it once and use it in recitation, in examinations and in pleadings.',
  'sections': [
   {'h': 'Issue, rule, application, conclusion', 'l': [
     'Issue. State the question the facts raise, naming the provision.',
     'Rule. Cite the provision by number and list its elements. Add the leading case if one settles a doubtful element.',
     'Application. Take the elements one at a time and match each to a fact. Say so when a fact is missing.',
     'Conclusion. Answer the question asked.']},
   {'h': 'In an examination, lead with the answer', 'p': ['Give your conclusion in the first sentence, then the rule, then the application. The reader should know your answer before reading your reasons.']},
   {'h': 'Common faults', 'l': [
     'Reciting the law without applying it to the facts.',
     'Retelling the facts without stating a rule.',
     'Skipping the element that is actually in dispute.',
     'Answering a question that was not asked.']}],
  'try': ['Open any provision with a Self-test in its Understand step. Answer one question in four sentences: conclusion, rule, application, conclusion.']},

 'research': {'title': 'Find the law and cite it', 'mins': 7,
  'lead': 'Research is a short, repeatable routine: start from the provision, confirm its current text, find how the Court reads it, and record exactly where you found each thing.',
  'sections': [
   {'h': 'Know the rank of what you are reading', 'l': [
     'The Constitution controls everything below it: {civil:article-7}.',
     'Statutes, and treaties the Senate has concurred in ({const1987:art-vii-sec-21}). Generally accepted principles of international law are part of the law of the land ({const1987:art-ii-sec-2}).',
     'Administrative rules, valid only when not contrary to the laws or the Constitution.',
     'Decisions of the Supreme Court, which tell you what all of the above mean: {civil:article-8}.']},
   {'h': 'A routine that works', 'l': [
     'Read the provision in full, with its neighbours.',
     'Check whether it has been amended. In this app, amended text appears under the article with the amending law named.',
     'Find the leading case and the most recent case.',
     'Confirm the ruling still stands: look for a later en banc decision or a later statute.',
     'Write down the source and the date you checked it.']},
   {'h': 'Citing', 'p': [
     'Cite a recent case by title, docket number and date of promulgation; older cases are also cited to the Philippine Reports or the SCRA by volume and page. Cite a statute by its number and the section, and a code by its name and the article. Law schools here commonly follow the Philippine Manual of Legal Citations; use the form your professor or journal requires, and use it consistently.']},
   {'h': 'Honest sourcing', 'p': ['Never cite a decision you have not read. In this app each recent ruling is marked by how it was verified: against the decision itself, or only against a Supreme Court release or news report. Treat the second kind as a lead to follow, not as authority.']}],
  'try': ['Choose one provision from this week’s readings. Find its leading case and its latest case, and write both citations in full.']},

 'thesis': {'title': 'Write a legal thesis', 'mins': 8,
  'lead': 'A thesis is an argument, not a survey. It asks one question that the existing law leaves open and defends one answer.',
  'sections': [
   {'h': 'Start from a question, not a topic', 'p': ['“Cyber libel” is a topic. “Does the one-year prescriptive period for libel apply to cyber libel?” is a question. A good question is specific, open to more than one reasonable answer, and answerable with legal materials.']},
   {'h': 'Find the gap', 'l': [
     'A provision that is silent or ambiguous on a recurring problem.',
     'Decisions that cannot be reconciled.',
     'An old provision applied to new facts.',
     'A rule that works differently elsewhere, with lessons for ours.']},
   {'h': 'State your claim in one sentence', 'p': ['“Provision X should be read (or amended) to mean Y, because Z.” If you cannot write that sentence, you are not ready to draft.']},
   {'h': 'Choose and declare a method', 'l': [
     'Doctrinal: text, legislative history and decisions.',
     'Comparative: how other jurisdictions solve the same problem.',
     'Policy or empirical: what the rule does in practice.']},
   {'h': 'A structure readers expect', 'l': [
     'Introduction: the problem, the question, your claim, and a roadmap.',
     'Legal framework: the provisions, quoted exactly, and how they came to be.',
     'Analysis: the competing readings, the cases, your argument, and the strongest objections to it.',
     'Proposal: the reading you urge, or the amendment in draft form.',
     'Conclusion: what changes if you are right.']},
   {'h': 'Habits that protect you', 'l': [
     'Argue from the words of the provision first.',
     'State the opposing view at its strongest before answering it.',
     'Keep a source log from the first day. Cite every idea that is not yours and quote only what you must.']}],
  'try': ['In five lines, write your question, your one-sentence claim, and your three strongest sources.']},

 'intl-map': {'title': 'How international law enters Philippine law', 'mins': 6,
  'lead': 'A Philippine court applies international law only through the Constitution. Two doors matter most: incorporation and transformation.',
  'sections': [
   {'h': 'Incorporation', 'p': ['By {const1987:art-ii-sec-2}, the generally accepted principles of international law are part of the law of the land. No statute is needed. This is how custom and general principles reach our courts.']},
   {'h': 'Transformation', 'p': ['A treaty or international agreement is valid and effective here only with the concurrence the Constitution requires of the Senate: {const1987:art-vii-sec-21}. Foreign military bases, troops and facilities have their own, stricter clause: {const1987:art-xviii-sec-25}.']},
   {'h': 'When a treaty and a statute conflict', 'p': ['Courts first try to give effect to both. Where they cannot, neither outranks the other inside the Philippines merely by its kind, and the Constitution prevails over both. Your syllabus lists the cases to read on this: Secretary of Justice v. Lantion and Ichong v. Hernandez.']},
   {'h': 'Where international law itself comes from', 'p': ['Treaties, international custom, and general principles of law are the primary sources; judicial decisions and the teachings of publicists are subsidiary means of finding the rules. That list is taken from Article 38 of the Statute of the International Court of Justice, which your syllabus assigns.']},
   {'h': 'What is in this library', 'p': ['The constitutional clauses, and the Philippine statutes that carry out treaty obligations. The treaty texts themselves are not here yet.']}],
  'try': ['For each case in the first part of your PIL syllabus, say which door it came through: incorporation or transformation.']},

 'eth-frame': {'title': 'Why lawyers owe more than ordinary duties', 'mins': 8,
  'lead': 'Legal ethics is easier to learn as a set of answers to one question: whom does this duty protect? Start there, and the rules stop looking like a list.',
  'sections': [
   {'h': 'A privilege with conditions', 'p': ['The practice of law is not a right or an ordinary business. It is a privilege the State grants to those who show and keep the required learning and character, and the Supreme Court alone admits to it and disciplines within it: {const1987:art-viii-sec-5}.']},
   {'h': 'Four relationships', 'l': [
     'To society: obey the law, do not counsel its evasion, make legal services available.',
     'To the profession: uphold its integrity and deal fairly with other lawyers.',
     'To the courts: candour, respect, and no delay of justice.',
     'To the client: competence, diligence, loyalty and confidence.']},
   {'h': 'When duties collide', 'p': ['The lawyer is an officer of the court before being the client’s advocate. A client’s cause is pursued with full effort, but only by means the law and the truth allow. Most hard cases in your syllabus are a conflict between two of the four relationships; identify which two.']},
   {'h': 'A question worth keeping open', 'p': ['May a lawyer do for a client what would be wrong to do for oneself? The adversary system answers yes, within limits: you may press a lawful claim you personally dislike, and you may hold the other side to its proof. It does not license deceiving the court, suppressing evidence, or using procedure to harass.']},
   {'h': 'Discipline is its own kind of case', 'p': ['A disciplinary proceeding is neither civil nor criminal. Its purpose is to protect the public and the courts, not to punish or to compensate, which is why a complainant’s change of heart does not necessarily end it.']},
   {'h': 'Three codes, one idea', 'p': ['Lawyers are governed by the Code of Professional Responsibility and Accountability (2023); judges by the 2025 Code of Judicial Conduct and Accountability; court personnel by the 2025 Code of Conduct and Accountability for Court Officials and Personnel. Public officers generally answer to {const1987:art-xi-sec-1} and the statutes under it.']}],
  'try': ['For the next ethics case you read, answer four things: who owed the duty, to whom, what act breached it, and why that sanction.']},

 'eth-cpra': {'title': 'The CPRA in six canons', 'mins': 6,
  'lead': 'The Code of Professional Responsibility and Accountability (A.M. No. 22-09-01-SC, 2023) replaced the 1988 Code. It is organised into six canons. This is a map in our own words; study the official text for the wording.',
  'sections': [
   {'h': 'The six canons', 'l': [
     'Canon I, Independence. Professional judgment free of improper influence, including the lawyer’s own interests.',
     'Canon II, Propriety. Proper conduct in professional and personal dealings, including online.',
     'Canon III, Fidelity. Loyalty to the Constitution and the law, to the courts, and to the client: the lawyer-client relationship, conflicts of interest and confidences are here.',
     'Canon IV, Competence and Diligence. Service that is skilled, prompt and thorough.',
     'Canon V, Equality. Fair and equal treatment of every person, and access to justice.',
     'Canon VI, Accountability. How lawyers are disciplined: the procedure, the classes of offences and the sanctions.']},
   {'h': 'How to study it', 'p': ['Most cases in your syllabus were decided under the 1988 Code. For each, ask which of the six canons the same conduct would fall under today. That translation is a common examination question.']}],
  'try': ['Sort ten cases from your ethics syllabus under the six canons.']},

 'eth-judge': {'title': 'Judges: independence with accountability', 'mins': 5,
  'lead': 'A judge must be free to decide without fear, and must still answer for how the office is used. The Constitution sets both halves.',
  'sections': [
   {'h': 'Independence', 'p': ['Who may be appointed, and with what character: {const1987:art-viii-sec-7}. Security of tenure, and the Supreme Court’s exclusive power to discipline: {const1987:art-viii-sec-11}. No assignment to non-judicial bodies: {const1987:art-viii-sec-12}.']},
   {'h': 'Accountability', 'p': ['A decision must state the facts and the law on which it rests: {const1987:art-viii-sec-14}. Cases must be decided within fixed periods: {const1987:art-viii-sec-15}. Delay is the most common ground of discipline in the cases you will read.']},
   {'h': 'The current code', 'p': ['The 2025 Code of Judicial Conduct and Accountability (A.M. No. 25-04-04-SC) took effect on December 21, 2025 and applies to all incumbent justices and judges. Cases decided before then cite the earlier codes; note which code a decision applied.']}],
  'try': ['From memory, state the period within which each level of court must decide a case, then check {const1987:art-viii-sec-15}.']},

 'eth-public': {'title': 'Public office is a public trust', 'mins': 5,
  'lead': 'One sentence of the Constitution carries the whole subject. The statutes spell out what it demands.',
  'sections': [
   {'h': 'The principle', 'p': ['{const1987:art-xi-sec-1}. Read it slowly: it lists what officers owe the people, and each word has been litigated.']},
   {'h': 'The norms and the prohibitions', 'p': ['The Code of Conduct and Ethical Standards sets the norms in {ra6713:section-4} and the prohibited acts in {ra6713:section-7}. The Anti-Graft and Corrupt Practices Act lists corrupt practices in {ra3019:section-3}; recent acquittals turn on whether bad faith was “evident” or negligence “gross”.']},
   {'h': 'Disclosure', 'p': ['Assets, liabilities and net worth must be declared: {const1987:art-xi-sec-17} and {ra6713:section-8}.']},
   {'h': 'Removal', 'p': ['Impeachable officers and grounds are in {const1987:art-xi-sec-2}; the procedure and the one-year bar are in {const1987:art-xi-sec-3}, where the 2025 and 2026 rulings on the Vice President’s impeachment are filed.']}],
  'try': ['List the norms of conduct in RA 6713, Sec. 4 from memory, then check.']},
}

# --------------------------------------------------------------------------- the House of Law (memory palace)
# One building, drawn after the Supreme Court on Padre Faura (four columns, three doors, seven steps), read from the roof down. Each field of law has one place in it (a fixed place is a
# fixed cue), and each track inside a field is one object at that place.
PARTS = {
 'pol':   (1, 'pediment', 'Pediment', 'The pediment crowns the house, as the Constitution crowns the State.'),
 'craft': (2, 'inscription', 'Inscription', 'The Court’s motto carved above the columns: Batas at Bayan. Read the words closely before you argue from them.'),
 'lab':   (3, 'col1', 'First column', 'Four columns stand like sentries. The first: work, and the welfare of people in need.'),
 'civ':   (4, 'col2', 'Second column', 'The second pillar: persons, family, property and obligations.'),
 'com':   (5, 'col3', 'Third column', 'The third pillar: business, money and tax.'),
 'crim':  (6, 'col4', 'Fourth column', 'The fourth pillar: what the State may punish, and how much.'),
 'intl':  (7, 'doors', 'Three doors', 'Three great doors open onto the world.'),
 'eth':   (8, 'steps', 'Seven steps', 'Seven marble steps lead up to the Court. Every lawyer climbs them, and the house stands on them.'),
}
PICS = {
 'pol': ['The gold emblem of the scales at the centre of the pediment.', 'Three carved figures in the pediment: Congress, the President, the Court.', 'A ballot slipped into a crack in the stone.',
         'The flag on the roof.', 'A watchman standing on the cornice.', 'Rice terraces carved along the slopes of the pediment.', 'A lightning rod and a fire bell on the roof.'],
 'craft': ['Each carved letter, read one word at a time.', 'A chisel correcting a doubtful letter.', 'A row of case numbers carved under the words.',
           'An open book carved at the end of the band.', 'Court seals pressed along the cornice.'],
 'lab': ['A hard hat resting on the capital.', 'A pay envelope tucked into the fluting.', 'An apron and a passport hanging from a nail.', 'A safety net wrapped round the base.'],
 'civ': ['A thick red Civil Code resting on the capital.', 'A family portrait hung on the shaft.', 'A land title rolled inside the fluting.', 'House keys hanging on a hook.', 'A phone glowing on the column, signing a contract.'],
 'com': ['A company seal pressed into the capital.', 'A cheque, a policy and a share certificate pinned to the shaft.', 'A tax stamp the size of a door, pasted on the column.',
         'A vault door set into the base.', 'A lightbulb glowing at the top.'],
 'crim': ['Handcuffs hanging from the capital.', 'A clock carved into the shaft, counting the sentence.', 'A raised palm painted on the column: stop.', 'A small handprint at a child’s height.',
          'A sachet and a pistol locked in an iron cage at the base.', 'A bribe envelope slipped into the fluting.', 'A rope coiled tight round the column.', 'A forged cheque nailed to the shaft.',
          'A security camera bolted near the top.'],
 'intl': ['The two side doors: incorporation on the left, transformation on the right.', 'A dove carved over the centre door.', 'A passport stamp on a brass handle.', 'Treaties posted on the doors.'],
 'eth': ['The bottom step, where the oath is taken.', 'A lawyer’s pin set into the third step.', 'A gavel resting on the fifth step.', 'A badge of public office on the top step.'],
}
# places for an ordered list (a walk), from the roof down, left to right
LOCI = ['Flag', 'Pediment', 'Inscription', 'Left wing', 'First column', 'Left door', 'Second column', 'Centre door', 'Third column', 'Right door', 'Fourth column', 'Right wing', 'Statues', 'Seven steps']

LINK = re.compile(r'\{([a-z0-9]+):([a-z0-9-]+)\}')


def links(text):
    def rep(m):
        cid, pid = m.group(1), m.group(2)
        return f'⟦{cid}|{pid}|{plabel(cid, pid)}⟧'
    return LINK.sub(rep, text)


def main():
    homes = {}
    for f in FIELDS:
        for tr in f['tracks']:
            for it in tr['items']:
                if it['t'] == 'code' and not it.get('x'):
                    if it['id'] in homes:
                        raise SystemExit(f"{it['id']} has two homes: {homes[it['id']]} and {f['id']}")
                    homes[it['id']] = f['id']
                if it['t'] == 'lesson': assert it['id'] in LESSONS, it['id']
                if it['t'] == 'set': assert it['id'] in SETS, it['id']
    missing = sorted(set(CODES) - set(homes))
    if missing:
        raise SystemExit('codes without a field: ' + ', '.join(missing))
    for f in FIELDS:
        n, part, pname, hook = PARTS[f['id']]
        f.update({'n': n, 'part': part, 'pname': pname, 'hook': hook})
        assert len(PICS[f['id']]) == len(f['tracks']), f['id']
        for tr, pic in zip(f['tracks'], PICS[f['id']]):
            tr['pic'] = pic
    FIELDS.sort(key=lambda f: f['n'])
    sets = {}
    for sid, s in SETS.items():
        items = []
        k = len(s['items'])
        for j, (cid, pid, why) in enumerate(s['items']):
            p = prov(cid, pid)
            loc = LOCI[j] if k >= len(LOCI) else LOCI[round(j * (len(LOCI) - 1) / max(1, k - 1))]
            items.append({'c': cid, 'i': pid, 'l': plabel(cid, pid), 'cap': p.get('c') or '', 'why': why, 'loc': loc})
        sets[sid] = {'title': s['title'], 'blurb': s['blurb'], 'items': items}
    lessons = {}
    for lid, l in LESSONS.items():
        secs = []
        for s in l['sections']:
            secs.append({'h': s['h'], 'p': [links(x) for x in s.get('p', [])], 'l': [links(x) for x in s.get('l', [])]})
        lessons[lid] = {'title': l['title'], 'mins': l['mins'], 'lead': links(l['lead']), 'sections': secs, 'try': [links(x) for x in l.get('try', [])]}
    out = {'fields': FIELDS, 'homes': homes, 'sets': sets, 'lessons': lessons, 'focus': ['pol', 'crim', 'eth', 'intl']}
    js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    open(f'{SITE}/curriculum.json', 'w').write(js)
    cat = json.load(open(f'{SITE}/catalog.json'))
    cat['chash'] = hashlib.md5(js.encode()).hexdigest()[:10]
    json.dump(cat, open(f'{SITE}/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    words = sum(len((' '.join(s.get('p', []) + s.get('l', []))).split()) for l in LESSONS.values() for s in l['sections'])
    print(f"fields {len(FIELDS)} · codes placed {len(homes)}/{len(CODES)} · sets {len(sets)} · lessons {len(lessons)} (~{words} words)")
    for f in FIELDS:
        print(' ', f['id'], [len(t['items']) for t in f['tracks']])


if __name__ == '__main__':
    main()
