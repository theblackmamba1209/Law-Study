"""Study notes, in our own words, for the CPRA sections not covered in notes_ethics.py.

Imported by notes_ethics.py: add(n) registers every note through its n() helper.
CHK maps a provision to words that must appear in its verbatim text, so a note cannot
silently drift from the rule it explains (periods, numbers, key terms).
"""

ULAS = {'t': 'Rules on the Unified Legal Aid Service (ULAS), A.M. No. 22-11-01-SC', 's': 'The current framework for compulsory free legal aid by every lawyer; de officio and limited legal services count toward it.', 'u': 'https://sc.judiciary.gov.ph/'}
MCLE = {'t': 'Mandatory Continuing Legal Education, B.M. No. 850, as amended', 's': 'The units every practising lawyer must complete each compliance period; the duty in Sec. 24 to “participate in continuing legal education programs” is enforced through it.', 'u': 'https://sc.judiciary.gov.ph/'}
CLEP = {'t': 'Revised Law Student Practice Rule (Rule 138-A), A.M. No. 19-03-24-SC', 's': 'Certified law students may give limited legal services and appear in court through a law school clinic, always under a supervising lawyer.', 'u': 'https://sc.judiciary.gov.ph/'}
R139A = {'t': 'Rule 139-A of the Rules of Court (Integrated Bar of the Philippines)', 's': 'Every lawyer is a member of the IBP and pays annual dues. Default for six months warrants suspension of IBP membership; default for one year is a ground to remove the lawyer’s name from the Roll of Attorneys.', 'u': ''}
RA6713 = {'t': 'R.A. No. 6713 (Code of Conduct and Ethical Standards for Public Officials and Employees, 1989)', 's': 'Section 7 prohibits, among others, a financial or material interest in any transaction requiring the approval of one’s office, and soliciting or accepting gifts in connection with official duties.', 'u': ''}
AMLA = {'t': 'Anti-Money Laundering Act (R.A. No. 9160), as amended — lawyers as covered persons since R.A. No. 10365 (2013)', 's': 'Lawyers who, for a client, manage money or assets, organize contributions for companies, create or manage juridical persons, or buy and sell business entities are covered persons who must report covered and suspicious transactions. The law itself spares information obtained under professional secrecy or legal professional privilege.', 'u': ''}
R137 = {'t': 'Rule 137, Sec. 1 of the Rules of Court (disqualification of judges)', 's': 'A judge must not sit where he or she is related to a party within the sixth degree, or to counsel within the fourth degree, of consanguinity or affinity, among other grounds. Sec. 20 makes the lawyer flag such a relationship early.', 'u': ''}
JAR = {'t': 'Judicial Affidavit Rule, A.M. No. 12-8-8-SC (2012)', 's': 'Judicial affidavits replace direct testimony in most cases and must be filed before the pre-trial or preliminary conference.', 'u': ''}
R139B = 'Rule 139-B of the Rules of Court (repealed by the CPRA)'

CHK = {}


def add(n):
    def m(pid, x, chk=None, **kw):
        if chk:
            CHK[pid] = chk
        n(pid, x, **kw)

    # ------------------------------------------------------------ Canon I — Independence
    m('canon-i-sec-1', 'The opening duty of the whole Code: make legal services accessible, and deliver them efficiently and effectively — while staying independent and acting with integrity. Access and independence are paired on purpose: a lawyer who is easy to reach but beholden to someone is not serving justice.',
      chk=['accessible', 'independence'],
      k=['Three things at once: accessibility, independence, integrity.', 'The aim is the efficient and effective delivery of justice, not only of a service to one client.'],
      o='Canon 2 (making legal services available in an efficient and convenient manner)')
    m('canon-i-sec-3', 'In arguing a client’s cause, a lawyer must not be swayed by dishonest or immoral considerations, or by outside influence or pressure — from the client, the public, the media, or anyone else.',
      chk=['external influences', 'pressure'],
      t=['Pressure from the lawyer’s own client is still “pressure”: independence runs against the client too (see Sec. 5, the client may not dictate procedure).'])

    # ------------------------------------------------------------ Canon II — Propriety
    m('canon-ii-sec-5', 'In everything, personal or professional, the lawyer insists on fairness and obedience to the law — including with his or her own client.',
      chk=['fairness and obedience'], o='Rule 15.07')
    m('canon-ii-sec-6', 'No harassing or threatening another lawyer, that lawyer’s client, a witness, or any court or agency official or employee.',
      chk=['harass or threaten'],
      t=['A threat that amounts to a crime is a serious offense (Sec. 33(m)); other unlawful threats are less serious (Sec. 34(h)).'])
    m('canon-ii-sec-7', 'Formal decorum before every court and agency. Attire must fit the dignity of the forum, with respect for the lawyer’s sexual orientation, gender identity and gender expression.',
      chk=['formal decorum', 'gender expression'],
      t=['The SOGIE clause is new: the dress rule may not be used to force a lawyer to dress against his or her gender identity or expression.'],
      o='Rule 11.01 (appearing in court properly attired)')
    m('canon-ii-sec-9', 'Two prohibitions: do not block another lawyer’s access to evidence (testimonial evidence included) during trial; and never alter, destroy or conceal evidence.',
      chk=['alter, destroy, or conceal'],
      t=['Hiding a witness is “obstructing access to testimonial evidence”.'])
    m('canon-ii-sec-10', 'Rules for handling witnesses: no impropriety in presenting or confronting them; no coaching, abuse, discrimination or harassment, in or out of court; no talking to a witness during a break while the witness is still under examination; and no helping a witness lie.',
      chk=['coach', 'during a break or recess'],
      k=['Coaching is barred — preparing a witness to tell the truth clearly is not coaching; feeding answers is.', 'The recess rule: once examination has begun and until it ends, the lawyer may not speak with the witness during breaks.', 'No directing, assisting or abetting a witness’s misrepresentation.'],
      t=['The recess rule applies to one’s own witness too.'],
      o='Rules 12.06 and 12.07')
    m('canon-ii-sec-12', 'Two reporting duties. First, tell the court or agency at once of dishonest, deceitful or misleading conduct connected with a matter the lawyer is handling there. Second, report transactions the law requires to be reported — e.g., covered and suspicious transactions under anti-money-laundering law. Reporting these is not a breach of confidentiality, the information stays confidential, and a baseless report exposes the reporter to civil, criminal or administrative action.',
      chk=['anti-money laundering', 'baseless report'],
      k=['Duty 1: candor to the tribunal about deceit in the lawyer’s own matter.', 'Duty 2: statutory reporting (AMLA and similar).', 'Safe harbor: lawful reports do not violate confidentiality.', 'Counterweight: baseless reports are actionable.'],
      t=['Read with the AMLA: a lawyer is a covered person only for listed services (managing client assets, setting up companies, and the like), and the AMLA itself excludes information protected by legal professional privilege.'],
      i=[AMLA])
    m('canon-ii-sec-13', 'No accusing another lawyer — directly or through others — of misconduct, impropriety or a crime without factual or legal basis, and no filing (or helping file) frivolous or baseless complaints against another lawyer.',
      chk=['frivolous or baseless'],
      t=['Instituting frivolous actions, once a final decision so finds, is a less serious offense (Sec. 34(i)).'],
      o='Canon 8 (courtesy, fairness and candor toward colleagues)')
    m('canon-ii-sec-14', 'Grievances against a judge or other officer go through the proper remedy before the proper authority — not to the media or social media. Insinuating improper motive without substantial evidence is itself a ground for discipline.',
      chk=['substantial evidence'],
      t=['The standard is “substantial evidence”: a suspicion is not enough to say a judge was bribed or biased.'],
      o='Rules 11.04 and 11.05')
    m('canon-ii-sec-16', 'A lawyer who reasonably believes a life-threatening situation is likely to develop in connection with any proceeding must report it immediately to the proper authorities.',
      chk=['life-threatening'],
      w='Courtroom violence against judges, lawyers and witnesses is a real risk; a lawyer often hears of it first.')
    m('canon-ii-sec-18', 'After a case or matter ends, the lawyer may not make public appearances or statements about it to promote himself or herself, to self-aggrandize, or to win public sympathy.',
      chk=['terminated case', 'self-promotion'],
      t=['Sub judice (Sec. 19) covers pending cases; Sec. 18 covers terminated ones — the motive (self-promotion) is what is banned, not all discussion.'])
    m('canon-ii-sec-20', 'At the first chance, the lawyer must formally disclose on the record any relationship or connection with the judge, presiding officer or court personnel — or between them and the lawyer’s partners, associates or clients — that could be a ground for mandatory inhibition.',
      chk=['mandatory inhibition', 'first available opportunity'],
      t=['Disclosure must be formal and on record — telling the judge privately is not compliance.'],
      i=[R137])
    m('canon-ii-sec-21', 'No gifts, donations or contributions of any value, on any occasion, to any court or agency or its officers and staff — directly or indirectly.',
      chk=['of any value', 'on any occasion'],
      t=['“Any value” and “any occasion”: Christmas gifts to court staff are covered. There is no de minimis exception in the text.'])
    m('canon-ii-sec-22', 'A lawyer must not exploit a non-lawyer’s lack of education or legal knowledge.',
      chk=['lack of education'],
      w='The lawyer’s superior knowledge is a public trust; using it against the uninformed (for example, in a deal with an unrepresented person) is the abuse the rule targets.')
    m('canon-ii-sec-23', 'Two rules on abuse of process. Forum shopping — done knowingly or through gross negligence — is banned as a falsehood imposed on the courts. And no filing (or advising) multiple cases to gain leverage, harass, delay, or raise the cost of litigation.',
      chk=['forum shopping', 'increase the cost of litigation'],
      k=['Forum shopping: filing actions involving the same parties, rights and reliefs in different fora, hoping for a favorable result (tested by litis pendentia or res judicata).', 'Multiple suits as a weapon — even if not technically forum shopping — are separately banned.'],
      t=['Willful forum shopping, and forum shopping through gross negligence, are serious offenses (Sec. 33(n)).'],
      o='Rule 12.02 (no multiple actions from the same cause) and Rule 12.04')
    m('canon-ii-sec-24', 'No encroaching on another lawyer’s engagement. This includes communicating, negotiating or dealing with a person who has a lawyer, unless the person initiated it or the other lawyer knows. But anyone seeking relief against a perceived unfaithful or neglectful counsel may be properly advised.',
      chk=['encroach', 'neglectful counsel'],
      k=['The “no-contact” rule: deal with a represented party through his or her lawyer.', 'Two exceptions: the represented person initiates, or the person’s lawyer knows.', 'Advising someone unhappy with counsel is allowed.'],
      o='Rule 8.02',
      d=[{'n': 'Linsangan v. Tolentino', 'c': 'A.C. No. 6672, September 4, 2009', 'h': 'A lawyer whose agent persuaded another lawyer’s clients to transfer their cases to him was suspended, among others, for encroaching on that lawyer’s professional employment.', 'r': 'Encroachment by inducing clients to switch.'}])
    m('canon-ii-sec-25', 'A solo practitioner has no partner to catch what falls through: he or she must make sure every matter that needs a lawyer’s skill and judgment is handled promptly and competently.',
      chk=['solo practice'])
    m('canon-ii-sec-26', 'A law firm is an office, partnership or association made up only of lawyers practising law and holding themselves out as such. Its name may not be false, misleading or assumed. A deceased, incapacitated or retired partner’s name may stay, if the firm says so in all its communications.',
      chk=['deceased, incapacitated, or retired'],
      t=['Only lawyers: a firm with non-lawyer partners is not a law firm under the CPRA.', 'The 1988 rule allowed only a deceased partner’s name; the CPRA adds incapacitated and retired partners.'],
      o='Rule 3.02',
      d=[{'n': 'In re: Petition for Authority to Continue Use of the Firm Name “Sycip, Salazar, Feliciano, Hernandez & Castillo”', 'c': '92 SCRA 1 (1979)', 'h': 'The Court then refused to let firms keep the names of deceased partners: a firm name should identify the lawyers who actually practise in it, and a partnership for the practice of law is not a business that can trade on a name.', 'r': 'The old rule — later relaxed by Rule 3.02 (1988) and Sec. 26 (2023).'}])
    m('canon-ii-sec-27', 'A partner who takes public office must withdraw from the firm, and his or her name must come off the firm name — unless the law allows that office to practise law at the same time.',
      chk=['assumes public office'],
      o='Rule 3.03',
      w='So that the firm does not trade on the influence of an official who is not practising with it.')
    m('canon-ii-sec-28', 'Government lawyers answer to the CPRA, to R.A. No. 6713, and to other laws on public officers. Discipline under the CPRA is separate from any liability under those other laws.',
      chk=['separate and distinct'],
      t=['Separate and distinct: an Ombudsman or Civil Service ruling does not bar — and is not required for — discipline as a lawyer. (But see Canon VI, Sec. 2: such complaints are filed only with the Supreme Court.)'],
      o='Canon 6', i=[RA6713])
    m('canon-ii-sec-30', 'A government lawyer may not use office to advance his or her own or another’s private or financial interest in transactions the office must approve, may not solicit or take anything of value in connection with it, and may not give anything of value to or unduly favor people dealing with the office in expectation of a return.',
      chk=['requiring the approval'],
      o='Rule 6.02', i=[RA6713])
    m('canon-ii-sec-31', 'A public prosecutor’s first duty is not to convict but to see justice done. Suppressing facts, hiding or tampering with evidence, coaching a witness or offering false testimony is ground for discipline. Private lawyers authorized to prosecute under the prosecutor’s direct supervision carry the same duties.',
      chk=['not to convict but to see that justice is done'],
      k=['The prosecutor represents the State, whose interest is justice — including the acquittal of the innocent.', 'Applies to authorized private prosecutors too.'],
      o='Rule 6.01',
      d=[{'n': 'Suarez v. Platon', 'c': '69 Phil. 556 (1940)', 'h': 'The Court described the prosecutor as the representative of a sovereignty whose interest in a criminal prosecution is not that it shall win a case but that justice shall be done — borrowing the classic formulation of the U.S. Supreme Court in Berger v. United States (1935).', 'r': 'The source of the “not to convict” formula.'}])
    m('canon-ii-sec-32', 'Law deans, administrators and teachers are held to the full CPRA standards — propriety, respectability and decorum inside and outside the classroom, and in all media.',
      chk=['inside and outside the classroom'])
    m('canon-ii-sec-33', 'A law teacher or school official must disclose to the institution any adverse interest of a client — and, specifically, any adverse interest of a client that directly affects a student under his or her direct supervision.',
      chk=['adverse interest'],
      w='A teacher grades and mentors students; a client’s interest against a student (or the school) can compromise both roles.')
    m('canon-ii-sec-37', 'Online posts must uphold the dignity of the profession and respect for the law — whether the post is public or in a restricted setting that still has an audience.',
      chk=['restricted privacy setting'],
      t=['“Friends only” is still an audience: a restricted setting is not a shield.'],
      d=[{'n': 'Belo-Henares v. Guevarra', 'c': 'A.C. No. 11394, December 1, 2016', 'h': 'A lawyer who posted insulting and threatening statements about a doctor on Facebook was suspended for one year. Posts set to “Friends” were not private: they could be viewed by many and shared further, so there was no reasonable expectation of privacy.', 'r': 'Social media posts and lawyer discipline; the case behind the “restricted setting” language.'}])
    m('canon-ii-sec-39', 'No creating or running anonymous or fake social media accounts to hide one’s identity in order to get around the law or the CPRA.',
      chk=['hide his or her identity'],
      t=['Anonymity alone is not banned; anonymity for the purpose of circumventing the law or the CPRA is.'])
    m('canon-ii-sec-41', 'A lawyer who discusses client matters through a social media account must take steps to prevent inadvertent disclosure of, or unauthorized access to, that account.',
      chk=['unauthorized access'],
      k=['Practical meaning: secure passwords, two-factor authentication, no shared devices, care with group chats.'])
    m('canon-ii-sec-44', 'Be careful with posts and comments that could create a conflict of interest — for example, publicly taking a position against a current or former client, or commenting on a matter one is handling for the other side.',
      chk=['conflict of interest'])

    # ------------------------------------------------------------ Canon III — Fidelity
    m('canon-iii-sec-5', 'A lawyer who appears is presumed authorized; no written power of attorney is needed to appear in court. The court may, on its own or on motion and for just cause, require proof of authority.',
      chk=['presumed to be properly authorized', 'no written power of attorney'],
      t=['Contrast Sec. 4: authority to appear is presumed, but authority to compromise or to receive payment of the client’s claim requires a special power of attorney.', 'This is the former Rule 138, Sec. 21, moved into the CPRA (the CPRA repealed Rule 138, Secs. 20–37).'],
      o='Rule 138, Sec. 21 of the Rules of Court')
    m('canon-iii-sec-9', 'If a lawyer learns that the client, during the representation, committed fraud on a court, agency or its officer in the matter handled, the lawyer must promptly call on the client to correct it. The fraud also lets the lawyer end the engagement.',
      chk=['rectify', 'termination'],
      k=['Step 1: call on the client to rectify.', 'Step 2 (if the client refuses): the lawyer may terminate.'],
      t=['Failing to call on the client to rectify is a light offense (Sec. 35(e)).', 'The 1988 rule required termination if the client refused; the CPRA makes the fraud a ground the lawyer may invoke.'],
      o='Rule 19.02')
    m('canon-iii-sec-10', 'A lawyer or firm answers for the mistakes, negligence, acts and omissions of a subordinate lawyer, paralegal or employee under direct supervision and acting within assigned tasks, where they cause damage that dishonors the profession or breach confidentiality. Defense: proof of the diligence of a good parent of a family in selecting and supervising that person.',
      chk=['diligence of a good parent of a family'],
      k=['Elements: (1) subordinate under direct supervision and control; (2) acting within assigned tasks; (3) damage or injury that dishonors the profession or violates confidentiality.', 'Defense: diligence in selection and supervision.'],
      t=['The defense mirrors the employer’s defense under Civil Code, Art. 2180 — a useful cross-subject link.'])
    m('canon-iii-sec-11', 'The supervising lawyer co-signs submissions made with the supervised lawyer, and is liable for the supervised lawyer’s violation if he or she (a) ordered or ratified it, (b) knew of it in time to prevent or mitigate it but did nothing, or (c) should have known in time to take remedial action.',
      chk=['co-sign', 'should have known'],
      k=['(a) orders or ratifies;', '(b) knows and fails to act;', '(c) should have known — a negligence standard.', 'Supervising lawyers of law students under Rule 138-A are included.'],
      t=['Ground (c) goes further than the U.S. Model Rule 5.1, which stops at actual knowledge.'])
    m('canon-iii-sec-12', 'Acting on a superior’s instructions is no excuse: a supervised lawyer remains personally bound by the CPRA.',
      chk=['nevertheless bound'],
      t=['“I was only following the partner’s orders” is not a defense.'])
    m('canon-iii-sec-15', 'A lawyer joining a firm must disclose, as early as possible, former clients who may conflict with the firm’s current clients. Where a potential conflict exists, the new lawyer must not work on the affected client’s case.',
      chk=['joins a law firm', 'shall not act'],
      t=['The CPRA screens the incoming lawyer from the affected case.'])
    m('canon-iii-sec-18', 'Duties to former clients: (a) keep their confidences after the engagement ends; (b) do not use information from the former representation; (c) do not take on a new client in the same or a related matter whose interests are materially adverse to the former client, unless the former client gives written informed consent.',
      chk=['materially adverse', 'same or related legal matter'],
      k=['Exceptions to (a) and (b): written informed consent, allowance by the CPRA or law, or the information has become generally known.', 'Test for (c): same or related matter + materially adverse interests.'],
      t=['The duty of confidentiality survives the end of the engagement — and even the client’s death.',
         'Older cases (e.g., Quiambao) put the bar broadly — even against a former client in unrelated cases. Sec. 18(c) now limits it to the same or a related matter with materially adverse interests; the duties in (a) and (b) still apply in every matter.'],
      o='Rule 15.03 and Canon 21',
      d=[{'n': 'Quiambao v. Bamba', 'c': 'A.C. No. 6708, August 25, 2005', 'h': 'A lawyer who had acted for the complainant later appeared against her in other cases for the opposing side. The Court held there was conflict of interest even if no confidential information was used: the rule prevents the appearance of treachery and protects trust in the profession.', 'r': 'Conflict with a former client; no need to prove use of confidences.'}])
    m('canon-iii-sec-19', 'Representing a corporation or organization does not automatically mean representing its parent, subsidiary or other affiliates. A corporate lawyer who also sits on the board must check whether the two roles conflict and, if they do, disclose the conflict to everyone concerned.',
      chk=['parent or subsidiary', 'board of directors or trustees'],
      w='The organization itself is the client; officers and affiliates are not clients by default.')
    m('canon-iii-sec-20', 'A legal services organization is a private body — a legal aid clinic, partnership, association or corporation — whose main purpose is free legal service. The lawyer-client relationship arises only with the handling lawyers, but every lawyer who took part in a matter is bound by the conflict and confidentiality rules.',
      chk=['free legal services', 'handling lawyers'],
      t=['Only the handling lawyers become counsel — so one clinic lawyer’s client does not disqualify unrelated lawyers in the same organization.'])
    m('canon-iii-sec-23', 'A lawyer may not, without just cause, refuse a court’s or agency’s request to act as amicus curiae in his or her field of expertise.',
      chk=['amicus curiae'], o='Rule 14.02')
    m('canon-iii-sec-24', 'Keep up with legal developments; take continuing legal education; support high standards in law schools and student training; help educate the public about the law. IBP chapters provide supervising lawyers to legal aid clinics in their areas.',
      chk=['continuing legal education'],
      o='Canon 5', i=[MCLE, CLEP])
    m('canon-iii-sec-25', 'Lawyers should support internships and apprenticeships, accept law students for training, treat them as junior colleagues and future counsel, and supervise them conscientiously.',
      chk=['junior colleagues'])
    m('canon-iii-sec-26', 'Pay IBP dues promptly unless a law or rule expressly exempts you.',
      chk=['membership dues'],
      t=['Being a senior citizen, working abroad, or not practising does not by itself exempt a lawyer from IBP dues.'],
      i=[R139A],
      d=[{'n': 'Santos v. Llamas', 'c': 'A.C. No. 4749, January 20, 2000', 'h': 'A lawyer who stopped paying IBP dues for years, claiming an exemption as a senior citizen, and who misrepresented his IBP compliance in pleadings, was suspended. Exemption from taxes for senior citizens does not cover IBP dues, which are a condition of practice.', 'r': 'IBP dues are compulsory.'},
         {'n': 'Letter of Atty. Cecilio Y. Arevalo, Jr. Requesting Exemption from Payment of IBP Dues', 'c': 'B.M. No. 1370, May 9, 2005', 'h': 'A lawyer who worked abroad and in government and did not practise was denied an exemption: dues are a regulatory measure tied to membership in the Bar, not to actual practice.', 'r': 'Non-practice is no exemption.'}])
    m('canon-iii-sec-29', 'A lawyer who leaves a firm remains bound to keep the confidences of that firm’s clients.',
      chk=['previous law office or law firm'])
    m('canon-iii-sec-30', 'Within a firm, a lawyer may share a client’s matter with partners, associates, paralegals, interns and staff who are or will be working on it, unless the client forbids it. The lawyer who received the confidences must take measures so that those colleagues do not disclose or use them without the client’s written informed consent.',
      chk=['unless expressly prohibited by the client'],
      t=['Sharing is limited to people involved in handling the account — not the whole firm.'],
      o='Rule 21.04')
    m('canon-iii-sec-31', 'Client confidences may not be discussed even with family members.',
      chk=['family members'], o='Rule 21.08')
    m('canon-iii-sec-32', 'A lawyer must not reveal that he or she was consulted about a particular case, except to avoid a possible conflict of interest.',
      chk=['consulted about a particular case'],
      t=['Even the fact of a consultation is protected — not only what was said.'],
      o='Rule 21.07')
    m('canon-iii-sec-33', 'Foreign lawyers may not practise law in the Philippines, directly or indirectly.',
      chk=['Foreign lawyers'],
      t=['Rooted in the Constitution: the practice of professions is limited to Filipino citizens save as provided by law (Art. XII, Sec. 14). Admission to the Bar requires citizenship (Rule 138, Sec. 2).'])
    m('canon-iii-sec-34', 'Lawyers should take part in improving the legal system: law reform, better administration of justice, and advocacy in areas such as the environment, indigenous peoples’ rights, human rights, access to justice and good governance.',
      chk=['law reform'], o='Canon 4')
    m('canon-iii-sec-36', 'A lawyer appointed counsel de officio may not refuse limited legal services pro bono because of a conflict of interest; instead he or she discloses the conflict to all affected. In any case, the lawyer must render the service to the extent needed to protect the person’s fundamental rights and remedies. Government lawyers are not exempt and may be appointed de officio unless law, Civil Service rules, or a conflict with the government prevents it.',
      chk=['counsel de officio', 'fundamental rights'],
      k=['Conflict is not a ground to refuse de officio limited services — disclose instead.', 'Floor: protect fundamental rights and preserve remedies.', 'Government lawyers can be appointed.'],
      t=['This is the reverse of the usual conflict rule: in limited, court-appointed services the duty to protect fundamental rights outweighs the conflict.'],
      o='Rule 14.02', i=[ULAS])
    m('canon-iii-sec-37', 'Confidences received in limited legal services are protected exactly as in a regular engagement.',
      chk=['same extent'])
    m('canon-iii-sec-38', 'Outside the de officio situation in Sec. 36, a lawyer must stop giving limited legal services on becoming aware of an actual or potential conflict, unless the client gives written informed consent. Limited legal services end when the service is completed.',
      chk=['written informed consent', 'completion'])
    m('canon-iii-sec-39', 'Limited legal services given by law student practitioners under the Clinical Legal Education Program are governed by the CPRA.',
      chk=['law student practitioner'], i=[CLEP])
    m('canon-iii-sec-40', 'Clinic directors and supervising lawyers under Rule 138-A must give students meaningful training, take responsibility for the students’ work while under supervision, and follow the law student practice rules.',
      chk=['assume responsibility'], i=[CLEP])
    m('canon-iii-sec-42', 'On a referral, with the client’s written informed consent, the referring lawyer may share in the fee in proportion to the work done and responsibility assumed. A lawyer who completes a deceased lawyer’s unfinished business may share fees with the deceased lawyer’s heirs or estate.',
      chk=['proportion to the work performed and responsibility assumed'],
      t=['No pure “referral fee” for doing nothing: the share follows work and responsibility.', 'Sharing fees with a non-lawyer is a less serious offense (Sec. 34(o)); the heirs of a deceased lawyer are the recognized exception.'],
      o='Rules 20.02 and 9.02(b)')
    m('canon-iii-sec-44', 'No fee, commission, rebate or other compensation from anyone other than the client without the client’s written informed consent. Even with consent, third-party payment must not affect the lawyer’s independence, judgment or loyalty, and must not lead to disclosure of privileged information.',
      chk=['anyone other than the client'],
      k=['Typical case: an employer or insurer pays for the lawyer of an employee or insured.', 'Three safeguards: consent, independence, privilege.'],
      o='Rule 20.03')
    m('canon-iii-sec-45', 'A lawyer is entitled to prompt payment. If there is no express fee agreement, the lawyer is paid reasonable fees under the Sec. 41 factors (quantum meruit).',
      chk=['prompt payment', 'Section 41'])
    m('canon-iii-sec-46', 'Avoid fee disputes with clients; sue only to prevent imposition, injustice or fraud.',
      chk=['imposition, injustice or fraud'], o='Rule 20.04')
    m('canon-iii-sec-48', 'Where the law provides funds, the court may order a counsel de officio paid an amount it fixes using the Sec. 41 factors — unless the work falls under limited legal services.',
      chk=['availability of funds'],
      t=['Discretionary (“may”), and subject to available funds.'],
      o='Rule 138, Sec. 32 of the Rules of Court (now repealed and absorbed)')
    m('canon-iii-sec-55', 'The death of the lawyer or of the client ends the lawyer-client relationship. But a lawyer’s death does not end the engagement between the client and the law firm handling the matter.',
      chk=['death', 'law firm'],
      t=['When a party-client dies, counsel must inform the court within thirty days and give the name and address of the legal representative (Rules of Court, Rule 3, Sec. 16).', 'Contrast: the firm survives the death of one of its lawyers.'])
    m('canon-iii-sec-56', 'When the engagement ends, the lawyer — subject to the attorney’s lien — must at once account for and turn over the client’s documents, evidence, funds and property, and cooperate with the successor lawyer. The lawyer has a retaining lien on the client’s funds, documents and papers lawfully in his or her possession until fair fees and disbursements are paid, and may apply those funds to them.',
      chk=['turn over', 'lien'],
      k=['Retaining lien (this section): over client’s funds, documents and papers in the lawyer’s possession.', 'Charging lien (Sec. 54): over money judgments and executions in the case.'],
      t=['The lien is not a license to hold documents the client urgently needs to protect rights in pending litigation; the duty to cooperate with successor counsel stays.'],
      o='Rules 16.03 and 22.02; Rule 138, Sec. 37')

    # ------------------------------------------------------------ Canon IV — Competence and diligence
    m('canon-iv-sec-2', 'Take on only what you can deliver. With the client’s prior written consent, a lawyer may bring in collaborating counsel.',
      chk=['collaborating counsel', 'prior written consent'],
      o='Rule 18.01')
    m('canon-iv-sec-4', 'Be diligent in every undertaking and do not cause delay. Come to trial knowing the law, the facts and the evidence, and ready with object and documentary evidence and the witnesses’ judicial affidavits when required.',
      chk=['judicial affidavits'],
      o='Rules 12.01, 12.04 and 18.02', i=[JAR])
    m('canon-iv-sec-5', 'After reasonable inquiry, give the client a prompt and objective assessment of the merits and likely outcome, and explain the viable options so the client can decide.',
      chk=['objective assessment', 'viable options'],
      t=['Neither overstating nor understating the case — false hope to win an engagement is a violation.'],
      o='Rule 15.05')
    m('canon-iv-sec-7', 'Avoid asking for extensions unless the rules allow them or there is good cause. Once an extension is granted, file within it — unless the client has decided not to pursue the case or there is other justifiable cause.',
      chk=['extension', 'lapse'],
      t=['Under the 2019 amendments to the Rules of Civil Procedure, a defendant gets only one extension of up to thirty days to answer (Rule 11, Sec. 11).', 'Letting an extended period lapse is a classic neglect case.'],
      o='Rule 12.03')
    m('canon-iv-sec-9', 'A lawyer who also practises another profession (e.g., accountancy, brokerage) must state in the contract what services he or she is engaged to perform, and the other profession must not compromise the lawyer’s competence, integrity, probity or independence.',
      chk=['another profession or occupation'],
      w='The client must know when the lawyer is acting as lawyer — privilege and professional duties depend on it.',
      o='Rule 15.08')
    m('canon-iv-sec-10', 'A lawyer in business or another non-legal profession is still bound by the CPRA’s ethical duties.',
      chk=['non-legal profession'],
      t=['Discipline reaches conduct outside the practice of law: the lawyer’s fitness is judged as a whole.'])

    # ------------------------------------------------------------ Canon V — Equality
    m('canon-v-sec-2', 'With a client from a vulnerable sector, the lawyer must be sensitive to the client’s circumstances and the special laws that apply, give a higher standard of service, and assert the client’s right to meaningful access to justice. A vulnerable person is one at higher risk of harm — including children, the elderly, the homeless, persons with disability, persons deprived of liberty, human rights victims, victims of domestic violence or armed conflict, the socio-economically disadvantaged, racial or ethnic minorities, and those with debilitating conditions.',
      chk=['higher standard of service', 'persons deprived of liberty'],
      k=['Special laws to keep in mind: R.A. 7610 (children), R.A. 9262 (VAWC), R.A. 9344 (juvenile justice), R.A. 7277 as amended (persons with disability).'],
      t=['The list is inclusive (“shall include”), not exhaustive.'])
    m('canon-v-sec-4', 'Same standard of service for every client whatever the pay — except the higher standard owed to vulnerable persons.',
      chk=['regardless of remuneration'],
      t=['Pro bono and de officio clients get the same diligence as paying clients.'],
      o='Rule 14.04')

    # ------------------------------------------------------------ Canon VI — Accountability: procedure
    m('canon-vi-sec-3', 'The complaint must be verified, state the acts or omissions clearly and concisely, and come with the witnesses’ judicial affidavits and supporting documents. If filed with the IBP, six copies go to the IBP Secretary or a chapter secretary, who transmits it to the Board of Governors.',
      chk=['verified', 'six (6) copies'],
      t=['Judicial affidavits are attached at the outset — a change from the old practice under Rule 139-B.'],
      o=R139B)
    m('canon-vi-sec-4', 'The IBP recommends 150 lawyers in good standing, drawn proportionately from its nine regions, to serve as Investigating Commissioners; only those the Supreme Court approves may serve, for three-year terms, and each takes an oath.',
      chk=['one hundred fifty (150)', 'nine (9)', 'three (3) years'],
      w='The Supreme Court controls who investigates lawyers — consistent with its exclusive constitutional power over the practice of law (Art. VIII, Sec. 5(5)).')
    m('canon-vi-sec-5', 'The IBP Board of Governors assigns a complaint by raffle to one Investigating Commissioner — or, in special circumstances, to a panel of three.',
      chk=['raffle', 'three (3)'])
    m('canon-vi-sec-6', 'For a complaint against a government lawyer, the Investigating Commissioner decides within five calendar days from raffle whether the agency, the Ombudsman, or the Supreme Court has jurisdiction. The case proceeds if it touches the lawyer’s continuing duties under the CPRA, or if the allegations, if true, would make the lawyer unfit to practise; otherwise dismissal is recommended.',
      chk=['five (5) calendar days', 'unfit to practice'],
      k=['Test: does the charge concern the lawyer qua lawyer (continuing CPRA duties / fitness to practise) or only the official qua official?'],
      t=['Read with Sec. 2: a complaint seeking to discipline a government lawyer as a member of the Bar is filed only with the Supreme Court.'])
    m('canon-vi-sec-7', 'An Investigating Commissioner must recuse for relationship within the fourth degree of consanguinity or affinity with a party or counsel, a professional legal relationship, pecuniary interest, or having acted as counsel for a party (this last one can be waived by the parties’ written consent on record). A motion to disqualify goes to the IBP Board, which resolves it within five calendar days; its ruling is final.',
      chk=['fourth degree', 'five (5) calendar days'],
      t=['Only the “acted as counsel” ground can be waived by written consent.', 'The text says the Board designates “a replace” of the commissioner — so it reads in both the primary and the ChanRobles transcriptions; the intended word is “replacement”.'])
    m('canon-vi-sec-8', 'The Investigating Commissioner investigates and submits a report with recommendations to the IBP Board within 180 calendar days from raffle — the overall ceiling for the investigation.',
      chk=['one hundred eighty (180)'])
    m('canon-vi-sec-9', 'Only three submissions are allowed: complaint, answer, and position papers — all verified. The complaint carries a certificate of non-forum shopping. An unverified complaint is recommended for outright dismissal; an unverified answer or position paper is disregarded.',
      chk=['Certificate of Non-Forum Shopping', 'unverified'],
      t=['Different consequences: unverified complaint → dismissal; unverified answer/position paper → not considered.'])
    m('canon-vi-sec-10', 'Prohibited: motions to dismiss (except for lack of jurisdiction, litis pendentia or res judicata); bills of particulars; motions to reopen or for new trial; petitions for relief from judgment; supplemental pleadings; and motions for reconsideration of a judgment on the merits (but reconsideration of interlocutory orders is allowed).',
      chk=['litis pendentia or res judicata', 'interlocutory'],
      t=['The pattern copies summary procedure — speed is the design goal.', 'Note the reversal from ordinary civil procedure: here an MR of an interlocutory order is allowed, an MR of the judgment on the merits is not.'])
    m('canon-vi-sec-11', 'Within fifteen calendar days from raffle, if there is no prima facie showing of liability, the commissioner recommends outright dismissal to the Supreme Court, which may adopt it; otherwise the Court orders further proceedings.',
      chk=['fifteen (15) calendar days', 'prima facie'],
      t=['Only the Supreme Court dismisses — the commissioner only recommends.'])
    m('canon-vi-sec-12', 'No disciplinary case may be started against a dead lawyer; one filed anyway is dismissed; and a lawyer’s death while the case is pending also causes its dismissal.',
      chk=['died', 'dismissal'],
      w='Discipline protects the public and the courts from an unfit practitioner; a deceased lawyer no longer practises, so the case becomes pointless.')
    m('canon-vi-sec-13', 'Within fifteen calendar days from raffle, the commissioner issues summons, with the verified complaint and supporting documents, requiring a verified answer.',
      chk=['fifteen (15) calendar days'])
    m('canon-vi-sec-14', 'The verified answer, with judicial affidavits and supporting documents, is due within thirty calendar days from receipt of summons. One fifteen-day extension may be given, on motion and for good cause. Two copies go to the commissioner, with proof of service on the complainant.',
      chk=['thirty (30) calendar days', 'one extension of fifteen (15)'],
      t=['Only one extension, and only fifteen days.'])
    m('canon-vi-sec-15', 'If the verified answer shows the complaint has no merit, the commissioner recommends dismissal to the Supreme Court; otherwise the Court directs further proceedings.',
      chk=['not meritorious'])
    m('canon-vi-sec-17', 'The IBP Board may appoint a member of the Bar as counsel de officio for the complainant or the respondent when assistance is needed.',
      chk=['counsel de officio'])
    m('canon-vi-sec-18', 'Once issues are joined (or the respondent fails to answer), the investigation proceeds — ex parte if the respondent, despite notice, does not answer or appear — and always with dispatch. The respondent has full opportunity to be heard, with or without counsel, and to present witnesses. The commissioner may issue subpoenas and administer oaths.',
      chk=['ex parte', 'subpoenae'])
    m('canon-vi-sec-19', 'Wilful disobedience of the commissioner’s subpoena or lawful order is indirect contempt. Show cause within ten days; a hearing (if needed) ends within fifteen days; the report goes to the IBP Board within fifteen days; the Board acts within thirty days and its action is immediately executory. Appeal lies to the Supreme Court, but execution is stayed only by a bond fixed by the Board.',
      chk=['ten (10) calendar days', 'thirty (30) calendar days', 'immediately executory'],
      k=['10 days — show cause', '15 days — hearing', '15 days — report', '30 days — Board resolution', 'Appeal to SC; stay only on bond'])
    m('canon-vi-sec-20', 'On receipt of the answer, the commissioner notifies the parties to file, simultaneously and within ten non-extendible calendar days, preliminary conference briefs containing admissions, stipulations, issues, judicial affidavits and marked exhibits (with counsel’s certification of faithful reproduction), and other matters that help speed the case.',
      chk=['non-extendible period of ten (10)'])
    m('canon-vi-sec-21', 'Within ten calendar days from receipt of the briefs, the commissioner issues a Preliminary Conference Order summarizing stipulated facts, issues and exhibits, and directs verified position papers within ten non-extendible days.',
      chk=['Preliminary Conference Order', 'ten (10) calendar days'])
    m('canon-vi-sec-22', 'Within ten calendar days from the last position paper, the commissioner decides whether a clarificatory hearing is needed; if so, it is set within fifteen days, limited to the factual issues identified, may be in person or by videoconference, and ends within thirty days. The commissioner questions the witnesses first; the parties may then confront them on those issues.',
      chk=['videoconferencing', 'thirty (30) calendar days'],
      t=['It is a clarificatory hearing, not a full trial: the commissioner sets the issues and leads the questioning.'])
    m('canon-vi-sec-23', 'Proceedings before the IBP are recorded.', chk=['recorded'])
    m('canon-vi-sec-24', 'A party who does not appear at the clarificatory hearing waives the right to take part in it.', chk=['waiver'])
    m('canon-vi-sec-25', 'The report and recommendation is due within sixty non-extendible calendar days from the last position paper (if there is no hearing) or within thirty non-extendible days from the end of the hearing. It attaches the transcript, audio recording, or the commissioner’s signed notes, and the evidence; it need not wait for the transcription. Videoconference hearings are recorded and form part of the record.',
      chk=['sixty (60) calendar days', 'thirty (30) calendar days'],
      k=['No hearing → 60 days from last position paper.', 'With hearing → 30 days from end of hearing.'])
    m('canon-vi-sec-26', 'The IBP Board has ninety non-extendible calendar days from receipt of the report to submit to the Supreme Court its resolution adopting, modifying or disapproving it.',
      chk=['ninety (90) calendar days'],
      t=['The Board’s resolution is still only a recommendation: the Supreme Court alone imposes discipline (a change made by B.M. No. 1645 in 2015 and kept by the CPRA).'])
    m('canon-vi-sec-27', 'Depositions may be taken under the Rules of Civil Procedure, with the commissioner’s leave.', chk=['with leave'])
    m('canon-vi-sec-28', 'Filing and service may be personal, by registered mail, accredited courier, e-mail or other electronic means, or under international conventions. The office and e-mail addresses the lawyer gave the IBP are the official addresses for service.',
      chk=['electronic mail'],
      t=['A lawyer who never updates his or her IBP addresses cannot complain of not receiving notices sent there.'])
    m('canon-vi-sec-29', 'Substantial defects in the complaint, notices, answer, proceedings or report that may cause a miscarriage of justice are raised as errors before the Supreme Court. If the defect amounts to denial of due process, the remedy is a motion to reopen before the IBP Board within sixty calendar days from knowledge.',
      chk=['motion to reopen', 'sixty (60) calendar days'])
    m('canon-vi-sec-30', 'For cases the Supreme Court starts itself or that are filed with it, the Court may refer the case to the Office of the Bar Confidant, the IBP, or another fact-finding body. Referred cases follow Sections 5 to 29, and the Court reviews the report directly.',
      chk=['Office of the Bar Confidant', 'Sections 5 to 29'])
    m('canon-vi-sec-31', 'After the answer (or the lapse of the period to answer), the Supreme Court — on its own or on recommendation of the IBP Board, the Bar Confidant or the fact-finding body — may preventively suspend the lawyer for up to 180 calendar days, or until lifted, to prevent obstruction, tampering with evidence, or intimidation of witnesses.',
      chk=['one hundred eighty (180) calendar days'],
      k=['When: after answer or lapse of period to answer.', 'Who: only the Supreme Court.', 'Why: to protect the investigation, not to punish.', 'How long: up to 180 days or until lifted.'],
      t=['Preventive suspension is not a penalty.'],
      o='Rule 139-B, Sec. 15 (which had no fixed limit)')

    # ------------------------------------------------------------ Canon VI — offenses and penalties
    m('canon-vi-sec-34', 'The less serious offenses: simple misconduct; simple negligence (not depriving the client of a day in court); violating Supreme Court rules on bar matters and disciplinary cases, including wilful disobedience of SC or IBP orders; simple dishonesty; other conflict-of-interest violations; prohibited borrowing from or lending to a client; other unlawful threats; frivolous suits (once finally so declared); violating sub judice; deliberately not paying just debts; withdrawing without good cause and written notice; intemperate language before a tribunal; unjustified refusal to account for client funds; sharing fees with non-lawyers; and other reportorial violations.',
      chk=['Less serious offenses', 'subjudice', 'just debts'],
      k=['Pair each with its serious version in Sec. 33: simple vs. gross misconduct; simple vs. gross negligence; simple vs. serious dishonesty; “other” vs. intentional conflict-of-interest violations; other threats vs. threats amounting to a crime.'],
      t=['The dividing line for negligence: did it deprive the client of his or her day in court? If yes — serious (Sec. 33(d)).', 'Frivolous suits count only after a final decision dismissing them as frivolous.'])
    m('canon-vi-sec-35', 'The light offenses: violating IBP membership rules; vulgar or offensive language in personal dealings; fraternizing with court or agency personnel where one has a pending case, so as to suggest influence; frivolous motions for inhibition; failing to promptly call on a client to rectify fraud; and other similar infractions.',
      chk=['Light offenses', 'Fraternizing'],
      t=['Offensive language before a tribunal is less serious (Sec. 34(m)); in personal dealings it is light (Sec. 35(b)).'])
    m('canon-vi-sec-36', 'A lawyer who knowingly helps another lawyer commit any CPRA offense may also be held liable.',
      chk=['knowingly assist'])
    m('canon-vi-sec-41', 'Fines must be paid, and client money or property returned, within three months from receipt of the decision; otherwise the Court may cite the lawyer for indirect contempt.',
      chk=['three (3) months', 'indirect contempt'],
      t=['Restitution of client money is ordered in the disciplinary case itself when the amounts are intrinsically linked to the professional engagement.'])
    m('canon-vi-sec-42', 'A lawyer already disbarred who is found guilty of a new charge may be fined or ordered to return a client’s money or property. If the new offense deserves disbarment or suspension, that penalty is not imposed (there is nothing left to take away) but is recorded in the lawyer’s file at the Office of the Bar Confidant — and counted against any later petition for judicial clemency.',
      chk=['previously disbarred', 'recorded'],
      t=['There is no “double disbarment” — but the record matters at clemency.'])
    m('canon-vi-sec-44', 'Proceedings against lawyers are confidential; only the Supreme Court’s final order is published like its other decisions.',
      chk=['confidential'],
      w='To let the Court investigate free from outside pressure, to protect lawyers’ reputations against baseless charges, and to keep the press from trying the case first.',
      t=['Confidentiality binds the parties: a complainant who publicizes the complaint risks contempt.'],
      o='Rule 139-B, Sec. 18',
      d=[{'n': 'Fortun v. Quinsayas', 'c': 'G.R. No. 194578, February 13, 2013', 'h': 'Lawyers who distributed copies of a pending disbarment complaint to the media were held in indirect contempt for violating the confidentiality of disciplinary proceedings. The media outlets were not held liable: they reported a matter of public interest (the Maguindanao massacre case) and the respondent lawyer had become a public figure in it.', 'r': 'Purpose and limits of confidentiality.'}])
    m('canon-vi-sec-46', 'The sworn statement (Sec. 45) is proof of compliance with the suspension, and the lawyer may resume practice once it is filed with the Supreme Court. A false statement is a ground for disbarment; if the Bar Confidant finds one, it refers it to the Court within five days.',
      chk=['resume the practice of law', 'five (5) days'],
      t=['Resumption is upon filing — no separate order lifting the suspension is needed.'],
      d=[{'n': 'Maniago v. De Dios', 'c': 'A.C. No. 7472, March 30, 2010', 'h': 'The Court laid down the earlier guidelines: suspension is not automatically lifted at the end of the period; the lawyer files a sworn statement of non-practice, with copies to the courts where he or she has pending cases, and a false statement is ground for more severe punishment.', 'r': 'The pre-CPRA procedure that Secs. 45–46 build on.'}])
    m('canon-vi-sec-49', 'The Supreme Court first evaluates a clemency petition for prima facie merit under the Sec. 48 criteria. With merit, it refers the petition to the Bar Confidant or a fact-finding body; without merit, it denies it outright.',
      chk=['prima facie merit', 'denied outright'])
    m('canon-vi-sec-50', 'The Bar Confidant or designated body finishes its investigation and reports within ninety calendar days from referral.',
      chk=['ninety (90) calendar days'])
    m('canon-vi-sec-51', 'Judicial clemency is decided on clear and convincing evidence.',
      chk=['clear and convincing evidence'],
      t=['Contrast Sec. 32: discipline needs only substantial evidence; reinstatement after disbarment needs clear and convincing proof of reform. The higher bar is on the lawyer seeking to return.'])
    m('canon-vi-sec-53', 'Reasonable and necessary expenses of disciplinary and disbarment proceedings may be charged to the parties as costs, upon proof.',
      chk=['taxed as costs'], o='Rule 139-B, Sec. 19')

    # ------------------------------------------------------------ General provisions
    m('gp-sec-3', 'The CPRA takes effect fifteen calendar days after publication in the Official Gazette or a newspaper of general circulation. It was published in the Manila Bulletin and the Philippine Star on May 14, 2023, and took effect on May 29, 2023, according to OCA Circular No. 200-2023 (one later Supreme Court resolution, A.M. No. 23-05-05-SC, gives May 30).',
      chk=['fifteen (15) calendar days'],
      t=['Approved April 11, 2023 in Baguio City; launched April 13, 2023; effective May 29, 2023.'],
      i=[{'t': 'OCA Circular No. 200-2023', 's': 'Informed first- and second-level courts of the CPRA and of its effectivity on May 29, 2023, after publication on May 14, 2023.', 'u': 'https://oca.judiciary.gov.ph/wp-content/uploads/2023/05/OCA-Circular-No.-200-2023.pdf'}])
