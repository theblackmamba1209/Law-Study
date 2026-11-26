"""Study notes, in our own words, for the CPRA, the notarial rules, and the AEP and immigration provisions.

Fields per provision:  x  plain meaning      k  key points / elements      t  exam traps      w  why it exists
                       o  closest rule of the 1988 Code of Professional Responsibility (most pre-2023 cases cite it)
                       i  implementing rules and issuances: [{t: title, s: what it does (our words), u: link}]
                       d  case digests (our words)
Writes data/notes/cpra.json and data/notes/notarial.json; merges into data/notes/labor.json and data/notes/ca613.json.
"""
import json, os, hashlib

SITE = '/home/claude/site/data'

ULAS = {'t': 'Rules on the Unified Legal Aid Service (ULAS), A.M. No. 22-11-01-SC (in force February 3, 2025)',
        's': 'Requires every lawyer to render free legal aid each compliance period (or pay in lieu where allowed), and organizes legal aid through the IBP and accredited providers. It replaced the 2009 Rule on Mandatory Legal Aid Service (B.M. No. 2012).',
        'u': 'https://sc.judiciary.gov.ph/'}
MCLE = {'t': 'Mandatory Continuing Legal Education, B.M. No. 850, as amended',
        's': 'Every practising lawyer must complete the required MCLE units each compliance period; non-compliance makes the lawyer a delinquent member and pleadings must state the MCLE compliance number.',
        'u': 'https://sc.judiciary.gov.ph/'}
CLEP = {'t': 'Revised Law Student Practice Rule (Rule 138-A) and the Clinical Legal Education Program, A.M. No. 19-03-24-SC',
        's': 'Lets certified law students appear and give limited legal services under a supervising lawyer through a law school’s clinic; the clinic director and supervising lawyer answer for the students’ work.',
        'u': 'https://sc.judiciary.gov.ph/'}
NOTARIAL = {'t': '2004 Rules on Notarial Practice, A.M. No. 02-8-13-SC', 's': 'Who may notarize, what a notary may not do (e.g., notarize without the signatory’s personal appearance), the notarial register, and sanctions. Violations are also violations of the lawyer’s oath and the CPRA.', 'u': '#/code/notarial'}
REMOTE = {'t': '2020 Rules on Remote Notarization of Paper Documents, A.M. No. 20-07-04-SC', 's': 'Allows notarization over videoconference under strict conditions: the signatory must be seen and identified in real time, and the paper document must reach the notary.', 'u': '#/code/remotenot'}
CPRA_GP = {'t': 'CPRA, General Provisions, Sec. 1 (transitory provision)', 's': 'The CPRA applies to all pending and future cases, unless the Court finds that applying it to a pending case would be unfeasible or unjust; then the 1988 Code applies.', 'u': '#/p/cpra/gp-sec-1'}

N = {}
def n(pid, x, k=None, t=None, w=None, o=None, i=None, d=None):
    e = {'x': x}
    if k: e['k'] = k
    if t: e['t'] = t
    if w: e['w'] = w
    if o: e['o'] = o
    if i: e['i'] = i
    if d: e['d'] = d
    N[pid] = e

# ---------------------------------------------------------------- the frame
n('preamble', 'The Preamble states the theory of the whole Code: an ethical lawyer is a lawyer of integrity, and integrity is shown through six values that become the six Canons — independence, propriety, fidelity, competence and diligence, equality, and accountability. A lawyer serves in four capacities at once: citizen, member of the profession, officer of the court, and the client’s fiduciary.',
  k=['Six Canons: I Independence, II Propriety, III Fidelity, IV Competence and Diligence, V Equality, VI Accountability.',
     'Four roles of a lawyer: citizen (allegiance to the Constitution and laws), member of the profession, officer of the court, and representative of the client (fiduciary).',
     'Breach of the Code results in sanctions; Canon VI sets the procedure and penalties.'],
  t=['Do not confuse the CPRA (2023, six Canons with numbered Sections) with the 1988 CPR (22 Canons with Rules). Citations like “Canon III, Section 6” are CPRA; “Canon 16, Rule 16.01” is the old Code.'],
  w='The 1988 Code was rules-based. The CPRA is values-based, so that conduct not foreseen by a specific rule can still be judged against the value it offends.', i=[CPRA_GP])
n('lawyers-oath', 'The Revised Lawyer’s Oath replaces the oath in Rule 138. The new lawyer accepts practice as an honor and a responsibility, declares fealty to the Constitution, and promises to work for the rule of law, truth, justice and the rights of all persons, without discrimination, with integrity and competence.',
  k=['Taken before admission; violating it is itself a ground for discipline.', 'Has a version for oaths (“So help me, God”) and one for affirmations.'],
  t=['The old oath (“I will do no falsehood… I will delay no man for money or malice”) is superseded, but cases decided under it remain good law on the duties it expressed.'],
  o='Lawyer’s Oath, Rule 138, Sec. 17 (superseded)')
n('gp-sec-1', 'The CPRA governs every case, pending or new, from its effectivity (May 29, 2023). The Court may apply the old 1988 Code to a pending case only if applying the CPRA would be unfeasible or would work an injustice.',
  t=['Many 2023–2025 decisions cite the CPRA even for acts done before 2023, because of this provision.'], o='—')
n('gp-sec-2', 'Repeals the 1988 Code of Professional Responsibility, Sections 20 to 37 of Rule 138 (duties of attorneys, fees, liens, discipline grounds) and Rule 139-B (disbarment procedure), and supersedes the old Lawyer’s Oath. Inconsistent issuances and doctrines are modified accordingly.',
  t=['Rule 138, Sec. 27 (grounds for disbarment) is among the repealed sections; grounds now come from Canon VI, Secs. 33–35.'])

# ---------------------------------------------------------------- Canon I — Independence
n('canon-i', 'Independence means the lawyer acts free from improper influence, pressure or interference — from the client, from government, from anyone — because effective representation and the rule of law depend on it.', o='Canons 13 and 15 (in part)')
n('canon-i-sec-2', 'Win on the merits only. A lawyer may not use, or appear to use, influence over a court or agency, and may not undermine its authority.',
  k=['Two prohibitions: exerting influence, and giving the appearance of influence.', 'Covers courts, tribunals and every government agency.'],
  t=['The appearance alone is enough: bragging of connections with a judge is sanctionable even if no influence was actually exerted (see also Canon II, Sec. 15).'],
  o='Canon 13 (rely on the merits; refrain from impropriety that tends to influence the court)')
n('canon-i-sec-4', 'A lawyer may not get a branch, office or officer of government to interfere in a case before a court or agency, unless a law or the court allows it.', o='Rule 13.01 and Canon 6 (in part)')
n('canon-i-sec-5', 'The client decides the objectives; the lawyer, after consulting the client, decides the procedure and the means — which motions to file, which witnesses to call — and is not bound to follow a client’s instruction that is unlawful or that would compromise the lawyer’s independence.',
  t=['Matters of procedure belong to the lawyer, but settlement, compromise and other acts that give away the client’s substantive rights need the client’s authority (Canon III, Sec. 4).'], o='Rule 19.03')

# ---------------------------------------------------------------- Canon II — Propriety
n('canon-ii', 'Propriety means conduct that is proper and that looks proper, in public and in private life. It is the Canon most often invoked in discipline.', o='Canons 1, 7, 8, 10 and 11')
n('canon-ii-sec-1', 'A lawyer must not engage in conduct that is unlawful, dishonest, immoral or deceitful. It applies to private conduct as well as professional work: the question is whether the act shows the lawyer unfit to be trusted with the duties of the profession.',
  k=['Unlawful: contrary to law (a conviction is not required).', 'Dishonest: lying, cheating, or stealing.', 'Immoral: conduct so corrupt or shameless that it offends the community; disbarment needs gross immorality.', 'Deceitful: misleading another to his or her damage.'],
  t=['Acquittal in a criminal case does not bar discipline: the proof needed is only substantial evidence (Canon VI, Sec. 32).', 'Failure to pay a just debt and issuing bouncing checks have been punished under this rule.'],
  o='Rule 1.01 (no unlawful, dishonest, immoral or deceitful conduct)')
n('canon-ii-sec-2', 'A lawyer must respect the law, the courts and agencies, their officials and staff, and the people who appear before them, and must not act in a way that reflects badly on fitness to practise or behave scandalously, in public or in private.',
  o='Canon 11 (respect for courts) and Rule 7.03 (conduct that adversely reflects on fitness)')
n('canon-ii-sec-3', 'A lawyer must not create or promote an unsafe or hostile environment, in or out of work, and must not commit physical, sexual, psychological or economic abuse or violence, including sexual harassment.', t=['New in the CPRA: abuse and harassment are named expressly, including online.'], o='—')
n('canon-ii-sec-4', 'Use dignified, gender-fair, child- and culturally-sensitive language in pleadings, in court and online. Abusive, intemperate or offensive language is forbidden.',
  t=['Vigorous advocacy is allowed; insults are not. Strong words in a pleading that attack the person rather than the argument are sanctioned.'],
  o='Rule 8.01 (no abusive, offensive or improper language)', i=[{'t': 'Rules on the Use of Gender-Fair Language in the Judiciary, A.M. No. 21-11-25-SC', 's': 'Sets the gender-fair language courts and lawyers should use in court documents and proceedings.', 'u': 'https://sc.judiciary.gov.ph/'}])
n('canon-ii-sec-8', 'Never mislead a court or agency: do not misquote or misrepresent the contents of a document, the opposing counsel’s argument, a decision or the law, and do not cite as law something that has been repealed or never existed.',
  t=['Citing a non-existent case or a fabricated quotation — including text produced by an AI tool and not checked — falls squarely here.'],
  o='Rules 10.01 and 10.02 (no falsehood; no misquoting or misrepresenting authorities)')
n('canon-ii-sec-11', 'A lawyer must not make false representations or statements, including in demand letters, and must correct false or inaccurate statements made in bar applications, pleadings or submissions.',
  t=['A demand letter that threatens unfounded criminal or administrative charges to collect a civil debt is itself a violation.'], o='Rule 10.01; Rule 7.01')
n('canon-ii-sec-15', 'A lawyer must keep a proper distance from court and agency personnel. Familiarity that gives an appearance of influence or favor must be avoided, and claiming influence is forbidden.', o='Rule 13.01 and Canon 13')
n('canon-ii-sec-17', 'No soliciting legal business, directly or indirectly. Advertising is allowed only if dignified, verifiable and factual (biographical data, contact details, fields of practice, services) and never self-laudatory. No paying media, award-giving bodies or personalities for publicity.',
  k=['Solicitation: prohibited outright.', 'Advertising: allowed within limits — dignified, verifiable, factual, not self-laudatory, any platform.', 'Paying for publicity or awards: prohibited.'],
  t=['The 1988 Code allowed only a narrow list of ads (Rule 3.01, 2.03). The CPRA is more liberal on platforms but keeps the ban on self-praise and on paid publicity.'],
  o='Rules 2.03 and 3.01 to 3.05', d=[{'n': 'Linsangan v. Tolentino', 'c': 'A.C. No. 6672, September 4, 2009', 'h': 'A lawyer who used agents to approach seafarers and persuade them to transfer their cases to him was suspended. Soliciting through others is still solicitation, and law is a profession, not a trade.', 'r': 'The standard case on “ambulance chasing”.'}])
n('canon-ii-sec-19', 'Sub judice rule: while a case is pending, a lawyer must not make public statements that would prejudge it, sway public opinion, or obstruct the administration of justice.', o='Rule 13.02')
n('canon-ii-sec-29', 'A lawyer who left government may not accept engagement in any matter in which he or she intervened while in government service.',
  t=['The bar is tied to the specific “matter” handled in government, not to every case against the former agency.', 'Read with Sec. 7(b) of RA 6713 (one-year bar on private practice connected with one’s former office).'],
  o='Rule 6.03', d=[{'n': 'PCGG v. Sandiganbayan', 'c': 'G.R. Nos. 151809-12, April 12, 2005', 'h': 'A former Solicitor General who, while in office, advised on the liquidation of a bank was not barred from later representing parties in sequestration cases: the “matter” he handled was the liquidation, not the sequestration, and the rule is not applied to bar lawyers indefinitely.', 'r': 'Defines “matter” and “intervention” under the revolving-door rule.'}],
  i=[{'t': 'RA 6713, Sec. 7(b)', 's': 'Public officials may not practise their profession in connection with their former office for one year after leaving it.', 'u': '#/code/ra6713'}])
n('canon-ii-sec-34', 'Lawyers may use paralegals for non-diagnostic, non-advisory legal work, but must direct and supervise them, and the duty of confidentiality extends to the paralegal.', o='Canon 9, Rules 9.01–9.02 (in part)')
n('canon-ii-sec-35', 'Some tasks belong to lawyers alone. A lawyer may not let a non-lawyer, including a paralegal, accept cases for the lawyer, give legal advice or opinions, act without the lawyer’s supervision, hold himself or herself out as a lawyer, appear in court or formal proceedings for a client (unless the law or rules allow), negotiate with third parties without supervision, sign correspondence containing a legal opinion, or do anything only lawyers may do.',
  t=['Law student practitioners under Rule 138-A are outside this prohibition.'], o='Rule 9.01', i=[CLEP])
n('canon-ii-sec-36', 'A lawyer who uses social media must understand its benefits and risks and use it responsibly, consistent with the Code.', t=['Sections 36 to 44 form a chapter on social media, new in the CPRA.'], o='—')
n('canon-ii-sec-38', 'A lawyer must not knowingly or maliciously post, share or upload false or unverified statements or disinformation.', o='—')
n('canon-ii-sec-40', 'Do not reveal privileged information in online posts, even in a “private” group.', o='Canon 21 (in part)')
n('canon-ii-sec-42', 'A lawyer must not use social media to communicate with a judge, justice or agency officer about a pending case in order to influence its outcome.', o='Canon 13')
n('canon-ii-sec-43', 'A lawyer may post general legal information online. But advice on specific facts disclosed by a person online is Limited Legal Service, and it creates duties (confidentiality and conflict-of-interest rules apply).', t=['General information creates no lawyer-client relationship; specific advice can.'], o='—')

# ---------------------------------------------------------------- Canon III — Fidelity
n('canon-iii', 'Fidelity is loyalty: to the Constitution and laws, to the administration of justice as an officer of the court, and to the client within the bounds of law. It is the longest Canon and covers the lawyer-client relationship from start to end, conflicts, confidentiality, fees and money.', o='Canons 15 to 22')
n('canon-iii-sec-1', 'Practice of law: rendering legal service or doing acts that apply law, legal principles, procedure or legal knowledge, which require the skill of a lawyer — in or out of court.',
  t=['It is not limited to court appearances: preparing contracts, giving legal advice and similar work count.'],
  d=[{'n': 'Cayetano v. Monsod', 'c': 'G.R. No. 100113, September 3, 1991', 'h': 'Practice of law means any activity, in or out of court, that requires the application of law, legal procedure, knowledge, training and experience. Monsod’s work as a lawyer-economist, manager and negotiator counted toward the ten years of practice required of the COMELEC Chairman.', 'r': 'The standard definition, now written into the CPRA.'}])
n('canon-iii-sec-2', 'The responsible lawyer upholds the Constitution and laws, promotes respect for legal processes, assists in the speedy administration of justice as an officer of the court, and represents the client with zeal within the bounds of the law and the CPRA.', o='Canon 1, Rule 1.02; Canons 12 and 19')
n('canon-iii-sec-3', 'The lawyer-client relationship is of the highest fiduciary character. It begins when the lawyer agrees, expressly or impliedly, to render legal service, and duties of confidentiality may attach even to a prospective client.',
  t=['No written contract or fee is needed for the relationship to exist; consultation with a view to engagement can be enough.'], o='Canons 15 and 17')
n('canon-iii-sec-4', 'A lawyer binds the client in a legal engagement only when authorized in writing.', t=['Compromise of the client’s claim needs special authority.'], o='Rule 138, Sec. 23 (repealed)')
n('canon-iii-sec-6', 'A lawyer must honor the trust the client reposes: no abuse or exploitation of the relationship. Money received for a purpose must be used for it or returned on demand.',
  t=['Failure to return money on demand gives rise to a presumption of misappropriation.'],
  o='Canon 16, Rules 16.01–16.03; Canon 17')
n('canon-iii-sec-7', 'No frivolous suits or abuse of court processes: no filing of suits without basis in law and evidence, no undue delay of executing a valid judgment, no abuse of procedure.', o='Rules 10.03, 12.02 and 12.04')
n('canon-iii-sec-8', 'Encourage the client to avoid, end or settle disputes on fair terms, and help the parties and the court with mediation and other dispute resolution.', o='Rule 1.04')
n('canon-iii-sec-13', 'A lawyer may not represent conflicting interests unless all concerned give written informed consent after full disclosure. The test: is it the lawyer’s duty to fight for an issue or claim for one client that he or she must oppose for the other?',
  k=['Conflict exists when a lawyer represents inconsistent or opposing interests of two or more persons.', 'Cure: written informed consent of all concerned, after full disclosure.', 'The test looks at duties, not at whether confidences were actually used.'],
  t=['It does not matter that the cases are unrelated or that no confidential information was actually used: the duty to the client continues.', 'Consent must be written and informed; oral consent is not enough under the CPRA.'],
  o='Rule 15.03', d=[{'n': 'Hornilla v. Salunat', 'c': 'A.C. No. 5804, July 1, 2003', 'h': 'A lawyer who acted for a corporation’s board and then appeared for the directors in a derivative suit against them by shareholders represented conflicting interests. The Court explained the tests: whether one duty requires opposing what the other requires; whether acceptance of the new engagement will require the lawyer to use against the former client information obtained in the previous relation.', 'r': 'The tests for conflict of interest, now restated in Sec. 13.'}])
n('canon-iii-sec-14', 'Rules for dealings with current clients that create conflicts. A lawyer may not enter into a business transaction with a client, or acquire an interest adverse to the client, unless the terms are fair and fully disclosed in writing, the client is advised in writing to consult an independent lawyer, and the client gives written informed consent. The section lists further situations of the same kind.',
  k=['Business deal with a client: (1) fair and fully disclosed in writing; (2) written advice to seek independent counsel; (3) written informed consent to the terms and to the lawyer’s role.'],
  t=['All three conditions are needed; a client’s signature on the deal alone is not enough.'], o='Rule 15.03; Rule 16.04 (in part)')
n('canon-iii-sec-16', 'A lawyer must not have dating, romantic or sexual relations with a client during the engagement, unless the relationship existed before the engagement.', t=['New in the CPRA.'], o='—')
n('canon-iii-sec-17', 'Conflict with a former client: a lawyer may not act against a former client in the same or a related matter, or use information from the former engagement against that client, without written informed consent.', o='Rule 15.03; Canon 21')
n('canon-iii-sec-21', 'Government lawyers and conflicts: a lawyer in government service must not represent private interests that conflict with the government’s, and must observe the rules on private practice.', o='Canon 6, Rules 6.02–6.03', i=[{'t': 'RA 6713, Sec. 7', 's': 'Prohibited acts of public officials, including private practice unless authorized and not in conflict with official functions.', 'u': '#/code/ra6713'}])
n('canon-iii-sec-22', 'A conflict of interest of a Public Attorney’s Office lawyer is imputed only to that lawyer and his or her direct supervisor. Other PAO lawyers may still represent the affected client after full disclosure and written informed consent.',
  t=['The PAO asked the Court to delete this section; the Court refused (A.M. No. 23-05-05-SC, 2023) and later held the PAO chief in contempt over an office order that resisted it (2024).'],
  d=[{'n': 'Request of the Public Attorney’s Office to Delete Section 22, Canon III of the Proposed CPRA', 'c': 'A.M. No. 23-05-05-SC', 'h': 'The Court denied the request, holding that the rule protects the poor’s access to counsel: imputing a conflict to the whole PAO would leave one of two indigent parties without a lawyer.', 'r': 'Explains why this section departs from the usual rule that a conflict is imputed to all lawyers of a firm.'}])
n('canon-iii-sec-27', 'A lawyer must keep the client’s confidences and respect data privacy laws. The duty continues after the engagement ends.',
  t=['The duty survives the end of the engagement.', 'Read with the Data Privacy Act (RA 10173): client data are personal information the lawyer must protect.'],
  o='Canon 21, Rules 21.01–21.02',
  d=[{'n': 'Regala v. Sandiganbayan', 'c': 'G.R. No. 105938, September 20, 1996', 'h': 'Lawyers could not be compelled to disclose the identity of the clients for whom they set up corporations: where revealing the name would expose the client to the very liability that was the subject of the legal advice, the identity itself is privileged.', 'r': 'The leading case on when a client’s identity is privileged.'}],
  i=[{'t': 'Data Privacy Act of 2012 (RA 10173)', 's': 'Personal and sensitive personal information of clients must be processed lawfully and kept secure.', 'u': '#/code/ra10173'}])
n('canon-iii-sec-28', 'Protect client confidences from disclosure by the lawyer and by the lawyer’s staff and associates.', o='Rules 21.01, 21.04 and 21.05')
n('canon-iii-sec-35', 'Limited Legal Services: short-term, discrete legal help (advice, document review) without an expectation of continuing representation. Conflict and confidentiality rules still apply.', t=['New in the CPRA.'], o='—')
n('canon-iii-sec-41', 'Fees must be fair and reasonable, judged by the factors the section lists: time spent and extent of service; novelty and difficulty of the issues; skill and expertise required; probability of losing other engagements; customary charges and the IBP chapter’s schedule of fees; the value of the client’s interest or the benefit to the client; contingency or certainty of compensation; and the character of the engagement, among others.',
  k=['Without a written agreement, fees are fixed on quantum meruit (as much as the lawyer deserves).', 'A contingent fee is allowed if reasonable and not unconscionable.'],
  t=['Courts may reduce an unconscionable fee even if the client agreed to it.'], o='Canon 20, Rule 20.01')
n('canon-iii-sec-43', 'A lawyer may not share, split or divide a fee for legal services — directly or indirectly — with anyone not licensed or authorized to practise law.', o='Rule 9.02')
n('canon-iii-sec-47', 'Attorney’s liens: a retaining lien over the client’s funds, documents and papers in the lawyer’s lawful possession, and a charging lien over money judgments the lawyer secured, to answer for unpaid fees.', o='Rule 138, Sec. 37 (repealed); Rule 16.03')
n('canon-iii-sec-49', 'A lawyer must account for all money and property received from or for the client, and must deliver them when due or on demand.', o='Rules 16.01 and 16.03')
n('canon-iii-sec-50', 'Keep the client’s funds separate from the lawyer’s own; no commingling.', o='Rule 16.02')
n('canon-iii-sec-51', 'A lawyer may not acquire an interest in the subject of the litigation he or she is handling.', t=['Read with Art. 1491(5) of the Civil Code, which forbids lawyers to buy property in litigation in which they take part.'], o='Rule 10.01; Civil Code, Art. 1491(5)')
n('canon-iii-sec-52', 'While the engagement lasts, a lawyer may not lend money to a client except in urgent and justifiable circumstances (advances for fees and necessary expenses of the case are not covered), and may not borrow from a client unless the client’s interests are fully protected by the nature of the case or by independent advice.',
  t=['Borrowing is allowed for ordinary commercial transactions the client offers to the public, an existing business relationship, or a contract between them.'], o='Rule 16.04')
n('canon-iii-sec-53', 'A lawyer may end the engagement only for good cause and with written notice. The grounds listed: the client pursues an illegal or immoral course; the client insists on conduct that violates the Code; inability to work with co-counsel harms the client; the lawyer’s condition makes the work difficult; the client deliberately fails to pay or comply with the retainer, or cannot be found; the lawyer is elected or appointed to public office; and similar cases.',
  t=['Written notice is required; abandoning the client without it is a violation even if a ground exists.'], o='Canon 22, Rule 22.01')
n('canon-iii-sec-54', 'The client may end the engagement at any time, with or without cause, but must pay the fees earned.', o='Rule 138, Sec. 26 (repealed)')

# ---------------------------------------------------------------- Canon IV — Competence and Diligence
n('canon-iv', 'A lawyer must bring competence, diligence, commitment and skill to every engagement, and keep learning.', o='Canon 18')
n('canon-iv-sec-1', 'Provide legal service that is competent, efficient and conscientious.', o='Canon 18, Rule 18.01')
n('canon-iv-sec-3', 'Act on the client’s matter diligently and on time, and be punctual in every appearance and filing.',
  t=['Missing a deadline to appeal or failing to file a required brief is the classic violation; it is not excused by heavy workload.'], o='Rule 18.03 (neglect of a legal matter)')
n('canon-iv-sec-6', 'Keep the client regularly informed of the status and result of the matter, and respond to the client’s requests for information.', o='Rule 18.04')
n('canon-iv-sec-8', 'A competent lawyer keeps learning throughout his or her career.', o='Canon 5', i=[MCLE])

# ---------------------------------------------------------------- Canon V — Equality
n('canon-v', 'Every person is entitled to legal representation, without discrimination, and lawyers owe a higher standard of care to the vulnerable.', o='Canon 14')
n('canon-v-sec-1', 'A lawyer may not refuse to represent a person solely because of nationality, ethnicity, sexual orientation or gender identity, religion, disability, age, or similar grounds.', o='Rule 14.01')
n('canon-v-sec-3', 'A lawyer may not refuse an indigent person except when (a) he or she cannot do the work competently for a justifiable cause, (b) there would be a conflict of interest, or (c) the lawyer is related to the adverse party or counsel within the degrees stated.',
  k=['Indigent: no money or property sufficient for food, shelter and basic necessities for oneself and family.'], o='Rule 14.03', i=[ULAS])

# ---------------------------------------------------------------- Canon VI — Accountability
n('canon-vi', 'By taking the oath a lawyer accepts accountability to society, the courts, the profession and clients. Canon VI is the procedure and the penalties.', o='Rule 139-B (repealed)')
n('canon-vi-sec-1', 'Disciplinary proceedings are confidential and summary in nature, but the Supreme Court’s final order is published like any decision.',
  t=['They are sui generis: neither civil nor criminal. Their object is to protect the courts and the public, not to punish the lawyer.'],
  d=[{'n': 'In re Almacen', 'c': 'G.R. No. L-27654, February 18, 1970', 'h': 'Disciplinary proceedings against lawyers are sui generis: an investigation by the Court into the conduct of its own officers, not a civil or criminal action. The lawyer was suspended for scurrilous attacks on the Court.', 'r': 'The classic statement of the nature of disciplinary proceedings.'}],
  o='Rule 139-B, Sec. 18 (repealed)')
n('canon-vi-sec-2', 'Proceedings may start on the Supreme Court’s own initiative, or on a verified complaint filed with the Supreme Court or with the IBP. Complaints against sitting Justices of the appellate courts and judges go to the Supreme Court.', o='Rule 139-B, Sec. 1 (repealed)')
n('canon-vi-sec-16', 'The complainant’s desistance, settlement or withdrawal does not end the case: the Court may proceed if the evidence supports it.', t=['A favorite trap: an affidavit of desistance does not bar discipline.'])
n('canon-vi-sec-32', 'The complainant must prove the charge by substantial evidence — relevant evidence a reasonable mind might accept as adequate to support a conclusion.',
  t=['Not proof beyond reasonable doubt, and not preponderance. An acquittal does not bar discipline; a conviction is not required.'])
n('canon-vi-sec-33', 'Serious offenses include gross misconduct; serious dishonesty, fraud or deceit (including falsification and untruthful statements); bribery or corruption; gross negligence that deprives the client of his or her day in court; conviction of a crime involving moral turpitude; grossly immoral conduct; misappropriating a client’s funds or property; gross ignorance of the law attended by bad faith or malice; and the other acts listed.',
  t=['Penalties for serious offenses are in Sec. 37(a): disbarment, suspension over six months, revocation of notarial commission, or a fine over P100,000.'], o='Rule 138, Sec. 27 (repealed)')
n('canon-vi-sec-37', 'Penalties by class of offense. Serious: disbarment; suspension over six months; revocation of notarial commission with disqualification for at least two years; or a fine over P100,000. Less serious: suspension of one to six months (or revocation of notarial commission with disqualification under two years) and/or a fine of P35,000 to P100,000. Light: fine of P1,000 to P35,000, censure or reprimand, plus possible community or legal aid service.',
  k=['Money or property owed to the client in connection with the engagement must always be ordered returned.'],
  t=['Sanctions may be combined for serious and less serious offenses.', 'Read with Secs. 38–40: modifying circumstances can double the maximum or halve the minimum, and separate penalties are imposed for separate acts.'])
n('canon-vi-sec-38', 'Mitigating circumstances (first offense, good faith, restitution, remorse, reconciliation, and others) and aggravating circumstances (prior liability, fraudulent concealment, bad faith, lack of remorse, defiance of Court or IBP orders, and others) adjust the penalty.',
  t=['Age and years in practice appear in both lists: they can cut either way.'])
n('canon-vi-sec-39', 'With only aggravating circumstances, the Court may double the maximum suspension or fine, or disbar. With only mitigating circumstances, it may go down to half the minimum. When both exist, they may offset.')
n('canon-vi-sec-40', 'Separate acts, separate penalties; if they add up to more than five years’ suspension or P1,000,000 in fines, the Court may disbar instead. One act that is several offenses gets only the penalty for the most serious.')
n('canon-vi-sec-43', 'The Court’s decision imposing discipline is immediately executory.', t=['A motion for reconsideration does not stay the suspension.'])
n('canon-vi-sec-45', 'After a suspension ends, the lawyer files a sworn statement that he or she did not practise during the suspension; it is proof of compliance and lets the lawyer resume practice. A false statement is a ground for disbarment.')
n('canon-vi-sec-47', 'A disbarred lawyer may seek reinstatement through a verified petition for judicial clemency, but only after five years from receipt of the disbarment decision.', t=['The five-year wait is new and strict.'])
n('canon-vi-sec-48', 'The petition for clemency must show: filing after five years; full compliance with prior orders; recognition of the wrong and genuine reform; reconciliation or a good-faith attempt (or a public apology where there is no private offended party); and present good moral character and fitness. It may add that the lawyer still has productive years or shows promise.',
  t=['These conditions codify the clemency guidelines first laid down in Re: Letter of Judge Augustus C. Diaz, A.M. No. 07-7-17-SC (2007).'])
n('canon-vi-sec-52', 'A disbarred or suspended lawyer may not practise in any form: no legal advice, no appearance before courts or agencies, no representation at depositions, no negotiating for clients, no handling of client funds, no teaching law subjects, and no notarial work. A suspended lawyer must stop at once; clients may hire new counsel.',
  t=['Teaching law subjects and notarial work are expressly covered — both are common exam traps.'])

# ---------------------------------------------------------------- the remaining sections (notes_cpra_rest.py)
import notes_cpra_rest
notes_cpra_rest.add(n)

# ---------------------------------------------------------------- notarial rules (selected)
NN = {}
def nn(pid, x, k=None, t=None, d=None):
    e = {'x': x}
    if k: e['k'] = k
    if t: e['t'] = t
    if d: e['d'] = d
    NN[pid] = e

# AEP / immigration -----------------------------------------------------------
AEP_SET = [
    {'t': 'DOLE Department Order No. 248, s. 2025 — Rules on the Employment of Foreign Nationals (in force February 2025)',
     's': 'Replaced D.O. 221-21. Before filing, the employer runs a Labor Market Test (publishing the vacancy) to show no competent, able and willing Filipino is available; DOLE also applies an Economic Needs Test. Certain employers must run an Understudy Training Program or Skills Development Program to transfer skills to at least two Filipino understudies. Exempt foreign nationals must secure a Certificate of Exemption.',
     'u': 'https://insightplus.bakermckenzie.com/bm/employment-compensation/philippines-dole-issues-new-rules-and-regulations-on-the-employment-of-foreign-nationals-in-the-philippines'},
    {'t': 'DOLE Department Order No. 248-A, s. 2025 — Supplemental Guidelines',
     's': 'Clarified D.O. 248: the training-program requirement applies only to certain employers (e.g., Foreign Investment Act registrants with fiscal incentives, public utilities, strategic or critical sectors); created technical working groups for training programs and the Economic Needs Test; listed exempt categories.',
     'u': 'https://insightplus.bakermckenzie.com/bm/employment-compensation/philippines-dole-issues-supplemental-guidelines-clarifying-and-amending-the-rules-on-alien-employment-permits'},
    {'t': 'DOLE Administrative Order No. 199, s. 2026 and Department Order No. 248-B, s. 2026 — Centralization of AEP processing (effective June 9, 2026)',
     's': 'All new and renewal AEP applications, and every related function — receiving, evaluating, approving, issuing, renewing, cancelling, revoking and enforcing AEPs, Certificates of Exemption or Exclusion, training-program submissions, and the Economic Needs Test — moved from the Regional Offices to the DOLE Central Office, Bureau of Local Employment (BLE). Authority of Regional Directors passed to the BLE Director. Applications filed with Regional Offices up to June 8, 2026 were transferred to the BLE. Exception: motions for reconsideration of orders cancelling or revoking an AEP now go to the Director of the DOLE Legal Service.',
     'u': 'https://www.divinalaw.com/wp-content/uploads/2026/09/DOLE-01-Alien-Employment-Permits.pdf'},
    {'t': 'DOLE Department Order No. 248-C, s. 2026 — Simplified issuance (announced October 28, 2026)',
     's': 'Removes several documentary requirements (e.g., PCAB license, PRC special temporary permit, DOJ authority to employ alien, DENR authority) from the AEP filing, though compliance with those agencies’ laws remains required; cuts processing time from 15 to 10 working days, extendible once by 10; moves Labor Market Test notices from paid newspaper publication to the DOLE portal; lets employers file through their own HR staff. Takes effect 15 days after publication.',
     'u': 'https://tribune.net.ph/2026/10/28/dole-simplifies-issuance-of-alien-employment-permits'},
    {'t': 'Centralized online filing and zero-contact policy (DOLE advisory, 2026)', 's': 'AEP applications are filed through DOLE’s centralized online platform; transactions and inquiries follow a zero-contact policy.', 'u': 'https://www.envoyglobal.com/news-alert/philippines-centralizes-alien-employment-permit-processing/'},
]
LABOR = {
    'article-40': {'x': 'A non-resident foreign national may work in the Philippines only with an Alien Employment Permit (AEP) from DOLE. Both the foreign national seeking entry for work and the employer who wants to hire one must secure it. The permit issues only after DOLE finds that no Filipino is competent, able and willing to do the job at the time of application.',
                   'k': ['Who needs it: non-resident foreign nationals, and their domestic or foreign employers.', 'The core test: non-availability of a competent, able and willing Filipino (shown through the Labor Market Test).',
                         'For enterprises registered in preferred areas of investment, the permit may issue on the recommendation of the government agency charged with supervising the enterprise.',
                         'The AEP is separate from the visa: the Bureau of Immigration issues the work visa (e.g., the Sec. 9(g) pre-arranged employment visa) — both are needed.'],
                   't': ['Resident aliens are outside Art. 40; they register differently. The AEP rule applies to non-residents.',
                         'Since June 9, 2026, only the DOLE Central Office (Bureau of Local Employment) processes AEPs — not the Regional Offices.',
                         'Working without an AEP: the foreign national generally cannot obtain relief from the labor tribunals (WPP v. Galera; McBurnie v. Ganzon), unless the employer’s own fault caused the lapse (Rouche).'],
                   'w': 'To reserve jobs for Filipinos when Filipinos can do them, while letting needed foreign skills in and transferring those skills to Filipino workers.',
                   'i': AEP_SET,
                   'd': [{'n': 'General Milling Corp. v. Torres', 'c': 'G.R. No. 93666, April 22, 1991', 'h': 'The Labor Secretary validly cancelled the AEP of a foreign basketball coach. An employer’s right to choose its employees is limited by Art. 40, and the Secretary may consider whether the foreign national’s employment will serve the national interest. The comparison with a long-time resident foreign coach failed because Art. 40 covers only non-resident aliens.', 'r': 'The Secretary’s discretion under Art. 40, and the non-resident limit.'},
                         {'n': 'WPP Marketing Communications, Inc. v. Galera', 'c': '630 Phil. 410 (2010)', 'h': 'A foreign national who worked without a valid work permit was found illegally dismissed but was denied employee benefits: one who comes to court with unclean hands cannot claim the protection of the Labor Code for an employment that violated it.', 'r': 'Effect of working without an AEP.'},
                         {'n': 'McBurnie v. Ganzon', 'c': '719 Phil. 680 (2013) (En Banc)', 'h': 'A foreign national’s labor complaint was dismissed because he did not show that he was qualified and authorized, through an employment permit, to work in the Philippines.', 'r': 'Affirms WPP.'},
                         {'n': 'Rouche v. French Chamber of Commerce in the Philippines', 'c': 'G.R. No. 238581 (Second Division, Leonen, J.)', 'h': 'The foreign employee had held a valid AEP and 9(g) visa; the lapse came after his promotion and from the negligence of the employer’s counsel. Given those circumstances, WPP and McBurnie did not apply, and he was awarded relief for illegal dismissal.', 'r': 'An exception where the employer caused the lack of permit.'}]},
    'article-41': {'x': 'Once an AEP is issued, the foreign national may not transfer to another job or change employer without prior approval of the Secretary of Labor. A non-resident foreign national who entered as a tourist or on another non-working visa may not take up employment without first securing the permit.',
                   't': ['A change of position or employer needs a new or amended AEP; working beyond the approved position is a violation.'], 'i': AEP_SET[2:4]},
    'article-42': {'x': 'Employers who already employed non-resident foreign nationals when the Code took effect had to submit a list of them to the Secretary of Labor; the Secretary may require the submission of training programs to replace them with Filipinos. Today the Understudy Training and Skills Development Programs under D.O. 248 carry this idea forward.', 'i': AEP_SET[:2]},
}
CA613 = {
    'section-9': {'x': 'Section 9 lists the non-immigrant classes of foreigners: those who come for a temporary stay (tourists, visitors for business or pleasure), those in transit, seamen, treaty traders and investors, students, and — under paragraph (g) — those coming to the Philippines for pre-arranged employment.',
                  'k': ['9(a) temporary visitors (business, pleasure, health)', '9(b) transit', '9(c) seamen', '9(d) treaty traders and investors', '9(e) foreign government officials', '9(f) students', '9(g) pre-arranged employment'],
                  't': ['The 9(g) visa is issued by the Bureau of Immigration; it needs the DOLE AEP (Labor Code, Art. 40) as a supporting requirement — the two are different documents from different agencies.',
                        'A tourist (9(a)) who works needs a Special Work Permit or must convert to 9(g); working on a tourist visa is a ground for deportation.'],
                  'i': [{'t': 'DOLE AEP rules (D.O. 248 series, centralized at the BLE since June 9, 2026)', 's': 'The AEP is the labor clearance the Bureau of Immigration requires for a 9(g) visa.', 'u': '#/p/labor/article-40'}]},
    'section-13': {'x': 'Section 13 provides for immigrant (permanent residence) visas: a yearly quota by nationality, and non-quota immigrants such as the foreign spouse and unmarried minor children of a Filipino citizen (13(a)) and others listed.'},
    'section-29': {'x': 'Section 29 lists the classes of foreigners who must be excluded from entering the Philippines — for example, persons likely to become a public charge, persons convicted of crimes involving moral turpitude, and others listed — and who may be refused admission at the port.'},
    'section-37': {'x': 'Section 37 lists the grounds for arrest and deportation of foreigners (for example, entry by fraud, overstaying, conviction of certain crimes, and violating the conditions of one’s stay), on the warrant of the Commissioner of Immigration after a determination by the Board of Commissioners.',
                   't': ['Deportation is an administrative proceeding, not a criminal one: the protections of criminal procedure (like the right against double jeopardy) do not apply in the same way.']},
}


def merge(code, entries):
    f = f'{SITE}/notes/{code}.json'
    cur = json.load(open(f)) if os.path.exists(f) else {}
    for k, v in entries.items():
        cur[k] = {**cur.get(k, {}), **v}
    json.dump(cur, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
    return len(cur)


def main():
    cpra = json.load(open(f'{SITE}/codes/cpra.json'))
    ids = {p['i'] for p in cpra['provisions']}
    bad = [k for k in N if k not in ids]
    assert not bad, bad
    # accuracy check: each listed word must appear in the verbatim text of the section it explains
    text = {p['i']: ' '.join(p['p']) for p in cpra['provisions']}
    miss = [(k, w) for k, ws in notes_cpra_rest.CHK.items() for w in ws if w not in text[k]]
    assert not miss, miss
    json.dump(N, open(f'{SITE}/notes/cpra.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    for code, ent in (('labor', LABOR), ('ca613', CA613)):
        d = json.load(open(f'{SITE}/codes/{code}.json'))
        assert all(k in {p['i'] for p in d['provisions']} for k in ent), code
        merge(code, ent)
    # catalog flags
    cat = json.load(open(f'{SITE}/catalog.json'))
    for c in cat['codes']:
        nf = f"{SITE}/notes/{c['id']}.json"
        if os.path.exists(nf):
            c['notes'] = True
            c['nhash'] = hashlib.sha1(open(nf, 'rb').read()).hexdigest()[:10]
    json.dump(cat, open(f'{SITE}/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('CPRA notes', len(N), 'of', len(ids), '| labor + immigration notes merged')


if __name__ == '__main__':
    main()
