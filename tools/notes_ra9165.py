"""RA 9165 (Comprehensive Dangerous Drugs Act): study notes in our own words, written to data/notes/ra9165.json, checked against the text."""
import json
SITE = '/home/claude/site/data'
IRR21 = {'t': 'IRR of RA 9165 (2002), Art. II, Sec. 21', 's': 'Details the custody and disposition procedure; read with RA 10640 (2014).', 'u': '#/p/irr9165/article-ii-sec-21'}
PB = {'t': 'A.M. No. 18-03-16-SC (2018), Plea Bargaining Framework in Drugs Cases, as later amended', 's': 'Lists the lesser offenses an accused may plead to, by quantity and kind of drug, and conditions such as drug dependency assessment.', 'u': 'https://sc.judiciary.gov.ph/'}
N = {
 'section-5': ({'x': 'Selling, trading, administering, dispensing, delivering, giving away, distributing, dispatching in transit or transporting any dangerous drug, regardless of quantity and purity, without authority, is punished by life imprisonment and a fine of ₱500,000 to ₱10,000,000.',
   'k': ['Elements of illegal sale: (1) the identity of the buyer and seller, the object and the consideration; (2) the delivery of the thing sold and the payment for it.', 'The corpus delicti is the drug itself; its identity must be proved beyond reasonable doubt through an unbroken chain of custody.'],
   't': ['Quantity does not matter for sale: even a trace amount is punished.', 'A buy-bust operation is a valid form of entrapment, not instigation.'], 'i': [IRR21]}, ['five hundred thousand pesos']),
 'section-11': ({'x': 'Possession of dangerous drugs without legal authority, with penalties graded by kind and quantity: life imprisonment and a large fine for the larger quantities listed (e.g., 50 grams or more of shabu), down to twelve years and one day to twenty years for less than five grams.',
   'k': ['Elements: (1) the accused is in possession of an item identified as a dangerous drug; (2) the possession is not authorized by law; (3) the accused freely and consciously possessed it.', 'Possession may be actual or constructive (dominion and control over the place).'],
   't': ['Mere possession of a prohibited drug is prima facie evidence of animus possidendi, which the accused must explain.'], 'i': [IRR21]}, ['twelve (12) years']),
 'section-15': ({'x': 'A person found positive for use of dangerous drugs after a confirmatory test is punished, for a first offense, by a minimum of six months’ rehabilitation in a government center; for a second offense, by imprisonment and a fine. This applies only if he is not also found to possess the drugs (then Sec. 11 applies).',
   't': ['A drug test under this section is for persons apprehended for crimes under RA 9165; it may not be required of persons arrested for unrelated crimes (Dela Cruz v. People, 2014).'],
   'd': [{'n': 'Social Justice Society v. Dangerous Drugs Board', 'c': 'G.R. No. 157870, November 3, 2008', 'h': 'Mandatory drug testing of candidates for public office (an added qualification) and of persons charged before the prosecutor’s office was unconstitutional; random testing of students and of public and private employees was upheld as reasonable.', 'r': 'Limits of mandatory drug testing.'}]}, ['six (6) months']),
 'section-21': ({'x': 'The chain-of-custody rule. Immediately after seizure, the apprehending team must physically inventory and photograph the seized drugs in the presence of the accused and the required witnesses, and turn them over to the PDEA forensic laboratory for examination within twenty-four hours. As amended by RA 10640 (2014), the witnesses are an elected public official and a representative of the National Prosecution Service or the media; for warrantless seizures, the inventory may be made at the nearest police station or office of the team.',
   'k': ['The four links of the chain: (1) seizure and marking by the apprehending officer; (2) turnover to the investigating officer; (3) turnover to the forensic chemist; (4) turnover and submission of the marked drug to the court.'],
   't': ['Non-compliance does not automatically acquit if the prosecution proves justifiable grounds and that the integrity and evidentiary value of the items were preserved; but the prosecution must acknowledge and explain the lapses, and show earnest efforts to secure the witnesses.', 'The witnesses must be present at or near the time of apprehension and seizure, not merely called in for the inventory later (People v. Tomawis, 2018).'],
   'd': [{'n': 'People v. Lim', 'c': 'G.R. No. 231989, September 4, 2018 (En Banc)', 'h': 'The Court laid down a mandatory policy: the apprehending officers must state their compliance with Sec. 21 in their sworn statements, or the justifiable reasons for non-compliance and the steps taken to preserve the evidence; prosecutors must ensure this before filing, and courts may dismiss for unexplained lapses.', 'r': 'The controlling procedure on Sec. 21.'},
         {'n': 'Mallillin v. People', 'c': 'G.R. No. 172953, April 30, 2008', 'h': 'Chain of custody requires testimony about every link, from seizure to presentation in court, showing how the item was handled and that it was not altered or substituted.', 'r': 'What the chain of custody is.'}],
   'i': [IRR21, {'t': 'RA 10640 (2014)', 's': 'Amended Sec. 21(1): fewer required witnesses (elected official plus NPS or media), inventory at the nearest police station allowed for warrantless seizures, and a saving clause for justified non-compliance.', 'u': 'https://lawphil.net/statutes/repacts/ra2014/ra_10640_2014.html'}]}, ['twenty-four (24) hours']),
 'section-23': ({'x': 'The Act barred plea bargaining for anyone charged under it, regardless of the penalty. The Supreme Court struck this down in 2017; plea bargaining in drug cases is now governed by the Court’s own framework.',
   'd': [{'n': 'Estipona v. Lobrigo', 'c': 'G.R. No. 226679, August 15, 2017', 'h': 'Section 23 is unconstitutional: plea bargaining is a rule of procedure, and the power to promulgate rules of procedure belongs exclusively to the Supreme Court.', 'r': 'Why the ban fell.'}],
   'i': [PB]}, ['plea-bargaining']),
}
def main():
    d = json.load(open(f'{SITE}/codes/ra9165.json')); by = {p['i']: p for p in d['provisions']}
    errs = []
    for pid, (e, chk) in N.items():
        t = ' '.join(x for x in by[pid]['p'] if isinstance(x, str)).lower()
        errs += [f'{pid}: “{c}”' for c in chk if c.lower() not in t]
    if errs: raise SystemExit('\n'.join(errs))
    json.dump({k: v[0] for k, v in N.items()}, open(f'{SITE}/notes/ra9165.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('RA 9165 notes:', len(N))
if __name__ == '__main__':
    main()
