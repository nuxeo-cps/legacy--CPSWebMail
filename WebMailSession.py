# -*- coding: iso-8859-15 -*-
#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# Julien Anguenot <mailto:ja@nuxeo.com>
# See LICENSE.TXT for licensing information
#

"""
    WebMailSession.py
"""

import string

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from RFC822MessagesTools import render_date
from DateTime import *

from zLOG import LOG, DEBUG

UseWebMailPermission = "Use WebMail"

class WebMailSession:
    """WebMailSession class.

    It handles the users sessions behaviour.
    """

    security = ClassSecurityInfo()

    security.declareProtected(UseWebMailPermission, "beginMailSession")
    def beginMailSession(self, REQUEST):
        """Begin a new mail session"""
        if not REQUEST.SESSION.has_key('mail_session'):
            REQUEST.SESSION['mail_session'] = {
                'att_list' : [], 'nb_att' : 0, 'start' : 0,
                'IMAPName' : 'INBOX'}

    security.declareProtected(UseWebMailPermission, "createMailSession")
    def createMailSession(self, REQUEST):
        """Stock a new mail session"""

        mail_structure = {}

        if REQUEST.has_key('to'):
            mail_structure['to']  = REQUEST['to']
        if REQUEST.has_key('cc'):
            mail_structure['cc']  = REQUEST['cc']
        if REQUEST.has_key('bcc'):
            mail_structure['bcc'] = REQUEST['bcc']
        if REQUEST.has_key('subject'):
            mail_structure['subject'] = REQUEST['subject']
        if REQUEST.has_key('body'):
            mail_structure['body'] = REQUEST['body']

        if REQUEST.SESSION.has_key('mail_session'):
            mail = REQUEST.SESSION.get('mail_session',{})
            if mail.has_key('nb_att') and mail.has_key('att_list'):
                mail_structure['nb_att'] = mail['nb_att']
                mail_structure['att_list'] = mail['att_list']
        else:
            mail_structure['nb_att'] = 0
            mail_structure['att_list'] = []
        REQUEST.SESSION['mail_session'] = mail_structure

    security.declareProtected(UseWebMailPermission, "createReplySession")
    def createReplySession(self, REQUEST, all=0):
        """Create a new mail session of reply"""

        # Get session objects
        mail_structure = REQUEST.SESSION.get('mail_session')
        the_id = REQUEST.get('IMAPId')
        if not the_id:
            the_id = REQUEST.SESSION.get('vm_session', {})['IMAPId']

        # Get message
        folder  = self.getInboxFolder(REQUEST)
        message = folder.getIMAPMessage(the_id)
        subject = message.getSubject()

        # Mailreaders in different countries usually use their own language to
        # construct the "Re:" prefix on subjects.  However, most of the time
        # they comply with the standard of using two letters + a colon.
        # Therefore, only apply a 'Re:' string if the third letter is NOT a
        # colon.
        if len(subject) > 2 and subject[2] != ':':
            subject = 'Re:' + subject
        mail_structure['subject'] = subject
        mail_structure['body'] = ('\n> ' + string.join(
            string.split(message.render_body(message.getBody(), 'html'),'\n'),
            '\n> ') + '\n\n')

        if all:
            mail_structure['to'] = message.getTo()
            mail_structure['cc'] = message.getCC()
        else:
            mail_structure['to'] = message.getSenderMail()

        flag = REQUEST.get('flag', 'reply')
        if flag is not None:
            mail_structure['flag'] = flag
        if the_id:
            mail_structure['IMAPId'] = the_id


        # Commit of session object
        REQUEST.SESSION['mail_session'] = mail_structure

    security.declareProtected(UseWebMailPermission, "createForwardSession")
    def createForwardSession(self, REQUEST):
        """Create a new mail session for forwarding"""

        # Get session object
        mail_structure = REQUEST.SESSION.get('mail_session')
        the_id = REQUEST.SESSION.get('vm_session')['IMAPId']

        # Get the message
        folder  = self.getInboxFolder(REQUEST)
        message = folder.getIMAPMessage(the_id)

        # Body
        body = "\n\n>> Expéditeur d'origine: "
        body += message.getSenderName() +\
            ' (' + message.getSenderMail() + ') '
        body += "\n>> Date: " \
            + render_date(message.getDate()) + "\n\n"
        new_body = string.split(
            message.render_body(message.getBody(), 'html'), '\n')
        new_body = '>> ' + string.join(new_body, '\n>> ')  + ' \n\n'
        new_body = body + new_body

        mail_structure['body'] = new_body
        mail_structure['subject'] = 'Fwd: ' + message.getSubject()

        flag = REQUEST.get('flag', 'forward')
        if flag is not None:
            mail_structure['flag'] = flag
        if the_id:
            mail_structure['IMAPId'] = the_id

        # Commit of session object
        REQUEST.SESSION['mail_session'] = mail_structure


    security.declareProtected(UseWebMailPermission, "saveMailSession")
    def saveMailSession(self, REQUEST):
        """Save a mail_session_composer"""
        mail_structure = REQUEST.SESSION.get('mail_session', {})

        if REQUEST.has_key('to'):
            mail_structure['to'] = REQUEST['to']
        if REQUEST.has_key('cc'):
            mail_structure['cc'] = REQUEST['cc']
        if REQUEST.has_key('bcc'):
            mail_structure['bcc'] = REQUEST['bcc']
        if REQUEST.has_key('subject'):
            mail_structure['subject'] = REQUEST['subject']
        if REQUEST.has_key('body'):
            mail_structure['body'] = REQUEST['body']
        if REQUEST.has_key('IMAPId'):
            mail_structure['IMAPId'] = REQUEST['IMAPId']
        if REQUEST.has_key('flag'):
            mail_structure['flag'] = REQUEST['flag']

        if not (mail_structure.has_key('nb_att')
                and mail_structure.has_key('att_list')):
            mail_structure['nb_att'] = 0
            mail_structure['att_list'] = []

        REQUEST.SESSION['mail_session'] = mail_structure

    security.declareProtected(UseWebMailPermission, "createDraftSession")
    def  createDraftSession(self, IMAPId, IMAPName, REQUEST):
        """Create a draft session"""
        message = self.getMessage(IMAPName, IMAPId)
        mail_session = {}
        mail_session['to'] = message.getTo()
        mail_session['cc'] = message.getCC()
        mail_session['bcc'] = message.getBCC()
        mail_session['subject'] = message.getSubject()
        mail_session['body'] = message.getBody()
        mail_session['IMAPName'] = IMAPName
        mail_session['IMAPId'] = IMAPId

        if message.existAttachment():
            attachements = message.getAttachments()
            mail_session['att_list'] = attachements
            mail_session['nb_att'] = len(attachements)

        REQUEST.SESSION['mail_session'] = mail_session

    security.declareProtected(UseWebMailPermission, "endMailSession")
    def endMailSession(self, REQUEST):
        """Erase current session object"""
        REQUEST.SESSION['mail_session'] = {}

    security.declareProtected(UseWebMailPermission, "createViewSession")
    def createViewSession(self, REQUEST):
        """Initialize a new view message session"""
        vm_session = {'IMAPId': REQUEST['IMAPId'],
                      'IMAPName': REQUEST['IMAPName'],
                      'view': REQUEST['view']}
        REQUEST.SESSION['vm_session'] = vm_session

    security.declareProtected(UseWebMailPermission, "initGroupMailSession")
    def initGroupMailSession(self, REQUEST):
        """Init of a grouping mail sending"""

        # Update Session With the selected contacts
        mail_session = REQUEST.SESSION.get('mail_session',{})
        email_list_to = REQUEST.form.get('pto', [])
        email_list_cc = REQUEST.form.get('pcc', [])
        email_list_bcc = REQUEST.form.get('pbcc', [])

        # XXX: please comment
        to = mail_session.get('to', "")
        if to != "":
            to += ", "

        for pto in email_list_to:
            to += pto + ', '

        tmp = ""
        i   = 0
        while i < (len(to) - 2):
            tmp = tmp + to[i]
            i = i + 1

        to = tmp

        cc = mail_session.get('cc', "")
        if cc != "":
            cc += ", "

        for pcc in email_list_cc:
            cc += pcc + ', '

        tmp = ""
        i   = 0

        while i < (len(cc) -2):
            tmp = tmp + cc[i]
            i = i + 1

        cc = tmp

        bcc = mail_session.get('bcc', "")
        if bcc != "" and bcc != []:
            bcc += ", "

        for pbcc in email_list_bcc:
            bcc += pbcc + ', '

        tmp = ""
        i  = 0

        while i < (len(bcc) - 2):
            tmp = tmp + bcc[i]
            i = i + 1

        bcc = tmp

        mail_session['to'] = to
        mail_session['cc'] = cc
        mail_session['bcc'] = bcc

        REQUEST.SESSION['mail_session'] = mail_session

    security.declareProtected(UseWebMailPermission, "setSearchSession")
    def setSearchSession(self, addressbook, REQUEST):
        """Init of search result session"""

        # Destruction of an older session if exists
        REQUEST.SESSION['search_results'] = ()

        visible = addressbook.getVisibleSchemaKeys()
        search_param = REQUEST.form.get('search_param', '')

        # Built of the dictionnary results of search on all visibles params
        res = ()
        for props in visible:
            t = addressbook.searchEntry(**{props: search_param})
            for x in t:
                # dictionnary
                if x not in res:
                    res = res + (x,)

        # Init of the results session
        REQUEST.SESSION['search_results'] = res

    security.declareProtected(UseWebMailPermission, "setSearchSessionCPS3")
    def setSearchSessionCPS3(self, addressbook, REQUEST):
        """Init of search result session for CPS3"""
        REQUEST.SESSION['search_results'] = ()

        widgets = addressbook._getLayout(search=1).objectItems()
        visible = [x.getWidgetId() for y, x in widgets]
        search_param = REQUEST.form.get('search_param', '')

        # Built of the dictionnary results of search on all visibles params
        res = ()
        for props in visible:
            t = addressbook.searchEntries(**{props : search_param})
            for x in t:
                # dictionnary
                if x not in res:
                    res = res + (x,)

        # Init of the results session
        REQUEST.SESSION['search_results'] = res

    security.declareProtected(UseWebMailPermission, "setIndexSearchSession")
    def setIndexSearchSession(self, addressbook, begin, REQUEST):
        """Set a search session for an index"""

        # Destruction of an older session if exists
        REQUEST.SESSION['search_results'] = ()

        id_field = addressbook['id_field']
        title_field = addressbook['title_field']

        # Built of the dictionnary results of search on all Name Visible param
        lrange = {'A' : ['A', 'B', 'C', 'D', 'E'],
              'F' : ['F', 'G', 'H', 'I'],
              'J' : ['J', 'K', 'L', 'M', 'N', 'O', 'Q', 'R', 'S'],
              'T' : ['T', 'U'],
              'V' : ['V', 'W', 'X', 'Y', 'Z']}

        t = addressbook.searchEntry()
        res = ()
        for x in t:
            if string.capitalize(x[title_field])[0] in lrange[begin] \
               or string.capitalize(x[id_field])[0] in lrange[begin]:
                res += (x,)

        # Upgrade of the results session
        REQUEST.SESSION['search_results'] = res

#InitializeClass(WebMailSession)
