"""Treaties and international law binding on the Philippines: a registry in our own words.
Ratification dates: exact days where an official UN-system record was checked (OHCHR treaty-body records as compiled
for the Universal Periodic Review, ICRC statements, the University of Minnesota Human Rights Library); otherwise the
year only. Treaty texts are not reproduced: each entry links to the depositary's official text."""
import json, hashlib
T = []
def t(**k): T.append(k)

UNTC = 'https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no={}&chapter={}&clang=_en'
# ---------------------------------------------------------------- the framework
t(id='un-charter', area='Framework', name='Charter of the United Nations', adopted='1945', ph='Original member: signed at San Francisco in 1945, ratified the same year', status='party',
  what='Creates the United Nations and its organs. Binds members to settle disputes peacefully, to refrain from the threat or use of force against any state (Art. 2(4)), subject to self-defence (Art. 51) and Security Council action (Chapter VII), and to carry out Security Council decisions (Art. 25). The Statute of the International Court of Justice is part of it.',
  how='The Constitution renounces war as an instrument of national policy and adopts the generally accepted principles of international law as part of the law of the land (Art. II, Sec. 2).',
  laws=[('const1987', 'art-ii-sec-2', 'Constitution, Art. II, Sec. 2')], cases=[], url='https://www.un.org/en/about-us/un-charter/full-text')
t(id='vclt', area='Framework', name='Vienna Convention on the Law of Treaties', adopted='1969', ph='Ratified 1972', status='party',
  what='The treaty on treaties: how they are concluded, reserved to, interpreted (good faith, ordinary meaning in context, object and purpose: Arts. 31–32), suspended and terminated. Pacta sunt servanda (Art. 26); a state may not invoke its internal law to justify failing to perform a treaty (Art. 27); treaties conflicting with jus cogens are void (Art. 53).',
  how='Applied by the Supreme Court in construing treaties and executive agreements. Under the Constitution, no treaty or international agreement is valid and effective unless concurred in by at least two-thirds of all the Members of the Senate (Art. VII, Sec. 21).',
  laws=[('const1987', 'art-vii-sec-21', 'Constitution, Art. VII, Sec. 21')],
  cases=[dict(n='Bayan Muna v. Romulo', cite='G.R. No. 159618, February 1, 2011', held='The RP-US Non-Surrender Agreement was a valid executive agreement that did not need Senate concurrence; executive agreements bind the state like treaties under international law.'),
         dict(n='Intellectual Property Association of the Philippines v. Ochoa', cite='G.R. No. 204605, July 19, 2016', held='Accession to the Madrid Protocol was validly done as an executive agreement, without Senate concurrence.')],
  url=UNTC.format('XXIII-1', '23'))
t(id='unclos', area='Law of the sea', name='United Nations Convention on the Law of the Sea (UNCLOS)', adopted='1982', ph='Signed 1982, ratified 1984', status='party',
  what='The constitution of the oceans: baselines, a 12-mile territorial sea, a 24-mile contiguous zone, a 200-mile exclusive economic zone, the continental shelf, archipelagic states and archipelagic waters (Part IV), innocent and archipelagic sea-lanes passage, and compulsory dispute settlement (Part XV).',
  how='Implemented by the Philippine Archipelagic Baselines Law (RA 9522, 2009), the Maritime Zones Act and the Archipelagic Sea Lanes Act (both 2024). The national territory clause speaks of the archipelago and its waters (Art. I).',
  laws=[('const1987', 'art-i', 'Constitution, Art. I'), ('law', 'ra-9522', 'RA 9522 (baselines)'), ('law', 'ra-12064', 'RA 12064 (Maritime Zones Act)'), ('law', 'ra-12065', 'RA 12065 (Archipelagic Sea Lanes Act)')],
  cases=[dict(n='Magallona v. Ermita', cite='G.R. No. 187167, August 16, 2011', held='RA 9522, redrawing the baselines to conform to UNCLOS, is constitutional; it does not cede territory, and baselines laws are a means of marking maritime zones, not of acquiring or losing territory.'),
         dict(n='The South China Sea Arbitration (Philippines v. China)', cite='PCA Case No. 2013-19, Award of July 12, 2016', held='An UNCLOS Annex VII tribunal ruled that China’s claimed historic rights within the “nine-dash line” have no legal basis to the extent they exceed UNCLOS entitlements, and that certain features are rocks or low-tide elevations.')],
  url=UNTC.format('XXI-6', '21'))
# ---------------------------------------------------------------- human rights
t(id='udhr', area='Human rights', name='Universal Declaration of Human Rights', adopted='1948', ph='Voted for in the General Assembly, 1948 (a declaration, not a treaty)', status='declaration',
  what='The founding statement of human rights: dignity, equality, life, liberty, fair trial, privacy, expression, religion, work, education and the rest. Not a treaty, but much of it is treated as customary international law.',
  how='Cited by the Supreme Court as part of the generally accepted principles adopted by the Constitution.',
  laws=[('const1987', 'art-ii-sec-11', 'Constitution, Art. II, Sec. 11')],
  cases=[dict(n='Government of Hong Kong SAR v. Olalia', cite='G.R. No. 153675, April 19, 2007', held='Relying on the UDHR and the country’s human-rights commitments, the Court held that a potential extraditee may apply for bail on clear and convincing proof that he is not a flight risk.'),
         dict(n='Republic v. Sandiganbayan', cite='G.R. No. 104768, July 21, 2003', held='During the interregnum after the 1986 revolution the Bill of Rights was not operative, but the ICCPR and the UDHR remained in effect and protected individuals against the revolutionary government.')],
  url='https://www.un.org/en/about-us/universal-declaration-of-human-rights')
t(id='iccpr', area='Human rights', name='International Covenant on Civil and Political Rights (ICCPR)', adopted='1966', ph='Signed 19 Dec 1966; ratified 23 Oct 1986. First Optional Protocol (individual complaints) 22 Aug 1989; Second Optional Protocol (abolition of the death penalty) 20 Nov 2007', status='party',
  what='Life, freedom from torture, liberty and security, fair trial, privacy, thought, expression, assembly, association, participation, equality, minority rights. The Second Optional Protocol binds the state not to execute anyone and to abolish the death penalty.',
  how='The Bill of Rights covers most of it; RA 9346 (2006) prohibited the imposition of the death penalty before ratification of the Second Optional Protocol.',
  laws=[('ra9346', None, 'RA 9346 (death penalty prohibited)')], cases=[], url=UNTC.format('IV-4', '4'))
t(id='icescr', area='Human rights', name='International Covenant on Economic, Social and Cultural Rights (ICESCR)', adopted='1966', ph='Signed 19 Dec 1966; ratified 7 Jun 1974', status='party',
  what='Work and just conditions of work, trade unions, social security, family protection, an adequate standard of living, health, education and culture, to be realised progressively to the maximum of available resources.',
  how='Echoed in the social justice provisions of the Constitution (Art. XIII) and in labor and social legislation.', laws=[], cases=[], url=UNTC.format('IV-3', '4'))
t(id='icerd', area='Human rights', name='International Convention on the Elimination of All Forms of Racial Discrimination (ICERD)', adopted='1965', ph='Signed 7 Mar 1966; ratified 15 Sep 1967', status='party',
  what='Bans racial discrimination in all its forms and requires states to prohibit it in law and practice.', how='Equal protection (Art. III, Sec. 1).', laws=[], cases=[], url=UNTC.format('IV-2', '4'))
t(id='cedaw', area='Human rights', name='Convention on the Elimination of All Forms of Discrimination against Women (CEDAW)', adopted='1979', ph='Signed 15 Jul 1980; ratified 5 Aug 1981. Optional Protocol 12 Nov 2003', status='party',
  what='Requires states to eliminate discrimination against women in public and private life, including through legislation and temporary special measures.',
  how='Implemented chiefly by the Magna Carta of Women (RA 9710, 2009) and the Anti-VAWC Act (RA 9262, 2004).', laws=[('ra9710', None, 'RA 9710 (Magna Carta of Women)'), ('ra9262', None, 'RA 9262 (Anti-VAWC Act)')], cases=[], url=UNTC.format('IV-8', '4'))
t(id='cat', area='Human rights', name='Convention against Torture and Other Cruel, Inhuman or Degrading Treatment or Punishment (CAT)', adopted='1984', ph='Acceded 18 Jun 1986. Optional Protocol (OPCAT) acceded 17 Apr 2012', status='party',
  what='An absolute ban on torture, with no exceptions even in emergencies; criminalisation; non-refoulement; investigation; redress. OPCAT adds preventive visits to places of detention.',
  how='Implemented by the Anti-Torture Act (RA 9745, 2009). The Constitution itself bans torture, force, violence, threat and intimidation (Art. III, Sec. 12(2)).', laws=[('const1987', 'art-iii-sec-12', 'Constitution, Art. III, Sec. 12'), ('law', 'ra-9745', 'RA 9745 (Anti-Torture Act)')], cases=[], url=UNTC.format('IV-9', '4'))
t(id='crc', area='Human rights', name='Convention on the Rights of the Child (CRC)', adopted='1989', ph='Signed 26 Jan 1990; ratified 21 Aug 1990. Optional Protocols on children in armed conflict (2003) and on the sale of children (2002)', status='party',
  what='The best interests of the child as a primary consideration; survival, development, protection and participation rights; special protection from exploitation, abuse and armed conflict.',
  how='Implemented by, among others, RA 7610 (child abuse), RA 9344 (juvenile justice), RA 11188 (children in armed conflict), RA 11930 (online sexual abuse) and RA 11648 (age of consent raised to 16).',
  laws=[('ra7610', None, 'RA 7610'), ('ra9344', None, 'RA 9344'), ('ra11930', None, 'RA 11930'), ('ra11648', None, 'RA 11648')], cases=[], url=UNTC.format('IV-11', '4'))
t(id='crpd', area='Human rights', name='Convention on the Rights of Persons with Disabilities (CRPD)', adopted='2006', ph='Ratified 2008', status='party',
  what='Equality and non-discrimination for persons with disabilities, accessibility, legal capacity, inclusive education and work.', how='Magna Carta for Persons with Disability (RA 7277, as amended).', laws=[('law', 'ra-7277', 'RA 7277')], cases=[], url=UNTC.format('IV-15', '4'))
t(id='icrmw', area='Human rights', name='International Convention on the Protection of the Rights of All Migrant Workers and Members of Their Families', adopted='1990', ph='Ratified 1995', status='party',
  what='Rights of migrant workers and their families in the countries of origin, transit and employment, documented or not.',
  how='The Migrant Workers and Overseas Filipinos Act (RA 8042, 1995, as amended by RA 10022) and the creation of the Department of Migrant Workers (RA 11641, 2021).', laws=[('ra8042', None, 'RA 8042'), ('ra10022', None, 'RA 10022'), ('law', 'ra-11641', 'RA 11641 (Department of Migrant Workers)')], cases=[], url=UNTC.format('IV-13', '4'))
t(id='refugees', area='Human rights', name='Convention relating to the Status of Refugees (1951) and its 1967 Protocol', adopted='1951 / 1967', ph='Acceded to both 22 Jul 1981', status='party',
  what='Who is a refugee, their rights, and the rule against refoulement (sending a refugee back to persecution).', how='Refugee status determination is handled by the Department of Justice; the Philippine Immigration Act (CA 613) governs entry.', laws=[('ca613', None, 'CA 613 (Immigration Act)')], cases=[], url=UNTC.format('V-2', '5'))
t(id='genocide', area='Human rights', name='Convention on the Prevention and Punishment of the Crime of Genocide', adopted='1948', ph='Signed 11 Dec 1948; ratified 7 Jul 1950', status='party',
  what='Genocide is a crime under international law, whether in peace or war; states must prevent and punish it.', how='Genocide is punishable under RA 9851 (2009).', laws=[('ra9851', None, 'RA 9851')], cases=[], url=UNTC.format('IV-1', '4'))
# ---------------------------------------------------------------- international humanitarian and criminal law
t(id='geneva', area='Armed conflict and international crimes', name='Geneva Conventions of 1949 (I–IV)', adopted='1949', ph='Signed 8 Dec 1949; ratified 6 Oct 1952', status='party',
  what='Protect the wounded and sick on land (I) and at sea (II), prisoners of war (III) and civilians (IV). Common Article 3 sets minimum humane treatment in non-international armed conflicts. Grave breaches must be prosecuted or extradited.',
  how='RA 9851 (2009) defines and punishes war crimes, genocide and crimes against humanity; RA 10530 protects the red cross emblem.', laws=[('ra9851', None, 'RA 9851'), ('law', 'ra-10530', 'RA 10530 (emblems)')],
  cases=[dict(n='Kuroda v. Jalandoni', cite='G.R. No. L-2662, March 26, 1949', held='Generally accepted rules of war (the Hague and Geneva Conventions) were part of the law of the land under the Constitution’s incorporation clause, even before the Philippines signed them; the military commission could try a Japanese general for war crimes.')],
  url='https://ihl-databases.icrc.org/en/ihl-treaties/gci-1949')
t(id='ap', area='Armed conflict and international crimes', name='Additional Protocols I and II to the Geneva Conventions (1977)', adopted='1977', ph='Both signed 1977. Protocol II ratified 11 Dec 1986; Protocol I ratified 30 Mar 2012', status='party',
  what='Protocol I strengthens protection in international armed conflicts (distinction, proportionality, precautions). Protocol II protects victims of non-international armed conflicts.',
  how='Implemented through RA 9851, RA 11188 (children in armed conflict) and related laws.', laws=[('ra9851', None, 'RA 9851'), ('law', 'ra-11188', 'RA 11188')], cases=[], url='https://ihl-databases.icrc.org/en/ihl-treaties/api-1977')
t(id='rome', area='Armed conflict and international crimes', name='Rome Statute of the International Criminal Court', adopted='1998', ph='Signed 28 Dec 2000; ratified 30 Aug 2011 (in force for the Philippines 1 Nov 2011). Withdrawal notified in March 2018, effective 17 Mar 2019', status='withdrawn',
  what='Creates the ICC, with jurisdiction over genocide, crimes against humanity, war crimes and aggression when national courts are unwilling or unable to act (complementarity). A withdrawal does not affect jurisdiction over crimes committed while the state was a party.',
  how='Even before ratification, RA 9851 punished the same crimes domestically and allows surrender to international courts.', laws=[('ra9851', None, 'RA 9851')],
  cases=[dict(n='Pimentel v. Office of the Executive Secretary', cite='G.R. No. 158088, July 6, 2005', held='The President, as head of the country’s foreign relations, cannot be compelled by mandamus to transmit a signed treaty (the Rome Statute) to the Senate for concurrence.'),
         dict(n='Pangilinan v. Cayetano', cite='G.R. No. 238875, March 16, 2021', held='Petitions against the withdrawal from the Rome Statute were dismissed as moot; the Court discussed the President’s authority over withdrawal and the limits where the Senate has conditioned its concurrence or a law requires the treaty.')],
  url=UNTC.format('XVIII-10', '18'))
# ---------------------------------------------------------------- crime and corruption
t(id='untoc', area='Crime and corruption', name='UN Convention against Transnational Organized Crime and its Trafficking and Migrant Smuggling Protocols (Palermo)', adopted='2000', ph='Signed 14 Dec 2000; convention and both protocols ratified 28 May 2002', status='party',
  what='Criminalise participation in organised criminal groups, money laundering, corruption and obstruction of justice; the protocols define trafficking in persons and migrant smuggling.',
  how='Anti-Trafficking in Persons Act (RA 9208, 2003, expanded by RA 10364 and RA 11862) and the Anti-Money Laundering Act (RA 9160).', laws=[('ra9208', None, 'RA 9208'), ('ra10364', None, 'RA 10364'), ('ra11862', None, 'RA 11862'), ('ra9160', None, 'RA 9160')], cases=[], url=UNTC.format('XVIII-12', '18'))
t(id='uncac', area='Crime and corruption', name='United Nations Convention against Corruption (UNCAC)', adopted='2003', ph='Ratified 2006', status='party',
  what='Prevention, criminalisation (bribery, embezzlement, illicit enrichment), international cooperation and asset recovery.', how='RA 3019, RA 6713, RA 7080 (plunder) and the Ombudsman Act (RA 6770).',
  laws=[('ra3019', None, 'RA 3019'), ('ra6713', None, 'RA 6713'), ('ra7080', None, 'RA 7080'), ('ra6770', None, 'RA 6770')], cases=[], url=UNTC.format('XVIII-14', '18'))
t(id='terror', area='Crime and corruption', name='Counter-terrorism conventions (hostage-taking, terrorist bombings, terrorist financing)', adopted='1979–1999', ph='Hostages: ratified 14 Oct 1980. Bombings and financing: ratified 7 Jan 2004', status='party',
  what='Require states to criminalise and prosecute or extradite those who take hostages, bomb public places, or finance terrorism.', how='Anti-Terrorism Act of 2020 (RA 11479) and the Terrorism Financing Prevention and Suppression Act (RA 10168).', laws=[('ra11479', None, 'RA 11479'), ('law', 'ra-10168', 'RA 10168')], cases=[], url='https://www.un.org/counterterrorism/international-legal-instruments')
t(id='budapest', area='Crime and corruption', name='Council of Europe Convention on Cybercrime (Budapest Convention)', adopted='2001', ph='Acceded 2018', status='party',
  what='Harmonises cybercrime offences, procedural powers over computer data, and international cooperation.', how='Cybercrime Prevention Act (RA 10175, 2012) and the Supreme Court’s Rule on Cybercrime Warrants (2018).', laws=[('ra10175', None, 'RA 10175')], cases=[], url='https://www.coe.int/en/web/conventions/full-list?module=treaty-detail&treatynum=185')
# ---------------------------------------------------------------- labour
t(id='ilo-core', area='Labour', name='ILO fundamental conventions (freedom of association, collective bargaining, equal pay, non-discrimination, forced and child labour)', adopted='1930–1999', ph='C87 and C98: 29 Dec 1953. C100: 29 Dec 1953. C105 and C111: 17 Nov 1960. C182: 28 Nov 2000. Others in later years', status='party',
  what='Workers’ right to organise and bargain collectively, equal remuneration, freedom from discrimination, and the elimination of forced labour and the worst forms of child labour.',
  how='The Labor Code’s Book V (labor relations) and the Constitution’s guarantee of the right to self-organisation (Art. III, Sec. 8; Art. XIII, Sec. 3).', laws=[('labor', None, 'Labor Code'), ('const1987', 'art-xiii-sec-3', 'Constitution, Art. XIII, Sec. 3')], cases=[], url='https://normlex.ilo.org/dyn/normlex/en/f?p=1000:11200:0::NO::P11200_COUNTRY_ID:102970')
t(id='ilo-189', area='Labour', name='ILO Domestic Workers Convention (C189) and Maritime Labour Convention (MLC, 2006)', adopted='2006 / 2011', ph='Both ratified 2012', status='party',
  what='Decent work for domestic workers; a bill of rights for seafarers.', how='Batas Kasambahay (RA 10361, 2013) and the Magna Carta of Filipino Seafarers (RA 12021, 2024).', laws=[('ra10361', None, 'RA 10361 (Batas Kasambahay)'), ('law', 'ra-12021', 'RA 12021 (Magna Carta of Filipino Seafarers)')], cases=[], url='https://normlex.ilo.org/dyn/normlex/en/f?p=1000:11200:0::NO::P11200_COUNTRY_ID:102970')
# ---------------------------------------------------------------- trade, private international law, IP
t(id='wto', area='Trade, investment and intellectual property', name='Marrakesh Agreement Establishing the World Trade Organization (with GATT 1994, GATS, TRIPS)', adopted='1994', ph='Senate concurrence December 1994; member since 1 Jan 1995', status='party',
  what='Most-favoured-nation treatment, national treatment, tariff bindings, trade in services, minimum standards of intellectual property protection (TRIPS), and binding dispute settlement.',
  how='Implemented through tariff and customs laws (now the CMTA, RA 10863), the Intellectual Property Code (RA 8293) and trade-remedy laws.', laws=[('cmta', None, 'CMTA (RA 10863)'), ('ipcode', None, 'IP Code (RA 8293)')],
  cases=[dict(n='Tañada v. Angara', cite='G.R. No. 118295, May 2, 1997', held='The Senate’s concurrence in the WTO Agreement was valid. The constitutional policy of economic nationalism does not bar membership; sovereignty is limited by the country’s own treaty commitments, as with any treaty.')],
  url='https://www.wto.org/english/docs_e/legal_e/04-wto_e.htm')
t(id='ny-conv', area='Trade, investment and intellectual property', name='Convention on the Recognition and Enforcement of Foreign Arbitral Awards (New York Convention)', adopted='1958', ph='Acceded 1967', status='party',
  what='Courts must recognise arbitration agreements and enforce foreign arbitral awards, refusing only on the narrow grounds the Convention lists.', how='ADR Act of 2004 (RA 9285) and the Special Rules of Court on ADR (2009).', laws=[('ra9285', None, 'RA 9285 (ADR Act)'), ('ra876', None, 'RA 876 (Arbitration Law)')], cases=[], url='https://www.newyorkconvention.org/text')
t(id='apostille', area='Trade, investment and intellectual property', name='Hague Convention Abolishing the Requirement of Legalisation for Foreign Public Documents (Apostille Convention)', adopted='1961', ph='Acceded 2018; in force for the Philippines 14 May 2019', status='party',
  what='Replaces consular legalisation (“red ribbon”) with a single apostille certificate for public documents used between parties.', how='The Department of Foreign Affairs issues apostilles; the Rules on Evidence (2019) accommodate apostilled documents.', laws=[], cases=[], url='https://www.hcch.net/en/instruments/conventions/full-text/?cid=41')
t(id='madrid', area='Trade, investment and intellectual property', name='Madrid Protocol (international registration of marks), Paris Convention and Berne Convention', adopted='1883 / 1886 / 1989', ph='Paris and Berne: member since the mid-20th century. Madrid Protocol: acceded 2012', status='party',
  what='National treatment and priority for industrial property (Paris), copyright without formalities (Berne), and one application to register a mark in many countries (Madrid).', how='Intellectual Property Code (RA 8293).', laws=[('ipcode', None, 'IP Code (RA 8293)')],
  cases=[dict(n='Intellectual Property Association of the Philippines v. Ochoa', cite='G.R. No. 204605, July 19, 2016', held='Accession to the Madrid Protocol was an executive agreement implementing existing law and did not require Senate concurrence.')],
  url='https://www.wipo.int/treaties/en/registration/madrid_protocol/')
t(id='hague-children', area='Trade, investment and intellectual property', name='Hague Conventions on Intercountry Adoption (1993) and on International Child Abduction (1980)', adopted='1980 / 1993', ph='Intercountry Adoption: ratified 1996. Child Abduction: acceded 2016', status='party',
  what='Safeguards so intercountry adoptions serve the child’s best interests; prompt return of children wrongfully removed across borders.', how='Domestic and intercountry adoption under RA 11642 (2022) and the National Authority for Child Care.', laws=[('ra11642', None, 'RA 11642')], cases=[], url='https://www.hcch.net/en/instruments/conventions/full-text/?cid=69')
# ---------------------------------------------------------------- environment
t(id='climate', area='Environment', name='UN Framework Convention on Climate Change, Kyoto Protocol and Paris Agreement; Convention on Biological Diversity', adopted='1992 / 1997 / 2015', ph='UNFCCC ratified 1994; Kyoto 2003; Paris Agreement 2017; CBD 1993', status='party',
  what='Stabilise greenhouse gases; nationally determined contributions to keep warming well below 2°C (Paris); conserve biodiversity and share its benefits.', how='Climate Change Act (RA 9729, 2009), Clean Air Act (RA 8749), Ecological Solid Waste Management Act (RA 9003), and the expanded protected areas law.', laws=[('law', 'ra-9729', 'RA 9729 (Climate Change Act)'), ('ra8749', None, 'RA 8749 (Clean Air Act)'), ('ra9003', None, 'RA 9003')],
  cases=[dict(n='Oposa v. Factoran', cite='G.R. No. 101083, July 30, 1993', held='Minors, for themselves and for generations yet unborn, had standing to sue to stop timber licences; the right to a balanced and healthful ecology (Art. II, Sec. 16) is self-executing and judicially enforceable.')],
  url='https://unfccc.int/process-and-meetings/the-paris-agreement')
# ---------------------------------------------------------------- regional and bilateral security
t(id='asean', area='Regional and bilateral', name='ASEAN Charter', adopted='2007', ph='Ratified 2008', status='party',
  what='Gives ASEAN legal personality; principles of non-interference, consensus and peaceful settlement of disputes.', how='Executive and legislative measures on ASEAN integration.', laws=[], cases=[], url='https://asean.org/our-communities/asean-charter/')
t(id='mdt-vfa', area='Regional and bilateral', name='Mutual Defense Treaty with the United States (1951), Visiting Forces Agreement (1998) and EDCA (2014)', adopted='1951 / 1998 / 2014', ph='MDT signed 1951. VFA concurred in by the Senate in 1999. EDCA signed 2014 as an executive agreement', status='party',
  what='Mutual defence against armed attack in the Pacific; the legal status of visiting US forces; access to agreed locations in Philippine bases.',
  how='Foreign military bases, troops or facilities are not allowed except under a treaty concurred in by the Senate (Art. XVIII, Sec. 25).', laws=[('const1987', 'art-xviii-sec-25', 'Constitution, Art. XVIII, Sec. 25')],
  cases=[dict(n='Bayan v. Zamora', cite='G.R. No. 138570, October 10, 2000', held='The VFA is valid: it was concurred in by the Senate as a treaty, satisfying Art. XVIII, Sec. 25; that the United States treats it as an executive agreement does not matter.'),
         dict(n='Lim v. Executive Secretary', cite='G.R. No. 151445, April 11, 2002', held='The Balikatan exercises fall within the VFA’s “activities”, but US forces may not engage in combat on Philippine soil.'),
         dict(n='Nicolas v. Romulo', cite='G.R. No. 175888, February 11, 2009', held='The VFA is valid, but the agreements keeping a convicted US serviceman in US custody at the embassy did not conform to the VFA.'),
         dict(n='Saguisag v. Ochoa', cite='G.R. No. 212426, January 12, 2016', held='EDCA is a valid executive agreement: it implements the MDT and the VFA and does not allow new foreign bases, so it needed no separate Senate concurrence.')],
  url='https://avalon.law.yale.edu/20th_century/phil001.asp')
# ---------------------------------------------------------------- soft law and transformation
t(id='who-code', area='How international law enters Philippine law', name='International Code of Marketing of Breast-milk Substitutes (WHO, 1981)', adopted='1981', ph='Adopted by the World Health Assembly; transformed into law by the Milk Code (EO 51, 1986)', status='soft law',
  what='Restricts the marketing of breast-milk substitutes. A recommendation of the World Health Assembly, not a treaty.',
  how='Only the parts written into the Milk Code bind; WHA resolutions that were not transformed are soft law.', laws=[('milk', None, 'Milk Code (EO 51)')],
  cases=[dict(n='Pharmaceutical and Health Care Association of the Philippines v. Duque', cite='G.R. No. 173034, October 9, 2007', held='International law becomes part of domestic law by transformation (through legislation) or incorporation (generally accepted principles). The WHO Code was transformed by the Milk Code; later WHA resolutions were neither, so a rule based on them alone was void.')],
  url='https://www.who.int/publications/i/item/9241541601')

# links: ('<library code>', '<provision or None>', label) or ('law', '<statute id>', label)
for x in T:
    x['laws'] = [{'c': c, 'i': i, 't': l} for c, i, l in x['laws']]
out = {'built': 'treaties', 'treaties': T,
       'note': 'Registry in our own words. Ratification facts are given as a year unless an exact date was checked against a UN-system record. The treaty texts are not reproduced: open the official text from the depositary.'}
js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open('/home/claude/site/data/treaties.json', 'w').write(js)
cat = json.load(open('/home/claude/site/data/catalog.json'))
cat['thash'] = hashlib.md5(js.encode()).hexdigest()[:10]
json.dump(cat, open('/home/claude/site/data/catalog.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(T), 'treaties')
