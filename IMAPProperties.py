# -*- coding: iso-8859-15 -*-
#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# Julien Anguenot <mailto:ja@nuxeo.com>
# See LICENSE.TXT for licensing information
#

# $Id$

""" IMAPProperties class
"""

from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

class IMAPProperties(SimpleItem):
    """IMAPProperties contains user's parameters for the Portal_WebMail
    Product"""
    id = "IMAPProperties"
    meta_type = "IMAPProperties"

    security = ClassSecurityInfo()

    def _getDirectory(self):
        dirtool = getToolByName(self, 'portal_directories', None)
        return dirtool

    def _getCurrentUserEntry(self):
        dirtool = self._getDirectory()
        mtool = getToolByName(self, 'portal_membership')
        member_id = mtool.getAuthenticatedMember().getUserName()
        entry = dirtool.members.getEntry(member_id)
        if entry is None:
            raise 'Unauthorized'
        return entry

    def getIMAPLogin(self):
        """Return IMAP login"""
        entry = self._getCurrentUserEntry()
        imap_login = entry.get('imap_login', None)
        if imap_login == '':
            imap_login = None
        return imap_login

    def getIMAPPassword(self):
        """Return IMAPPassword"""
        entry = self._getCurrentUserEntry()
        imap_password = entry.get('imap_password', None)
        if imap_password == '':
            imap_password = None
        return imap_password

    def getMailFrom(self):
        """Return mail from"""
        entry = self._getCurrentUserEntry()
        return entry.get('email', None)

    def getIdentity(self):
        """Return nom from"""
        entry = self._getCurrentUserEntry()
        memberdir = self._getDirectory().members
        title_field = getattr(memberdir, 'title_field', None)
        return entry.get(title_field, None)

    def getSignature(self):
        """Return personal mail signature"""
        return "I'm Test Mail"

    def getAutoSaveSentMessage(self):
        """Return AutoSaveSentMessage value"""
        return "yes"

    def getNbCharSubject(self):
        """Return Nb characters display for message subject"""
        return 25

    def getListingSize(self):
        """Return the number of messages diplay on one page view"""
        return 20

    def getAutoViewAtt(self):
        """Return the autoViewAtt value"""
        return 0

    def getSortMail(self, REQUEST=None):
        """Return the sorting for getting mail headers"""
        if REQUEST is not None:
            return REQUEST.get('sortmail', "date")
        else:
            return "date"

    def getDefaultFoldersNames(self):
        """Return default folders names"""
        return ({'Inbox': ['INBOX','_Inbox_Folder_'],
                 'Sent': ['INBOX.Sent','_Sent_element_folder_'],
                 'Drafts': ['INBOX.Drafts', '_Draft_folder_'],
                 'Trash': ['INBOX.Trash', '_Trash_folder_'],
                }
               )

InitializeClass(IMAPProperties)

