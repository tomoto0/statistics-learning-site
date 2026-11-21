#!/usr/bin/env python3
"""Generate one consistent, original 3:2 SVG concept illustration per module."""
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/modules.json"
OUT = ROOT / "public/images/module-cards"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#101a2b"
PANEL = "#17263d"
GRID = "#2b3a53"
AXIS = "#8190a3"
MINT = "#61d6b3"
CORAL = "#ff8a76"
BLUE = "#8fb5ff"
GOLD = "#f0c46d"
PALE = "#dce7f3"
MUTED = "#9aabc0"

DESCRIPTIONS = {
    "statistical-thinking": "A schematic histogram shows a low-frequency, isolated right-tail bin; its mean is to the right of its median.",
    "probability": "A branching probability tree separates event and non-event cases.",
    "distributions": "Raw observations and a narrower sampling distribution of means.",
    "estimation": "Repeated estimates shown with uncertainty intervals and a reference value.",
    "p-values": "A null reference curve with highlighted two-sided tail regions.",
    "regression": "Paired observations and a fitted linear relationship.",
    "causal": "A confounder, treatment and outcome linked in a causal graph.",
    "time-series": "An ordered economic series with changing local variation.",
    "returns-risk": "A wealth path with a visible peak-to-trough drawdown.",
    "portfolio": "A portfolio risk curve that changes with co-movement.",
    "bayesian": "Prior and posterior distributions after evidence updates beliefs.",
    "backtesting": "Many strategy paths and one selected winner among them.",
    "correlation": "A scatterplot with a trend and an influential point.",
    "exploratory-data-analysis": "A compact histogram, box summary and scatter display.",
    "kernel-density": "Individual smooth kernels combining into a density estimate.",
    "statistical-tools": "A small data table flowing into a labeled chart.",
    "research-design": "A question-to-estimand workflow with a comparison design.",
    "experimental-design": "Eligible units randomly assigned to offer and comparison groups.",
    "iv-2sls": "A causal graph shows instrument Z affecting treatment D and outcome Y only through D, while U confounds D and Y. The exclusion restriction is the absence of a direct Z-to-Y arrow; relevance, independence, and exclusion remain assumptions.",
    "difference-in-differences": "Canonical two-group, two-period schematic aligned to the lesson example. Observed means are treated 50→56 and comparison 48→51; the open dashed treated-post value of 53 is the unobserved untreated counterfactual. The difference in changes is 3 illustrative outcome units under parallel trends.",
    "regression-discontinuity": "Local trends on either side of an assignment cutoff.",
    "panel-fixed-effects": "Repeated unit paths emphasize within-unit changes over time.",
    "robust-clustered-inference": "Observations grouped into assignment clusters.",
    "matching-weighting": "Treatment and comparison covariate distributions move toward overlap.",
    "synthetic-control": "A treated path and weighted comparison diverge after a policy.",
    "limited-outcomes": "Linear and logistic predictions on a probability scale.",
    "selection-missing-data": "The assigned sample is tracked into observed and missing outcomes; analysis of missing cases depends on assumptions.",
    "heterogeneous-effects": "Subgroup effect estimates and their uncertainty intervals.",
    "functional-form-specification": "Observed points compared with linear and curved fits.",
    "applied-macro-time-series": "A time-series history extends into a mean-reverting forecast band.",
    "multilevel-partial-pooling": "No-pooling group estimates move toward a shared population mean.",
    "complex-survey-sampling": "Unequal sample and population shares are reconciled with design weights.",
    "survival-duration-analysis": "Two event-free survival curves descend over a follow-up horizon.",
    "spatial-dependence-regional-econometrics": "A regional grid and neighbor links reveal spatial dependence.",
    "bootstrap-inference": "Repeated samples with replacement form an empirical distribution of a statistic.",
    "statistical-power-planning": "A rising power curve shows how sample size changes the chance of detection.",
    "measurement-error-economics": "Noisy measured predictors flatten an association under classical error assumptions.",
    "price-indices-real-values": "Weighted item price changes form an index used to deflate a nominal value.",
    "regularization-cross-validation": "Coefficient paths shrink as a penalty grows; a validation curve illustrates a bias–variance trade-off.",
    "meta-analysis-evidence-synthesis": "Study estimates with uncertainty intervals combine into a random-effects summary.",
    "causal-mediation-mechanisms": "Treatment, a proposed mediator, outcome, a direct path and possible hidden confounding are shown.",
    "partial-identification-bounds": "Incomplete binary outcomes yield an interval of compatible treatment effects rather than one point.",
}

VISIBLE_LABELS = {
    "statistical-thinking": "Histogram · mean (coral) > median (mint) · distant tail bin",
    "probability": "Branching event cases · probabilities omitted",
    "distributions": "Single outcomes vs sample means",
    "estimation": "Point estimates + intervals · reference value",
    "p-values": "Shaded tails: two-sided p-value under H₀",
    "regression": "Predictor X → outcome Y · fitted linear trend",
    "causal": "U confounder · D treatment · Y outcome",
    "time-series": "Observed series (blue) · trend (mint) · time",
    "returns-risk": "Wealth peak-to-trough decline = drawdown",
    "portfolio": "Portfolio risk changes with correlation ρ",
    "bayesian": "Prior (blue) → posterior (coral)",
    "backtesting": "Tried strategy paths · selected maximum (coral)",
    "correlation": "Paired X/Y · coral point is influential",
    "exploratory-data-analysis": "Histogram · box summary · paired values",
    "kernel-density": "Kernel contributions (mint) · density sum (coral)",
    "statistical-tools": "Rows → plot · gaps are not zeros",
    "research-design": "Question → population → comparison → estimand",
    "experimental-design": "Random offer · treatment vs comparison",
    "iv-2sls": "Exclusion assumption: no direct Z → Y path",
    "difference-in-differences": "Time · (56−50) − (51−48) = 3 units · parallel trends",
    "regression-discontinuity": "Assignment score · cutoff · local contrast",
    "panel-fixed-effects": "Time (t1–t5) · same units · within-unit changes",
    "robust-clustered-inference": "Districts are clusters · assignment affects inference",
    "matching-weighting": "Coral = treated · blue = comparison · mint = after weighting",
    "synthetic-control": "Blue = weighted synthetic · coral = treated",
    "limited-outcomes": "Blue = linear probability · coral = logit · counts are discrete",
    "selection-missing-data": "Observed/missing outcomes require assumptions",
    "heterogeneous-effects": "Subgroup effects · intervals · zero reference",
    "functional-form-specification": "Mint = linear · coral = curved fit · inspect residuals",
    "applied-macro-time-series": "Blue = observed history · coral = forecast · dashed = interval",
    "multilevel-partial-pooling": "No pooling vs partial pooling · group estimates",
    "complex-survey-sampling": "Population vs sample shares · weights target mix",
    "survival-duration-analysis": "Survival probability over follow-up time",
    "spatial-dependence-regional-econometrics": "Cell shade = illustrative values · gold = neighbor links",
    "bootstrap-inference": "Resample with replacement · statistic distribution · interval",
    "statistical-power-planning": "Power rises with n · plan for a meaningful effect",
    "measurement-error-economics": "Latent X vs noisy X* · attenuation under assumptions",
    "price-indices-real-values": "Basket weights → price index → real value",
    "regularization-cross-validation": "Penalty λ shrinks coefficients · choose with validation data",
    "meta-analysis-evidence-synthesis": "Study estimates + intervals · pooled mean allows heterogeneity",
    "causal-mediation-mechanisms": "T → M → Y · direct path · mediation assumptions matter",
    "partial-identification-bounds": "Observed data → lower and upper effect bounds",
}


def esc(value):
    return html.escape(str(value), quote=True)


def line(x1, y1, x2, y2, color=GRID, width=3, dash=None, opacity=1):
    attrs = f' stroke="{color}" stroke-width="{width}" opacity="{opacity}"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{attrs}/>'


def path(points, color=BLUE, width=6, fill="none", dash=None, opacity=1):
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    attrs = f' fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    return f'<polyline points="{coords}"{attrs}/>'


def circle(x, y, r=7, fill=BLUE, stroke=PANEL, sw=2, opacity=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'


def rect(x, y, w, h, fill=PANEL, stroke=GRID, radius=12, sw=2, opacity=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'


def label(x, y, value, color=PALE, size=16, anchor="middle", weight=700):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'


def arrow(x1, y1, x2, y2, color=MUTED, width=4, dash=None):
    attrs = f' stroke="{color}" stroke-width="{width}" marker-end="url(#arrow)"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{attrs}/>'


def grid():
    out = ""
    for x in (120, 210, 300, 390, 480):
        out += line(x, 105, x, 310, GRID, 1.5, opacity=.68)
    for y in (125, 185, 245, 305):
        out += line(75, y, 525, y, GRID, 1.5, opacity=.68)
    out += line(75, 310, 525, 310, AXIS, 2)
    out += line(75, 105, 75, 310, AXIS, 2)
    return out


def bell(cx, base, sx, sy, color, width=6, opacity=1):
    pts = []
    for i in range(49):
        x = cx - 3 * sx + 6 * sx * i / 48
        z = (x - cx) / sx
        y = base - math.exp(-.5 * z * z) * sy
        pts.append((x, y))
    return path(pts, color, width, opacity=opacity)


def draw(kind):
    s = grid()
    if kind == "statistical-thinking":
        vals = [24, 42, 60, 82, 106, 117, 106, 82, 60, 42, 24]
        for i, h in enumerate(vals):
            s += rect(105 + i * 32, 305 - h, 25, h, BLUE, "none", 4, 0, .8)
        s += line(278, 166, 278, 307, MINT, 5)  # median stays near the central bin
        s += line(284, 166, 284, 307, CORAL, 5)  # the distant right tail pulls the mean right
        s += rect(472, 281, 25, 24, GOLD, "none", 4, 0, .9)  # a low-frequency tail bin, not a floating point
    elif kind == "probability":
        s += line(300, 120, 205, 190, BLUE, 5) + line(300, 120, 395, 190, MINT, 5)
        s += line(205, 195, 155, 270, GOLD, 4) + line(205, 195, 255, 270, CORAL, 4)
        s += line(395, 195, 345, 270, BLUE, 4) + line(395, 195, 445, 270, MINT, 4)
        for x, y, c in [(300,120,CORAL),(205,190,BLUE),(395,190,MINT),(155,270,GOLD),(255,270,CORAL),(345,270,BLUE),(445,270,MINT)]:
            s += circle(x, y, 14 if y < 200 else 11, c, PANEL, 3)
    elif kind == "distributions":
        s += bell(300, 306, 115, 140, BLUE, 6, .68)
        s += bell(300, 306, 67, 116, MINT, 7, .98)
        s += line(300, 175, 300, 308, CORAL, 4, "7 7")
    elif kind == "estimation":
        s += line(300, 112, 300, 306, GOLD, 4, "8 8")
        for i, (center, width, c) in enumerate([(265,110,BLUE),(321,145,MINT),(278,70,CORAL),(340,110,GOLD),(292,160,BLUE)]):
            y = 138 + i * 37
            s += line(center-width/2, y, center+width/2, y, c, 5)
            s += line(center-width/2, y-9, center-width/2, y+9, c, 3)
            s += line(center+width/2, y-9, center+width/2, y+9, c, 3)
            s += circle(center, y, 7, c, PANEL, 2)
    elif kind == "p-values":
        s += bell(300, 304, 100, 145, BLUE, 6)
        s += path([(100,304),(100,295),(120,274),(140,252),(160,236),(180,231),(195,247),(205,274),(215,304)], CORAL, 2, "#ff8a7633")
        s += path([(385,304),(395,274),(405,247),(420,231),(440,236),(460,252),(480,274),(500,295),(500,304)], CORAL, 2, "#ff8a7633")
        s += line(205, 157, 205, 306, GOLD, 4)
        s += line(395, 157, 395, 306, GOLD, 4)
    elif kind == "regression":
        for i in range(13):
            x = 115 + i * 31
            y = 275 - i * 11 + [18,-8,7,-14,12,-6,8,-17,13,-7,6,-12,9][i]
            s += circle(x, y, 7, BLUE, PANEL, 2, .95)
        s += path([(100,284),(505,144)], CORAL, 7)
    elif kind == "causal":
        for x1,y1,x2,y2,c in [(194,196,272,143,CORAL),(194,207,355,228,CORAL),(326,144,403,195,MINT)]:
            s += arrow(x1,y1,x2,y2,c,5)
        for x,y,txt,c in [(160,205,"U",GOLD),(300,132,"D",CORAL),(430,208,"Y",MINT)]:
            s += circle(x,y,34,c,PANEL,4) + label(x,y+6,txt,NAVY,20)
    elif kind == "time-series":
        pts = [(82,228),(112,199),(140,215),(170,174),(198,193),(225,152),(253,163),(280,120),(307,171),(335,148),(363,188),(391,151),(419,205),(447,160),(476,178),(505,138),(525,156)]
        s += path(pts, BLUE, 6)
        s += path([(82,265),(145,255),(208,248),(271,233),(334,240),(397,222),(460,226),(525,208)], MINT, 5)
        s += rect(247, 105, 105, 205, "#ff8a7610", "none", 0, 0)
    elif kind == "returns-risk":
        pts = [(82,263),(120,235),(156,250),(192,190),(230,179),(266,212),(302,146),(338,167),(374,118),(410,157),(446,142),(484,183),(525,132)]
        s += path(pts, MINT, 7)
        s += path([(374,118),(410,157),(446,142),(484,183)], CORAL, 7)
        s += line(374,118,484,118,GOLD,3,"7 7")
        s += path([(374,118),(410,157),(446,142),(484,183),(484,118)], CORAL, 1, "#ff8a7628")
    elif kind == "portfolio":
        pts = []
        for i in range(41):
            x = 92 + i * 10.3
            q = -1 + i / 20
            y = 144 + 105 * (q - .08) ** 2
            pts.append((x,y))
        s += path(pts, BLUE, 7)
        s += circle(290, 153, 10, CORAL, PALE, 3)
        s += line(290, 153, 290, 304, CORAL, 3, "7 7")
    elif kind == "bayesian":
        s += bell(265, 304, 95, 128, BLUE, 6)
        s += bell(335, 304, 72, 150, CORAL, 7)
        s += line(265, 178, 265, 305, BLUE, 3, "5 6")
        s += line(335, 154, 335, 305, CORAL, 3, "5 6")
    elif kind == "backtesting":
        for j in range(7):
            pts = []
            for i in range(9):
                x = 90 + i * 52
                y = 244 - j * 7 + math.sin(i * .85 + j * 1.3) * (13 + j)
                pts.append((x,y))
            s += path(pts, BLUE if j % 2 == 0 else MINT, 3.5, opacity=.48)
        s += path([(90,251),(143,236),(196,224),(249,209),(302,195),(355,177),(408,151),(461,126),(514,106)], CORAL, 7)
    elif kind == "correlation":
        for i in range(14):
            x = 115 + (i % 7) * 58
            row = i // 7
            y = 269 - (i % 7) * 20 + (12 if row else -8)
            s += circle(x, y, 7, BLUE, PANEL, 2)
        s += path([(115,270),(500,132)], MINT, 6)
        s += circle(498, 274, 11, CORAL, PALE, 3)
    elif kind == "exploratory-data-analysis":
        for i,h in enumerate([38,58,78,105,120,92,66,45]):
            s += rect(92+i*25, 300-h, 18, h, BLUE, "none", 4, 0, .9)
        s += rect(335, 162, 188, 116, "none", GRID, 14, 3)
        s += line(352,220,503,220,GOLD,5)
        s += line(385,202,465,202,MINT,7)
        s += circle(429,202,9,CORAL,PANEL,3)
        for x,y in [(362,252),(380,240),(405,258),(430,246),(456,261),(482,240),(505,254)]:
            s += circle(x,y,5,BLUE,PANEL,1)
    elif kind == "kernel-density":
        s += bell(205, 305, 48, 85, MINT, 3, .65)
        s += bell(300, 305, 53, 112, MINT, 3, .65)
        s += bell(398, 305, 48, 80, MINT, 3, .65)
        pts=[]
        for i in range(49):
            x=85+i*9.1
            y=305-(math.exp(-.5*((x-205)/48)**2)*85+math.exp(-.5*((x-300)/53)**2)*112+math.exp(-.5*((x-398)/48)**2)*80)*.58
            pts.append((x,y))
        s += path(pts,CORAL,7)
        for x in (205,300,398): s += line(x,300,x,314,BLUE,3)
    elif kind == "statistical-tools":
        for i in range(5):
            s += line(94,138+i*31,257,138+i*31,GRID,2)
        for i in range(4):
            s += line(94+i*42,122,94+i*42,272,GRID,2)
        s += rect(94,122,163,31,"#8fb5ff22",GRID,5,1)
        s += arrow(274,201,324,201,GOLD,4)
        s += line(337,270,522,270,AXIS,2) + line(337,270,337,130,AXIS,2)
        s += path([(350,246),(375,230),(397,239),(422,190),(447,205),(470,160),(496,174),(516,140)],MINT,6)
        for x,y in [(375,230),(422,190),(470,160),(516,140)]: s += circle(x,y,5,CORAL,PANEL,2)
    elif kind == "research-design":
        xs=[82,203,324,445]
        colors=[BLUE,CORAL,MINT,GOLD]
        for i,(x,c) in enumerate(zip(xs,colors)):
            s += rect(x,158,91,92,PANEL,c,18,3)
            s += circle(x+45,184,10,c,PANEL,2)
            s += line(x+23,216,x+68,216,c,4)
        for x in (177,298,419): s += arrow(x,204,x+22,204,MUTED,3)
    elif kind == "experimental-design":
        s += circle(300,150,36,BLUE,PANEL,4)
        s += arrow(276,177,198,235,CORAL,5) + arrow(324,177,402,235,MINT,5)
        for x,c in [(180,CORAL),(420,MINT)]:
            s += rect(x-73,226,146,70,PANEL,c,17,3)
            for j in range(3): s += circle(x-38+j*38,260,8,c,PANEL,2)
    elif kind == "iv-2sls":
        s += arrow(183,201,279,145,MINT,5) + arrow(322,145,418,201,MINT,5)
        s += arrow(300,242,300,161,GOLD,4) + arrow(326,256,412,224,GOLD,4)  # U causes both D and Y
        for x,y,t,c in [(155,210,"Z",MINT),(300,128,"D",CORAL),(445,210,"Y",BLUE),(300,275,"U",GOLD)]:
            s += circle(x,y,33,c,PANEL,4) + label(x,y+7,t,NAVY,20)
    elif kind == "difference-in-differences":
        x_pre,x_post,x_gap=165,440,535
        Y=lambda value:310-(value-40)*10
        for value in (40,45,50,55,60):
            y=Y(value);s+=line(75,y,525,y,GRID,1.5)+label(62,y+5,str(value),MUTED,11,"end",500)
        s+=label(190,82,"Treated · observed",CORAL,11)+line(95,78,125,78,CORAL,5)
        s+=label(370,82,"Comparison · observed",BLUE,11)+line(270,78,300,78,BLUE,5)
        s+=line(105,96,135,96,CORAL,3,"8 8")+label(310,100,"Dashed: treated if untreated (unobserved)",PALE,10)
        s+=line(75,310,525,310,AXIS,2)+line(75,105,75,310,AXIS,2)
        s+='<text x="34" y="205" transform="rotate(-90 34 205)" fill="{0}" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">Mean outcome (illustrative units)</text>'.format(PALE)
        s+=line(310,105,310,310,GOLD,3,"8 7")+label(310,119,"Treatment starts",GOLD,10)
        comparison=[(x_pre,Y(48)),(x_post,Y(51))]
        treated=[(x_pre,Y(50)),(x_post,Y(56))]
        counterfactual=[(x_pre,Y(50)),(x_post,Y(53))]
        s+=path(comparison,BLUE,6)+path(treated,CORAL,6)+path(counterfactual,CORAL,3,dash="8 8",opacity=.95)
        for x,y in comparison:s+=circle(x,y,6,BLUE,PANEL,2)
        for x,y in treated:s+=circle(x,y,6,CORAL,PANEL,2)
        s+=circle(x_post,Y(53),6,PANEL,CORAL,3)
        s+=label(x_pre-12,Y(50)-8,"50",CORAL,11,"end")+label(x_pre-12,Y(48)+14,"48",BLUE,11,"end")
        s+=label(x_post+14,Y(56)-8,"56",CORAL,11,"start")+label(x_post+14,Y(53)-8,"53 · unobserved",CORAL,10,"start")+label(x_post+14,Y(51)+14,"51",BLUE,11,"start")
        s+=line(x_gap,Y(56),x_gap,Y(53),MINT,2)+line(x_gap-6,Y(56),x_gap+6,Y(56),MINT,2)+line(x_gap-6,Y(53),x_gap+6,Y(53),MINT,2)+label(545,169,"DiD = 3",MINT,10,"start")
        s+=line(x_pre,310,x_pre,316,MUTED,1)+line(x_post,310,x_post,316,MUTED,1)+label(x_pre,331,"Pre",PALE,11)+label(x_post,331,"Post",PALE,11)
    elif kind == "regression-discontinuity":
        s += line(300,105,300,310,GOLD,4,"8 8")
        for i in range(10):
            x=105+i*19; y=266-i*8+[7,-5,4,-7,5,-3,8,-4,3,-5][i]
            s += circle(x,y,6,BLUE,PANEL,2)
        for i in range(10):
            x=316+i*19; y=195-(x-316)*.34+[4,-6,7,-3,2,-5,5,-4,3,-2][i]
            s += circle(x,y,6,CORAL,PANEL,2)
        s += path([(100,268),(294,184)],BLUE,6) + path([(307,169),(510,83)],CORAL,6)
    elif kind == "panel-fixed-effects":
        for i,(offset,c) in enumerate([(0,BLUE),(42,MINT),(84,CORAL)]):
            y=160+offset
            pts=[(98,y),(205,y-20),(300,y-38),(410,y-57),(510,y-72)]
            s += path(pts,c,5,opacity=.9)
            for x,yy in pts: s += circle(x,yy,5,c,PANEL,2)
            s += label(520,pts[-1][1]+4,f"Unit {i+1}",c,9,"start",600)
        for i,x in enumerate([98,205,300,410,510]): s += label(x,328,f"t{i+1}",MUTED,9,"middle",500)
        s += '<text x="34" y="208" transform="rotate(-90 34 208)" fill="{0}" font-family="Arial, sans-serif" font-size="9" font-weight="500" text-anchor="middle">Outcome (illustrative units)</text>'.format(MUTED)
    elif kind == "robust-clustered-inference":
        for i,(x,c) in enumerate([(115,BLUE),(265,MINT),(415,CORAL)]):
            s += rect(x,146,105,133,"#17263d",c,19,3)
            for j in range(5):
                px=x+24+(j%2)*42
                py=173+(j//2)*34+(i%2)*3
                s += circle(px,py,7,c,PANEL,2)
        s += line(85,304,530,304,AXIS,2)
    elif kind == "matching-weighting":
        s += line(96,96,118,96,CORAL,4)+label(125,100,"Treated",CORAL,9,"start")
        s += line(223,96,245,96,BLUE,4)+label(252,100,"Comparison",BLUE,9,"start")
        s += line(376,96,398,96,MINT,4)+label(405,100,"After weights",MINT,9,"start")
        s += bell(235,300,87,112,CORAL,5,.7)
        s += bell(355,300,86,112,BLUE,5,.7)
        s += bell(295,300,80,113,MINT,7,.95)
        s += line(295,175,295,306,GOLD,3,"8 8")
    elif kind == "synthetic-control":
        s += line(120,94,144,94,BLUE,4)+label(151,98,"Weighted synthetic",BLUE,9,"start")
        s += line(350,94,374,94,CORAL,4)+label(381,98,"Treated",CORAL,9,"start")
        s += line(300,105,300,310,GOLD,4,"8 8")
        s += path([(85,262),(190,229),(295,191),(400,156),(510,126)],BLUE,7)
        s += path([(85,268),(190,235),(295,197),(400,124),(510,81)],CORAL,7)
        for x,y in [(85,262),(190,229),(295,191),(400,156),(510,126)]: s += circle(x,y,5,BLUE,PANEL,2)
        for x,y in [(85,268),(190,235),(295,197),(400,124),(510,81)]: s += circle(x,y,5,CORAL,PANEL,2)
    elif kind == "limited-outcomes":
        s += line(116,94,140,94,BLUE,4)+label(147,98,"Linear probability",BLUE,9,"start")
        s += line(343,94,367,94,CORAL,4)+label(374,98,"Logit",CORAL,9,"start")
        s += path([(86,260),(180,225),(270,192),(360,156),(450,121),(520,98)],BLUE,6)
        pts=[]
        for i in range(49):
            x=85+i*9.1
            y=288-190/(1+math.exp(-(x-300)/54))
            pts.append((x,y))
        s += path(pts,CORAL,7)
    elif kind == "selection-missing-data":
        for i,(x,c) in enumerate([(190,BLUE),(410,CORAL)]):
            s += rect(x-66,132,132,46,PANEL,c,12,3)
            s += arrow(x,180,x-38,222,MINT,4) + arrow(x,180,x+38,222,CORAL,4)
            s += rect(x-77,236,68,48,"#61d6b322",MINT,10,2)
            s += rect(x+9,236,68,48,"#ff8a7622",CORAL,10,2)
            s += line(x-55,259,x-29,259,MINT,4) + line(x+29,259,x+55,259,CORAL,4)
    elif kind == "heterogeneous-effects":
        s += line(300,105,300,310,GOLD,3,"8 8")
        for i,(center,c) in enumerate([(244,BLUE),(300,MINT),(352,CORAL),(277,GOLD)]):
            y=145+i*42; w=[92,138,86,110][i]
            s += line(center-w/2,y,center+w/2,y,c,5)
            s += line(center-w/2,y-9,center-w/2,y+9,c,3) + line(center+w/2,y-9,center+w/2,y+9,c,3)
            s += circle(center,y,7,c,PANEL,2)
    elif kind == "functional-form-specification":
        for i in range(13):
            x=103+i*32; z=-1+2*i/12
            y=240-55*z-65*z*z+[10,-8,12,-6,7,-11,9,-4,8,-7,4,-9,7][i]
            s += circle(x,y,6,BLUE,PANEL,2)
        s += path([(90,188),(530,153)],MINT,5)
        pts=[]
        for i in range(41):
            x=90+i*11
            z=(x-310)/220
            pts.append((x,240-55*z-65*z*z))
        s += path(pts,CORAL,7)
    elif kind == "applied-macro-time-series":
        s += line(90,94,114,94,BLUE,4)+label(121,98,"Observed",BLUE,9,"start")
        s += line(234,94,258,94,CORAL,4)+label(265,98,"Forecast mean",CORAL,9,"start")
        s += line(405,94,429,94,CORAL,2,"7 7")+label(436,98,"Uncertainty",PALE,9,"start")
        hist=[(82,198),(110,177),(138,194),(166,161),(194,182),(222,140),(250,167),(278,148),(306,184),(334,158),(362,192),(390,171),(418,209),(446,181)]
        s += path(hist,BLUE,6)
        s += line(446,105,446,310,GOLD,3,"8 8")
        forecast=[]
        for i in range(1,7):
            x=446+i*13
            y=181+(1-math.pow(.68,i))*32
            forecast.append((x,y))
        s += path(forecast,CORAL,7)
        s += path([(446,170),(459,156),(472,149),(485,144),(498,141),(511,139),(524,137)],CORAL,2,dash="7 7",opacity=.75)
        s += path([(446,192),(459,206),(472,214),(485,219),(498,223),(511,226),(524,229)],CORAL,2,dash="7 7",opacity=.75)
    elif kind == "multilevel-partial-pooling":
        s += line(300,105,300,309,GOLD,3,"7 7")
        for i,(obs,pooled,c) in enumerate([(166,222,BLUE),(237,265,MINT),(366,331,CORAL),(448,391,GOLD)]):
            y=143+i*43
            s += line(90,y,520,y,GRID,1.5)
            s += line(obs,y,300,y,c,2.5)
            s += circle(obs,y,7,CORAL,PANEL,2)
            s += circle(pooled,y,7,MINT,PANEL,2)
        s += line(85,322,520,322,AXIS,2)
        s += label(174,116,"Local",CORAL,13) + label(365,116,"Pooled",MINT,13)
    elif kind == "complex-survey-sampling":
        s += rect(105,124,414,62,"#17263d",GRID,13,2)
        s += rect(105,124,152,62,CORAL,"none",13,0,.88)
        s += rect(105,215,414,62,"#17263d",GRID,13,2)
        s += rect(105,215,243,62,BLUE,"none",13,0,.88)
        s += label(300,111,"Population",PALE,14)
        s += label(300,202,"Unequal-probability sample",PALE,13)
        s += line(257,128,257,182,GOLD,3,"5 5")
        s += line(348,219,348,273,GOLD,3,"5 5")
        s += arrow(260,301,345,301,MINT,4)
        s += label(300,332,"Weights restore the target mix",MINT,13)
    elif kind == "survival-duration-analysis":
        s += line(92,305,520,305,AXIS,2) + line(92,105,92,305,AXIS,2)
        for y in (155,205,255): s += line(92,y,520,y,GRID,1.5)
        s += path([(96,111),(155,126),(212,151),(270,183),(328,218),(388,249),(450,273),(518,289)],BLUE,6)
        s += path([(96,111),(155,143),(212,181),(270,219),(328,253),(388,276),(450,291),(518,299)],CORAL,6)
        for x,y in [(188,141),(301,201),(419,261)]: s += line(x,y-7,x,y+7,GOLD,3)
        s += label(175,112,"Lower hazard",BLUE,12) + label(400,151,"Higher hazard",CORAL,12)
    elif kind == "spatial-dependence-regional-econometrics":
        palette=[BLUE,"#6f92c9","#89a1bf",MINT,CORAL,GOLD]
        for row in range(5):
            for col in range(5):
                x=100+col*54; y=119+row*43
                color=palette[(row*2+col+(row//2))%len(palette)]
                s += rect(x,y,42,32,color,"#dce7f3",5,1,.83)
        for a,b in [((121,135),(175,135)),((175,135),(229,178)),((229,178),(283,178)),((175,221),(229,178)),((283,178),(337,221)),((337,221),(391,221)),((229,264),(283,221))]:
            s += line(a[0],a[1],b[0],b[1],GOLD,2.5,opacity=.82)
        s += label(447,165,"Cell shading",PALE,10) + label(447,181,"= regional value",MUTED,9)
        s += line(393,214,420,214,GOLD,2.5,opacity=.82) + label(427,218,"Neighbor link",GOLD,9,"start",600)
    elif kind == "bootstrap-inference":
        s += label(145,126,"Observed sample",BLUE,11) + label(297,126,"Resample n with replacement",MINT,10)
        s += label(459,126,"Repeat T*",CORAL,10) + label(459,146,"many times",MUTED,9)
        for i, x in enumerate([120,151,182,213]):
            s += rect(x,161,23,24,BLUE if i != 2 else GOLD,"none",5,0,.9)
            s += rect(x,202,23,24,[BLUE,GOLD,BLUE,MINT][i],"none",5,0,.85)
            s += rect(x,243,23,24,[GOLD,BLUE,MINT,BLUE][i],"none",5,0,.85)
        s += arrow(230,194,267,194,MUTED,3) + arrow(391,194,421,194,MUTED,3)
        for i, h in enumerate([24,42,63,87,106,90,68,45,26]):
            s += rect(438+i*10,307-h,7,h,[BLUE,BLUE,MINT,CORAL,CORAL,CORAL,MINT,BLUE,BLUE][i],"none",3,0,.9)
        s += line(466,188,466,309,GOLD,2,"6 5")
        s += label(482,321,"Empirical T* distribution",PALE,9)
    elif kind == "statistical-power-planning":
        s += line(95,305,520,305,AXIS,2) + line(95,115,95,305,AXIS,2)
        for y in [150,205,260]: s += line(95,y,520,y,GRID,1.5)
        s += line(95,175,520,175,GOLD,2,"7 6")
        s += label(503,164,"80% target",GOLD,9,"end")
        pts=[]
        for i in range(21):
            x=105+i*19.5; z=i/20
            pts.append((x,294-116*(1-math.exp(-3*z))))
        s += path(pts,CORAL,7)
        s += circle(*pts[12],7,MINT,PANEL,2) + label(300,112,"Effect, noise, α and n",PALE,10)
        s += label(300,331,"Independent sample size n →",PALE,10)
    elif kind == "measurement-error-economics":
        s += label(184,116,"Latent X",BLUE,11) + label(422,116,"Noisy observed X*",CORAL,11)
        for i,(x,y) in enumerate([(112,268),(144,248),(176,226),(208,201),(240,180),(272,154)]):
            s += circle(x,y,5,BLUE,PANEL,1.5)
        s += line(106,275,278,145,MINT,4)
        for i,(x,y) in enumerate([(334,251),(370,246),(398,204),(421,221),(451,175),(476,198),(506,145),(532,170)]):
            s += circle(x,y,5,CORAL,PANEL,1.5)
        s += line(329,250,537,176,BLUE,3) + line(329,264,537,129,MINT,4)
        s += label(427,292,"Observed slope can flatten",PALE,9)
        s += label(427,309,"under classical-error assumptions",MUTED,8)
    elif kind == "price-indices-real-values":
        s += label(180,116,"Basket & price relatives",PALE,10) + label(438,116,"Index base = 100",GOLD,11)
        for i,(name,h,c) in enumerate([("Food",69,BLUE),("Rent",112,CORAL),("Travel",48,MINT)]):
            x=128+i*66
            s += rect(x,290-h,40,h,c,"none",7,0,.9)
            s += label(x+20,280-h,name,PALE,8)
            s += circle(x+20,306,6,GOLD,PANEL,1.5)
        s += arrow(352,209,383,209,MUTED,3)
        s += rect(394,164,92,72,"#263650",GOLD,12,2)
        s += label(440,194,"Weighted",PALE,9) + label(440,215,"index",GOLD,12)
        s += arrow(490,209,514,209,MUTED,3)
        s += label(468,268,"Nominal ÷ price index",MINT,9)
        s += label(468,286,"= real value",PALE,10)
    elif kind == "regularization-cross-validation":
        s += line(90,305,520,305,AXIS,2) + line(90,115,90,305,AXIS,2)
        s += path([(103,150),(184,172),(265,215),(346,252),(427,274),(510,287)],BLUE,6)
        s += path([(103,284),(184,261),(265,225),(346,190),(427,156),(510,133)],CORAL,6)
        s += path([(103,250),(184,213),(265,167),(346,148),(427,170),(510,225)],MINT,5)
        s += line(351,112,351,305,GOLD,3,"7 7") + label(350,105,"validation minimum",GOLD,9)
    elif kind == "meta-analysis-evidence-synthesis":
        s += line(300,105,300,306,GOLD,3,"7 7")
        for i,(center,width,c) in enumerate([(245,115,BLUE),(321,92,MINT),(365,136,CORAL),(280,105,GOLD),(335,158,BLUE)]):
            y=136+i*38
            s += line(center-width/2,y,center+width/2,y,c,4) + circle(center,y,7,c,PANEL,2)
        s += path([(271,315),(302,299),(336,315),(302,331),(271,315)],MINT,3,MINT)
    elif kind == "causal-mediation-mechanisms":
        s += arrow(197,203,278,157,BLUE,5) + arrow(321,157,402,203,MINT,5)
        s += arrow(199,183,401,183,CORAL,4) + arrow(300,262,291,180,GOLD,3,"7 6") + arrow(315,262,408,221,GOLD,3,"7 6")
        for x,y,t,c in [(175,213,"T",BLUE),(300,145,"M",CORAL),(425,213,"Y",MINT),(306,282,"U",GOLD)]:
            s += circle(x,y,29,c,PANEL,4) + label(x,y+7,t,NAVY,19)
    elif kind == "partial-identification-bounds":
        s += label(300,116,"Compatible group means",PALE,12)
        s += line(150,165,390,165,BLUE,8) + line(150,151,150,179,BLUE,3) + line(390,151,390,179,BLUE,3)
        s += line(205,217,460,217,MINT,8) + line(205,203,205,231,MINT,3) + line(460,203,460,231,MINT,3)
        s += line(300,106,300,301,GOLD,3,"7 7")
        s += line(270,282,435,282,CORAL,8) + line(270,268,270,296,CORAL,3) + line(435,268,435,296,CORAL,3)
    else:
        raise KeyError(f"No card illustration renderer for {kind!r}")
    return s


modules = json.loads(DATA.read_text())
ids = [module["id"] for module in modules]
missing = sorted(set(ids) - set(DESCRIPTIONS))
unknown = sorted(set(DESCRIPTIONS) - set(ids))
missing_labels = sorted(set(ids) - set(VISIBLE_LABELS))
unknown_labels = sorted(set(VISIBLE_LABELS) - set(ids))
if missing or unknown or missing_labels or unknown_labels:
    raise SystemExit(f"Card illustration map mismatch: descriptions missing={missing}, unknown={unknown}; labels missing={missing_labels}, unknown={unknown_labels}")

for module in modules:
    module_id = module["id"]
    title = module.get("title", module_id)
    desc = DESCRIPTIONS[module_id]
    inner = draw(module_id)
    inner += label(300, 346, VISIBLE_LABELS[module_id], PALE, 11)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)} — concept illustration</title>
<desc id="desc">{esc(desc)} Original schematic for learning, not measured data.</desc>
<defs>
  <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="#15243a"/></linearGradient>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L0,10 L9,5 z" fill="{MUTED}"/></marker>
</defs>
<rect width="600" height="400" rx="28" fill="url(#surface)"/>
<rect x="18" y="18" width="564" height="364" rx="23" fill="{PANEL}" stroke="#31415a" stroke-width="2"/>
{inner}
<text x="548" y="365" text-anchor="end" fill="{MUTED}" font-family="Arial, sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">CONCEPT · NOT DATA</text>
</svg>
'''
    out_path = OUT / f"{module_id}.svg"
    out_path.write_text(svg)
    module["cardImage"] = f"/images/module-cards/{module_id}.svg"

DATA.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Generated {len(modules)} consistent module card illustrations in {OUT}")
