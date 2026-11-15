#!/usr/bin/env python3
"""Build the Tamil Nadu CA Mastery Hub question bank + past-papers archive.

Outputs (repo root): questions_bank.json, questions_database.js, past_papers_archive.json, past_papers_database.js
Inputs (this folder): ca_templates.py (computed numeric items), ca_statutory.py (hand-authored items).
Run:  python3 scripts/build_ca_question_bank.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ca_statutory as st  # noqa: E402
import ca_templates as tp  # noqa: E402

F, G1, G2, FIN = "CA Foundation", "CA Inter G1", "CA Inter G2", "CA Final & SPOM"
LEVEL = {F: "Level 1 — CA Foundation", G1: "Level 2 — CA Inter Group I", G2: "Level 2 — CA Inter Group II", FIN: "Level 3 — CA Final / SPOM"}
SUBJ = {1: F, 2: G1, 3: G2, 4: FIN}
CATS = {"N": "Numerical / Working Note Computation", "S": "Statutory Section & Exception Trap",
        "A": "Accounting / Auditing Standard (AS/Ind AS/SA)", "L": "Landmark Case Law Application", "C": "Case-Scenario MCQ (2M)"}
PYQ = ["ICAI RTP May 2026 / Nov 2025", "ICAI Past Paper Sep 2025", "ICAI MTP Series I — 2026", "ICAI Case Scenario Digest", "ICAI Past Paper Jan 2026"]
VIDEOS = [("CA in Tamil", "https://www.youtube.com/@CAinTamil"), ("ICAI CA Tube", "https://www.youtube.com/@icai_ca_tube"), ("KPG Classes", "https://www.youtube.com/@KPGClasses")]
LETTERS = "ABCD"

# numeric bank slots: id -> (template, chapter, ref, tags, difficulty)
NUM = {
    101: ("f_ci", "Paper 3: Quantitative Aptitude — Time Value of Money (Compound Interest)", "ICAI BoS — Business Mathematics, Compound Interest", "qa", "Medium"),
    102: ("f_dep", "Paper 1: Accounting — Depreciation Accounting (AS 10 / Ind AS 16)", "ICAI BoS — Accounting, Depreciation (SLM)", "acc", "Easy"),
    103: ("f_wmean", "Paper 3: Quantitative Aptitude — Statistical Description (Weighted Mean)", "ICAI BoS — Business Statistics, Measures of Central Tendency", "qa", "Medium"),
    104: ("f_elast", "Paper 4: Business Economics — Theory of Demand (Elasticity)", "ICAI BoS — Business Economics, Elasticity of Demand", "eco", "Medium"),
    105: ("f_comb", "Paper 3: Quantitative Aptitude — Permutations & Combinations", "ICAI BoS — Business Mathematics, Permutations & Combinations", "qa", "Easy"),
    106: ("f_pv", "Paper 3: Quantitative Aptitude — Time Value of Money (Present Value)", "ICAI BoS — Business Mathematics, Time Value of Money", "qa", "Medium"),
    107: ("f_stock", "Paper 1: Accounting — Inventory Valuation (AS 2)", "ICAI BoS — AS 2 Valuation of Inventories", "acc", "Medium"),
    108: ("f_margin", "Paper 1: Accounting — Mark-up and Margin", "ICAI BoS — Accounting, Profit Concepts", "acc", "Easy"),
    201: ("g_goodwill", "Paper 1: Advanced Accounting — Partnership: Valuation of Goodwill", "ICAI BoS — Advanced Accounting, Partnership Accounts (Super Profit Method)", "acc", "Medium"),
    202: ("g_tax_new", "Paper 3: Taxation — Income Tax Sec 115BAC & Heads of Income", "ICAI BoS — Income-tax Act 1961, Sec 115BAC(1A) (AY 2026-27)", "tax", "Hard"),
    203: ("g_gst", "Paper 3: Taxation — GST Payment of Tax & ITC Set-off", "ICAI BoS — CGST Act 2017, Sec 49 & Sec 16", "tax", "Medium"),
    204: ("g_wdv", "Paper 1: Advanced Accounting — Depreciation (Written Down Value)", "ICAI BoS — AS 10 / Ind AS 16 Depreciation", "acc", "Easy"),
    205: ("g_hp", "Paper 3: Taxation — Income from House Property", "ICAI BoS — Income-tax Act 1961, Sec 22–24", "tax", "Medium"),
    301: ("c_eoq", "Paper 4: Cost & Management Accounting — Material Cost (EOQ)", "ICAI BoS — Cost & Management Accounting, Inventory Control", "cost", "Medium"),
    302: ("c_bep", "Paper 4: Cost & Management Accounting — Marginal Costing & CVP", "ICAI BoS — Cost & Management Accounting, Break-even Analysis", "cost", "Easy"),
    303: ("c_mpv", "Paper 4: Cost & Management Accounting — Standard Costing (Material Variance)", "ICAI BoS — Cost & Management Accounting, Standard Costing", "cost", "Hard"),
    304: ("c_wacc", "Paper 6: Financial Management — Cost of Capital (WACC)", "ICAI BoS — Financial Management, Cost of Capital", "afm", "Medium"),
    305: ("c_opcycle", "Paper 6: Financial Management — Working Capital (Operating Cycle)", "ICAI BoS — Financial Management, Working Capital Management", "afm", "Medium"),
    306: ("c_process", "Paper 4: Cost & Management Accounting — Process Costing (Normal Loss)", "ICAI BoS — Cost & Management Accounting, Process Costing", "cost", "Hard"),
    307: ("c_capm", "Paper 6: Financial Management — Cost of Equity (CAPM)", "ICAI BoS — Financial Management, CAPM", "afm", "Easy"),
    401: ("l_lease", "Paper 1: Financial Reporting — Ind AS 115 & Ind AS 116 (Lease Liability)", "ICAI BoS — Ind AS 116 Leases", "acc", "Hard"),
    402: ("l_ifrs15", "Paper 1: Financial Reporting — Ind AS 115 & Ind AS 116 (Revenue Allocation)", "ICAI BoS — Ind AS 115 Revenue from Contracts with Customers", "acc", "Medium"),
    403: ("l_ltcg", "Paper 4: Direct Tax & International Tax — Capital Gains (Sec 112A)", "ICAI BoS — Income-tax Act 1961, Sec 112A (post 23-Jul-2024)", "tax", "Medium"),
    404: ("l_fx", "Paper 2: Advanced Financial Management — Foreign Exchange Risk (IRP)", "ICAI BoS — AFM, Foreign Exchange Exposure & Interest Rate Parity", "afm", "Hard"),
    405: ("l_effint", "Paper 1: Financial Reporting — Ind AS 109 Financial Instruments (Amortised Cost)", "ICAI BoS — Ind AS 109 Financial Instruments", "acc", "Hard"),
}

META = {}  # id -> {"cat","tags"}  (kept out of the JSON)


def video(sub, tags, chapter):
    ch = VIDEOS[1] if "tax" in tags else VIDEOS[2] if tags & {"cost", "afm"} else VIDEOS[0]
    topic = chapter.split("—", 1)[-1].strip()
    return {"title": f"{topic} — concept revision ({LEVEL[sub]})", "channel": ch[0], "url": ch[1]}


def assemble(qid, chapter, ref, pyq, diff, tags, cat, en, ta, ch_en, ch_ta, ans_idx, xe, xt, tip, wrong):
    sub = SUBJ[qid % 10000 // 100]
    tags = set(tags.split(",")) if isinstance(tags, str) else set(tags)
    assert 0 <= ans_idx < 4 and len(wrong) == 3
    wl = [l for i, l in enumerate(LETTERS) if i != ans_idx]
    scen = cat == "C"
    qtype = ("Numerical / Computation MCQ" if cat == "N" else "Case-Scenario MCQ (2M, 0 Neg)" if scen and sub != F
             else "Foundation Objective MCQ (+1 / -0.25)" if sub == F else "Statutory Provision & Case Law MCQ")
    META[qid] = {"cat": cat, "tags": tags}
    return {
        "id": qid, "subject": sub, "classLevel": LEVEL[sub], "chapter": chapter, "ncertRef": ref,
        "pyqTag": f"{pyq} (pattern-based)", "questionType": qtype, "difficulty": diff, "stem_en": en, "stem_ta": ta,
        "choices": [{"letter": L, "text_en": ch_en[i], "text_ta": ch_ta[i]} for i, L in enumerate(LETTERS)],
        "correct": LETTERS[ans_idx], "explanation_en": xe, "explanation_ta": xt, "ncert_key_point": tip,
        "trap_breakdown": dict(zip(wl, wrong)), "videoTutorial": video(sub, tags, chapter),
    }


def from_stat(t):
    qid, ch, ref, pyq, diff, tags, cat, en, ta, chs, ans, xe, xt, tip, traps = t
    pairs = [c.split("|", 1) if "|" in c else [c, c] for c in chs]
    a = LETTERS.index(ans)
    ok = pairs[a]
    wrong = [(pr, traps[i]) for i, pr in enumerate(x for k, x in enumerate(pairs) if k != a)]
    pos = qid % 4  # rebalance correct-letter distribution; each trap reason stays with its own option
    order = [w[0] for w in wrong]
    order.insert(pos, ok)
    return assemble(qid, ch, ref, pyq, diff, tags, cat, en, ta, [p[0].strip() for p in order], [p[1].strip() for p in order],
                    pos, xe, xt, tip, [w[1] for w in wrong])


def from_num(qid, tmpl_name, j, pyq):
    """j = parameter-set index; qid = bank id (j=0) or variant id."""
    base = qid % 10000
    func, sets = tp.TEMPLATES[tmpl_name]
    p = sets[j]
    d = func(j, p) if isinstance(p, list) else func(j, *p)
    _, ch, ref, tags, diff = NUM[base]
    pos = (base * 3 + j) % 4
    texts = list(d["bad"])
    texts.insert(pos, d["ok"])
    assert len(set(texts)) == 4, (qid, texts)
    texts_ta = [t.replace(" units", " அலகுகள்").replace(" days", " நாட்கள்") for t in texts]
    return assemble(qid, ch, ref, pyq, diff, tags, "N", d["en"], d["ta"], texts, texts_ta, pos, d["xe"], d["xt"], d["tip"], d["tr"])


def pick(ids, n):
    return [ids[int(k * len(ids) / n)] for k in range(n)]


# ------------------------------------------------------------------ bank
def build_bank():
    qs = []
    for base, (tn, *_r) in NUM.items():
        qs.append(from_num(base, tn, 0, PYQ[base % 5]))
    for lst in (st.FOUNDATION, st.INTER_G1, st.INTER_G2, st.FINAL):
        qs.extend(from_stat(t) for t in lst)
    qs.sort(key=lambda q: q["id"])
    by = defaultdict(list)
    for q in qs:
        by[q["subject"]].append(q["id"])
    ids = lambda pred: [q["id"] for q in qs if pred(META[q["id"]]["tags"])]  # noqa: E731
    mk = lambda title, mode, mins, corr, wrong, qids: {"title": title, "name": title, "mode": mode, "durationMinutes": mins,  # noqa: E731
                                                       "marking": {"correct": corr, "wrong": wrong, "unanswered": 0}, "questionIds": qids}
    TA = {"ca_all_levels_mock_1": "ICAI அனைத்து நிலை விரிவான கண்டறியும் மாதிரித் தேர்வு (ஃபவுண்டேஷன் + இன்டர் + ஃபைனல்)",
          "ca_foundation_mock_1": "நிலை 1: CA ஃபவுண்டேஷன் முழு மாதிரித் தேர்வு (தாள் 1–4 • -0.25 எதிர்மறை மதிப்பெண்)",
          "ca_inter_g1_mock": "நிலை 2A: CA இன்டர் குரூப் I வழக்குச் சூழல் மாதிரித் தேர்வு (மேம்பட்ட கணக்கியல், நிறுவனச் சட்டம், வரி AY 2026-27 & GST)",
          "ca_inter_g2_mock": "நிலை 2B: CA இன்டர் குரூப் II வழக்குச் சூழல் மாதிரித் தேர்வு (செலவியல், தணிக்கை SA, நிதி & உத்தி மேலாண்மை)",
          "ca_final_spom_mock": "நிலை 3: CA ஃபைனல் (குரூப் I & II + IBS) & SPOM A–D வழக்குச் சூழல் மாதிரித் தேர்வு",
          "ca_tax_gst_drill": "அதிக முக்கியத்துவ வருமான வரி (Sec 115BAC AY 2026-27) & CGST ITC Sec 16/17 பயிற்சி",
          "ca_law_audit_drill": "நிறுவனச் சட்டம் 2013, ஒப்பந்தச் சட்டம், IBC 2016 & தணிக்கைத் தரநிலைகள் (SA) பயிற்சி",
          "ca_accounts_afm_cost_drill": "கணக்கியல் தரநிலைகள் (AS / Ind AS 115, 116, 109), செலவியல் & AFM கணக்கீட்டுப் பயிற்சி"}
    mods = {
        "ca_all_levels_mock_1": mk("ICAI All-Levels Comprehensive Diagnostic Mock (Foundation + Inter + Final)", "mock", 90, 2, -0.25,
                                   pick(by[F], 15) + pick(by[G1], 15) + pick(by[G2], 12) + pick(by[FIN], 18)),
        "ca_foundation_mock_1": mk("Level 1: CA Foundation Full Mock (Papers 1–4 • -0.25 Negative Marking)", "mock", 45, 1, -0.25, by[F]),
        "ca_inter_g1_mock": mk("Level 2A: CA Intermediate Group I Case-Scenario Mock (Adv Accounts, Corp Law, Tax AY 2026-27 & GST)", "mock", 45, 2, 0, by[G1]),
        "ca_inter_g2_mock": mk("Level 2B: CA Intermediate Group II Case-Scenario Mock (Costing, Auditing SAs, FM & SM)", "mock", 40, 2, 0, by[G2]),
        "ca_final_spom_mock": mk("Level 3: CA Final (Group I & II + IBS) & SPOM Sets A–D Case-Scenario Mock", "mock", 50, 2, 0, by[FIN]),
        "ca_tax_gst_drill": mk("High-Yield Income Tax (Sec 115BAC AY 2026-27) & CGST ITC Sec 16/17 Drill", "practice", 30, 2, 0, ids(lambda t: "tax" in t)),
        "ca_law_audit_drill": mk("Companies Act 2013, Contract Act, IBC 2016 & Standards on Auditing (SAs) Drill", "practice", 30, 2, 0, ids(lambda t: bool(t & {"law", "audit"}))),
        "ca_accounts_afm_cost_drill": mk("Accounting Standards (AS / Ind AS 115, 116, 109), Costing & AFM Numericals Drill", "practice", 30, 2, -0.25, ids(lambda t: bool(t & {"acc", "cost", "afm"}))),
    }
    for k, m in mods.items():
        m["id"], m["title_ta"] = k, TA[k]
        m["description"] = f"{len(m['questionIds'])} questions • {m['durationMinutes']} min • {m['mode']} mode. Original exam-pattern items (bilingual English + Tamil)."
    meta = {
        "exam": "ICAI Chartered Accountancy (New Scheme — Foundation, Intermediate, Final & SPOM)",
        "region": "Tamil Nadu (SIRC of ICAI — Bilingual English + Tamil Explanations)",
        "totalQuestionsInBank": len(qs), "subjectCounts": {s: len(by[s]) for s in (F, G1, G2, FIN)},
        "markingScheme": {"correct": 2, "incorrect": -0.25, "unanswered": 0, "fullExamMaxMarks": 100, "paperMinPassPct": 40, "groupAggregatePassPct": 50, "exemptionPct": 60},
        "disclaimer": "Original exam-pattern practice questions authored for this hub; they are NOT verbatim ICAI papers. 'pyqTag' marks the cycle/series the item is modelled on. Verify statutory limits and exam-scheme rules against the latest ICAI/CBDT/CBIC/MCA notifications before relying on them.",
    }
    return {"metadata": meta, "modules": mods, "questions": qs}


# ------------------------------------------------------------------ archive
PAPERS = [  # id, title, label, year, cycle, kind, language, subjects
    ("rtp_may_2026", "ICAI RTP May 2026 — All Levels (pattern set)", "ICAI RTP May 2026", 2026, "May", "rtp", "English + Tamil", [F, G1, G2, FIN]),
    ("exam_jan_2026", "Jan 2026 Exam — Foundation & Inter Group I (pattern set)", "ICAI Exam Jan 2026", 2026, "Jan", "exam", "English + Tamil", [F, G1]),
    ("rtp_nov_2025", "ICAI RTP Nov 2025 — Foundation, Inter G1 & Final (pattern set)", "ICAI RTP Nov 2025", 2025, "Nov", "rtp", "English + Tamil", [F, G1, FIN]),
    ("exam_sep_2025", "Sep 2025 Exam — Inter Groups I & II (pattern set)", "ICAI Exam Sep 2025", 2025, "Sep", "exam", "English + Tamil", [G1, G2]),
    ("exam_may_2025", "May 2025 Exam — Final & SPOM (pattern set)", "ICAI Exam May 2025", 2025, "May", "exam", "English + Tamil", [FIN]),
    ("mtp_series2_2025", "ICAI MTP Series II 2025 — Inter & Final (pattern set)", "ICAI MTP Series II 2025", 2025, "Oct", "mtp", "English + Tamil", [G1, G2, FIN]),
    ("exam_nov_2024", "Nov 2024 Exam — Inter G2 & Final (pattern set)", "ICAI Exam Nov 2024", 2024, "Nov", "exam", "English + Tamil", [G2, FIN]),
    ("exam_may_2024_new_scheme", "May 2024 New Scheme Inaugural Exam — Foundation & Inter (pattern set)", "ICAI New Scheme May 2024", 2024, "May", "exam", "English + Tamil", [F, G1, G2]),
    ("exam_nov_2023", "Nov 2023 Exam — Inter G1 & Final (pattern set)", "ICAI Exam Nov 2023", 2023, "Nov", "exam", "English + Tamil", [G1, FIN]),
    ("exam_may_2023", "May 2023 Exam — Inter Groups I & II (pattern set)", "ICAI Exam May 2023", 2023, "May", "exam", "English + Tamil", [G1, G2]),
    ("exam_nov_2022", "Nov 2022 Exam — Foundation & Inter G2 (pattern set)", "ICAI Exam Nov 2022", 2022, "Nov", "exam", "English + Tamil", [F, G2]),
    ("exam_may_2022", "May 2022 Exam — Inter G1 & Final (pattern set)", "ICAI Exam May 2022", 2022, "May", "exam", "English + Tamil", [G1, FIN]),
    ("exam_nov_2021", "Nov 2021 Exam — Inter G2 & Final (pattern set)", "ICAI Exam Nov 2021", 2021, "Nov", "exam", "English + Tamil", [G2, FIN]),
    ("exam_nov_2020", "Nov 2020 Exam — Foundation & Inter G1 (pattern set)", "ICAI Exam Nov 2020", 2020, "Nov", "exam", "English + Tamil", [F, G1]),
    ("exam_nov_2019", "Nov 2019 Exam — Inter Groups I & II (pattern set)", "ICAI Exam Nov 2019", 2019, "Nov", "exam", "English + Tamil", [G1, G2]),
    ("mtp_series1_2026", "ICAI MTP Series I 2026 — All Levels (pattern set)", "ICAI MTP Series I 2026", 2026, "Mar", "mtp", "English + Tamil", [F, G1, G2, FIN]),
    ("booklet_foundation_ta", "Tamil Bilingual Concept Booklet — CA Foundation", "Tamil Concept Booklet — Foundation", 2026, "Booklet", "booklet", "Tamil + English", [F]),
    ("booklet_inter_ta", "Tamil Bilingual Concept Booklet — CA Intermediate", "Tamil Concept Booklet — Inter", 2026, "Booklet", "booklet", "Tamil + English", [G1, G2]),
]


ORIGIN = {}  # archive question id -> source id (bank id, or variant id) ; used for analytics + arithmetic verification
TA_MON = {"Jan": "ஜனவரி", "May": "மே", "Sep": "செப்டம்பர்", "Nov": "நவம்பர்", "Mar": "மார்ச்", "Oct": "அக்டோபர்"}
TA_LVL = {F: "ஃபவுண்டேஷன்", G1: "இன்டர் குரூப் I", G2: "இன்டர் குரூப் II", FIN: "ஃபைனல் & SPOM"}
GROUPS = {"exam": "ICAI Exam-Cycle Pattern Sets (2019–2026)", "rtp": "ICAI RTP Pattern Sets", "mtp": "ICAI MTP Pattern Sets",
          "booklet": "Tamil Bilingual Concept Booklets", "special": "Special Revision Modules"}
NOTE = ("Original exam-pattern items, not verbatim ICAI text. All items apply current law (FY 2025-26 / AY 2026-27) "
        "irrespective of the cycle label, which indicates style and level mix only.")


def build_archive(bank):
    bq = {q["id"]: q for q in bank["questions"]}
    by = defaultdict(list)
    for q in bank["questions"]:
        by[q["subject"]].append(q["id"])
    # 1) variants: parameter sets 1..4 of every numeric template, each owned by exactly one paper
    owned = {p[0]: [] for p in PAPERS}
    src = dict(bq)
    for j in (1, 2, 3, 4):
        for base in sorted(NUM):
            sub = SUBJ[base // 100]
            p = min((c for c in PAPERS if sub in c[7]), key=lambda c: (len(owned[c[0]]), c[0]))
            vid = 10000 * j + base
            src[vid] = from_num(vid, NUM[base][0], j, p[2])
            owned[p[0]].append(vid)
    arc, first, paper_q = [], {}, {}
    ORIGIN.clear()

    def copy(sid, paper_id, title, year, lang, tag):
        q = src[sid]
        o = {"id": 1001 + len(arc), "examYear": year, "paperId": paper_id, "paperTitle": title, "language": lang}
        o.update({k: v for k, v in q.items() if k not in ("id", "pyqTag")})
        o.update({"isOutOfSyllabus": False, "answerStatus": "normal", "acceptedOptions": [q["correct"]], "pyqTag": tag})
        arc.append(o)
        ORIGIN[o["id"]] = sid
        first.setdefault(sid, o["id"])
        return o["id"]

    # 2) fill each paper with bank questions to 15..22
    for i, p in enumerate(PAPERS):
        pid, title, label, year, cycle, kind, lang, subs = p
        ids = list(owned[pid])
        pool = [x for s in subs for x in by[s]]
        target, k = 15 + (i * 3) % 8, 0
        while len(ids) < target and k < 10 * len(pool):
            cand = pool[(i * 5 + k * 2) % len(pool)]
            k += 1
            if cand not in ids:
                ids.append(cand)
        tag = f"{label} (pattern-based)"
        paper_q[pid] = [copy(sid, pid, title, year, "ta" if kind == "booklet" else "en", tag) for sid in ids]
    # 3) special modules (reuse existing copies; add copies only for questions not in any paper)
    tg = lambda i: META[i]["tags"]  # noqa: E731
    special = {
        "icai_landmark_caselaws": ("Landmark Case Laws — Mohori Bibee, Carlill, Hadley v Baxendale & Statutory Case Applications",
                                   "முக்கிய வழக்குச் சட்டங்கள் — Mohori Bibee, Carlill, Hadley v Baxendale மற்றும் சட்டப் பயன்பாட்டு வினாக்கள்",
                                   "Case-law and case-scenario questions from Contract Act, Companies Act, SEBI SAST and IBC.",
                                   [i for i in sorted(bq) if META[i]["cat"] in ("L", "C") and "law" in tg(i)]),
        "icai_rtp_mtp_2026_capsule": ("RTP / MTP 2026 Capsule — Quick Revision Across Levels", "RTP / MTP 2026 சுருக்கத் திருப்புதல் — அனைத்து நிலைகள்",
                                      "Union of the May 2026 RTP and MTP Series I 2026 pattern sets.", None),
        "icai_amendments_ay2026_27": ("Amendments Digest AY 2026-27 — Sec 115BAC, 87A, 112A/111A, GST Sec 16/17",
                                      "திருத்தங்கள் AY 2026-27 — Sec 115BAC, 87A, 112A/111A, GST Sec 16/17",
                                      "All tax and GST questions with current-year rates and limits.", [i for i in sorted(bq) if "tax" in tg(i)]),
        "icai_spom_set_ab_cbt": ("SPOM Sets A/B CBT Style — IBC 2016, SEBI SAST/LODR & Corporate Law", "SPOM தொகுப்பு A/B CBT பாணி — IBC 2016, SEBI SAST/LODR, நிறுவனச் சட்டம்",
                                 "IBC, SEBI and Companies Act questions in CBT style.", [426, 427, 428, 429, 430, 211, 212, 213, 214, 215, 217]),
        "icai_ibs_case_studies": ("IBS Multidisciplinary Case-Scenario Drill — Law + Tax + Reporting + Audit", "IBS பல்துறை வழக்கு வினாக்கள் — சட்டம் + வரி + அறிக்கையிடல் + தணிக்கை",
                                  "Cross-discipline case questions in the style of CA Final Paper 6.", [401, 402, 403, 404, 405, 409, 410, 411, 417, 420, 422, 424, 425, 429, 430]),
        "icai_foundation_neg_marking_drill": ("Foundation Objective Papers 3 & 4 — Negative Marking (-0.25) Practice", "ஃபவுண்டேஷன் தாள் 3 & 4 — எதிர்மறை மதிப்பெண் (-0.25) பயிற்சி",
                                              "All Foundation questions with negative-marking drill.", [i for i in sorted(bq) if i // 100 == 1]),
    }
    mods = {}
    for p in PAPERS:
        pid, title, label, year, cycle, kind, lang, subs = p
        ids = paper_q[pid]
        mode = "mock" if kind == "exam" else "practice"
        lv = " + ".join(TA_LVL[s] for s in subs)
        ta = {"exam": "தேர்வு", "rtp": "RTP", "mtp": "MTP", "booklet": "தமிழ் கருத்துக் கையேடு"}[kind]
        title_ta = (f"தமிழ் இருமொழி கருத்துக் கையேடு — {lv}" if kind == "booklet"
                    else f"{TA_MON[cycle]} {year} {ta} — {lv} (மாதிரி வினாத்தொகுப்பு)")
        mods[pid] = {"id": pid, "title": title, "title_ta": title_ta, "group": GROUPS[kind], "mode": mode, "isPastPaper": True,
                     "isPatternSet": True, "examYear": year, "paperLanguage": "ta" if kind == "booklet" else "en",
                     "durationMinutes": round(len(ids) * 1.5), "marking": {"correct": 2, "wrong": -0.25 if mode == "mock" else 0, "unanswered": 0},
                     "description": f"{len(ids)} questions modelled on the {label} pattern. " + NOTE, "questionIds": ids}
    for mid, (t, tta, desc, bases) in special.items():
        if bases is None:
            ids = sorted(set(paper_q["rtp_may_2026"]) | set(paper_q["mtp_series1_2026"]))
        else:
            ids = [first[b] if b in first else copy(b, mid, t, 2026, "en", "ICAI Special Module 2026 (pattern-based)") for b in bases]
        mods[mid] = {"id": mid, "title": t, "title_ta": tta, "group": GROUPS["special"], "mode": "practice", "isPastPaper": False,
                     "isExemplarOrCoaching": True, "isControversialModule": mid == "icai_landmark_caselaws", "examYear": 2026,
                     "paperLanguage": "en", "durationMinutes": round(len(ids) * 1.5), "marking": {"correct": 2, "wrong": 0, "unanswered": 0},
                     "description": desc + " " + NOTE, "questionIds": ids}
    cat = lambda q: CATS[META[ORIGIN[q["id"]]]["cat"]]  # noqa: E731
    overall = Counter(cat(q) for q in arc)
    yr = defaultdict(Counter)
    for q in arc:
        yr[q["examYear"]][cat(q)] += 1
    years = list(range(2019, 2027))
    qty = {}
    for y in years:
        c, tot = dict(yr.get(y, {})), sum(yr.get(y, {}).values())
        qty[str(y)] = {"total": tot, "counts": c, "pct": {k: round(100 * v / tot, 1) for k, v in c.items()} if tot else {}}
    top = {}
    for s in (F, G1, G2, FIN):
        c = Counter(q["chapter"] for q in arc if q["subject"] == s)
        tot = sum(c.values())
        top[s] = [{"chapter": ch, "count": n, "sharePct": round(100 * n / tot, 1)} for ch, n in c.most_common(5)]
    kind_of = {p[0]: p[5] for p in PAPERS}
    cnt = lambda f: sum(1 for q in arc if f(q))  # noqa: E731
    meta = {
        "title": "Official ICAI Past Exam Papers, RTPs (Revision Test Papers), MTPs & Case-Scenario Archive (2018–2026)",
        "totalQuestions": len(arc),
        "officialPyqQuestions": 0,
        "patternSetQuestions": cnt(lambda q: kind_of.get(q["paperId"]) == "exam"),
        "englishQuestions": cnt(lambda q: q["language"] == "en"),
        "tamilBookletQuestions": cnt(lambda q: q["language"] == "ta"),
        "exemplarAndCoachingQuestions": cnt(lambda q: kind_of.get(q["paperId"], "special") in ("rtp", "mtp", "special")),
        "totalPapers": len(PAPERS), "specialModulesCount": len(special), "yearsCovered": years,
        "subjectCounts": dict(Counter(q["subject"] for q in arc)),
        "sources": ["ICAI Board of Studies study material, RTPs and MTPs (icai.org) — syllabus and topic coverage",
                    "Income-tax Act 1961 (Finance Act 2025, AY 2026-27); CGST/IGST Acts 2017; Companies Act 2013; IBC 2016; SEBI SAST/LODR; Ind AS/AS/SA",
                    "All questions are original exam-pattern items (bilingual) authored for this hub, not verbatim ICAI papers; "
                    "titles marked '(pattern set)' reflect the cycle's style, not its actual question list."],
        "disclaimer": "officialPyqQuestions is 0 by design: no verbatim ICAI paper text is reproduced. " + NOTE + " Confirm all dates, limits and scheme rules on icai.org.",
    }
    V = "Confirm against the latest ICAI announcement."
    dossier = [
        {"exam": "Finance Act 2025 — AY 2026-27", "qNum": "Income Tax: Sec 115BAC(1A) default regime vs old regime", "subject": G1, "chapter": "Paper 3: Taxation — Income Tax Sec 115BAC & Heads of Income",
         "status": "High-failure trap", "acceptedKey": "New regime is default: slabs 0–4L nil … >24L 30%; std deduction ₹75,000; 87A rebate up to ₹60,000 if income ≤ ₹12L; 80CCD(2) allowed; add 4% cess. Old regime only if opted.",
         "summary": "Students apply 80C/80D/HRA and old slabs by habit although the new regime is the default; they also forget cess. Read 'default / opted out' in the stem first.", "linkedQuestionIds": [202, 222, 223]},
        {"exam": "CGST Act 2017 — Sec 17(5) / 16", "qNum": "Blocked credit exceptions, ITC time limit and 180-day rule", "subject": G1, "chapter": "Paper 3: Taxation — GST Input Tax Credit",
         "status": "Examiner favourite", "acceptedKey": "Motor vehicles (≤13 persons), food & beverages, club membership etc. are blocked, except the statutory exceptions (further supply, passenger transport, driving training; where obligatory under law). ITC: Sec 16(4) deadline 30 Nov; reverse if unpaid in 180 days.",
         "summary": "Treating the block as absolute, or ignoring the time limit and payment condition.", "linkedQuestionIds": [219, 220, 425]},
        {"exam": "Companies Act 2013 — Sec 185 / 186", "qNum": "Loans to directors vs exemptions", "subject": G1, "chapter": "Paper 2: Corporate & Other Laws — Loans to Directors",
         "status": "Concept trap", "acceptedKey": "Permitted: MD/WTD loan under all-employee service conditions or special-resolution scheme; loans to other director-interested persons need special resolution, principal-business use and Sec 186(7) interest floor.",
         "summary": "Confusing Sec 185 (loans to directors/interested persons) with Sec 186 (limits on loans, guarantees and investments).", "linkedQuestionIds": [213]},
        {"exam": "Ind AS 116 — Para 44–46", "qNum": "Lease modification and remeasurement of lease liability", "subject": FIN, "chapter": "Paper 1: Financial Reporting — Ind AS 115 & Ind AS 116",
         "status": "High-failure trap", "acceptedKey": "Modification not a separate lease → remeasure liability at the revised discount rate and adjust the ROU asset; scope decreases give gain/loss.",
         "summary": "Keeping the original discount rate, or mixing lessee and lessor accounting. Draw the timeline and discount at the revised rate.", "linkedQuestionIds": [401, 406, 411]},
        {"exam": "ICAI Exam Rules — CA Foundation", "qNum": "Negative marking (-0.25) and 40% per paper / 50% aggregate", "subject": F, "chapter": "Paper 3 & 4: Objective papers",
         "status": "Exam-rule trap", "acceptedKey": "Foundation: at least 40% in each paper and 50% in aggregate; wrong MCQ answers cost 1/4 of the mark. " + V,
         "summary": "Blind guessing on all MCQs, or ignoring the aggregate while meeting the per-paper floor.", "linkedQuestionIds": [101, 103, 105]},
        {"exam": "ICAI CA Final — Paper 6 (IBS)", "qNum": "Multidisciplinary case study and indexed reference material", "subject": FIN, "chapter": "Paper 6: Integrated Business Solutions",
         "status": "Exam-strategy trap", "acceptedKey": "Index statutes/standards by topic in advance and practise cross-discipline cases. " + V + " (including which reference material is permitted in the hall).",
         "summary": "Treating IBS as four separate papers, or spending time on bare-act search instead of application.", "linkedQuestionIds": [430, 429, 424]},
    ]
    timeline = [
        {"year": "2019", "headline": "Pre-New-Scheme baseline", "impact": "Inter and Final had 8 papers each (old scheme) — the benchmark for later pattern changes."},
        {"year": "2020–2021", "headline": "Pandemic disruption", "impact": "Postponements and opt-out facilities for some cycles; irregular attempt patterns. " + V},
        {"year": "2023", "headline": "ICAI New Scheme of Education & Training announced", "impact": "Inter and Final consolidated from 8 to 6 papers each. " + V},
        {"year": "2024", "headline": "First New-Scheme cycles; case-scenario MCQs (about 30%) in Inter & Final", "impact": "Application-heavy MCQs with 2-mark weightage. " + V},
        {"year": "2025", "headline": "Foundation and Inter offered Jan / May / Sep", "impact": "More attempts per year. " + V},
        {"year": "2025", "headline": "SPOM online modules / CBT sets (A–D) at Final level", "impact": "Separate preparation track (IBC 2016, SEBI, SCMPE). " + V},
        {"year": "2026", "headline": "Two-year uninterrupted articleship; 60% marks exemption rule", "impact": "Plan attempts around exemptions. " + V},
    ]
    insights = {
        "patternShifts": [{"era": "Old scheme (to 2023)", "format": "8 papers each in Inter and Final", "summary": "Descriptive answers dominated; amendments tested by long problems."},
                          {"era": "New scheme (2024 onwards)", "format": "6 papers; case-scenario MCQs (~30%) in Inter & Final", "summary": "Application-heavy MCQs, bigger weight on amendments (default tax regime) and an integrated IBS case study."}],
        "controversiesAndLessons": [{"title": "Amendment cut-off dates", "detail": "Apply the law applicable to the stated assessment year / attempt, not the latest amendment by default."},
                                    {"title": "Ambiguous MCQ keys", "detail": "ICAI's published suggested answers settle disputes; practise reading the stem for the governing provision."}],
        "coachingAndRedditMeta": [{"source": "r/CharteredAccountants", "verdict": "Students commonly report ICAI RTP/MTP practice as the best proxy for question style (anecdotal, not an official statistic)."},
                                  {"source": "Coaching institutes (e.g. KS Academy, Srinivasa Academy) and test series", "verdict": "Widely used for timed practice; compare syllabus coverage independently."},
                                  {"source": "TAHDCO-supported free CA coaching", "verdict": "Check current eligibility and intake on the TAHDCO website."}],
        "tamilNaduEcosystem": [{"name": "SIRC of ICAI — Chennai, Coimbatore, Madurai, Trichy branches", "focus": "Classes, study circles and CPE events in Tamil Nadu.", "url": "https://www.icai.org"},
                               {"name": "CA in Tamil", "focus": "Concept revision in Tamil.", "url": "https://www.youtube.com/@CAinTamil"},
                               {"name": "KPG Classes (Tamil)", "focus": "Subject revision for Foundation to Final.", "url": "https://www.youtube.com/@KPGClasses"},
                               {"name": "ICAI CA Tube", "focus": "Official ICAI video lectures.", "url": "https://www.youtube.com/@icai_ca_tube"}],
    }
    papers = [{"id": p[0], "year": p[3], "language": "ta" if p[5] == "booklet" else "en", "title": p[1], "count": len(paper_q[p[0]]),
               "label": p[2], "cycle": p[4], "type": p[5], "subjects": p[7]} for p in PAPERS]
    analytics = {"overallQuestionTypes": dict(overall), "questionTypeByYear": qty, "topChaptersBySubject": top,
                 "disputedQuestionsDossier": dossier, "examShocksTimeline": timeline, "unofficialInsights": insights, "papers": papers}
    return {"metadata": meta, "analytics": analytics, "unofficialInsights": insights, "disputedQuestionsDossier": dossier,
            "examShocksTimeline": timeline, "papers": papers, "modules": mods, "questions": arc}


# ------------------------------------------------------------------ io + verification
def dump(path, obj, var=None, alias=None):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
        if var:
            f.write(f"window.{var} = {json.dumps(obj, ensure_ascii=False)};\nwindow.{alias} = window.{var};\n")
        else:
            json.dump(obj, f, ensure_ascii=False, indent=1)


HAND_ANSWERS = {117: "₹12,000 and ₹12,000", 125: "5/36", 126: "820", 212: "₹12 lakh", 223: "Nil", 319: "1.25", 320: "3 years", 410: "₹0.8 crore",
                412: "₹11.80", 413: "₹12", 414: "1.04", 421: "25.168%", 424: "₹12,11,250", 211: "200", 214: "3", 420: "₹3 crore"}
# hand-computed correct answers for parameter set 0 of every numeric template (independent of ca_templates.py)
HAND_NUMERIC = {101: "₹10,500", 102: "₹1,20,000", 103: "₹360", 104: "1.5", 105: "56", 106: "₹1,00,000", 107: "₹14,000", 108: "20%",
                201: "₹3,00,000", 202: "₹1,09,200", 203: "₹54,000", 204: "₹80,000", 205: "₹1,65,000",
                301: "600 units", 302: "5,000 units", 303: "₹10,000 (A)", 304: "11.8%", 305: "100 days", 306: "₹26", 307: "12%",
                401: "₹2,48,685", 402: "₹6,00,000", 403: "₹26,000", 404: "₹86.25", 405: "₹9,64,000"}


def verify():
    def load(p):
        return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))

    def js(p, var, alias):
        t = open(os.path.join(ROOT, p), encoding="utf-8").read()
        pre = f"window.{var} = "
        assert t.startswith(pre) and t.rstrip().endswith(f"window.{alias} = window.{var};"), p
        return json.loads(t[len(pre):t.index(";\nwindow.")])

    bank, arc = load("questions_bank.json"), load("past_papers_archive.json")
    assert js("questions_database.js", "CA_QUESTION_BANK", "NEET_QUESTION_BANK") == bank
    assert js("past_papers_database.js", "CA_PAST_PAPERS_ARCHIVE", "NEET_PAST_PAPERS_ARCHIVE") == arc
    for name, d in (("bank", bank), ("archive", arc)):
        ids = [q["id"] for q in d["questions"]]
        assert len(ids) == len(set(ids)), f"{name}: duplicate ids"
        for mid, m in d["modules"].items():
            assert m["id"] == mid and m["title"].strip() and m["title_ta"].strip() and m["description"].strip(), (name, mid)
            assert m["questionIds"] and set(m["questionIds"]) <= set(ids), (name, mid, set(m["questionIds"]) - set(ids))
            assert len(m["questionIds"]) == len(set(m["questionIds"])), (name, mid, "dup in module")
        for q in d["questions"]:
            assert q["subject"] in LEVEL and q["classLevel"] == LEVEL[q["subject"]]
            assert [c["letter"] for c in q["choices"]] == list(LETTERS), q["id"]
            assert len({c["text_en"] for c in q["choices"]}) == 4, q["id"]
            assert q["correct"] in LETTERS and q["difficulty"] in ("Easy", "Medium", "Hard")
            for k in ("stem_en", "stem_ta", "explanation_en", "explanation_ta", "ncert_key_point", "chapter", "ncertRef", "pyqTag", "questionType"):
                assert isinstance(q[k], str) and q[k].strip(), (q["id"], k)
            assert all(c["text_en"].strip() and c["text_ta"].strip() for c in q["choices"]), q["id"]
            assert set(q["trap_breakdown"]) == set(LETTERS) - {q["correct"]}, q["id"]
            assert all(v.strip() for v in q["trap_breakdown"].values()) and q["videoTutorial"]["url"].startswith("https://www.youtube.com/@")
    # arithmetic (1): every numeric item's stored answer equals a fresh template run for its parameter set
    for q in arc["questions"]:
        sid = ORIGIN[q["id"]]
        base, j = sid % 10000, sid // 10000
        if base in NUM:
            func, sets = tp.TEMPLATES[NUM[base][0]]
            p = sets[j]
            d = func(j, p) if isinstance(p, list) else func(j, *p)
            assert next(c["text_en"] for c in q["choices"] if c["letter"] == q["correct"]) == d["ok"], q["id"]
    # arithmetic (2): hard-coded, hand-computed expected answers (independent of the template code)
    bmap = {q["id"]: q for q in bank["questions"]}
    ans = lambda q: next(c["text_en"] for c in q["choices"] if c["letter"] == q["correct"])  # noqa: E731
    for table in (HAND_NUMERIC, HAND_ANSWERS):
        for qid, want in table.items():
            assert ans(bmap[qid]) == want, (qid, ans(bmap[qid]), want)
    assert round(((400000 * .05) + (400000 * .10) + (300000 * .15)) * 1.04) == 109200 and abs(22 * 1.10 * 1.04 - 25.168) < 1e-9
    # counts / structure
    bm = bank["metadata"]
    assert bm["totalQuestionsInBank"] == len(bank["questions"]) >= 90
    for s, mn in ((F, 25), (G1, 25), (G2, 20), (FIN, 25)):
        assert bm["subjectCounts"][s] == sum(q["subject"] == s for q in bank["questions"]) >= mn, s
    assert len(bank["modules"]["ca_all_levels_mock_1"]["questionIds"]) == 60
    am = arc["metadata"]
    assert am["totalQuestions"] == len(arc["questions"]) >= 200 and am["totalPapers"] == len(arc["papers"]) == 18 and am["specialModulesCount"] == 6
    assert am["patternSetQuestions"] + am["tamilBookletQuestions"] + am["exemplarAndCoachingQuestions"] == am["totalQuestions"]
    for p in arc["papers"]:
        m = arc["modules"][p["id"]]
        assert 15 <= len(m["questionIds"]) <= 30 and p["count"] == len(m["questionIds"]), p["id"]
        assert {q["paperId"] for q in arc["questions"] if q["id"] in set(m["questionIds"])} == {p["id"]}
    for k in ("icai_landmark_caselaws", "icai_rtp_mtp_2026_capsule", "icai_amendments_ay2026_27", "icai_spom_set_ab_cbt", "icai_ibs_case_studies"):
        assert k in arc["modules"]
    assert len(arc["disputedQuestionsDossier"]) == 6 and arc["analytics"]["papers"] == arc["papers"]
    assert set(arc["analytics"]["questionTypeByYear"]) == {str(y) for y in range(2019, 2027)}
    print(f"VERIFIED: bank={len(bank['questions'])} {bm['subjectCounts']} | archive={len(arc['questions'])} questions, "
          f"{len(arc['papers'])} papers (sizes {sorted(p['count'] for p in arc['papers'])})")


def main():
    bank = build_bank()
    arc = build_archive(bank)
    dump("questions_bank.json", bank)
    dump("questions_database.js", bank, "CA_QUESTION_BANK", "NEET_QUESTION_BANK")
    dump("past_papers_archive.json", arc)
    dump("past_papers_database.js", arc, "CA_PAST_PAPERS_ARCHIVE", "NEET_PAST_PAPERS_ARCHIVE")
    verify()


if __name__ == "__main__":
    main()
