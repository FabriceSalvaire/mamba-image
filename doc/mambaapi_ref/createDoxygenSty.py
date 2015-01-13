# Creating the mambaDoxygen.sty using the generated doxygen style
#

#Copyright (c) <2011>, <Nicolas BEUCHER>

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

f = file('latex/doxygen.sty')
lines = f.readlines()
f.close()

#\documentclass[a4paper]{book}
#\usepackage{makeidx}
#\usepackage{graphicx}
#\usepackage{multicol}
#\usepackage{float}
#\usepackage{listings}
#\usepackage{color}
#\usepackage{ifthen}
#\usepackage[table]{xcolor}
#\usepackage{textcomp}
#\usepackage{alltt}
#\usepackage[utf8]{inputenc}
#\usepackage{mathptmx}
#\usepackage[scaled=.90]{helvet}
#\usepackage{courier}
#\usepackage{doxygen}
#\lstset{language=C++,inputencoding=utf8,basicstyle=\footnotesize,breaklines=true,breakatwhitespace=true,tabsize=4,numbers=left }
#\makeindex
#\setcounter{tocdepth}{3}
#\renewcommand{\footrulewidth}{0.4pt}

out_lines = []
in_fancy = False
for l in lines:
    l = l.replace('\n', '')
    if l=='% Packages used by this style file':
        l = l + '\n\\RequirePackage[table]{xcolor}'
    if l=='% Setup fancy headings':
        in_fancy = True
    if l=='%---------- Internal commands used in this style file ----------------':
        in_fancy = False
    if l=="\\RequirePackage{helvet}":
        l = "%\\RequirePackage{helvet}"
    if l=="\\RequirePackage{sectsty}":
        l = "%\\RequirePackage{sectsty}"
    if l=="\\RequirePackage{tocloft}":
        l = "%\\RequirePackage{tocloft}"
    if l=="   {\\usefont{OT1}{phv}{bc}{n}\\color{darkgray}}}":
        l = "   {}}"
    if l=="\\allsectionsfont{\\usefont{OT1}{phv}{bc}{n}\\selectfont\\color{darkgray}}":
        l = "%\\allsectionsfont{\\usefont{OT1}{phv}{bc}{n}\\selectfont\\color{darkgray}}"
    if l=="  \\begin{figure}[H]%":
        l = "  \\begin{figure}%"
    if l=="\\setlength{\\parskip}{0.2cm}":
        l = "\\setlength{\\parskip}{0.0cm}"
    if in_fancy:
        l = '%'+l
    out_lines.append(l+'\n')
    
f = file('latex/mambaDoxygen.sty', 'w')
f.writelines(out_lines)
f.close()
