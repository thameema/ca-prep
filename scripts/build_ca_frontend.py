#!/usr/bin/env python3
"""
Builds /Users/thameema/git/ca-prep/index.html (and ca_interactive_practice.html + manifest.json)
by adapting the battle-tested Tamil Nadu NEET 720 Mastery Hub UI/UX to the Tamil Nadu ICAI CA
(Chartered Accountant) Mastery Hub (Foundation, Intermediate Group I & II, Final Group I & II, and SPOM Sets A-D),
including all 12+ SIRC of ICAI branches in Tamil Nadu and Public/Government Free CA Coaching Institutes
(TAHDCO, Naan Mudhalvan, ICAI BoS Free Live Classes & SSP Scholarships, Anandam & RPCT Charitable Trusts).
"""

import json
import pathlib
import shutil

NEET_HTML = pathlib.Path("/Users/thameema/git/neet-prep/index.html").read_text(encoding="utf-8")
CA_DIR = pathlib.Path("/Users/thameema/git/ca-prep")

html = NEET_HTML

# 1. Title & Brand Header
html = html.replace(
    "<title>Tamil Nadu NEET-UG Mastery Hub — OMR Mock Exams, Score Tracker & Bilingual Gemini Coach</title>",
    "<title>Tamil Nadu ICAI CA Mastery Hub — Foundation, Intermediate, Final & SPOM Mock Exams + Bilingual Gemini AI Coach</title>",
)
html = html.replace('<span class="brand-badge">TN NEET 720</span>', '<span class="brand-badge">TN ICAI CA HUB</span>')
html = html.replace(
    '<span class="brand-full-text">TAMIL NADU NEET-UG MASTERY HUB</span>',
    '<span class="brand-full-text">TAMIL NADU ICAI CA MASTERY HUB (FOUNDATION • INTER • FINAL)</span>',
)
html = html.replace(
    'Past Papers &amp; Exemplar (7,484 Qs)',
    'ICAI Past Papers, RTPs &amp; Case Scenarios',
)
html = html.replace(
    'Score & Mentor Tracker',
    'Score, 60% Exemption &amp; Aggregate Tracker',
)
html = html.replace(
    'TN NEET Guide & YouTube Hub',
    'TN CA Guide, Public Institutes (TAHDCO/SIRC) &amp; YouTube',
)

# 2. Left OMR / Marking Sidebar & Free Preview Banner
html = html.replace("NTA OMR Bubble Sheet", "ICAI Exam Question Grid")
html = html.replace("Submit OMR", "Submit Paper")
html = html.replace("Wrong (-1)", "Wrong / Trap")
html = html.replace(
    "NTA Marking: <strong>+4</strong> Correct | <strong>-1</strong> Wrong | <strong>0</strong> Blank",
    "ICAI Rule: <strong>40%</strong> Paper Floor | <strong>50%</strong> Group Agg | <strong>60%+</strong> Exemption",
)
html = html.replace(
    "&#10024; Free Trial Preview (Questions 1–3 of 7,484):</strong> Try the first 3 questions below! Unlock all 7,484 Official PYQs &amp; 24/7 Bilingual Gemini AI Coach for free.",
    "&#10024; Free Trial Preview (Questions 1–3 across Foundation, Inter &amp; Final):</strong> Try the first 3 ICAI questions below! Unlock all ICAI Past Papers, RTPs, Case Scenarios &amp; 24/7 Bilingual Gemini AI CA Coach for free.",
)
html = html.replace(
    "openAccessGateModal('Unlock all 7,484 NEET Questions, 27-Year Past Papers &amp; 24/7 Gemini AI Coach instantly — 100% free.')",
    "openAccessGateModal('Unlock all ICAI CA Foundation, Intermediate, Final &amp; SPOM Questions, RTP/MTP Archive &amp; 24/7 Gemini AI CA Coach instantly — 100% free.')",
)
html = html.replace('<span class="badge badge-marks">+4 / -1 OMR</span>', '<span class="badge badge-marks" id="q-marking-badge">ICAI New Scheme</span>')

# 3. Right Docked Gemini AI CA Coach
html = html.replace('<div class="coach-title">Gemini AI NEET Coach</div>', '<div class="coach-title">Gemini AI ICAI CA Coach</div>')
html = html.replace(
    """        <div class="coach-quick-chips">
          <button class="chip-btn" onclick="askCoachPreset('Explain this question step-by-step using NCERT.')">Step-by-Step</button>
          <button class="chip-btn" onclick="askCoachPreset('இந்த வினாவை தமிழில் எளிமையாக விளக்கவும்.')">தமிழில் விளக்குக</button>
          <button class="chip-btn" onclick="askCoachPreset('Why do the wrong options fail and cause a -1 negative mark trap?')">-1 Trap Check</button>
          <button class="chip-btn" onclick="askCoachPreset('Give me the fastest NCERT topper shortcut or memory rule for this topic.')">NCERT Shortcut</button>
          <button class="chip-btn" onclick="askCoachPreset('Give me 1 new NEET-level practice MCQ on this exact chapter to test me.')">Similar MCQ</button>
        </div>""",
    """        <div class="coach-quick-chips">
          <button class="chip-btn" onclick="askCoachPreset('Explain this question step-by-step with ICAI Working Note and Statutory Provision / AS / Ind AS / SA.')">Working Note &amp; Sec</button>
          <button class="chip-btn" onclick="askCoachPreset('இந்த வினாவை தமிழில் எளிமையாக விளக்கவும் (Section / Standard உடன்).')">தமிழில் விளக்குக</button>
          <button class="chip-btn" onclick="askCoachPreset('Why do the other options fail and what is the ICAI examiner trap here?')">Examiner Trap</button>
          <button class="chip-btn" onclick="askCoachPreset('Give me the fastest ICAI Ranker memory hook for this Section / Standard and how to score 60%+ Exemption.')">60% Exemption Tip</button>
          <button class="chip-btn" onclick="askCoachPreset('Give me 1 new ICAI RTP/MTP level Case-Scenario MCQ on this exact topic to test me.')">Similar Case MCQ</button>
        </div>""",
)

# 4. View 1.5: ICAI Past Papers, RTPs, MTPs & Case-Scenario Archive
old_pyq_header = """        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
          <div>
            <h1 style="font-size:19px;color:var(--navy);">Official NTA NEET / AIPMT Past Papers (2000–2026) + NCERT Exemplar &amp; Coaching Archive</h1>
            <p style="font-size:12.5px;color:var(--text-sec);margin-top:3px;">
              <strong>7,404 Archive Questions</strong> (<strong>5,968 Official PYQs</strong> across <strong>40 Official Papers 2000–2026</strong> + <strong>1,436 NCERT Exemplar, Line-by-Line &amp; NTA Abhyas / Coaching Mock Questions</strong> across <strong>5 Dedicated Modules</strong> + <strong>Disputed / Bonus / Supreme Court Module</strong>).
            </p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="btn-outline" onclick="loadSelectedModule('pyq_controversial_2024_2026'); switchMobilePane('question');">Disputed &amp; SC Landmark Qs (8 Qs)</button>
            <button class="btn-outline" onclick="loadSelectedModule('mock_abhyas_cbt_full'); switchMobilePane('question');">NTA Abhyas 180-Q Mock</button>
            <button class="btn-primary" onclick="loadSelectedModule('pyq_reneet_2026'); switchMobilePane('question');">Launch Re-NEET 2026 Paper</button>
          </div>
        </div>"""

new_pyq_header = """        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
          <div>
            <h1 style="font-size:19px;color:var(--navy);">Official ICAI Past Exam Papers, RTPs (Revision Test Papers), MTPs &amp; Case-Scenario Archive (2019–2026)</h1>
            <p style="font-size:12.5px;color:var(--text-sec);margin-top:3px;">
              Covers all <strong>3 Student Groups/Levels</strong> under the <strong>ICAI New Scheme</strong>: <strong>Level 1 CA Foundation</strong> (Papers 1–4), <strong>Level 2 CA Intermediate Group I &amp; II</strong> (Papers 1–6), and <strong>Level 3 CA Final Group I &amp; II + Mandatory SPOM Sets A–D &amp; Open-Book IBS</strong>.
            </p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="btn-outline" onclick="loadSelectedModule('ca_foundation_mock_1'); switchMobilePane('question');">Level 1: CA Foundation Mock</button>
            <button class="btn-outline" onclick="loadSelectedModule('ca_inter_g1_mock'); switchMobilePane('question');">Level 2: CA Inter G1 Mock</button>
            <button class="btn-primary" onclick="loadSelectedModule('ca_final_spom_mock'); switchMobilePane('question');">Level 3: CA Final &amp; SPOM Mock</button>
          </div>
        </div>"""
html = html.replace(old_pyq_header, new_pyq_header)

old_pyq_sec12 = """        <div class="section-card">
          <h2>1. NCERT Exemplar, Line-by-Line, Coaching Mocks, Subject Sprints &amp; Disputed NTA Keys</h2>
          <p style="font-size:12.5px;color:var(--text-sec);margin-bottom:12px;">
            Practice the <strong>NCERT Exemplar &amp; Back-Exercise Level-4 Analytical Bank (709 Qs)</strong>, <strong>NCERT Line-by-Line Page-Wise Biology (342 Qs)</strong>, <strong>NTA Abhyas 180-Q Full CBT Mock</strong>, <strong>Coaching High-Yield PCB Pack (205 Qs)</strong>, <strong>27-Year Subject PYQ Sprints (45 Qs)</strong>, or the <strong>Disputed / Bonus (+4) / Supreme Court Landmark Module</strong>.
          </p>
          <div class="resource-grid" id="pyq-sprint-cards"></div>
        </div>

        <div class="section-card">
          <h2>2. Launch Full Official Past NEET / Re-NEET / AIPMT / தமிழ் Exam Papers (40 Papers, 2000–2026)</h2>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            <button class="subj-pill active" id="pyq-filter-all" onclick="filterPyqPaperCards('all')">All 40 Official Papers</button>
            <button class="subj-pill" id="pyq-filter-recent" onclick="filterPyqPaperCards('recent')">2020–2026 NTA Era</button>
            <button class="subj-pill" id="pyq-filter-ta" onclick="filterPyqPaperCards('ta')">Official NTA தமிழ் Booklets (2018–2021)</button>
            <button class="subj-pill" id="pyq-filter-classic" onclick="filterPyqPaperCards('classic')">2013–2019 NEET / AIPMT</button>
            <button class="subj-pill" id="pyq-filter-aipmt" onclick="filterPyqPaperCards('aipmt')">2000–2012 Classic AIPMT (Prelims &amp; Mains)</button>
          </div>
          <div class="resource-grid" id="pyq-paper-cards"></div>
        </div>"""

new_pyq_sec12 = """        <div class="section-card">
          <h2>1. ICAI Level-Wise Mocks, RTP/MTP Capsules, Finance Act Amendments &amp; Landmark Case Laws</h2>
          <p style="font-size:12.5px;color:var(--text-sec);margin-bottom:12px;">
            Practice dedicated modules for <strong>Group 1: CA Foundation (Papers 1–4 with -0.25 negative marking)</strong>, <strong>Group 2: CA Intermediate (Group I &amp; II 30% Case-Scenario MCQs)</strong>, <strong>Group 3: CA Final (Group I &amp; II + Paper 6 Open-Book IBS + SPOM Sets A–D)</strong>, <strong>Income Tax Sec 115BAC (AY 2026-27) &amp; CGST Sec 16/17</strong>, and <strong>Landmark Corporate/Contract Case Laws</strong>.
          </p>
          <div class="resource-grid" id="pyq-sprint-cards"></div>
        </div>

        <div class="section-card">
          <h2>2. Launch ICAI Past Exam Cycles, RTPs (Revision Test Papers) &amp; MTPs (2019–2026)</h2>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            <button class="subj-pill active" id="pyq-filter-all" onclick="filterPyqPaperCards('all')">All ICAI Papers &amp; RTPs</button>
            <button class="subj-pill" id="pyq-filter-recent" onclick="filterPyqPaperCards('recent')">2024–2026 ICAI New Scheme</button>
            <button class="subj-pill" id="pyq-filter-ta" onclick="filterPyqPaperCards('ta')">Bilingual தமிழ் + EN Concept Booklets</button>
            <button class="subj-pill" id="pyq-filter-classic" onclick="filterPyqPaperCards('classic')">2019–2023 ICAI Past Cycles</button>
            <button class="subj-pill" id="pyq-filter-aipmt" onclick="filterPyqPaperCards('aipmt')">RTP / MTP &amp; SPOM Specials</button>
          </div>
          <div class="resource-grid" id="pyq-paper-cards"></div>
        </div>"""
html = html.replace(old_pyq_sec12, new_pyq_sec12)

html = html.replace("3. 14-Year NTA Question-Format Shift (2013–2026)", "3. ICAI Question-Format Distribution by Cycle (2019–2026)")
html = html.replace("4. Highest-Yield NCERT Chapters (2013–2026 Frequency)", "4. Highest-Weightage ICAI Chapters across All 3 Levels")
html = html.replace("Top recurring NCERT Class 11 &amp; 12 chapters across 3,564 official NEET questions.", "Top recurring ICAI BoS chapters across CA Foundation, CA Intermediate (G1 &amp; G2), and CA Final &amp; SPOM.")
html = html.replace("5. Verified Dossier: Disputed NTA Answer Keys, Bonus Drops &amp; Supreme Court Rulings (2018–2026)", "5. Verified ICAI Examiner Dossier: Finance Act Amendments, 60% Exemption Rules &amp; High-Failure Traps")
html = html.replace("Every NEET aspirant must know how NTA resolves printing errors, old-vs-new NCERT conflicts, and Tamil translation disputes. Click any landmark case below or launch the interactive <strong>9-Question Disputed &amp; Landmark Module</strong>.", "Every CA student must master how ICAI examiners test Finance Act default tax regime switches (Sec 115BAC), CGST Sec 17(5) blocked credit exceptions, Companies Act exemptions, and the 40% Paper Floor vs 50% Group Aggregate rule.")

# 5. View 2: Score Tracker labels
html = html.replace("NEET Score Progression & Mentor Analytics", "ICAI CA Score, 60% Exemption &amp; 50% Aggregate Tracker")
html = html.replace("Projected Score Trend (Out of 720)", "ICAI Percentage Score Trend (40% Pass • 50% Agg • 60% Exemption)")
html = html.replace("Subject-Wise Accuracy (PCB)", "Level-Wise Mastery (Foundation • Inter G1 • Inter G2 • Final &amp; SPOM)")
html = html.replace("<th>Projected / 720</th>", "<th>Score % (ICAI)</th>")
html = html.replace("<th>-1 Lost</th>", "<th>Neg Lost</th>")
html = html.replace("<th>TN Medical College Benchmark</th>", "<th>ICAI Pass / 50% Aggregate / 60% Exemption Status</th>")

# 6. View 3: Replace TN NEET Guide with comprehensive TN ICAI CA 3-Group + Public Institutes (TAHDCO, Naan Mudhalvan, SIRC 12+ Branches) + YouTube Guide
start_guide = html.index('<!-- VIEW 3: TAMIL NADU NEET REFERENCE GUIDE & YOUTUBE HUB -->')
end_guide = html.index('<!-- MOBILE BOTTOM APP BAR -->')

ca_guide_section = """<!-- VIEW 3: TAMIL NADU ICAI CA 3-GROUP GUIDE, PUBLIC INSTITUTES (TAHDCO, NAAN MUDHALVAN, SIRC) & YOUTUBE HUB -->
  <section id="view-guide" class="view-section">
    <div class="page-scroll">
      <div class="page-container">

        <div class="section-card">
          <h2>1. The 3 Student Groups / Levels in ICAI Chartered Accountancy (New Scheme 2024–2026)</h2>
          <p style="font-size:13px;color:var(--text-sec);line-height:1.65;margin-bottom:14px;">
            Under the <strong>ICAI New Scheme of Education and Training</strong>, students preparing for Chartered Accountancy fall into <strong>three distinct student groups/levels</strong>. Every level requires <strong>minimum 40% marks in each individual paper</strong> AND <strong>minimum 50% aggregate marks across the Group</strong>. Scoring <strong>60% or more in any paper earns an automatic 3-Attempt Exemption</strong> in that paper!
          </p>
          <div style="overflow-x:auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student Group / Level</th>
                  <th>Who Takes It &amp; Entry Route</th>
                  <th>Papers &amp; Syllabus Structure</th>
                  <th>Exam Pattern, Negative Marking &amp; Passing Criteria</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Group / Level 1:<br>CA Foundation</strong><br><span style="font-size:11px;color:var(--primary);font-weight:700;">(Jan / May / Sep — 3x/Year)</span></td>
                  <td><strong>Class 12 Students &amp; Pass-outs</strong> (Samacheer Kalvi Commerce or Science stream, CBSE, ISC). Provisional registration allowed after Class 10.</td>
                  <td>
                    <strong>4 Papers (400 Marks):</strong><br>
                    • <strong>Paper 1:</strong> Accounting (100M)<br>
                    • <strong>Paper 2:</strong> Business Laws (100M — Contract, Sale of Goods, Partnership, LLP, Companies Act, NI Act)<br>
                    • <strong>Paper 3:</strong> Quantitative Aptitude — Maths, LR &amp; Statistics (100M)<br>
                    • <strong>Paper 4:</strong> Business Economics (100M)
                  </td>
                  <td>
                    • <strong>Papers 1 &amp; 2:</strong> Descriptive (0 Negative)<br>
                    • <strong>Papers 3 &amp; 4:</strong> 100% MCQ with <strong>+1 Correct &amp; -0.25 Negative Marking</strong><br>
                    • <strong>Pass Rule:</strong> <strong>40%+</strong> in each paper AND <strong>50%+ Aggregate (200/400)</strong>.
                  </td>
                </tr>
                <tr>
                  <td><strong>Group / Level 2:<br>CA Intermediate<br>(Group I &amp; Group II)</strong><br><span style="font-size:11px;color:var(--primary);font-weight:700;">(Jan / May / Sep — 3x/Year)</span></td>
                  <td>
                    <strong>Route A (Foundation Route):</strong> Cleared CA Foundation.<br>
                    <strong>Route B (Direct Entry):</strong> Commerce Graduates/PG with <strong>&ge;55%</strong> (Non-Commerce Graduates with <strong>&ge;60%</strong>, or CS/CMA Inter pass) — <strong>100% Exempt from CA Foundation!</strong>
                  </td>
                  <td>
                    <strong>6 Papers across 2 Groups (600 Marks):</strong><br>
                    <strong>Group I (300M):</strong><br>
                    • <strong>P1:</strong> Advanced Accounting (AS &amp; Co. Accounts)<br>
                    • <strong>P2:</strong> Corporate &amp; Other Laws (Companies Act Sec 1–148, LLP, FEMA)<br>
                    • <strong>P3:</strong> Taxation (Income Tax 50M + GST 50M)<br>
                    <strong>Group II (300M):</strong><br>
                    • <strong>P4:</strong> Cost &amp; Management Accounting<br>
                    • <strong>P5:</strong> Auditing &amp; Ethics (SAs, CARO 2020)<br>
                    • <strong>P6:</strong> Financial Mgmt (50M) &amp; Strategic Mgmt (50M)
                  </td>
                  <td>
                    • <strong>All 6 Papers:</strong> <strong>30% Compulsory Case-Scenario MCQs (0 Negative Marking!)</strong> + <strong>70% Descriptive</strong>.<br>
                    • <strong>Pass Rule:</strong> <strong>40%+ per paper</strong> + <strong>50%+ Group Aggregate</strong> (150/300 per group or 300/600 both groups with set-off).<br>
                    • <strong>Exemption:</strong> <strong>60%+</strong> in any paper exempts that paper for 3 attempts!
                  </td>
                </tr>
                <tr>
                  <td><strong>Group / Level 3:<br>CA Final (Group I &amp; II)<br>+ Mandatory SPOM (Sets A–D)</strong><br><span style="font-size:11px;color:var(--primary);font-weight:700;">(May / Nov — 2x/Year)</span></td>
                  <td><strong>Articleship &amp; Final Students:</strong> Cleared both groups of CA Inter, completed <strong>2 Years Practical Articleship</strong> + AICITSS, and cleared <strong>Self-Paced Online Modules (SPOM Sets A, B, C &amp; D)</strong>.</td>
                  <td>
                    <strong>SPOM (CBT Online MCQ, 100M each):</strong><br>
                    • <strong>Set A:</strong> Corporate &amp; Economic Laws (IBC, SEBI, FEMA, PMLA)<br>
                    • <strong>Set B:</strong> Strategic Cost Mgmt (SCMPE)<br>
                    • <strong>Sets C &amp; D:</strong> Elective &amp; Multidisciplinary<br>
                    <strong>CA Final (6 Papers, 600M):</strong><br>
                    • <strong>G1:</strong> P1 Financial Reporting (Ind AS), P2 Adv. Financial Mgmt (AFM), P3 Adv. Auditing &amp; Ethics<br>
                    • <strong>G2:</strong> P4 Direct Tax &amp; Intl Tax, P5 Indirect Tax (GST &amp; Customs), <strong>P6 Integrated Business Solutions (IBS — Open Book)</strong>
                  </td>
                  <td>
                    • <strong>SPOM Sets A–D:</strong> 100M Computer-Based MCQ, <strong>50% to Pass, 0 Negative Marking</strong>.<br>
                    • <strong>Final Papers 1–6:</strong> <strong>30% Case-Scenario MCQs (0 Negative)</strong> + <strong>70% Descriptive</strong>.<br>
                    • <strong>Paper 6 (IBS):</strong> 4-Hour <strong>Open-Book</strong> Multidisciplinary Case Study (40% MCQ + 60% Descriptive).
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="section-card">
          <h2>2. Public &amp; Government Free CA Coaching Institutes &amp; Scholarships in Tamil Nadu</h2>
          <p style="font-size:13px;color:var(--text-sec);line-height:1.65;margin-bottom:14px;">
            Students in Tamil Nadu who cannot afford private coaching fees (&#8377;45,000–&#8377;1,20,000) can access <strong>100% Free or Heavily Subsidized Public/Government Coaching &amp; Monthly Scholarships</strong> through the Government of Tamil Nadu and ICAI:
          </p>
          <div class="resource-grid">
            <div class="resource-item">
              <div style="font-size:10.5px;font-weight:800;color:var(--primary);margin-bottom:4px;">GOVT OF TAMIL NADU • 100% FREE COACHING</div>
              <h4>1. TAHDCO Free CA / CS / CMA Coaching Scheme</h4>
              <p><strong>Tamil Nadu Adi Dravidar Housing &amp; Development Corporation (TAHDCO)</strong> provides <strong>100% Free CA Foundation &amp; CA Intermediate Coaching</strong>, study materials, and fee support for eligible SC/ST students across Tamil Nadu (family income &le; &#8377;2.5–3.0L).</p>
              <a class="resource-link" href="https://tahdco.com" target="_blank" rel="noopener">Open Official TAHDCO Portal (tahdco.com) &rarr;</a>
            </div>
            <div class="resource-item">
              <div style="font-size:10.5px;font-weight:800;color:var(--primary);margin-bottom:4px;">GOVT OF TAMIL NADU • COLLEGE COMMERCE &amp; BFSI</div>
              <h4>2. Naan Mudhalvan Scheme (TNSDC — Govt &amp; Aided Colleges)</h4>
              <p>Tamil Nadu Government's flagship skill &amp; competitive exam initiative across Govt &amp; Aided Arts &amp; Science Colleges (B.Com/BBA), providing BFSI, GST, Corporate Accounting, and Audit tracks for <strong>CA Direct Entry Route</strong> aspirants.</p>
              <a class="resource-link" href="https://www.naanmudhalvan.tn.gov.in" target="_blank" rel="noopener">Open Naan Mudhalvan Portal &rarr;</a>
            </div>
            <div class="resource-item">
              <div style="font-size:10.5px;font-weight:800;color:var(--primary);margin-bottom:4px;">STATUTORY PUBLIC BODY • 100% FREE LIVE CLASSES</div>
              <h4>3. ICAI Board of Studies (BoS) Free Live Learning &amp; SSP Scholarships</h4>
              <p>ICAI provides <strong>100% Free Live Virtual Classes</strong> for every Foundation, Inter &amp; Final paper via <strong>BoS Live / ICAI CA Tube</strong>, plus <strong>Need-Based SSP Scholarships (&#8377;1,500–&#8377;5,000/month)</strong> for students with parental income &le; &#8377;3–5 Lakhs.</p>
              <a class="resource-link" href="https://boslive.icai.org" target="_blank" rel="noopener">Open ICAI BoS Live &amp; SSP Portal &rarr;</a>
            </div>
            <div class="resource-item">
              <div style="font-size:10.5px;font-weight:800;color:var(--primary);margin-bottom:4px;">PUBLIC CHARITABLE TRUST • CHENNAI / TN</div>
              <h4>4. Anandam Charitable Trust &amp; RPCT Free CA Coaching (Chennai)</h4>
              <p><strong>Anandam Charitable Trust</strong> and <strong>Ramanathan Public Charitable Trust (RPCT)</strong> in Chennai offer <strong>100% Free CA Coaching, ICAI registration fee sponsorship, books, and mentorship</strong> for meritorious Govt/Corporation school students.</p>
              <a class="resource-link" href="https://anandamtrust.org" target="_blank" rel="noopener">Open Anandam Charitable Trust &rarr;</a>
            </div>
          </div>
        </div>

        <div class="section-card">
          <h2>3. Official SIRC of ICAI Headquarters (Chennai) &amp; All 12+ Tamil Nadu District Branches</h2>
          <p style="font-size:13px;color:var(--text-sec);line-height:1.65;margin-bottom:14px;">
            The <strong>Southern India Regional Council (SIRC) of ICAI</strong> is the statutory public body governing CA education across South India. Every Tamil Nadu district branch listed below offers <strong>Subsidized Public Oral Coaching, AC Student Reading Rooms/Libraries, Official BoS Study Material Counters, ICITSS/AICITSS Computer &amp; Orientation Labs, and Physical Mock Test Centers</strong>:
          </p>
          <div style="overflow-x:auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>SIRC / ICAI Branch</th>
                  <th>Official Address &amp; Location</th>
                  <th>Student Services &amp; Public Facilities</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>1. Chennai — SIRC HQ</strong></td>
                  <td><strong>ICAI Bhawan</strong>, 122, Mahatma Gandhi Road (Nungambakkam High Road), Chennai – 600 034 (<a class="resource-link" href="https://sirc-icai.org" target="_blank" rel="noopener">sirc-icai.org</a>)</td>
                  <td>Regional Headquarters, AC Reading Libraries, BoS Publication Counter, Oral Coaching Classes, ICITSS/AICITSS Labs, Articleship Placement Cell.</td>
                </tr>
                <tr>
                  <td><strong>2. Coimbatore Branch</strong></td>
                  <td>ICAI Bhawan, Race Course / Thudiyalur Main Road, Kurudampalayam, Coimbatore – 641 017 / 641 034 (<a class="resource-link" href="https://coimbatore-icai.org" target="_blank" rel="noopener">coimbatore-icai.org</a>)</td>
                  <td>Western TN Hub — Foundation/Inter Oral Coaching, Student Reading Library, IT &amp; Orientation Batches, Mock Test Center.</td>
                </tr>
                <tr>
                  <td><strong>3. Madurai Branch</strong></td>
                  <td>ICAI Bhawan, No. 30, P.T.R. Road / Visalakshipuram 2nd Street, Narimedu, Madurai – 625 002 / 625 014 (<a class="resource-link" href="https://madurai-icai.org" target="_blank" rel="noopener">madurai-icai.org</a>)</td>
                  <td>Southern TN Hub — Student Reading Room, Coaching Batches, ICITSS/AICITSS Labs, Physical MTP Exams.</td>
                </tr>
                <tr>
                  <td><strong>4. Tiruchirappalli (Trichy)</strong></td>
                  <td>ICAI Bhawan, No. 24, SBI Officers Colony, Lawsons Road, Cantonment, Tiruchirappalli – 620 001</td>
                  <td>Central TN Hub — Student Library, Orientation &amp; IT Training, Foundation/Inter Study Circle.</td>
                </tr>
                <tr>
                  <td><strong>5. Salem Branch</strong></td>
                  <td>ICAI Bhawan, 66, Ramakrishna Road, Hasthampatti, Salem – 636 007</td>
                  <td>Salem / Namakkal / Dharmapuri Hub — IT Labs, Student Library, Mock Test Series.</td>
                </tr>
                <tr>
                  <td><strong>6. Erode Branch</strong></td>
                  <td>ICAI Bhawan, Perundurai Road / Mettukadai, Erode – 638 107</td>
                  <td>Erode Commerce Belt — ICITSS/AICITSS Computer Labs, Reading Room &amp; Coaching.</td>
                </tr>
                <tr>
                  <td><strong>7. Tirupur Branch</strong></td>
                  <td>ICAI Bhawan, No. 46, P.N. Road, Tirupur – 641 602</td>
                  <td>Export &amp; Textile GST/Forex Articleship Hub — Student Library, IT Labs &amp; MTP Center.</td>
                </tr>
                <tr>
                  <td><strong>8. Tirunelveli Branch</strong></td>
                  <td>ICAI Bhawan, Palayamkottai / Vannarpettai, Tirunelveli – 627 002</td>
                  <td>Tirunelveli / Kanyakumari / Tenkasi Hub — Student Library, Orientation &amp; IT Training.</td>
                </tr>
                <tr>
                  <td><strong>9. Vellore Branch</strong></td>
                  <td>ICAI Bhawan, Katpadi / Gandhi Nagar, Vellore – 632 006</td>
                  <td>Northern TN Hub (Vellore / Ranipet / Tiruvannamalai) — Study Material &amp; Training Center.</td>
                </tr>
                <tr>
                  <td><strong>10. Kumbakonam Branch</strong></td>
                  <td>ICAI Bhawan, No. 23, Pachayappa Street, Kumbakonam – 612 001</td>
                  <td>Cauvery Delta Hub (Thanjavur / Kumbakonam / Tiruvarur / Nagapattinam) — Library &amp; Training.</td>
                </tr>
                <tr>
                  <td><strong>11. Sivakasi Branch</strong></td>
                  <td>ICAI Bhawan, Velayutham Road, Sivakasi – 626 123</td>
                  <td>Virudhunagar District Hub — Student Reading Room, Coaching &amp; MTP Center.</td>
                </tr>
                <tr>
                  <td><strong>12. Tuticorin (Thoothukudi)</strong></td>
                  <td>ICAI Bhawan, Ettayapuram Road, Thoothukudi – 628 002</td>
                  <td>Port &amp; Customs/GST Hub — Student Library &amp; ICITSS Center.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="section-card">
          <h2>4. Verified Tamil + English CA YouTube Channels &amp; Top Tamil Nadu Academies</h2>
          <div class="resource-grid">
            <div class="resource-item">
              <h4>CA in Tamil (@CAinTamil)</h4>
              <p>Dedicated Tamil explanations for <strong>CA Intermediate Direct Tax (Income Tax AY 2026-27), GST, Corporate &amp; Other Laws (Companies Act 2013), and RTP/MTP Amendments</strong>.</p>
              <a class="resource-link" href="https://www.youtube.com/@CAinTamil" target="_blank" rel="noopener">Open @CAinTamil &rarr;</a>
            </div>
            <div class="resource-item">
              <h4>ICAI CA Tube (Official ICAI BoS Channel)</h4>
              <p>Official Board of Studies channel streaming <strong>100% free live revision marathons, Case Scenario discussions, and RTP/MTP solving sessions</strong> across Foundation, Inter &amp; Final.</p>
              <a class="resource-link" href="https://www.youtube.com/@icai_ca_tube" target="_blank" rel="noopener">Open @icai_ca_tube &rarr;</a>
            </div>
            <div class="resource-item">
              <h4>KPG Classes Tamil (@KPGClasses)</h4>
              <p>Bilingual Tamil + English lectures covering <strong>CA Foundation Business Economics &amp; Business Laws</strong> and <strong>CA Intermediate Auditing &amp; Strategic Management</strong>.</p>
              <a class="resource-link" href="https://www.youtube.com/@KPGClasses" target="_blank" rel="noopener">Open @KPGClasses &rarr;</a>
            </div>
            <div class="resource-item">
              <h4>Learn with JJ / Tamil Accounting &amp; Costing</h4>
              <p>Clear Tamil step-by-step working notes for <strong>Accounting, Advanced Accounting, Cost &amp; Management Accounting (Marginal, Standard, Process), and Financial Management</strong>.</p>
              <a class="resource-link" href="https://www.youtube.com/@LearnwithJJ" target="_blank" rel="noopener">Open @LearnwithJJ &rarr;</a>
            </div>
            <div class="resource-item">
              <h4>Audit Raza — CA Inter &amp; Final Tamil</h4>
              <p>Standards on Auditing (<strong>SA 200 to SA 720</strong>), <strong>CARO 2020</strong> clauses, and Professional Ethics schedules explained in Tamil with keyword memory hooks.</p>
              <a class="resource-link" href="https://www.youtube.com/results?search_query=CA+Inter+Audit+Tamil" target="_blank" rel="noopener">Open CA Audit Tamil &rarr;</a>
            </div>
            <div class="resource-item">
              <h4>Top Private TN Academies (Reference &amp; Test Series)</h4>
              <p><strong>KS Academy (KSA)</strong> (Chennai, Coimbatore, Trichy), <strong>Srinivasa Academy</strong> (Chennai), <strong>Yeshas / JK Shah</strong>, and <strong>Sree Atchayaa / Padmarajam</strong> (Madurai).</p>
              <a class="resource-link" href="https://sirc-icai.org" target="_blank" rel="noopener">Compare with SIRC Public Coaching &rarr;</a>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>

  """

html = html[:start_guide] + ca_guide_section + html[end_guide:]

# 7. Mobile bottom nav & Modals (Profile, Access Gate, Admin Console)
html = html.replace('<span id="mnav-omr-label">OMR Sheet</span>', '<span id="mnav-omr-label">Q Grid</span>')
html = html.replace('<span>PYQs</span>', '<span>RTP/PYQs</span>')
html = html.replace('<span>TN Guide</span>', '<span>CA Guide</span>')

old_profile_modal = """  <!-- STUDENT PROFILE & SETTINGS MODAL -->
  <div class="modal-backdrop" id="profile-modal">
    <div class="modal-card">
      <h3 style="font-size:16.5px;color:var(--navy);margin-bottom:6px;">Student Profile & Tamil Nadu Quota Settings</h3>
      <p style="font-size:12.5px;color:var(--text-sec);margin-bottom:14px;">
        Personalizes your score tracker, Tamil Nadu Government Medical College cutoffs, and Bilingual Gemini AI Coach.
      </p>
      <div class="form-group">
        <label>Student Name</label>
        <input type="text" id="prof-name" class="form-control" placeholder="e.g., Ananya" />
      </div>
      <div class="form-group">
        <label>Tamil Nadu District</label>
        <input type="text" id="prof-district" class="form-control" placeholder="e.g., Chennai, Madurai, Coimbatore" />
      </div>
      <div class="form-group">
        <label>School Curriculum</label>
        <select id="prof-board" class="form-control">
          <option value="TN State Board (Samacheer Kalvi)">TN State Board (Samacheer Kalvi)</option>
          <option value="CBSE (NCERT)">CBSE (NCERT)</option>
          <option value="ICSE / ISC">ICSE / ISC</option>
        </select>
      </div>
      <div class="form-group">
        <label>Counseling Quota Category</label>
        <select id="prof-quota" class="form-control">
          <option value="BC (85% TN State Quota)">BC / BCM (85% TN State Quota)</option>
          <option value="MBC / DNC (85% TN State Quota)">MBC / DNC (85% TN State Quota)</option>
          <option value="OC / General (85% TN State Quota)">OC / General (85% TN State Quota)</option>
          <option value="SC / SCA / ST (85% TN State Quota)">SC / SCA / ST (85% TN State Quota)</option>
          <option value="7.5% TN Govt School Quota">7.5% TN Government School Preferential Quota</option>
        </select>
      </div>
      <div class="form-group">
        <label>Target NEET Score (Out of 720)</label>
        <input type="number" id="prof-target" class="form-control" min="360" max="720" value="650" />
      </div>"""

new_profile_modal = """  <!-- STUDENT PROFILE & SETTINGS MODAL -->
  <div class="modal-backdrop" id="profile-modal">
    <div class="modal-card">
      <h3 style="font-size:16.5px;color:var(--navy);margin-bottom:6px;">CA Student Profile &amp; ICAI Level Settings</h3>
      <p style="font-size:12.5px;color:var(--text-sec);margin-bottom:14px;">
        Personalizes your 40% Paper Floor / 50% Group Aggregate / 60% Exemption tracker, SIRC Branch, and Bilingual Gemini AI CA Coach.
      </p>
      <div class="form-group">
        <label>Student Name</label>
        <input type="text" id="prof-name" class="form-control" placeholder="e.g., Karthik / Divya" />
      </div>
      <div class="form-group">
        <label>Tamil Nadu District / SIRC Branch</label>
        <input type="text" id="prof-district" class="form-control" placeholder="e.g., Chennai, Coimbatore, Madurai, Trichy, Salem" />
      </div>
      <div class="form-group">
        <label>Current ICAI CA Level / Student Group</label>
        <select id="prof-board" class="form-control">
          <option value="Level 1: CA Foundation (After Class 12)">Group / Level 1: CA Foundation (4 Papers)</option>
          <option value="Level 2: CA Intermediate (Group I & II)">Group / Level 2: CA Intermediate (Group I &amp; II — 6 Papers)</option>
          <option value="Level 2: CA Intermediate (Direct Entry Graduate)">Group / Level 2: CA Intermediate (Direct Entry Route)</option>
          <option value="Level 3: CA Final & SPOM Sets A-D">Group / Level 3: CA Final (Group I &amp; II + IBS + SPOM Sets A–D)</option>
        </select>
      </div>
      <div class="form-group">
        <label>Coaching / Scholarship Track</label>
        <select id="prof-quota" class="form-control">
          <option value="ICAI BoS Free Live + Self Study">ICAI BoS Free Live Classes + Self Study</option>
          <option value="TAHDCO Free CA Coaching (Govt of TN)">TAHDCO Free CA Coaching Scheme (Govt of TN)</option>
          <option value="Naan Mudhalvan / Govt Aided College Commerce">Naan Mudhalvan / TN Govt &amp; Aided College Track</option>
          <option value="ICAI SSP Need / Merit Scholarship">ICAI SSP Need / Merit Scholarship (&le; &#8377;3–5L Income)</option>
          <option value="SIRC Branch Oral Coaching / Private Academy">SIRC Branch Oral Coaching / Private Academy</option>
        </select>
      </div>
      <div class="form-group">
        <label>Target Score Percentage (60%+ = ICAI Exemption!)</label>
        <input type="number" id="prof-target" class="form-control" min="40" max="100" value="65" />
      </div>"""
html = html.replace(old_profile_modal, new_profile_modal)

# Intro Video Modal & Access Gate Modal updates
html = html.replace(
    "Complete tour of all 4 tabs: NTA 180-Q OMR Workspace, -1 Negative Mark Trap Box, 24/7 Bilingual Gemini AI Coach, 27-Year Past Papers &amp; NCERT Exemplar Archive (7,484 Qs), and TN Medical College Score Tracker.",
    "Complete tour of all 4 tabs: ICAI 3-Level Workspace (Foundation, Inter G1/G2, Final &amp; SPOM), Statutory &amp; Working Note Solutions, 24/7 Bilingual Gemini AI CA Coach, RTP/MTP Past Paper Archive, and Public Institutes (TAHDCO, Naan Mudhalvan, SIRC Branches).",
)
html = html.replace(
    "Unlock All 7,484 NEET Questions &amp; AI Coach",
    "Unlock All ICAI CA Levels, RTP/MTP Archive &amp; AI Coach",
)
html = html.replace(
    "Enter your Name &amp; Email below to unlock the full 27-Year NEET Archive &amp; 24/7 Bilingual (தமிழ் + English) Gemini AI Coach immediately.",
    "Enter your Name &amp; Email below to unlock all 3 ICAI Levels (Foundation, Intermediate, Final &amp; SPOM) + 24/7 Bilingual (தமிழ் + English) Gemini AI CA Coach immediately.",
)
html = html.replace(
    """          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;" id="req-role-pills">
            <button type="button" class="role-pill-btn" data-role="NEET Student (Class 11/12/Dropper)" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:12px;font-weight:800;border-radius:7px;border:1.5px solid #0f766e;background:#f0fdfa;color:#0f766e;cursor:pointer;">&#127891; Student</button>
            <button type="button" class="role-pill-btn" data-role="Parent of NEET Aspirant" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:12px;font-weight:700;border-radius:7px;border:1px solid var(--border);background:#ffffff;color:var(--text-sec);cursor:pointer;">&#128106; Parent</button>
            <button type="button" class="role-pill-btn" data-role="Teacher / NEET Mentor" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:12px;font-weight:700;border-radius:7px;border:1px solid var(--border);background:#ffffff;color:var(--text-sec);cursor:pointer;">&#128218; Teacher</button>
          </div>
          <input type="hidden" id="req-purpose" value="NEET Student (Class 11/12/Dropper)" />""",
    """          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;" id="req-role-pills">
            <button type="button" class="role-pill-btn" data-role="Group 1: CA Foundation Student" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:11.5px;font-weight:800;border-radius:7px;border:1.5px solid #0f766e;background:#f0fdfa;color:#0f766e;cursor:pointer;">&#127891; Foundation</button>
            <button type="button" class="role-pill-btn" data-role="Group 2: CA Intermediate Student" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:11.5px;font-weight:700;border-radius:7px;border:1px solid var(--border);background:#ffffff;color:var(--text-sec);cursor:pointer;">&#128218; CA Inter</button>
            <button type="button" class="role-pill-btn" data-role="Group 3: CA Final / Articleship / Mentor" onclick="selectGateRolePill(this)" style="padding:7px 8px;font-size:11.5px;font-weight:700;border-radius:7px;border:1px solid var(--border);background:#ffffff;color:var(--text-sec);cursor:pointer;">&#9878; CA Final / Mentor</button>
          </div>
          <input type="hidden" id="req-purpose" value="Group 1: CA Foundation Student" />""",
)
html = html.replace("Unlock All 7,484 Questions &amp; AI Coach Now &rarr;", "Unlock All CA Levels, RTPs &amp; AI Coach Now &rarr;")
html = html.replace("Unlock All 7,484 Questions & AI Coach Now →", "Unlock All CA Levels, RTPs & AI Coach Now →")
html = html.replace("<code>NEET-XXXXXX</code>", "<code>CA-XXXXXX</code>")
html = html.replace("placeholder=\"e.g., NEET-7X9K2M\"", "placeholder=\"e.g., CA-7X9K2M\"")
html = html.replace("100% Free for NEET Aspirants • Includes 40 Bilingual Gemini AI Coach explanations/day.", "100% Free for Tamil Nadu CA Aspirants (Foundation • Inter • Final) • Includes 40 Bilingual Gemini AI Coach explanations/day.")
html = html.replace("NEET 720 Gatekeeper — Access Requests &amp; Analytics", "CA Mastery Hub Gatekeeper — Access Requests &amp; Analytics")

# 8. JavaScript State, Storage Keys, Grading & Rendering adaptations
html = html.replace("window.NEET_QUESTION_BANK", "(window.CA_QUESTION_BANK || window.NEET_QUESTION_BANK)")
html = html.replace("window.NEET_PAST_PAPERS_ARCHIVE", "(window.CA_PAST_PAPERS_ARCHIVE || window.NEET_PAST_PAPERS_ARCHIVE)")
html = html.replace("http://localhost:8090", "http://localhost:8096")
html = html.replace("tn_neet_backend_override", "tn_ca_backend_override")

old_storage_keys = """    const STORAGE_KEYS = {
      profile: "tn_neet_student_profile_v1",
      session: "tn_neet_active_session_v1",
      localAttempts: "tn_neet_local_attempts_v1",
      mistakes: "tn_neet_mistake_ids_v1",
      chat: "tn_neet_coach_chat_v1",
      accessCode: "tn_neet_access_code_v1",
      deviceId: "tn_neet_device_id_v1",
      pendingToken: "tn_neet_pending_req_token_v1"
    };"""

new_storage_keys = """    const STORAGE_KEYS = {
      profile: "tn_ca_student_profile_v1",
      session: "tn_ca_active_session_v1",
      localAttempts: "tn_ca_local_attempts_v1",
      mistakes: "tn_ca_mistake_ids_v1",
      chat: "tn_ca_coach_chat_v1",
      accessCode: "tn_ca_access_code_v1",
      deviceId: "tn_ca_device_id_v1",
      pendingToken: "tn_ca_pending_req_token_v1"
    };"""
html = html.replace(old_storage_keys, new_storage_keys)

old_default_prof = """    let profile = {
      student_id: "tn_student_1",
      name: "NEET Aspirant",
      district: "Chennai",
      board: "TN State Board (Samacheer Kalvi)",
      quota_category: "BC (85% TN State Quota)",
      language_pref: "bilingual",
      target_score: 650,
      custom_gemini_key: ""
    };

    let state = {
      moduleId: "full_mock_1","""

new_default_prof = """    let profile = {
      student_id: "tn_ca_student_1",
      name: "CA Aspirant",
      district: "Chennai (SIRC HQ)",
      board: "Level 1: CA Foundation (After Class 12)",
      quota_category: "ICAI BoS Free Live + Self Study",
      language_pref: "bilingual",
      target_score: 65,
      custom_gemini_key: ""
    };

    let state = {
      moduleId: "ca_all_levels_mock_1","""
html = html.replace(old_default_prof, new_default_prof)

old_groups_js = """      const groups = [
        { label: "Core Bilingual Mastery Mocks & Chapter Drills", filter: m => !m.id.startsWith("pyq_") && !m.isExemplarOrCoaching },
        { label: "NCERT Exemplar, Line-by-Line & Coaching Mock Series", filter: m => Boolean(m.isExemplarOrCoaching) },
        { label: "NTA Disputed Keys & 27-Year Subject PYQ Sprints", filter: m => m.id === "pyq_controversial_2024_2026" || m.isDynamicSubjectPyq },
        { label: "Official Past NEET & Re-NEET Papers (2020–2026)", filter: m => m.isPastPaper && !m.isControversialModule && m.paperLanguage !== "ta" && (m.examYear || 0) >= 2020 },
        { label: "Official NTA தமிழ் Booklet Past Papers (2018–2021)", filter: m => m.isPastPaper && m.paperLanguage === "ta" },
        { label: "Official Past NEET & AIPMT Papers (2013–2019)", filter: m => m.isPastPaper && m.paperLanguage !== "ta" && (m.examYear || 0) >= 2013 && (m.examYear || 0) < 2020 },
        { label: "Classic CBSE AIPMT Past Papers (2000–2012 Prelims & Mains)", filter: m => m.isPastPaper && m.paperLanguage !== "ta" && (m.examYear || 0) < 2013 }
      ];"""

new_groups_js = """      const groups = [
        { label: "ICAI 3-Level Comprehensive Mocks & Statutory Drills (Foundation • Inter • Final)", filter: m => !m.isPastPaper && !m.isExemplarOrCoaching },
        { label: "ICAI RTP, MTP, Finance Act AY 2026-27 & Landmark Case Law Modules", filter: m => Boolean(m.isExemplarOrCoaching) || Boolean(m.isControversialModule) },
        { label: "ICAI New Scheme Past Exam & RTP Papers (2024–2026)", filter: m => m.isPastPaper && !m.isControversialModule && m.paperLanguage !== "ta" && (m.examYear || 0) >= 2024 },
        { label: "Bilingual தமிழ் + English CA Concept & Case-Scenario Booklets", filter: m => m.isPastPaper && m.paperLanguage === "ta" },
        { label: "ICAI Past Exam & RTP Papers (2019–2023)", filter: m => m.isPastPaper && m.paperLanguage !== "ta" && (m.examYear || 0) < 2024 }
      ];"""
html = html.replace(old_groups_js, new_groups_js)

html = html.replace(
    'loadSelectedModule("full_mock_1", true);',
    'const firstModId = BANK.modules["ca_all_levels_mock_1"] ? "ca_all_levels_mock_1" : Object.keys(BANK.modules)[0]; loadSelectedModule(firstModId, true);',
)

html = html.replace(
    'text: "வணக்கம்! Welcome to your **Tamil Nadu NEET-UG Mastery Workspace**. Select any question or ask me in **English** or **தமிழ்** for step-by-step NCERT explanations, shortcuts, or -1 negative-mark trap analysis."',
    'text: "வணக்கம்! Welcome to your **Tamil Nadu ICAI CA Mastery Workspace (Foundation • Intermediate • Final & SPOM)**. Select any question or click **Ask Coach** for step-by-step **ICAI Working Notes**, **Statutory Provisions (Companies Act, Income Tax AY 2026-27, CGST, AS/Ind AS, SAs)**, **தமிழ் விளக்கம்**, and **60%+ Exemption** strategies."',
)

html = html.replace('["Physics", "Chemistry", "Botany", "Zoology"]', '["CA Foundation", "CA Inter G1", "CA Inter G2", "CA Final & SPOM"]')

html = html.replace(
    'state.mode === "mock" ? "NTA OMR Mock Sheet" : "Practice Question Grid";',
    'state.mode === "mock" ? "ICAI Mock Question Grid" : "Practice Question Grid";',
)

html = html.replace(
    '`Scheme: <strong>+4</strong> Right | <strong>-1</strong> Wrong | <strong>0</strong> Blank`;',
    '`Pass: <strong>40%</strong> Paper | <strong>50%</strong> Agg | <strong>60%+</strong> Exempt`;',
)

# Update solution panel and marking badge in renderCurrentQuestion
old_marking_sol = """      document.getElementById("q-badges").innerHTML = `
        <span class="badge" style="background:var(--navy);color:#fff;border-color:var(--navy);">Q.${globalNum}/${state.questionIds.length}</span>
        <span class="badge badge-subj">${escapeHtml(q.subject)}</span>
        <span class="badge">${escapeHtml(q.classLevel)} — ${escapeHtml(q.chapter)}</span>
        <span class="badge badge-pyq">${escapeHtml(q.pyqTag)}</span>
        ${statusBadgeHtml}
      `;"""

new_marking_sol = """      const isFoundQ = String(q.subject || "").includes("Foundation");
      const mBadgeEl = document.getElementById("q-marking-badge");
      if (mBadgeEl) {
        mBadgeEl.textContent = isFoundQ ? "+1 / -0.25 Foundation MCQ" : "+2 / 0 Case-Scenario MCQ";
      }
      document.getElementById("q-badges").innerHTML = `
        <span class="badge" style="background:var(--navy);color:#fff;border-color:var(--navy);">Q.${globalNum}/${state.questionIds.length}</span>
        <span class="badge badge-subj">${escapeHtml(q.subject)}</span>
        <span class="badge">${escapeHtml(q.classLevel)} — ${escapeHtml(q.chapter)}</span>
        <span class="badge badge-pyq">${escapeHtml(q.pyqTag)}</span>
        ${statusBadgeHtml}
      `;"""
html = html.replace(old_marking_sol, new_marking_sol)

html = html.replace(
    '<h4>Verified NCERT Solution — ${statusTag}</h4>',
    '<h4>Verified ICAI Statutory Solution &amp; Working Note — ${statusTag}</h4>',
)
html = html.replace(
    '<div class="sol-block"><strong>Reference:</strong> ${escapeHtml(q.ncertRef)}</div>',
    '<div class="sol-block"><strong>ICAI BoS / Statutory Ref:</strong> ${escapeHtml(q.ncertRef)}</div>',
)
html = html.replace(
    '<div class="sol-block"><strong>English Derivation:</strong> ${renderInlineRich(q.explanation_en)}</div>',
    '<div class="sol-block"><strong>ICAI Working Note &amp; Provision (English):</strong> ${renderInlineRich(q.explanation_en)}</div>',
)
html = html.replace(
    '<div class="sol-block"><strong>Topper Rule:</strong> ${renderInlineRich(q.ncert_key_point)}</div>',
    '<div class="sol-block"><strong>ICAI Examiner Tip &amp; 60% Exemption Rule:</strong> ${renderInlineRich(q.ncert_key_point)}</div>',
)
html = html.replace(
    'Why Other Bubbles Trigger -1 Negative Marks:',
    'Why Other Options Fail (ICAI Examiner Traps):',
)

# Update Ask Coach autoPrompt and evaluateTnTierLocal + gradeLocally + renderMockResultBanner + refreshScoreDashboard
old_ask_coach_block = """      if (profile.language_pref === "ta") {
        autoPrompt = userChoice
          ? `வினா ${globalNum} (${q.subject} — ${q.chapter}): நான் தேர்ந்தெடுத்த விருப்பம் ${userChoice} சரியானதா? படிப்படியாக விளக்கவும்.`
          : `வினா ${globalNum} (${q.subject} — ${q.chapter}): இந்த வினாவை தமிழில் படிப்படியாக விளக்கவும்.`;
      } else {
        autoPrompt = userChoice
          ? `Explain Q.${globalNum} (${q.subject} — ${q.chapter}) step-by-step and check my selected option ${userChoice}.`
          : `Explain Q.${globalNum} (${q.subject} — ${q.chapter}) step-by-step using NCERT and highlight the -1 trap.`;
      }"""

new_ask_coach_block = """      if (profile.language_pref === "ta") {
        autoPrompt = userChoice
          ? `வினா ${globalNum} (${q.subject} — ${q.chapter}): நான் தேர்ந்தெடுத்த விருப்பம் ${userChoice} சரியானதா? ICAI விதி மற்றும் கணக்கீட்டுடன் தமிழில் படிப்படியாக விளக்கவும்.`
          : `வினா ${globalNum} (${q.subject} — ${q.chapter}): இந்த வினாவை ICAI விதி மற்றும் கணக்கீட்டுடன் தமிழில் படிப்படியாக விளக்கவும்.`;
      } else {
        autoPrompt = userChoice
          ? `Explain Q.${globalNum} (${q.subject} — ${q.chapter}) step-by-step with ICAI Working Note / Statutory Section and check my selected option ${userChoice}.`
          : `Explain Q.${globalNum} (${q.subject} — ${q.chapter}) step-by-step with ICAI Working Note / Statutory Section and highlight the examiner trap.`;
      }"""
html = html.replace(old_ask_coach_block, new_ask_coach_block)

old_eval_tier_js = """    function evaluateTnTierLocal(proj720, quota) {
      if ((quota || "").includes("7.5%")) {
        if (proj720 >= 565) return "On Track: Tier-1 TN Govt Medical College (MMC / Stanley — 7.5% Quota)";
        if (proj720 >= 515) return "On Track: Tier-2 TN Govt Medical College (7.5% Quota)";
        if (proj720 >= 465) return "On Track: TN District Govt Medical College (7.5% Quota)";
        return "Foundation Phase: Target 470+/720 via NCERT Biology";
      }
      if (proj720 >= 665) return "On Track: Tier-1 TN Govt Medical College (MMC Chennai / Stanley)";
      if (proj720 >= 630) return "On Track: Tier-2 Premier TN Govt Medical College (Kilpauk / Madurai / Coimbatore)";
      if (proj720 >= 595) return "On Track: TN State Quota Government Medical College";
      if (proj720 >= 520) return "Borderline Quota — Cut -1 Negative Marks to cross 600+";
      return "Foundation Phase — Master NCERT Biology (340+/360) & Avoid Guessing";
    }"""

new_eval_tier_js = """    function evaluateTnTierLocal(pct100, quota) {
      if (pct100 >= 70) return "ICAI Distinction & Rank Trajectory (70%+) — 60%+ Exemption & 50% Aggregate Cleared!";
      if (pct100 >= 60) return "ICAI 60%+ EXEMPTION SECURED — Exempt for 3 Attempts & 50% Group Aggregate Cleared!";
      if (pct100 >= 50) return "ICAI PASS (50%+ Group Aggregate & 40%+ Paper Minimum Met) — Push for 60%+ Exemption!";
      if (pct100 >= 40) return "40% Paper Floor Met, but Below 50% ICAI Group Aggregate — Need +10% in Practical/MCQ Papers";
      return "Below 40% ICAI Paper Minimum — Focus on BoS Case Scenarios, AS/Ind AS & Statutory Amendments";
    }"""
html = html.replace(old_eval_tier_js, new_eval_tier_js)

old_grade_local = """    function gradeLocally(payload) {
      let correct = 0, wrong = 0, unans = 0;
      const wrongIds = [];
      const sb = {};
      payload.question_ids.forEach(qid => {
        const q = Q_MAP[qid];
        if (!q) return;
        if (!sb[q.subject]) sb[q.subject] = { total: 0, correct: 0, wrong: 0, unanswered: 0, score: 0, max_score: 0 };
        sb[q.subject].total += 1;
        sb[q.subject].max_score += 4;
        const ch = payload.answers[qid];
        if (q.answerStatus === "dropped") {
          correct += 1; sb[q.subject].correct += 1; sb[q.subject].score += 4;
        } else if (!ch) {
          unans += 1; sb[q.subject].unanswered += 1;
        } else if (isAnswerCorrectForQ(q, ch)) {
          correct += 1; sb[q.subject].correct += 1; sb[q.subject].score += 4;
        } else {
          wrong += 1; wrongIds.push(qid); sb[q.subject].wrong += 1; sb[q.subject].score -= 1;
        }
      });
      const total = payload.question_ids.length;
      const raw = correct * 4 - wrong;
      const maxS = total * 4;
      const proj = maxS > 0 ? Math.round((raw / maxS) * 720) : 0;"""

new_grade_local = """    function gradeLocally(payload) {
      let correct = 0, wrong = 0, unans = 0, raw = 0, maxS = 0, negLost = 0;
      const wrongIds = [];
      const sb = {};
      payload.question_ids.forEach(qid => {
        const q = Q_MAP[qid];
        if (!q) return;
        const isFound = String(q.subject || "").includes("Foundation");
        const qCorr = isFound ? 1 : 2;
        const qWrong = isFound ? -0.25 : 0;
        if (!sb[q.subject]) sb[q.subject] = { total: 0, correct: 0, wrong: 0, unanswered: 0, score: 0, max_score: 0 };
        sb[q.subject].total += 1;
        sb[q.subject].max_score += qCorr;
        maxS += qCorr;
        const ch = payload.answers[qid];
        if (q.answerStatus === "dropped") {
          correct += 1; raw += qCorr; sb[q.subject].correct += 1; sb[q.subject].score += qCorr;
        } else if (!ch) {
          unans += 1; sb[q.subject].unanswered += 1;
        } else if (isAnswerCorrectForQ(q, ch)) {
          correct += 1; raw += qCorr; sb[q.subject].correct += 1; sb[q.subject].score += qCorr;
        } else {
          wrong += 1; wrongIds.push(qid); raw += qWrong; negLost += Math.abs(qWrong); sb[q.subject].wrong += 1; sb[q.subject].score += qWrong;
        }
      });
      raw = Math.round(raw * 100) / 100;
      negLost = Math.round(negLost * 100) / 100;
      const total = payload.question_ids.length;
      const proj = maxS > 0 ? Math.round((raw / maxS) * 100) : 0;"""
html = html.replace(old_grade_local, new_grade_local)
html = html.replace("negative_marks_lost: wrong,", "negative_marks_lost: negLost,")

html = html.replace('<div class="res-stat-label">Projected / 720</div>', '<div class="res-stat-label">ICAI Score %</div>')
html = html.replace('<div class="res-stat-val" style="color:#5eead4;">${g.projected_720} / 720</div>', '<div class="res-stat-val" style="color:#5eead4;">${g.projected_720}%</div>')
html = html.replace('<div class="res-stat-label">Correct (+4)</div>', '<div class="res-stat-label">Correct</div>')
html = html.replace('<div class="res-stat-label">Wrong (-1)</div>', '<div class="res-stat-label">Wrong (Neg)</div>')

html = html.replace("Goal: ${profile.target_score} / 720", "Exemption Goal: ${profile.target_score}%")
html = html.replace("${best720} / 720", "${best720}%")
html = html.replace("Avg: ${avg720} / 720", "Avg: ${avg720}% (Pass: 50% Agg)")
html = html.replace("Math.round((Math.max(0, a.projected_720) / 720) * 100)", "Math.max(8, Math.min(100, Math.round(Math.max(0, a.projected_720))))")
html = html.replace("const rollup = { Physics: { c: 0, t: 0 }, Chemistry: { c: 0, t: 0 }, Botany: { c: 0, t: 0 }, Zoology: { c: 0, t: 0 } };", "const rollup = { 'CA Foundation': { c: 0, t: 0 }, 'CA Inter G1': { c: 0, t: 0 }, 'CA Inter G2': { c: 0, t: 0 }, 'CA Final & SPOM': { c: 0, t: 0 } };")
html = html.replace("${a.projected_720}/720", "${a.projected_720}%")
html = html.replace("${a.projected_720} / 720", "${a.projected_720}%")

# Update renderPyqArchiveHub for CA subjects
old_pyq_kpis = """      kpiWrap.innerHTML = `
        <div class="kpi-card">
          <div class="kpi-label">Total Archive Questions</div>
          <div class="kpi-value" style="color:var(--primary);">${totalPyq.toLocaleString()}</div>
          <div class="kpi-note">${officialPyq.toLocaleString()} Official PYQs + ${exCoachCount.toLocaleString()} Exemplar/Mocks</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Official Past Booklets</div>
          <div class="kpi-value">${totalPapers} Papers</div>
          <div class="kpi-note">2000–2026 NEET, Re-NEET, AIPMT &amp; தமிழ் (${meta.tamilBookletQuestions || 651} Qs)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Biology Pool (Bot + Zoo)</div>
          <div class="kpi-value">${((subjCounts.Botany || 0) + (subjCounts.Zoology || 0)).toLocaleString()}</div>
          <div class="kpi-note">Botany: ${subjCounts.Botany || 0} • Zoology: ${subjCounts.Zoology || 0}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Physics &amp; Chemistry Pool</div>
          <div class="kpi-value">${((subjCounts.Physics || 0) + (subjCounts.Chemistry || 0)).toLocaleString()}</div>
          <div class="kpi-note">Physics: ${subjCounts.Physics || 0} • Chemistry: ${subjCounts.Chemistry || 0}</div>
        </div>
      `;"""

new_pyq_kpis = """      kpiWrap.innerHTML = `
        <div class="kpi-card">
          <div class="kpi-label">Total ICAI Questions</div>
          <div class="kpi-value" style="color:var(--primary);">${BANK.questions.length.toLocaleString()}</div>
          <div class="kpi-note">Foundation • Inter G1 &amp; G2 • Final &amp; SPOM</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">ICAI Past Papers &amp; RTPs</div>
          <div class="kpi-value">${Object.keys(BANK.modules).length} Modules</div>
          <div class="kpi-note">2019–2026 Past Cycles, RTPs, MTPs &amp; Case Scenarios</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Foundation &amp; Inter G1</div>
          <div class="kpi-value">${((subjCounts["CA Foundation"] || 0) + (subjCounts["CA Inter G1"] || 0)).toLocaleString()}</div>
          <div class="kpi-note">Foundation: ${subjCounts["CA Foundation"] || 0} • Inter G1: ${subjCounts["CA Inter G1"] || 0}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Inter G2 &amp; Final/SPOM</div>
          <div class="kpi-value">${((subjCounts["CA Inter G2"] || 0) + (subjCounts["CA Final & SPOM"] || 0)).toLocaleString()}</div>
          <div class="kpi-note">Inter G2: ${subjCounts["CA Inter G2"] || 0} • Final/SPOM: ${subjCounts["CA Final & SPOM"] || 0}</div>
        </div>
      `;"""
html = html.replace(old_pyq_kpis, new_pyq_kpis)

old_sprint_ids = """        const sprintIds = [
          "pyq_controversial_2024_2026",
          "mock_abhyas_cbt_full",
          "coaching_pcb_chapter_pack",
          "exemplar_bio_class11",
          "exemplar_bio_class12",
          "ncert_line_by_line_bio",
          "pyq_sprint_botany",
          "pyq_sprint_zoology",
          "pyq_sprint_chemistry",
          "pyq_sprint_physics"
        ];"""

new_sprint_ids = """        const sprintIds = Object.keys(BANK.modules).filter(id => !BANK.modules[id].isPastPaper || BANK.modules[id].isControversialModule).slice(0, 10);"""
html = html.replace(old_sprint_ids, new_sprint_ids)

html = html.replace(
    '["Botany", "Zoology", "Chemistry", "Physics"].map(subj =>',
    '["CA Foundation", "CA Inter G1", "CA Inter G2", "CA Final & SPOM"].map(subj =>',
)
html = html.replace(
    "const dossierList = analytics.disputedQuestionsDossier",
    "const dossierList = (PYQ_ARCHIVE.disputedQuestionsDossier || analytics.disputedQuestionsDossier || [])",
)
html = html.replace(
    "if (dossierGrid && Array.isArray(analytics.disputedQuestionsDossier)) {\n        dossierGrid.innerHTML = analytics.disputedQuestionsDossier.map(",
    "const dList = PYQ_ARCHIVE.disputedQuestionsDossier || analytics.disputedQuestionsDossier || [];\n      if (dossierGrid && Array.isArray(dList)) {\n        dossierGrid.innerHTML = dList.map(",
)

old_filter_papers = """      const filtered = papers.filter(m => {
        const isTa = m.paperLanguage === "ta" || m.id.startsWith("pyq_ta_") || m.id.endsWith("_ta");
        if (filterKey === "recent") return !isTa && (m.examYear || 0) >= 2020;
        if (filterKey === "ta") return isTa;
        if (filterKey === "classic") return !isTa && (m.examYear || 0) >= 2013 && (m.examYear || 0) < 2020;
        if (filterKey === "aipmt") return !isTa && (m.examYear || 0) < 2013;
        return true;
      });"""

new_filter_papers = """      const filtered = papers.filter(m => {
        const isTa = m.paperLanguage === "ta" || m.id.includes("_ta");
        if (filterKey === "recent") return !isTa && (m.examYear || 0) >= 2024;
        if (filterKey === "ta") return isTa;
        if (filterKey === "classic") return !isTa && (m.examYear || 0) < 2024;
        if (filterKey === "aipmt") return Boolean(m.isExemplarOrCoaching || m.id.includes("rtp") || m.id.includes("spom") || m.id.includes("ibs"));
        return true;
      });"""
html = html.replace(old_filter_papers, new_filter_papers)

html = html.replace("if (/^NEET-[A-Z0-9]{4,10}$/.test(cleanCode)", "if (/^(CA|NEET)-[A-Z0-9]{4,10}$/.test(cleanCode)")
html = html.replace(
    'const DEFAULT_TUNNEL_URL = "https://wallpapers-regular-gallery-dash.trycloudflare.com";',
    'const DEFAULT_TUNNEL_URL = "https://same-reasonably-graduates-passengers.trycloudflare.com";',
)

(CA_DIR / "index.html").write_text(html, encoding="utf-8")
shutil.copyfile(CA_DIR / "index.html", CA_DIR / "ca_interactive_practice.html")

manifest = {
    "name": "Tamil Nadu ICAI CA Mastery Hub — Foundation, Inter, Final & SPOM + Bilingual AI Coach",
    "short_name": "TN CA Hub",
    "start_url": "./index.html",
    "display": "standalone",
    "background_color": "#0f172a",
    "theme_color": "#0f172a",
    "description": "ICAI Chartered Accountancy New Scheme Mock Exams, Case Scenarios, RTP/MTP Archive, TAHDCO & SIRC TN Public Coaching Guide, and 24/7 Bilingual Tamil+English Gemini AI Coach.",
}
(CA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(CA_DIR / "CNAME").write_text("caprep.memnos.net\n", encoding="utf-8")
(CA_DIR / ".gitignore").write_text("ca_data.db\nca_data.db-*\n__pycache__/\n*.pyc\n.DS_Store\n", encoding="utf-8")
print("Generated /Users/thameema/git/ca-prep/index.html, ca_interactive_practice.html, manifest.json, and .gitignore successfully!")
