You are collaborating with `agy-ca-neet` (Antigravity) to build the **Tamil Nadu CA (Chartered Accountant) Mastery Hub** in `/Users/thameema/git/ca-prep`.

Your task is to create and execute `/Users/thameema/git/ca-prep/scripts/build_ca_question_bank.py` so that it generates four files in `/Users/thameema/git/ca-prep/`:
1. `questions_bank.json`
2. `questions_database.js` (`window.CA_QUESTION_BANK = ...; window.NEET_QUESTION_BANK = window.CA_QUESTION_BANK;`)
3. `past_papers_archive.json`
4. `past_papers_database.js` (`window.CA_PAST_PAPERS_ARCHIVE = ...; window.NEET_PAST_PAPERS_ARCHIVE = window.CA_PAST_PAPERS_ARCHIVE;`)

### Exact Schema Requirements (Must match the frontend & server expectations!)

#### A. `questions_bank.json`
- `"metadata"`:
  - `"exam"`: `"ICAI Chartered Accountancy (New Scheme — Foundation, Intermediate, Final & SPOM)"`
  - `"region"`: `"Tamil Nadu (SIRC of ICAI — Bilingual English + Tamil Explanations)"`
  - `"totalQuestionsInBank"`: total count (generate at least 90–120 rich, authentic, mathematically & statutorily verified questions across the 4 subject/level buckets)
  - `"subjectCounts"`: object mapping the 4 primary level buckets used by the filter pills:
    - `"CA Foundation"`: count (at least 25 Qs covering Paper 1 Accounting, Paper 2 Business Laws, Paper 3 Quantitative Aptitude, Paper 4 Business Economics)
    - `"CA Inter G1"`: count (at least 25 Qs covering Paper 1 Advanced Accounting, Paper 2 Corporate & Other Laws, Paper 3 Taxation - Income Tax AY 2026-27 & GST)
    - `"CA Inter G2"`: count (at least 20 Qs covering Paper 4 Cost & Management Accounting, Paper 5 Auditing & Ethics, Paper 6 Financial Management & Strategic Management)
    - `"CA Final & SPOM"`: count (at least 25 Qs covering Paper 1 FR Ind AS, Paper 2 AFM, Paper 3 Advanced Auditing & Ethics, Paper 4 Direct Tax & Intl Tax, Paper 5 Indirect Tax GST/Customs, Paper 6 IBS Multidisciplinary Case Study, and SPOM Sets A/B IBC 2016, SEBI, SCMPE)
  - `"markingScheme"`: `{"correct": 2, "incorrect": -0.25, "unanswered": 0, "fullExamMaxMarks": 100, "paperMinPassPct": 40, "groupAggregatePassPct": 50, "exemptionPct": 60}`
- `"modules"`: dictionary of practice & mock modules, including:
  - `"ca_all_levels_mock_1"`: `"ICAI All-Levels Comprehensive Diagnostic Mock (Foundation + Inter + Final)"` (mode `"mock"`, durationMinutes `90`, marking `{"correct": 2, "wrong": -0.25, "unanswered": 0}`, questionIds: list of 60 IDs across all 4 buckets)
  - `"ca_foundation_mock_1"`: `"Level 1: CA Foundation Full Mock (Papers 1–4 • -0.25 Negative Marking)"` (mode `"mock"`, durationMinutes `45`, marking `{"correct": 1, "wrong": -0.25, "unanswered": 0}`, questionIds: all CA Foundation IDs)
  - `"ca_inter_g1_mock"`: `"Level 2A: CA Intermediate Group I Case-Scenario Mock (Adv Accounts, Corp Law, Tax AY 2026-27 & GST)"` (mode `"mock"`, durationMinutes `45`, marking `{"correct": 2, "wrong": 0, "unanswered": 0}`, questionIds: all CA Inter G1 IDs)
  - `"ca_inter_g2_mock"`: `"Level 2B: CA Intermediate Group II Case-Scenario Mock (Costing, Auditing SAs, FM & SM)"` (mode `"mock"`, durationMinutes `40`, marking `{"correct": 2, "wrong": 0, "unanswered": 0}`, questionIds: all CA Inter G2 IDs)
  - `"ca_final_spom_mock"`: `"Level 3: CA Final (Group I & II + IBS) & SPOM Sets A–D Case-Scenario Mock"` (mode `"mock"`, durationMinutes `50`, marking `{"correct": 2, "wrong": 0, "unanswered": 0}`, questionIds: all CA Final & SPOM IDs)
  - `"ca_tax_gst_drill"`: `"High-Yield Income Tax (Sec 115BAC AY 2026-27) & CGST ITC Sec 16/17 Drill"` (mode `"practice"`, durationMinutes `30`, marking `{"correct": 2, "wrong": 0, "unanswered": 0}`)
  - `"ca_law_audit_drill"`: `"Companies Act 2013, Contract Act, IBC 2016 & Standards on Auditing (SAs) Drill"` (mode `"practice"`, durationMinutes `30`, marking `{"correct": 2, "wrong": 0, "unanswered": 0}`)
  - `"ca_accounts_afm_cost_drill"`: `"Accounting Standards (AS / Ind AS 115, 116, 109), Costing & AFM Numericals Drill"` (mode `"practice"`, durationMinutes `30`, marking `{"correct": 2, "wrong": -0.25, "unanswered": 0}`)
- `"questions"`: list of question objects, each having:
  - `"id"`: integer (e.g. 101..130 for `"CA Foundation"`, 201..230 for `"CA Inter G1"`, 301..325 for `"CA Inter G2"`, 401..430 for `"CA Final & SPOM"`)
  - `"subject"`: MUST be one of `"CA Foundation"`, `"CA Inter G1"`, `"CA Inter G2"`, `"CA Final & SPOM"`
  - `"classLevel"`: e.g., `"Level 1 — CA Foundation"`, `"Level 2 — CA Inter Group I"`, `"Level 2 — CA Inter Group II"`, `"Level 3 — CA Final / SPOM"`
  - `"chapter"`: specific Paper & Chapter name (e.g., `"Paper 3: Quantitative Aptitude — Time Value of Money"`, `"Paper 3: Taxation — Income Tax Sec 115BAC & Heads of Income"`, `"Paper 1: Financial Reporting — Ind AS 115 & Ind AS 116"`, etc.)
  - `"ncertRef"`: ICAI Statutory / BoS Reference (e.g., `"ICAI BoS Module — Companies Act 2013, Sec 135 (CSR)"`, `"ICAI BoS — CGST Act 2017, Sec 17(5) Blocked ITC"`, `"ICAI BoS — Ind AS 116 Leases"`, `"ICAI BoS — SA 700 / SA 705 Audit Opinion"`)
  - `"pyqTag"`: e.g., `"ICAI RTP May 2026 / Nov 2025"`, `"ICAI Past Paper Sep 2025"`, `"ICAI MTP Series I — 2026"`, `"ICAI Case Scenario Digest"`
  - `"questionType"`: e.g., `"Case-Scenario MCQ (2M, 0 Neg)"`, `"Foundation Objective MCQ (+1 / -0.25)"`, `"Numerical / Computation MCQ"`, `"Statutory Provision & Case Law MCQ"`
  - `"difficulty"`: `"Easy"`, `"Medium"`, or `"Hard"`
  - `"stem_en"`: Rich, realistic ICAI exam question or mini case scenario (using Chennai/Coimbatore/Madurai Ltd. company examples where appropriate, clear numbers, sections, dates).
  - `"stem_ta"`: Accurate, natural Tamil translation + summary of the question stem for Tamil Nadu students (`தமிழ் சுருக்கம் / வினா`).
  - `"choices"`: 4 options (`"A"`, `"B"`, `"C"`, `"D"`), each with `"letter"`, `"text_en"`, `"text_ta"`.
  - `"correct"`: `"A"`, `"B"`, `"C"`, or `"D"` (100% verified against statutory provisions & arithmetic!).
  - `"explanation_en"`: Step-by-step ICAI working note / statutory provision / case law explanation in English.
  - `"explanation_ta"`: Clear step-by-step Tamil conceptual explanation (`தமிழ் விளக்கம்`) explaining the section/standard/calculation.
  - `"ncert_key_point"`: High-yield ICAI Examiner Tip / Exemption Rule / Section Memory Hook.
  - `"trap_breakdown"`: dict explaining why the other 3 options are classic ICAI examiner traps (e.g. old tax regime vs default Sec 115BAC, blocked credit exception under Sec 17(5), simple vs effective interest, 40% paper floor vs 50% aggregate).
  - `"videoTutorial"`: `{"title": ..., "channel": ..., "url": ...}` pointing to real CA Tamil/English YouTube channels (`https://www.youtube.com/@CAinTamil`, `https://www.youtube.com/@icai_ca_tube`, `https://www.youtube.com/@KPGClasses`, etc.).

#### B. `past_papers_archive.json`
Must match the rich archive structure used by the Past Papers & RTP/MTP Explorer tab:
- `"metadata"`:
  - `"title"`: `"Official ICAI Past Exam Papers, RTPs (Revision Test Papers), MTPs & Case-Scenario Archive (2018–2026)"`
  - `"totalQuestions"`: total questions across the archive (generate a rich set of 200+ questions across past exam cycles & RTP/MTP modules so students can drill paper-by-paper!)
  - `"officialPyqQuestions"`, `"englishQuestions"`, `"tamilBookletQuestions"`, `"exemplarAndCoachingQuestions"`, `"totalPapers"` (e.g. 18 papers across May/Sep/Nov/Jan cycles 2019–2026), `"specialModulesCount"`: 6, `"yearsCovered"`: `[2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]`, `"subjectCounts"`, `"sources"`
- `"analytics"`:
  - `"overallQuestionTypes"`: counts by type (`"Case-Scenario MCQ (2M)"`, `"Numerical / Working Note Computation"`, `"Statutory Section & Exception Trap"`, `"Accounting / Auditing Standard (AS/Ind AS/SA)"`, `"Landmark Case Law Application"`)
  - `"questionTypeByYear"`: 2019..2026 breakdown
  - `"topChaptersBySubject"`: top high-weightage chapters for `"CA Foundation"`, `"CA Inter G1"`, `"CA Inter G2"`, `"CA Final & SPOM"`
- `"disputedQuestionsDossier"`: 6 landmark ICAI Examiner Rulings, Amendment Transitions & High-Failure Traps (e.g., Finance Act 2025/2026 Default New Tax Regime Sec 115BAC(1A) vs Old Regime trap; CGST Sec 17(5) motor vehicle & food/beverages blocked credit exceptions; Companies Act Sec 185 Loan to Directors vs exemptions; Ind AS 116 Lease liability modification; CA Foundation Paper 3 & 4 `-0.25` negative marking & 50% aggregate trap; CA Final Paper 6 IBS Open-Book index trap).
- `"examShocksTimeline"`: 2019–2026 ICAI New Scheme milestones (30% compulsory Case-Scenario MCQs in Inter & Final; May 2024 ICAI New Scheme launch reducing Inter & Final from 8 papers to 6 papers; Tri-annual exams Jan/May/Sep for Foundation & Inter; Mandatory SPOM Sets A, B, C, D CBT exams; 2-year uninterrupted Articleship + 60% permanent/3-attempt paper exemption rule).
- `"unofficialInsights"`: `patternShifts`, `controversiesAndLessons`, `coachingAndRedditMeta` (e.g., `r/CharteredAccountants`, ICAI BoS RTP/MTP hit-rate, KS Academy / Srinivasa Academy / TAHDCO test-series strategy), `tamilNaduEcosystem` (TAHDCO Free CA Coaching, SIRC Chennai/Coimbatore/Madurai/Trichy branches, `@CAinTamil`, `KPG Classes Tamil`, `ICAI CA Tube`).
- `"papers"`: list of 16–20 selectable past papers & RTP/MTP papers (covering May 2026 RTP, Jan 2026 Exam, Sep 2025 Exam, May 2025 Exam, Nov 2024 Exam, May 2024 New Scheme Inaugural Exam, Nov 2023, May 2023, Nov 2022, May 2022, Nov 2021, Nov 2020, Nov 2019, plus Tamil Bilingual Concept Booklets for Foundation & Inter).
- `"modules"`: dictionary containing each paper ID from `"papers"` plus special modules (`"icai_landmark_caselaws"`, `"icai_rtp_mtp_2026_capsule"`, `"icai_amendments_ay2026_27"`, `"icai_spom_set_ab_cbt"`, `"icai_ibs_case_studies"`).
- `"questions"`: list of all questions referenced by `"modules"` in `past_papers_archive.json` (can include the base bank questions + systematic parametric/case-scenario variations across 2019–2026 exam cycles so every single paper in `"papers"` has 15–30 real playable questions with full English + Tamil explanations!).

After generating the files, run a verification check in Python to assert:
1. Every module's `questionIds` exist in `questions`.
2. Every question has valid `A/B/C/D` choices, a valid `correct` key, non-empty `stem_en`, `stem_ta`, `explanation_en`, `explanation_ta`, and verified arithmetic.
