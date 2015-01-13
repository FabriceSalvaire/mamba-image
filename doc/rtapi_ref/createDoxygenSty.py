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

import sys

f = file(sys.argv[1]+'/doxygen.sty')
lines = f.readlines()
f.close()

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
    
f = file(sys.argv[1]+'/mambaDoxygen.sty', 'w')
f.writelines(out_lines)
f.close()
