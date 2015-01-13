"""
Test cases for the error string function.

The error function allows to associate a small string explanation with an error
code.
    
Python function:
    Not Applicable
    
C function:
    MB_StrErr
"""

import mambaCore
import unittest
import random

class TestError(unittest.TestCase):

    def testError(self):
        """Tests error function"""
        for i in range(mambaCore.ERR_UNKNOWN+1):
            err_str = mambaCore.MB_StrErr(i)
            self.assert_(err_str!="")
            
        ref_str = mambaCore.MB_StrErr(mambaCore.ERR_UNKNOWN)
        for i in range(mambaCore.ERR_UNKNOWN+1,10):
            err_str = mambaCore.MB_StrErr(i)
            self.assert_(err_str==ref_str)
            
        self.assert_(mambaCore.NO_ERR==0)
            

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestError)

if __name__ == '__main__':
    unittest.main()
