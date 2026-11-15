"""Parametric numeric question templates. Every correct answer and distractor is COMPUTED here,
so arithmetic is verified by construction. Each template: f(i, *params) -> dict(en,ta,ok,bad[3],xe,xt,tip,tr[3])."""
import math

ORGS = [("Chennai Textiles Ltd.", "சென்னை டெக்ஸ்டைல்ஸ் லிமிடெட்"), ("Coimbatore Pumps Ltd.", "கோயம்புத்தூர் பம்ப்ஸ் லிமிடெட்"),
        ("Madurai Foods Ltd.", "மதுரை ஃபுட்ஸ் லிமிடெட்"), ("Trichy Steel Ltd.", "திருச்சி ஸ்டீல் லிமிடெட்"),
        ("Salem Auto Ltd.", "சேலம் ஆட்டோ லிமிடெட்"), ("Tirunelveli Agro Ltd.", "திருநெல்வேலி அக்ரோ லிமிடெட்")]


def org(i):
    return ORGS[i % len(ORGS)]


def inr(x):
    x = round(x, 2)
    neg, x = x < 0, abs(x)
    ip = int(x)
    fp = round(x - ip, 2)
    s = str(ip)
    if len(s) > 3:
        head, tail, g = s[:-3], s[-3:], []
        while len(head) > 2:
            g.insert(0, head[-2:])
            head = head[:-2]
        if head:
            g.insert(0, head)
        s = ",".join(g + [tail])
    if fp:
        s += f"{fp:.2f}"[1:]
    return ("-" if neg else "") + "₹" + s


def num(x, d=2):
    return f"{x:,.{d}f}".rstrip("0").rstrip(".") if d else f"{x:,.0f}"


def pf(x):
    return num(x) + "%"


# ---------------- CA Foundation ----------------
def f_ci(i, P, r, n):
    o, ot = org(i)
    ci = P * ((1 + r / 100) ** n - 1)
    si = P * r * n / 100
    hy = P * ((1 + r / 200) ** (2 * n) - 1)
    return dict(
        en=f"{o} invests {inr(P)} for {n} years at {r}% p.a., interest compounded annually. The compound interest earned is:",
        ta=f"{ot} {inr(P)}-ஐ {n} ஆண்டுகளுக்கு ஆண்டுக்கு {r}% வட்டியில் (ஆண்டுதோறும் கூட்டு வட்டி) முதலீடு செய்கிறது. கிடைக்கும் கூட்டு வட்டி எவ்வளவு?",
        ok=inr(ci), bad=[inr(si), inr(P + ci), inr(hy)],
        xe=f"CI = P[(1+r)^n − 1] = {P} × [(1+{r/100})^{n} − 1] = {inr(ci)}.",
        xt=f"கூட்டு வட்டி = P[(1+r)^n − 1] = {P} × [(1+{r/100})^{n} − 1] = {inr(ci)}. வட்டிக்கு வட்டி சேர்க்கப்படுவதால் தனி வட்டியை விட அதிகம்.",
        tip="CI = Amount − Principal. Check the compounding frequency before computing.",
        tr=["Simple interest ignores interest-on-interest.", "That is the compound AMOUNT (principal + interest), not the interest.",
            "Half-yearly compounding applies only if stated; here compounding is annual."])


def f_dep(i, C, S, L):
    o, ot = org(i)
    ok = (C - S) / L
    return dict(
        en=f"{o} buys machinery costing {inr(C)} with estimated scrap value {inr(S)} and useful life of {L} years. Annual depreciation under the Straight Line Method is:",
        ta=f"{ot} {inr(C)} மதிப்புள்ள இயந்திரத்தை வாங்குகிறது; மதிப்பிடப்பட்ட கழிவு மதிப்பு {inr(S)}, பயன்பாட்டுக் காலம் {L} ஆண்டுகள். நேர்கோட்டு முறையில் (SLM) ஆண்டு தேய்மானம் எவ்வளவு?",
        ok=inr(ok), bad=[inr(C / L), inr((C + S) / L), inr((C - S) / (L + 1))],
        xe=f"SLM depreciation = (Cost − Scrap) / Life = ({C} − {S}) / {L} = {inr(ok)}.",
        xt=f"SLM தேய்மானம் = (செலவு − கழிவு மதிப்பு) / ஆயுள் = ({C} − {S}) / {L} = {inr(ok)}.",
        tip="Depreciable amount = Cost − Residual value (AS 10 / Ind AS 16).",
        tr=["Ignores the scrap value – depreciates the full cost.", "Adds scrap instead of deducting it.", "Divides by (life + 1) – wrong denominator."])


def f_wmean(i, n1, m1, n2, m2):
    o, ot = org(i)
    ok = (n1 * m1 + n2 * m2) / (n1 + n2)
    return dict(
        en=f"At {o}, {n1} workers earn an average of {inr(m1)} per day and {n2} workers earn an average of {inr(m2)}. The combined mean wage of all workers is:",
        ta=f"{ot} நிறுவனத்தில் {n1} தொழிலாளர்களின் சராசரி ஊதியம் {inr(m1)}, {n2} தொழிலாளர்களின் சராசரி ஊதியம் {inr(m2)}. அனைவரின் கூட்டு சராசரி ஊதியம் எவ்வளவு?",
        ok=inr(ok), bad=[inr((m1 + m2) / 2), inr((n2 * m1 + n1 * m2) / (n1 + n2)), inr(n1 * m1 + n2 * m2)],
        xe=f"Combined mean = (n1·m1 + n2·m2)/(n1+n2) = ({n1}×{m1} + {n2}×{m2})/{n1+n2} = {inr(ok)}.",
        xt=f"கூட்டு சராசரி = (n1·m1 + n2·m2)/(n1+n2) = ({n1}×{m1} + {n2}×{m2})/{n1+n2} = {inr(ok)}.",
        tip="Combined mean is a WEIGHTED mean – never the simple average of the two means.",
        tr=["Simple average of the two means ignores group sizes.", "Weights are swapped between the groups.", "That is the total wage bill, not the mean."])


def f_elast(i, p0, p1, q0, q1):
    pp, pq = (p1 - p0) / p0 * 100, (q0 - q1) / q0 * 100
    ed = pq / pp
    o, ot = org(i)
    return dict(
        en=f"When the price of a product of {o} rises from ₹{p0} to ₹{p1}, quantity demanded falls from {q0} to {q1} units. Price elasticity of demand (percentage method, numerical value) is:",
        ta=f"{ot} தயாரிப்பின் விலை ₹{p0}-இலிருந்து ₹{p1} ஆக உயரும்போது தேவைப்படும் அளவு {q0}-இலிருந்து {q1} அலகுகளாகக் குறைகிறது. விலை நெகிழ்ச்சி (சதவீத முறை, எண் மதிப்பு) என்ன?",
        ok=num(ed), bad=[num(1 / ed), num((q0 - q1) / (p1 - p0)), num(pq)],
        xe=f"%ΔP = {pp:g}%, %ΔQ = {pq:g}%. Ed = %ΔQ / %ΔP = {pq:g}/{pp:g} = {num(ed)}.",
        xt=f"விலை மாற்றம் = {pp:g}%, அளவு மாற்றம் = {pq:g}%. Ed = {pq:g}/{pp:g} = {num(ed)}.",
        tip="Ed = %ΔQd ÷ %ΔP. >1 elastic, <1 inelastic, =1 unitary.",
        tr=["Reciprocal – ratio inverted.", "That is the slope (ΔQ/ΔP in absolute units), not elasticity.", "That is only %ΔQ – the denominator %ΔP is not applied."])


def f_comb(i, n, r):
    o, ot = org(i)
    c, p = math.comb(n, r), math.perm(n, r)
    return dict(
        en=f"A committee of {r} members is to be selected from {n} directors of {o}, order of selection being irrelevant. The number of ways is:",
        ta=f"{ot} நிறுவனத்தின் {n} இயக்குநர்களில் இருந்து {r} பேர் கொண்ட குழுவைத் தேர்வு செய்ய வேண்டும்; வரிசை முக்கியமில்லை. எத்தனை வழிகள்?",
        ok=str(c), bad=[str(p), str(n * r), str(math.comb(n + 1, r))],
        xe=f"Order irrelevant → combination: C({n},{r}) = {n}!/({r}!·{n-r}!) = {c}.",
        xt=f"வரிசை முக்கியமில்லை → சேர்மானம்: C({n},{r}) = {c}.",
        tip="Selection = nCr; Arrangement = nPr.",
        tr=[f"{p} is the permutation nPr (order counted).", "n × r is a multiplication, not a counting formula.", "Uses n+1 objects instead of n."])


def f_pv(i, P, r, n):
    o, ot = org(i)
    FV = P * (1 + r / 100) ** n
    return dict(
        en=f"{o} will receive {inr(FV)} after {n} years. Discounting at {r}% p.a. compounded annually, the present value is:",
        ta=f"{ot} {n} ஆண்டுகளுக்குப் பிறகு {inr(FV)} பெறும். ஆண்டுக்கு {r}% கூட்டு வட்டியில் தள்ளுபடி செய்தால் தற்போதைய மதிப்பு என்ன?",
        ok=inr(P), bad=[inr(FV / (1 + r * n / 100)), inr(FV * (1 - r * n / 100)), inr(FV / (1 + r / 100))],
        xe=f"PV = FV/(1+r)^n = {round(FV,2)}/(1+{r/100})^{n} = {inr(P)}.",
        xt=f"PV = FV/(1+r)^n = {round(FV,2)}/(1+{r/100})^{n} = {inr(P)}.",
        tip="PV = FV × discount factor; use (1+r)^n, not (1+rn).",
        tr=["Uses simple-interest discounting.", "Subtracts r×n% from FV – not a valid discounting formula.", "Discounts for only one period."])


def f_stock(i, items):
    o, ot = org(i)
    desc = "; ".join(f"{q} units (cost ₹{c}, NRV ₹{n})" for q, c, n in items)
    ok = sum(q * min(c, n) for q, c, n in items)
    return dict(
        en=f"{o} holds three items at year-end – {desc}. Closing inventory under AS 2 (item-wise lower of cost and NRV) is:",
        ta=f"{ot} ஆண்டு இறுதியில் மூன்று பொருட்களை வைத்துள்ளது – {desc}. AS 2-இன்படி (ஒவ்வொரு பொருளும் செலவு அல்லது NRV இதில் குறைவானது) இறுதிச் சரக்கு மதிப்பு?",
        ok=inr(ok), bad=[inr(sum(q * c for q, c, n in items)), inr(sum(q * n for q, c, n in items)), inr(sum(q * max(c, n) for q, c, n in items))],
        xe="Value each item at the lower of cost and NRV: " + " + ".join(f"{q}×{min(c, n)}" for q, c, n in items) + f" = {inr(ok)}.",
        xt="ஒவ்வொரு பொருளையும் செலவு/NRV-ல் குறைவானதில் மதிப்பிடவும்: " + " + ".join(f"{q}×{min(c, n)}" for q, c, n in items) + f" = {inr(ok)}.",
        tip="AS 2 / Ind AS 2: lower of cost and NRV, applied item by item (not in total).",
        tr=["Total at cost – ignores write-down to NRV.", "Total at NRV – ignores items where cost is lower.", "Takes the HIGHER of cost and NRV – opposite of the rule."])


def f_margin(i, m):
    o, ot = org(i)
    ok = 100 * m / (100 + m)
    return dict(
        en=f"{o} sells goods at a mark-up of {m}% on cost. Gross profit as a percentage of SALES is:",
        ta=f"{ot} பொருட்களை செலவின் மீது {m}% மார்க்-அப்புடன் விற்கிறது. விற்பனையில் மொத்த இலாப சதவீதம் என்ன?",
        ok=pf(ok), bad=[pf(m), pf(100 * m / (100 - m)), pf(m / 2)],
        xe=f"Let cost = 100; sales = {100+m}; profit = {m}. Margin on sales = {m}/{100+m} × 100 = {pf(ok)}.",
        xt=f"செலவு = 100 என்க; விற்பனை = {100+m}; இலாபம் = {m}. விற்பனையில் இலாபம் = {m}/{100+m} × 100 = {pf(ok)}.",
        tip="Mark-up is on COST; margin is on SALES: Margin = Markup/(100+Markup).",
        tr=["That is the mark-up on cost, not margin on sales.", "Inverse formula (margin→markup) used by mistake.", "Arbitrary halving has no basis."])


# ---------------- CA Inter Group I ----------------
def g_goodwill(i, A, K, r, y):
    o, ot = org(i)
    sp = A - K * r / 100
    return dict(
        en=f"{o} has average maintainable profit of {inr(A)}, capital employed {inr(K)} and normal rate of return {r}%. Goodwill at {y} years' purchase of super profit is:",
        ta=f"{ot} நிறுவனத்தின் சராசரி இலாபம் {inr(A)}, முதலீடு {inr(K)}, இயல்பான வருவாய் விகிதம் {r}%. மிகை இலாபத்தின் {y} ஆண்டு கொள்முதல் அடிப்படையில் நற்பெயர் மதிப்பு?",
        ok=inr(sp * y), bad=[inr(sp), inr(A * y), inr(K * r / 100 * y)],
        xe=f"Normal profit = {K}×{r}% = {inr(K*r/100)}; Super profit = {A} − {K*r/100:g} = {inr(sp)}; Goodwill = {inr(sp)} × {y} = {inr(sp*y)}.",
        xt=f"இயல்பான இலாபம் = {inr(K*r/100)}; மிகை இலாபம் = {inr(sp)}; நற்பெயர் = {inr(sp)} × {y} = {inr(sp*y)}.",
        tip="Super profit = Average profit − Normal profit. Goodwill = Super profit × years' purchase.",
        tr=["That is only one year's super profit – not multiplied by years' purchase.", "Multiplies average profit, not SUPER profit.", "Multiplies NORMAL profit – wrong base."])


SLABS = [(400000, 0.0), (800000, 0.05), (1200000, 0.10), (1600000, 0.15), (2000000, 0.20), (2400000, 0.25), (math.inf, 0.30)]


def new_tax(T):
    t, lo = 0.0, 0
    for hi, rt in SLABS:
        if T > lo:
            t += (min(T, hi) - lo) * rt
        lo = hi
    return t


def old_tax(T):
    return 0 if T <= 250000 else (min(T, 500000) - 250000) * .05 + (max(0, min(T, 1000000) - 500000)) * .2 + max(0, T - 1000000) * .3


def g_tax_new(i, S):
    T = S - 75000
    assert T > 1300000  # above rebate / marginal-relief zone
    tx = new_tax(T)
    return dict(
        en=f"Ms. Kavitha, a resident individual (age < 60) in Chennai, has gross salary of {inr(S)} for FY 2025-26. She follows the default regime u/s 115BAC(1A) (AY 2026-27); her only deduction is the standard deduction of ₹75,000. Tax liability including 4% cess is:",
        ta=f"சென்னையில் வசிக்கும் (60 வயதுக்குக் குறைவான) கவிதாவின் FY 2025-26 மொத்த சம்பளம் {inr(S)}. அவர் AY 2026-27-க்கு 115BAC(1A) இயல்புநிலை வரி முறையைப் பின்பற்றுகிறார்; நிலையான கழிவு ₹75,000 மட்டுமே. 4% செஸ் உட்பட வரிப் பொறுப்பு?",
        ok=inr(tx * 1.04), bad=[inr(tx), inr(new_tax(S) * 1.04), inr(old_tax(T) * 1.04)],
        xe=f"Taxable income = {S} − 75,000 = {inr(T)}. New-regime slabs (0–4L nil, 4–8L 5%, 8–12L 10%, 12–16L 15%, 16–20L 20%, 20–24L 25%, >24L 30%) give tax {inr(tx)}; rebate u/s 87A not available (income > ₹12L); add 4% cess → {inr(tx*1.04)}.",
        xt=f"வரி விதிக்கத்தக்க வருமானம் = {S} − 75,000 = {inr(T)}. புதிய முறை ஸ்லாப்கள் படி வரி {inr(tx)}; வருமானம் ₹12 லட்சத்துக்கு மேல் என்பதால் 87A தள்ளுபடி இல்லை; 4% செஸ் சேர்த்து {inr(tx*1.04)}.",
        tip="Default regime AY 2026-27: std deduction ₹75,000; 87A rebate only if income ≤ ₹12L; always add 4% cess.",
        tr=["Omits 4% health & education cess.", "Forgets the ₹75,000 standard deduction (taxes gross salary).", "Applies OLD-regime slabs although the default regime is chosen."])


def g_gst(i, O, I):
    o, ot = org(i)
    return dict(
        en=f"{o} (Tamil Nadu) made intra-state taxable outward supplies of {inr(O)} and eligible inward supplies of {inr(I)}, all at 18% GST (CGST 9% + SGST 9%). Assuming no opening credit, total GST payable in cash is:",
        ta=f"{ot} (தமிழ்நாடு) மாநிலத்துக்குள் {inr(O)} வெளிப்புற வரிவிதிப்பு விநியோகங்களையும் {inr(I)} தகுதியான உள்வரும் கொள்முதல்களையும் செய்தது; அனைத்தும் 18% GST (CGST 9% + SGST 9%). தொடக்க ITC இல்லை எனில் ரொக்கமாகச் செலுத்த வேண்டிய மொத்த GST?",
        ok=inr((O - I) * .18), bad=[inr(O * .18), inr((O - I) * .09), inr(I * .18)],
        xe=f"Output GST = {O}×18% = {inr(O*.18)}; ITC = {I}×18% = {inr(I*.18)}; Net cash payable = {inr((O-I)*.18)} (CGST {inr((O-I)*.09)} + SGST {inr((O-I)*.09)}).",
        xt=f"வெளிப்புற GST = {inr(O*.18)}; ITC = {inr(I*.18)}; ரொக்கமாகச் செலுத்த = {inr((O-I)*.18)} (CGST {inr((O-I)*.09)} + SGST {inr((O-I)*.09)}).",
        tip="Net GST = Output tax − eligible ITC (Sec 49 set-off order: IGST→CGST→SGST).",
        tr=["Ignores ITC completely (gross output tax).", "Shows only the CGST (or SGST) half of the net liability.", "That is the ITC amount, not the net liability."])


def g_wdv(i, C, r):
    o, ot = org(i)
    y1 = C * r / 100
    y2 = (C - y1) * r / 100
    return dict(
        en=f"{o} bought machinery for {inr(C)} on 1 April 2024 and depreciates it at {r}% p.a. under the Written Down Value method. Depreciation for the SECOND year (FY 2025-26) is:",
        ta=f"{ot} 1 ஏப்ரல் 2024 அன்று {inr(C)}-க்கு இயந்திரம் வாங்கியது; எஞ்சிய மதிப்பு (WDV) முறையில் ஆண்டுக்கு {r}% தேய்மானம். இரண்டாம் ஆண்டு (FY 2025-26) தேய்மானம்?",
        ok=inr(y2), bad=[inr(y1), inr(2 * y1), inr(y1 + y1 * r / 100)],
        xe=f"Year 1 = {C}×{r}% = {inr(y1)}; WDV = {inr(C-y1)}; Year 2 = {inr(C-y1)}×{r}% = {inr(y2)}.",
        xt=f"முதல் ஆண்டு = {inr(y1)}; WDV = {inr(C-y1)}; இரண்டாம் ஆண்டு = {inr(C-y1)}×{r}% = {inr(y2)}.",
        tip="WDV method: rate applies to the opening book value, so depreciation falls each year.",
        tr=["That is year-1 depreciation (SLM-like constant charge).", "Doubles year 1 – WDV charge reduces, never grows.", "Adds interest-like compounding on the charge – no such concept in WDV."])


def g_hp(i, G, M, Int):
    o, ot = org(i)
    nav = G - M
    inc = nav - 0.3 * nav - Int
    return dict(
        en=f"Mr. Arun owns a let-out house in Coimbatore: Gross Annual Value {inr(G)}, municipal taxes paid {inr(M)}, interest on housing loan {inr(Int)} (all accrued in FY 2025-26). Income from house property is:",
        ta=f"கோயம்புத்தூரில் வாடகைக்கு விடப்பட்ட வீடு: மொத்த ஆண்டு மதிப்பு (GAV) {inr(G)}, செலுத்திய நகராட்சி வரி {inr(M)}, வீட்டுக்கடன் வட்டி {inr(Int)} (FY 2025-26). வீட்டுச் சொத்து வருமானம்?",
        ok=inr(inc), bad=[inr(G - .3 * G - Int), inr(nav - Int), inr(nav - .3 * nav)],
        xe=f"NAV = {G} − {M} = {inr(nav)}; Less 30% std deduction (Sec 24(a)) = {inr(.3*nav)}; Less interest (Sec 24(b)) = {inr(Int)}; Income = {inr(inc)}.",
        xt=f"NAV = {G} − {M} = {inr(nav)}; 30% நிலையான கழிவு (Sec 24(a)) = {inr(.3*nav)}; வட்டி (Sec 24(b)) = {inr(Int)}; வருமானம் = {inr(inc)}.",
        tip="HP income = NAV − 30% of NAV − interest; municipal tax is deducted only if paid by the owner during the year.",
        tr=["Forgets to deduct municipal taxes before the 30% deduction.", "Omits the 30% standard deduction.", "Omits interest on borrowed capital."])


# ---------------- CA Inter Group II ----------------
def c_eoq(i, q, C, A):
    O = q * q * C / (2 * A)
    assert O == int(O)
    o, ot = org(i)
    return dict(
        en=f"{o}: annual demand {A:,} units, ordering cost ₹{int(O)} per order, carrying cost ₹{C} per unit per annum. The Economic Order Quantity is:",
        ta=f"{ot}: ஆண்டு தேவை {A:,} அலகுகள், ஒரு ஆர்டருக்கான செலவு ₹{int(O)}, ஓர் அலகுக்கான ஆண்டு சுமப்புச் செலவு ₹{C}. பொருளாதார ஆர்டர் அளவு (EOQ)?",
        ok=f"{q:,} units", bad=[f"{round(q/math.sqrt(2)):,} units", f"{q*q:,} units", f"{round(q*math.sqrt(2)):,} units"],
        xe=f"EOQ = √(2AO/C) = √(2×{A}×{int(O)}/{C}) = √{q*q:,} = {q:,} units.",
        xt=f"EOQ = √(2AO/C) = √(2×{A}×{int(O)}/{C}) = √{q*q:,} = {q:,} அலகுகள்.",
        tip="EOQ = √(2AO/C); at EOQ ordering cost = carrying cost.",
        tr=["Drops the factor 2 inside the root (√(AO/C)).", "Forgets the square root.", "Uses 4AO/C inside the root."])


def c_bep(i, c, b, V):
    S, F = V + c, c * b
    o, ot = org(i)
    return dict(
        en=f"{o} sells a product at ₹{S} per unit; variable cost is ₹{V} per unit and fixed costs are {inr(F)}. Break-even point (in units) is:",
        ta=f"{ot} ஒரு பொருளை அலகுக்கு ₹{S}-க்கு விற்கிறது; மாறுபடும் செலவு அலகுக்கு ₹{V}; நிலையான செலவுகள் {inr(F)}. சமநிலைப் புள்ளி (அலகுகளில்)?",
        ok=f"{b:,} units", bad=[f"{round(F/S):,} units", f"{round(F/V):,} units", f"{round(F/(S+V)):,} units"],
        xe=f"Contribution/unit = {S} − {V} = ₹{c}; BEP = Fixed cost / Contribution per unit = {F:,}/{c} = {b:,} units.",
        xt=f"அலகுக்கு பங்களிப்பு = {S} − {V} = ₹{c}; BEP = நிலையான செலவு / பங்களிப்பு = {F:,}/{c} = {b:,} அலகுகள்.",
        tip="BEP (units) = Fixed cost ÷ Contribution per unit (not ÷ selling price).",
        tr=["Divides by selling price – ignores variable cost.", "Divides by variable cost – wrong denominator.", "Divides by S+V – meaningless."])


def c_mpv(i, SP, AP, AQ, SQ):
    v = (SP - AP) * AQ
    f = lambda x: f"{inr(abs(x))} ({'F' if x > 0 else 'A'})"
    o, ot = org(i)
    return dict(
        en=f"{o}: standard price ₹{SP}/kg; actual price ₹{AP}/kg; actual quantity purchased and used {AQ:,} kg; standard quantity for actual output {SQ:,} kg. Material Price Variance is:",
        ta=f"{ot}: நிலையான விலை ₹{SP}/கிலோ; உண்மை விலை ₹{AP}/கிலோ; வாங்கி பயன்படுத்திய உண்மை அளவு {AQ:,} கிலோ; உண்மை உற்பத்திக்கான நிலையான அளவு {SQ:,} கிலோ. பொருள் விலை மாறுபாடு?",
        ok=f(v), bad=[f((SP - AP) * SQ), f(-v), f((SQ - AQ) * SP)],
        xe=f"MPV = (SP − AP) × AQ = ({SP} − {AP}) × {AQ:,} = {f(v)}.",
        xt=f"MPV = (SP − AP) × AQ = ({SP} − {AP}) × {AQ:,} = {f(v)}. (நிலையான விலை > உண்மை விலை எனில் சாதகம் F).",
        tip="MPV = (SP − AP) × AQ (actual quantity!). Positive = Favourable.",
        tr=["Uses standard quantity instead of actual quantity.", "Sign reversed – favourable/adverse flipped.", "That is the Material USAGE variance (SQ − AQ)×SP."])


def c_wacc(i, E, D, ke, kd, t):
    we = E / (E + D)
    ok = we * ke + (1 - we) * kd * (1 - t / 100)
    o, ot = org(i)
    return dict(
        en=f"{o} has equity of ₹{E} crore (cost of equity {ke}%) and debt of ₹{D} crore (pre-tax cost {kd}%). Tax rate is {t}%. Using book-value weights, WACC is:",
        ta=f"{ot}: பங்கு மூலதனம் ₹{E} கோடி (செலவு {ke}%), கடன் ₹{D} கோடி (வரிக்கு முன் செலவு {kd}%). வரி விகிதம் {t}%. புத்தக மதிப்பு எடைகளில் WACC?",
        ok=pf(ok), bad=[pf(we * ke + (1 - we) * kd), pf(ke), pf((ke + kd * (1 - t / 100)) / 2)],
        xe=f"Kd (post-tax) = {kd}×(1−{t/100}) = {num(kd*(1-t/100))}%; WACC = {num(we)}×{ke} + {num(1-we)}×{num(kd*(1-t/100))} = {pf(ok)}.",
        xt=f"வரிக்குப் பிந்தைய Kd = {num(kd*(1-t/100))}%; WACC = {num(we)}×{ke} + {num(1-we)}×{num(kd*(1-t/100))} = {pf(ok)}.",
        tip="Interest is tax-deductible: use Kd(1−t) in WACC.",
        tr=["Uses pre-tax cost of debt.", "Considers only cost of equity (ignores debt).", "Simple average ignores capital-structure weights."])


def c_opcycle(i, rm, wip, fg, dr, cr):
    ok = rm + wip + fg + dr - cr
    o, ot = org(i)
    return dict(
        en=f"{o}: raw material holding {rm} days, WIP {wip} days, finished goods {fg} days, debtors collection {dr} days, creditors payment {cr} days. The operating cycle (net) is:",
        ta=f"{ot}: மூலப்பொருள் {rm} நாட்கள், WIP {wip} நாட்கள், முடிந்த பொருட்கள் {fg} நாட்கள், கடனாளிகள் வசூல் {dr} நாட்கள், கடன் கொடுத்தோர் செலுத்தல் {cr} நாட்கள். நிகர இயக்கச் சுழற்சி?",
        ok=f"{ok} days", bad=[f"{rm+wip+fg+dr} days", f"{rm+wip+fg-cr} days", f"{rm+wip+fg+cr-dr} days"],
        xe=f"Operating cycle = RM + WIP + FG + Debtors − Creditors = {rm}+{wip}+{fg}+{dr}−{cr} = {ok} days.",
        xt=f"இயக்கச் சுழற்சி = RM + WIP + FG + கடனாளிகள் − கடன் கொடுத்தோர் = {rm}+{wip}+{fg}+{dr}−{cr} = {ok} நாட்கள்.",
        tip="Net operating cycle deducts the credit period received from creditors.",
        tr=["Omits the creditors' credit period (gross cycle).", "Omits debtors' collection period.", "Adds creditors and deducts debtors – reversed."])


def c_process(i, inp, lp, sc, u):
    loss = inp * lp // 100
    good = inp - loss
    total = u * good + sc * loss
    o, ot = org(i)
    return dict(
        en=f"{o} Process I: input {inp:,} units; total process cost {inr(total)}; normal loss {lp}% of input, sold as scrap at ₹{sc} per unit. Cost per unit of good output is:",
        ta=f"{ot} செயல்முறை I: உள்ளீடு {inp:,} அலகுகள்; மொத்தச் செலவு {inr(total)}; இயல்பான இழப்பு உள்ளீட்டில் {lp}%, கழிவாக அலகுக்கு ₹{sc}-க்கு விற்பனை. நல்ல உற்பத்தியின் அலகுச் செலவு?",
        ok=inr(u), bad=[inr(total / inp), inr(total / good), inr((total - sc * loss) / inp)],
        xe=f"Normal loss = {loss:,} units; scrap value = {inr(sc*loss)}; Net cost = {inr(total)} − {inr(sc*loss)} = {inr(total-sc*loss)}; Good output = {good:,}; Cost/unit = {inr(u)}.",
        xt=f"இயல்பான இழப்பு = {loss:,} அலகுகள்; கழிவு மதிப்பு = {inr(sc*loss)}; நிகரச் செலவு = {inr(total-sc*loss)}; நல்ல உற்பத்தி = {good:,}; அலகுச் செலவு = {inr(u)}.",
        tip="Normal loss: deduct scrap value from cost and divide by GOOD units.",
        tr=["Divides total cost by input units – ignores loss and scrap.", "Ignores scrap realisation of normal loss.", "Deducts scrap but divides by input instead of good output."])


def c_capm(i, rf, b, rm):
    ok = rf + b * (rm - rf)
    o, ot = org(i)
    return dict(
        en=f"For {o}: risk-free return {rf}%, market return {rm}%, equity beta {b}. Cost of equity under CAPM is:",
        ta=f"{ot}: ஆபத்தற்ற வருவாய் {rf}%, சந்தை வருவாய் {rm}%, பீட்டா {b}. CAPM படி பங்கு மூலதனச் செலவு?",
        ok=pf(ok), bad=[pf(rf + b * rm), pf(b * (rm - rf)), pf(rm)],
        xe=f"Ke = Rf + β(Rm − Rf) = {rf} + {b}×({rm} − {rf}) = {pf(ok)}.",
        xt=f"Ke = Rf + β(Rm − Rf) = {rf} + {b}×({rm} − {rf}) = {pf(ok)}.",
        tip="Premium is (Rm − Rf), not Rm.",
        tr=["Multiplies beta by the whole market return instead of the premium.", "Risk premium only – risk-free rate not added back.", "Market return ignores the company's beta."])


# ---------------- CA Final ----------------
def l_lease(i, P, n, r):
    f = (1 - (1 + r / 100) ** -n) / (r / 100)
    pv = round(P * f)
    o, ot = org(i)
    return dict(
        en=f"{o} (lessee) leases equipment for {n} years with annual payments of {inr(P)} at each year-end. Incremental borrowing rate is {r}%. Initial lease liability under Ind AS 116 (nearest rupee) is:",
        ta=f"{ot} (குத்தகைதாரர்) {n} ஆண்டுகளுக்கு உபகரணத்தைக் குத்தகைக்கு எடுக்கிறது; ஒவ்வொரு ஆண்டு இறுதியிலும் {inr(P)} செலுத்த வேண்டும். கூடுதல் கடன் வட்டி விகிதம் {r}%. Ind AS 116-இன்படி தொடக்கக் குத்தகைப் பொறுப்பு (அருகிலுள்ள ரூபாய்)?",
        ok=inr(pv), bad=[inr(P * n), inr(round(pv * (1 + r / 100))), inr(round(P * n / (1 + r / 100) ** n))],
        xe=f"Lease liability = PV of lease payments = {P} × [1 − (1+{r/100})^−{n}]/{r/100} = {P} × {f:.4f} = {inr(pv)}.",
        xt=f"குத்தகைப் பொறுப்பு = குத்தகைத் தொகைகளின் தற்போதைய மதிப்பு = {P} × {f:.4f} = {inr(pv)}.",
        tip="Ind AS 116: lessee recognises liability = PV of unpaid lease payments at the rate implicit (or IBR).",
        tr=["Undiscounted total of payments.", "Annuity-due value – payments here fall at year-END.", "Discounts the whole total as one lump sum at the end."])


def l_ifrs15(i, B, x, y):
    ok = B * x / (x + y)
    o, ot = org(i)
    return dict(
        en=f"{o} sells equipment and 3-year support to a customer in a single contract for {inr(B)}. Stand-alone selling prices: equipment {inr(x)}, support {inr(y)}. Under Ind AS 115, the transaction price allocated to the equipment is:",
        ta=f"{ot} உபகரணம் மற்றும் 3 ஆண்டு ஆதரவு சேவையை ஒரே ஒப்பந்தத்தில் {inr(B)}-க்கு விற்கிறது. தனிப்பட்ட விற்பனை விலை: உபகரணம் {inr(x)}, ஆதரவு {inr(y)}. Ind AS 115-இன்படி உபகரணத்துக்கு ஒதுக்கப்படும் தொகை?",
        ok=inr(ok), bad=[inr(x), inr(B / 2), inr(B - y)],
        xe=f"Allocate on relative SSP: {B} × {x}/({x}+{y}) = {inr(ok)}.",
        xt=f"ஒப்பீட்டு SSP அடிப்படையில்: {B} × {x}/({x}+{y}) = {inr(ok)}.",
        tip="Step 4 of Ind AS 115: allocate transaction price in proportion to stand-alone selling prices (discount spread pro-rata).",
        tr=["Uses the stand-alone price itself – ignores the bundle discount.", "Equal split ignores relative SSPs.", "Residual approach – allowed only in narrow cases (highly variable/uncertain SSP)."])


def l_ltcg(i, G):
    ok = (G - 125000) * .125 * 1.04
    return dict(
        en=f"Mr. Ravi (resident individual, Madurai) sold listed equity shares (STT paid) on 15 January 2026 and earned LTCG of {inr(G)} in FY 2025-26. Assume his other income already exhausts the basic exemption limit and ignore surcharge. Tax on this gain u/s 112A including 4% cess is:",
        ta=f"மதுரையைச் சேர்ந்த ரவி (குடியுரிமை தனிநபர்) பட்டியலிடப்பட்ட பங்குகளை (STT செலுத்தப்பட்டது) 15 ஜனவரி 2026 அன்று விற்று FY 2025-26-ல் {inr(G)} LTCG ஈட்டினார். அவரது பிற வருமானம் ஏற்கெனவே அடிப்படை விலக்கு வரம்பைத் தீர்த்துவிட்டதாகவும் சர்சார்ஜ் இல்லை எனவும் கொள்க. 4% செஸ் உட்பட 112A வரி?",
        ok=inr(ok), bad=[inr(max(0, G - 100000) * .10 * 1.04), inr(G * .125 * 1.04), inr((G - 125000) * .125)],
        xe=f"Exempt up to ₹1,25,000; taxable LTCG = {G} − 125000 = {inr(G-125000)}; tax @12.5% = {inr((G-125000)*.125)}; + 4% cess = {inr(ok)}.",
        xt=f"₹1,25,000 வரை விலக்கு; வரிக்குரிய LTCG = {inr(G-125000)}; 12.5% வரி = {inr((G-125000)*.125)}; 4% செஸ் சேர்த்து = {inr(ok)}.",
        tip="Transfers on/after 23-Jul-2024: Sec 112A rate 12.5%, exemption ₹1.25 lakh.",
        tr=["Uses pre-Budget 2024 rate (10%) and ₹1 lakh exemption.", "Ignores the ₹1.25 lakh exemption.", "Omits the 4% cess."])


def l_fx(i, S, ih, jf):
    F = S * (1 + ih / 100) / (1 + jf / 100)
    o, ot = org(i)
    return dict(
        en=f"{o} needs a 1-year forward quote. Spot ₹{S}/USD; 1-year interest rates: India {ih}%, USA {jf}%. Under Interest Rate Parity, the 1-year forward rate (₹/USD, 2 decimals) is:",
        ta=f"{ot}-க்கு 1 ஆண்டு ஃபார்வர்டு விகிதம் தேவை. ஸ்பாட் ₹{S}/USD; 1 ஆண்டு வட்டி: இந்தியா {ih}%, அமெரிக்கா {jf}%. வட்டி விகிதச் சமநிலை (IRP) படி 1 ஆண்டு ஃபார்வர்டு விகிதம் (₹/USD)?",
        ok=f"₹{F:.2f}", bad=[f"₹{S*(1+ih/100-jf/100):.2f}", f"₹{S*(1+jf/100)/(1+ih/100):.2f}", f"₹{S*(1+ih/100):.2f}"],
        xe=f"F = S × (1+i_INR)/(1+i_USD) = {S} × {1+ih/100:g}/{1+jf/100:g} = ₹{F:.2f}.",
        xt=f"F = S × (1+i_INR)/(1+i_USD) = {S} × {1+ih/100:g}/{1+jf/100:g} = ₹{F:.2f}. அதிக வட்டி நாட்டு நாணயம் ஃபார்வர்டில் தள்ளுபடியில் (depreciates) வரும்.",
        tip="IRP: the higher-interest currency (INR here) trades at a forward DISCOUNT, i.e. the forward rate is higher in ₹/USD.",
        tr=["Linear approximation (S×(1+Δi)) is not the exact IRP formula.", "Ratio inverted – gives INR appreciation.", "Ignores the foreign interest rate."])


def l_effint(i, carry, eir, face, cp):
    exp, cpn = carry * eir / 100, face * cp / 100
    close = carry + exp - cpn
    o, ot = org(i)
    return dict(
        en=f"{o} issued 5-year debentures of face value {inr(face)} carrying coupon {cp}% p.a. (paid annually). Initial amortised cost (net of costs) is {inr(carry)}; effective interest rate (EIR) is {eir}%. Carrying amount at end of Year 1 under Ind AS 109 is:",
        ta=f"{ot} {inr(face)} முகமதிப்புள்ள, ஆண்டுக்கு {cp}% கூப்பன் (ஆண்டுதோறும் செலுத்தப்படும்) கடனீட்டுப் பத்திரங்களை வெளியிட்டது. தொடக்க திருத்திய செலவு {inr(carry)}; பயனுள்ள வட்டி விகிதம் (EIR) {eir}%. Ind AS 109-இன்படி 1-ஆம் ஆண்டு இறுதியில் உள்ள கடன் மதிப்பு?",
        ok=inr(close), bad=[inr(carry + cpn), inr(carry - (exp - cpn)), inr(carry + exp)],
        xe=f"Interest expense = {carry}×{eir}% = {inr(exp)}; Coupon paid = {inr(cpn)}; Closing = {carry} + {exp:g} − {cpn:g} = {inr(close)}.",
        xt=f"வட்டிச் செலவு = {inr(exp)}; கூப்பன் செலுத்தியது = {inr(cpn)}; இறுதி மதிப்பு = {carry} + {exp:g} − {cpn:g} = {inr(close)}.",
        tip="Amortised cost: Opening + EIR interest − cash coupon paid.",
        tr=["Adds the coupon instead of EIR interest and does not deduct payment.", "Subtracts the unwinding – direction reversed (discount unwinds UPWARDS).", "Adds interest but forgets to deduct the coupon paid."])


# name -> (func, params sets)
TEMPLATES = {
    "f_ci": (f_ci, [(50000, 10, 2), (40000, 5, 2), (20000, 10, 3), (80000, 20, 2), (25000, 8, 2)]),
    "f_dep": (f_dep, [(660000, 60000, 5), (440000, 40000, 8), (810000, 30000, 6), (360000, 60000, 4), (1000000, 100000, 6)]),
    "f_wmean": (f_wmean, [(40, 300, 60, 400), (30, 250, 20, 300), (25, 480, 75, 400), (60, 350, 40, 300), (50, 280, 30, 360)]),
    "f_elast": (f_elast, [(10, 12, 500, 350), (20, 25, 400, 340), (40, 44, 300, 240), (50, 60, 200, 170), (100, 120, 1000, 900)]),
    "f_comb": (f_comb, [(8, 3), (10, 2), (7, 4), (9, 3), (6, 2)]),
    "f_pv": (f_pv, [(100000, 10, 2), (50000, 20, 2), (200000, 5, 2), (80000, 25, 2), (60000, 10, 3)]),
    "f_stock": (f_stock, [[(100, 50, 45), (200, 30, 36), (50, 80, 70)], [(400, 25, 22), (300, 40, 45), (150, 60, 52)],
                          [(80, 120, 100), (120, 90, 95), (60, 150, 160)], [(500, 18, 20), (250, 32, 28), (100, 70, 64)],
                          [(60, 200, 180), (90, 140, 150), (40, 300, 260)]]),
    "f_margin": (f_margin, [(25,), (50,), (20,), (60,), (40,)]),
    "g_goodwill": (g_goodwill, [(300000, 2000000, 10, 3), (450000, 3000000, 12, 4), (620000, 4000000, 10, 2), (190000, 1000000, 12, 5), (500000, 3500000, 10, 3)]),
    "g_tax_new": (g_tax_new, [(1575000,), (1475000,), (1875000,), (2275000,), (2675000,)]),
    "g_gst": (g_gst, [(800000, 500000), (1200000, 700000), (650000, 400000), (950000, 600000), (500000, 350000)]),
    "g_wdv": (g_wdv, [(500000, 20), (800000, 15), (400000, 25), (600000, 10), (900000, 20)]),
    "g_hp": (g_hp, [(480000, 30000, 150000), (600000, 40000, 200000), (360000, 24000, 80000), (720000, 60000, 300000), (540000, 36000, 120000)]),
    "c_eoq": (c_eoq, [(600, 10, 9000), (400, 4, 8000), (500, 10, 5000), (300, 5, 9000), (800, 8, 16000)]),
    "c_bep": (c_bep, [(100, 5000, 140), (60, 7500, 90), (125, 4800, 175), (80, 9000, 120), (150, 3600, 250)]),
    "c_mpv": (c_mpv, [(40, 42, 5000, 4800), (25, 24, 8000, 8200), (60, 63, 2000, 2200), (80, 78, 1500, 1400), (35, 38, 4000, 4100)]),
    "c_wacc": (c_wacc, [(6, 4, 15, 10, 30), (3, 2, 14, 12, 25), (3, 1, 16, 10, 30), (7, 3, 12, 8, 25), (4, 6, 20, 12, 25)]),
    "c_opcycle": (c_opcycle, [(45, 20, 30, 40, 35), (30, 15, 25, 45, 30), (60, 10, 20, 50, 30), (40, 25, 35, 60, 45), (50, 20, 15, 35, 40)]),
    "c_process": (c_process, [(10000, 10, 10, 26), (8000, 5, 20, 30), (6000, 10, 8, 45), (12000, 5, 15, 22), (5000, 20, 12, 32)]),
    "c_capm": (c_capm, [(6, 1.2, 11), (7, 0.8, 12), (6.5, 1.5, 10.5), (5, 1.6, 10), (8, 0.5, 13)]),
    "l_lease": (l_lease, [(100000, 3, 10), (250000, 3, 12), (150000, 4, 10), (80000, 5, 8), (200000, 2, 9)]),
    "l_ifrs15": (l_ifrs15, [(900000, 800000, 400000), (450000, 360000, 240000), (1200000, 1000000, 500000), (630000, 500000, 250000), (990000, 600000, 500000)]),
    "l_ltcg": (l_ltcg, [(325000,), (525000,), (725000,), (1125000,), (275000,)]),
    "l_fx": (l_fx, [(83, 6, 2), (90, 7, 3), (82, 8, 4), (85, 5, 1), (88, 9, 3)]),
    "l_effint": (l_effint, [(950000, 12, 1000000, 10), (475000, 12, 500000, 10), (1900000, 11, 2000000, 9), (760000, 10, 800000, 8), (2850000, 9, 3000000, 7)]),
}
