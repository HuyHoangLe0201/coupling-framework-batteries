r"""Assemble batt-main.tex (Wiley NJD v5, AMA, Times2COL) from the converted body.

Structure mapping:
  - `# Title`                            -> \title{}
  - `\textbf{Article type:} Perspective` -> \articletype{Perspective}
  - `\textbf{Keywords:} ...`             -> \keywords{...}
  - `## Abstract`                        -> \abstract[Abstract]{...}
  - `## N. Heading`                      -> \section{Heading}   (LaTeX numbers it)
  - back-matter `## X`                   -> \bmsection*{X}
  - `\textbf{Table 1.} ...`              -> table* with caption + tabular*
  - `\textbf{Figure 1.} ...`             -> figure* with \includegraphics + caption

The manuscript refers to (Figure 1c), (Figure 1d) and (Table 1); those become
\ref-based cross-references. The figure PDF and references.bib are copied into the
template folder so the submission is self-contained.
"""
import io
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
WILEY = os.path.join(HERE, "wiley-njd")


def _find_asset(rel_candidates, label):
    """Locate a companion asset in either layout.

    The working tree keeps the manuscript beside research/11-figures/ and
    research/04-literature/; the published repository renames those to figures/
    and code/lit-audit/. Hard-coding one of the two silently breaks the other, so
    both are tried and a miss is a loud error rather than a stale copy.
    """
    tried = []
    for rel in rel_candidates:
        p = os.path.normpath(os.path.join(HERE, rel))
        tried.append(p)
        if os.path.isfile(p):
            return p
    raise SystemExit(
        "could not locate {} in any of:\n  {}\n"
        "build the figures / restore the bibliography before assembling.".format(
            label, "\n  ".join(tried)))


FIGURE_SRC = _find_asset(
    [os.path.join("..", "11-figures", "figure-mechanism.pdf"),
     os.path.join("..", "figures", "figure-mechanism.pdf")],
    "figure-mechanism.pdf")
BIB_SRC = _find_asset(
    [os.path.join("..", "04-literature", "references.bib"),
     os.path.join("..", "code", "lit-audit", "references.bib")],
    "references.bib")

body = io.open(os.path.join(HERE, "_converted-body.tex"), encoding="utf-8").read()
lines = body.split("\n")

title = None
article_type = None
keywords = None
abstract = []
sections = []
backmatter = []
legend_table = None
legend_table2 = None
legend_figure = None

i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("# "):
        title = ln[2:].strip()
        i += 1
        continue
    if ln.startswith(r"\textbf{Article type:}"):
        article_type = re.sub(r"^\\textbf\{Article type:\}\s*", "", ln).strip().strip("{}")
        i += 1
        continue
    if ln.startswith(r"\textbf{Keywords:}"):
        keywords = re.sub(r"^\\textbf\{Keywords:\}\s*", "", ln).strip().strip("{}")
        i += 1
        continue
    m = re.match(r"^##\s+(.*)$", ln)
    if m:
        head = m.group(1).strip()
        i += 1
        block = []
        while i < len(lines) and not re.match(r"^##\s+", lines[i]):
            if lines[i].strip() != "---":
                block.append(lines[i])
            i += 1
        text = "\n".join(block).strip()
        low = head.lower()
        if low.startswith("abstract"):
            abstract.append(text)
        elif low.startswith("figure legends"):
            for item in re.split(
                    r"(?=^\s*\\textbf\{Table 1\.\}|^\s*\\textbf\{Table 2\.\}"
                    r"|^\s*\\textbf\{Figure 1\.\})",
                    text, flags=re.M):
                item = item.strip()
                if item.startswith(r"\textbf{Table 1.}"):
                    legend_table = item
                elif item.startswith(r"\textbf{Table 2.}"):
                    legend_table2 = item
                elif item.startswith(r"\textbf{Figure 1.}"):
                    legend_figure = item
        elif re.match(r"^\d+\.\s", head):
            sections.append((re.sub(r"^\d+\.\s*", "", head), text))
        else:
            backmatter.append((head, text))
        continue
    i += 1

assert title and article_type and keywords and abstract and legend_table and legend_table2 \
    and legend_figure, (title, article_type, keywords, abstract, legend_table,
                        legend_table2, legend_figure)

TITLE = "From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries"

for idx, (h, t) in enumerate(sections):
    t = t.replace("(Figure 1c)", r"(Figure~\ref{fig1}c)")
    t = t.replace("(Figure 1d)", r"(Figure~\ref{fig1}d)")
    t = t.replace("(Table 1)", r"(Table~\ref{tab1})")
    t = t.replace("(Table 2)", r"(Table~\ref{tab2})")
    sections[idx] = (h, t)

legend_table = re.sub(r"^\\textbf\{Table 1\.\}\s*", "", legend_table)
legend_table2 = re.sub(r"^\\textbf\{Table 2\.\}\s*", "", legend_table2)
legend_figure = re.sub(r"^\\textbf\{Figure 1\.\}\s*", "", legend_figure)
legend_figure = re.sub(r"\((\w)\) ", r"\\textbf{(\1)} ", legend_figure)

out = []
out.append(r"""\documentclass[AMA,Times2COL]{WileyNJDv5}

\articletype{Perspective}

\received{Date Month Year}
\revised{Date Month Year}
\accepted{Date Month Year}

\journal{Batteries \& Supercaps}
\volume{00}
\copyyear{2026}
\startpage{1}

\raggedbottom

\begin{document}

\title{%s}

\author[1]{Huy Hoang Le}

\author[2]{Kim-Anh Nguyen}

\authormark{LE and NGUYEN}
\titlemark{From Loss Accounting to Feedback Loops}

\address[1]{\orgdiv{R\&D Department}, \orgname{PowerMore Ltd.}, \orgaddress{\city{Da Nang 550000}, \country{Vietnam}}}

\address[2]{\orgdiv{Faculty of Electrical Engineering}, \orgname{University of Science and Technology, The University of Danang}, \orgaddress{\city{Da Nang 550000}, \country{Vietnam}}}

\corres{Corresponding author Kim-Anh Nguyen, Faculty of Electrical Engineering, University of Science and Technology, The University of Danang, Da Nang 550000, Vietnam. \email{nkanh@dut.udn.vn}\\ORCID: Kim-Anh Nguyen 0000-0003-3408-847X; Huy Hoang Le 0009-0009-2138-5468.}

\abstract[Abstract]{%s}

\keywords{%s}

\maketitle

""" % (TITLE, abstract[0].replace("\n", " "), keywords))

out.append(r"""
\begin{table*}[!t]
\begin{center}
\begin{minipage}{\textwidth}
\hrule\vspace{3pt}
\noindent\textbf{Box 1. Terms used in this Perspective.} \textbf{Knee.} The cycle at which fade stops being gradual and becomes abrupt. \textbf{Interphase.} The nanometer film where electrolyte meets electrode, through which lithium must pass. \textbf{Plating.} Lithium deposited as metal instead of entering the anode, which usually shortens life sharply. \textbf{LLI, LAM, KL.} Loss of lithium inventory, of active material, kinetic or polarization loss: the three channels through which capacity disappears. \textbf{C-rate.} How fast a cell is charged or discharged relative to its capacity; 1\,C empties it in one hour. \textbf{Margin.} The gap between a loop's operating value and the threshold where it runs away.
\vspace{3pt}\hrule
\end{minipage}
\end{center}
\end{table*}
""")

for head, text in sections:
    tag = head.split(":")[0].strip().replace(" ", "")
    out.append("\\section{%s}\\label{sec:%s}" % (head, tag))
    if head.startswith("Six falsifiable"):
        # Declared immediately after the heading, not after the paragraph, so the
        # float lands on the page where Table 2 is first cited. Declared at the end
        # of §7 it was pushed past the start of the reference list (page 7).
        out.append(r"""
\begin{table*}[t]
\caption{%s}
\label{tab2}
\small
\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{0.17\textwidth}@{}}
\toprule
 & Prediction & Refuted if & Data status\\
\midrule
P1 (Loop C) & Identical chemistry at different stack pressure shows knees at different cycle counts & the knees coincide & already published\\
P2 (Loop A) & Anode-free and graphite cells at matched inventory-loss rate show different efficiency curvature & the curvatures coincide & new experiment\\
P3 (Loop B) & Suppressing dissolution moves the slope of inventory loss, not its intercept & only the intercept moves & re-analysis\\
P4 (Loop D) & At fixed total additive mass, electrolyte loading in g~Ah$^{-1}$ predicts life & life is invariant & re-analysis\\
P5 (Loop C) & Single-crystal and polycrystalline material differ in knee sharpness, not initial fade rate & fade rates differ while knee shape does not & already published\\
P6 (all loops) & Retention is concave over a pre-registered window no narrower than 90\%% & a majority of cells are convex over that window & checked here (SI S1.15)\\
\bottomrule
\end{tabularx}
\end{table*}
""" % legend_table2)
    out.append(text)
    out.append("")
    if head.startswith("Loss accounting"):
        out.append(r"""
\begin{table*}[t]
\caption{%s}
\label{tab1}
\begin{tabular*}{\textwidth}{@{\extracolsep\fill}lll@{}}
\toprule
Mechanism & First channel to move & Time law\\
\midrule
M1 interphase growth & LLI & steady accumulation; anode impedance grows while LAM stays flat\\
M2 lithium plating & LLI & accelerating; voltage hysteresis grows\\
M3 metal dissolution & LAM and LLI together & the two rise in step; Mn detected on the anode\\
M4 particle fracture & LAM, then LLI & stepwise; responds to stack pressure, not to the voltage window\\
\bottomrule
\end{tabular*}
\end{table*}
""" % legend_table)
    if head.startswith("Introduction"):
        out.append(r"""
""")
        out.append(r"""
\begin{figure*}[t]
\centerline{\includegraphics[width=\textwidth]{figure-mechanism}}
\caption{%s}
\label{fig1}
\end{figure*}
""" % legend_figure)

bm_map = {
    "Conflict of interest": "Conflict of interest",
    "Data availability statement": "Data availability statement",
    "Acknowledgements and funding": "Acknowledgements and funding",
}
for head, text in backmatter:
    if head in bm_map:
        out.append("\\bmsection*{%s}" % bm_map[head])
        out.append(text)
        out.append("")

out.append("\\bibliography{references}")
out.append("")
out.append("\\end{document}")

tex = "\n".join(out) + "\n"
io.open(os.path.join(WILEY, "batt-main.tex"), "w", encoding="utf-8", newline="\n").write(tex)
print("wrote batt-main.tex (%d chars)" % len(tex))

shutil.copy2(FIGURE_SRC, os.path.join(WILEY, "figure-mechanism.pdf"))
shutil.copy2(BIB_SRC, os.path.join(WILEY, "references.bib"))
print("copied figure-mechanism.pdf and references.bib into the template folder")
