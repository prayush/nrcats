import re

original_paper = r"""% ****** Start of file apssamp.tex ******
%
%   This file is part of the APS files in the REVTeX 4.2 distribution.
%   Version 4.2a of REVTeX, December 2014
%
%   Copyright (c) 2014 The American Physical Society.
%
%   See the REVTeX 4 README file for restrictions and more information.
%
% TeX'ing this file requires that you have AMS-LaTeX 2.0 installed
% as well as the rest of the prerequisites for REVTeX 4.2
%
% See the REVTeX 4 README file
% It also requires running BibTeX. The commands are as follows:
%
%  1)  latex apssamp.tex
%  2)  bibtex apssamp
%  3)  latex apssamp.tex
%  4)  latex apssamp.tex
%
\documentclass[%
 reprint,
%superscriptaddress,
%groupedaddress,
%unsortedaddress,
%runinaddress,
%frontmatterverbose, 
%preprint,
%preprintnumbers,
%nofootinbib,
%nobibnotes,
%bibnotes,
 amsmath,amssymb,
 aps,
 % onecolumn,
%pra,
%prb,
%rmp,
%prstab,
%prstper,
%floatfix,
]{revtex4-2}

% \usepackage{caption}
% \captionsetup{justification=justified, singlelinecheck=false}
\usepackage{graphicx}% Include figure files
\usepackage{dcolumn}% Align table columns on decimal point
\usepackage{bm}% bold math
%\usepackage{hyperref}% add hypertext capabilities
%\usepackage[mathlines]{lineno}% Enable numbering of text and display math
%\linenumbers\relax % Commence numbering lines
\usepackage{xcolor}
\usepackage[normalem]{ulem} % for \sout{} in tracked edits

% --- Tracked-edits helpers (delete/insert/replace) ---
\newcommand{\del}[1]{\textcolor{red}{\sout{#1}}}
\newcommand{\add}[1]{\textcolor{blue}{#1}}
\newcommand{\repl}[2]{\del{#1}\add{#2}}

\usepackage{graphicx}% Include figure files
\usepackage{float}
\usepackage{hyperref}

\usepackage{mathtools}
\usepackage{mathrsfs} % for the nice curly letters for Lagrangian, Hamiltonian, etc
\usepackage[noabbrev, capitalise]{cleveref}
\usepackage{orcidlink}

% \usepackage{subcaption}
\usepackage{booktabs}
\usepackage{subfig}

\makeatletter
\long\def\@makecaption#1#2{%
  \par
  \begingroup
    \small
    \setlength{\parindent}{0pt}
    \leftskip=0pt
    \rightskip=0pt plus 2em
    \textbf{#1.} #2\par
  \endgroup}
\makeatother
%\usepackage[showframe,%Uncomment any one of the following lines to test 
%%scale=0.7, marginratio={1:1, 2:3}, ignoreall,% default settings
%%text={7in,10in},centering,
%%margin=1.5in,
%%total={6.5in,8.75in}, top=1.2in, left=0.9in, includefoot,
%%height=10in,a5paper,hmargin={3cm,0.8in},
%]{geometry}
\newcommand{\prayush}[1]{\textcolor{purple}{\small{\sf{[PK: #1]}}}}

\newcommand{\ICTS}{\affiliation{
    International Centre for Theoretical Sciences,
    Tata Institute of Fundamental Research, Bangalore 560089, India
}}

\newcommand{\IISC}{\affiliation{
    Department of Physics, Indian Institute of Science,
    Bangalore, 560012, Karnataka, India.
}}

\begin{document}

% \preprint{APS/123-QED}

\title{}

\author{Prayush Kumar\,\orcidlink{0000-0001-5523-4603}}\ICTS{}
 


\date{\today}% It is always \today, today,
             %  but any date may be explicitly specified

\begin{abstract}

  
\end{abstract}

%\keywords{Suggested keywords}%Use showkeys class option if keyword
                              %display desired
\maketitle

%\tableofcontents

\section{\label{sec:level1}Introduction}




\bibliography{References}% Produces the bibliography via BibTeX.

\end{document}
%
% ****** End of file apssamp.tex ******
"""

with open('/home/prayush/src/nr-catalog-tools/project/paper.tex', 'w') as f:
    f.write(original_paper)

with open('/home/prayush/src/nr-catalog-tools/project/paper_draft.md', 'r') as f:
    md = f.read()

# Basic replacements
tex = md
tex = re.sub(r'## (.*?)\n', r'\\section{\1}\n', tex)
tex = re.sub(r'### (.*?)\n', r'\\subsection{\1}\n', tex)
tex = re.sub(r'#### (.*?)\n', r'\\subsubsection{\1}\n', tex)
tex = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', tex)
# REMOVED: tex = re.sub(r'_(.*?)_', r'\\textit{\1}', tex)
# Replace *...* with \textit{...}
tex = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'\\textit{\1}', tex)

tex = re.sub(r'\$\$(.*?)\$\$', r'\\begin{equation}\1\\end{equation}', tex, flags=re.DOTALL)

def replace_fig(match):
    caption = match.group(1)
    filepath = match.group(2)
    label = match.group(3) if len(match.groups()) > 2 else ""
    return f"""\\begin{{figure}}[h!]
\\centering
\\includegraphics[width=\\columnwidth]{{{filepath}}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{figure}}"""

tex = re.sub(r'!\[(.*?)\]\((.*?)\)(?:\{#(.*?)\})?', replace_fig, tex)

def convert_table(match):
    lines = match.group(0).strip().split('\n')
    header = lines[0]
    aligns = lines[1]
    rows = lines[2:]
    
    col_count = len(header.split('|')) - 2
    tex_align = "c" * col_count
    
    out = ["\\begin{table}[h!]", "\\centering", f"\\begin{{tabular}}{{{tex_align}}}", "\\toprule"]
    
    def process_row(row):
        cells = [c.strip() for c in row.split('|')[1:-1]]
        return " & ".join(cells) + " \\\\"
        
    out.append(process_row(header))
    out.append("\\midrule")
    for row in rows:
        out.append(process_row(row))
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    out.append("\\end{table}")
    return "\n".join(out)

tex = re.sub(r'\|.*\|\n\|[-|]+\|\n(?:\|.*\|\n)+', convert_table, tex)

with open('/home/prayush/src/nr-catalog-tools/project/paper.tex', 'r') as f:
    paper = f.read()

title_match = re.search(r'# (.*?)\n', md)
title = title_match.group(1) if title_match else "Paper Title"

abstract_match = re.search(r'\\section{Abstract}\n(.*?)\n\n\\section', tex, flags=re.DOTALL)
abstract = abstract_match.group(1).strip() if abstract_match else ""

tex = re.sub(r'\\section{Abstract}\n.*?\n\n\\section', r'\\section', tex, flags=re.DOTALL)
tex = re.sub(r'# .*?\n', '', tex, count=1)
tex = re.sub(r'\\textbf{Prayush Kumar}.*?\n', '', tex)
tex = re.sub(r'_Draft — not for circulation_\n', '', tex)
tex = re.sub(r'---\n', '', tex)

paper = re.sub(r'\\title{.*?}', f'\\\\title{{{title}}}', paper, flags=re.DOTALL)
paper = re.sub(r'\\begin{abstract}.*?\\end{abstract}', f'\\\\begin{{abstract}}\n{abstract}\n\\\\end{{abstract}}', paper, flags=re.DOTALL)

body_start = paper.find('\\section{\\label{sec:level1}Introduction}')
if body_start != -1:
    body_end = paper.find('\\bibliography{References}')
    paper = paper[:body_start] + tex + '\n\n' + paper[body_end:]

with open('/home/prayush/src/nr-catalog-tools/project/paper.tex', 'w') as f:
    f.write(paper)

print("Successfully generated paper.tex")
