"""
Module defining the class used to generate output in HTML format in a given 
file for the Mamba Test Platform.
The class also produces minimal output, if selected, on the standard output.
"""

from .MambaTestOutput import *

import sys
import time

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

################################################################################
# HTML specific string
################################################################################

_header_begin = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="fr" xml:lang="fr">
<head>
   <title>Mamba Test Results</title>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   
    <style type="text/css">
    body {
        padding: 0px;
        margin: 0px;
        width:100%;
    }
    
    div#header {
        display: block;
        position:absolute;
        padding: 0px;
        margin: 0px;
        width:100%;
        height: 60px;
        top: 0px;
        left: 0px;
        border-bottom: 1px solid #000000;
        background:#d0ffd0 url(http://www.mamba-image.org/images/mamba_logo.png) no-repeat right top;
    }
    div#header p {
        margin: 5px;
        font-size:12px;
    }
    div#header p.alert {
        margin: 5px;
        font-size:12px;
        color: #ff0000;
    }
    
    div.listPackages {
        display: block;
        position:absolute;
        padding: 0px;
        margin: 0px;
        width:20%;
        left: 0px;
        top: 60px;
        border-right: 1px solid #000000;
        border-bottom: 1px solid #000000;
    }
    div.listPackages p {
        display: block;
        padding: 3px 0px 3px 5px;
        margin: 0px;
        vertical-align:middle;
        background-color:#ffffff; /*important*/
    }
    div.listPackages span.expander {
        display: inline-block;
        width:5%;
        height:18px;
        padding: 0px;
        margin: 0px;
        color:#000000;
        font-size:14px;
        text-align:center;
        vertical-align:middle;
        font-weight:bold;
        background-color:#ffffff; /*important*/
        border: 1px solid #000000;
    }
    div.listPackages span.expander:hover {
        color:#ffffff;
        background-color:#000000; /*important*/
    }
    div.listPackages span.pack_ok {
        display: inline-block;
        width:85%;
        height:18px;
        padding: 0px 0px 0px 10px;
        margin: 0px 0px 0px 5px;
        font-size:14px;
        font-weight:bold;
        vertical-align:middle;
        color:#60df60;
        border: 1px solid #60df60;
    }
    div.listPackages span.pack_ko {
        display: inline-block;
        width:85%;
        height:18px;
        padding: 0px 0px 0px 10px;
        margin: 0px 0px 0px 5px;
        font-size:14px;
        font-weight:bold;
        vertical-align:middle;
        color:#df6060;
        border: 1px solid #df6060;
    }
    div.listModules {
        display: block;
        padding: 0px;
        margin: 0px;
        width:100%;
    }
    div.listModules ul{
        background:#fff;
        padding: 0px;
        margin: 0px;
        list-style: none;
    }
    div.listModules ul li{
        padding: 0px;
        margin: 0px;
    }
    div.listModules ul li a.ok {
        display: block;
        padding: 3px 0px 3px 20px;
        vertical-align:middle;
        color:#60df60;
        font-size:12px;
        font-weight:bold;
        text-decoration:none;
        background-color:#ffffff; /*important*/
    }
    div.listModules ul li a.ok:hover {
        font-weight:normal;
        color:#FFFFFF;
        background-color:#60df60;
    }
    div.listModules ul li a.ko {
        display: block;
        padding: 3px 0px 3px 20px;
        vertical-align:middle;
        color:#df6060;
        font-size:12px;
        font-weight:bold;
        text-decoration:none;
        background-color:#ffffff; /*important*/
    }
    div.listModules ul li a.ko:hover {
        font-weight:normal;
        color:#FFFFFF;
        background-color:#df6060;
    }
    
    div#testModule {
        display: block;
        margin:10px 10px 10px 10px;
        position:absolute;
        padding:0px;
        width: 75%;
        left: 20%;
        top: 60px;
        border: 1px solid #000000;
    }
    div#testModule h2 {
        margin:0px 0px 0px 0px;
        font-size:16px;
        font-family:monospace;
        font-weight:bold;
        text-indent:10px;
        width:100%;
        background:#555555;
        color:#FFFFFF;
    }
    div#testModule div.moddesc {
        margin: 0px;
        padding: 2px 10px 2px 10px;
        background:#ffff60;
        border-bottom: 1px solid #000000;
        font-size:12px;
    }
    div#testModule p.desctitle {
        font-size:12px;
        font-weight:bold;
        text-decoration: underline;
    }
    div#testModule p.testdesc {
        margin:1px;
        font-size:12px;
    }
    div#testModule p.testname {
        margin:1px;
        font-size:12px;
        text-decoration:underline;
    }
    div#testModule div.modres {
        margin: 0px;
        padding: 2px 10px 2px 10px;
        font-size:12px;
    }
    div#testModule table {
        width:100%;
    }
    div#testModule p.time {
        font-size:12px;
        color:#202020;
    }
    div#testModule th {
        border: 1px solid #0970d0;
        font-size:13px;
        padding:0px;
        background : #2299ff;
        text-align:left;
    }
    div#testModule td.desc {
        font-size:12px;
        width:50%;
    }
    div#testModule td.info {
        font-size:12px;
        width:45%;
    }
    div#testModule td.resok {
        background:#70ff70;
        font-size:12px;
        font-weight:bold;
        border: 1px solid #0970d0;
        width:5%;
    }
    div#testModule td.reserr {
        background:#ff7070;
        font-family:monospace;
        font-size:12px;
        font-weight:bold;
        border: 1px solid #0970d0;
        width:5%;
    }
    div#testModule td.resfail {
        background:#ff7070;
        font-size:12px;
        font-weight:bold;
        border: 1px solid #0970d0;
        width:5%;
    }
    
    </style>

<script language="JavaScript" type="text/javascript">
<!--
"""

_header_end = """
function displayTestModule(index)
{
    document.getElementById("testModule").innerHTML = testModules[index];
}

function expand(pack_name)
{
    if (testPackages[pack_name][0]==true) {
        document.getElementById("exp_"+pack_name).innerHTML = "+";
        document.getElementById(pack_name).innerHTML = "";
        testPackages[pack_name][0]=false;
    } else {
        document.getElementById("exp_"+pack_name).innerHTML = "-";
        document.getElementById(pack_name).innerHTML = testPackages[pack_name][1];
        testPackages[pack_name][0]=true;
    }
}

// -->
</script>

</head>
"""

_body_end = """
</body>
</html>
"""

################################################################################
# Class for HTML output
################################################################################
class MambaTestOutputHtml(MambaTestOutput):
    """
    This class implements a HTML output generator for the Mamba Test Platform.
    """
    
    def __init__(self, fpath, descriptions=1, verbosity=0):
        """
        Creator with level of verbosity, descriptions allowed, and path of the
        file created by the html generator.
        
        By default, description option is not taken into account. If verbose
        is greater than 0 the class will also produce minimal information on the
        standard output.
        """
        MambaTestOutput.__init__(self, descriptions, verbosity)
        self.stream = open(fpath, 'w')
        self.fpath = fpath
        
    def notifyModuleTestStart(self, moduleInfo):
        """Notifies the beginnig of a module test."""
        if self.verbosity>0:
            sys.stdout.write(moduleInfo.name+" : ")
            sys.stdout.flush()

    def _getDescription(self, test):
        # returns the descriptions associated with a test
        return str(test.shortDescription())
            
    def _getName(self, test):
        # returns the name of the test case function or method
        return str(test)
        
    def notifyTestStart(self, test):
        """Notifies the beginning of a test."""
        pass
        
    def notifyTestEnd(self, test, result):
        """Notifies the end of a test with its result."""
        pass
        
    def printModuleReport(self, moduleInfo, moduleResult):
        """
        Produces a report for the played module. 
        'moduleInfo' contains the name, description and time taken for the tests.
        'moduleResult' is an instance of MambaTestResult produced for the given 
        module.
        """
        if self.verbosity>0:
            run = moduleResult.testsRun
            sys.stdout.write("Ran %d test%s in %.3fs" % (run, run != 1 and "s" or "", moduleInfo.timeTaken))
            if not moduleResult.wasSuccessful():
                sys.stdout.write(" - FAILED\n")
            else:
                sys.stdout.write(" - OK\n")
                
    def _prepErrInfo(self, err):
        s = err.replace('\n','<br />')
        ls = s.split('"')
        a = "<a href='"+ls[1]+"'>"+ls[1]+"</a>"
        s = ls[0]+a+''.join(ls[2:])
        return s
                
    def _writeInfoAndResult2Html(self, modinfo, result):
        # Returns a string with the module info and the result in html format
        s = "<h2>"+modinfo.name+"</h2>"
        s = s + "<div class='moddesc'><p class='desctitle'>Description :</p>"
        s = s + "<pre>"+modinfo.desc.replace('\n','\\n')+"</pre></div>"
        run = result.testsRun
        s = s + "<div class='modres'>"
        s = s + "<p class='time'>Ran %d test%s in %.3fs</p>" % (run, run != 1 and "s" or "", modinfo.timeTaken)
        s = s + "<table>"
        s = s + "<tr><th>Test</th><th>Result</th><th>Info</th></tr>"
        for test in result.success:
            s = s + "<tr> <td class='desc'>"
            s = s + "<p class='testname'>%s :</p>" % (self._getName(test))
            s = s + "<p class='testdesc'>%s</p></td> " % (self._getDescription(test))
            s = s + "<td class='resok'>OK</td> "
            s = s + "<td class='info'> </td> </tr>"
        for test, err in result.failures:
            s = s + "<tr> <td class='desc'>"
            s = s + "<p class='testname'>%s :</p>" % (self._getName(test))
            s = s + "<p class='testdesc'>%s</p></td> " % (self._getDescription(test))
            s = s + "<td class='resfail'>FAIL</td> "
            s = s + "<td class='info'>%s</td> </tr>" % (self._prepErrInfo(err))
        for test, err in result.errors:
            s = s + "<tr> <td class='desc'>"
            s = s + "<p class='testname'>%s :</p>" % (self._getName(test))
            s = s + "<p class='testdesc'>%s</p></td> " % (self._getDescription(test))
            s = s + "<td class='reserr'>ERR</td> "
            s = s + "<td class='info'>%s</td> </tr>" % (self._prepErrInfo(err))
        s = s + "</table></div>"
        
        return s
        
    def _writeGeneralInfos2Html(self, playedModules, cov, morfs):
        # Computes general information such as the total number of modules
        # played, the number of tests (total), if there is some errors and 
        # so on
        s = time.strftime("<p>tests played on : %a, %d %b %Y %H:%M:%S</p>", time.gmtime())
        run = 0
        fails = 0
        timeTaken = 0.0
        for modinfo, result in list(playedModules.items()):
            run = run + result.testsRun
            fails = fails + sum(map(len, (result.failures, result.errors)))
            timeTaken = timeTaken + modinfo.timeTaken
        s = s + "<p>Ran %d test%s in %.3fs</p>" % (run, run != 1 and "s" or "", timeTaken)
        if cov:
            cov.html_report(directory='covhtml', morfs=morfs)
            s = s + "<p><a href='covhtml/index.html'>Code coverage infos</a></p>"
        if fails!=0:
            s = s + "<p class='alert'>%d test%s failed or encountered an error</p>" % (fails, fails != 1 and "s" or "")
        return s
        
    def printGeneralReport(self, playedModules, cov=None, morfs=[]):
        """
        Produces a complete report associated with a MambaTestRunner instance.
        All the modules played, their results and other information are displayed.
        """
        packages = {}
        index = 0
        first_error_index = -1
        self.stream.write(_header_begin)
        self.stream.write("var testModules = [\n")
        for modinfo, result in list(playedModules.items()):
            pack = modinfo.name.split('.')[0]
            if not pack in packages:
                packages[pack] = [True, [], 0]
            packages[pack][1].append((modinfo.name, result.wasSuccessful(), index))
            if first_error_index<0 and not result.wasSuccessful():
                first_error_index = index
            packages[pack][0] &= result.wasSuccessful()
            packages[pack][2] += result.testsRun
            s = self._writeInfoAndResult2Html(modinfo, result)
            self.stream.write('"'+s+'",\n')
            index = index + 1
        self.stream.write("];\n\n")
        self.stream.write("var testPackages = [];\n")
        pack_names = list(packages.keys())
        pack_names.sort()
        for pack in pack_names:
            modules = packages[pack][1]
            modules.sort()
            first_index = modules[0][2]
            s = "<ul>"
            for name, success, index in modules:
                if success:
                    s+="<li><a class='ok' href='Javascript:displayTestModule(%d);'>%s</a></li>" % (index,name)
                else:
                    s+="<li><a class='ko' href='Javascript:displayTestModule(%d);'>%s</a></li>" % (index,name)
            s+="</ul>"
            self.stream.write('testPackages["'+pack+'"] = [false, "'+s+'"];\n')
        self.stream.write(_header_end)
        if first_error_index<0:
            self.stream.write("<body onload='displayTestModule(%d)'>\n" % (first_index))
        else:
            self.stream.write("<body onload='displayTestModule(%d)'>\n" % (first_error_index))
        self.stream.write("<div id='header'>\n")
        s = self._writeGeneralInfos2Html(playedModules, cov, morfs)
        self.stream.write(s+"\n")
        self.stream.write("</div>\n")
        self.stream.write("<div class='listPackages'>\n")
        for pack in pack_names:
            self.stream.write('<p><span class="expander" onclick="expand('+repr(pack)+')" id="exp_'+pack+'">+</span>')
            if packages[pack][0]:
                self.stream.write("<span class='pack_ok'>"+pack+" ("+str(packages[pack][2])+" tests)</span>")
            else:
                self.stream.write("<span class='pack_ko'>"+pack+" ("+str(packages[pack][2])+" tests)</span>")
            self.stream.write("</p>\n")
            self.stream.write("<div id='"+pack+"' class='listModules'>\n")
            self.stream.write("</div>\n")
        self.stream.write("</div>\n")
        self.stream.write("<div id='testModule'>\n")
        self.stream.write("</div>\n")
        self.stream.write(_body_end)
        self.stream.close()
