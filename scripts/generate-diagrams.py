#!/usr/bin/env python3
"""Generate original, source-controlled SVG schematics for the applied-economics lessons."""
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/modules.json"
OUT = ROOT / "public/diagrams"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#172239"
MUTED = "#657286"
CORAL = "#e66d59"
MINT = "#4b9279"
BLUE = "#6c8fca"
GOLD = "#d8a847"
PALE = "#f4f6f7"
GRID = "#dce2e7"
WHITE = "#ffffff"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, label, size=12, color=NAVY, weight=500, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(label)}</text>'


def line(x1, y1, x2, y2, color=GRID, width=1.5, dash=None, marker=False):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    extra += ' marker-end="url(#arrow)"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{extra}/>'


def rect(x, y, w, h, fill=WHITE, stroke=GRID, radius=13, sw=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def circle(x, y, r, fill=BLUE, stroke="none", sw=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def poly(points, color=BLUE, width=3, fill="none", dash=None):
    p = " ".join(f"{x},{y}" for x, y in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{p}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def document(title, subtitle, inner, height=244):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{height}" viewBox="0 0 760 {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle)} Original explanatory schematic, not measured data.</desc>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L0,9 L8,4.5 z" fill="{MUTED}"/></marker></defs>
<rect x="0" y="0" width="760" height="{height}" rx="18" fill="{PALE}"/>
{inner}
<text x="738" y="{height - 15}" text-anchor="end" fill="{MUTED}" font-family="Arial, sans-serif" font-size="9">ORIGINAL SCHEMATIC · NOT DATA</text>
</svg>'''


def flow_box(x, title, sub, fill=WHITE, stroke=BLUE):
    return rect(x, 86, 144, 74, fill, stroke) + text(x + 72, 115, title, 12, NAVY, 700, "middle") + text(x + 72, 137, sub, 10, MUTED, 500, "middle")


def build_svgs():
    art = {}
    # Research design: state the target before selecting the estimator.
    s = text(26, 30, "A defensible analysis starts with the question", 15, NAVY, 700)
    s += flow_box(28, "Population", "Who is the claim about?", "#edf2fa", BLUE)
    s += flow_box(210, "Treatment & outcome", "Assigned, measured, and when?", "#fff2ed", CORAL)
    s += flow_box(392, "Comparison design", "What is the counterfactual?", "#eef7f2", MINT)
    s += flow_box(574, "Estimand & checks", "Effect, for whom, assumptions?", "#fbf4e3", GOLD)
    for x in [174, 356, 538]:
        s += line(x, 123, x + 30, 123, MUTED, 2, marker=True)
    art["research-design"] = document("From question to credible estimate", "Question, population, treatment, comparison design and estimand flow.", s)

    # Randomization.
    s = text(26, 30, "Random assignment makes offer and comparison groups comparable", 15, NAVY, 700)
    s += rect(30, 82, 160, 76, "#edf2fa", BLUE) + text(110, 112, "Eligible units", 13, NAVY, 700, "middle") + text(110, 134, "define the study sample", 10, MUTED, 500, "middle")
    s += line(190, 120, 260, 120, MUTED, 2, marker=True)
    s += rect(266, 91, 124, 58, WHITE, MUTED) + text(328, 116, "Random", 12, NAVY, 700, "middle") + text(328, 134, "assignment", 11, NAVY, 600, "middle")
    s += line(390, 105, 460, 79, CORAL, 2, marker=True) + line(390, 136, 460, 163, BLUE, 2, marker=True)
    s += rect(466, 50, 248, 58, "#fff2ed", CORAL) + text(590, 75, "Offer group", 12, NAVY, 700, "middle") + text(590, 94, "estimate intention-to-treat", 10, MUTED, 500, "middle")
    s += rect(466, 133, 248, 58, "#edf2fa", BLUE) + text(590, 158, "Comparison group", 12, NAVY, 700, "middle") + text(590, 177, "same assignment lottery", 10, MUTED, 500, "middle")
    s += text(590, 215, "Compare outcomes by original assignment", 10, MINT, 600, "middle")
    art["experimental-design"] = document("Randomized policy trial", "Eligible units are randomly assigned to an offer or comparison group; compare outcomes by assignment.", s)

    # IV DAG.
    s = text(26, 30, "Instrument-driven variation isolates a treatment contrast only under assumptions", 15, NAVY, 700)
    nodes = {"Z": (146, 120, "Z · instrument", "external variation"), "D": (378, 86, "D · treatment", "endogenous choice"), "Y": (620, 120, "Y · outcome", "policy result"), "U": (378, 184, "U · common causes", "unobserved factors")}
    s += line(205, 116, 317, 89, MINT, 3, marker=True) + line(438, 90, 561, 114, MINT, 3, marker=True)
    s += line(416, 164, 416, 111, GOLD, 2.5, marker=True) + line(437, 176, 566, 135, GOLD, 2.5, marker=True)
    for key, (x, y, label, sub) in nodes.items():
        fill, stroke = {"Z": ("#edf7f2", MINT), "D": ("#fff2ed", CORAL), "Y": ("#edf2fa", BLUE), "U": ("#fff7e6", GOLD)}[key]
        s += rect(x - 75, y - 27, 150, 54, fill, stroke) + text(x, y - 3, label, 12, NAVY, 700, "middle") + text(x, y + 15, sub, 9, MUTED, 500, "middle")
    s += text(146, 207, "No direct Z → Y path (exclusion)", 10, MINT, 600, "middle")
    s += text(380, 237, "Relevance, independence, and exclusion are assumptions", 9, MUTED, 500, "middle")
    art["iv-2sls"] = document("Instrumental variables causal graph", "Z affects D and D affects Y; U confounds D and Y. Instrument relevance, independence from unobserved outcome causes, and exclusion are identifying assumptions, not facts proven by the graph.", s, height=272)

    # Canonical two-group, two-period DiD: display all four observed cell means and the missing counterfactual.
    s = text(26, 29, "Two groups, two periods: compare changes", 15, NAVY, 700)
    s += line(31, 52, 53, 52, CORAL, 3) + text(59, 56, "Treated · observed", 9, CORAL, 600)
    s += line(214, 52, 236, 52, BLUE, 3) + text(242, 56, "Comparison · observed", 9, BLUE, 600)
    s += line(427, 52, 449, 52, CORAL, 2.5, "7 5") + text(455, 56, "Treated · untreated counterfactual", 9, CORAL, 600)
    x_pre, x_post, x_gap = 205, 490, 620
    y0 = 207
    Y = lambda value: y0 - (value - 40) * 6
    s += line(93, 219, 628, 219, MUTED, 1.5) + line(93, 219, 93, 87, MUTED, 1.5)
    s += '<text x="32" y="153" transform="rotate(-90 32 153)" fill="{0}" font-family="Arial, sans-serif" font-size="10" font-weight="500" text-anchor="middle">Mean outcome (illustrative units)</text>'.format(MUTED)
    for value in (40, 45, 50, 55, 60):
        y = Y(value)
        s += line(93, y, 628, y, GRID, 1) + text(85, y + 3, str(value), 8, MUTED, 500, "end")
    for x, label in ((x_pre, "Pre"), (x_post, "Post")):
        s += line(x, 219, x, 224, MUTED, 1) + text(x, 238, label, 9, MUTED, 600, "middle")
    s += text(358, 257, "Period", 10, MUTED, 500, "middle")
    s += line(350, 88, 350, 219, GOLD, 1.8, "6 5") + text(350, 83, "Treatment begins", 8, GOLD, 700, "middle")
    means = {"treated_pre": 50, "comparison_pre": 48, "comparison_post": 51, "treated_counterfactual_post": 53, "treated_observed_post": 56}
    treated = [(x_pre, Y(means["treated_pre"])), (x_post, Y(means["treated_observed_post"]))]
    comparison = [(x_pre, Y(means["comparison_pre"])), (x_post, Y(means["comparison_post"]))]
    counterfactual = [(x_pre, Y(means["treated_pre"])), (x_post, Y(means["treated_counterfactual_post"]))]
    s += poly(comparison, BLUE, 3) + poly(treated, CORAL, 3) + poly(counterfactual, CORAL, 2.5, dash="7 5")
    for x, y in comparison: s += circle(x, y, 4.5, BLUE)
    for x, y in treated: s += circle(x, y, 4.5, CORAL)
    s += circle(x_post, Y(means["treated_counterfactual_post"]), 5, WHITE, CORAL, 2)
    s += text(x_pre - 11, Y(means["treated_pre"]) - 7, "50", 8, CORAL, 700, "end")
    s += text(x_pre - 11, Y(means["comparison_pre"]) + 12, "48", 8, BLUE, 700, "end")
    s += text(x_post + 9, Y(means["treated_observed_post"]) - 5, "56", 8, CORAL, 700)
    s += text(x_post + 9, Y(means["treated_counterfactual_post"]) - 4, "53 · unobserved", 8, CORAL, 700)
    s += text(x_post + 9, Y(means["comparison_post"]) + 12, "51", 8, BLUE, 700)
    top, bottom = Y(means["treated_observed_post"]), Y(means["treated_counterfactual_post"])
    s += line(x_gap, top, x_gap, bottom, MINT, 2) + line(x_gap - 5, top, x_gap + 5, top, MINT, 2) + line(x_gap - 5, bottom, x_gap + 5, bottom, MINT, 2)
    s += text(x_gap + 8, bottom + 12, "DiD = 3 units", 8, MINT, 700)
    s += text(33, 282, "(56 − 50) − (51 − 48) = 3 · causal meaning requires parallel trends", 10, MUTED, 600)
    art["difference-in-differences"] = document("Difference-in-differences: two groups and two periods", "Illustrative outcome means aligned to the lesson example: treated 50→56, comparison 48→51. The open dashed endpoint is the treated group's unobserved post-period outcome without treatment (53); the observed treated–counterfactual gap is 3 units and equals the difference in group changes only under parallel trends.", s, height=326)

    # RD.
    s = text(26, 28, "Compare outcomes locally on either side of the assignment cutoff", 15, NAVY, 700)
    s += line(88, 196, 710, 196, MUTED, 1.5) + line(88, 196, 88, 62, MUTED, 1.5)
    for value,y in [(0,196),(10,129),(20,62)]: s+=line(88,y,710,y,GRID,1)+line(83,y,88,y,MUTED,1)+text(78,y+3,str(value),8,MUTED,500,"end")
    s += text(395, 224, "Assignment score (illustrative units; cutoff = 0)", 9, MUTED, 500, "middle")
    s += '<text x="32" y="129" transform="rotate(-90 32 129)" fill="{0}" font-family="Arial, sans-serif" font-size="9" font-weight="500" text-anchor="middle">Outcome (illustrative units)</text>'.format(MUTED)
    for value, x in [(-8, 120), (-4, 260), (0, 400), (4, 540), (8, 680)]: s += line(x, 196, x, 201, MUTED, 1) + text(x, 213, str(value), 8, MUTED, 500, "middle")
    s += text(400, 239, "Mint outline = local fitting window · observations are simulated", 8, MUTED, 500, "middle")
    s += line(400, 62, 400, 196, GOLD, 2, "6 5") + text(407, 72, "Cutoff", 9, GOLD, 700)
    left=[]; right=[]
    for i in range(12):
        x=112+i*23; y=156-i*3 + [0,5,-4,3,-2,6,-1,2,-5,4,-2,1][i]
        left.append((x,y)); s+=circle(x,y,3.5,BLUE)
    for i in range(12):
        x=424+i*22; y=123-(x-424)*.13 + [3,-4,5,-2,1,-5,3,-1,4,-4,2,0][i]
        right.append((x,y)); s+=circle(x,y,3.5,CORAL)
    s+=poly([left[0],left[-1]],BLUE,3)+poly([right[0],right[-1]],CORAL,3)
    s+=rect(309,77,181,109,"none",MINT,8,1.5).replace(' fill="none"',' fill="none"')
    s+=text(182, 49, "Below cutoff", 9, BLUE, 700, "middle") + text(615, 49, "Above cutoff", 9, CORAL, 700, "middle")
    s+=text(26, 266, "A jump is not automatically causal; RD needs continuity and no precise manipulation.", 9, MUTED, 500)
    art["regression-discontinuity"] = document("Regression discontinuity at a policy threshold", "Illustrative observations and local fitted trends show outcomes just below and above a cutoff. The jump is a local contrast; causal interpretation requires continuity and no precise manipulation.", s, height=300)

    # Panel.
    s=text(26,30,"A panel observes the same units in repeated periods",15,NAVY,700)
    s+=text(110,68,"Unit",10,MUTED,700,"middle")
    for j,x in enumerate([218,372,526,680]): s+=text(x,68,f"t{j+1}",10,MUTED,700,"middle")
    for i,y in enumerate([101,143,185]):
        s+=text(110,y+4,f"i{i+1}",10,MUTED,600,"middle")
        for j,x in enumerate([218,372,526,680]):
            fill = "#fff7e6" if j==3 else WHITE
            s+=rect(x-38,y-14,76,28,fill,GRID,8,1)
            s+=text(x,y+4,["Observed","Observed","Observed","Post-shock"][j],8,MUTED,500,"middle")
    s+=line(218,211,526,211,CORAL,2,marker=True)+text(372,229,"Within-unit change",9,CORAL,700,"middle")
    s+=line(680,82,680,201,GOLD,1.7,"5 4")+text(680,82,"Common time shock",9,GOLD,700,"middle")
    art["panel-fixed-effects"] = document("Panel data and fixed effects", "Repeated observations allow within-unit comparisons; fixed effects absorb stable unit differences, not all changing confounders.", s)

    # Cluster inference.
    s=text(26,30,"Units assigned together may share shocks",15,NAVY,700)
    s+=text(26,58,"Policy assigned at district level",10,MUTED,500)
    for k,x in enumerate([120,280,440,600]):
        col=[BLUE,CORAL,MINT,GOLD][k]
        s+=rect(x-55,82,110,110,WHITE,col,14,2)+text(x,75,f"District {k+1}",10,col,700,"middle")
        for i in range(6):
            xx=x-30+(i%3)*30; yy=112+(i//3)*35
            s+=circle(xx,yy,8,col,"#ffffff",1.5)
    s+=line(60,210,700,210,NAVY,2)+text(380,224,"Assignment and shared dependence may be clustered—not each row",9,NAVY,700,"middle")
    s+=text(380,246,"Few clusters need appropriate small-sample or design-based inference",9,MUTED,500,"middle")
    art["robust-clustered-inference"] = document("Clustered outcomes and policy assignment", "Illustrative individual observations grouped within districts. Assignment and shared dependence can operate at cluster level; the number of clusters matters for uncertainty.", s, height=272)

    # Matching balance plot.
    s=text(26,30,"Matching aims to reduce measured covariate imbalance",15,NAVY,700)
    s+=line(396,65,396,205,MUTED,1.5,"5 5")+text(396,60,"Zero standardized difference",9,MUTED,700,"middle")
    names=["Prior income","Age","Education","Baseline health","Region"]
    before=[-125,92,-78,142,-45]; after=[-28,21,-17,33,-12]
    for value in (-1.5, -1, -.5, 0, .5, 1, 1.5):
        x = 396 + value * 105
        s += line(x, 204, x, 209, MUTED, 1) + text(x, 220, f"{value:g}", 8, MUTED, 500, "middle")
    for i,name in enumerate(names):
        y=88+i*27;s+=text(34,y+4,name,10,MUTED,500)
        x1=396+before[i];x2=396+after[i]
        s+=line(min(x1,x2),y,max(x1,x2),y,GRID,1)
        s+=circle(x1,y,4.5,CORAL)+circle(x2,y,4.5,MINT)
    s+=circle(430,239,4,CORAL)+text(440,243,"Before match/weight",8,CORAL,600)+circle(590,239,4,MINT)+text(600,243,"After match/weight",8,MINT,600)
    s+=line(238,204,554,204,MUTED,1)+text(396,263,"Standardized mean difference (SD units)",9,MUTED,600,"middle")
    art["matching-weighting"] = document("Covariate balance before and after matching", "Schematic signed standardized mean differences show measured covariates closer to zero after matching or weighting; the horizontal axis is in standard-deviation units. Unmeasured confounding can remain.", s, height=294)

    # Synthetic control.
    s=text(26,28,"A weighted donor group can provide a comparison for one treated case",15,NAVY,700)
    s+=line(72,194,710,194,MUTED,1.5)+line(72,194,72,61,MUTED,1.5)
    for value,y in [(0,194),(5,127.5),(10,61)]: s+=line(72,y,710,y,GRID,1)+line(68,y,72,y,MUTED,1)+text(62,y+3,str(value),8,MUTED,500,"end")
    s+=text(390,220,"Time (periods)",10,MUTED,500,"middle")
    s+='<text x="24" y="127" transform="rotate(-90 24 127)" fill="{0}" font-family="Arial, sans-serif" font-size="8" font-weight="500" text-anchor="middle">Outcome (illustrative units)</text>'.format(MUTED)
    s+=line(92,51,114,51,CORAL,3)+text(120,55,"Treated (observed)",9,CORAL,600)+line(290,51,312,51,BLUE,3)+text(318,55,"Synthetic control (weighted donors)",9,BLUE,600)
    s+=text(286,75,"PRE-INTERVENTION",9,MUTED,700,"middle")+text(593,75,"POST-INTERVENTION",9,MUTED,700,"middle")
    for value, x in [(0, 95), (2, 245), (4, 395), (6, 545), (8, 695)]: s += line(x, 194, x, 199, MUTED, 1) + text(x, 211, str(value), 8, MUTED, 500, "middle")
    s += text(390, 239, "Simulated series · post-policy gap is descriptive", 8, MUTED, 500, "middle")
    xs=[95,170,245,320,395,470,545,620,695]
    treated=[]; synth=[]
    for i,x in enumerate(xs):
        base=154-i*8
        synth.append((x,base+[0,3,-2,2,-1,1,0,-1,1][i]))
        treated.append((x,base+[1,-2,1,-1,1,2,-14,-25,-28][i]))
    s+=poly(synth,BLUE,3)+poly(treated,CORAL,3)
    for x,y in synth:s+=circle(x,y,3.5,BLUE)
    for x,y in treated:s+=circle(x,y,3.5,CORAL)
    s+=line(505,62,505,194,GOLD,2,"6 5")+text(510,94,"Intervention",9,GOLD,700)
    s+=text(26,263,"Post-intervention gap is descriptive; it is not automatically causal.",9,MUTED,500)
    art["synthetic-control"] = document("Synthetic control comparison", "The observed treated outcome is compared with a weighted synthetic control built from donor units. The horizontal axis is time in periods and the vertical axis is illustrative outcome units; the gap is descriptive, not automatically causal.", s, height=294)

    # Limited outcomes.
    s=text(26,30,"Match the model to the outcome’s possible values",15,NAVY,700)
    s+=rect(42,68,315,133,WHITE,GRID,14,1)+rect(403,68,315,133,WHITE,GRID,14,1)
    s+=text(60,91,"Binary outcome Y ∈ {0,1}",11,NAVY,700)+text(420,91,"Count outcome",11,NAVY,700)
    s+=line(66,176,334,176,MUTED,1)+line(66,176,66,107,MUTED,1)
    s+='<text x="48" y="142" transform="rotate(-90 48 142)" fill="{0}" font-family="Arial, sans-serif" font-size="8" text-anchor="middle">Predicted probability</text>'.format(MUTED)
    for value,y in [(0,176),(.5,143),(1,110)]: s+=line(62,y,66,y,MUTED,1)+text(59,y+3,f"{value:g}",7,MUTED,500,"end")
    for value,x in [(-4,70),(0,196),(4,322)]: s+=line(x,176,x,181,MUTED,1)+text(x,193,str(value),7,MUTED,500,"middle")
    s+=text(196,211,"Predictor index (illustrative units)",8,MUTED,500,"middle")
    pts=[]
    for i in range(37):
        x=70+i*7; z=(i-18)/4; prob=1/(1+math.exp(-z)); y=170-prob*55;pts.append((x,int(y)))
    s+=poly(pts,CORAL,3)+text(195,235,"Logit probability stays in [0, 1]",8,MUTED,500,"middle")
    s+=line(425,176,695,176,MUTED,1)+text(560,105,"Illustrative frequency",8,MUTED,500,"middle")
    for i,h in enumerate([22,39,62,51,31,18,9]):
        x=444+i*34;s+=f'<rect x="{x}" y="{176-h}" width="22" height="{h}" rx="3" fill="{BLUE}" opacity=".86"/>'
    for i in range(7): s+=text(455+i*34,190,str(i),7,MUTED,500,"middle")
    s+=text(560,211,"Count outcome value",8,MUTED,500,"middle")
    s+=text(560,235,"Illustrative count frequencies",8,MUTED,500,"middle")
    art["limited-outcomes"] = document("Binary and count outcomes", "An illustrative logistic probability curve shows probabilities between zero and one against a predictor index with labeled ticks; a separate schematic frequency distribution shows discrete count outcomes 0 through 6.", s, height=272)

    # Missingness / selection.
    s=text(26,30,"Follow every assigned unit through outcome measurement",15,NAVY,700)
    s+=rect(42,88,150,66,"#edf2fa",BLUE)+text(117,116,"Assigned sample",12,NAVY,700,"middle")+text(117,136,"keep denominator",9,MUTED,500,"middle")
    s+=line(192,121,224,121,MUTED,2)+line(224,84,224,167,MUTED,2)+circle(224,121,3,MUTED)
    s+=rect(258,54,174,60,"#edf7f2",MINT)+text(345,80,"Outcome observed",11,NAVY,700,"middle")+text(345,99,"include in analysis",9,MUTED,500,"middle")
    s+=rect(258,137,174,60,"#fff2ed",CORAL)+text(345,163,"Follow-up missing",11,NAVY,700,"middle")+text(345,182,"why did loss occur?",9,MUTED,500,"middle")
    s+=line(224,84,258,84,MINT,2,marker=True)+line(224,167,258,167,CORAL,2,marker=True)
    s+=rect(506,52,210,64,WHITE,BLUE)+text(611,79,"Observed-data model",11,NAVY,700,"middle")+text(611,98,"MAR / weighting or imputation",9,MUTED,500,"middle")
    s+=rect(506,137,210,64,WHITE,GOLD)+text(611,164,"Sensitivity analysis",11,NAVY,700,"middle")+text(611,183,"plausible unseen outcomes",9,MUTED,500,"middle")
    s+=text(380,224,"MAR / MNAR assumptions cannot be verified from observed outcomes alone",9,MUTED,500,"middle")
    art["selection-missing-data"] = document("Selection and missing outcomes flow", "All assigned units branch to observed or missing outcomes. Models, weighting, or imputation require assumptions; sensitivity analysis considers plausible unseen outcomes.", s)

    # Heterogeneity forest plot.
    s=text(26,28,"Average effects can differ across pre-specified groups",15,NAVY,700)
    x0,x1=300,700
    s+=line(500,66,500,196,MUTED,1.5,"5 5")+text(500,60,"Zero effect",9,MUTED,700,"middle")
    for i,(name,lo,mid,hi,col) in enumerate([("Group A",385,445,500,BLUE),("Group B",420,510,590,MINT),("Group C",515,602,685,CORAL)]):
        y=95+i*42;s+=text(32,y+4,name,11,NAVY,600)
        s+=line(lo,y,hi,y,col,3)+line(lo,y-5,lo,y+5,col,1.5)+line(hi,y-5,hi,y+5,col,1.5)+circle(mid,y,6,col,WHITE,2)
    for value,x in [(-3,300),(-1.5,400),(0,500),(1.5,600),(3,700)]: s+=line(x,207,x,212,MUTED,1)+text(x,222,f"{value:g}",8,MUTED,500,"middle")
    s+=line(x0,207,x1,207,GRID,1)+text(500,240,"Effect estimate (illustrative outcome units)",9,MUTED,600,"middle")
    s+=text(380,264,"Point = estimate · bar = interval · subgroup contrast needs a direct test",8,MUTED,500,"middle")
    art["heterogeneous-effects"] = document("Heterogeneous effects forest plot", "Illustrative subgroup effect estimates and intervals are plotted in outcome units around a labeled zero-effect reference. Group differences require a direct contrast, not separate significance or interval overlap.", s, height=294)

    # Specification.
    s=text(26,28,"Use plots to question functional form and residual patterns",15,NAVY,700)
    s+=line(66,191,360,191,MUTED,1)+line(66,191,66,64,MUTED,1)+line(412,191,706,191,MUTED,1)+line(412,191,412,64,MUTED,1)
    s+='<text x="48" y="128" transform="rotate(-90 48 128)" fill="{0}" font-family="Arial, sans-serif" font-size="9" font-weight="500" text-anchor="middle">Outcome (units)</text>'.format(MUTED)
    s+='<text x="396" y="128" transform="rotate(-90 396 128)" fill="{0}" font-family="Arial, sans-serif" font-size="9" font-weight="500" text-anchor="middle">Residual (units)</text>'.format(MUTED)
    xs=[78+i*7 for i in range(39)]
    linear=[(x,150-(x-212)*.24) for x in xs]
    curve=[(x,145+((x-212)/90)**2*18) for x in xs]
    s+=poly(linear,BLUE,2.5)+poly(curve,CORAL,2.5)
    s+=text(95,70,"Outcome vs predictor",9,NAVY,700)+text(300,84,"Linear",9,BLUE,700)+text(300,98,"Curved",9,CORAL,700)
    for i in range(15):
        x=424+i*19;y=122+[0,12,-8,20,-13,8,-19,13,-5,18,-12,6,-16,10,-3][i]
        s+=circle(x,y,3.5,BLUE)
    s+=line(420,122,704,122,MUTED,1,"5 4")+text(558,75,"Residuals should not show a strong pattern",9,MUTED,500,"middle")+text(425,117,"0",8,MUTED,500)
    s+=text(212,229,"Predictor X (illustrative units)",8,MUTED,500,"middle")+text(558,229,"Fitted value (illustrative units)",8,MUTED,500,"middle")
    art["functional-form-specification"] = document("Functional form and residual checks", "An illustrative outcome-versus-predictor panel compares linear and curved fits; a residual-versus-fitted panel shows residual units about a zero reference.", s, height=272)

    # Macro time series forecast.
    s=text(26,28,"Forecast only with information available at each date",15,NAVY,700)
    s+=line(66,195,710,195,MUTED,1.5)+line(66,195,66,60,MUTED,1.5)
    for value,y in [(0,195),(10,127.5),(20,60)]: s+=line(66,y,710,y,GRID,1)+line(62,y,66,y,MUTED,1)+text(57,y+3,str(value),8,MUTED,500,"end")
    s+=text(390,230,"Time (periods)",10,MUTED,500,"middle")
    s+='<text x="24" y="127" transform="rotate(-90 24 127)" fill="{0}" font-family="Arial, sans-serif" font-size="8" font-weight="500" text-anchor="middle">Series value (illustrative units)</text>'.format(MUTED)
    for value,x in [(0,82),(4,218),(8,354),(12,490),(16,657)]: s+=line(x,195,x,200,MUTED,1)+text(x,213,str(value),8,MUTED,500,"middle")
    obs=[]
    for i in range(13):
        x=82+i*34;y=155-i*4+[0,8,-6,10,-7,4,-10,8,-3,6,-7,5,0][i]
        obs.append((x,y))
    s+=poly(obs,BLUE,3)
    for x,y in obs:s+=circle(x,y,3.5,BLUE)
    s+=line(512,61,512,196,GOLD,2,"6 5")+text(516,70,"Forecast origin",9,GOLD,700)
    center=[obs[-1][1]+4,obs[-1][1]+8,obs[-1][1]+11,obs[-1][1]+13]
    fpts=[(528+i*43,center[i]) for i in range(4)]
    band=[(x,y-12-i*3) for i,(x,y) in enumerate(fpts)] + [(x,y+12+i*3) for i,(x,y) in reversed(list(enumerate(fpts)))]
    s+=poly(band,GRID,1,fill="#dce9f7")+poly(fpts,CORAL,3)
    for x,y in fpts:s+=circle(x,y,3.5,CORAL)
    s+=text(621,80,"Forecast interval",9,CORAL,700,"middle")
    s+=text(390,250,"Observed history",8,BLUE,700,"middle")+text(615,250,"Forecast mean + widening uncertainty band",8,CORAL,700,"middle")
    art["applied-macro-time-series"] = document("Macroeconomic series and forecast horizon", "A simulated observed series in illustrative units ends at a forecast origin; future mean predictions and a widening uncertainty band are displayed over time in periods.", s, height=280)

    # Original teaching schematic; inspired by NIST's replicate trace + histogram and Penn State's empirical-population workflow.
    s=text(26,30,"From an observed sample to an estimated sampling distribution",15,NAVY,700)
    s+=rect(28,76,130,88,"#edf2fa",BLUE)+text(93,103,"1 · Observed",11,NAVY,700,"middle")+text(93,124,"sample of n",9,MUTED,500,"middle")+text(93,144,"compute T",10,BLUE,600,"middle")
    s+=line(158,120,177,120,MUTED,2,marker=True)
    s+=rect(184,76,140,88,"#fff7e6",GOLD)+text(254,103,"2 · Empirical",10,NAVY,700,"middle")+text(254,122,"distribution",10,NAVY,700,"middle")+text(254,144,"sample stands in",9,MUTED,500,"middle")
    s+=line(324,120,340,120,MUTED,2,marker=True)
    s+=rect(347,76,158,88,"#eef7f2",MINT)+text(426,101,"3 · Resample",11,NAVY,700,"middle")+text(426,122,"n with replacement",9,MUTED,500,"middle")+text(426,143,"recompute T* · repeat B",8,MINT,600,"middle")
    s+=line(505,120,521,120,MUTED,2,marker=True)
    s+=rect(528,59,200,145,"#fff2ed",CORAL)+text(628,78,"4 · Inspect replicates",10,NAVY,700,"middle")
    s+=text(628,98,"T* by resample number",8,MUTED,500,"middle")
    trace=[(542+i*19,112+[-5,1,-2,6,-3,2,0,-6,4,1][i]) for i in range(10)]
    s+=poly(trace,BLUE,1.6)
    s+=text(628,140,"Histogram of T*",8,MUTED,500,"middle")
    for i,h in enumerate([9,16,23,31,36,31,24,17,10]):
        x=548+i*18;y=184-h
        s+=f'<rect x="{x}" y="{y}" width="11" height="{h}" rx="2" fill="{[BLUE,BLUE,MINT,CORAL,CORAL,CORAL,MINT,BLUE,BLUE][i]}" opacity=".9"/>'
    s+=line(598,146,598,186,GOLD,1.5,"4 3")+line(680,146,680,186,GOLD,1.5,"4 3")
    s+=text(30,230,"Trace: replicate stability  ·  Histogram: shape and tails  ·  resample clusters or time blocks when required",9,NAVY,600)
    s+=text(30,253,"These are simulated reuses of observed data, not new population observations.",9,MUTED,500)
    art["bootstrap-inference"] = document("Bootstrap resampling, replicate trace and distribution", "An original four-step schematic shows the observed sample standing in for the population, repeated samples of size n drawn with replacement, and recomputed statistics. A replicate trace supports Monte Carlo stability checks; a histogram shows distribution shape and approximate interval limits. Design-aware resampling is needed for dependent observations.", s, height=280)

    # Original two-panel teaching visual: overlapping null/alternative distributions and power versus n.
    s=text(26,28,"Effect size, variability and independent n shape detection",15,NAVY,700)
    s+=rect(38,49,174,55,"#edf2fa",BLUE)+text(125,71,"Choose meaningful δ",10,NAVY,700,"middle")+text(125,89,"outcome units",8,MUTED,500,"middle")
    s+=rect(293,49,174,55,"#fff7e6",GOLD)+text(380,71,"State σ and α",10,NAVY,700,"middle")+text(380,89,"plus assignment design",8,MUTED,500,"middle")
    s+=rect(548,49,174,55,"#eef7f2",MINT)+text(635,71,"Evaluate power",10,NAVY,700,"middle")+text(635,89,"P(reject H₀ | δ)",9,MINT,700,"middle")
    for x in [212,467]: s+=line(x,76,x+70,76,MUTED,2,marker=True)
    s+=rect(38,124,326,143,WHITE,GRID)+rect(386,124,336,143,WHITE,GRID)
    s+=text(201,142,"Overlapping null and alternative",9,NAVY,700,"middle")
    x0,x1,y0=62,347,248
    critical_z=2.0
    critical_x=x0+(critical_z+3)/7.2*(x1-x0)
    s+=line(x0,y0,x1,y0,MUTED,1)
    h0=[];h1=[]
    for i in range(61):
        z=-3+i*.12;x=x0+(z+3)/7.2*(x1-x0)
        h0.append((x,y0-46*math.exp(-.5*z*z)))
        h1.append((x,y0-46*math.exp(-.5*(z-1.35)**2)))
    power_tail=[(critical_x,y0)]
    for i in range(61):
        z=-3+i*.12
        if z>=critical_z:
            x=x0+(z+3)/7.2*(x1-x0)
            power_tail.append((x,y0-46*math.exp(-.5*(z-1.35)**2)))
    power_tail.append((x1,y0))
    s+=poly(power_tail,MINT,0,fill="#d9f0e4")
    s+=line(x0,y0,x1,y0,MUTED,1)+poly(h0,BLUE,2)+poly(h1,CORAL,2.5)
    s+=line(critical_x,156,critical_x,y0,GOLD,1.5,"5 4")
    s+=text(146,169,"H₀",8,BLUE,700,"middle")+text(254,169,"specified H₁",8,CORAL,700,"middle")
    s+=text(critical_x,184,"right-tail cutoff",7,GOLD,600,"middle")+text(309,197,"power under H₁",7,MINT,700,"middle")
    s+=text(201,263,"A chosen alternative, not a probability H₁ is true",7,MUTED,500,"middle")
    s+=text(554,142,"Power across independent n",9,NAVY,700,"middle")
    gx0,gx1,gy0,gy1=410,698,246,163
    s+=line(gx0,gy0,gx1,gy0,MUTED,1)+line(gx0,gy1,gx0,gy0,MUTED,1)+line(gx0,gy1+16,gx1,gy1+16,GOLD,1.5,"5 4")
    s+=text(690,gy1+12,"chosen target",7,GOLD,600,"end")+text(554,262,"More information can raise power · schematic",8,MUTED,500,"middle")
    pts=[]
    for i in range(31):
        z=i/30;x=gx0+z*(gx1-gx0);y=gy0-74*(1-math.exp(-3*z));pts.append((x,y))
    s+=poly(pts,MINT,2.5)+text(416,156,"Power",7,MUTED,500)+text(695,257,"n →",8,NAVY,600,"end")
    s+=text(38,286,"Precision plans target interval width; power plans target detection under stated assumptions.",9,NAVY,600)
    art["statistical-power-planning"] = document("Statistical power, overlapping distributions and sample-size planning", "An original two-panel illustration contrasts the null and a specified alternative distribution around a rejection cutoff. The shaded right tail under H₁ beyond the cutoff represents power for that specified alternative; power depends on the effect, variability and design. A separate power-versus-independent-sample-size curve is schematic. Precision planning is a distinct target and neither calculation guarantees a result.", s, height=302)

    # Measurement error: distinguish a latent quantity, noisy observed proxy and the conditional attenuation result.
    s=text(26,30,"Separate the economic concept from its recorded proxy",15,NAVY,700)
    s+=rect(37,76,176,65,"#edf2fa",BLUE)+text(125,103,"Latent quantity X",12,NAVY,700,"middle")+text(125,123,"true but not fully observed",9,MUTED,500,"middle")
    s+=rect(292,76,176,65,"#fff2ed",CORAL)+text(380,103,"Recorded X*",12,NAVY,700,"middle")+text(380,123,"X* = X + measurement error u",9,MUTED,500,"middle")
    s+=line(213,108,292,108,GOLD,2,marker=True)+text(252,91,"add u",8,GOLD,700,"middle")
    s+=rect(547,76,176,65,"#eef7f2",MINT)+text(635,103,"Outcome Y",12,NAVY,700,"middle")+text(635,123,"economic outcome",9,MUTED,500,"middle")
    s+=line(468,108,547,108,MUTED,2,marker=True)
    s+=rect(48,171,318,96,WHITE,GRID)+rect(394,171,318,96,WHITE,GRID)
    s+=text(207,190,"True X vs Y",10,NAVY,700,"middle")+text(553,190,"Noisy X* vs Y",10,NAVY,700,"middle")
    for i,(x,y) in enumerate([(92,246),(130,235),(168,224),(206,211),(244,196),(282,184)]): s+=circle(x,y,3.5,BLUE)
    s+=line(88,250,291,177,BLUE,2.5)
    for i,(x,y) in enumerate([(428,243),(462,249),(490,222),(520,231),(548,203),(580,215),(612,181),(654,194)]): s+=circle(x,y,3.5,CORAL)
    s+=line(423,246,659,195,CORAL,2.5)+line(423,255,659,173,MINT,2,"5 4")
    s+=text(553,280,"Slope may flatten only under classical-error assumptions",9,MUTED,600,"middle")
    art["measurement-error-economics"] = document("Measurement error in an economic predictor", "The observed predictor equals the latent quantity plus measurement error. Side-by-side schematic relationships contrast a less steep observed association under a classical additive predictor-error model; attenuation is conditional on assumptions and is not universal.", s, height=300)

    # Price index: fixed basket weighted price changes and a compatible deflator.
    s=text(26,30,"A weighted basket turns item price relatives into an index",15,NAVY,700)
    rows=[("Food",.35,1.08,BLUE), ("Housing",.45,1.06,CORAL), ("Transport",.20,.98,MINT)]
    for i,(name,weight,relative,col) in enumerate(rows):
        y=76+i*49
        s+=rect(38,y,190,37,WHITE,GRID,8)+text(52,y+23,name,10,NAVY,600)+text(207,y+23,f"weight {weight:.0%}",9,MUTED,600,"end")
        s+=line(244,y+18,340,y+18,col,5)+circle(340+(relative-1)*270,y+18,5,col)
        s+=text(350,y+22,f"price relative {relative:.2f}",9,col,600)
    s+=line(505,83,505,213,GOLD,2)+text(505,72,"weighted basket",8,GOLD,600,"middle")
    s+=rect(545,94,180,66,"#edf2fa",BLUE)+text(635,120,"Price indexₜ",12,NAVY,700,"middle")+text(635,143,"base period = 100",9,MUTED,500,"middle")
    s+=line(635,160,635,190,MUTED,2,marker=True)
    s+=rect(545,195,180,58,"#eef7f2",MINT)+text(635,218,"Real value = nominal",10,NAVY,600,"middle")+text(635,237,"÷ (index / 100)",10,MINT,700,"middle")
    s+=text(38,263,"Index changes describe the stated basket; household experience and official methods may differ.",9,MUTED,500)
    art["price-indices-real-values"] = document("Price index and real-value conversion", "Illustrative category weights combine item price relatives into an index normalized to 100 in a base period. A compatible index can deflate a nominal amount. The schematic weights and relatives are examples, not official CPI data.", s, height=286)
    return art


modules = json.loads(DATA.read_text())
lab_map = {
    "research-design": "design", "experimental-design": "experiment", "iv-2sls": "iv",
    "difference-in-differences": "did", "regression-discontinuity": "rdd",
    "panel-fixed-effects": "panel", "robust-clustered-inference": "cluster",
    "matching-weighting": "matching", "synthetic-control": "synthetic",
    "limited-outcomes": "limited", "selection-missing-data": "missing",
    "heterogeneous-effects": "hetero", "functional-form-specification": "specification",
    "applied-macro-time-series": "macro", "bootstrap-inference": "bootstrap",
    "statistical-power-planning": "powerplan", "measurement-error-economics": "measurement",
    "price-indices-real-values": "priceindex",
}
alt = {
    "research-design": "Four linked stages define the population and treatment or outcome, identify the counterfactual through a comparison design, then state the estimand and assumptions or checks.",
    "experimental-design": "Eligible units are randomly assigned to offer or comparison groups; outcomes are compared by original assignment, with no causal link between the groups.",
    "iv-2sls": "A causal diagram shows an instrument affecting treatment, treatment affecting outcome, and a common cause of treatment and outcome. Relevance, independence, and exclusion are assumptions; exclusion rules out a direct instrument-to-outcome path.",
    "difference-in-differences": "Two periods (Pre and Post) on a mean-outcome scale in illustrative units. Observed means are treated 50 and 56 and comparison 48 and 51; the open dashed treated-post value 53 is the unobserved no-treatment counterfactual. The displayed difference in changes is (56−50)−(51−48)=3 units under parallel trends.",
    "regression-discontinuity": "Illustrative outcomes just below and above a cutoff show local fitted trends and a jump. A causal local interpretation requires continuity and no precise manipulation.",
    "panel-fixed-effects": "A repeated-observation grid highlights within-unit changes; the final period is highlighted for every unit to show a common time shock, not a treatment group.",
    "robust-clustered-inference": "Individual observations are grouped inside districts to show how assignment or shared dependence can cluster; the number of clusters matters for uncertainty.",
    "matching-weighting": "A schematic covariate balance plot shows signed standardized differences closer to zero after matching or weighting; unmeasured confounding can remain.",
    "synthetic-control": "Observed treated outcomes and a weighted synthetic control are compared before and after intervention; the post-event gap is descriptive, not automatically causal.",
    "limited-outcomes": "Observed binary outcomes take values 0 or 1 while their predicted probabilities stay in [0,1]; a separate schematic shows nonnegative integer count support.",
    "selection-missing-data": "Assigned participants branch to observed and missing outcomes; modeling, weighting, or imputation requires assumptions, and sensitivity analysis considers unseen outcomes.",
    "heterogeneous-effects": "An illustrative forest plot compares subgroup effect estimates and intervals around zero; group differences require a direct contrast, not separate significance tests.",
    "functional-form-specification": "An outcome-versus-predictor panel compares linear and curved fits; a residual-versus-fitted panel shows a zero reference and a pattern-free schematic cloud.",
    "applied-macro-time-series": "A time series ends at a forecast origin and continues as predictions with a widening uncertainty band.",
    "bootstrap-inference": "An observed sample is resampled with replacement, the statistic is recomputed, and the empirical distribution summarizes approximate sampling variation; dependent designs require a matching resampling unit.",
    "statistical-power-planning": "The shaded right tail under the specified alternative H₁ beyond the rejection cutoff represents power for that particular effect and design. The separate power-versus-independent-sample-size curve is schematic; power depends on the specified effect, variability and design assumptions.",
    "measurement-error-economics": "Observed X* equals latent X plus error u. The side-by-side schematic shows a potentially attenuated association only under classical additive predictor-error assumptions.",
    "price-indices-real-values": "Illustrative category weights combine price relatives into an index normalized to 100, which can deflate a nominal value using a compatible base; examples are not official CPI data.",
}
caption = "Original teaching schematic; shapes and paths are explanatory illustrations, not measured economic data."
caption_by_id = {
    "difference-in-differences": "Pre and Post mean outcomes (illustrative units): observed treated 50→56 and comparison 48→51. The open dashed treated-post value 53 is unobserved; (56−50)−(51−48)=3 units under parallel trends."
}
art = build_svgs()
for module in modules:
    key = module["id"]
    if key not in art:
        continue
    (OUT / f"{key}.svg").write_text(art[key] + "\n")
    module["lab"] = lab_map[key]
    module["diagram"] = f"/diagrams/{key}.svg"
    module["diagramAlt"] = alt[key]
    module["diagramCaption"] = caption_by_id.get(key, caption)
DATA.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Generated {len(art)} original SVG diagrams and linked them to the module bundle.")
