#! /usr/bin/python
# Test of FakeIMAPProps Class
# 21/06/2002 : JA

import os, sys
sys.path.insert(0, '..')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../..')+'/lib/python/')
sys.path.insert(0, os.environ.get('ZOPE_HOME', '../../..')+'/Products/WebMail/')

import Zope
from WebMailTool import FakeIMAPProps
from unittest import TestCase, main
from Testing import makerequest


class FakeIMAPPropsTestCase(TestCase):
    """ Testing FakeIMAPProps Class """
    def setUp(self):
        self.app = makerequest.makerequest(Zope.app())
        get_transaction().begin
        self.app.manage_addProduct['NuxWebMail'].manage_addFakeIMAPProps()
        self.Fake = self.app.imapprops
        
    def tear_down(self):
        get_transaction().abort()
        self.app._p_jar.close()

    def test_one(self):
        #
        # Test all methods of the FakeIMAPProps Class
        #
         self.assertEquals(self.Fake.getIMAPLogin()  ,'janguenot@nuxeo.com')
         self.assertEquals(self.Fake.getMailFrom()   ,'janguenot@nuxeo.com')
         self.assertEquals(self.Fake.getNameFrom()    ,'Julien Anguenot')
         self.assertEquals(self.Fake.getIMAPServer() ,'imap.nuxeo.com')
         self.assertEquals(self.Fake.getIMAPPort()   ,'')
         self.assertEquals(self.Fake.getSMTPServer() ,'localhost')
         self.assertEquals(self.Fake.getSMTPPort()   ,'')
         self.assertEquals(self.Fake.getSignature()  ,'Julien Anguenot')
         self.assertEquals(self.Fake.getAutoSaveSentMessage() , 0)
         self.assertEquals(self.Fake.getNbCharSubject() , 25)
         self.assertEquals(self.Fake.getListingSize(), 15)
         self.assertEquals(self.Fake.getAutoViewAtt(), 0)
         self.assertEquals(self.Fake.getSortMail(), "order")
         self.assertEquals(self.Fake.getDefaultFoldersNames(),
                           {'Inbox':  ['INBOX','Boîte de réception'],
                            'Sent':   ['INBOX.Sent','Eléments envoyés'],
                            'Drafts': ['INBOX.Drafts', 'Brouillons'],
                            'Trash':  ['INBOX.Trash', 'Corbeille']}
                           )
         
if __name__ == '__main__':
    main(argv = ['-v', '-v'])
