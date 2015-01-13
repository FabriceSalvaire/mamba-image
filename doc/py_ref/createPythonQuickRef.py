# Python API quick reference generating script
#
# This script generates the python API quick reference for the Mamba library
# It produces a tex file which is then compiled by pdflatex to produce a PDF
# document.
#
# To make it work, you will need to install a latex distribution on your 
# computer (such as Miktex for Windows users) and make sure pdflatex program can
# be found in the PATH on your system (try calling it on any command line to make
# sure this is the case). The tool also use the pydoc script.
#
# The script must be launched in its correct position inside the mamba source tree
# after a complete build using the distutils setup was performed. The tool will
# use the generated files found in the created build directory (and not a previous
# installation on your machine).

#Copyright (c) <2009>, <Nicolas BEUCHER>

#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish, 
#distribute, sublicense, and/or sell copies of the Software, and to permit 
#persons to whom the Software is furnished to do so, subject to the following 
#conditions: The above copyright notice and this permission notice shall be 
#included in all copies or substantial portions of the Software.

#Except as contained in this notice, the names of the above copyright 
#holders shall not be used in advertising or otherwise to promote the sale, 
#use or other dealings in this Software without their prior written 
#authorization.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
# 
import os
import sys
import glob
import pydoc

################################################################################
# Latex predefined beginning and ending
################################################################################
begin = r"""
\documentclass[a4paper,10pt,oneside]{article}
\usepackage{tikz}
\usepackage{xcolor}
\usepackage[a4paper, top=2cm, bottom=2cm, left=0.5cm, right=0.5cm]{geometry}
\usepackage{setspace}
\usepackage{pifont}
\usepackage{multicol}
\usepackage{multirow}
\RequirePackage{fancyhdr}

\definecolor{pagebg}{HTML}{80D080}
\definecolor{modfg}{HTML}{008000}
\definecolor{parts}{HTML}{0040A0}
\definecolor{classfg}{HTML}{E78F05}
\definecolor{deffg}{HTML}{8D1405}
\pagecolor{pagebg}

\fancyfoot{}
\rfoot{\textcolor{white}{\textbf{\thepage}}}
\lfoot{\textcolor{white}{\textbf{www.mamba-image.org}}}
\fancyhead{}
\chead{
\begin{tikzpicture}
\node (Logo) [rectangle, fill=white, rounded corners]
{
    \begin{tabular*}{1.0\textwidth}{ @{ \extracolsep{\fill} } lr}
    \multirow{2}{*}{\includegraphics[width=0.2\textwidth]{mamba_logo.pdf}} &
    \textbf{python API quick reference} \\
    & for version %s \\
    \end{tabular*}
};
\end{tikzpicture}
}

\newcommand{\modName}[1]{\textcolor{modfg}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Module : }\textbf{#1}}\vspace{0.2cm}}

\newcommand{\className}[1]{\textcolor{classfg}{\footnotesize{\textbf{#1}}}}

\newcommand{\defp}{\textcolor{deffg}{\textbf{def }}}

\newenvironment{modDesc}
{\scriptsize\begin{spacing}{0}}
{\end{spacing}\normalsize\vspace{0.3cm}}

\newenvironment{classSec}
{\small\textcolor{parts}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Class :}}\\\vspace{0.1cm}\scriptsize\begin{spacing}{0}}
{\end{spacing}\normalsize\vspace{0.2cm}}

\newenvironment{methodList}
{\tiny\begin{spacing}{0}}
{\end{spacing}\normalsize\vspace{0.1cm}}

\newenvironment{funcSec}
{\small\textcolor{parts}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Functions :}}\\\vspace{0.1cm}\scriptsize\begin{spacing}{0}}
{\end{spacing}\normalsize\vspace{0.2cm}}

\setlength{\parskip}{0.1cm}

\begin{document}
\pagestyle{fancy}
\begin{center}
\tikzstyle{module}=[rectangle, fill=white, rounded corners]

"""

end = r"""

\begin{tikzpicture}
\node (general) [module] {
\begin{minipage}{1.0\textwidth}
\begin{multicols}{2}
\begin{flushleft}

\textcolor{modfg}{\rule{1ex}{1ex}\hspace{1ex}\textsc{General}}\vspace{0.2cm}

\begin{minipage}{\columnwidth}
\small\textcolor{parts}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Grid and Edge:}}

\scriptsize
Mamba can work with two grids : \textbf{HEXAGONAL} and \textbf{SQUARE}.

The \textbf{DEFAULT\_GRID} is used by the function when no other grid is
specified. Its value, HEXAGONAL at start, can be changed with the appropriate 
function.

Two edge behaviors are defined : \textbf{EMPTY} and \textbf{FILLED}.
\end{minipage}

\begin{minipage}{\columnwidth}
\small\textcolor{parts}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Directions/Neighbors :}}

\scriptsize
\begin{center}
\begin{tabular}{cc}
hexagonal grid & square grid \\
\includegraphics[scale=0.22]{../userman/hxGriddir.png} &
\includegraphics[scale=0.3]{../userman/sqGriddir.png} \\
\end{tabular}
\end{center}
\normalsize

\end{minipage}

\begin{minipage}{\columnwidth}
\small\textcolor{parts}{\rule{1ex}{1ex}\hspace{1ex}\textsc{Structuring elements :}}

\scriptsize
\begin{center}
\begin{tabular}{c}
List of structuring elements defined in Mamba\\
\includegraphics[scale=0.25]{../userman/se.png} \\
\end{tabular}
\end{center}
\normalsize

\end{minipage}

\end{flushleft}
\end{multicols}
\end{minipage}
};
\end{tikzpicture}

\end{center}
\end{document}
"""

################################################################################
# Global variables
################################################################################
VERSION = "Undef"
PROVDOC = 'doc.txt'
OUTDOC = 'pyquickref.tex'

################################################################################
# Data representation
################################################################################
# Here we stored the information collected in the Python source code (docstring)
# into a workable class
class klass:
    def __init__(self, name):
        self.name = name.replace('_','\\_')
        self.desc = ''
        self.methods = {}
    def fillDesc(self, d):
        self.desc = self.desc+' '+d.replace('_','\\_')
    def addMethod(self, m):
        if m!='':
            m = m.replace('_','\\_')
            self.methods[m] = ''
    def fillMethod(self, m, d):
        if m!='':
            m = m.replace('_','\\_')
            self.methods[m] = self.methods[m]+' '+d.replace('_','\\_')
    def __repr__(self):
        return self.name
        
class func:
    def __init__(self, name):
        self.name = name.replace('_','\\_')
        self.desc = ''
    def fillDesc(self, d):
        self.desc = self.desc+' '+d.replace('_','\\_')
    def __repr__(self):
        return self.name
            
################################################################################
# The module information extraction
################################################################################
# The function parses the pydoc output and produces a tex format of it.
# In the case of the quick reference, this format is particular (only the
# function names and signature are used)
def extractModule(path):
    f = file(path)
    lines = f.readlines()
    f.close()

    sections = {
                "NAME" : '',
                "FILE" : '',
                "DESCRIPTION" : '',
                "CLASSES" : [],
                "FUNCTIONS" : [],
                "DATA" : []
                }
        
    in_section = ""
    in_klass = False
    in_klass_method_list = False
    for i,l in enumerate(lines):
        l = l.replace('\n','')
        if l!='':
            if i>0 and l[0]!=' ':
                in_section = l
            else:
                if in_section=="NAME" or in_section=="FILE":
                    # sections NAME and FILE contains only one information
                    sections[in_section] = l[4:]
                elif in_section=="DESCRIPTION":
                    # The DESCRIPTION can be spreaded along multiple lines
                    # here we concatened all of them
                    sections[in_section] = sections[in_section]+' '+l[4:]
                elif in_section=="CLASSES":
                    # The CLASSES section lists all the classes and their methods
                    sl = l[4:].split(' ')
                    if sl[0]=="class":
                        k = klass(sl[1])
                        sections[in_section].append(k)
                        in_klass = True
                        in_klass_method_list = False
                        m = ''
                    elif in_klass and len(sl)<1:
                        in_klass = False
                    elif in_klass:
                        if l.find("Methods defined here")>=0:
                            in_klass_method_list = True
                        elif not in_klass_method_list:
                            k.fillDesc(l[8:])
                        elif in_klass_method_list and len(sl)>3 and sl[3]!='' and l.find('(')>=0:
                            m=l[8:]
                            k.addMethod(m)
                        elif in_klass_method_list and m:
                            k.fillMethod(m, l[12:]+'\n')
                elif in_section=="FUNCTIONS":
                    # Handling the functions
                    if len(l)>4 and l[4]!=' ':
                        fn = func(l[4:])
                        sections[in_section].append(fn)
                    elif len(l)>=8:
                        fn.fillDesc(l[8:]+'\n')
        
    #Begin
    linesout = []
    

    # Module name and description
    s = "\\begin{tikzpicture}\n"
    linesout.append(s)
    s = "\\node ("+sections["NAME"]+") [module] { \n"
    linesout.append(s)
    s = "\\begin{minipage}{1.0\\textwidth}\n"
    linesout.append(s)
    s = "\\begin{multicols}{2}\n"
    linesout.append(s)
    s = "\\begin{flushleft}\n\n"
    linesout.append(s)
    
    s = "\\modName{"+sections["NAME"]+"}\n\n"
    linesout.append(s)
    
    s = "\\begin{modDesc}\n"
    linesout.append(s)
    s = sections["DESCRIPTION"].strip()+"\n"
    linesout.append(s)
    s = "\\end{modDesc}\n\n"
    linesout.append(s)

    # Classes
    if sections["CLASSES"]!=[]:

        s = "\\begin{classSec}\n\n"
        linesout.append(s)
        for k in sections["CLASSES"]:
            s = "\\className{"+k.name+"}\n"
            linesout.append(s)
            s = "\\begin{methodList}\n"
            linesout.append(s)
            meths = k.methods.keys()
            meths.sort()
            for m in meths:
                s = "\\ding{70} "+m+"\\newline\n"
                linesout.append(s)
            s = "\\end{methodList}\n\n"
            linesout.append(s)
        s = "\\end{classSec}\n\n"
        linesout.append(s)

    # Functions
    if sections["FUNCTIONS"]!=[]:

        s = "\\begin{funcSec}\n"
        linesout.append(s)
        for fn in sections["FUNCTIONS"]:
            s = "\defp "+fn.name+":\\newline\n"
            linesout.append(s)
        s = "\\end{funcSec}\n\n"
        linesout.append(s)
    
    s = "\\end{flushleft}\n"
    linesout.append(s)
    s = "\\end{multicols}\n"
    linesout.append(s)
    s = "\\end{minipage}\n"
    linesout.append(s)
    s = "};\n"
    linesout.append(s)
    s = "\\end{tikzpicture}\n\n"
    linesout.append(s)
    
    return linesout

################################################################################
# Main script
################################################################################
# First moving to where the sources can be found
cwd = os.getcwd()
os.chdir(glob.glob('../../src/mambaApi/build/lib*/')[0])
# Listing all the interesting Python sources
mod_mbComp = glob.glob('mambaComposed/[!_]*.py') # __init__.py is not catch
mod_mbComp.sort()
# The file to document
pyfile_list = ['mamba.py','mambaDraw.py','mambaExtra.py'] + mod_mbComp
# getting the version
os.system('%s -c "import mamba; print mamba.VERSION" > %s' %(sys.executable, PROVDOC) )
VERSION = file(PROVDOC).readlines()[0]
# Creating the tex file (all the lines)
lines = [begin % (VERSION)]
for f in pyfile_list:
    os.system(sys.executable+' '+pydoc.__file__+' '+f.split('.')[0].replace('/','.').replace('\\','.')+' > '+PROVDOC)
    lines = lines+extractModule(PROVDOC)
lines.append(end)
# Removing byproducts and returning to the original directory
os.remove(PROVDOC)
os.chdir(cwd)
# writing the final tex file
f = file(OUTDOC,'w')
f.writelines(lines)
f.close()
#creating the pdf
os.system('pdflatex '+OUTDOC)
os.system('pdflatex '+OUTDOC)
