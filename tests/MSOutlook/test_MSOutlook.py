#! /usr/bin/python
# Test of MSOutlook Class
# 09/07/2002 : JA

import os, sys
sys.path.insert(0, '..')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../../../')+'/lib/python/')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../../../')+'/Products/WebMail/')

from MSOutlookImport import MSOutlookImport 
from unittest import TestCase, main

class MSOutlookImportTestCase(TestCase):
    """ Testing MSOutlookImport Class """
    def setUp(self):
        """ Getting an instance of tested class """
        #
        # Doing some instances with differents export
        #
        self.instance0 = MSOutlookImport(open('carnet.txt'))
        self.instance1 = MSOutlookImport(open('carnet2.txt'))

    def test0(self):
        """ Testing the first instance """
        print self.instance0.do_list()

    def test1(self):
        """ Testing the second instance """
        print self.instance1.do_list()
        
if __name__ == '__main__':
    main(argv = ['-v', '-v'])


    
         
        
    
