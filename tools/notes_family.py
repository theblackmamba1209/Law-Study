"""Family Code (EO 209): study notes in our own words, merged into data/notes/family.json, with a numeric check against the text."""
import json

SITE = '/home/claude/site/data'
N = {}


def n(a, x, t=None, k=None, d=None, chk=()):
    e = {'x': x}
    if t: e['t'] = t
    if k: e['k'] = k
    if d: e['d'] = [{'n': a1, 'c': b, 'h': c, 'r': r} for a1, b, c, r in d]
    N[f'article-{a}'] = (e, chk)


n(5, 'Any male or female of the age of eighteen years or upwards not under any of the impediments in Arts. 37 and 38 may contract marriage.', chk=['eighteen years'])
n(6, 'No prescribed form or religious rite is required for the solemnization of marriage, but the parties must personally appear before the solemnizing officer and declare, in the presence of at least two witnesses of legal age, that they take each other as husband and wife.', chk=['two witnesses'])
n(7, 'Who may solemnize marriage: incumbent members of the judiciary within their jurisdiction; priests, rabbis, imams or ministers of registered churches or sects, under the conditions stated; ship captains and airplane chiefs in articulo mortis; military commanders in the absence of a chaplain, in articulo mortis; and consuls-general, consuls or vice-consuls abroad. (Mayors may also solemnize under the Local Government Code.)')
n(8, 'Marriage shall be solemnized publicly in the chambers of the judge or in open court, in the church, chapel or temple, or in the office of the consul, except in articulo mortis, in remote places, or when both parties request in a sworn statement a different place.', t=['A wrong venue is an irregularity: it does not void the marriage (Art. 4).'])
n(9, 'A marriage license is issued by the local civil registrar of the city or municipality where either contracting party habitually resides.')
n(14, 'If either or both parties are between eighteen and twenty-one years old, they must present the written consent of their father, mother, surviving parent or guardian, or persons having legal charge of them, in that order.', t=['Lack of parental consent makes the marriage voidable (Art. 45(1)), not void.'], chk=['eighteen', 'twenty-one'])
n(15, 'Parties between twenty-one and twenty-five years old must ask their parents or guardian for advice; if advice is not obtained or is unfavorable, the license is not issued until three months after the completion of publication.', t=['Absence of parental advice does not affect validity; it only delays the license.'], chk=['twenty-one', 'twenty-five', 'three months'])
n(17, 'The local civil registrar posts a notice of the application for a marriage license for ten consecutive days in a conspicuous place.', chk=['ten consecutive days'])
n(20, 'The marriage license is valid in any part of the Philippines for one hundred twenty days from the date of issue, and is automatically cancelled at the end of that period if unused.', chk=['one hundred twenty days'])
n(21, 'Foreign nationals must submit a certificate of legal capacity to contract marriage issued by their diplomatic or consular officials before a license is obtained; stateless persons and refugees submit an affidavit instead.')
n(34, 'No license is required for the marriage of a man and a woman who have lived together as husband and wife for at least five years and without any legal impediment to marry each other; they state these facts in an affidavit.',
  t=['The five years must be continuous and immediately before the marriage, and the parties must have had no legal impediment throughout those five years (Niñal v. Bayadog, 2000).'], chk=['five years'])
n(39, 'The action or defense for the declaration of absolute nullity of a marriage does not prescribe (as amended by RA 8533).', t=['Only the spouses may file the petition (A.M. No. 02-11-10-SC), for marriages under the Family Code.'])
n(40, 'The absolute nullity of a previous marriage may be invoked for purposes of remarriage only on the basis of a final judgment declaring that previous marriage void.', t=['Without a judicial declaration, a second marriage is bigamous even if the first was void (Mercado v. Tan, 2000).'])
n(41, 'A marriage contracted by a person during the subsistence of a previous marriage is void, unless before the second marriage the prior spouse had been absent for four consecutive years and the spouse present had a well-founded belief that the absent spouse was already dead; two years suffice where there is danger of death under Art. 391 of the Civil Code. A judicial declaration of presumptive death is required for remarriage.',
  t=['“Well-founded belief” requires diligent and reasonable efforts to locate the absent spouse; passive inquiries are not enough (Republic v. Cantor, 2013).'], chk=['four consecutive years', 'two years'])
n(42, 'The subsequent marriage under Art. 41 is automatically terminated by the recording of the affidavit of reappearance of the absent spouse, unless there is a judgment annulling the previous marriage or declaring it void.')
n(43, 'Effects of termination of the subsequent marriage: children conceived before termination are legitimate; the absolute community or conjugal partnership is dissolved and liquidated, and the spouse in bad faith forfeits his or her share of the net profits; donations by reason of marriage to the spouse in bad faith are revoked by operation of law; the innocent spouse may revoke the designation of the guilty spouse as insurance beneficiary; and the spouse in bad faith is disqualified to inherit from the innocent spouse.')
n(46, 'Fraud for annulment refers only to: non-disclosure of a previous conviction of a crime involving moral turpitude; concealment by the wife that at the time of marriage she was pregnant by another man; concealment of a sexually transmissible disease; and concealment of drug addiction, habitual alcoholism, homosexuality or lesbianism. No other misrepresentation as to character, health, rank, fortune or chastity is fraud.', t=['The list is exclusive.'])
n(47, 'Who may sue and when: for lack of parental consent, the party whose parent did not consent within five years after reaching twenty-one, or the parent before that; for insanity, the sane spouse without knowledge, or the insane spouse during a lucid interval, at any time before the death of either; for fraud, the injured party within five years after discovery; for force, intimidation or undue influence, the injured party within five years from the time they disappeared or ceased; for impotence and sexually transmissible disease, the injured party within five years after the marriage.', chk=['five years'])
n(48, 'In all cases of annulment or declaration of absolute nullity, the court orders the prosecuting attorney or fiscal to appear for the State to take steps to prevent collusion and to see that evidence is not fabricated or suppressed. No judgment may be based on a stipulation of facts or confession of judgment.')
n(50, 'The effects of Art. 43(2) to (5) apply to marriages declared void or annulled; the final judgment provides for the liquidation, partition and distribution of the properties, custody and support of the children, and delivery of the presumptive legitimes, unless already adjudicated.')
n(52, 'The judgment of annulment or of absolute nullity, the partition and distribution of the properties, and the delivery of the children’s presumptive legitimes must be recorded in the civil registry and registries of property; otherwise they do not affect third persons.')
n(53, 'Either former spouse may marry again after complying with Art. 52; otherwise the subsequent marriage is null and void.')
n(54, 'Children conceived or born before the judgment of annulment or of absolute nullity under Art. 36 has become final and executory are legitimate, as are children of a subsequent marriage under Art. 53.', t=['Children of void marriages are generally illegitimate, with these two exceptions (Art. 36 and Art. 53).'])
n(55, 'Grounds for legal separation: repeated physical violence or grossly abusive conduct; physical violence or moral pressure to compel a change of religious or political affiliation; attempt to corrupt or induce the petitioner or a child into prostitution; final judgment sentencing the respondent to more than six years’ imprisonment; drug addiction or habitual alcoholism; lesbianism or homosexuality; contracting a subsequent bigamous marriage; sexual infidelity or perversion; attempt against the life of the petitioner; and abandonment without justifiable cause for more than one year.',
  t=['Legal separation does not dissolve the marriage bond: the spouses cannot remarry.'], chk=['six years', 'one year'])
n(56, 'The petition for legal separation shall be denied on any of these grounds: condonation; consent; connivance; recrimination (both parties have given ground); collusion; and prescription.', k=['Mnemonic: 4 Cs and 2 Ps … condonation, consent, connivance, collusion, recrimination (mutual guilt), prescription.'])
n(57, 'An action for legal separation must be filed within five years from the time of the occurrence of the cause.', chk=['five years'])
n(58, 'An action for legal separation shall in no case be tried before six months have elapsed since the filing of the petition (cooling-off period).', t=['The cooling-off period does not apply when the ground involves violence under RA 9262; the court proceeds to hear the case (and may issue protection orders) at once.'], chk=['six months'])
n(63, 'Effects of the decree of legal separation: the spouses may live separately, but the marriage bond is not severed; the community or partnership is dissolved and liquidated, the offending spouse having no right to any share of the net profits; custody of minor children goes to the innocent spouse (subject to Art. 213); and the offending spouse is disqualified to inherit from the innocent spouse by intestate succession.')
n(66, 'Reconciliation terminates the legal separation proceedings if still pending, and sets aside the decree if already rendered, but the separation of property and forfeiture of the guilty spouse’s share stay unless the spouses agree to revive their former property regime.')
n(68, 'The husband and wife are obliged to live together, observe mutual love, respect and fidelity, and render mutual help and support.')
n(73, 'Either spouse may exercise any legitimate profession, occupation, business or activity without the consent of the other; the other spouse may object only on valid, serious and moral grounds.')
n(74, 'The property relations between husband and wife are governed in this order: by marriage settlements executed before the marriage; by the provisions of the Family Code; and by the local custom.')
n(75, 'The future spouses may agree in the marriage settlement on absolute or relative community, conjugal partnership of gains, complete separation of property, or any other regime. Absent a settlement or a valid one, the system of absolute community of property governs.', t=['For marriages before August 3, 1988 without a settlement, the default was the conjugal partnership of gains.'])
n(87, 'Every donation or grant of gratuitous advantage, direct or indirect, between spouses during the marriage is void, except moderate gifts on the occasion of any family rejoicing. The prohibition also applies to persons living together as husband and wife without a valid marriage.')
n(88, 'The absolute community of property commences at the precise moment the marriage is celebrated; any stipulation to the contrary is void.')
n(91, 'Unless otherwise provided, the community property consists of all the property owned by the spouses at the time of the marriage or acquired thereafter.')
n(92, 'Excluded from the community: property acquired during the marriage by gratuitous title (and its fruits) unless the donor or testator provides otherwise; property for personal and exclusive use, except jewelry; and property acquired before the marriage by a spouse who has legitimate descendants by a former marriage (and its fruits and income).')
n(96, 'The administration and enjoyment of the community property belong to both spouses jointly; in case of disagreement, the husband’s decision prevails, subject to recourse to the court by the wife within five years. Neither may dispose of or encumber community property without the other’s written consent or court authority; a disposition without it is void, but is treated as a continuing offer that the other spouse may accept before it is withdrawn.', chk=['five years'])
n(105, 'In the conjugal partnership of gains, the spouses place in a common fund the proceeds, products, fruits and income from their separate properties and those acquired by either or both through their efforts or by chance; on dissolution, the net gains are divided equally, unless otherwise agreed.')
n(116, 'All property acquired during the marriage, whether in the name of one or both spouses, is presumed conjugal unless the contrary is proved.')
n(124, 'The administration and enjoyment of the conjugal partnership belong to both spouses jointly; dispositions or encumbrances without the other’s written consent or court authority are void, but treated as a continuing offer.', t=['Same rule as Art. 96 for the absolute community.'])
n(134, 'In the absence of an express declaration in the marriage settlements, the separation of property between spouses during the marriage shall not take place except by judicial order.')
n(148, 'In cohabitation not covered by Art. 147 (e.g., where a party is married to another), only properties acquired by both through their actual joint contribution of money, property or industry are owned in common in proportion to their contributions; contributions are presumed equal absent proof.',
  t=['Unlike Art. 147, efforts in the care of the home are not counted as contribution, and there is no presumption of joint acquisition.'])
n(149, 'The family, being the foundation of the nation, is a basic social institution which public policy cherishes and protects.')
n(151, 'No suit between members of the same family shall prosper unless it appears from the verified complaint that earnest efforts toward a compromise have been made but failed.', t=['It covers only spouses, ascendants and descendants, and brothers and sisters; not in-laws or cousins (Gayon v. Gayon, 1970).'])
n(152, 'The family home is constituted jointly by the husband and wife or by an unmarried head of a family; it is the dwelling house where they and their family reside and the land on which it is situated.')
n(153, 'The family home is deemed constituted from the time it is occupied as a family residence; from then on it is exempt from execution, forced sale or attachment, except as the Code provides, as long as any of its beneficiaries actually resides in it.')
n(155, 'The family home is exempt from execution except: for nonpayment of taxes; for debts incurred before its constitution; for debts secured by mortgages on the premises before or after constitution; and for debts due to laborers, mechanics, architects, builders and suppliers who rendered service or furnished material for its construction.')
n(163, 'The filiation of children may be by nature or by adoption; natural filiation may be legitimate or illegitimate.')
n(164, 'Children conceived or born during the marriage of the parents are legitimate. Children conceived by artificial insemination of the wife with the sperm of the husband or of a donor, both spouses having authorized it in a written instrument signed before the child’s birth, are also legitimate.')
n(166, 'Legitimacy may be impugned only on these grounds: physical impossibility of sexual intercourse with the wife within the first 120 days of the 300 days before the birth (impotence, living separately, or serious illness); biological or other scientific reasons; or, for artificial insemination, the written authorization was obtained through mistake, fraud, violence, intimidation or undue influence.', chk=['120', '300'])
n(167, 'The child is considered legitimate although the mother may have declared against its legitimacy or may have been sentenced as an adulteress.')
n(170, 'The action to impugn legitimacy must be brought within one year from knowledge of the birth or its recording, if the husband or his heirs reside in the city or municipality of birth; two years if they reside elsewhere in the Philippines; three years if abroad.', t=['Only the husband (or, in limited cases, his heirs) may impugn; legitimacy cannot be attacked collaterally (Liyao v. Tanhoti-Liyao, 2002).'], chk=['one year', 'two years', 'three years'])
n(172, 'The filiation of legitimate children is established by the record of birth in the civil register or a final judgment, or by an admission of filiation in a public document or a private handwritten instrument signed by the parent. Absent these, by open and continuous possession of the status of a legitimate child, or by any other means allowed by the Rules of Court and special laws.')
n(173, 'The action to claim legitimacy may be brought by the child during his or her lifetime, and transmitted to the heirs if the child dies during minority or in a state of insanity, within five years.', chk=['five years'])
n(175, 'Illegitimate children may establish their filiation in the same way and on the same evidence as legitimate children. The action must be brought within the periods in Art. 173, except when based on open and continuous possession or other evidence under Art. 172(2), in which case it must be brought during the lifetime of the alleged parent.')
n(176, 'Illegitimate children use the surname and are under the parental authority of their mother, and are entitled to support. Under RA 9255 they may use the father’s surname if he has expressly recognized them. The legitime of each illegitimate child is one-half of that of a legitimate child.',
  t=['Use of the father’s surname is permissive (“may”), not mandatory (Grande v. Antonio, 2014). Parental authority stays with the mother even if the father recognizes the child.'])
n(177, 'Children conceived and born outside of wedlock of parents who, at the time of conception, were not disqualified by any impediment to marry each other, or were disqualified only because either or both were below eighteen years of age, may be legitimated (as amended by RA 9858).', chk=['below eighteen (18) years'])
n(178, 'Legitimation takes place by a subsequent valid marriage between the parents; the annulment of a voidable marriage does not affect it.')
n(180, 'The effects of legitimation retroact to the time of the child’s birth.')
n(194, 'Support comprises everything indispensable for sustenance, dwelling, clothing, medical attendance, education and transportation, in keeping with the financial capacity of the family; education includes schooling or training even beyond the age of majority.')
n(195, 'Persons obliged to support each other: the spouses; legitimate ascendants and descendants; parents and their legitimate children and the legitimate and illegitimate children of the latter; parents and their illegitimate children and the legitimate and illegitimate children of the latter; and legitimate brothers and sisters, whether of full or half-blood.', t=['Illegitimate brothers and sisters owe support only under Art. 196 (unless the need is due to the claimant’s fault or negligence).'])
n(201, 'The amount of support is in proportion to the resources or means of the giver and to the necessities of the recipient.')
n(203, 'The obligation to give support is demandable from the time the person entitled needs it, but it is not paid except from the date of judicial or extrajudicial demand.')
n(209, 'Parental authority and responsibility include the caring for and rearing of unemancipated children for civic consciousness and efficiency, and the development of their moral, mental and physical character and well-being.')
n(211, 'The father and the mother jointly exercise parental authority over the persons of their common children; in case of disagreement, the father’s decision prevails unless there is a judicial order to the contrary.')
n(213, 'In case of separation of the parents, parental authority is exercised by the parent designated by the court, which considers all relevant matters, especially the choice of a child over seven years old unless the parent chosen is unfit. No child under seven years of age shall be separated from the mother unless the court finds compelling reasons to order otherwise (tender-age presumption).', t=['Compelling reasons include neglect, abandonment, unemployment and immorality, habitual drunkenness, drug addiction, maltreatment, insanity, or a communicable disease.'], chk=['seven years'])
n(216, 'In default of parents or a judicially appointed guardian, substitute parental authority is exercised by the surviving grandparent, the oldest brother or sister over twenty-one years old unless unfit, and the child’s actual custodian over twenty-one years old unless unfit, in that order.', chk=['twenty-one'])
n(218, 'The school, its administrators and teachers, or the individual, entity or institution engaged in child care have special parental authority and responsibility over the minor child while under their supervision, instruction or custody, including during activities outside the school.')
n(219, 'Those given special parental authority are principally and solidarily liable for damages caused by the acts or omissions of the unemancipated minor; the parents, judicial guardians or persons exercising substitute parental authority are subsidiarily liable. The liability does not apply if they prove they exercised the proper diligence required.')
n(234, 'Emancipation takes place by the attainment of majority. Majority commences at the age of eighteen years (as amended by RA 6809).', chk=['majority commences at the age of eighteen'])
n(236, 'Emancipation terminates parental authority over the person and property of the child, who is then qualified for all acts of civil life, save the exceptions established by existing laws in special cases (e.g., parental consent for those under twenty-one to marry).')


def main():
    d = json.load(open(f'{SITE}/codes/family.json'))
    by = {p['i']: p for p in d['provisions']}
    errs = []
    for pid, (e, chk) in N.items():
        if pid not in by:
            errs.append('no provision ' + pid); continue
        text = ' '.join(x for x in by[pid]['p'] if isinstance(x, str))
        text += ' ' + ' '.join(x for a in by[pid].get('a', []) for x in a['p'] if isinstance(x, str))
        for c in chk:
            if c.lower() not in text.lower():
                errs.append(f'{pid}: “{c}” not in the text')
    if errs:
        raise SystemExit('\n'.join(errs))
    cur = json.load(open(f'{SITE}/notes/family.json'))
    for pid, (e, _) in N.items():
        cur[pid] = {**cur.get(pid, {}), **e}   # this script's latest text wins; it shares no keys with earlier notes
    json.dump(cur, open(f'{SITE}/notes/family.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('Family Code notes:', len(N), '| family total:', len(cur))


if __name__ == '__main__':
    main()
