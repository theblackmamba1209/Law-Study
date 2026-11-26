"""Enforcing a judgment: the playbook.
Written in our own words. Rules of Court references are to Rule 39 (Execution) and related rules as amended;
the Rules of Court are not in this library, so they are cited, not linked. Codal references link to the text.
Every case cited was checked against the decision (SC E-Library, LawPhil) or the Court's own release."""
import json, hashlib

def L(c, i, t): return {'c': c, 'i': i, 't': t}
def R(t): return {'t': t}

STAGES = [
  dict(id='s0', n=0, title='Before you win', short='Secure', goal='Build a judgment you can collect: freeze assets early, plead every liable person, and write a dispositive portion a sheriff can execute.'),
  dict(id='s1', n=1, title='From finality to writ', short='Writ', goal='Get the writ out fast, and ask in the same motion for every order you will need later.'),
  dict(id='s2', n=2, title='The writ in hand', short='Strike', goal='Hit everything at once before word spreads: demand, garnish every bank and debtor of the debtor, register the levy.'),
  dict(id='s3', n=3, title='When the debtor pushes back', short='Defend', goal='Answer the usual defenses: a third person claims the property, the family home, the spouse, a “supervening event”.'),
  dict(id='s4', n=4, title='Return unsatisfied: find the money', short='Find', goal='Use the supplementary proceedings: examine the debtor and his debtors under oath, apply income, appoint a receiver.'),
  dict(id='s5', n=5, title='Assets moved: follow them', short='Follow', goal='Undo transfers made to defeat you, and reach the new owner when the law allows.'),
  dict(id='s6', n=6, title='Special debtors', short='Special', goal='The government, a local government, a dead debtor, an employer answering for its employee.'),
  dict(id='s7', n=7, title='Judgments that are not for money', short='Acts', goal='Possession, demolition, a deed the loser will not sign, an act only he can do.'),
  dict(id='s8', n=8, title='Keep the judgment alive', short='Clock', goal='Watch the five-year and ten-year clocks, and keep the sheriff moving.'),
]

M = []
def move(**k): M.append(k)

# ---------------------------------------------------------------- s0
move(id='attach', stage='s0', title='Attach at the start, not at the end',
  hook='A preliminary attachment gives you a lien before judgment and a surety to collect from later.',
  when='The defendant contracted the debt by fraud, is hiding or disposing of property, is about to leave the country to defraud creditors, or cannot be found here.',
  steps=['Plead the specific facts of fraud or concealment in a verified complaint or affidavit; a bare allegation of fraud will not do.',
         'Post the applicant’s bond. The writ may issue ex parte, but it can be implemented only with or after service of summons, when the court has acquired jurisdiction over the defendant.',
         'If the defendant discharges the attachment with a counter-bond, keep the surety in your sights: once the judgment is executory, the surety is charged on the counter-bond and may be made to pay after notice and summary hearing in the same case.'],
  basis=[R('Rule 57, Sec. 1 (grounds), Sec. 5 (implementation with summons), Sec. 17 (recovery on the counter-bond)')],
  cases=[dict(n='Davao Light & Power Co. v. Court of Appeals', cite='G.R. No. 93262, December 29, 1991', held='A writ of preliminary attachment may be issued before summons, but enforcing it against the defendant requires the court’s jurisdiction over him.')],
  traps=['A wrongful attachment exposes you to damages on your bond.', 'Attachment does not replace the case: it secures the result.'])

move(id='lispendens', stage='s0', title='Annotate the title the day you file',
  hook='A notice of lis pendens makes every later buyer take the land subject to your case.',
  when='The action affects title to, or possession of, registered land.',
  steps=['Register a notice of lis pendens with the Register of Deeds where the land lies, identifying the case, the court and the title.',
         'If the defendant still sells the thing in litigation without the knowledge and approval of the litigants or the court, the sale is rescissible.'],
  basis=[L('pd1529', 'section-76', 'PD 1529, Sec. 76 (lis pendens)'), L('pd1529', 'section-52', 'PD 1529, Sec. 52 (constructive notice)'), L('civil', 'article-1381', 'Civil Code, Art. 1381(4)')],
  cases=[dict(n='Ada v. Baylon', cite='G.R. No. 182435, August 13, 2012', held='Rescission under Art. 1381(4) needs only that the defendant, while the case is pending, contracted over the thing in litigation without the knowledge and approval of the litigants or the court; it does not wait for a final ruling on ownership. It was sought by supplemental pleading in the same case.')],
  traps=['Lis pendens is for actions affecting the land itself, not a plain collection suit.'])

move(id='dispositive', stage='s0', title='Write the dispositive portion the sheriff will read',
  hook='Only the dispositive portion is executed. Make it complete.',
  when='Every case, from the complaint’s prayer to the proposed decision.',
  steps=['Pray for exact sums, the interest rate and the date it runs from (see the legal-interest shift: Nacar and Lara’s Gifts).',
         'If liability is solidary, say so expressly: solidarity is not presumed.',
         'Implead every person who may answer: co-obligors, the surety, and any company you suspect is the debtor’s alter ego. A non-party cannot ordinarily be reached by the writ.',
         'For property, describe it the way the title or tax declaration does.'],
  basis=[L('civil', 'article-1207', 'Civil Code, Art. 1207 (solidarity not presumed)')],
  cases=[dict(n='Kukan International Corp. v. Reyes', cite='G.R. No. 182729, September 29, 2010', held='A corporation never impleaded or served with summons cannot be made to answer through the writ; piercing the veil does not supply jurisdiction the court never had.')],
  traps=['A writ that goes beyond the dispositive portion is void to that extent.'])

# ---------------------------------------------------------------- s1
move(id='omnibus-writ', stage='s1', title='One motion, every order you will need',
  hook='Ask for the writ and for the orders that usually cost a second hearing.',
  when='As soon as the judgment is final and executory.',
  steps=['Move for execution in the court of origin with certified copies of the judgment and the entry of judgment. If the records are still with the appellate court, ask that court to direct the issuance of the writ.',
         'In the same motion, ask the court to approve the sheriff’s estimated expenses, to be deposited with the clerk of court.',
         'If structures stand on the land, ask for a special order of demolition, to issue after hearing and after the loser fails to remove them within the period the court fixes.',
         'If the loser must sign a deed, ask the court in the alternative for an order divesting his title and vesting it in your client.',
         'If the court refuses to issue the writ of a final judgment, the duty is ministerial: mandamus lies.'],
  basis=[R('Rule 39, Sec. 1 (execution as of right; appellate court may direct issuance), Sec. 10(a) and (d)'), R('Rule 141, Sec. 10 (sheriff’s expenses)'), R('Rule 65, Sec. 3 (mandamus)')],
  cases=[],
  traps=['Execution as of right still needs a motion with notice to the adverse party.'])

move(id='pending-appeal', stage='s1', title='Execute while the appeal is pending',
  hook='If waiting would make the judgment illusory, ask for discretionary execution.',
  when='The losing party appeals but you can show compelling, urgent reasons.',
  steps=['File the motion with notice while the trial court still has jurisdiction and holds the records; once it has lost jurisdiction, file it in the appellate court.',
         'Prove “good reasons”: circumstances so urgent they outweigh the harm to the loser if he wins on appeal. The court must state them in a special order.',
         'Expect the loser to offer a supersedeas bond to stay it.',
         'Remember the judgments not stayed by appeal at all: injunction, receivership, accounting and support. In ejectment the judgment against the defendant is immediately executory unless he appeals, files a supersedeas bond and keeps depositing the rentals. In labor cases the reinstatement aspect is executory at once, without a writ.'],
  basis=[R('Rule 39, Secs. 2, 3 and 4'), R('Rule 70, Secs. 19 and 21'), L('labor', 'article-229', 'Labor Code, Art. 229')],
  cases=[dict(n='Roxas v. Court of Appeals', cite='157 SCRA 370 (1988)', held='Posting a bond, by itself, is not a good reason for execution pending appeal; otherwise advance execution would become routine.'),
         dict(n='Pioneer Texturizing Corp. v. NLRC', cite='G.R. No. 118651, October 16, 1997', held='An award of reinstatement is self-executory; the employer must reinstate, actually or in the payroll, without waiting for a writ.')],
  traps=['If the executed judgment is reversed, the court may order restitution or reparation of damages (Rule 39, Sec. 5).'])

# ---------------------------------------------------------------- s2
move(id='demand', stage='s2', title='The demand comes first',
  hook='The sheriff must first demand payment in full; only then may he levy or garnish.',
  when='The writ is in the sheriff’s hands.',
  steps=['Go with the sheriff. Bring a computation sheet: principal, interest to date, costs and lawful fees.',
         'Payment is in cash, a certified bank check payable to your client, or any other form your client accepts.',
         'Note any refusal in writing; it will be in the sheriff’s return.'],
  basis=[R('Rule 39, Sec. 9(a)')],
  cases=[], traps=['A levy made without a prior demand invites a motion to quash and an administrative complaint against the sheriff.'])

move(id='garnish-banks', stage='s2', title='Garnish every bank on the same morning',
  hook='Serve notices of garnishment on every bank the debtor may use, at once, before he can move the money.',
  when='Immediately after the demand is refused.',
  steps=['Build the list before the writ issues: checks and deposit slips in your files, invoices with bank details, financial statements filed with the SEC, earlier payments in the case.',
         'Have the sheriff serve all the notices the same day. A garnishee bank must report to the court within five days whether it holds enough; the amount garnished is delivered directly to your client within ten working days of the notice to deliver.',
         'The garnishment covers only the judgment and lawful fees. If several banks hold deposits, the debtor may choose which pays; if he does not, your client chooses.',
         'Banks sometimes cite bank secrecy. It does not stand in the way of garnishment.'],
  basis=[R('Rule 39, Sec. 9(c)')],
  cases=[dict(n='China Banking Corp. v. Ortega', cite='G.R. No. L-34964, January 31, 1973', held='RA 1405 did not mean to put deposits beyond execution; a bank served with garnishment must say whether the debtor has a deposit, since the disclosure is only incidental to the court’s process.'),
         dict(n='Perla Compania de Seguros v. Ramolete', cite='G.R. No. L-60887, November 13, 1991', held='Service of the notice of garnishment alone binds the garnishee to the court; it need not be summoned or impleaded.')],
  traps=['Foreign-currency deposits are exempt from garnishment by law (RA 6426, Sec. 8); the one exception, Salvacion v. Central Bank (1997), turned on extraordinary facts.'])

move(id='garnish-receivables', stage='s2', title='Garnish what others owe the debtor',
  hook='A business debtor’s biggest asset is often what its customers, tenants and contract partners owe it.',
  when='The debtor runs a business, leases out property, has contract receivables, commissions, royalties or a salary.',
  steps=['List the debtor’s customers, tenants, principals and employer, and garnish each.',
         'A salary may be garnished. The Supreme Court has held that no law exempts a public official’s pay; the exemptions protect the wages of laborers (Civil Code, Art. 1708) and earnings for personal services within four months before the levy that the family needs for support.',
         'If the third person denies owing anything, the court cannot decide that denial summarily; use the route in Stage 4.'],
  basis=[R('Rule 39, Sec. 9(c) and Sec. 13(i)'), L('civil', 'article-1708', 'Civil Code, Art. 1708')],
  cases=[dict(n='Bagbagen v. Perez', cite='G.R. No. 274980, February 17, 2025', held='A city councilor’s salaries, deposited in his bank account, were validly garnished: no law exempts the salaries of public officials, and the wage exemptions favor laborers.')],
  traps=['Earnings the family needs for support, within the four months before the levy, are exempt.'])

move(id='levy', stage='s2', title='Levy, register, and register today',
  hook='Your lien runs from the levy; on registered land, register it the same day.',
  when='Cash and garnishment are not enough.',
  steps=['The debtor may choose which property to levy; if he does not choose at once, the sheriff levies first on personal property, then on real property.',
         'For titled land, register the writ and the notice of levy with the Register of Deeds. Registration is notice to the world.',
         'The levy creates a lien on the debtor’s interest as it stood at the levy, subject to liens already there. Check the title for earlier mortgages before you spend on a sale.',
         'Property of every kind not exempt may be levied: vehicles, shares, equipment, receivables, interests in an estate or a co-owned property.'],
  basis=[R('Rule 39, Secs. 9(b) and 12'), L('pd1529', 'section-69', 'PD 1529, Sec. 69 (registration of writs)'), L('pd1529', 'section-52', 'PD 1529, Sec. 52')],
  cases=[], traps=['Only enough property to satisfy the judgment and fees should be sold.'])

move(id='credit-bid', stage='s2', title='Bid your judgment at the auction',
  hook='As the judgment creditor you may buy without paying cash, up to the amount of the judgment.',
  when='There is no third-party claim and bidders are few.',
  steps=['Check the notice of sale: posting in three public places; for land, 20 days of posting, plus newspaper publication if the assessed value exceeds ₱50,000; written notice to the debtor at least three days before; the sale held between 9:00 a.m. and 2:00 p.m.',
         'Bid. If your client is the buyer and there is no third-party claim, he pays only the excess of the bid over the judgment.',
         'For land, the debtor may redeem within one year from registration of the certificate of sale by paying the price plus 1% a month, and the taxes and assessments the buyer paid, with interest at the same rate. Either way your client wins: the money with interest, or the land with a final deed.',
         'Until the redemption period ends, rents and income belong to the debtor. After it, the buyer gets the deed and possession, unless a third person holds the land adversely to the debtor.'],
  basis=[R('Rule 39, Secs. 15, 19, 21, 28, 32 and 33')],
  cases=[], traps=['A sale without the required notice can be set aside, and the officer is liable (Rule 39, Sec. 17).', 'The sheriff and his deputies cannot buy.'])

# ---------------------------------------------------------------- s3
move(id='terceria', stage='s3', title='A third person claims the property',
  hook='Decide fast: post an indemnity bond and keep the levy, or let it go and attack the transfer.',
  when='Someone other than the debtor serves an affidavit of title or right to possession on the sheriff.',
  steps=['The sheriff need not keep the property unless your client files a bond, approved by the court, for at least the value of the property.',
         'If you are confident the claim is a sham (a relative with no proof of payment, a transfer after the judgment), post the bond. A claim for damages against the bond must be filed within 120 days from its filing.',
         'The claimant may also sue separately to vindicate his claim, and your client may claim damages against a claimant whose claim is frivolous or plainly spurious.',
         'If the transfer to the claimant was real but made to defeat you, release the property and bring the accion pauliana (Stage 5).'],
  basis=[R('Rule 39, Sec. 16')],
  cases=[], traps=['A bond posted on a weak position can cost your client damages.'])

move(id='exemptions', stage='s3', title='Exemptions: know the list, insist it be claimed',
  hook='Exemption is the debtor’s personal privilege; he must claim and prove it before the sale.',
  when='The debtor says the property cannot be touched.',
  steps=['The list: the family home as the law provides; tools of trade; up to three beasts of burden; necessary clothing (not jewelry); household furniture and utensils up to ₱100,000; provisions for four months; professional libraries and equipment up to ₱300,000; one fishing boat and accessories up to ₱100,000; earnings needed for the family within four months before the levy; lettered gravestones; benefits growing out of life insurance; the right to support; government pensions and gratuities; and what special laws exempt.',
         'No item is exempt from execution on a judgment for its own price or for the foreclosure of a mortgage on it.',
         'If the debtor did not claim the exemption at the levy or within a reasonable time after, and before the sale, it is waived.'],
  basis=[R('Rule 39, Sec. 13')],
  cases=[dict(n='Honrado v. Court of Appeals', cite='G.R. No. 166333, November 25, 2005', held='The family-home exemption must be claimed by the debtor himself, not the sheriff, and presented before the execution sale; raised only after the sale and the lapse of the redemption period, it was barred.')],
  traps=['The burden of proving the exemption is on the debtor.'])

move(id='family-home', stage='s3', title='The family home is not a wall',
  hook='It is exempt only within limits, has four exceptions, and can be sold if it is worth more than the law protects.',
  when='The debtor invokes the family home.',
  steps=['Check the exceptions: taxes; debts incurred before the home was constituted; debts secured by a mortgage on it; debts to the laborers, builders and suppliers who built it.',
         'Check the date. A home occupied after August 3, 1988 is a family home from occupation. One occupied earlier is treated as constituted only on that date, unless it was constituted under the Civil Code, so debts incurred before that date are not barred.',
         'Check the value. If the home is worth more than the maximum the law protects (₱300,000 urban, ₱200,000 rural, at constitution), ask the court that rendered the judgment to order its sale. No bid below the protected value is accepted; the protected amount goes to the family first, then your client is paid, and any excess returns to the debtor.'],
  basis=[L('family', 'article-153', 'Family Code, Art. 153'), L('family', 'article-155', 'Art. 155 (exceptions)'), L('family', 'article-157', 'Art. 157 (maximum value)'), L('family', 'article-160', 'Art. 160 (sale of a home worth more)')],
  cases=[dict(n='Modequillo v. Breva', cite='G.R. No. 86355, May 31, 1990', held='The Family Code’s rules on the family home are not retroactive: an existing residence became a family home only when the Code took effect, so it was not exempt from a judgment for a debt that arose from a 1976 accident.')],
  traps=['Only the beneficiaries’ actual residence qualifies; a vacation house does not.'])

move(id='spouses', stage='s3', title='The debtor is married',
  hook='Find the property regime first; the community answers for a spouse’s debt only in the cases the Family Code lists.',
  when='The property is in both spouses’ names or acquired during the marriage.',
  steps=['Absolute community is the default for marriages from August 3, 1988 without a settlement; conjugal partnership for most earlier marriages.',
         'Under absolute community, debts contracted by one spouse without the other’s consent bind the community to the extent the family benefited. Liabilities from a crime or quasi-delict, and antenuptial debts that did not benefit the family, may be paid from the community when the debtor-spouse’s own property is absent or insufficient, as advances charged to that spouse’s share.',
         'Under conjugal partnership, personal debts are charged to the partnership only insofar as they benefited the family. Debts contracted before the marriage, fines and indemnities may be enforced against partnership assets only after its own obligations under Art. 121 are covered, and only if the debtor-spouse’s exclusive property is absent or insufficient.',
         'Build the proof of benefit to the family (a loan used for the family’s home or business) before you levy community or conjugal property.'],
  basis=[L('family', 'article-94', 'Family Code, Art. 94'), L('family', 'article-121', 'Art. 121'), L('family', 'article-122', 'Art. 122')],
  cases=[], traps=['Levying community property for a debt it does not answer for invites the other spouse’s third-party claim or separate action.'])

move(id='supervening', stage='s3', title='Answer the “supervening event”',
  hook='Only new facts, after finality, that make execution unjust or impossible, proven by competent evidence.',
  when='The debtor moves to stay or quash the writ.',
  steps=['Ask: did the fact arise after finality? Does it directly affect what was decided? Is it proven, not just alleged?',
         'Point out a rehash of defenses already decided.',
         'A lawyer who unduly impedes the execution of a warranted judgment violates the CPRA. Say so, with restraint.'],
  basis=[L('cpra', 'canon-iii-sec-7', 'CPRA, Canon III, Sec. 7(b) and (c)')],
  cases=[dict(n='Abrigo v. Flores', cite='G.R. No. 160786, June 17, 2013', held='A supervening event must alter the parties’ situation so that execution becomes inequitable, impossible or unfair, and cannot rest on unproved or uncertain facts; a claimed post-judgment sale of a share did not stop execution.')],
  traps=[])

# ---------------------------------------------------------------- s4
move(id='examine-debtor', stage='s4', title='Put the debtor under oath',
  hook='Once the return shows the judgment unsatisfied, the debtor must appear and answer about his property and income.',
  when='The sheriff’s return shows the judgment unpaid in whole or in part.',
  steps=['Move for an order to examine the debtor before the court or a commissioner, in the province or city where he lives or is found.',
         'Prepare it like a deposition: bank accounts, cards, vehicles, shares, businesses and their customers, receivables, inheritances, insurance, the spouse’s property, and every transfer in the last four years (that is your accion pauliana evidence).',
         'Attendance can be compelled by order or subpoena. Refusing to attend, to be sworn or to answer is contempt.'],
  basis=[R('Rule 39, Secs. 36 and 38')],
  cases=[], traps=['Examine only after an unsatisfied return; earlier, the motion is premature.'])

move(id='examine-third', stage='s4', title='Freeze what others hold for the debtor',
  hook='The order to examine the debtor’s debtor binds the credits and property in his hands from the moment it is served.',
  when='You can show the court that a person or company holds the debtor’s property or owes him money.',
  steps=['Move for an order requiring that person or company to appear and be examined. Proof to the court’s satisfaction is enough; an affidavit is one way, not the only way.',
         'From service of the order, the credits and property it covers are bound.',
         'If the person admits the debt, the court may order it applied to the judgment. A debtor of the debtor may also pay the sheriff directly.'],
  basis=[R('Rule 39, Secs. 37, 39 and 40')],
  cases=[], traps=[])

move(id='installments', stage='s4', title='Turn income into an order the court can enforce',
  hook='If the debtor earns more than his family needs, the court may order him to pay in monthly installments, on pain of contempt.',
  when='The debtor has a salary or steady income but nothing to levy.',
  steps=['After examining his current income and expenses, ask the court to fix monthly installments.',
         'Failure to pay an installment without good excuse may be punished as indirect contempt.',
         'This is the one lawful route by which a money judgment comes to be backed by contempt. Nonpayment of a money judgment as such is not contempt: the Rules provide levy and sale instead, and the Constitution forbids imprisonment for debt. What the Rule punishes is defiance, without excuse, of an order the court found he could obey.'],
  basis=[R('Rule 39, Sec. 40'), L('const1987', 'art-iii-sec-20', 'Constitution, Art. III, Sec. 20')],
  cases=[], traps=['Keep the record of the debtor’s income: without it there is no basis for the order.'])

move(id='receiver', stage='s4', title='A receiver for cash flow',
  hook='When the debtor has income but no seizable cash, a receiver can collect it for you.',
  when='Rental buildings, a running business, a stream of fees.',
  steps=['Ask the court to appoint a receiver of the debtor’s property and to forbid any transfer of, or interference with, his non-exempt property.',
         'Have the receiver collect rents and income and apply them to the judgment under the court’s direction.'],
  basis=[R('Rule 39, Sec. 41'), R('Rule 59 (receivership)')],
  cases=[], traps=['The receiver’s fees come out of what is collected; use it where the income is worth it.'])

move(id='denied-debt', stage='s4', title='The garnishee says he owes nothing',
  hook='The court cannot try the denial summarily, but it can freeze the claim while you sue.',
  when='A person said to owe the debtor, or to hold his property, denies it or claims it as his own.',
  steps=['Ask the court to authorize your client to sue that person for the debt or the property.',
         'Ask, in the same order, that any transfer of the interest or debt be forbidden for 120 days from notice, with disobedience punishable as contempt.',
         'File the action within that window.'],
  basis=[R('Rule 39, Sec. 43')],
  cases=[], traps=['Ordering a third person who denies the debt to pay, without a separate action, is a denial of due process.'])

# ---------------------------------------------------------------- s5
move(id='pauliana', stage='s5', title='Undo the transfer: the accion pauliana',
  hook='A transfer by a debtor already hit by a judgment, in any instance, is presumed made to defraud creditors.',
  when='The debtor gave away or sold property after you sued, and the writ has come back unsatisfied.',
  steps=['Know the presumptions. A donation is presumed fraudulent if the donor did not keep enough to pay his earlier debts. A sale or other onerous transfer is presumed fraudulent if made after a judgment against him in any instance, or after a writ of attachment was issued, even if neither concerned the property transferred.',
         'Without a presumption, prove the design to defraud by the usual badges: a relative or insider as buyer, a price far below value, the debtor staying in possession, secrecy, timing just after suit.',
         'Exhaust first. The action is subsidiary; it lies only when there is no other way to collect. It accrues when, after judgment and a writ, the sheriff fails to satisfy the claim, and it must be brought within four years from then.',
         'If the onerous transferee was in good faith, rescission does not reach the property; claim damages instead. A transferee in bad faith who cannot return the thing must pay for the loss.'],
  basis=[L('civil', 'article-1381', 'Civil Code, Art. 1381(3)'), L('civil', 'article-1383', 'Art. 1383 (subsidiary)'), L('civil', 'article-1387', 'Art. 1387 (presumptions)'), L('civil', 'article-1385', 'Art. 1385'), L('civil', 'article-1388', 'Art. 1388'), L('civil', 'article-1389', 'Art. 1389 (four years)')],
  cases=[dict(n='Khe Hong Cheng v. Court of Appeals', cite='G.R. No. 144169, March 28, 2001', held='The four years run not from registration of the donations but from the time the creditor discovered it had no other remedy, after judgment, a writ and the sheriff’s failure to find property.')],
  traps=['Filed before the writ is returned unsatisfied, the action is premature.'])

move(id='subrogatoria', stage='s5', title='Use the debtor’s own rights against others',
  hook='After pursuing the debtor’s property, you may exercise his rights and actions in his place.',
  when='The debtor has a claim he will not press: a debt owed to him, a share he will not collect.',
  steps=['Show that you first went after the property in his possession.',
         'Exercise his rights and actions, except those inherent in his person (for example, rights tied to his family status).'],
  basis=[L('civil', 'article-1177', 'Civil Code, Art. 1177')],
  cases=[], traps=[])

move(id='alter-ego', stage='s5', title='The assets moved to a company',
  hook='The writ does not reach a company that was never sued, save in the narrow case where it is plainly the debtor in another form.',
  when='The debtor’s business or property now sits in a new or related corporation.',
  steps=['Default rule: sue the company in a new action, alleging and proving that it is the debtor’s alter ego, or rescind the transfer to it.',
         'Narrow exception: where clear and convincing evidence shows the company was used to shield the debtor’s assets, especially its own admissions, the Court has allowed execution on its property (“reverse piercing”).',
         'See the doctrinal shift “Reaching a company that was never sued”.'],
  basis=[L('rcc', 'section-2', 'Revised Corporation Code, Sec. 2')],
  cases=[dict(n='Kukan International Corp. v. Reyes', cite='G.R. No. 182729, September 29, 2010', held='No execution against a corporation not impleaded and not under the court’s jurisdiction.'),
         dict(n='I/AME v. Litton and Co.', cite='G.R. No. 191525, December 13, 2017', held='Reverse piercing allowed at execution where the debtor conceived and funded the corporation, moved the property to it during the appeal, and the corporation’s own pleading admitted it was his alter ego.')],
  traps=['Reverse piercing is an exception the Court itself said should be used sparingly.'])

move(id='criminal-exposure', stage='s5', title='When hiding assets is a crime',
  hook='Absconding with property to prejudice creditors, and fictitious contracts, are crimes. File only on evidence, never as a threat.',
  when='The facts show the debtor fled with his property or executed a simulated sale.',
  steps=['Fraudulent insolvency: a person who absconds with his property to the prejudice of his creditors.',
         'Other deceits: a person who, to another’s prejudice, executes a fictitious contract.',
         'File the complaint only on evidence of the elements, and never use the threat of one to force payment.'],
  basis=[L('rpc', 'article-314', 'RPC, Art. 314'), L('rpc', 'article-316', 'RPC, Art. 316(4)'), L('cpra', 'canon-ii-sec-6', 'CPRA, Canon II, Sec. 6')],
  cases=[], traps=['A criminal case does not collect the money by itself; the civil remedies still do the work.'])

# ---------------------------------------------------------------- s6
move(id='government', stage='s6', title='The debtor is the government',
  hook='Public funds cannot be garnished. Go to the Commission on Audit, unless money has been appropriated for your judgment.',
  when='Judgment against the State, an agency, a state university or a local government.',
  steps=['File the money claim with the Commission on Audit, which has primary jurisdiction, even though a final judgment already validates it. Courts are told to observe utmost caution before issuing writs against government funds.',
         'Exception: funds already appropriated by law or ordinance for your specific judgment may be garnished.',
         'If a local government refuses, without justifiable reason, to pay a final judgment, mandamus lies to compel its council to enact the appropriation and to disburse it.',
         'Property of a local government devoted to public use cannot be levied.',
         'An official’s own salary, once in his personal account, is another matter: it may be garnished for his personal debts.'],
  basis=[L('const1987', 'section-29', 'Constitution, Art. VI, Sec. 29(1)'), R('PD 1445 (Government Auditing Code); SC Administrative Circular No. 10-2000')],
  cases=[dict(n='University of the Philippines v. Dizon', cite='G.R. No. 171182, August 23, 2012', held='UP’s funds are public funds that could not be garnished; the contractor’s claim, though already adjudged, had to be filed with COA.'),
         dict(n='City of Caloocan v. Allarde', cite='G.R. No. 107271, September 10, 2003', held='Garnishment of city funds was valid because a city ordinance had appropriated the exact sum for the employee’s back salaries.'),
         dict(n='Municipality of Makati v. Court of Appeals', cite='G.R. Nos. 89898-99, October 1, 1990', held='Where a municipality refuses without justifiable reason to pay a final money judgment, the claimant may seek mandamus to compel the appropriation and disbursement.')],
  traps=['A writ against public funds without an appropriation will be quashed.'])

move(id='dead-debtor', stage='s6', title='The debtor died',
  hook='Before the levy, the judgment becomes a claim against the estate; after the levy, the sale proceeds.',
  when='The judgment debtor dies.',
  steps=['If he died after the levy, the levied property may be sold to satisfy the judgment.',
         'If he died before the levy, present the money judgment as a claim in the settlement of his estate, within the time the probate court fixes.',
         'A judgment to recover property or enforce a lien on it is executed against the executor, administrator or successor in interest.'],
  basis=[R('Rule 39, Sec. 7'), R('Rule 86, Sec. 5 (claims against the estate)')],
  cases=[], traps=['A claim not filed in time in the estate proceedings is barred.'])

move(id='employer', stage='s6', title='The employee committed the crime: the employer pays',
  hook='An employer in industry is subsidiarily liable for its employee’s crime committed in the discharge of his duties.',
  when='A criminal judgment awards civil liability against an employee (a driver, a guard) and the writ against him comes back unsatisfied.',
  steps=['Move, in the same criminal case, for a subsidiary writ of execution against the employer.',
         'At the hearing, prove: the employment, that the employer is engaged in an industry, that the crime was committed in the discharge of the employee’s duties, and that the employee is insolvent (the unsatisfied return).',
         'The conviction binds the employer as to the civil liability.'],
  basis=[L('rpc', 'article-103', 'RPC, Art. 103')],
  cases=[dict(n='Basilio v. Court of Appeals', cite='G.R. No. 113433, March 17, 2000', held='The subsidiary liability is enforced in the same criminal case, after a hearing that establishes the four requisites.'),
         dict(n='Yonaha v. Court of Appeals', cite='G.R. No. 112346, March 29, 1996', held='The hearing is mandatory; a subsidiary writ issued without one was set aside.')],
  traps=[])

# ---------------------------------------------------------------- s7
move(id='possession', stage='s7', title='Possession: three working days, then out',
  hook='The sheriff demands that occupants leave within three working days; then he removes them, with police help if needed.',
  when='A judgment for delivery or restitution of real property.',
  steps=['The demand runs to the defendant and everyone claiming under him.',
         'Structures cannot be demolished without a special order, issued on motion after hearing and after the loser fails to remove them within the time fixed. Ask for it early.',
         'Document the turnover: inventory, photographs, a caretaker, new locks.',
         'If the ousted party re-enters, or induces others to, that is indirect contempt.'],
  basis=[R('Rule 39, Sec. 10(c) and (d)'), R('Rule 71, Sec. 3(b)')],
  cases=[], traps=['Costs and damages in the same judgment are collected like any money judgment.'])

move(id='conveyance', stage='s7', title='The loser will not sign the deed',
  hook='You do not need his signature: the court can sign for him, or simply transfer the title by order.',
  when='A judgment orders a conveyance, a deed or some act a third person can perform.',
  steps=['Ask the court to direct the act done, at the loser’s cost, by a person it appoints; the act has the same effect as if he did it.',
         'For property in the Philippines, ask instead for an order divesting his title and vesting it in your client. The order has the force of a conveyance; register it.'],
  basis=[R('Rule 39, Sec. 10(a)')],
  cases=[], traps=['Contempt is slower and unnecessary where the court can act in his place.'])

move(id='special-act', stage='s7', title='An act only he can perform',
  hook='For judgments that require some other act, disobedience is punished as contempt.',
  when='The judgment orders an act that no one else can do for him (and is not for money or delivery of property).',
  steps=['Have a certified copy of the judgment attached to the writ and served on the party.',
         'If he disobeys, move to cite him for contempt.'],
  basis=[R('Rule 39, Sec. 11'), R('Rule 71')],
  cases=[], traps=['Money and property judgments are executed by the sheriff under Secs. 9 and 10, not by contempt.'])

# ---------------------------------------------------------------- s8
move(id='clock', stage='s8', title='Five years by motion, ten by action',
  hook='Calendar both clocks the day the judgment becomes final.',
  when='Always.',
  steps=['By motion: within five years from entry of judgment. The writ stays in effect during that period.',
         'After that: an action to revive the judgment, within ten years from finality. The revived judgment can again be executed by motion within five years from its entry.',
         'Time during which execution was stayed (by injunction, by appeal with supersedeas, by agreement) and delays caused by the debtor or for his benefit are not counted against your client.'],
  basis=[R('Rule 39, Secs. 6 and 14'), L('civil', 'article-1144', 'Civil Code, Art. 1144(3)'), L('civil', 'article-1152', 'Art. 1152')],
  cases=[dict(n='Lancita v. Magbanua', cite='G.R. No. L-15467, January 31, 1963', held='In computing the time to enforce a judgment, periods when execution is stayed are excluded, and any delay caused by the debtor extends the time.'),
         dict(n='Perez v. Manotok Realty', cite='G.R. No. 216157, October 14, 2019', held='Reiterated Lancita: execution by motion may be allowed after five years where the delay was caused by, or benefited, the debtor.')],
  traps=['Equity extends the period only for delays not of your own making.'])

move(id='sheriff', stage='s8', title='Keep the sheriff moving, the right way',
  hook='The sheriff’s duty is ministerial, and he must report every thirty days until the judgment is paid.',
  when='Throughout execution.',
  steps=['Expenses go through the court: the sheriff estimates, the court approves, you deposit with the clerk, and the sheriff liquidates. Never hand money to the sheriff directly.',
         'If the judgment is not satisfied within 30 days of the sheriff’s receipt of the writ, he must report why, and then report every 30 days. Calendar the dates and ask for the reports.',
         'Unexplained inaction can be raised with the court and, if needed, in an administrative complaint with the Office of the Court Administrator.'],
  basis=[R('Rule 39, Sec. 14'), R('Rule 141, Sec. 10')],
  cases=[], traps=['Paying a sheriff outside the court’s approval exposes both of you to discipline.'])

DAY1 = [
  'Get certified copies of the writ, the judgment and the entry of judgment. Check that the writ matches the dispositive portion: parties, amounts, interest, solidary liability.',
  'Prepare a computation sheet: principal, interest to date at the correct rate, costs and lawful fees.',
  'Have the sheriff’s estimated expenses approved by the court and deposited with the clerk.',
  'Build the asset map: banks, receivables, titles at the Register of Deeds, vehicles, shares, businesses, the spouse’s property.',
  'Go with the sheriff for the demand.',
  'Serve every notice of garnishment the same morning.',
  'Register the levy on titled land the same day.',
  'Calendar: garnishee reports (5 days), delivery (10 working days), sheriff’s return (30 days, then every 30), the five- and ten-year limits.',
  'If the return comes back unsatisfied: move to examine the debtor and his debtors.',
]

GUARD = [
  dict(t='Do not impede, do not abuse', x='The CPRA forbids unduly impeding the execution of a warranted judgment, and abusing court processes. The first binds the loser’s lawyer; the second binds you.', l=L('cpra', 'canon-iii-sec-7', 'CPRA, Canon III, Sec. 7')),
  dict(t='No harassment, no threats', x='A lawyer shall not harass or threaten the other party. Criminal remedies are filed on evidence, not waved as leverage.', l=L('cpra', 'canon-ii-sec-6', 'CPRA, Canon II, Sec. 6')),
  dict(t='Money to the sheriff only through the court', x='Sheriff’s expenses are estimated, approved by the court, deposited with the clerk and liquidated.', l=None),
  dict(t='No imprisonment for debt', x='Creativity stops at the Constitution. Contempt is for defying specific orders, not for being unable to pay.', l=L('const1987', 'art-iii-sec-20', 'Constitution, Art. III, Sec. 20')),
]

DRILLS = [
  dict(id='d1', q='Two months after the RTC rendered judgment against him (now on appeal), D sold his only lot to his brother for a fraction of its value. The judgment became final; the writ came back unsatisfied. Your best move?',
       options=['Levy on the lot as if it were still D’s', 'Accion pauliana: the sale is presumed fraudulent because it came after a judgment against D in any instance', 'Cite D for contempt for selling', 'Nothing: the sale was registered'],
       a=1, why='Art. 1387 presumes fraud in an onerous alienation made after a judgment against the debtor in any instance. The action accrued when the writ was returned unsatisfied (Khe Hong Cheng).', m=['pauliana']),
  dict(id='d2', q='The bank served with a notice of garnishment refuses to say whether the debtor has a deposit, citing the Bank Secrecy Law. What do you tell the court?',
       options=['The bank is right; get the depositor’s written consent', 'Garnishment is not the inquiry the law forbids; the disclosure is incidental, and the bank must comply', 'Bank deposits can never be garnished', 'File a separate action against the bank'],
       a=1, why='China Banking Corp. v. Ortega: RA 1405 did not put deposits beyond execution. Only foreign-currency deposits are exempt by law.', m=['garnish-banks']),
  dict(id='d3', q='A city lost a final money judgment. The sheriff garnished the city’s general funds in its depository bank. No ordinance appropriates money for the judgment. The garnishment is…',
       options=['valid, because the judgment is final', 'invalid; the claimant should go to COA and, if the city refuses without justification, seek mandamus to compel the appropriation', 'valid if the funds exceed the judgment', 'valid if the mayor consents'],
       a=1, why='Public funds are not garnishable absent an appropriation for the judgment (Municipality of Makati; contrast City of Caloocan v. Allarde, where an ordinance appropriated the sum). Money claims go to COA (UP v. Dizon).', m=['government']),
  dict(id='d4', q='After the sheriff ousted the defendant and turned the land over to your client, the defendant came back and fenced off a portion. Fastest remedy?',
       options=['File a new ejectment case', 'Indirect contempt: re-entry after being ejected by court process', 'Ask the sheriff to levy on the defendant’s car', 'File for damages'],
       a=1, why='Rule 71, Sec. 3(b) treats re-entry, or inducing others to enter, after dispossession by court process as indirect contempt.', m=['possession']),
  dict(id='d5', q='A final judgment orders the defendant to execute a deed of sale of a lot in Laguna in your client’s favor. He refuses. Best move?',
       options=['Contempt until he signs', 'Ask the court for an order divesting his title and vesting it in your client, and register it', 'Wait for him to change his mind', 'File a new action for specific performance'],
       a=1, why='Rule 39, Sec. 10(a): for property in the Philippines, the court may divest and vest title by order, with the effect of a conveyance.', m=['conveyance']),
  dict(id='d6', q='Your debtor’s business is now run by a new corporation that was never a party. The sheriff wants to levy on its trucks. The general rule says…',
       options=['levy away; piercing is automatic', 'the corporation, not impleaded, is beyond the writ (Kukan) unless clear proof, ideally its own admission, shows it is the debtor’s alter ego used to evade the judgment (I/AME)', 'only the SEC can decide', 'the trucks are exempt'],
       a=1, why='Kukan is the rule; I/AME v. Litton is a narrow exception. Otherwise sue the corporation or rescind the transfer.', m=['alter-ego']),
  dict(id='d7', q='Entry of judgment was six years ago. For two of those years the debtor’s TRO stopped execution. May you still move for execution?',
       options=['No, five years have passed', 'Yes: the period of the stay, caused by the debtor, is not counted', 'Only by a new action', 'Only with the debtor’s consent'],
       a=1, why='Lancita v. Magbanua and later cases exclude periods when execution was stayed, and delays caused by the debtor.', m=['clock']),
  dict(id='d8', q='A bus driver was convicted of reckless imprudence resulting in homicide; the writ for civil indemnity against him came back unsatisfied. The bus company was not a party. Remedy?',
       options=['A new civil case against the company is the only way', 'A motion in the same criminal case for a subsidiary writ against the employer, after a hearing on the requisites', 'Nothing: the company was never charged', 'Garnish the company’s accounts at once without hearing'],
       a=1, why='RPC Art. 103; Basilio v. CA and Yonaha v. CA: enforce in the same case, but only after a hearing.', m=['employer']),
  dict(id='d9', q='At the levy and auction the debtor said nothing. A year later, after the redemption period, he claims the house was his family home. The claim is…',
       options=['valid; the family home is always exempt', 'too late: the exemption must be claimed by the debtor before the sale', 'valid if the house is in an urban area', 'for the sheriff to decide'],
       a=1, why='Honrado v. CA: the exemption is personal and must be presented before the execution sale.', m=['exemptions', 'family-home']),
  dict(id='d10', q='The debtor earns a good salary but owns nothing to levy. Which tool makes payment enforceable by contempt?',
       options=['Imprisonment for the debt', 'An order under Rule 39, Sec. 40 fixing monthly installments after examining his income', 'A criminal complaint for estafa', 'A writ of possession'],
       a=1, why='Sec. 40 lets the court order installments if earnings exceed family needs; unexcused default is indirect contempt. Imprisonment for debt itself is barred by Art. III, Sec. 20.', m=['installments']),
]

out = {'built': 'enforce', 'stages': STAGES, 'moves': M, 'day1': DAY1, 'guard': GUARD, 'drills': DRILLS,
       'note': 'Study aid in our own words. The Rules of Court are cited by section; check the current text, as amended, before you file.'}
js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open('/home/claude/site/data/enforce.json', 'w').write(js)
cat = json.load(open('/home/claude/site/data/catalog.json'))
cat['ehash'] = hashlib.md5(js.encode()).hexdigest()[:10]
json.dump(cat, open('/home/claude/site/data/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(STAGES), 'stages', len(M), 'moves', len(DRILLS), 'drills')
