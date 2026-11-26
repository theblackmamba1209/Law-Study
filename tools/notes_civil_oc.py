"""Civil Code, Obligations and Contracts (Arts. 1156-1422): study notes in our own words, merged into data/notes/civil.json.
'chk' holds words the note relies on that must appear in the verbatim article; the script fails otherwise.
"""
import json

SITE = '/home/claude/site/data'
N = {}


def n(a, x, t=None, k=None, d=None, chk=()):
    e = {'x': x}
    if t: e['t'] = t
    if k: e['k'] = k
    if d: e['d'] = [{'n': a1, 'c': b, 'h': c, 'r': r} for a1, b, c, r in d]
    N[f'article-{a}'] = (e, chk)


# ---------------------------------------------------------------- general provisions and nature of obligations
n(1158, 'Obligations created by law are not presumed; only those expressly determined in the Code or special laws are demandable, governed by the law that creates them and suppletorily by this Book.')
n(1160, 'Obligations from quasi-contracts are governed by Chapter 1, Title XVII (negotiorum gestio, solutio indebiti and the others).')
n(1161, 'Civil obligations from criminal offenses are governed by the penal laws, subject to the Civil Code’s provisions on human relations (Art. 2177) and damages.')
n(1162, 'Obligations from quasi-delicts are governed by Chapter 2, Title XVII (Arts. 2176 ff.) and by special laws.')
n(1163, 'One obliged to give a determinate thing must take care of it with the proper diligence of a good father of a family, unless the law or the parties require another standard.', chk=['good father of a family'])
n(1164, 'The creditor has a right to the fruits of the thing from the time the obligation to deliver it arises, but acquires no real right over it until it is delivered.', t=['Before delivery the creditor has only a personal right (jus ad rem), not a real right (jus in re).'])
n(1165, 'If the debtor fails to deliver a determinate thing, the creditor may compel specific performance; if a generic thing, the creditor may have it delivered at the debtor’s cost. A debtor in delay, or who promised the same thing to two or more persons with separate interests, bears the loss even by fortuitous event until delivery.')
n(1167, 'If a person obliged to do something fails to do it, it is executed at his cost; the same if he does it in contravention of the obligation, or poorly, and what was badly done may be undone.')
n(1168, 'When the obligation consists in not doing, and the obligor does what was forbidden, it is undone at his expense.')
n(1169, 'Those obliged to deliver or to do something incur delay from the time the creditor judicially or extrajudicially demands fulfillment. Demand is unnecessary when the obligation or the law so declares, when time was the controlling motive, or when demand would be useless. In reciprocal obligations, from the moment one party fulfills, delay by the other begins.',
  k=['Mora solvendi (debtor’s delay); mora accipiendi (creditor’s delay); compensatio morae (both in delay in reciprocal obligations: neither is in delay).'],
  t=['Default generally needs a demand; a fixed due date alone is not enough unless one of the exceptions applies.'])
n(1171, 'Responsibility arising from fraud is demandable in all obligations; any waiver of an action for future fraud is void.', chk=['void'])
n(1172, 'Responsibility arising from negligence is also demandable, but courts may regulate it according to the circumstances.', t=['Unlike future fraud, liability for future negligence may be waived, except where public policy forbids (e.g., gross negligence, or common carriers).'])
n(1175, 'Usurious transactions are governed by special laws.', t=['Usury ceilings were suspended (CB Circular No. 905, 1982), but courts still void unconscionable interest rates.'])
n(1176, 'A receipt of the principal without reservation about interest raises the presumption that the interest has been paid; a receipt for a later installment without reservation as to prior ones raises the presumption that the prior ones were paid.')
n(1177, 'Creditors, after exhausting the debtor’s property in possession, may exercise all the debtor’s rights and actions except those inherent in his person (accion subrogatoria), and may impugn acts the debtor did to defraud them (accion pauliana).', k=['Remedies of creditors: specific performance or damages; exhaustion of the debtor’s assets; accion subrogatoria; accion pauliana; and in special cases accion directa.'])
n(1178, 'Rights acquired by virtue of an obligation are transmissible, if there is no stipulation or law to the contrary.')

# ---------------------------------------------------------------- pure and conditional obligations
n(1179, 'An obligation whose performance does not depend on a future or uncertain event, or on a past event unknown to the parties, is demandable at once. An obligation with a resolutory condition is also demandable at once, without prejudice to the effects of the happening of the event.')
n(1181, 'In conditional obligations, rights are acquired upon the happening of a suspensive condition; rights already acquired are lost upon the happening of a resolutory condition.')
n(1182, 'When the fulfillment of the condition depends on the sole will of the debtor, the conditional obligation is void. If it depends on chance or the will of a third person, the obligation takes effect.',
  t=['Only a suspensive condition potestative on the debtor voids the obligation; a resolutory condition depending on the debtor’s will is valid. A condition depending on the creditor’s will is valid.'])
n(1183, 'Impossible conditions, those contrary to good customs or public policy, and those prohibited by law annul the obligation that depends on them. A condition not to do an impossible thing is considered as not having been agreed upon.')
n(1186, 'A condition is deemed fulfilled when the obligor voluntarily prevents its fulfillment (constructive fulfillment).')
n(1187, 'Once a suspensive condition is fulfilled, its effects retroact to the day the obligation was constituted; but in obligations to give, fruits and interests during the pendency are deemed mutually compensated in reciprocal obligations.')
n(1189, 'Rules when a determinate thing is lost, deteriorates or improves before a suspensive condition happens: loss without the debtor’s fault extinguishes the obligation; loss through his fault makes him liable for damages; deterioration without fault is borne by the creditor; deterioration through fault gives the creditor the choice of rescission or fulfillment, with damages either way; improvement by nature or time inures to the creditor; improvement at the debtor’s expense gives him only the usufructuary’s rights.')
n(1190, 'When a resolutory condition is fulfilled, the parties must return to each other what they received, applying Art. 1189’s rules to the one who must return.')

# ---------------------------------------------------------------- obligations with a period
n(1193, 'Obligations with a day certain become demandable only when that day comes. A day certain is one that must necessarily come, even if it is not known when.', t=['If the uncertainty is whether the day will come at all, it is a condition, not a period.'])
n(1195, 'Anything paid or delivered before the period, in the belief that it was due, may be recovered with fruits and interests.')
n(1196, 'Whenever a period is designated, it is presumed established for the benefit of both creditor and debtor, unless the tenor of the obligation or other circumstances show otherwise.')
n(1197, 'If the obligation does not fix a period but it can be inferred that one was intended, the courts may fix it. They also fix it when its duration depends on the debtor’s will. Once fixed by the court, the period cannot be changed by the parties.',
  t=['The court must fix the period in a proper action first; it cannot be fixed in an action for specific performance that assumes the obligation is already due (unless both are prayed for).'])
n(1198, 'The debtor loses the benefit of the period when: he becomes insolvent after the obligation is contracted, unless he gives a guaranty; he does not furnish promised guaranties or securities; he impairs them, or they disappear through fortuitous event, unless he gives new ones; he violates any undertaking in consideration of which the creditor agreed to the period; or he attempts to abscond.')

# ---------------------------------------------------------------- alternative, facultative, joint and solidary
n(1199, 'In alternative obligations, the debtor is bound to give one of several prestations, and must completely perform one of them; the creditor cannot be compelled to receive part of one and part of another.')
n(1200, 'The right of choice belongs to the debtor, unless it has been expressly granted to the creditor. The debtor may not choose prestations that are impossible, unlawful, or could not have been the object of the obligation.')
n(1201, 'The choice produces no effect except from the time it has been communicated.')
n(1206, 'A facultative obligation has only one prestation, but the debtor may render another in substitution. Loss of the substitute through the debtor’s fault does not make him liable; loss of the principal thing through fortuitous event extinguishes the obligation.', t=['Alternative: several things are due, one is chosen. Facultative: one thing is due, another may be substituted.'])
n(1207, 'Concurrence of two or more creditors or debtors in one obligation does not imply that each may demand, or must render, the entire prestation. There is solidary liability only when the obligation expressly so states, or when the law or the nature of the obligation requires it.', t=['The presumption is joint, not solidary. Solidarity by law: e.g., co-principals in a quasi-delict (Art. 2194).'])
n(1208, 'If from the law or the nature or wording of the obligation nothing indicates otherwise, the credit or debt is presumed divided into as many equal shares as there are creditors or debtors, the credits or debts being distinct from one another.')
n(1211, 'Solidarity may exist even if the creditors and debtors are not bound in the same manner, for the same periods and under the same conditions.')
n(1212, 'Each solidary creditor may do whatever may be useful to the others, but not anything prejudicial to them.')
n(1214, 'The debtor may pay any one of the solidary creditors, but if any of them has made a judicial demand, payment should be made to him.')
n(1215, 'Novation, compensation, confusion or remission of the debt made by any of the solidary creditors or with any of the solidary debtors extinguishes the obligation; the creditor who did it is liable to the others for their shares.')
n(1216, 'The creditor may proceed against any one, some or all of the solidary debtors simultaneously. Demand on one does not bar later demands on the others while the debt has not been fully collected.')
n(1217, 'Payment by one solidary debtor extinguishes the obligation; he may claim from his co-debtors only the share corresponding to each, with interest for the payment already made.')
n(1222, 'A solidary debtor may use all defenses derived from the nature of the obligation and those personal to him or pertaining to his own share; defenses personal to the others may be used only as regards the share of the debt for which they are responsible.')
n(1223, 'The divisibility or indivisibility of the things that are the object of an obligation in which there is only one debtor and one creditor does not alter or modify its provisions.')
n(1226, 'In obligations with a penal clause, the penalty substitutes for indemnity for damages and the payment of interest in case of non-compliance, unless otherwise stipulated. Damages may still be recovered if the obligor refuses to pay the penalty or is guilty of fraud.')
n(1229, 'The judge shall equitably reduce the penalty when the principal obligation has been partly or irregularly complied with, and even if there has been no performance, if the penalty is iniquitous or unconscionable.')

# ---------------------------------------------------------------- extinguishment
n(1231, 'Obligations are extinguished by payment or performance, loss of the thing due, condonation or remission, confusion or merger, compensation, and novation. Other causes: annulment, rescission, fulfillment of a resolutory condition, and prescription.')
n(1233, 'A debt is not understood to have been paid unless the thing or service in which the obligation consists has been completely delivered or rendered.')
n(1235, 'When the creditor accepts performance knowing its incompleteness or irregularity and without protest or objection, the obligation is deemed fully complied with.')
n(1236, 'The creditor is not bound to accept payment from a third person who has no interest in the fulfillment, unless otherwise stipulated. A third person who pays may recover what he paid; if he paid without the debtor’s knowledge or against his will, he may recover only insofar as the payment benefited the debtor.')
n(1240, 'Payment must be made to the person in whose favor the obligation was constituted, or his successor in interest, or any person authorized to receive it.', t=['Payment to the wrong person does not extinguish the debt, except as Arts. 1241–1242 provide (e.g., payment in good faith to one in possession of the credit).'])
n(1242, 'Payment made in good faith to any person in possession of the credit releases the debtor.')
n(1244, 'The debtor of a thing cannot compel the creditor to receive a different one, even if of equal or greater value.')
n(1245, 'Dation in payment (dacion en pago), whereby property is alienated to the creditor in satisfaction of a debt in money, is governed by the law on sales.')
n(1248, 'Unless expressly stipulated, the creditor cannot be compelled partially to receive the prestations, nor the debtor to make partial payments.')
n(1249, 'Payment of debts in money must be made in the currency stipulated, or if not possible, in the currency that is legal tender in the Philippines. Checks and other mercantile documents produce the effect of payment only when cashed, or when impaired through the creditor’s fault.',
  t=['A check is not legal tender; a creditor may refuse it. Tender of a check may still be valid where the creditor did not object to it on that ground.'], chk=['legal tender'])
n(1250, 'In case an extraordinary inflation or deflation of the currency supervenes, the value of the currency at the time the obligation was established is the basis of payment, unless there is an agreement to the contrary.', t=['The extraordinary inflation must be officially declared, and the article applies to contractual obligations only.'])
n(1252, 'One who has various debts of the same kind in favor of one creditor may declare, when paying, to which of them the payment applies (application of payments); if the debtor accepts a receipt in which the creditor applied it, he cannot complain unless there was a cause invalidating the contract.')
n(1254, 'When payment cannot be applied by the rules, it is deemed applied to the debt which is most onerous to the debtor among those due; if they are of the same nature and burden, proportionately.')
n(1255, 'The debtor may cede or assign his property to his creditors in payment of his debts (cession), which releases him only up to the net proceeds of the property, unless otherwise agreed.')
n(1256, 'If the creditor refuses without just cause to accept the payment, the debtor is released by consignation of the thing or sum due. Consignation alone also releases him, without prior tender, when the creditor is absent or unknown, incapacitated, refuses to issue a receipt without just cause, two or more persons claim the same right to collect, or the title has been lost.',
  k=['Requisites: a valid existing debt; a valid prior tender (unless excused); prior notice of consignation to the persons interested; actual deposit with the court; subsequent notice of the consignation.'],
  t=['Tender of payment without consignation does not extinguish the debt.'])
n(1262, 'An obligation to deliver a determinate thing is extinguished if it is lost or destroyed without the debtor’s fault and before he has incurred delay. Even with a fortuitous event, he is liable when the law or the stipulation so provides, or when the nature of the obligation requires the assumption of risk.')
n(1263, 'In an obligation to deliver a generic thing, its loss or destruction does not extinguish the obligation (genus nunquam perit).')
n(1266, 'The debtor in obligations to do is also released when the prestation becomes legally or physically impossible without his fault.')
n(1267, 'When the service has become so difficult as to be manifestly beyond the contemplation of the parties, the obligor may also be released in whole or in part (rebus sic stantibus).', t=['Applied sparingly: it does not cover mere increases in cost or ordinary business risk.'])
n(1270, 'Condonation or remission is essentially gratuitous and requires the obligor’s acceptance. It may be express or implied; express condonation must comply with the forms of donation.')
n(1275, 'The obligation is extinguished from the time the characters of creditor and debtor are merged in the same person (confusion).')
n(1278, 'Compensation takes place when two persons, in their own right, are creditors and debtors of each other.')
n(1279, 'Requisites of legal compensation: each obligor is bound principally and is at the same time a principal creditor of the other; both debts consist in sums of money, or of consumable things of the same kind and quality if specified; both debts are due; both are liquidated and demandable; and neither is subject to a retention or controversy commenced by third persons and communicated in due time to the debtor.', chk=['liquidated and demandable'])
n(1287, 'Compensation shall not be proper when one of the debts arises from a depositum or from the obligations of a depositary or bailee in commodatum; nor can it be set up against a creditor who has a claim for support due by gratuitous title.', t=['Bank deposits are loans, not depositum, so banks may set off a depositor’s debts against his deposits.'])
n(1288, 'Compensation shall not be proper when one of the debts consists in civil liability arising from a penal offense.')
n(1290, 'When all the requisites concur, compensation takes effect by operation of law, and extinguishes both debts to the concurrent amount, even though the creditors and debtors are not aware of it.')
n(1291, 'Obligations may be modified by changing their object or principal conditions, by substituting the person of the debtor, or by subrogating a third person in the rights of the creditor.')
n(1292, 'For an obligation to be extinguished by another that substitutes it, this must be declared in unequivocal terms, or the old and the new obligations must be on every point incompatible with each other.', t=['Novation is never presumed. A mere extension of time or a change in the manner of payment does not extinguish the obligation.'])
n(1293, 'Novation by substituting a new debtor in place of the original one may be made even without his knowledge or against his will, but not without the creditor’s consent.', k=['Expromision: the new debtor’s initiative. Delegacion: the old debtor’s initiative.'])
n(1300, 'Subrogation of a third person in the creditor’s rights is either legal or conventional. Legal subrogation is not presumed except in the cases expressly mentioned in the Code; conventional subrogation must be clearly established.')
n(1302, 'Legal subrogation is presumed when a creditor pays another creditor who is preferred, even without the debtor’s knowledge; when a third person not interested in the obligation pays with the debtor’s express or tacit approval; and when one interested in the fulfillment pays, even without the debtor’s knowledge.')

# ---------------------------------------------------------------- contracts
n(1306, 'Parties may establish such stipulations, clauses, terms and conditions as they deem convenient, provided they are not contrary to law, morals, good customs, public order or public policy (autonomy of contracts).')
n(1307, 'Innominate contracts are regulated by the stipulations of the parties, by the general principles on obligations and contracts, by the rules on the most analogous nominate contracts, and by the customs of the place.', k=['Do ut des, do ut facias, facio ut des, facio ut facias.'])
n(1308, 'The contract must bind both contracting parties; its validity or compliance cannot be left to the will of one of them (mutuality of contracts).', t=['A unilateral escalation clause allowing the lender alone to raise interest rates violates mutuality.'])
n(1311, 'Contracts take effect only between the parties, their assigns and heirs, except where the rights and obligations are not transmissible. A stipulation in favor of a third person (stipulation pour autrui) may be demanded by him if he communicated his acceptance to the obligor before its revocation.',
  k=['Requisites of stipulation pour autrui: the stipulation is in favor of a third person; it is part, not the whole, of the contract; the parties clearly and deliberately conferred a favor on him; the third person communicated his acceptance before revocation; neither party represents him.'])
n(1314, 'Any third person who induces another to violate his contract shall be liable for damages to the other contracting party (tortious interference).',
  d=[('So Ping Bun v. Court of Appeals', 'G.R. No. 120554, September 21, 1999', 'A person who induced a lessor to lease premises to him, knowing they were leased to another, was liable for interference; but where the interferer acted to protect a legitimate business interest without malice, damages may not be awarded.', 'Elements of interference.')])
n(1315, 'Contracts are perfected by mere consent; from that moment the parties are bound to fulfill what was expressly stipulated and all consequences that, according to their nature, may be in keeping with good faith, usage and law.')
n(1316, 'Real contracts, such as deposit, pledge and commodatum, are not perfected until the object is delivered.')
n(1317, 'No one may contract in the name of another without being authorized by him or having a right to represent him. A contract entered into in another’s name without authority is unenforceable, unless ratified expressly or impliedly by the person in whose name it was made before it is revoked by the other party.')
n(1319, 'Consent is manifested by the meeting of the offer and the acceptance upon the thing and the cause. The offer must be certain and the acceptance absolute; a qualified acceptance is a counter-offer. Acceptance by letter or telegram binds the offerer only from the time it came to his knowledge (cognition theory).')
n(1320, 'An acceptance may be express or implied.')
n(1323, 'An offer becomes ineffective upon the death, civil interdiction, insanity or insolvency of either party before acceptance is conveyed.')
n(1324, 'When the offerer has allowed the offeree a certain period to accept, the offer may be withdrawn at any time before acceptance by communicating the withdrawal, except when the option is founded upon a consideration, as something paid or promised.',
  d=[('Sanchez v. Rigos', 'G.R. No. L-25494, June 14, 1972', 'An option without a separate consideration is a mere offer, which the offeror may withdraw; but if it is accepted before withdrawal, a bilateral contract of sale is perfected.', 'Option contracts.')])
n(1326, 'Advertisements for bidders are simply invitations to make proposals; the advertiser is not bound to accept the highest or lowest bidder, unless the contrary appears.')
n(1327, 'Unemancipated minors, and insane or demented persons and deaf-mutes who do not know how to write, cannot give consent to a contract.', t=['The contract is voidable (Art. 1390), not void; if both parties are incapacitated, it is unenforceable (Art. 1403(3)).'])
n(1330, 'A contract where consent is given through mistake, violence, intimidation, undue influence or fraud is voidable.')
n(1331, 'To invalidate consent, the mistake must refer to the substance of the thing, or to conditions that principally moved the parties to contract. Mistake as to identity or qualifications of a person invalidates only when they were the principal cause.')
n(1335, 'Violence is serious or irresistible force used to wrest consent. Intimidation is a reasonable and well-grounded fear of an imminent and grave evil upon one’s person or property, or that of one’s spouse, descendants or ascendants. A threat to enforce a just or legal claim through competent authority does not vitiate consent.')
n(1337, 'There is undue influence when a person takes improper advantage of his power over the will of another, depriving the latter of a reasonable freedom of choice.')
n(1338, 'There is fraud when, through insidious words or machinations of one party, the other is induced to enter into a contract which, without them, he would not have agreed to.', t=['Only causal fraud (dolo causante) makes a contract voidable; incidental fraud (dolo incidente, Art. 1344) only gives rise to damages.'])
n(1344, 'To make a contract voidable, the fraud should be serious and should not have been employed by both parties. Incidental fraud only obliges the person who employed it to pay damages.')
n(1345, 'Simulation of a contract may be absolute (the parties do not intend to be bound at all) or relative (they conceal their true agreement).')
n(1346, 'An absolutely simulated or fictitious contract is void. A relatively simulated contract binds the parties to their real agreement, when it does not prejudice a third person and is not intended for an illicit purpose.')
n(1347, 'All things that are not outside the commerce of men, including future things, may be the object of a contract. Rights not intransmissible may also be. No contract may be entered into on future inheritance except in cases expressly authorized by law.')
n(1350, 'In onerous contracts the cause is the prestation or promise of a thing or service by the other; in remuneratory ones, the service or benefit remunerated; in contracts of pure beneficence, the mere liberality of the benefactor.', t=['Cause (why the obligation exists, the same in every contract of its kind) is not motive (the personal reason, which varies).'])
n(1352, 'Contracts without cause, or with unlawful cause, produce no effect whatever. The cause is unlawful if it is contrary to law, morals, good customs, public order or public policy.')
n(1355, 'Except in cases specified by law, lesion or inadequacy of cause does not invalidate a contract, unless there has been fraud, mistake or undue influence.')
n(1356, 'Contracts are obligatory in whatever form they may have been entered into, provided all the essential requisites for their validity are present. When the law requires a form for validity or enforceability, that requirement is absolute.')
n(1358, 'Acts and contracts that must appear in a public document include those creating, transmitting, modifying or extinguishing real rights over immovable property, and others listed.', t=['The form in Art. 1358 is for convenience, not validity: an oral or private sale of land is valid between the parties, who may compel each other to execute the public instrument (Art. 1357).'])
n(1359, 'When the true intention of the parties is not expressed in the instrument because of mistake, fraud, inequitable conduct or accident, either party may ask for reformation of the instrument.', t=['Reformation corrects the document to express the true agreement; annulment sets aside the agreement itself.'])
n(1370, 'If the terms of a contract are clear and leave no doubt on the intention of the parties, the literal meaning of its stipulations controls. If the words seem contrary to the evident intention of the parties, the latter prevails.')
n(1377, 'The interpretation of obscure words or stipulations in a contract shall not favor the party who caused the obscurity.', t=['Contracts of adhesion are valid, but ambiguities in them are construed strictly against the party who drafted them.'])

# ---------------------------------------------------------------- defective contracts
n(1380, 'Contracts validly agreed upon may be rescinded in the cases established by law.', k=['Defective contracts, from least to most defective: rescissible, voidable, unenforceable, void.'])
n(1381, 'Rescissible contracts: those entered into by guardians when the ward suffers lesion of more than one-fourth of the value of the things; those agreed upon in representation of absentees, with the same lesion; those undertaken in fraud of creditors who cannot collect in any other manner; those referring to things under litigation if entered into without the knowledge and approval of the litigants or the court; and others specially declared by law.', chk=['one-fourth'])
n(1383, 'The action for rescission is subsidiary: it cannot be instituted except when the injured party has no other legal means to obtain reparation.')
n(1385, 'Rescission obliges the return of the things that were the object of the contract, with their fruits, and of the price with its interest. It cannot take place when the things are legally in the possession of third persons who did not act in bad faith.')
n(1387, 'Alienations by gratuitous title are presumed fraudulent when the debtor did not reserve sufficient property to pay all debts contracted before the donation. Alienations by onerous title are presumed fraudulent when made by persons against whom a judgment has been issued or a writ of attachment issued.', t=['Other badges of fraud (inadequate price, transfer to a relative, keeping possession) are recognized by jurisprudence.'])
n(1389, 'The action to claim rescission must be commenced within four years.', chk=['four years'])
n(1390, 'Voidable (annullable) contracts: those where one party is incapable of giving consent, and those where consent is vitiated by mistake, violence, intimidation, undue influence or fraud. They are binding unless annulled by a proper action, and may be ratified.')
n(1391, 'The action for annulment must be brought within four years, counted from the time the intimidation, violence or undue influence ceases; from discovery of the mistake or fraud; and, for incapacity, from the time the guardianship ceases.', chk=['four years'])
n(1392, 'Ratification extinguishes the action to annul a voidable contract.')
n(1397, 'The action for annulment may be instituted by all who are obliged principally or subsidiarily; but persons capable of contracting cannot allege the incapacity of those with whom they contracted, nor can those who exerted intimidation or violence or employed fraud base their action on these flaws.')
n(1398, 'An obligation having been annulled, the contracting parties must restore to each other the things which were the object of the contract, with their fruits, and the price with interest.')
n(1399, 'When the defect of the contract consists in the incapacity of one of the parties, the incapacitated person is not obliged to make any restitution except insofar as he has been benefited by the thing or price received.')
n(1403, 'Unenforceable contracts: those entered into in the name of another without authority or beyond one’s powers; those that do not comply with the Statute of Frauds; and those where both parties are incapable of giving consent. The Statute of Frauds requires a writing for: agreements not to be performed within a year; special promises to answer for another’s debt; agreements in consideration of marriage, other than a mutual promise to marry; sales of goods at a price not less than five hundred pesos (unless partly accepted or paid); leases for more than one year and sales of real property or an interest therein; and representations as to another’s credit.',
  t=['The Statute of Frauds applies only to executory contracts, not to those partly or fully performed (Carbonnel v. Poncio, 1958).', 'It is a rule of evidence that can be waived by failure to object or by accepting benefits (Art. 1405).'], chk=['five hundred pesos', 'one year'])
n(1405, 'Contracts infringing the Statute of Frauds are ratified by the failure to object to the presentation of oral evidence to prove them, or by the acceptance of benefits under them.')
n(1407, 'In a contract where both parties are incapable of giving consent, express or implied ratification by the parent or guardian of one of them gives it the effect of a voidable contract; ratification by both makes it valid from the inception.')
n(1410, 'The action or defense for the declaration of the inexistence of a contract does not prescribe.')
n(1411, 'When the nullity proceeds from the illegality of the cause or object and the act constitutes a criminal offense, both parties being in pari delicto have no action against each other, and both are prosecuted; the things and price are confiscated in favor of the government.')
n(1412, 'If the act in which the unlawful or forbidden cause consists does not constitute a criminal offense: when both parties are at fault, neither may recover what he gave or demand performance; when only one is at fault, he may not recover what he gave, but the innocent party may demand the return of what he gave.', t=['In pari delicto does not apply when it would offend public policy, or to void contracts that are not illegal (e.g., absolutely simulated ones).'])
n(1414, 'When money is paid or property delivered for an illegal purpose, the contract may be repudiated by one of the parties before the purpose has been accomplished, or before any damage has been caused to a third person; the court may then allow him to recover what he has paid or delivered.')
n(1416, 'When the agreement is not illegal per se but is merely prohibited, and the prohibition by law is designed for the protection of the plaintiff, he may recover what he has paid or delivered, if public policy is thereby enhanced.')
n(1419, 'When the law sets a minimum wage, a laborer who agrees to accept a lower wage may still recover the deficiency.')
n(1422, 'A contract which is the direct result of a previous illegal contract is also void and inexistent.')


def main():
    d = json.load(open(f'{SITE}/codes/civil.json'))
    by = {p['i']: p for p in d['provisions']}
    errs = []
    for pid, (e, chk) in N.items():
        if pid not in by:
            errs.append('no provision ' + pid); continue
        text = ' '.join(x for x in by[pid]['p'] if isinstance(x, str)).lower()
        for c in chk:
            if c.lower() not in text:
                errs.append(f'{pid}: “{c}” not in the text')
    if errs:
        raise SystemExit('\n'.join(errs))
    cur = json.load(open(f'{SITE}/notes/civil.json'))
    added = 0
    for pid, (e, _) in N.items():
        if pid not in cur:
            added += 1
        cur[pid] = {**cur.get(pid, {}), **e}   # this script's latest text wins; it shares no keys with earlier notes
    json.dump(cur, open(f'{SITE}/notes/civil.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('Obligations and Contracts notes:', len(N), '| new:', added, '| civil total:', len(cur))


if __name__ == '__main__':
    main()
