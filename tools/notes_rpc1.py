"""Revised Penal Code, Book One: study notes in our own words, merged into data/notes/rpc.json.

Accuracy check: each note may name facts ('chk') that must appear in the provision's verbatim text
(or in an amending law shown under it). The script fails if any is missing, so a wrong number cannot be published.
"""
import json, re

SITE = '/home/claude/site/data'
N = {}


def n(a, x, k=None, t=None, w=None, d=None, i=None, chk=()):
    e = {'x': x}
    for key, v in (('k', k), ('t', t), ('w', w), ('d', d), ('i', i)):
        if v:
            e[key] = v
    N[f'article-{a}'] = (e, chk)


RA10951 = {'t': 'RA 10951 (2017)', 's': 'Adjusted the amounts of property and damage on which penalties depend, and the fines, in many RPC articles to reflect present values.', 'u': '#/code/ra10951'}
RA10592 = {'t': 'RA 10592 (2013)', 's': 'Amended Arts. 29, 94, 97, 98 and 99: credit for preventive imprisonment, and larger good-conduct and loyalty allowances, granted by the BuCor, BJMP and jail wardens.', 'u': '#/code/ra10592'}
RA9344 = {'t': 'RA 9344, the Juvenile Justice and Welfare Act, as amended by RA 10630', 's': 'A child 15 or under is exempt from criminal liability; one over 15 and under 18 is exempt unless he or she acted with discernment. Sentence of a child in conflict with the law is automatically suspended.', 'u': '#/code/ra9344'}
RA9346 = {'t': 'RA 9346 (2006)', 's': 'Prohibits the imposition of the death penalty. Reclusion perpetua (or life imprisonment) is imposed instead, without eligibility for parole.', 'u': '#/code/ra9346'}
RA10159 = {'t': 'RA 10159 (2012)', 's': 'Amended Art. 39: one day of subsidiary imprisonment for each amount equal to the highest minimum wage prevailing in the Philippines when the judgment is rendered.', 'u': '#/code/rpc'}

# ----------------------------------------------------------------- Title One: felonies
n(1, 'The Revised Penal Code took effect on January 1, 1932.', chk=['thirty-two'])
n(2, 'The Code applies throughout the Philippines and, by way of exception, to five kinds of acts committed abroad: on a Philippine ship or airship; forging or counterfeiting Philippine coins, currency notes or obligations; introducing those forged items into the country; offenses of public officers in the exercise of their functions; and crimes against national security and the law of nations (Title One of Book Two).',
  k=['Territoriality is the rule; Art. 2 lists the exceptions (extraterritoriality).', 'Generality (Art. 14, Civil Code): penal laws bind all who live or sojourn here, subject to treaty and international-law exemptions.'],
  t=['A Philippine vessel in foreign territorial waters: the Code applies only if the crime is not tried by the foreign state (the English rule on vessels is followed for foreign merchant ships in our waters).'])
n(5, 'When a court finds an act that the law does not punish but thinks should be punished, it must still acquit, and may report its reasons to the Chief Executive. When a strict application of the law would impose a clearly excessive penalty, the court must still impose it, and may recommend executive clemency.',
  t=['Courts cannot create crimes or lower penalties by themselves: nullum crimen, nulla poena sine lege.'])
n(7, 'Light felonies are punished only when consummated, except those committed against persons or property.', t=['Attempted or frustrated light felonies against persons or property (e.g., attempted light theft) are punishable.'])
n(9, 'Felonies are grave (punished by capital or afflictive penalties), less grave (correctional penalties), or light (arresto menor or a fine not exceeding P40,000 under RA 10951).',
  t=['The classification is by the penalty prescribed by law, not the penalty actually imposed.'], i=[RA10951])
n(10, 'Offenses under special laws are not governed by the Code, but the Code applies to them suppletorily unless the special law provides otherwise.',
  t=['Concepts like conspiracy can be applied to special-law offenses through this article.'],
  d=[{'n': 'Ladonga v. People', 'c': 'G.R. No. 141066, February 17, 2005', 'h': 'The RPC’s rules on conspiracy apply suppletorily to violations of BP 22, since the special law does not provide otherwise.', 'r': 'Suppletory application of the Code to special laws.'}])

# ----------------------------------------------------------------- circumstances and persons liable
n(15, 'Alternative circumstances may aggravate or mitigate depending on the nature and effects of the crime: relationship (spouse, ascendant, descendant, sibling or relative by affinity in the same degrees), intoxication, and the offender’s degree of instruction and education.',
  k=['Intoxication mitigates when not habitual and not intended to commit the felony; it aggravates when habitual or intentional.', 'Relationship usually aggravates crimes against persons and mitigates crimes against property (theft between certain relatives is exempt under Art. 332).'],
  t=['Low instruction mitigates only where it explains the act; it does not mitigate crimes everyone knows are wrong, like murder or rape.'])
n(16, 'For grave and less grave felonies, principals, accomplices and accessories are liable. For light felonies, only principals and accomplices.')
n(17, 'Principals are those who take a direct part in the act, those who directly force or induce others to commit it, and those who cooperate in its commission by another act without which it would not have been accomplished (indispensable cooperation).',
  k=['By direct participation.', 'By inducement: the inducement must be the determining cause of the crime, made before its commission.', 'By indispensable cooperation.'],
  t=['In a conspiracy, the act of one is the act of all: each conspirator is a principal regardless of his part.'])
n(18, 'Accomplices are those who, not being principals, cooperate in the execution of the offense by previous or simultaneous acts that are not indispensable.', t=['When in doubt whether one is a principal or an accomplice, the courts lean toward the milder form, accomplice.'])
n(19, 'Accessories know of the crime and, without having taken part as principals or accomplices, take part afterward by: (1) profiting or helping the offender profit from its effects; (2) concealing or destroying the body of the crime, its effects or instruments, to prevent discovery; or (3) harboring, concealing or helping the principal escape — if a public officer abusing his functions, or if the principal is guilty of treason, parricide, murder, an attempt on the life of the Chief Executive, or is known to be habitually guilty of another crime.',
  t=['Accessories are not liable for light felonies (Art. 16).', 'PD 1829 (obstruction of justice) and PD 1612 (fencing) punish some of the same acts as principal offenses.'])
n(20, 'Spouses, ascendants, descendants, legitimate, natural and adopted brothers and sisters, and relatives by affinity within the same degrees are exempt as accessories — except those who profit or help the offender profit from the crime.', t=['The exemption rests on family affection; it does not cover profiting (Art. 19, par. 1).'])

# ----------------------------------------------------------------- penalties: general
n(21, 'No felony shall be punished by a penalty not prescribed by law before its commission.', w='Fair warning: a person can be punished only under a law that existed when he acted.')
n(22, 'Penal laws apply retroactively when favorable to the accused, unless he is a habitual criminal, even if final sentence has been pronounced and the convict is serving it.',
  t=['A habitual delinquent (Art. 62, rule 5) does not get the benefit.', 'Example: RA 10951’s lower property thresholds were applied to persons already convicted.'])
n(23, 'A pardon by the offended party does not extinguish criminal liability, except as provided in Art. 344 for the private crimes; civil liability may be waived by the offended party.')
n(24, 'Not considered penalties: arrest and temporary detention of accused persons; commitment of a minor to a facility; suspension from office during an investigation; fines and corrective measures by superiors in administrative discipline; and deprivations of rights and reparations imposed by civil laws.')
n(25, 'The scale of principal penalties (capital, afflictive, correctional, light) and accessory penalties.', t=['Death is capital but cannot be imposed (RA 9346).'], i=[RA9346])
n(26, 'A fine is afflictive if it exceeds P1,200,000; correctional if from P40,000 to P1,200,000; and light if it does not exceed P40,000 (as amended by RA 10951).',
  t=['When the law imposes imprisonment and a fine, the fine’s class may differ from the imprisonment’s; prescription follows the higher.'], i=[RA10951])
n(27, 'Duration of penalties: reclusion perpetua, 20 years and 1 day to 40 years; reclusion temporal, 12 years and 1 day to 20 years; prision mayor and temporary disqualification, 6 years and 1 day to 12 years; prision correccional, suspension and destierro, 6 months and 1 day to 6 years; arresto mayor, 1 month and 1 day to 6 months; arresto menor, 1 to 30 days.',
  t=['Reclusion perpetua is indivisible even though RA 7659 gave it a duration (People v. Lucas, 1995).', 'Reclusion perpetua (an RPC penalty with accessory penalties) is not the same as life imprisonment (special laws).'],
  chk=['twenty years', 'twelve years', 'six years'])
n(28, 'If the offender is in prison, his term runs from the day the judgment becomes final. If not, from the day he is placed at the disposal of the authorities for its enforcement.')
n(29, 'Time spent in preventive imprisonment is credited against the sentence: in full if the detainee agrees in writing to abide by the same disciplinary rules as convicted prisoners, otherwise four-fifths of it. RA 10592 also provides for immediate release once the time served equals the maximum imposable penalty.',
  t=['Recidivists, those previously convicted twice or more, and those who failed to surrender for execution of sentence are not entitled to the credit (read the text as amended).'],
  i=[RA10592], d=[{'n': 'Inmates of the New Bilibid Prison v. De Lima', 'c': 'G.R. No. 212719, June 25, 2019', 'h': 'The IRR of RA 10592 could not make the law prospective only. Being penal and favorable to the accused, its time allowances apply retroactively.', 'r': 'Retroactivity of RA 10592.'}])
for a, x in ((30, 'Perpetual or temporary absolute disqualification deprives the offender of public office and employment, of the right to vote and be voted for, and of retirement pay for the office he held, for life or for the term of the sentence.'),
             (31, 'Perpetual or temporary special disqualification for public office, profession or calling deprives the offender of the office or exercise of the profession named in the sentence, and of the right to hold similar offices.'),
             (32, 'Perpetual or temporary special disqualification from suffrage deprives the offender of the right to vote or to be elected, for life or the duration of the sentence.'),
             (33, 'Suspension from public office, profession or calling, or from the right of suffrage, disqualifies the offender from exercising them during the term of the sentence.'),
             (34, 'Civil interdiction deprives the offender, while it lasts, of parental authority, guardianship, marital authority, the right to manage his property, and the right to dispose of it by act between living persons (he may still make a will).'),
             (35, 'A bond to keep the peace: the offender must give a guarantor answerable for any crime he might commit, or deposit an amount fixed by the court; failing to do so, he is detained (up to six months for a grave or less grave felony, thirty days for a light one).')):
    n(a, x)
n(36, 'A pardon does not restore the right to hold public office or the right of suffrage unless expressly restored by its terms, and does not exempt the culprit from paying civil indemnity.',
  d=[{'n': 'Risos-Vidal v. COMELEC', 'c': 'G.R. No. 206666, January 21, 2015', 'h': 'A pardon stating that the convict is “restored to his civil and political rights” expressly restored the right to hold office and vote, satisfying Arts. 36 and 41; a preamble expressing an intention not to seek office did not limit it.', 'r': 'What “expressly restored” requires.'}])
n(37, 'Costs include fees and indemnities in the course of judicial proceedings, whether fixed by law or not.')
n(38, 'When the offender’s property is not enough for all pecuniary liabilities, they are paid in this order: reparation of damage, indemnification for consequential damages, the fine, and the costs.', t=['The fine comes after the private offended party’s reparation and indemnity.'])
n(39, 'If the convict cannot pay the fine, he serves subsidiary imprisonment: one day for each amount equal to the highest minimum wage prevailing in the Philippines when judgment is rendered (RA 10159). It may not exceed one-third of the principal penalty, nor one year when the fine is for a grave or less grave felony, nor fifteen days for a light one.',
  t=['No subsidiary imprisonment when the principal penalty is higher than prision correccional.', 'It is imposed only for the fine, never for civil liability; and the judgment must state it.'], i=[RA10159])
for a, x in ((40, 'Accessory penalties of death (when not executed by pardon): perpetual absolute disqualification and civil interdiction for 30 years, unless expressly remitted.'),
             (41, 'Reclusion perpetua and reclusion temporal carry civil interdiction for life or the term of the sentence, and perpetual absolute disqualification even if pardoned as to the principal penalty, unless expressly remitted by the pardon.'),
             (42, 'Prision mayor carries temporary absolute disqualification and perpetual special disqualification from suffrage, unless expressly remitted by pardon.'),
             (43, 'Prision correccional carries suspension from public office, profession or calling, and perpetual special disqualification from suffrage if the sentence exceeds 18 months, unless expressly remitted.'),
             (44, 'Arresto carries suspension of the right to hold office and the right of suffrage during the term of the sentence.'),
             (45, 'Every penalty carries forfeiture of the proceeds of the crime and the instruments or tools used, unless they belong to a third person not liable for the offense; articles not subject to lawful commerce are destroyed.')):
    n(a, x)
n(46, 'The penalty the law prescribes for a felony is understood as the penalty for the principals in a consummated felony; the other articles graduate it for other stages and participants.')
n(47, 'Lays down when the death penalty could be imposed. It is now inoperative: RA 9346 prohibits imposing death.', i=[RA9346])
n(48, '', chk=())
del N['article-48']   # already annotated elsewhere
n(49, 'When the felony committed differs from the one intended (error in personae, for example), the offender gets the penalty for the lesser of the two, in its maximum period.', t=['It applies only when the two felonies carry different penalties; if the same (e.g., intending to kill A, killing B), Art. 4 makes him liable for the crime committed as if intended.'])
n(50, 'Principals of a frustrated felony: the penalty next lower in degree to that prescribed for the consummated felony.')
n(51, 'Principals of an attempted felony: the penalty two degrees lower.')
n(52, 'Accomplices in a consummated felony: one degree lower.')
n(53, 'Accessories in a consummated felony: two degrees lower.')
n(54, 'Accomplices in a frustrated felony: two degrees lower.')
n(55, 'Accessories in a frustrated felony: three degrees lower.')
n(56, 'Accomplices in an attempted felony: three degrees lower.')
n(57, 'Accessories in an attempted felony: four degrees lower.', k=['Memory grid: start at 0 for consummated principal; add 1 for each step to frustrated and to attempted, and 1 for accomplice, 2 for accessory.'])
n(58, 'A public officer who acts as an accessory by abusing his functions (Art. 19, par. 3) also suffers absolute perpetual disqualification if the principal committed a grave felony, and absolute temporary disqualification if a less grave felony.')
n(59, 'Impossible crimes are punished with arresto mayor or a fine, the court considering the offender’s social danger and degree of criminality.', t=['Impossible crime (Art. 4, par. 2) exists only when the act would be an offense against persons or property.'], i=[RA10951])
n(60, 'Arts. 50 to 57 do not apply when the law expressly penalizes the frustrated or attempted stage, or the accomplice or accessory, in a special way.')
n(61, 'Rules for graduating penalties: how to find the penalty “next lower in degree” for single indivisible penalties, for two indivisible penalties, for one indivisible and divisible penalties, and for penalties made of several periods, using the scales in Art. 71.')
n(62, 'Effect of modifying circumstances: aggravating circumstances that are themselves crimes, or inherent in the crime, or used by law in defining it, are not considered; personal circumstances affect only those to whom they attach; and a habitual delinquent gets an additional penalty.',
  k=['Habitual delinquent: within ten years from release or last conviction of serious or less serious physical injuries, robbery, theft, estafa or falsification, found guilty of any of them a third time or oftener.'],
  t=['Habitual delinquency differs from recidivism (Art. 14, par. 9): it needs three convictions of specified crimes within ten-year spans and adds a penalty; recidivism is a generic aggravating circumstance.'])
n(63, 'Indivisible penalties: a single indivisible penalty is applied regardless of circumstances. When the law prescribes two indivisible penalties, one aggravating circumstance calls for the greater; one or more mitigating and no aggravating, the lesser; both, they offset by number and weight.')
n(64, 'Divisible penalties of three periods: no circumstance — medium period; only a mitigating — minimum; only an aggravating — maximum; both — offset; two or more mitigating and no aggravating — the next lower penalty, in the period the court fixes. No aggravating circumstances, however many, can raise the penalty beyond the maximum period.',
  t=['Privileged mitigating circumstances (e.g., Art. 68, Art. 69) lower the penalty by degrees and cannot be offset by aggravating circumstances.'])
n(65, 'When a penalty is not made of three periods, divide its duration into three equal portions, each forming a period.')
n(66, 'In fixing a fine, the court may go anywhere within the limits set by law, considering the mitigating and aggravating circumstances and, more particularly, the wealth or means of the culprit.')
n(67, 'When an accident (Art. 12, par. 4) is not complete because the act was not lawful or due care was lacking, the penalty is arresto mayor maximum to prision correccional minimum for a grave felony, and arresto mayor minimum and medium for a less grave felony.')
n(68, 'A minor offender over 15 and under 18 who acted with discernment gets the penalty next lower in degree than that prescribed by law (a privileged mitigating circumstance). Children 15 and below are exempt under RA 9344.',
  t=['Read with RA 9344: the sentence is automatically suspended, and the child is placed in a rehabilitation program.'], i=[RA9344],
  d=[{'n': 'People v. Sarcia', 'c': 'G.R. No. 169641, September 10, 2009', 'h': 'An accused who was a minor when he committed the crime is entitled to the benefits of RA 9344, including the privileged mitigating circumstance and suspension of sentence, even if he is already an adult at the time of conviction.', 'r': 'The age that counts is the age at commission.'}])
n(69, 'When an act is not wholly excusable because some conditions of a justifying or exempting circumstance are lacking, the penalty is one or two degrees lower, provided the majority of the conditions are present (a privileged mitigating circumstance).',
  t=['If only unlawful aggression is present in self-defense, it is an ordinary mitigating circumstance (Art. 13, par. 1), not this privileged one.'])
n(70, 'When a convict has several penalties that cannot be served at the same time, he serves them successively in order of severity. But the total time served may not exceed three times the most severe penalty imposed (the three-fold rule), and never more than 40 years.',
  t=['The three-fold rule limits service, not the penalties the court imposes; the court imposes all penalties in full.'], chk=['forty years'])
n(71, 'The graduated scales used to find penalties higher or lower in degree.', k=['Scale 1: death, reclusion perpetua, reclusion temporal, prision mayor, prision correccional, arresto mayor, destierro, arresto menor, public censure, fine.'])
n(72, 'Civil liabilities of a convicted person are satisfied in the order of the dates of the final judgments.')
n(73, 'When a principal penalty carries accessory penalties by law, they are deemed imposed even if the judgment does not mention them.')
n(74, 'When the law prescribes a penalty higher than another given penalty without naming it, and that penalty would be death, the same penalty and the accessory penalties of Art. 40 are imposed, but death is not.')
n(75, 'To raise or lower a fine by degrees, increase or reduce its maximum by one-fourth for each degree, without changing the minimum.')
n(76, 'The table of the minimum, medium and maximum periods of each divisible penalty.')
n(77, 'When a penalty is composed of three distinct penalties, each forms a period: the lightest is the minimum, the next the medium, the most severe the maximum.')
n(78, 'No penalty may be executed except by virtue of a final judgment, and only in the form prescribed by law.')
n(79, 'If the convict becomes insane or imbecile after final sentence, execution of the personal penalty is suspended (but not the pecuniary penalty); he serves it upon recovering his reason.')
n(80, 'The Code’s old rule on suspended sentence of minors, now superseded by RA 9344.', i=[RA9344])
for a in (81, 82, 83, 84, 85):
    n(a, 'Provisions on the execution of the death penalty. Inoperative: death may not be imposed (RA 9346).', i=[RA9346])
n(86, 'Reclusion perpetua, reclusion temporal, prision mayor, prision correccional and arresto mayor are served in the penal institutions designated by law.')
n(87, 'Destierro: the convict may not enter the place or places designated in the sentence, nor within the radius it specifies, which must be not more than 250 and not less than 25 kilometers from the place designated.', chk=['250', '25'])
n(88, 'Arresto menor is served in the municipal jail or in the offender’s house under the surveillance of an officer, when the court so provides considering his health and other reasons.')

# ----------------------------------------------------------------- extinction of criminal liability
n(89, 'Criminal liability is totally extinguished by: (1) death of the convict — as to personal penalties, and as to pecuniary penalties only if death occurs before final judgment; (2) service of the sentence; (3) amnesty; (4) absolute pardon; (5) prescription of the crime; (6) prescription of the penalty; and (7) marriage of the offended woman, as provided in Art. 344.',
  k=['Amnesty looks backward and wipes out the offense; pardon looks forward and relieves the penalty.', 'Amnesty needs the concurrence of Congress; pardon does not.'],
  t=['Death pending appeal extinguishes criminal liability and the civil liability based solely on the crime; civil liability from other sources (law, contract, quasi-contract, quasi-delict) survives and may be pursued in a separate action.'],
  d=[{'n': 'People v. Bayotas', 'c': 'G.R. No. 102007, September 2, 1994', 'h': 'Death of the accused pending appeal extinguishes his criminal liability and the civil liability ex delicto. Claims for civil liability based on other sources survive and may be filed against his estate.', 'r': 'The leading rule on death of the accused.'}])
n(90, 'Prescription of crimes: those punishable by death, reclusion perpetua or reclusion temporal prescribe in 20 years; other afflictive penalties, 15 years; correctional penalties, 10 years (arresto mayor, 5); libel and similar offenses, 1 year; oral defamation and slander by deed, 6 months; light offenses, 2 months. A compound penalty follows its highest penalty.',
  t=['Offenses under special laws prescribe under Act No. 3326, not this article.', 'Cyber libel prescribes, like libel, in one year counted from discovery (Causing v. People, G.R. No. 258524: Third Division, October 11, 2023, affirmed on reconsideration by the Court en banc, 8–7, in April 2026), abandoning the unsigned 2018 resolution in Tolentino v. People.'],
  i=[{'t': 'Act No. 3326 (1926), as amended', 's': 'Prescriptive periods for offenses punished by special laws and municipal ordinances, and when they start to run.', 'u': '#/code/act3326'}],
  chk=['twenty years', 'fifteen years', 'ten years', 'two months'])
n(91, 'The period of prescription starts from the day the crime is discovered by the offended party, the authorities or their agents. It is interrupted by the filing of the complaint or information, and runs again if the proceedings end without conviction or acquittal or are unjustifiably stopped for reasons not imputable to the accused. It does not run while the offender is absent from the Philippines.',
  t=['A complaint filed with the prosecutor for preliminary investigation interrupts prescription; it need not be filed in court.'])
n(92, 'Penalties imposed by final sentence prescribe: death and reclusion perpetua in 20 years; other afflictive penalties in 15 years; correctional penalties in 10 years (arresto mayor, 5); light penalties in 1 year.', chk=['twenty years', 'fifteen years', 'ten years', 'one year'])
n(93, 'Prescription of a penalty starts when the convict evades service of sentence. It is interrupted if he gives himself up, is captured, goes to a foreign country with which the Philippines has no extradition treaty, or commits another crime before the period expires.', t=['There is no prescription of a penalty unless the convict evaded service by escaping; a convict never arrested after final judgment is not “evading”.'])
n(94, 'Criminal liability is partially extinguished by conditional pardon, commutation of sentence, and allowances for good conduct (and, under RA 10592, preventive imprisonment and allowances while under preventive imprisonment).', i=[RA10592])
n(95, 'A conditional pardonee must comply strictly with the conditions. Violation exposes him to prosecution under Art. 159 or to recommitment by the President.',
  d=[{'n': 'Torres v. Gonzales', 'c': 'G.R. No. 76872, July 23, 1987', 'h': 'The President may order the rearrest and recommitment of a conditional pardonee who violates the pardon’s conditions; a judicial conviction for a new offense is not required for that purely executive determination.', 'r': 'Two remedies for breach of a conditional pardon.'}])
n(96, 'Commutation changes the penalty to a lighter one; the convict serves the commuted penalty.')
n(97, 'Good conduct time allowance (GCTA) under RA 10592: a prisoner of good behavior, whether convicted or under preventive imprisonment, earns deductions for each month: 20 days in the first two years; 23 days in the third to fifth years; 25 days in the sixth to tenth years; 30 days from the eleventh year; plus up to 15 days for each month spent in teaching, studying or mentoring.',
  t=['RA 10592 excludes recidivists, habitual delinquents, escapees and persons charged with heinous crimes from the allowance during preventive imprisonment (Art. 29 as amended). The scope of the exclusion was the subject of the 2019 GCTA controversy.'], i=[RA10592])
n(98, 'Special time allowance for loyalty: a prisoner who escapes during a disaster or calamity and gives himself up within 48 hours after it ends earns a deduction of one-fifth of his sentence; under RA 10592, one who chooses to stay in his place of confinement earns two-fifths.', i=[RA10592])
n(99, 'Time allowances are granted by the Director of the Bureau of Corrections, the Chief of the BJMP, or the warden of a provincial, district, municipal or city jail (RA 10592). Once granted, they cannot be revoked.', i=[RA10592])

# ----------------------------------------------------------------- civil liability
n(100, 'Every person criminally liable for a felony is also civilly liable.', t=['Acquittal on reasonable doubt does not bar civil liability if the act or omission is proved by preponderance of evidence; acquittal because the act did not exist, or the accused did not commit it, does.'])
n(101, 'Civil liability survives some exemptions: the persons in charge of an insane or minor offender exempt under Art. 12 answer for the damage, unless free of fault; and in a state of necessity (Art. 11, par. 4), those who benefited answer in proportion to the benefit.', t=['There is no civil liability in the other justifying circumstances (self-defense, defense of relatives or strangers, fulfillment of duty, obedience to an order).'])
n(102, 'Innkeepers and similar keepers are subsidiarily liable for crimes committed in their establishments by their employees, and for theft of guests’ goods within their houses, if the guest gave notice of the deposit and followed their directions — but not for robbery with violence or intimidation unless committed by their employees.')
n(103, 'Employers engaged in any kind of industry are subsidiarily liable for felonies of their servants, pupils, workmen, apprentices or employees committed in the discharge of their duties.',
  k=['Requisites: the employer is engaged in an industry; the employee committed a felony in the discharge of his duties; the employee was convicted and is insolvent (the writ of execution against him was returned unsatisfied).'],
  t=['The subsidiary liability is enforced in the same criminal case by motion, after the employee’s insolvency is shown; the employer is bound by the judgment of conviction.'])
n(104, 'Civil liability includes restitution, reparation of the damage caused, and indemnification for consequential damages.')
n(105, 'Restitution: the very thing taken must be returned, even if found in the possession of a third person who acquired it lawfully (who may claim against the person liable), unless he acquired it in a manner and under the requirements that make it irrecoverable by law.')
n(106, 'Reparation: the court fixes the amount of damage, considering the price of the thing and its special sentimental value to the injured party.')
n(107, 'Indemnification for consequential damages covers the damages caused to the injured party, his family and third persons by the crime.')
n(108, 'The obligation to make restitution, reparation and indemnification passes to the heirs of the person liable; the right to demand them passes to the heirs of the injured party.')
n(109, 'When two or more are civilly liable for a felony, the court fixes the share of each.')
n(110, 'Principals, accomplices and accessories are each severally liable among themselves for their shares, and subsidiarily liable for the shares of the others: first the principals, then the accomplices, then the accessories.')
n(111, 'A person who gratuitously shared in the proceeds of a felony must make restitution up to the amount of his share.')
n(112, 'Civil liability is extinguished in the same way as other obligations under the Civil Code.')
n(113, 'A convict remains bound to satisfy his civil liability even after serving his sentence or being pardoned, and despite the extinction of his criminal liability by amnesty, pardon or service, unless the law provides otherwise.')

n('88-a', 'Community service (RA 11362, 2019): the court may let a convict serve arresto menor or arresto mayor by rendering community service in the place where the crime was committed, under a probation officer’s supervision, with rehabilitative counseling. Violation means re-arrest and service of the full term; the privilege may be availed of only once.',
  t=['Available only for arresto menor and arresto mayor, and only once.'], chk=['only once'])
n(125, 'A public officer who lawfully detains a person (for example, after a valid warrantless arrest) must deliver him to the proper judicial authorities within 12 hours for offenses punishable by light penalties, 18 hours for correctional penalties, and 36 hours for afflictive or capital penalties. The detainee must be told the cause of detention and may confer with counsel at any time.',
  k=['“Deliver to the judicial authorities” means filing the complaint or information in court, not physically bringing the person before a judge.'],
  t=['If the arrest itself was illegal, the crime is arbitrary detention (Art. 124), not delay in delivery.', 'A detainee who asks for preliminary investigation must waive Art. 125 in writing, with counsel (Rule 112, Sec. 7).'],
  chk=['twelve (12) hours', 'eighteen (18) hours', 'thirty-six (36) hours'])
n('134-a', 'Coup d’état (added by RA 6968, 1990): a swift attack, with violence, intimidation, threat, strategy or stealth, against duly constituted authorities or vital facilities (military camps, communications networks, public utilities), carried out by persons belonging to the military or police or holding public office or employment, with or without civilian support, to seize or diminish state power.',
  k=['Elements: (1) swift attack with violence, intimidation, threat, strategy or stealth; (2) against duly constituted authorities, military camps, communications, utilities or similar facilities; (3) by members of the military or police or public officers or employees; (4) to seize or diminish state power.'],
  t=['Rebellion needs a public uprising and taking up arms; coup d’état needs neither, and is committed by insiders through a swift attack.'], chk=['swift attack'])
n(135, 'Penalties for rebellion, insurrection and coup d’état (as amended by RA 6968): leaders of a rebellion or insurrection — reclusion perpetua; mere participants — reclusion temporal; leaders of a coup — reclusion perpetua; participants in government service — reclusion temporal maximum; participants not in government service, including financiers and supporters — prision mayor maximum.',
  t=['Rebellion absorbs common crimes committed in furtherance of it (People v. Hernandez, 1956); they cannot be complexed with it.'], chk=['reclusion perpetua'])


def main():
    d = json.load(open(f'{SITE}/codes/rpc.json'))
    amend = {}
    for code in ('ra10951', 'ra10592', 'ra7659'):
        try:
            for p in json.load(open(f'{SITE}/codes/{code}.json'))['provisions']:
                for x in p['p']:
                    if isinstance(x, str):
                        for m in re.finditer(r'Art(?:icle|\.)\s*(\d+)', x):
                            amend.setdefault(m.group(1), []).append(x)
        except FileNotFoundError:
            pass
    by = {p['i']: p for p in d['provisions']}
    errs = []
    for pid, (e, chk) in N.items():
        if pid not in by:
            errs.append('no such provision ' + pid)
            continue
        p = by[pid]
        text = ' '.join(x for x in p['p'] if isinstance(x, str))
        text += ' ' + ' '.join(x for a in p.get('a', []) for x in a['p'] if isinstance(x, str))
        text += ' ' + ' '.join(amend.get(p.get('n'), []))
        for c in chk:
            if c.lower() not in text.lower():
                errs.append(f'{pid}: “{c}” not in the text')
    if errs:
        raise SystemExit('\n'.join(errs))
    cur = json.load(open(f'{SITE}/notes/rpc.json'))
    for pid, (e, _) in N.items():
        cur[pid] = {**cur.get(pid, {}), **e}
    json.dump(cur, open(f'{SITE}/notes/rpc.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('RPC Book One notes:', len(N), '| rpc notes total:', len(cur))


if __name__ == '__main__':
    main()
