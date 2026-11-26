"""Labor Code (renumbered, DOLE 2022 edition): study notes in our own words, merged into data/notes/labor.json.
Article numbers follow the renumbering (RA 10151; DOLE Department Advisory No. 1, s. 2015); old numbers are given in parentheses.
Each note's figures ('chk') must appear in the verbatim article."""
import json

SITE = '/home/claude/site/data'
N = {}


def n(a, x, t=None, k=None, d=None, i=None, chk=()):
    e = {'x': x}
    if t: e['t'] = t
    if k: e['k'] = k
    if d: e['d'] = [{'n': a1, 'c': b, 'h': c, 'r': r} for a1, b, c, r in d]
    if i: e['i'] = [{'t': a1, 's': b, 'u': u} for a1, b, u in i]
    N[f'article-{a}'] = (e, chk)


HB = ('DOLE Handbook on Workers’ Statutory Monetary Benefits (latest edition)', 'DOLE’s guide to computing overtime, night shift, rest day, holiday and other premiums.', 'https://bwc.dole.gov.ph/')
DO174 = ('DOLE Department Order No. 174, s. 2017', 'Rules on contracting and subcontracting under Arts. 106–109: registration of contractors, substantial capital (₱5 million), and the badges of labor-only contracting. Replaced D.O. 18-A (2011).', '#/code/do174')
DO147 = ('DOLE Department Order No. 147, s. 2015', 'Amended the rules implementing Book VI: the twin-notice and hearing requirements for just causes, and notice to DOLE for authorized causes.', '#/code/labor')

# ---------------------------------------------------------------- Book III — conditions of employment
n(82, 'Book III on hours of work, rest and leave applies to employees in all establishments, whether for profit or not, but not to government employees, managerial employees, field personnel, members of the employer’s family who depend on him for support, domestic helpers, persons in the personal service of another, and workers paid by results as determined by DOLE regulations.',
  t=['Field personnel are non-agricultural employees who regularly work away from the principal place of business and whose actual hours of work cannot be determined with reasonable certainty.', 'Officers or members of a managerial staff are also excluded under the implementing rules.'])
n(83, 'The normal hours of work of any employee shall not exceed eight hours a day. Health personnel in cities and municipalities with a population of at least one million, or in hospitals and clinics with a bed capacity of at least one hundred, have a normal schedule of eight hours a day for five days a week.', chk=['eight (8) hours'])
n(84, 'Hours worked include all the time an employee is required to be on duty or at a prescribed workplace, and all time he is suffered or permitted to work. Rest periods of short duration during working hours are counted as hours worked.')
n(85, 'The employer must give employees not less than sixty minutes time-off for their regular meals, subject to the regulations of the Secretary of Labor.', t=['Shortened meal breaks of not less than twenty minutes are compensable hours worked under the implementing rules.'])
n(86, 'Every employee is paid a night shift differential of not less than ten percent of his regular wage for each hour worked between ten o’clock in the evening and six o’clock in the morning.', chk=['ten percent', '10%'], i=[HB])
n(87, 'Work beyond eight hours a day may be performed if the employee is paid an additional compensation of at least twenty-five percent of the regular wage; work beyond eight hours on a holiday or rest day is paid an additional thirty percent of the rate for that day.', chk=['twenty-five percent', 'thirty percent'], i=[HB])
n(88, 'Undertime work on any particular day shall not be offset by overtime work on any other day; permission to go on leave on a working day does not exempt the employer from paying overtime for work on another day.')
n(89, 'Employees may be required to perform overtime work in cases of war or national emergency; urgent work to prevent loss of life or property or in case of imminent danger to public safety; urgent work on machines or equipment to avoid serious loss; work necessary to prevent loss or damage to perishable goods; and to complete work started before the eighth hour if necessary to prevent serious obstruction of the business.')
n(91, 'Every employer must give his employees a rest period of not less than twenty-four consecutive hours after every six consecutive normal work days. The employer schedules the rest day, but must respect the employee’s preference based on religious grounds.', chk=['twenty-four (24) consecutive hours', 'six (6) consecutive normal work days'])
n(93, 'Work on a scheduled rest day is paid an additional compensation of at least thirty percent of the regular wage; work on a Sunday that is the employee’s rest day, or on a special holiday, likewise. Where the nature of the work requires work on Sunday and holidays without a regular rest day, the employee is paid an additional thirty percent for work on those days.', chk=['thirty percent'], i=[HB])
n(94, 'Every worker is paid his regular daily wage during regular holidays, except in retail and service establishments regularly employing less than ten workers. An employer who requires work on a regular holiday pays twice the regular rate.',
  t=['Holiday pay is for regular holidays; special non-working days follow “no work, no pay” unless a company policy or CBA provides otherwise.'], chk=['ten (10)', 'twice'], i=[HB])
n(95, 'Every employee who has rendered at least one year of service is entitled to a yearly service incentive leave of five days with pay. It does not apply to those already enjoying at least five days of vacation leave with pay, or to establishments regularly employing less than ten employees, among others.', t=['Unused service incentive leave is convertible to cash at the end of the year.'])
n(96, 'All service charges collected by hotels, restaurants and similar establishments are distributed completely and equally among the covered workers, except managerial employees (RA 11360, 2019). Service charges are not counted toward compliance with an increased minimum wage.',
  t=['Before RA 11360, the split was 85% to employees and 15% to management.'], i=[('DOLE Department Order No. 206, s. 2019', 'Implements RA 11360 on the full distribution of service charges.', '#/code/labor')])
n(97, 'Definitions for the wage provisions. “Wage” is the remuneration for work done, however fixed, and includes the fair and reasonable value of board, lodging or other facilities customarily furnished by the employer.', t=['Facilities (for the employee’s benefit, deductible from wages) differ from supplements (for the employer’s benefit, not deductible).'])
n(99, 'Regional minimum wages are those prescribed by the Regional Tripartite Wages and Productivity Boards.')
n(100, 'Nothing in Book III shall be construed to eliminate or in any way diminish supplements or other employee benefits being enjoyed at the time of the Code’s promulgation.',
  t=['Non-diminution protects benefits that are given regularly and deliberately over a long period; it does not protect benefits given by error in interpreting a doubtful law.'],
  d=[('Arco Metal Products Co. v. Samahan ng mga Manggagawa sa Arco Metal', 'G.R. No. 170734, May 14, 2008', 'An employer that for years paid benefits in full to employees who had not worked a full year could not later withdraw them, claiming error: the practice had ripened into a company practice protected by non-diminution.', 'When a benefit becomes a company practice.')])
n(102, 'Wages must be paid in legal tender; payment by promissory notes, vouchers, coupons, tokens or tickets is prohibited, even if requested by the employee. Payment by check or money order is allowed when customary or stipulated in a CBA, or in the cases the regulations allow.')
n(103, 'Wages must be paid at least once every two weeks or twice a month at intervals not exceeding sixteen days. When payment cannot be made with that regularity because of force majeure, it must be made immediately after the cause ceases.', chk=['sixteen (16) days'])
n(105, 'Wages are paid directly to the workers, except in case of force majeure (to a person authorized by the worker) or when the worker has died (to his heirs, without need of intestate proceedings).')
n(106, 'An employer who contracts out work remains solidarily liable with the contractor for the employees’ wages. Labor-only contracting is prohibited: it exists when the contractor does not have substantial capital or investment in tools, equipment or machinery, and the workers perform activities directly related to the principal’s main business. The principal is then treated as the employer of the workers.',
  k=['Legitimate job contracting: an independent business with substantial capital, control over its workers, and a service distinct from the principal’s.', 'Labor-only contracting: the “contractor” merely supplies workers; principal and contractor are solidarily liable and the workers become the principal’s employees.'],
  t=['In legitimate contracting, the principal is still solidarily liable for unpaid wages and labor standards, as an indirect employer (Arts. 107 and 109).'], i=[DO174])
n(107, 'An indirect employer is any person, partnership, association or corporation which, not being an employer, contracts with an independent contractor for the performance of any work, task, job or project. It is liable like a direct employer under Art. 106.')
n(109, 'Every employer or indirect employer is responsible with his contractor or subcontractor for any violation of the Code; they are considered direct employers for purposes of civil liability.')
n(110, 'In bankruptcy or liquidation of an employer’s business, workers enjoy first preference for unpaid wages and other monetary claims, ahead of other creditors, including the government.',
  t=['The preference applies only in a formal bankruptcy or liquidation proceeding, and is a preference of credit, not a lien over specific property.'])
n(111, 'In cases of unlawful withholding of wages, the culpable party may be assessed attorney’s fees equivalent to ten percent of the amount of wages recovered.', chk=['ten percent'])
n(113, 'No employer may make deductions from wages except when the worker is insured with his consent and the deduction pays the premium; for union dues where the right to check-off is recognized; and in cases authorized by law or by the Secretary of Labor.')
n(116, 'It is unlawful for any person to withhold any amount from wages or to induce the worker to give up any part of his wages by force, stealth, intimidation, threat or any other means without the worker’s consent.')
n(118, 'It is unlawful for an employer to refuse to pay or reduce wages and benefits, discharge or discriminate against an employee who has filed a complaint, instituted proceedings, or testified under Title II of Book III.')
n(124, 'Standards for setting minimum wages: the needs of workers and their families, the employers’ capacity to pay, consumer price indices, the cost of living, wages in other sectors, and the requirements of economic and social development. Wage distortions resulting from a wage order are corrected through the grievance machinery or, if unresolved, voluntary arbitration in organized establishments, and the NCMB and then the NLRC in unorganized ones.',
  t=['A wage distortion is a severe contraction of intentional quantitative differences in wage rates between employee groups; it cannot be a ground for a strike.'])
n(127, 'No wage order issued by a regional board may provide for wage rates lower than the statutory minimum wage rates prescribed by Congress.')
n(128, 'Visitorial and enforcement power of the Secretary of Labor or his representatives: they may inspect workplaces and records, and issue compliance orders and writs of execution to enforce labor standards, notwithstanding Art. 129 and Art. 224 (formerly 217), where the employer-employee relationship still exists.',
  t=['The power covers labor standards, regardless of the amount involved (RA 7730); the employer may contest it only on grounds that are documentary and verifiable from the records.'])
n(129, 'The DOLE regional director or a duly authorized hearing officer may hear and decide claims for wages and other monetary benefits arising from employer-employee relations, if the claimant does not seek reinstatement and the aggregate claim of each employee does not exceed five thousand pesos.', chk=['five thousand pesos'])

# ---------------------------------------------------------------- Book V — labor relations
n(218, 'The State’s labor-relations policy: promote collective bargaining and voluntary modes of settling disputes (conciliation, mediation, arbitration), ensure workers’ participation in decision-making, and foster free and voluntary organization of a strong and united labor movement.')
n(219, 'Definitions used in Book V, including employer, employee, labor organization, legitimate labor organization, company union, bargaining representative, unfair labor practice, labor dispute, strike, lockout and strike area.',
  t=['A “labor dispute” exists regardless of whether the disputants stand in the proximate relation of employer and employee.'])
n(224, 'Labor Arbiters have original and exclusive jurisdiction over: unfair labor practice cases; termination disputes; cases accompanied by a claim for reinstatement involving wages, hours of work and other terms; claims for damages arising from employer-employee relations; cases arising from violations of Art. 279 (formerly 264) including legality of strikes and lockouts; and all other money claims arising from employer-employee relations exceeding five thousand pesos, except those of Kasambahay. The NLRC has exclusive appellate jurisdiction over their decisions.',
  t=['The test is a reasonable causal connection between the claim and the employer-employee relationship; claims that need the application of civil law go to regular courts (San Miguel Corp. v. NLRC, 1988).', 'Disputes on interpretation of the CBA or company personnel policies go to the voluntary arbitrator (Art. 274).'])
n(229, 'Decisions of the Labor Arbiter are final and executory unless appealed to the NLRC within ten calendar days from receipt, on limited grounds. An employer’s appeal from a monetary award is perfected only upon posting of a cash or surety bond equal to the award. A decision ordering reinstatement is immediately executory even pending appeal: the employee is either admitted back to work or reinstated in the payroll, at the employer’s option.',
  t=['Posting the bond is jurisdictional, though the Court allows a provisional bond of ten percent of the award while a motion to reduce is pending (McBurnie v. Ganzon, 2013).', 'Reinstatement pending appeal is self-executory; no writ of execution is needed.'], chk=['ten (10)'])
n(233, 'Compromise agreements, including those resolving unfair labor practice cases, freely entered into and approved by DOLE’s mediators or conciliators, are final and binding, and the NLRC or any court will not assume jurisdiction over issues involved in them except in case of non-compliance or prima facie evidence that the settlement was obtained through fraud, misrepresentation or coercion.')
n(240, 'Requirements for registration of a labor organization: the application, names and addresses of officers, the minutes of the organizational meetings, the names of all members comprising at least twenty percent of the employees in the bargaining unit, the annual financial reports if the applicant has been in existence for one or more years, and the constitution and by-laws.', chk=['twenty percent'])
n(247, 'Grounds for cancellation of union registration: misrepresentation, false statement or fraud in connection with the adoption or ratification of the constitution, by-laws and amendments, or the election of officers; and voluntary dissolution by the members.', t=['RA 9481 (2007) narrowed the grounds; a union’s failure to file reports is no longer a ground for cancellation, and commingling of supervisory and rank-and-file employees is not a ground.'])
n(253, 'All persons employed in commercial, industrial and agricultural enterprises and in religious, charitable, medical or educational institutions, whether operating for profit or not, have the right to self-organization and to form, join or assist labor organizations for collective bargaining. Ambulant, intermittent and itinerant workers, the self-employed, rural workers and those without definite employers may form labor organizations for their mutual aid and protection.')
n(255, 'Managerial employees are not eligible to join, assist or form any labor organization. Supervisory employees may not join the rank-and-file union but may form their own; the rank-and-file union and the supervisors’ union may affiliate with the same federation.',
  t=['Confidential employees who assist managers in matters of labor relations are likewise excluded (doctrine of necessary implication).'])
n(258, 'Unfair labor practices violate the constitutional right of workers to self-organization, are inimical to the legitimate interests of labor and management, and disrupt industrial peace. They are both civil and criminal offenses; the civil aspect falls under the Labor Arbiters, and criminal prosecution needs a final judgment in the administrative case.')
n(259, 'Unfair labor practices of employers: interfering with or coercing employees in the exercise of their right to self-organization; requiring as a condition of employment that a person not join a union; contracting out services to bust a union; initiating, dominating or assisting a labor organization (company union); discriminating to encourage or discourage union membership; dismissing or discriminating against an employee for testifying; violating the duty to bargain collectively; paying negotiation or attorney’s fees to the union or its officers as part of a settlement; and gross violation of the CBA.',
  t=['ULP needs a connection to the employees’ right to self-organization. A mere CBA violation is ULP only if gross (flagrant or malicious refusal to comply with its economic provisions).'])
n(260, 'Unfair labor practices of labor organizations: restraining or coercing employees in their right to self-organization; causing the employer to discriminate against an employee; violating the duty to bargain collectively; causing or attempting to cause an employer to pay for services not performed (featherbedding); asking for or accepting negotiation fees from the employer; and gross violation of the CBA.')
n(263, 'The duty to bargain collectively means the performance of a mutual obligation to meet and convene promptly and expeditiously in good faith to negotiate an agreement on wages, hours of work and all other terms and conditions of employment, but it does not compel any party to agree to a proposal or to make any concession.')
n(265, 'Terms of a CBA: the representation aspect lasts five years; no petition questioning the majority status of the incumbent union may be entertained outside the sixty-day period immediately before the end of that five-year term (the freedom period). All other provisions are renegotiated not later than three years after execution.', chk=['five (5) years', 'sixty-day'])
n(267, 'The labor organization designated or selected by the majority of the employees in an appropriate bargaining unit is the exclusive representative of the employees in that unit for collective bargaining. Individual employees may still present grievances to the employer at any time.')
n(268, 'In organized establishments, when a verified petition questioning the majority status of the incumbent bargaining agent is filed by a legitimate labor organization within the sixty-day freedom period, a certification election shall automatically be conducted, provided the petition is supported by the written consent of at least twenty-five percent of all the employees in the bargaining unit.', chk=['twenty-five percent'])
n(269, 'In unorganized establishments, a certification election is automatically conducted by the Med-Arbiter upon the filing of a petition by any legitimate labor organization, including a national union or federation that has issued a charter certificate to its local or chapter.', t=['No minimum consent requirement applies in unorganized establishments.'])
n(271, 'In certification elections the employer is a bystander and has no right to oppose the petition or to take part in the proceedings, except to be notified or to ask for a certification election when asked to bargain.')
n(273, 'Every CBA must provide a grievance machinery to settle grievances arising from the interpretation or implementation of the agreement and from the interpretation or enforcement of company personnel policies; unresolved grievances go to voluntary arbitration.')
n(274, 'Voluntary arbitrators have original and exclusive jurisdiction over unresolved grievances arising from the interpretation or implementation of the CBA and from the interpretation or enforcement of company personnel policies. Gross violations of the CBA (flagrant refusal to comply with its economic provisions) are not treated as ULP and are resolved by them too.',
  t=['Their decisions are appealed to the Court of Appeals by petition for review under Rule 43 (Luzon Development Bank v. Association of Luzon Development Bank Employees, 1995).'])
n(275, 'Voluntary arbitrators may, upon agreement of the parties, hear and decide all other labor disputes, including unfair labor practices and bargaining deadlocks.')
n(278, 'Strikes, picketing and lockouts. A strike or lockout needs a notice to the NCMB: thirty days before the intended date in case of a bargaining deadlock, fifteen days in case of unfair labor practice (no notice period for union busting threatening the union’s existence). A strike vote by a majority of the bargaining unit, by secret ballot, must be reported to the NCMB at least seven days before the strike. In industries indispensable to the national interest, the Secretary of Labor may assume jurisdiction or certify the dispute to the NLRC, which automatically enjoins any strike or lockout and requires return to work.',
  k=['Valid grounds: bargaining deadlock and unfair labor practice only.', 'Requirements: notice, cooling-off period, strike vote, report of the vote, and the seven-day waiting period after it.'],
  t=['A union officer who knowingly takes part in an illegal strike may be dismissed; an ordinary member is liable only for knowingly taking part in illegal acts during the strike.', 'Defiance of a return-to-work order makes the strike illegal and those who defy it lose their employment status.'],
  chk=['thirty (30)'])
n(279, 'Prohibited activities: no strike or lockout without first having bargained collectively, or after assumption of jurisdiction or certification, or during the pendency of cases submitted to voluntary arbitration; no obstruction of free ingress to or egress from the employer’s premises; no use of violence, coercion or intimidation; and no use of strikebreakers.')
n(284, 'Foreigners may not engage in trade-union activities in the Philippines, except foreign nationals with valid working permits issued by DOLE (Alien Employment Permits) whose countries grant the same or similar rights to Filipino workers.', t=['Read with Art. 40 (AEP) and the reciprocity condition.'])

# ---------------------------------------------------------------- Book VI — post-employment
n(299, 'An employer may terminate an employee found to be suffering from any disease whose continued employment is prohibited by law or prejudicial to his health or that of his co-employees, upon payment of separation pay of at least one month’s salary or one-half month’s salary for every year of service, whichever is greater, a fraction of at least six months counting as one whole year.',
  t=['The implementing rules require a certification by a competent public health authority that the disease cannot be cured within six months even with proper medical treatment.'], chk=['one (1)', 'six (6)'])
n(300, 'An employee may terminate the employment without just cause by serving written notice on the employer at least one month in advance; without notice, for serious insult, inhuman and unbearable treatment, commission of a crime by the employer against him or his family, and analogous causes.',
  t=['Constructive dismissal: a resignation forced by the employer’s acts is treated as an illegal dismissal.'])
n(301, 'The bona fide suspension of the operation of a business or undertaking for a period not exceeding six months, or the fulfillment by the employee of a military or civic duty, does not terminate employment; the employer must reinstate the employee who indicates a desire to resume work not later than one month from the resumption of operations or relief from the duty.', chk=['six (6) months'])
n(302, 'Retirement: an employee may retire upon reaching the age fixed in a CBA or employment contract. Absent a retirement plan, an employee may retire at sixty (optional) and must retire at sixty-five (compulsory), if he has served at least five years, and is entitled to retirement pay of at least one-half month’s salary for every year of service, a fraction of at least six months counting as one year.',
  k=['“One-half month salary” means 22.5 days: 15 days’ salary, plus one-twelfth of the 13th month pay, plus the cash equivalent of five days of service incentive leave.'],
  t=['Underground mine workers may retire at fifty, and compulsorily at sixty, under RA 8558 (now RA 10757 also covers surface mine workers).', 'Retail, service and agricultural establishments employing not more than ten employees are exempt.'],
  chk=['sixty (60)', 'sixty-five (65)', 'five (5)'])
n(306, 'All money claims arising from employer-employee relations accruing during the effectivity of the Code shall be filed within three years from the time the cause of action accrued; otherwise they are forever barred.',
  t=['An action for illegal dismissal is an action for injury to rights and prescribes in four years (Art. 1146, Civil Code); the money claims attached to it prescribe in three years.'], chk=['three (3) years'])

IRR = {'82': ('biii-rule-i-sec-1', 'Book III, Rule I, Secs. 1–2: coverage and exemptions'),
       '83': ('biii-rule-i-a-sec-5', 'Book III, Rule I-A: hours of work of hospital and clinic personnel'),
       '84': ('biii-rule-i-sec-3', 'Book III, Rule I, Secs. 3–6: what counts as hours worked (waiting time, lectures, meetings, training)'),
       '85': ('biii-rule-i-sec-7', 'Book III, Rule I, Sec. 7: meal and rest periods, including shortened meal breaks'),
       '86': ('biii-rule-ii-sec-2', 'Book III, Rule II: night shift differential and how it combines with other premiums'),
       '87': ('biii-rule-i-sec-8', 'Book III, Rule I, Secs. 8–9: overtime pay and holiday or rest-day premiums'),
       '89': ('biii-rule-i-sec-10', 'Book III, Rule I, Sec. 10: when overtime may be compelled')}
for a, (pid, desc) in IRR.items():
    e, chk = N[f'article-{a}']
    e.setdefault('i', []).insert(0, {'t': 'Omnibus Rules Implementing the Labor Code (1989 compilation), ' + desc.split(':')[0], 's': desc.split(': ', 1)[1].capitalize() + '.', 'u': f'#/p/irrlabor/{pid}'})


def main():
    d = json.load(open(f'{SITE}/codes/labor.json'))
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
    cur = json.load(open(f'{SITE}/notes/labor.json'))
    for pid, (e, _) in N.items():
        cur[pid] = {**cur.get(pid, {}), **e}   # this script's latest text wins; it shares no keys with earlier notes
    json.dump(cur, open(f'{SITE}/notes/labor.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('Labor notes:', len(N), '| labor total:', len(cur))


if __name__ == '__main__':
    main()
