#! /usr/bin/python
# Test of WebMailTool Class
# 21/06/2002 : JA

import os, sys
sys.path.insert(0, '..')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../..')+'/lib/python/')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../..')+'/Products/WebMail/')

import Zope
from WebMailTool import WebMailTool
from unittest import TestCase, main
from Testing import makerequest

from AccessControl import SecurityManager

from Products.WebMail.IMAPFolder  import IMAPFolder
from Products.WebMail.IMAPMessage import IMAPMessage
from Products.WebMail.IMAPGateway import IMAPGateway


class UnitTestSecurityPolicy:
    "Stub out the existing security policy for unit testing purposes"
    #
    #   Standard SecurityPolicy interface
    #
    def validate(*args, **kw):
        return 1
  
    def checkPermission(*args, **kw):
        return 1

class WebMailToolTestCase(TestCase):
    """ Testing WebMailToolTestCase Class """
    def setUp(self):
        self.app = makerequest.makerequest(Zope.app())
        get_transaction().begin   
        self._policy = UnitTestSecurityPolicy()
        SecurityManager.setSecurityPolicy(self._policy)
        self.app.manage_addProduct['NuxWebMail'].manage_addTool(
            "Portal WebMail Tool") # meta_type
        self.portal_webMail = self.app.portal_webMail
        self.app.manage_addProduct["NuxWebMail"].manage_addFakeIMAPProps()
        
    def tear_down(self):
        get_transaction().abort()
        self.app._p_jar.close()

    def test_version(self):
        """Test of returned version"""
        self.assertEquals(self.portal_webMail.getVersion(), "0.1")
   
    def test_defaultImapName(self):
        """Test the default value for the Inbox folder"""
        self.assertEquals(self.portal_webMail.getImapName(), 'INBOX')

    def test_parsed_body(self):
        """Test a parsed body test"""
        #
        # Tests messages
        #
        IMAPId = "107"
        IMAPName = "INBOX"
        folder = IMAPFolder(IMAPName, IMAPName, self.portal_webMail)
        message = folder.getIMAPMessage(IMAPId)
        body = message.get_parsed_body()
        output = open('body', "w")
        output.write(body)
        output.close()

if __name__ == "__main__":
    main(argv = ['-v', '-v'])

