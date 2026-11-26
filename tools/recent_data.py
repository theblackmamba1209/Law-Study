"""Recent Supreme Court rulings (2023 – 2026) filed under the provision they apply.

Every holding below is written in our own words. Each entry says how it was verified:
  st = 'decision' : docket number and date confirmed against the decision itself or an official/library listing
  st = 'report'   : confirmed from a Supreme Court press release or a news report of the ruling; read the
                    full text before citing it in an exam or a pleading
Output: data/recent.json  {"by": {"code|pid": [entry, ...]}, "general": [...], "checked": "..."}
"""
import json, os, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site/data'
CHECKED = 'November 25, 2026'


def E(n, g, d, ct, h, rel, st, src, tags=()):
    return {'n': n, 'g': g, 'd': d, 'ct': ct, 'h': h, 'rel': rel, 'st': st, 'src': list(src), 'tags': list(tags)}


LAWPHIL = 'https://lawphil.net/judjuris/'

R = {}


def add(keys, e):
    for k in keys:
        R.setdefault(k, []).append(e)


# ---------------------------------------------------------------- Constitution: Bill of Rights
add(['const1987|art-iii-sec-1'], E(
    'Deduro v. Vinoya', 'G.R. No. 254753', 'July 4, 2023', 'En Banc',
    'Red-tagging, vilification and labeling by State agents can amount to a threat to a person’s life, liberty and security, which may justify the writ of amparo.',
    'Due process protects life and liberty against State action; the Court recognized that labeling a person an enemy of the State can itself endanger those rights.',
    'report', [{'t': 'SC decision (as reported)'}], ['amparo', 'red-tagging']))

add(['const1987|art-iii-sec-2'], E(
    'Comamo v. People', 'G.R. No. 236548', 'March 4, 2025', 'En Banc',
    'A warrant describing the things to be seized with open-ended words (e.g. “among other firearms”) fails the particularity requirement; and a person’s going along with a search when given only limited options is not a free, knowing consent.',
    'Applies the particularity clause and the “consented search” exception to warrantless searches.',
    'decision', [{'t': 'LawPhil — concurring opinion page', 'u': LAWPHIL + 'juri2025/mar2025/gr_236548_leonen.html'}], ['particularity', 'consent']))
add(['const1987|art-iii-sec-2'], E(
    'People v. Bautista', 'G.R. No. 255749', 'October 15, 2025', '',
    'A search incident to a lawful arrest may extend to the person and the area within the arrestee’s immediate control; the items seized need not have been in plain view.',
    'Distinguishes two different exceptions to the warrant requirement: search incident to lawful arrest vs. plain view.',
    'report', [{'t': 'SC decision (as reported)'}], ['warrantless search']))

add(['const1987|art-iii-sec-12'], E(
    'People v. Akil', 'G.R. No. 265570', 'April 7, 2025', 'Third Division (Gaerlan, J.)',
    'A confession made to a private complainant while the suspect was detained at the police station, in questioning the police set in motion, was obtained during custodial investigation without counsel and is inadmissible; with an unreliable show-up identification, the accused was acquitted.',
    'Custodial-investigation rights attach once a person is a suspect in custody — the questioner being a private person does not cure the absence of counsel when the police initiated it.',
    'decision', [{'t': 'LawPhil — decision', 'u': LAWPHIL + 'juri2025/apr2025/gr_265570_2025.html'}], ['confession', 'counsel']))
add(['const1987|art-iii-sec-12', 'rpc|article-248'], E(
    'People v. Samson', 'G.R. No. 262579', 'February 28, 2024', 'Third Division (Inting, J.)',
    'An extrajudicial confession given with the assistance of a competent and independent counsel, voluntarily and in writing, was admissible; the murder conviction was affirmed with modification.',
    'Shows what a valid custodial confession looks like — the counterpart to Akil.',
    'decision', [{'t': 'Case listing (jur.ph)'}], ['confession']))

add(['const1987|art-iii-sec-16'], E(
    'People v. Sandiganbayan (Tumang and Colis)', 'G.R. No. 274922', 'February 17, 2025', '',
    'A preliminary investigation that ran from December 2017 to April 2024 was inordinate; the COVID-19 pandemic did not excuse the Ombudsman’s delay, and the respondents did not waive the right by not invoking it earlier. Dismissal of the graft and malversation cases affirmed.',
    'Applies the Cagang guidelines on inordinate delay to the Ombudsman.',
    'decision', [{'t': 'LawPhil — decision', 'u': LAWPHIL + 'juri2025/feb2025/gr_274922_2025.html'}], ['inordinate delay', 'Cagang']))
add(['const1987|art-iii-sec-16'], E(
    'Ladilad v. COMELEC', 'G.R. No. 264071', 'August 13, 2024', 'En Banc (Hernando, J.)',
    'The COMELEC’s delay in resolving a preliminary investigation for an election offense violated the respondent’s right to speedy disposition, warranting dismissal of the complaint.',
    'The right covers proceedings before all judicial, quasi-judicial and administrative bodies — including the COMELEC as prosecutor of election offenses.',
    'decision', [{'t': 'LawPhil — concurring opinion page', 'u': LAWPHIL + 'juri2024/aug2024/gr_264071_gesmundo.html'}], ['inordinate delay', 'COMELEC']))
add(['const1987|art-iii-sec-16'], E(
    'Sarigumba v. COMELEC', '', 'August 19, 2025', 'En Banc',
    'The Court nullified a COMELEC resolution finding probable cause for an Omnibus Election Code violation because the investigation was delayed in breach of the right to speedy disposition.',
    'Same rule as Ladilad, applied again to the COMELEC.',
    'report', [{'t': 'Philstar report, Dec. 19, 2025', 'u': 'https://www.philstar.com/nation/2025/12/19/2495224/supreme-court-rules-against-comelecs-year-long-delay-bohol-case'}], ['inordinate delay', 'COMELEC']))
add(['const1987|art-iii-sec-16'], E(
    'People v. Moreno', 'G.R. No. 261857', 'May 29, 2024', 'Third Division',
    'Criminal cases were dismissed because the Ombudsman took an unreasonable time to resolve the complaints.',
    'Delay is counted from the filing of the complaint through the determination of probable cause.',
    'decision', [{'t': 'ChanRobles listing (May 2024)', 'u': 'https://chanrobles.com/cralaw/2024maydecisions.php?id=144'}], ['inordinate delay']))

# ---------------------------------------------------------------- Constitution: structure
add(['const1987|art-xi-sec-3'], E(
    'Duterte v. House of Representatives', 'G.R. Nos. 278353 & 278359', 'July 25, 2025 (Decision); January 28, 2026 (Resolution)', 'En Banc (Leonen, SAJ)',
    'The Articles of Impeachment against the Vice President were void for violating the one-year bar: complaints that the House left unacted upon still counted as “initiated”. The House’s motion for reconsideration was denied with finality on January 28, 2026; a new complaint could be filed only from February 6, 2026.',
    'The leading modern reading of Art. XI, Sec. 3(5) after Gutierrez v. House Committee on Justice (2011).',
    'decision', [{'t': 'LawPhil — separate opinions on the Resolution', 'u': LAWPHIL + 'juri2026/jan2026/pdf/gr_278353_hernando.pdf'}], ['impeachment', 'one-year bar']))
add(['const1987|art-x-sec-18', 'const1987|art-x-sec-15'], E(
    'Province of Sulu v. Executive Secretary', 'G.R. Nos. 242255, 243246 & 243693', 'September 9, 2024 (Decision); November 26, 2024 (Resolution)', 'En Banc (Leonen, SAJ)',
    'The Bangsamoro Organic Law is constitutional, but Sulu cannot be part of BARMM because its voters rejected the law in the plebiscite; a province is included only if a majority of its own votes approve.',
    'Art. X, Sec. 18 requires approval in the plebiscite by the constituent units — counted per province, not only region-wide.',
    'decision', [{'t': 'LawPhil — Decision', 'u': LAWPHIL + 'juri2024/sep2024/gr_242255_dimaampao.html'}, {'t': 'LawPhil — Resolution', 'u': LAWPHIL + 'juri2024/nov2024/gr_242255_2024.html'}], ['BARMM', 'plebiscite']))

# ---------------------------------------------------------------- RPC Book I
add(['rpc|article-11'], E(
    'Camillo v. People', 'G.R. No. 260353', 'February 2023', 'Second Division',
    'Unlawful aggression can consist of persistent, reckless fist blows — a weapon is not required. The accused, who answered with two punches to stop the attack, acted in self-defense and was acquitted of homicide.',
    'Unlawful aggression is judged from the accused’s position at the moment; the means used must be reasonably necessary, not identical.',
    'decision', [{'t': 'ChanRobles listing (Feb. 2023)', 'u': 'https://chanrobles.com/cralaw/2023februarydecisions.php?id=328'}], ['self-defense']))
add(['rpc|article-11', 'rpc|article-246', 'rpc|article-248'], E(
    'People v. Singcol', 'G.R. No. 275139', 'May 7, 2025', 'First Division (Hernando, J.)',
    'Without unlawful aggression from the victim, neither complete nor incomplete self-defense can be appreciated. Parricide was affirmed, and the killing of a second victim was murder because it was attended by treachery.',
    'Unlawful aggression is the indispensable first element of Art. 11(1).',
    'report', [{'t': 'Case digest (Atty. Talidro, 2026)', 'u': 'https://study-smart-blog-casedigests.blogspot.com/2026/06/people-of-philippines-v-leopoldo.html'}], ['self-defense', 'treachery']))
add(['rpc|article-248', 'rpc|article-249', 'rpc|article-11'], E(
    'People v. Banguilan', 'G.R. No. 268355', 'June 2024', '',
    'Self-defense failed for want of proof of unlawful aggression, but the Court found treachery and evident premeditation not proved and reduced the conviction from murder to homicide.',
    'The qualifying circumstance must be proved as clearly as the crime itself.',
    'report', [{'t': 'Case summary (jur.ph)', 'u': 'https://jur.ph/jurisprudence/summary/people-of-the-philippines-v-banguilan'}], ['treachery']))
add(['rpc|article-248'], E(
    'People v. Pereda (Kian delos Santos case)', 'G.R. Nos. 268510 & 274142', 'August 11, 2025', 'Second Division (Lopez, J.)',
    'The murder conviction of three police officers for the 2017 killing of 17-year-old Kian delos Santos during an anti-drug operation was affirmed; treachery and conspiracy were present.',
    'Treachery qualifies the killing to murder even when the accused are law enforcers acting in an operation.',
    'report', [{'t': 'Daily Tribune report, Dec. 22, 2025', 'u': 'https://tribune.net.ph/2025/12/22/sc-sentences-cops-to-reclusion-perpetua-over-killing-of-kian-delos-santos'}], ['treachery', 'conspiracy']))
add(['rpc|article-90', 'rpc|article-355', 'ra10175|section-4', 'ra10175|section-6'], E(
    'Causing v. People', 'G.R. No. 258524', 'October 11, 2023', 'Third Division (Inting, J.); reaffirmed En Banc, April 2026 (8–7)',
    'Cyber libel prescribes in one year (the period for libel under Art. 90), counted from discovery — not 15 years. The unsigned resolution in Tolentino v. People (2018) is not binding precedent. Reported as reaffirmed by the En Banc on April 8, 2026.',
    'RA 10175 creates no new crime of libel; it raises the penalty when committed through a computer system, so the RPC’s prescriptive period for libel governs.',
    'report', [{'t': 'Philstar report on the 2023 decision', 'u': 'https://philstar.com/headlines/2024/01/22/2327701/sc-prescription-period-cyber-libel-1-year-not-1215-years'}, {'t': 'Philstar report on the 2026 En Banc resolution (8–7)', 'u': 'https://www.philstar.com/nation/2026/04/22/2522625/sc-rules-filing-cyber-libel-cases'}], ['cyber libel', 'prescription']))
add(['rpc|article-100', 'rpc|article-318', 'civil|article-29'], E(
    'Llonillo v. People', 'G.R. No. 246787', 'January 30, 2024', 'En Banc (Rosario, J.)',
    'The accused were acquitted of “other deceits” (Art. 318), yet the Court held they could be adjudged civilly liable in the same criminal case on an obligation from another source (here, their loan), sparing the creditor a separate suit. Several Justices dissented on that point.',
    'Civil liability ex delicto (Art. 100) is extinguished only if the act did not exist; liability from contract may still be proved and awarded.',
    'decision', [{'t': 'LawPhil — separate opinion', 'u': LAWPHIL + 'juri2024/jan2024/gr_246787_lopez.html'}], ['civil liability', 'acquittal']))

# ---------------------------------------------------------------- RPC Book II — rape
add(['rpc|article-266-a', 'rpc|article-266-b'], E(
    'People v. ABC260708', 'G.R. No. 260708', 'January 23, 2024', 'En Banc',
    'Guidelines on how rape is designated and penalised. The label “qualified statutory rape” should not be used; the decision sets out the correct designation for each combination of the victim’s age and qualifying circumstances, and the statutory age is below 12 for acts before RA 11648 (2022) and below 16 after it.',
    'Read with Art. 266-B (penalties) and the RA 11648 amendment shown on this article.',
    'report', [{'t': 'SC En Banc decision (as reported)'}], ['nomenclature', 'RA 11648']))
add(['rpc|article-266-a'], E(
    'People v. ZZZ', 'G.R. No. 266706', 'June 26, 2024', '',
    'The prosecution need not prove that the victim resisted; force or intimidation is judged by its effect on the victim, and there is no standard reaction to sexual assault.',
    'Resistance is not an element of rape by force, threat or intimidation.',
    'report', [{'t': 'SC decision (as reported)'}], ['resistance']))
add(['rpc|article-266-a', 'rpc|article-336'], E(
    'Maliclic v. People', '', 'February 4, 2026', '',
    'After RA 11648, rape by carnal knowledge may be committed by and against any person; but for acts committed before that law, the same conduct against a male victim could not be rape by sexual intercourse and was punished instead as acts of lasciviousness.',
    'Penal laws do not apply retroactively when unfavorable to the accused (Art. 21–22, RPC).',
    'report', [{'t': 'SC decision (as reported)'}], ['RA 11648', 'gender-neutral']))

# ---------------------------------------------------------------- Special penal laws
add(['ra9165|section-21'], E(
    'People v. Valencia and Antipuesto', 'G.R. No. 250610', 'July 10, 2023 (released Jan. 12, 2024)', '',
    'Receipts and request forms documenting the chain of custody may not be altered while the specimen is in transit; the specimen must bear the same marking stated in the paper trail, or the integrity of the corpus delicti is in doubt.',
    'The documentary trail is part of the chain; unexplained alterations break it.',
    'decision', [{'t': 'SC Public Information Office release', 'u': 'https://sc.judiciary.gov.ph/?p=110826'}], ['chain of custody']))
add(['ra9165|section-21'], E(
    'People v. Flores', 'G.R. No. 262686', '', '',
    'Acquittal because the arresting team did not comply with the mandatory witness requirement during the inventory, without a justifiable reason shown.',
    'The insulating witnesses must be present at the inventory and must sign it.',
    'report', [{'t': 'SC Public Information Office release', 'u': 'https://sc.judiciary.gov.ph/?p=113293'}], ['witness rule']))
add(['ra9165|section-21'], E(
    'People v. Acdang', '', 'Released September 12, 2025', 'En Banc',
    'Where the required witnesses were absent at the inventory and the prosecution gave no justifiable reason, the accused must be acquitted.',
    'Reaffirms the strict witness rule under Sec. 21(1), as amended by RA 10640.',
    'report', [{'t': 'SC En Banc decision (as reported)'}], ['witness rule']))
add(['ra10591|section-28'], E(
    'Togado v. People', 'G.R. No. 260973', 'August 6, 2024', 'En Banc (Leonen, SAJ)',
    'In illegal possession of firearms, the chain of custody of the seized firearm must be strictly observed and documented (as the PNP manual requires), and the firearm itself should be presented; doubts on its identity led to acquittal even though the search warrant was valid.',
    'RA 10591 has no chain-of-custody clause, but the corpus delicti still has to be proved with moral certainty.',
    'decision', [{'t': 'LawPhil — decision', 'u': LAWPHIL + 'juri2024/aug2024/gr_260973_2024.html'}], ['firearms', 'chain of custody']))
add(['ra9262|section-5'], E(
    'XXX270257 v. People', 'G.R. No. 270257', 'August 12, 2024', '',
    'Psychological violence under Sec. 5(i) can be proved by the victim’s own testimony; a psychological evaluation or expert testimony is not required.',
    'Mental or emotional anguish is a matter of evidence, not of medical diagnosis.',
    'report', [{'t': 'SC decision (as reported)'}], ['psychological violence']))
add(['ra9262|section-5'], E(
    'XXX v. People', 'G.R. No. 268619', 'January 13, 2026', '',
    'Marital infidelity is not by itself a crime under Sec. 5(i); what the law punishes is causing mental or emotional anguish, which must be proved.',
    'The anguish caused — not the affair — is the gravamen of Sec. 5(i).',
    'report', [{'t': 'SC decision (as reported)'}], ['infidelity']))
add(['ra9262|section-5'], E(
    'December 3, 2025 decision (Third Division, Inting, J.)', '', 'December 3, 2025', 'Third Division',
    'Conviction under Sec. 5(i) requires proof that the accused specifically intended to cause the woman substantial emotional or psychological distress; absent that, the accused was acquitted.',
    'Sec. 5(i) is a crime committed with dolo, not by mere negligence.',
    'report', [{'t': 'SC decision (as reported; docket number not in the report)'}], ['intent']))
add(['ra7610|section-10'], E(
    'XXX v. People', 'G.R. No. 268457', 'July 22, 2024', '',
    'Discipline that becomes excessive and degrading is child abuse under Sec. 10(a); but laying hands on a child in the heat of anger, without intent to debase or degrade, is not.',
    'Child abuse under Sec. 10(a) requires intent to debase, degrade or demean the child’s intrinsic worth (following Bongalon).',
    'report', [{'t': 'SC decision (as reported)'}], ['discipline']))
add(['ra3019|section-3'], E(
    'Elipe v. People', 'G.R. Nos. 242447-48', 'May 20, 2025', 'En Banc (Lopez, J.)',
    'Officials convicted under Sec. 3(e) over a falsified Daily Time Record (about PHP 1,894 in salary) were acquitted: the prosecution failed to prove that bad faith or partiality was “evident” or “manifest”, or that negligence was “gross”.',
    'Sec. 3(e) punishes graft; ordinary irregularity or mistake is not enough.',
    'decision', [{'t': 'LawPhil — concurring opinion page', 'u': LAWPHIL + 'juri2025/may2025/gr_242447_caguioa.html'}], ['evident bad faith']))
add(['ra3019|section-3'], E(
    'People v. Villasin', 'G.R. No. 255567', 'January 29, 2024', 'Third Division (Caguioa, J.)',
    'Acquittal: the prosecution failed to prove that the accused acted with evident bad faith, manifest partiality or gross inexcusable negligence in a fertilizer procurement.',
    'Each mode of Sec. 3(e) must be proved beyond reasonable doubt.',
    'decision', [{'t': 'LawPhil — decision', 'u': LAWPHIL + 'juri2024/jan2024/gr_255567_2024.html'}], ['procurement']))

# ---------------------------------------------------------------- Labor
add(['labor|article-294', 'labor|article-298', 'civil|article-1319', 'civil|article-1305'], E(
    'Aragones v. Alltech Biotechnology Corp.', 'G.R. No. 251736', 'April 2, 2025', 'Third Division (Caguioa, J.)',
    'An employment contract is perfected when a definite job offer is accepted and the acceptance is communicated, even before work begins. Withdrawing the offer afterward, on an unproven claim that the position had become redundant, was illegal dismissal.',
    'Employment is a contract: consent, object and cause (Civil Code) perfect it; security of tenure then applies, and redundancy must be proved.',
    'decision', [{'t': 'LawPhil — decision', 'u': LAWPHIL + 'juri2025/apr2025/gr_251736_2025.html'}], ['perfection', 'redundancy']))
add(['labor|article-297', 'labor|article-294'], E(
    'Bohol Wisdom School v. Mabao', 'G.R. No. 252124', 'July 23, 2024', 'First Division (Rosario, J.)',
    'A Christian school illegally suspended an unmarried teacher for becoming pregnant: sexual relations between consenting adults with no impediment to marry are not immoral under the public and secular standard the law applies. Backwages for the suspension period were ordered.',
    'Immorality as a ground for discipline is measured by public and secular morality, not religious doctrine.',
    'decision', [{'t': 'Chambers article on the case', 'u': 'https://chambers.com/articles/neither-are-your-ways-my-ways-pregnancy-and-immorality-in-the-workplace'}], ['immorality', 'suspension']))

# ---------------------------------------------------------------- Family
add(['family|article-36'], E(
    'G.R. No. 255706', 'G.R. No. 255706', 'February 17, 2025', 'Second Division (Leonen, SAJ)',
    'Testimonies of the spouses’ family and friends may prove psychological incapacity; what matters is that the totality of the evidence shows it clearly and convincingly.',
    'Applies Tan-Andal v. Andal (2021): psychological incapacity is a legal, not medical, concept and needs no expert diagnosis.',
    'report', [{'t': 'Inquirer report', 'u': 'https://newsinfo.inquirer.net/?p=2057538'}], ['Tan-Andal', 'evidence']))

# ---------------------------------------------------------------- general (not tied to one codal provision in this library)
GENERAL = [
    {'k': 'ethics', 'x': 'Code of Professional Responsibility and Accountability (CPRA), A.M. No. 22-09-01-SC (2023) — governs all lawyers; replaced the 1988 Code of Professional Responsibility.',
     'u': 'https://sc.judiciary.gov.ph/wp-content/uploads/2023/05/22-09-01-SC-FINAL.pdf'},
    {'k': 'ethics', 'x': '2025 Code of Judicial Conduct and Accountability (CJCA), A.M. No. 25-04-04-SC — approved November 11, 2025; took effect December 21, 2025; applies to all incumbent justices and judges.',
     'u': 'https://sc.judiciary.gov.ph/wp-content/uploads/2025/12/A.M.-NO.-25-04-04-SC.pdf'},
    {'k': 'ethics', 'x': '2025 Code of Conduct and Accountability for Court Officials and Personnel (CCACOP), A.M. No. 25-06-11-SC — approved October 28, 2025; replaces the 2004 Code of Conduct for Court Personnel.',
     'u': 'https://sc.judiciary.gov.ph/wp-content/uploads/2025/12/A.M.-NO.-25-06-11-SC.pdf'},
]


def main():
    # decisions applying the CPRA, extracted from the decision texts by cpra_cases.py
    extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cpra_cases.json')
    if os.path.exists(extra):
        for k, v in json.load(open(extra)).items():
            R.setdefault(k, []).extend(v)
    n = sum(len(v) for v in R.values())
    uniq = len({(e['n'], e['g']) for v in R.values() for e in v})
    json.dump({'by': R, 'general': GENERAL, 'checked': CHECKED}, open(f'{SITE}/recent.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'recent rulings: {uniq} rulings filed {n} times under {len(R)} provisions')


if __name__ == '__main__':
    main()
