import os, json

cats = [
    # 1. Health Access & Financial Protection (15)
    ('Health Access & Financial Protection', [
        ('Ayushman Bharat - PM-JAY', 'Cashless secondary & tertiary hospitalisation assurance up to ₹5 Lakh/family/year.', 'SECC 2011 identified vulnerable families & expanded beneficiary lists.', 'All genders', 'Assistance', 'National Health Authority (NHA)', 'https://aam.mohfw.gov.in/'),
        ('Employees State Insurance (ESI) Scheme', 'Comprehensive medical care, sickness & maternity benefits for insured workers.', 'Employees in covered establishments earning within notified wage limits.', 'All genders', 'Assistance', 'ESIC, Ministry of Labour & Employment', 'https://www.esic.gov.in/'),
        ('Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)', 'Access to quality generic medicines & surgicals at 50-90% lower prices.', 'General public & patients visiting Janaushadhi Kendras.', 'All genders', 'Health Service', 'Department of Pharmaceuticals', 'https://janaushadhi.gov.in/'),
        ('Central Government Health Scheme (CGHS)', 'Comprehensive medical care facility for central government employees & pensioners.', 'Central Govt employees, pensioners, dependents & designated beneficiaries.', 'All genders', 'Health Service', 'Ministry of Health & Family Welfare', 'https://cghs.nic.in/'),
        ('Ex-Servicemen Contributory Health Scheme (ECHS)', 'Cashless healthcare support for retired armed forces personnel & dependents.', 'Ex-servicemen, armed forces pensioners & eligible dependents.', 'All genders', 'Health Service', 'Department of ESW, Ministry of Defence', 'https://echs.gov.in/'),
        ('Ayushman Bharat Health Account (ABHA)', 'Unique 14-digit digital health ID linking medical records securely across India.', 'All Indian citizens with Aadhaar or mobile verification.', 'All genders', 'Digital Health', 'National Health Authority (NHA)', 'https://abha.abdm.gov.in/'),
        ('Rashtriya Swasthya Bima Yojana Transition Support', 'Residual health cover transition support for unorganized sector workers.', 'Enrolled unorganized sector families holding smart cards.', 'All genders', 'Assistance', 'MoHFW / NHA', 'https://pmjay.gov.in/'),
        ('Health Minister Discretionary Grant (HMDG)', 'Financial assistance up to ₹1.25 Lakh for poor patients suffering from major diseases.', 'Patients with annual family income up to ₹1.25 Lakh in government hospitals.', 'All genders', 'Assistance', 'Ministry of Health & Family Welfare', 'https://main.mohfw.gov.in/'),
        ('Rashtriya Arogya Nidhi (RAN)', 'One-time financial grant for super-specialty treatment in tertiary government hospitals.', 'Below Poverty Line (BPL) patients suffering from life-threatening diseases.', 'All genders', 'Assistance', 'Ministry of Health & Family Welfare', 'https://main.mohfw.gov.in/'),
        ('State Illness Assistance Fund (SIAF)', 'State-level financial aid for BPL patients requiring specialized hospital treatments.', 'State-notified BPL families seeking specialized medical care.', 'All genders', 'Assistance', 'State Health Departments / MoHFW', 'https://mohfw.gov.in/'),
        ('PM-JAY Senior Citizen Health Expansion', 'Additional ₹5 Lakh annual health insurance cover for all senior citizens aged 70+.', 'All senior citizens aged 70 years and above regardless of income.', 'All genders', 'Assistance', 'National Health Authority (NHA)', 'https://pmjay.gov.in/'),
        ('Ayushman Vaya Vandana Card Initiative', 'Dedicated healthcare card providing priority hospital care for elderly citizens.', 'Citizens aged 70+ enrolled under expanded PM-JAY.', 'All genders', 'Assistance', 'National Health Authority (NHA)', 'https://pmjay.gov.in/'),
        ('Building & Construction Workers Health Cover', 'Medical assistance and emergency health insurance for registered construction workers.', 'Registered BOCW workers with active state welfare board membership.', 'All genders', 'Assistance', 'State Building & Construction Boards', 'https://labour.gov.in/'),
        ('Beedi Workers Medical Welfare Scheme', 'Reimbursement for specialized medical treatment for beedi workers & families.', 'Registered beedi workers and their dependent family members.', 'All genders', 'Assistance', 'Welfare Commissionerate, Ministry of Labour', 'https://labour.gov.in/'),
        ('Cine Workers Health Care Scheme', 'Health checkups, hospitalisation aid & medicine supply for cine industry workers.', 'Registered cine workers holding valid identity cards.', 'All genders', 'Assistance', 'Ministry of Labour & Employment', 'https://labour.gov.in/')
    ]),

    # 2. Maternal & Reproductive Health (22)
    ('Maternal & Reproductive Health', [
        ('Pradhan Mantri Matru Vandana Yojana (PMMVY)', 'Direct maternity cash benefit of ₹5,000 for first child & ₹6,000 for second female child.', 'Eligible pregnant women & lactating mothers from disadvantaged groups.', 'Women', 'Assistance', 'Ministry of Women & Child Development', 'https://wcd.gov.in/'),
        ('Janani Suraksha Yojana (JSY)', 'Institutional delivery cash incentive up to ₹1,400 to promote safe hospital births.', 'Pregnant women delivering in public/accredited private health facilities.', 'Women', 'Assistance', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Janani Shishu Suraksha Karyakram (JSSK)', 'Zero out-of-pocket expenses for delivery, C-section, medicines & transport for mother & newborn.', 'All pregnant women & sick infants accessing public health institutions.', 'Women & Infants', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Surakshit Matritva Aash आश्वासन (SUMAN)', 'Guaranteed dignified, respectful, quality maternal healthcare at zero cost.', 'All pregnant women, mothers up to 6 months post-delivery & sick newborns.', 'Women', 'Health Service', 'Ministry of Health & Family Welfare', 'https://suman.nhp.gov.in/'),
        ('Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)', 'Free comprehensive antenatal care checkups by specialists on 9th of every month.', 'All pregnant women in their 2nd and 3rd trimesters.', 'Women', 'Health Service', 'MoHFW / NHM', 'https://pmsma.nhp.gov.in/'),
        ('LaQshya - Labour Room Quality Improvement', 'Ensures high quality clinical care & respectful maternity care during childbirth.', 'Pregnant women giving birth in government medical colleges & district hospitals.', 'Women', 'Health Service', 'Ministry of Health & Family Welfare', 'https://nhm.gov.in/'),
        ('Maternal & Child Health Wings (MCH Wings)', 'Dedicated multi-bed specialized maternal and child healthcare units at hospitals.', 'Pregnant women, mothers and newborns needing secondary/tertiary care.', 'Women & Children', 'Facility', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Maternal Death Surveillance & Response (MDSR)', 'Systematic tracking & review of maternal deaths to prevent future mortality.', 'Healthcare facilities & public health system tracking maternal outcomes.', 'Women', 'Programme', 'MoHFW', 'https://nhm.gov.in/'),
        ('Anaemia Mukt Bharat - Maternal Intervention', 'Prophylactic iron-folic acid supplementation & parenteral iron for pregnant women.', 'Pregnant and lactating women diagnosed with or at risk of anaemia.', 'Women', 'Health Service', 'NHM & POSHAN Abhiyaan', 'https://anaemiamuktbharat.info/'),
        ('State Maternity Assistance Schemes', 'State-supplemented financial support during late pregnancy to compensate wage loss.', 'Pregnant women enrolled in public health facilities.', 'Women', 'Assistance', 'State Health Departments', 'https://nhm.gov.in/'),
        ('National Family Planning Programme', 'Free contraceptive choices, post-partum IUCD & sterilization healthcare support.', 'Reproductive age couples seeking voluntary family planning options.', 'All genders', 'Health Service', 'MoHFW', 'https://nhm.gov.in/'),
        ('Mission Parivar Vikas', 'Enhanced access to contraceptives & family planning services in high fertility districts.', 'Couples in notified high-total fertility rate (TFR) districts.', 'All genders', 'Programme', 'Ministry of Health & Family Welfare', 'https://nhm.gov.in/'),
        ('Post-Partum Family Planning (PPFP)', 'Immediate post-delivery counseling and contraception services prior to hospital discharge.', 'Mothers giving birth in institutional delivery facilities.', 'Women', 'Health Service', 'NHM', 'https://nhm.gov.in/'),
        ('High Dependency Units (HDU) for Maternal Care', 'Specialized intensive nursing care for mothers with severe obstetric complications.', 'Pregnant or post-partum women experiencing life-threatening delivery risks.', 'Women', 'Facility', 'MoHFW / NHM', 'https://nhm.gov.in/'),
        ('Obstetric ICU Support Network', 'Dedicated intensive care beds for critically ill pregnant women.', 'Pregnant women requiring mechanical ventilation or advanced life support.', 'Women', 'Facility', 'Ministry of Health & Family Welfare', 'https://nhm.gov.in/'),
        ('Kangaroo Mother Care (KMC) Promotion', 'Skin-to-skin contact and exclusive breastfeeding guidance for low birthweight babies.', 'Mothers with premature or low birthweight newborns.', 'Women & Infants', 'Health Service', 'NHM / MoHFW', 'https://nhm.gov.in/'),
        ('Maternal Care Mobile Helpline (Kilkari)', 'Free weekly voice message updates on pregnancy care and infant health.', 'Pregnant women & families registered on RCH portal.', 'Women', 'Digital Health', 'MoHFW / NHM', 'https://nhm.gov.in/'),
        ('Mobile Academy for ASHA Maternal Training', 'Audio-based training course to empower ASHA workers in maternal health guidance.', 'ASHA community health workers.', 'All genders', 'Programme', 'MoHFW', 'https://nhm.gov.in/'),
        ('Targeted Antenatal Ultrasound Screening Initiative', 'Free basic obstetric ultrasonography for detecting fetal anomalies & twin births.', 'Pregnant women registered in primary health centres during 2nd trimester.', 'Women', 'Health Service', 'NHM', 'https://nhm.gov.in/'),
        ('Screening for Gestational Diabetes Mellitus (GDM)', 'Universal blood sugar testing for pregnant women to prevent birth complications.', 'All pregnant women visiting ANC clinics.', 'Women', 'Health Service', 'MoHFW / NHM', 'https://nhm.gov.in/'),
        ('Screening & Management of Syphilis in Pregnancy', 'Free rapid plasma reagin testing to prevent congenital syphilis in newborns.', 'All pregnant women during early antenatal care visits.', 'Women', 'Health Service', 'NACO & NHM', 'https://naco.gov.in/'),
        ('Calcium Supplementation in Pregnancy Initiative', 'Free 500mg daily calcium tablet distribution from 14 weeks of gestation.', 'All pregnant women to prevent pre-eclampsia and bone density loss.', 'Women', 'Health Service', 'NHM', 'https://nhm.gov.in/')
    ]),

    # 3. Newborn, Child & Adolescent Health (22)
    ('Newborn, Child & Adolescent Health', [
        ('Rashtriya Bal Swasthya Karyakram (RBSK)', 'Early screening & intervention for 4 Ds: Defects at birth, Diseases, Deficiencies & Development delays.', 'Children from birth to 18 years in government schools & Anganwadis.', 'Children & Adolescents', 'Health Service', 'Ministry of Health & Family Welfare', 'https://rbsk.gov.in/'),
        ('Rashtriya Kishor Swasthya Karyakram (RKSK)', 'Adolescent health counseling, nutrition support & iron-folic acid distribution.', 'Adolescents aged 10-19 years.', 'Adolescents', 'Programme', 'Ministry of Health & Family Welfare', 'https://nhm.gov.in/'),
        ('Special Newborn Care Units (SNCU)', 'Specialized tertiary care for sick & premature infants at district hospital level.', 'Newborn infants (0-28 days) requiring specialized medical intervention.', 'Infants', 'Facility', 'NHM / MoHFW', 'https://nhm.gov.in/'),
        ('Newborn Stabilization Units (NBSU)', 'Intermediate care units at Community Health Centres for stabilized sick newborns.', 'Sick newborns requiring oxygen therapy, phototherapy, or monitoring.', 'Infants', 'Facility', 'NHM', 'https://nhm.gov.in/'),
        ('Newborn Care Corners (NBCC)', 'Immediate resuscitation & thermal care at every delivery point in public facilities.', 'All newborns immediately after birth in public health institutions.', 'Infants', 'Facility', 'NHM', 'https://nhm.gov.in/'),
        ('Home Based Newborn Care (HBNC)', 'Structured home visits by ASHA workers to monitor infant growth & prevent sepsis.', 'All newborns and mothers visited within 42 days of delivery.', 'Infants', 'Health Service', 'NHM', 'https://nhm.gov.in/'),
        ('Home Based Care for Young Child (HBYC)', 'Extended ASHA home visits at 3, 6, 9, 12, and 15 months to promote child development.', 'Young children aged 3 to 15 months.', 'Children', 'Health Service', 'NHM', 'https://nhm.gov.in/'),
        ('Facility-Based Management of Severe Acute Malnutrition (FCTC / NRC)', 'Nutritional Rehabilitation Centres (NRC) providing specialized therapeutic food for SAM children.', 'Children aged 6-59 months diagnosed with Severe Acute Malnutrition (SAM).', 'Children', 'Facility', 'NHM & MWCD', 'https://nhm.gov.in/'),
        ('Infant & Young Child Feeding (IYCF) Promotion (MAA)', 'Mother’s Absolute Affection (MAA) campaign promoting early & exclusive breastfeeding.', 'Pregnant women, nursing mothers & infants up to 2 years.', 'Women & Infants', 'Programme', 'MoHFW', 'https://nhm.gov.in/'),
        ('National Deworming Day (NDD) Initiative', 'Bi-annual mass administration of Albendazole tablets to eliminate intestinal worms.', 'Children and adolescents aged 1-19 years.', 'Children & Adolescents', 'Health Service', 'MoHFW', 'https://nhm.gov.in/'),
        ('Adolescent Friendly Health Clinics (AFHC / Saathiya)', 'Dedicated non-judgmental counseling & medical services for adolescents.', 'Adolescents aged 10-19 years.', 'Adolescents', 'Facility', 'NHM', 'https://nhm.gov.in/'),
        ('Weekly Iron & Folic Acid Supplementation (WIFS)', 'Supervised weekly IFA tablet distribution & deworming for school students.', 'School-going boys and girls in classes 6 to 12 & out-of-school girls.', 'Adolescents', 'Health Service', 'NHM & MWCD', 'https://nhm.gov.in/'),
        ('Scheme for Promotion of Menstrual Hygiene (MHS)', 'Subsidized sanitary napkin distribution & awareness campaigns in rural areas.', 'Adolescent girls aged 10-19 years residing in rural areas.', 'Adolescents (Girls)', 'Health Service', 'MoHFW', 'https://nhm.gov.in/'),
        ('Childhood Diarrhoea Control (IDCF)', 'Intensified Diarrhoea Control Fortnight with free ORS packet & Zinc tablet distribution.', 'Children under 5 years of age.', 'Children', 'Health Service', 'MoHFW', 'https://nhm.gov.in/'),
        ('SAANS Campaign for Pneumonia Control', 'Social Awareness & Action to Neutralize Pneumonia Successfully in children under 5.', 'Infants and children under 5 years of age.', 'Children', 'Programme', 'MoHFW', 'https://nhm.gov.in/'),
        ('Paediatric ICU (PICU) Strengthening Scheme', 'Dedicated paediatric intensive care beds at medical colleges & district hospitals.', 'Critically ill children requiring intensive organ support.', 'Children', 'Facility', 'MoHFW', 'https://nhm.gov.in/'),
        ('Congenital Heart Disease (CHD) Screening', 'Pulse oximetry screening for early detection of congenital heart defects in newborns.', 'All newborns delivered in public hospitals before discharge.', 'Infants', 'Health Service', 'RBSK / NHM', 'https://rbsk.gov.in/'),
        ('Retinopathy of Prematurity (ROP) Screening', 'Ophthalmic screening for premature infants to prevent lifelong blindness.', 'Preterm infants born before 34 weeks or weighing under 2,000g.', 'Infants', 'Health Service', 'RBSK', 'https://rbsk.gov.in/'),
        ('Clubfoot Management & Rehabilitation Programme', 'Ponseti non-surgical correction method & free orthotic braces for infants.', 'Infants born with clubfoot deformity.', 'Infants', 'Health Service', 'RBSK', 'https://rbsk.gov.in/'),
        ('Early Intervention Centres (DEIC)', 'District Early Intervention Centres offering multi-disciplinary therapy for developmental delays.', 'Children aged 0-6 years with birth defects or development delays.', 'Children', 'Facility', 'RBSK / NHM', 'https://rbsk.gov.in/'),
        ('School Health & Wellness Programme (SHWP)', 'Health education, mental health guidance & life-skills sessions under Ayushman Bharat.', 'Students enrolled in government & government-aided schools.', 'Children & Adolescents', 'Programme', 'MoHFW & MoE', 'https://nhm.gov.in/'),
        ('Kangaroo Mother Care Corner Network', 'Dedicated hospital corners for continuous skin-to-skin contact for low birth weight infants.', 'Low birth weight infants and their mothers.', 'Infants', 'Facility', 'NHM', 'https://nhm.gov.in/')
    ]),

    # 4. Immunization, Nutrition & Preventive Health (15)
    ('Immunization, Nutrition & Preventive Health', [
        ('Universal Immunization Programme (UIP)', 'Free vaccination against 12 vaccine-preventable diseases across life stages.', 'All infants, children & pregnant women in India.', 'All genders', 'Health Service', 'Ministry of Health & Family Welfare', 'https://nhm.gov.in/'),
        ('Mission Indradhanush / Intensified Mission Indradhanush (IMI)', 'Targeted drive to reach unvaccinated & partially vaccinated children in remote areas.', 'Children up to 2 years & pregnant women missed in routine immunization.', 'Children & Women', 'Programme', 'MoHFW', 'https://nhm.gov.in/'),
        ('U-WIN Digital Immunization Platform', 'Real-time digital registry tracking child vaccinations and generating digital certificates.', 'Parents, guardians & healthcare providers across India.', 'All genders', 'Digital Health', 'Ministry of Health & Family Welfare', 'https://uwin.mohfw.gov.in/'),
        ('POSHAN Abhiyaan (National Nutrition Mission)', 'Multi-sectoral mission to eradicate stunting, wasting, anaemia & low birthweight.', 'Pregnant women, lactating mothers & children aged 0-6 years.', 'Women & Children', 'Programme', 'Ministry of Women & Child Development', 'https://poshanabhiyaan.gov.in/'),
        ('PM POSHAN (Mid-Day Meal Scheme)', 'Nutritious hot cooked meal provided daily in schools to boost child health & attendance.', 'Students studying in primary & upper primary classes in public schools.', 'Children', 'Assistance', 'Ministry of Education', 'https://pmposhan.education.gov.in/'),
        ('POSHAN 2.0 Integrated Nutrition Support', 'Strengthening Anganwadi services for supplementary nutrition & early childhood care.', 'Children aged 6 months to 6 years, pregnant women & adolescent girls.', 'Women & Children', 'Programme', 'Ministry of Women & Child Development', 'https://wcd.gov.in/'),
        ('Anaemia Mukt Bharat (AMB) Strategy', '6x6x6 strategy providing iron-folic acid prophylaxis & deworming to 6 target groups.', 'Children, adolescents, women of reproductive age & pregnant women.', 'All genders', 'Programme', 'MoHFW & POSHAN', 'https://anaemiamuktbharat.info/'),
        ('National Vitamin A Prophylaxis Programme', 'Mass oral Vitamin A syrup administration every 6 months to prevent child blindness.', 'Children aged 9 months to 5 years.', 'Children', 'Health Service', 'NHM', 'https://nhm.gov.in/'),
        ('National Iodine Deficiency Disorders Control Programme (NIDDCP)', 'Promotion of iodized salt consumption to prevent goitre, cretinism & mental impairment.', 'General population across all states & UTs.', 'All genders', 'Programme', 'Ministry of Health & Family Welfare', 'https://main.mohfw.gov.in/'),
        ('Eat Right India Movement', 'FSSAI led initiative promoting safe, healthy & fortified food consumption habits.', 'General public, food vendors & consumer groups.', 'All genders', 'Programme', 'FSSAI', 'https://eatrightindia.gov.in/'),
        ('Food Fortification Resource Centre (FFRC) Drive', 'Mandatory fortification of staple foods with iron, folic acid, vitamin A & D.', 'Consumer food supply, PDS beneficiaries & school lunch schemes.', 'All genders', 'Programme', 'FSSAI & MoHFW', 'https://ffrc.fssai.gov.in/'),
        ('Fit India Movement - Health & Physical Fitness', 'National wellness campaign encouraging daily physical activity & healthy lifestyle choices.', 'Citizens of all age groups.', 'All genders', 'Programme', 'Ministry of Youth Affairs & Sports', 'https://fitindia.gov.in/'),
        ('Ayushman Arogya Mandir Wellness Activities', 'Free yoga sessions, health screening & wellness lifestyle education at primary centers.', 'Community members visiting Ayushman Arogya Mandirs.', 'All genders', 'Health Service', 'Ministry of Health & Family Welfare', 'https://aam.mohfw.gov.in/'),
        ('Human Papillomavirus (HPV) Cervical Cancer Prevention', 'Targeted HPV vaccination drives to prevent cervical cancer in young girls.', 'Adolescent girls aged 9-14 years.', 'Adolescents (Girls)', 'Health Service', 'MoHFW', 'https://nhm.gov.in/'),
        ('Pneumococcal Conjugate Vaccine (PCV) Rollout', 'Free PCV vaccine inclusion under UIP to prevent severe pneumonia & meningitis.', 'All infants at 6 weeks, 14 weeks and booster at 9 months.', 'Infants', 'Health Service', 'NHM', 'https://nhm.gov.in/')
    ]),

    # 5. Communicable Disease Control (29)
    ('Communicable Disease Control', [
        ('National Tuberculosis Elimination Programme (NTEP)', 'Free TB diagnosis, CBNAAT testing, anti-TB drug regimens & nutritional support.', 'All individuals with suspected or diagnosed Tuberculosis.', 'All genders', 'Programme', 'Central TB Division, MoHFW', 'https://nikshay.in/'),
        ('Nikshay Poshan Yojana', 'Direct benefit transfer of ₹500/month to all notified TB patients during treatment.', 'All active TB patients registered on the Nikshay portal.', 'All genders', 'Assistance', 'Ministry of Health & Family Welfare', 'https://nikshay.in/'),
        ('Nikshay Mitra Initiative (Community Support for TB)', 'Community adoption of TB patients providing nutritional baskets, diagnostic & vocational support.', 'Diagnosed TB patients undergoing active treatment.', 'All genders', 'Programme', 'MoHFW', 'https://communitysupport.nikshay.in/'),
        ('National Vector Borne Disease Control Programme (NVBDCP)', 'Free testing, bed net distribution & treatment for Malaria, Dengue, Chikungunya & Kala-Azar.', 'General public in high-endemic districts & vector prone areas.', 'All genders', 'Programme', 'Directorate of NVBDCP, MoHFW', 'https://nvbdcp.gov.in/'),
        ('National AIDS Control Programme (NACP Phase V)', 'Free HIV counseling, viral load testing, antiretroviral therapy (ART) & STI care.', 'People living with HIV (PLHIV) & key vulnerable populations.', 'All genders', 'Programme', 'National AIDS Control Organisation (NACO)', 'https://naco.gov.in/'),
        ('National Viral Hepatitis Control Programme (NVHCP)', 'Free screening, viral load testing & direct-acting antiviral (DAA) medicines for Hepatitis B & C.', 'General population & patients diagnosed with Hepatitis B or C.', 'All genders', 'Programme', 'MoHFW', 'https://nvhcp.mohfw.gov.in/'),
        ('National Leprosy Eradication Programme (NLEP)', 'Free Multi-Drug Therapy (MDT), disability prevention & reconstructive surgery grants.', 'Leprosy affected persons and family contacts.', 'All genders', 'Programme', 'Directorate General of Health Services', 'https://nlep.nic.in/'),
        ('National Rabies Control Programme (NRCP)', 'Free anti-rabies vaccine & rabies immunoglobulin administration at public hospitals.', 'Persons exposed to animal bites or suspected rabies infection.', 'All genders', 'Health Service', 'National Centre for Disease Control (NCDC)', 'https://ncdc.gov.in/'),
        ('National Centre for Disease Control (NCDC) Surveillance', 'Real-time epidemic intelligence, outbreak monitoring & public health response.', 'General public & healthcare system across India.', 'All genders', 'Programme', 'NCDC, MoHFW', 'https://ncdc.gov.in/'),
        ('Integrated Disease Surveillance Programme (IDSP / IHIP)', 'Digital disease surveillance portal tracking weekly outbreaks of infectious diseases.', 'Public health authorities & citizens.', 'All genders', 'Digital Health', 'NCDC & MoHFW', 'https://ihip.nhp.gov.in/'),
        ('National One Health Mission for Pandemics', 'Inter-disciplinary surveillance monitoring zoonotic diseases transmitted from animals to humans.', 'General public & agricultural/livestock communities.', 'All genders', 'Programme', 'Office of PSA & MoHFW', 'https://psa.gov.in/'),
        ('National Malaria Elimination Framework', 'Targeted indoor residual spraying, rapid diagnostic tests & Artemisinin combination therapy.', 'Population residing in malaria-endemic rural & tribal areas.', 'All genders', 'Programme', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Kala-Azar Elimination Programme', 'Single-dose Liposomal Amphotericin B treatment & financial compensation during recovery.', 'Patients diagnosed with Visceral Leishmaniasis (Kala-Azar).', 'All genders', 'Programme', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Lymphatic Filariasis Elimination (MDA Drive)', 'Annual Mass Drug Administration of DEC, Albendazole & Ivermectin in endemic districts.', 'Residents in filariasis endemic districts except children under 2.', 'All genders', 'Programme', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Japanese Encephalitis (JE) Control Initiative', 'JE vaccination drives, acute encephalitis syndrome (AES) care & vector control.', 'Children in endemic districts across 15 states.', 'Children', 'Programme', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Kyasanur Forest Disease (KFD) Response', 'Targeted vaccination & tick control measures in forest-bordering districts.', 'Forest workers & residents in KFD endemic Western Ghats districts.', 'All genders', 'Programme', 'NCDC & State Health Depts', 'https://ncdc.gov.in/'),
        ('Scrub Typhus Diagnostic & Care Drive', 'Free Weil-Felix testing & Doxycycline treatment at primary healthcare centers.', 'Rural patients presenting with acute fever & eschar lesions.', 'All genders', 'Health Service', 'NCDC', 'https://ncdc.gov.in/'),
        ('National Acute Respiratory Infection (ARI) Surveillance', 'Influenza-like illness (ILI) & Severe Acute Respiratory Infection (SARI) sentinel monitoring.', 'Patients presenting with acute respiratory distress at sentinel hospitals.', 'All genders', 'Programme', 'NCDC & ICMR', 'https://ncdc.gov.in/'),
        ('Antimicrobial Resistance (AMR) Containment Programme', 'Regulation of over-the-counter antibiotic sales & hospital infection control guidelines.', 'General public & healthcare facilities.', 'All genders', 'Programme', 'NCDC & FSSAI', 'https://ncdc.gov.in/'),
        ('COVID-19 Follow-up & Long-COVID Care Protocol', 'Post-COVID rehabilitation clinics & pulmonary care support at district hospitals.', 'Patients suffering from persistent post-viral respiratory/cardiac symptoms.', 'All genders', 'Health Service', 'MoHFW', 'https://mohfw.gov.in/'),
        ('Trachoma Elimination & Eye Health Initiative', 'Surgical interventions & antibiotic treatment maintaining India’s trachoma-free status.', 'Communities in endemic areas & school children.', 'All genders', 'Health Service', 'NPCBVI & MoHFW', 'https://npcbvi.gov.in/'),
        ('Yaws Eradication & Verification Maintenance', 'Continued surveillance ensuring non-recurrence of Yaws skin lesions in tribal pockets.', 'Tribal populations in previously endemic states.', 'All genders', 'Programme', 'NCDC', 'https://ncdc.gov.in/'),
        ('Waterborne Disease Outbreak Control (Diarrhoea & Cholera)', 'Safe water testing kits, super-chlorination of public wells & rapid medical teams.', 'Rural and urban slum communities during monsoon months.', 'All genders', 'Health Service', 'IDSP & NCDC', 'https://ncdc.gov.in/'),
        ('Dengue & Chikungunya Integrated Management', 'Free ELISA NS1 testing, vector breeding control & platelet management protocols.', 'Patients presenting with high fever & joint pain.', 'All genders', 'Health Service', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Prevention of Parent-to-Child Transmission (PPTCT) of HIV', 'Universal triple ART prophylaxis for HIV positive pregnant women to protect babies.', 'HIV-positive pregnant women and exposed infants.', 'Women & Infants', 'Health Service', 'NACO', 'https://naco.gov.in/'),
        ('Syphilis Elimination Drive under NACO', 'Dual HIV/Syphilis rapid point-of-care testing during antenatal visits.', 'Pregnant women accessing antenatal checkups.', 'Women', 'Health Service', 'NACO', 'https://naco.gov.in/'),
        ('National Filarial Morbidity Management (MMDP)', 'Free hydrocele surgeries & lymphedema washing kit distribution for filariasis patients.', 'Individuals suffering from elephantiasis or hydrocele.', 'All genders', 'Health Service', 'NVBDCP', 'https://nvbdcp.gov.in/'),
        ('Tuberculosis Preventive Treatment (TPT)', 'Short-course preventive therapy (3HP/6H) for high-risk household contacts of TB patients.', 'Household contacts & immunosuppressed individuals.', 'All genders', 'Programme', 'NTEP', 'https://nikshay.in/'),
        ('National Viral Hepatitis B Immunization Drive', 'Zero-dose Hepatitis B vaccination given within 24 hours of birth to all newborns.', 'All newborns delivered in institutional health facilities.', 'Infants', 'Health Service', 'UIP & NVHCP', 'https://nhm.gov.in/')
    ]),

    # 6. Non-Communicable, Mental Health & Geriatric Care (19)
    ('Non-Communicable, Mental Health & Geriatric Care', [
        ('National Programme for Prevention & Control of NCDs (NPNCD)', 'Free population screening for Diabetes, Hypertension & 3 common cancers (Oral, Breast, Cervical).', 'All adults aged 30 years and above.', 'All genders', 'Programme', 'Directorate General of Health Services', 'https://main.mohfw.gov.in/'),
        ('Tele-MANAS (Mental Health Assistance Network)', 'Free 24/7 tele-mental health counseling helpline (14416 / 1800-891-4416) in 20 languages.', 'Anyone experiencing stress, anxiety, depression or mental distress.', 'All genders', 'Digital Health', 'Ministry of Health & Family Welfare', 'https://telemanas.mohfw.gov.in/'),
        ('National Mental Health Programme (NMHP)', 'District Mental Health Units offering outpatient psychiatric care & counseling.', 'Persons suffering from mental health disorders & emotional distress.', 'All genders', 'Programme', 'MoHFW', 'https://main.mohfw.gov.in/'),
        ('National Programme for Health Care of the Elderly (NPHCE)', 'Dedicated geriatric clinics, weekly OPDs & free medicines for senior citizens.', 'Senior citizens aged 60 years and above.', 'Elderly', 'Health Service', 'Directorate General of Health Services', 'https://main.mohfw.gov.in/'),
        ('National Programme for Control of Cancer, Diabetes, CVDs & Stroke', 'Community screening, free essential NCD drugs & referral to tertiary care.', 'Adults aged 30+ visiting primary health centers.', 'All genders', 'Programme', 'MoHFW', 'https://main.mohfw.gov.in/'),
        ('National Programme for Control of Blindness & Visual Impairment (NPCBVI)', 'Free cataract surgeries, spectacle distribution for school children & corneal transplantation.', 'General public with visual impairment, especially elderly & students.', 'All genders', 'Health Service', 'MoHFW', 'https://npcbvi.gov.in/'),
        ('National Oral Health Programme (NOHP)', 'Free dental checkups, tooth extraction, cavity filling & oral cancer screening.', 'General public accessing public health facilities.', 'All genders', 'Health Service', 'MoHFW', 'https://nohp.mohfw.gov.in/'),
        ('National Tobacco Control Programme (NTCP)', 'Tobacco cessation centers, counseling helpline (1800-11-2356) & COTPA enforcement.', 'Tobacco users seeking cessation support.', 'All genders', 'Programme', 'MoHFW', 'https://ntcp.mohfw.gov.in/'),
        ('Pradhan Mantri National Dialysis Programme (PMNDP)', 'Free hemodialysis & peritoneal dialysis services for BPL chronic kidney disease patients.', 'BPL patients suffering from End-Stage Renal Disease (ESRD).', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('National Programme for Prevention & Management of Trauma & Burn Injuries', 'Dedicated trauma care centers on major national highways & specialized burn units.', 'Victims of road traffic accidents & severe burn injuries.', 'All genders', 'Facility', 'MoHFW', 'https://main.mohfw.gov.in/'),
        ('National Programme for Prevention & Control of Deafness (NPPCD)', 'Early hearing screening in newborns, free hearing aids & cochlear implant support.', 'Infants, children & adults suffering from hearing impairment.', 'All genders', 'Health Service', 'MoHFW', 'https://main.mohfw.gov.in/'),
        ('National Palliative Care Programme (NPPC)', 'Home-based palliative care, morphine availability & pain relief for terminally ill patients.', 'Patients suffering from advanced cancer, end-stage organ failure or ALS.', 'All genders', 'Health Service', 'MoHFW', 'https://main.mohfw.gov.in/'),
        ('Cardiovascular Disease Prevention & Care Drive', 'Free statins, anti-hypertensives & ECG screening at primary healthcare centers.', 'Adults diagnosed with stage 1 & 2 hypertension or high cholesterol.', 'All genders', 'Health Service', 'NPNCD', 'https://main.mohfw.gov.in/'),
        ('Cervical Cancer Screening & Cryotherapy', 'Visual Inspection with Acetic Acid (VIA) screening & immediate cryotherapy at PHCs.', 'Women aged 30-65 years.', 'Women', 'Health Service', 'NPNCD & NHM', 'https://main.mohfw.gov.in/'),
        ('Breast Cancer Early Detection Drive', 'Clinical breast examination by trained female nurses & free mammography referrals.', 'Women aged 30 years and above.', 'Women', 'Health Service', 'NPNCD', 'https://main.mohfw.gov.in/'),
        ('Oral Cancer Screening Initiative', 'Oral visual examination for leukoplakia & erythroplakia during NCD screening.', 'Adults aged 30+ with a history of tobacco/areca nut use.', 'All genders', 'Health Service', 'NPNCD & NOHP', 'https://main.mohfw.gov.in/'),
        ('National Stroke Care & Thrombolysis Protocol', 'Rapid CT scan access & free Tissue Plasminogen Activator (tPA) injections at district hospitals.', 'Acute ischemic stroke patients arriving within 4.5 hours of symptom onset.', 'All genders', 'Facility', 'NPNCD', 'https://main.mohfw.gov.in/'),
        ('Geriatric Respite & Home Care Initiative', 'Trained home care caregivers visiting bedridden senior citizens for physiotherapy & wound management.', 'Bedridden or severely frail senior citizens aged 75+.', 'Elderly', 'Health Service', 'NPHCE', 'https://main.mohfw.gov.in/'),
        ('Childhood Cancer Financial Support (RAN Cancer Fund)', 'Financial assistance up to ₹15 Lakh for BPL children undergoing cancer treatment.', 'BPL children diagnosed with leukemia, lymphoma, or solid tumors.', 'Children', 'Assistance', 'Rashtriya Arogya Nidhi, MoHFW', 'https://main.mohfw.gov.in/')
    ]),

    # 7. Disability, Rehabilitation & Assistive Care (8)
    ('Disability, Rehabilitation & Assistive Care', [
        ('Assistance to Disabled Persons for Purchase/Fitting of Aids (ADIP)', 'Free distribution of modern wheelchair, tri-cycles, hearing aids & prosthetics.', 'Persons with Disabilities (PwD) with benchmark disability of 40% and above.', 'All genders', 'Assistance', 'DEPwD, Ministry of Social Justice', 'https://adip.disabilityaffairs.gov.in/'),
        ('Rashtriya Vayoshri Yojana (RVY)', 'Free physical aids & assisted living devices for senior citizens suffering from age ailments.', 'Senior citizens belonging to BPL category or monthly income under ₹15,000.', 'Elderly', 'Assistance', 'ALIMCO / Ministry of Social Justice', 'https://disabilityaffairs.gov.in/'),
        ('Unique Disability ID (UDID) Card', 'National unified disability card granting access to healthcare & welfare concessions across India.', 'Persons with benchmark disability certified by medical authorities.', 'All genders', 'Digital Health', 'Department of Empowerment of PwD', 'https://www.swavlambancard.gov.in/'),
        ('District Disability Rehabilitation Centres (DDRC)', 'Comprehensive rehabilitation services including physiotherapy, occupational therapy & limb fitting.', 'Persons with disabilities living in rural & semi-urban districts.', 'All genders', 'Facility', 'DEPwD', 'https://disabilityaffairs.gov.in/'),
        ('Deendayal Disabled Rehabilitation Scheme (DDRS)', 'Grants-in-aid to NGOs running special schools, vocational training & early intervention centers.', 'Children & adults with intellectual, visual, or physical disabilities.', 'All genders', 'Programme', 'Ministry of Social Justice & Empowerment', 'https://disabilityaffairs.gov.in/'),
        ('Cochlear Implant Assistance under ADIP', 'Full financial support up to ₹6 Lakh for cochlear implant surgery in young children.', 'Profoundly deaf children under 5 years of age from low-income families.', 'Children', 'Assistance', 'DEPwD & ALIMCO', 'https://adip.disabilityaffairs.gov.in/'),
        ('National Spinal Cord Injury Rehabilitation Protocol', 'Specialized inpatient rehabilitation, bladder management & assistive devices for spinal injury patients.', 'Persons suffering from paraplegia or quadriplegia due to trauma.', 'All genders', 'Facility', 'Indian Spinal Injuries Centre & DEPwD', 'https://disabilityaffairs.gov.in/'),
        ('Artificial Limbs Manufacturing Corporation (ALIMCO) Camp Drive', 'Mass fitment camps manufacturing customized orthotic & prosthetic limbs.', 'Amputees & orthopedically impaired citizens.', 'All genders', 'Health Service', 'ALIMCO', 'https://alimco.in/')
    ]),

    # 8. AYUSH & Traditional Healthcare (10)
    ('AYUSH & Traditional Healthcare', [
        ('National AYUSH Mission (NAM)', 'Integration of Ayurveda, Yoga, Unani, Siddha & Homoeopathy services into public health.', 'General public seeking holistic & traditional healthcare options.', 'All genders', 'Programme', 'Ministry of AYUSH', 'https://nam.ayush.gov.in/'),
        ('AYUSH Health & Wellness Centres (AHWCs)', 'Upgraded primary healthcare centers providing AYUSH consultations, herbal gardens & yoga.', 'Community members seeking preventive wellness & traditional therapies.', 'All genders', 'Facility', 'Ministry of AYUSH', 'https://ayushnext.ayush.gov.in/'),
        ('Central Council for Research in Ayurvedic Sciences (CCRAS) Clinics', 'Specialized Ayurvedic OPDs for arthritis, skin disorders & metabolic health.', 'Patients seeking validated Ayurvedic treatment protocols.', 'All genders', 'Health Service', 'CCRAS, Ministry of AYUSH', 'https://ccras.nic.in/'),
        ('Central Council for Research in Homoeopathy (CCRH) Clinics', 'Homoeopathic clinical care for chronic pediatric, respiratory & allergic conditions.', 'General public seeking homoeopathic consultations & remedies.', 'All genders', 'Health Service', 'CCRH, Ministry of AYUSH', 'https://ccrhindia.nic.in/'),
        ('Central Council for Research in Unani Medicine (CCRUM) Clinics', 'Unani clinical care specializing in musculoskeletal, liver & dermatological ailments.', 'Patients seeking Unani system of medicine consultations.', 'All genders', 'Health Service', 'CCRUM, Ministry of AYUSH', 'https://ccrum.res.in/'),
        ('National Institute of Siddha (NIS) Healthcare Facility', 'Specialized Siddha system clinical care for chronic joint pain, skin & lifestyle conditions.', 'General public seeking authentic Siddha medical treatments.', 'All genders', 'Facility', 'NIS, Ministry of AYUSH', 'https://nissiddha.ac.in/'),
        ('National Institute of Naturopathy (NIN) Services', 'Drugless therapies, hydrotherapy, mud therapy & dietetics for chronic disease management.', 'Citizens seeking naturopathic lifestyle modification.', 'All genders', 'Facility', 'NIN, Ministry of AYUSH', 'https://punenin.ayush.gov.in/'),
        ('AYUSH Gram Initiative', 'Selection of villages for total health adoption through AYUSH lifestyle & medicinal plants.', 'Rural residents in selected AYUSH Gram villages.', 'All genders', 'Programme', 'Ministry of AYUSH', 'https://nam.ayush.gov.in/'),
        ('AYUSH Senior Citizen Healthcare Drive (Vayoshrestha AYUSH)', 'Specialized geriatric care camps utilizing Rasayana therapy & Panchakarma.', 'Senior citizens aged 60 years and above.', 'Elderly', 'Health Service', 'Ministry of AYUSH', 'https://ayush.gov.in/'),
        ('AYUSH Anaemia Control Programme (Raktavardhak)', 'Ayurvedic formulations (Punarnavadi Mandoor & Dhatri Lauha) for anaemia correction.', 'Anaemic adolescent girls and women of childbearing age.', 'Women & Adolescents', 'Health Service', 'Ministry of AYUSH', 'https://ayush.gov.in/')
    ]),

    # 9. Health Systems, Emergency & Digital Health (16)
    ('Health Systems, Emergency & Digital Health', [
        ('Ayushman Bharat Digital Mission (ABDM)', 'Creating an interoperable digital health ecosystem linking hospitals, labs & ABHA IDs.', 'All citizens, healthcare providers & health facilities.', 'All genders', 'Digital Health', 'National Health Authority (NHA)', 'https://abdm.gov.in/'),
        ('eSanjeevani Tele-consultation Service (eSanjeevaniOPD & HWC)', 'Free doctor-to-doctor & patient-to-doctor tele-consultations from home or local PHC.', 'All citizens seeking general or specialist medical advice remotely.', 'All genders', 'Digital Health', 'Ministry of Health & Family Welfare', 'https://esanjeevani.mohfw.gov.in/'),
        ('PM Ayushman Bharat Health Infrastructure Mission (PM-ABHIM)', 'Strengthening urban/rural health centers, critical care blocks & disease surveillance labs.', 'General population across all districts in India.', 'All genders', 'Programme', 'Ministry of Health & Family Welfare', 'https://pmabhim.mohfw.gov.in/'),
        ('National Ambulance Services (108 / 102 Emergency Response)', 'Free emergency toll-free ambulance transport for trauma, deliveries & acute illness.', 'Anyone requiring medical transport to nearby health facilities.', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Free Essential Drugs Service Initiative', 'Mandatory zero-cost supply of notified essential medicines in all public hospitals.', 'All patients visiting government primary, secondary & tertiary facilities.', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Free Essential Diagnostics Service Initiative', 'Zero-cost pathology tests, X-ray, ECG & CT scan facilities in public institutions.', 'Patients attending government hospitals & clinics.', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Blood Bank & e-RaktKosh Digital Portal', 'Real-time blood stock availability tracking & voluntary blood donor registration.', 'Patients requiring urgent blood transfusion & voluntary donors.', 'All genders', 'Digital Health', 'Ministry of Health & Family Welfare', 'https://eraktkosh.in/'),
        ('Organ Donation & NOTTO Registry', 'National registry facilitating organ allocation, donor pledge & transplant coordination.', 'Patients requiring kidney, liver, heart or corneal transplants.', 'All genders', 'Digital Health', 'National Organ & Tissue Transplant Organisation', 'https://notto.mohfw.gov.in/'),
        ('Critical Care Blocks (CCB) under PM-ABHIM', 'Dedicated 50-bed critical care units built in every district hospital for emergencies.', 'Patients experiencing acute respiratory distress, sepsis or severe trauma.', 'All genders', 'Facility', 'MoHFW', 'https://pmabhim.mohfw.gov.in/'),
        ('Integrated Public Health Laboratories (IPHL)', 'District-level multi-disciplinary diagnostic labs combining microbiology, pathology & biochemistry.', 'General public requiring specialized diagnostic investigations.', 'All genders', 'Facility', 'PM-ABHIM & MoHFW', 'https://pmabhim.mohfw.gov.in/'),
        ('Urban Health & Wellness Centres (U-HWC)', 'Primary healthcare clinics providing comprehensive outpatient care in urban slums.', 'Urban poor & slum dwellers.', 'All genders', 'Facility', 'National Urban Health Mission (NUHM)', 'https://nhm.gov.in/'),
        ('ASHA Worker Community Support System', 'Trained female community health activists bridging rural households with health centers.', 'Rural households across all Indian villages.', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('Mobile Medical Units (MMU)', 'Fully equipped healthcare vans bringing doctors, diagnostic tests & medicines to remote hamlets.', 'Tribal, hilly & hard-to-reach unserved populations.', 'All genders', 'Health Service', 'National Health Mission (NHM)', 'https://nhm.gov.in/'),
        ('National Emergency Medical Services (NEMS) Protocol', 'Standardized triage & resuscitation training for emergency room casualty staff.', 'Emergency room patients.', 'All genders', 'Programme', 'MoHFW', 'https://mohfw.gov.in/'),
        ('Health Management Information System (HMIS)', 'Centralized health data repository capturing facility service delivery indicators.', 'Public health administrators & policy planners.', 'All genders', 'Digital Health', 'Ministry of Health & Family Welfare', 'https://hmis.mohfw.gov.in/'),
        ('Emergency Relief & Disaster Medical Response', 'Rapid deployment medical teams & field hospital tents during floods, earthquakes or disasters.', 'Disaster affected populations.', 'All genders', 'Health Service', 'Emergency Medical Relief (EMR), MoHFW', 'https://mohfw.gov.in/')
    ])
]

schemes_list = []
total_count = 0

for cat_name, items in cats:
    for idx, item in enumerate(items, 1):
        total_count += 1
        slug = item[0].lower().replace(' ', '-').replace('(', '').replace(')', '').replace('&', 'and').replace('/', '-').replace(',', '').replace('\'', '')
        s_id = f'{cat_name[:3].lower()}-{idx:03d}-{slug[:25]}'
        schemes_list.append({
            'id': s_id,
            'title': item[0],
            'category': cat_name,
            'shortDescription': item[1],
            'keyBenefits': item[1],
            'eligibilityCriteria': [item[2]] if isinstance(item[2], str) else item[2],
            'genderEligible': item[3],
            'type': item[4],
            'officialSource': item[5],
            'sourceUrl': item[6],
            'benefitAmount': 'Free Healthcare' if item[4] != 'Assistance' else 'Direct Aid / Cover',
            'status': 'Eligible',
            'isEnrolled': False
        })

print(f'Total schemes generated: {total_count}')

out_code = f'''// Complete Health Schemes Corpus (156 Government of India Health Programmes)
export const SCHEMES_DATA = {json.dumps(schemes_list, indent=2)};

export const getLocalizedSchemes = (t) => {{
  return SCHEMES_DATA.map(scheme => ({{
    ...scheme,
    status: t("common.eligible")
  }}));
}};

export const getSchemes = (filterCategory = "All", searchQuery = "", t = null) => {{
  const schemes = t ? getLocalizedSchemes(t) : SCHEMES_DATA;
  return schemes.filter(scheme => {{
    const matchesCategory = 
      filterCategory === "All" || 
      filterCategory === "அனைத்தும்" || 
      filterCategory === "सभी" || 
      scheme.category.toLowerCase() === filterCategory.toLowerCase();

    const query = searchQuery ? searchQuery.toLowerCase().trim() : "";
    const matchesSearch = !query || 
      scheme.title.toLowerCase().includes(query) ||
      scheme.shortDescription.toLowerCase().includes(query) ||
      scheme.category.toLowerCase().includes(query) ||
      scheme.genderEligible.toLowerCase().includes(query);

    return matchesCategory && matchesSearch;
  }});
}};

export const getSchemeById = (id, t = null) => {{
  const schemes = t ? getLocalizedSchemes(t) : SCHEMES_DATA;
  if (!id) return schemes[0];
  const found = schemes.find(s => s.id === id || s.id.includes(id));
  return found || schemes[0];
}};
'''

with open('src/services/schemeService.js', 'w', encoding='utf-8') as f:
    f.write(out_code)

print('Saved src/services/schemeService.js successfully!')
