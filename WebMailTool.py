#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# Author: Julien Anguenot <mailto:ja@nuxeo.com>
# See LICENSE.TXT for licensing information
#

"""
   CPS WebMailTool Core Class
"""

__version__ = "0.1"

import os, time
from zLOG import LOG, DEBUG
from MSOutlookImport import MSOutlookImporter

#=============================================
# DEPENDENCES OF THE ORIGINAL WebMail Product
#=============================================

from IMAPGateway import IMAPGateway
from IMAPFolder  import IMAPFolder
from IMAPMessage import IMAPMessage
from Attachment  import Attachment

#===========================
#  BECAUSE ZOPE SECURITY
#===========================

from AccessControl import allow_class
allow_class(IMAPFolder)
allow_class(IMAPMessage)
allow_class(IMAPGateway)
allow_class(Attachment)

import timeoutsocket
timeoutsocket.setDefaultSocketTimeout(60) # Something to move somewhere else

import smtplib
import string
from urllib import quote

# XXX: make these imports explicit
from RFC822MessagesTools import *
from DateTime import DateTime

#============================
#   SPECIAL WebMailTool
#============================

from interfaces.IWebMailTool import WebMailToolInterface
from IMAPProperties import IMAPProperties
from WebMailSession import WebMailSession

import OFS # sendMail method need this
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import setDefaultRoles


#==========================
#    ZOPE PERMISSIONS
#==========================

#
# For the moment permissions in CPS
# are stored by hand with ZMI
#

UseWebMailPermission = "Use WebMail"
setDefaultRoles(UseWebMailPermission, ('Manager', 'Member'))

class WebMailTool(UniqueObject, Folder, IMAPProperties, WebMailSession):
    """ NuxWebMail Product (Portal Tool)
    """
    # This class implents the NuxWebmail interface

    __implements__ = WebMailToolInterface

    id = "portal_webMail"
    meta_type = "Portal WebMail Tool"

    security  = ClassSecurityInfo()

    manage_options = Folder.manage_options

    _basic_properties = (
        {'id': 'title',  'type': 'string', 'mode':'w', 'label':'Title'},
        {'id': 'IMAPServer', 'type': 'string', 'mode':'w', 'label':'IMAPServer'},
        {'id': 'IMAPPort', 'type': 'string', 'mode':'w', 'label':'IMAPPort'},
        {'id': 'SMTPServer', 'type': 'string', 'mode':'w', 'label':'SMTPServer'},
        {'id': 'SMTPPort', 'type': 'string', 'mode':'w', 'label':'SMTPPort'},
        {'id': 'Addressbook_name', 'type': 'string', 'mode':'w', 'label':'Addressbook_name'},
        {'id': 'AddressbookEmailProp', 'type': 'string', 'mode':'w', 'label':'AddressbookEmailProp'},
        {'id': 'PrivAddressbook_name', 'type': 'string', 'mode':'w', 'label':'PrivAddressbook_name'},
        {'id': 'PrivAddressbookEmailProp', 'type': 'string', 'mode':'w', 'label':'PrivAddressbookEmailProp'},
        {'id': 'Mailing_list_name', 'type': 'string', 'mode':'w', 'label':'Mailing_list_name'},
        {'id': 'MailingEmailsProp', 'type': 'string', 'mode':'w', 'label':'MailingEmailsProp'},
    )

    _properties = _basic_properties

    # For smooth upgrading:
    PrivAddressbook_name = ".addressbook"
    PrivAddressbookEmailProp = "email"

    def __init__(self):
        """WebMail Tool Constructor"""
        #
        # Default Properties Values
        #
        self.IMAPServer               = "localhost"
        self.IMAPPort                 = "143"
        self.SMTPServer               = "localhost"
        self.SMTPPort                 = "25"
        self.Addressbook_name         = "addressbook"
        self.AddressbookEmailProp     = "email"
        self.PrivAddressbook_name     = ".addressbook"
        self.PrivAddressbookEmailProp = "email"
        self.Mailing_list_name        = "mailinglists"
        self.MailingEmailsProp        = "emails"

    security.declareProtected(UseWebMailPermission, "getVersion")
    def getVersion(self):
        """Return the current version"""
        return __version__

    security.declareProtected(UseWebMailPermission, "getIMAPServer")
    def getIMAPServer(self):
        """Return the IMAP server name"""
        return self.IMAPServer

    security.declareProtected(UseWebMailPermission, "getIMAPPort")
    def getIMAPPort(self):
        """Return the IMAP server port"""
        return self.IMAPPort

    security.declareProtected(UseWebMailPermission, "getSMTPServer")
    def getSMTPServer(self):
        """Return the SMTP server name"""
        return self.SMTPServer

    security.declareProtected(UseWebMailPermission, "getSMTPPort")
    def getSMTPPort(self):
        """Return the SMTP server port"""
        return self.SMTPPort

    security.declareProtected(UseWebMailPermission, "getAddressBookName")
    def getAddressBookName(self):
        """Return the private addressbook name"""
        return self.Addressbook_name

    security.declareProtected(UseWebMailPermission, "getAddressBookEmailProperty")
    def getAddressBookEmailProperty(self):
        """Return the property for use in addressbook"""
        return self.AddressbookEmailProp

    security.declareProtected(UseWebMailPermission, "getPrivAddressBookName")
    def getPrivAddressBookName(self):
        """Return the private addressbook name"""
        return self.PrivAddressbook_name

    security.declareProtected(UseWebMailPermission, "getPrivAddressBookEmailProperty")
    def getPrivAddressBookEmailProperty(self):
        """Return the property for use in private addressbook"""
        return self.PrivAddressbookEmailProp

    security.declareProtected(UseWebMailPermission, "getMailingListName")
    def getMailingListName(self):
        """Return the property for use in mailinglist"""
        return self.Mailing_list_name

    security.declareProtected(UseWebMailPermission, "getMailingListsEmailProperty")
    def getMailingListsEmailProperty(self):
        """Return the property for use in mailinglists"""
        return self.MailingEmailsProp

    # XXX Hack du jeudi, soucis !
    security.declareProtected(UseWebMailPermission, "getConnection")
    def getConnection(self):
        con = IMAPGateway()
        con.connect(self, server=self.getIMAPServer(), port=self.getIMAPPort())
        login = self.getIMAPLogin()
        password = self.getIMAPPassword()
        if login == '':
            login = None
        if password == '':
            password = None
        if not login or not password:
            res = 'LOG_FAILED'
        else:
            res = con.login(login, password)
        if res == 'LOG_FAILED':
            raise 'Incorrect login or password'
        return con

    # XXX Hack du jeudi, ennuis !
    security.declareProtected(UseWebMailPermission, "verifyConnection")
    def verifyConnection(self):
        try:
            self.getConnection()
        except:
            return None
        return 1

    #===========================
    #    IMAP FUNCTIONS
    #===========================

    security.declareProtected(UseWebMailPermission, "getImapName")
    def getImapName(self, REQUEST=None):
        """Return the inbox folder name"""
        if REQUEST is not None and REQUEST.has_key('IMAPName'):
            return REQUEST['IMAPName']
        elif REQUEST is not None and REQUEST.SESSION.has_key('vm_session'):
            return REQUEST.SESSION.get('vm_session')['IMAPName']
        else:
            return 'INBOX'

    security.declareProtected(UseWebMailPermission, "setSortMail")
    def setSortMail(self, value, REQUEST=None, RESPONSE=None):
        """For compatibility with the orginal WebMail"""
        # Used in IMAP libs
        #
        pass

    security.declareProtected(UseWebMailPermission, "getMessage")
    def getMessage(self, IMAPName="INBOX", IMAPId=""):
        """Return the Message instance"""
        try:
            folder = self.getFolder(IMAPName)
            if not folder:
                folder = self.getFolder('INBOX')
                IMAPName = "INBOX"
            message = folder.getIMAPMessage(IMAPId)
        except:
            return 1

        if message != "DELETED":
            return message
        else:
            return 1

    security.declareProtected(UseWebMailPermission, "createIMAPFolder")
    def createIMAPFolder(self, title, folder):
        """Create a new Folder on IMAP Server"""
        con = self.getConnection()

        res_create = ''
        if title != '':
            folder = str(folder)
            if folder == 'INBOX':
                res_create = con.createFolder(title)
            elif folder.startswith('INBOX.'):
                folder = folder[6:]
                res_create = con.createFolder(folder+'.'+title)
            else:
                res_create = con.createFolder(folder+'.'+title)
        else:
            res_create = "NO"

        con.logout()

        if res_create != "NO":
            # Creation sucessfull
            return 0
        else:
            # Creation failed
            return 1

    security.declareProtected(UseWebMailPermission, "deleteIMAPFolders")
    def deleteIMAPFolders(self, IMAPNames, parentFolder=None):
        """Delete an IMAP Folder"""
        con = self.getConnection()

        for folder_name in IMAPNames:
            folder = self.getFolder(folder_name)
            messages_headers = folder.getIMAPMessagesHeaders(start=0, sortmail="date", listing_size = 999)
            imap_ids = [x['imap_id'] for x in messages_headers]

            folder_title = folder_name.split('.')[-1]
            if parentFolder is None:
                parentFolder = folder.getWebMail().getTrashFolder().getImapName()
            res_create = self.createIMAPFolder(folder_title, parentFolder)
            subfolders = folder.getIMAPDirectSubFolders()
            subfolders_names = [x.getImapName() for x in subfolders]
            if res_create == 0:
                # creation successfull : moving messages in that folder in trash box
                folder_new_name = parentFolder+'.'+folder_title
                folder.moveIMAPMessages(folderdest=folder_new_name, imapids=imap_ids, copy=1)
                self.deleteIMAPFolders(subfolders_names, parentFolder = folder_new_name)
            else:
                # creation unsuccessfull : moving messages directly to trash box
                folder.moveIMAPMessages(folderdest="deleting", imapids=imap_ids, copy=1)
                self.deleteIMAPFolders(subfolders_names)
            con.deleteFolder(wmail=self, name=folder_name)
        con.logout()
        return 0

    security.declareProtected(UseWebMailPermission, "emptyTrash")
    def emptyTrash(self):
        """Empty Trash"""
        con = self.getConnection()
        con.selectFolder(self.getTrashFolder().getImapName())
        res = con.connection.uid('SEARCH', 'ALL')
        list_res = map(int, string.split(res[-1][-1]))

        for IMAPId in list_res:
            con.setFlag(IMAPId = IMAPId, flag = "delete")

        con.expunge()
        con.logout()

        return 0

    security.declareProtected(UseWebMailPermission, "searchMail")
    def searchMail(self, REQUEST):
        """Send search request on IMAP Server"""
        # Not yet necessary
        flagged = "no"

        search_since_boolean = REQUEST.get('search_since_boolean', 0)
        if search_since_boolean:
            search_since_date = "%s-%s-%s" % (REQUEST.search_since_day,
                                              REQUEST.search_since_month,
                                              REQUEST.search_since_year)
        search_before_boolean = REQUEST.get('search_before_boolean', 0)
        if search_before_boolean:
            search_before_date = "%s-%s-%s" % (REQUEST.search_before_day,
                                               REQUEST.search_before_month,
                                               REQUEST.search_before_year)
        search_body = self.searchMailDummy(REQUEST.search_body)
        search_subject= self.searchMailDummy(REQUEST.search_subject)
        search_from = self.searchMailDummy(REQUEST.search_from)
        search_to = self.searchMailDummy(REQUEST.search_to)

        sortmail_list = ["search",]
        if search_body != "zz20":
            sortmail_list.extend(["BODY", search_body,])
        if search_subject != "zz20":
            sortmail_list.extend(["SUBJECT", search_subject,])
        if search_from != "zz20":
            sortmail_list.extend(["FROM", search_from,])
        if search_to != "zz20":
            sortmail_list.extend(["TO", search_to,])
        if len(sortmail_list) == 1:
            sortmail_list.extend(["BODY", search_body,])
        if search_since_boolean and search_before_boolean:
            if search_since_date == search_before_date:
                sortmail_list.extend(["ON", search_since_date,])
            else:
                # XXX AT: this doesn't work : the BEFORE will be ignored
                # as it is not possible to get the mails between 2 dates
                # in IMAP queries (not sure at all but looks like it)
                sortmail_list.extend(["SINCE", search_since_date,])
                sortmail_list.extend(["BEFORE", search_before_date,])
        else:
            if search_since_boolean:
                sortmail_list.extend(["SINCE", search_since_date,])
            elif search_before_boolean:
                sortmail_list.extend(["BEFORE", search_before_date,])
            else:
                sortmail_list.extend(["SINCE", "1-Jan-1980",])

        sortmail_list.append(flagged)
        sortmail_list.extend(["sort", "DATE",])

        sortmail = 'x2jq'.join(sortmail_list)

        if (int(REQUEST.search_since_year) > 1970 and int(REQUEST.search_since_day) >= 1 and int(REQUEST.search_since_day) <= 31) or (int(REQUEST.search_before_year) > 1970 and int(REQUEST.search_before_day) >= 1 and int(REQUEST.search_before_day) <= 31):
            # Search line OK
            return sortmail
        else:
            # Error in date (must be > 1970)
            return 1

    security.declareProtected(UseWebMailPermission, "searchMailDummy")
    def searchMailDummy(self, arg):
        arg = arg.replace("&", " ")
        arg = arg.replace('"', " ")
        arg = arg.replace(";", " ")
        if len(arg) < 1:
            arg = " "
        arg = string.replace(arg, " ", "zz20")
        return arg

    security.declareProtected(UseWebMailPermission, "getFolder")
    def getFolder(self, IMAPName):
        """Return a Folder instance"""
        for f in self.getIMAPFolders():
            if IMAPName == f.getImapName():
                return f

    security.declareProtected(UseWebMailPermission, "getInboxFolder")
    def getInboxFolder(self, REQUEST):
        """Return the Inbox folder id"""
        return IMAPFolder(
            self.getInboxIMAPName(REQUEST), self.getInboxRdName(), self)

    security.declareProtected(UseWebMailPermission, "getDraftFolder")
    def getDraftFolder(self):
        """Return the Draft folder id"""
        return IMAPFolder(
            self.getDraftIMAPName(), self.getDraftRdName(), self)

    security.declareProtected(UseWebMailPermission, "getSentMailFolder")
    def getSentMailFolder(self):
        """Return the Sent Mail folder id"""
        return IMAPFolder(
            self.getSentMailIMAPName(), self.getSentMailRdName(), self)

    security.declareProtected(UseWebMailPermission, "getTrashFolder")
    def getTrashFolder(self):
        """Return the Trash folder id"""
        return IMAPFolder(self.getTrashIMAPName(),
                                            self.getTrashRdName(),
                                            self)

    security.declareProtected(UseWebMailPermission, "getInboxRdName")
    def getInboxRdName(self):
        """Return readable name for Inbox"""
        return self.getDefaultFoldersNames()['Inbox'][1]

    security.declareProtected(UseWebMailPermission, "getInboxIMAPName")
    def getInboxIMAPName(self, REQUEST):
        """Return IMAP name for inbox folder"""
        return self.getImapName(REQUEST)

    security.declareProtected(UseWebMailPermission, "getSentMailRdName")
    def getSentMailRdName(self):
        """Return readable name for sent mail folder"""
        return self.getDefaultFoldersNames()['Sent'][1]

    security.declareProtected(UseWebMailPermission, "getSentMailIMAPName")
    def getSentMailIMAPName(self):
        """Return IMAP name for Sent Mail folder"""
        return self.getDefaultFoldersNames()['Sent'][0]

    security.declareProtected(UseWebMailPermission, "getDraftRdName")
    def getDraftRdName(self):
        """Return IMAP name for Sent Mail Folder"""
        return self.getDefaultFoldersNames()['Drafts'][1]

    security.declareProtected(UseWebMailPermission, "getDraftIMAPName")
    def getDraftIMAPName(self):
        """Return IMAP Name for Draft Folder"""
        return self.getDefaultFoldersNames()['Drafts'][0]

    security.declareProtected(UseWebMailPermission, "getTrashRdName")
    def getTrashRdName(self):
        """Return Readble name for Trash Folder"""
        return self.getDefaultFoldersNames()['Trash'][1]

    security.declareProtected(UseWebMailPermission, "getTrashIMAPName")
    def getTrashIMAPName(self):
        """Return the IMAP Trash Folder Name"""
        return self.getDefaultFoldersNames()['Trash'][0]

    security.declareProtected(UseWebMailPermission, "getIMAPFolders")
    def getIMAPFolders(self):
        """Return IMAP Folders List"""
        con = self.getConnection()

        imap_mailboxes = con.listFolders()
        imap_mailboxes.sort()
        res = []

        default_folders = self.getDefaultFoldersNames()
        defaults_map = {}
        for i in default_folders.values():
            defaults_map[i[0]] = i[1]

        for item in imap_mailboxes:
            readable_name = item

            if string.find(item, "&") != -1:
                readable_name = readable_name.replace("&AOk-", "é")
                readable_name = readable_name.replace("&AOA-", "à")
                readable_name = readable_name.replace("&AOI-", "â")
                readable_name = readable_name.replace("&AOg-", "è")
                readable_name = readable_name.replace("&-", "&")
                readable_name = readable_name.replace("&AOc-", "ç")
                readable_name = readable_name.replace("&APk-", "ù")
                readable_name = readable_name.replace("&AOo-", "ê")
                readable_name = readable_name.replace("&AOs-", "ë")
                readable_name = readable_name.replace("&AO4-", "î")
                readable_name = readable_name.replace("&APQ-", "ô")
                readable_name = readable_name.replace("&APM-", "ó")
                readable_name = readable_name.replace("&APE-", "ñ")
                readable_name = readable_name.replace("&AOE-", "á")
                readable_name = readable_name.replace("&AMk-", "É")

            if defaults_map.has_key(readable_name):
                readable_name = defaults_map[readable_name]
            else:
                readable_name = readable_name.replace("INBOX.", "")

            readable_name = readable_name.split('.')[-1]
            res.append(IMAPFolder(item, readable_name, self))

        #
        # Create default IMAP Folders if necessary
        #
        if not self.getSentMailIMAPName() in imap_mailboxes:
            con.connection.create(self.getSentMailIMAPName())
            res.append(IMAPFolder(self.getSentMailIMAPName(),
                                  self.getSentMailIMAPName(),
                                  self))

        if not self.getDraftIMAPName() in imap_mailboxes:
            con.connection.create(self.getDraftIMAPName())
            res.append(IMAPFolder(self.getDraftIMAPName(),
                                  self.getDraftIMAPName(),
                                  self))

        if not self.getTrashIMAPName() in imap_mailboxes:
            con.connection.create(self.getTrashIMAPName())
            res.append(IMAPFolder(self.getTrashIMAPName(),
                                  self.getTrashIMAPName(),
                                  self))

        con.logout()
        return res

    security.declareProtected(UseWebMailPermission, "getIMAPFoldersTree")
    def getIMAPFoldersTree(self):
        """Return IMAP Folders List with depth"""
        imap_folders = self.getIMAPFolders()
        res = []
        prev_folder = ""
        for imap_folder in imap_folders:
            imap_folder_list = imap_folder.getImapName().split('.')
            res.append((imap_folder, len(imap_folder_list)-1))
        return res


    security.declareProtected(UseWebMailPermission, "getQuota")
    def getQuota(self):
        """Return % used quota on Mailbox"""
        con = self.getConnection()

        try:
            res = con.getQuota()
        except:
            res = -1

        con.logout()
        return res

    security.declareProtected(UseWebMailPermission, "deleteMessages")
    def deleteMessages(self, REQUEST):
        """Delete IMAP messages on mail server"""
        if not REQUEST.form.has_key('IMAPIds'):
            return 1

        IMAPIds = REQUEST.form['IMAPIds']

        #
        # one or many messages to delete
        #
        if type(IMAPIds) is type(''):
            IMAPIds = [IMAPIds]

        if REQUEST.form.has_key('IMAPName'):
            IMAPName = REQUEST.form['IMAPName']
        else:
            IMAPName = "INBOX"

        #
        # copy = 1 if moving message to trash
        #
        _copy = 1

        quota = self.getQuota()

        #
        # copy = 0 if delete message from trash or quota exceed for
        # moving to trash
        #
        if IMAPName == self.getTrashFolder().getImapName() or quota > 999:
            _copy = 0

        f = self.getFolder(IMAPName)
        f.moveIMAPMessages(folderdest="deleting", imapids=IMAPIds, copy=_copy)
        return 0

    security.declareProtected(UseWebMailPermission, "moveMessages")
    def moveMessages(self, REQUEST):
        """Move messages from one IMAP folder to another one"""
        mail_session = REQUEST.SESSION.get('vm_session', {})
        IMAPIDs = mail_session['IMAPId']
        IMAPName = mail_session['IMAPName']

        #
        # From the fetching interface or the view interface
        #
        move_to_folder = mail_session.get(
            'move_to_folder', REQUEST.move_to_folder)

        if type(IMAPIDs) is type(''):
            IMAPIDs = [IMAPIDs]

        f = self.getFolder(IMAPName)
        f.moveIMAPMessages(folderdest=move_to_folder, imapids=IMAPIDs)

        return 0

    security.declareProtected(UseWebMailPermission, "getPreviousAndNextMessagesIds")
    def getPreviousAndNextMessagesIds(self, folderName, sortmail, IMAPId):
        """Return next IMAP id for sorted mails"""
        con = self.getConnection()
        res = con.getPreviousAndNextMessagesIds(folderName=folderName,
                                                sortmail=sortmail,
                                                IMAPId=IMAPId)
        con.logout()
        return res

    security.declareProtected(UseWebMailPermission, "saveDraft")
    def saveDraft(self, REQUEST):
        """Save Message in Draft Folder"""
        mail_structure = REQUEST.SESSION.get('mail_session')
        att_list = []

        _to = [mail_structure['to']]
        _cc = [mail_structure['cc']]
        _bcc = [mail_structure['bcc']]
        _headers = {'subject': mail_structure['subject']}
        att_list = mail_structure['att_list']

        message = IMAPMessage.IMAPMessage(
            sender=(self.getIdentity(), self.getMailFrom()),
            subject=mail_structure['subject'],
            date=DateTime().strftime('%d/%m/%Y %H:%M'),
            body=mail_structure['body'],
            recipients={'to': _to, 'cc': _cc, 'bcc': _bcc},
            attachments=att_list,
            headers=_headers)

        message.headers['date'] = self.ZopeTime().rfc822()
        raw_message = message.raw_message(0).replace("\n", "\r\n")

        draft_folder = self.getDraftFolder().getImapName()

        con = self.getConnection()
        con.writeMessage(draft_folder, raw_message)

        con.logout()

    #
    # Sending mail
    #
    security.declareProtected(UseWebMailPermission, "addPiece")
    def addPiece(self, REQUEST):
        """Add a piece in mail session object"""
        attKey = "attachment"
        #
        # Creation of an instance of Attachment
        #
        if REQUEST.has_key(attKey):
            if type(REQUEST[attKey]) is not type('') and REQUEST[attKey].filename:
                att = REQUEST[attKey]
                filename = os.path.split(att.filename)[1]
                data = att.read()
                content_type = OFS.content_types.guess_content_type(
                    name=filename, body=data,
                    default='application/octet-stream')[0]
                #
                # Modifications of the session object
                #
                mail = REQUEST.SESSION.get('mail_session', {})
                mail['nb_att'] += 1
                mail['att_list'].append(
                    Attachment.Attachment(id=str(mail['nb_att']),
                        filename=filename, content_type=content_type,
                        size=len(data), data=data))
                #
                # Commit modifications on session object
                #
                REQUEST.SESSION['mail_session'] = mail

    security.declareProtected(UseWebMailPermission, "removeOnePieces")
    def removeOnePieces(self, REQUEST):
        """Remove a piece from the session object"""
        mail_structure = REQUEST.SESSION.get('mail_session', {})
        att_list = mail_structure['att_list']

        l = []
        for piece in att_list:
            if piece.getId() != REQUEST['idpiece']:
                l.append(piece)
                i = 1
                for piece in l:
                    piece.setId(i)
                    i = i + 1

        #
        # commit of modifications
        #
        mail_structure['att_list'] = l
        mail_structure['nb_att'] = mail_structure['nb_att'] - 1
        REQUEST.SESSION['mail_session'] = mail_structure

    security.declareProtected(UseWebMailPermission, "removeSelectedPieces")
    def removeSelectedPieces(self, REQUEST):
        """Remove a piece from the session object"""
        mail_structure = REQUEST.SESSION.get('mail_session', {})
        att_list = mail_structure['att_list']

        pieces_to_remove = REQUEST.form.get('IDPieces', [])

        l = []
        # If nothing selected
        for item in pieces_to_remove:
            l = []
            for piece in att_list:
                if piece.getId() != item:
                    l.append(piece)
                    i = 1
                    for piece in l:
                        piece.setId(i)
                        i = i + 1

        # Commit modifications
        mail_structure['att_list'] = l
        mail_structure['nb_att'] = mail_structure['nb_att'] - 1
        REQUEST.SESSION['mail_session'] = mail_structure

        return 0

    security.declareProtected(UseWebMailPermission, "removeAllPieces")
    def removeAllPieces(self, REQUEST):
        """Remove all pieces from the current session object"""
        mail_structure = REQUEST.SESSION.get('mail_session',{})
        mail_structure['att_list'] = []
        mail_structure['nb_att'] = 0
        REQUEST.SESSION['mail_session'] = mail_structure

        return 0

    security.declareProtected(UseWebMailPermission, "sendMail")
    def sendMail(self, REQUEST, flag):
        """Send a mail from the compose interface"""

        mail_structure = REQUEST.SESSION.get('mail_session', {})

        _to = [mail_structure['to']]
        _cc = [mail_structure['cc']]
        _bcc = [mail_structure['bcc']]

        if not mail_structure.has_key('att_list'):
            mail_structure['att_list'] = []

        # XXX: what do we do with this now?
        ImapName = REQUEST.get("INBOX", "IMAPName")
        st = '0'

        if REQUEST.has_key('start'):
            st = REQUEST['start']

        if mail_structure['to'] + mail_structure['cc'] + mail_structure['bcc'] == '':
            return 1

        #
        # Add the attchement from the original message when forward or send
        # from draft
        #
        if (REQUEST.has_key('IMAPName')
                and REQUEST.has_key('IMAPId')
                and REQUEST.has_key('forward')
            or REQUEST.has_key('IMAPName')
                and REQUEST['IMAPName'] == self.getDraftFolder().getImapName()
                and REQUEST.has_key('IMAPId')):
            pass
            # FIXME: neither attForward nor listAtt are used anywhere !!!
            #
            # attForward is the list of attachment id to be forwarded
            #
            #f = self.getFolder(REQUEST['IMAPName'])
            #m = f.getIMAPMessage(REQUEST['IMAPId'])
            #if REQUEST.has_key('forwarded_attachment'):
            #    for a in m.getAttachments():
            #        if str(a.getId()) in REQUEST['forwarded_attachment']:
            #            listAtt.append(a)

        if mail_structure['subject'] != '':
            subject_mail = mail_structure['subject']
        else:
            subject_mail = "[no subject]"

        _headers = {'subject': subject_mail, 'date': self.ZopeTime().rfc822()}

        flags = {}

        if REQUEST.form.get('a_reception', "") != "":
            flags['a_reception'] = 1

        if REQUEST.form.get('a_read', "") != "" :
            flags['a_read'] = 1

        message = IMAPMessage.IMAPMessage(
            flags=flags,
            sender=(self.getIdentity(), self.getMailFrom()),
            subject=subject_mail,
            date= DateTime().strftime('%d/%m/%Y %H:%M'),
            body= mail_structure['body'],
            recipients={'to': _to, 'cc':_cc, 'bcc':_bcc},
            attachments=mail_structure['att_list'],
            headers=_headers)

        raw_message = message.raw_message(flag)

        if self.getAutoSaveSentMessage() == "yes":
            #
            # Copy to sent-mail Folder on Server
            #
            raw_message = string.replace(raw_message, "\n", "\r\n")
            con = self.getConnection()
            con.writeMessage(folderName=self.getSentMailFolder().getImapName(),
                             raw_message=raw_message)
            con.logout()

        smtp_connection = smtplib.SMTP(self.getSMTPServer())
        _recipients = []
        for item in ['to', 'cc', 'bcc']:
            for address in message.recipients[item]:
                spl = ","
                if address.find(",") != -1:
                    spl = ","
                else:
                    spl = ";"
                for people in address.split(spl):
                    peop = people.strip()
                    if len(peop) > 2:
                        _recipients.append(peop)

        smtp_connection.sendmail(
            self.getIdentity() + ' <' + self.getMailFrom() + '>',
            _recipients, raw_message)
        smtp_connection.quit()

        if (REQUEST.has_key('IMAPName') and REQUEST.has_key('IMAPId')\
            and REQUEST.has_key('flag')):
            con = self.getConnection()
            flag2 = REQUEST.get('flag')
            if flag2 == 'reply':
                con.setFlag(folderName=REQUEST['IMAPName'],
                            IMAPId=REQUEST['IMAPId'], flag="anwser")
            elif flag2 == 'forward':
                con.setFlag(folderName=REQUEST['IMAPName'],
                            IMAPId=REQUEST['IMAPId'], flag="forwarded")
            con.logout()

        return 0

    security.declareProtected(UseWebMailPermission, "sendReceptionAcc")
    def sendReceptionAcc(self, REQUEST):
        """Sending a mail: read flag"""
        mail_session = REQUEST.SESSION.get('vm_session', {})
        folder = IMAPFolder(mail_session.get('IMAPName', ""),
                            self.getInboxRdName(), self)
        message = folder.getIMAPMessage(mail_session.get('IMAPId', ""))

        #
        # Keeping the orignal mail information
        #
        exp_mail = message.getSenderMail()
        sub_mail = message.getSubject()

        current_time = time.strftime("%c", time.localtime())

        new_body = """\
        Voici le reçu de courrier que vous avez envoyé à %s le %s.
        Ce message vérifie que le message s'est affiché sur l'ordinateur du destinataire à %s.
        """ % (self.getMailFrom(), message.getDate(), current_time)

        _headers = {'subject': "Lu : " + sub_mail, 
                    'date': self.ZopeTime().rfc822()}
        #
        # Instance of the new message
        #
        new_message = IMAPMessage.IMAPMessage(
            sender=(self.getIdentity(),self.getMailFrom()),
            subject="Lu :",
            date=DateTime().strftime('%d/%m/%Y %H:%M'),
            body=new_body,
            recipients={'to': [exp_mail], 'cc': [], 'bcc': []},
            attachments=[],
            headers=_headers)

        raw_message = new_message.raw_message(flag="")
        _recipients = [exp_mail]
        #
        # SMTP Sending
        #
        smtp_connection = smtplib.SMTP(self.getSMTPServer())

        smtp_connection.sendmail(
            from_addr=self.getIdentity() + ' <' + self.getMailFrom() + '>',
            to_addrs=_recipients,
            msg=raw_message)
        smtp_connection.quit()

        return 0

    #=================================
    #      VIEW MESSAGE SECTION
    #=================================

    def __bobo_traverse__(self, REQUEST, name):
        """Redefined method for getting attachment name when downloading"""
        try:
            if hasattr(self, name) and not REQUEST.has_key('AttachId'):
                return getattr(self, name)
        except AttributeError:
            pass
        try:
            if REQUEST.has_key('AttachId'):
                return self.getAttachment
        except:
            pass

        REQUEST.RESPONSE.notFoundError("%s\n" % (name))

    security.declareProtected(UseWebMailPermission, "getAttachment")
    def getAttachment(self, IMAPId, AttachId=1, IMAPName="INBOX",
                      REQUEST=None, goback=1):
        """Return the attachment for downloading"""
        f = self.getFolder(IMAPName)
        m = f.getIMAPMessage(IMAPId)

        # If attachment not rfc822 (mail message) compliant
        if AttachId.find(".") == -1:
            for a in m.getAttachments():
                if a.getId() == int(AttachId):
                    return a.download(REQUEST, REQUEST.RESPONSE)
            if goback:
                return self.getMessage(IMAPName, IMAPId)
        # If attachment is rfc822 (mail message) type and contains attachments
        li = AttachId.split(".")

        # Attachment we want is in first level rfc822 maill attachment.
        # Li is [attachment level, attachment number from original level,
        # attachment number]
        if li[0] == "1":
            for a in m.getAttachments():
                if a.getId() == int(li[1]) + 1:
                    virtual_message = a.render_mail_attachment()
                    for a2 in virtual_message.getAttachments():
                        if a2.getId() == int(li[2]):
                            return a2.download(REQUEST, REQUEST.RESPONSE)

        # Attachment is in second level
        # Li is [attachment level, attachment number from original level,
        # attachment number from first level, attachment number]
        if li[0] == "2":
            for a in m.getAttachments():
                if a.getId() == int(li[1]) + 1:
                    virtual_message = a.render_mail_attachment()
                    for a2 in virtual_message.getAttachments():
                        if a2.getId() == int(li[2]) + 1:
                            virtual_message2 = a2.render_mail_attachment()
                            for a3 in virtual_message2.getAttachments():
                                if a3.getId() == int(li[3]):
                                    return a3.download(REQUEST, REQUEST.RESPONSE)

    security.declareProtected(UseWebMailPermission, "rangeView")
    def rangeView(self, start="0", folder_id=None, num_messages=1):
        """Return a href link for choosing a range of message"""
        menu = ""
        start = int(start)
        folder_id = quote(folder_id)
        listingSize = int(self.getListingSize())
        num_messages = int(num_messages)

        k = 1
        inf = 1
        sup = (10 * listingSize) - 2

        index = 1
        index2 = 1
        stop = 0

        while index < num_messages and not stop:
            if inf <= start and start < sup:
                k = index2
                stop = 1
            else:
                inf = inf + (10 * listingSize)
                sup = sup + (10 * listingSize)
                index2 = index2 + 1
                index = index + (10 * listingSize)

        i1 = k
        k = (k * 10) - 9
        i = 1 + (10 * listingSize) * (i1 - 1)
        j = 1

        if start > 2:
            prev = start - listingSize
            menu = menu + \
                "<a href='webmail_show?IMAPName=%s&start=%d'>%s</a>" \
                % (folder_id, prev, "&nbsp;<img src='previous.gif' width='6' height='10'>&nbsp;")

        while (i < (num_messages + start - 1)):
            if j < 11 and i <= num_messages:
                if i == start or i == (start + 1):
                    menu = menu + \
                        "<a href='webmail_show?IMAPName=%s&start=%d'>%s</a>"\
                    % (folder_id, i - 1, "")
                else:
                    menu = menu + \
                        "<a href='webmail_show?IMAPName=%s&start=%d'>%s</a>"\
                    % (folder_id, i - 1, "")
                    k = k + 1
                    i = i + listingSize
                    j = j + 1
            else:
                break

            sup = num_messages / listingSize

            if start >= (sup * listingSize):
                return menu
            else:
                next = start + listingSize
                menu += "<a href='webmail_show?IMAPName=%s&start=%d'>%s</a>" \
                    % (folder_id, next,
                        "&nbsp;<img src='next.gif' width='10' height='10'>&nbsp;")

            return menu


    #========================
    #      ADDRESSBOOK
    #========================

    security.declareProtected(UseWebMailPermission, "addressbookGroupDelete")
    def addressbookGroupDelete(self, addressbook, REQUEST):
        """Delete a group of contacts from the addressbook"""
        list_to_delete = REQUEST.form.get('to_delete', [])
        for entry_id in list_to_delete:
            addressbook.deleteEntry(entry_id)

    security.declareProtected(UseWebMailPermission, "deleteAllEntries")
    def deleteAllEntries(self, addressbook):
        """Delete all addressbook entries

        Used when a user choose to import an MSF**k**g Outlook addressbook and
        delete the old entries."""
        res = addressbook.searchEntry()
        for entry in res:
            entry_id = entry[addressbook.entry_prop]
            addressbook.deleteEntry(entry_id)

    security.declareProtected(UseWebMailPermission, "importMSOaddressbook")
    def importMSOaddressbook(self, addressbook, file):
        """Import the MS Outlook Addressbook into the NuxWebMail"""

        # Parsing the MsOutlook file
        if type(file) != type(''):
            # Cause if wrong file
            importer = MSOutlookImporter(file)
            contacts = importer.getContacts()
            for contact in contacts:
                p = addressbook.getEntry(contact['email'])
                if p is None and contact['email'] != "":
                    addressbook.createEntry(
                        {addressbook.entry_prop: contact['email'],
                         'name': contact['name'],
                         'givenName': contact['vorname'],
                         'email': contact['email']})
            return 0
        else:
            return 1

    security.declareProtected(UseWebMailPermission, "setListSearch")
    def setListSearch(self, list, id_list, REQUEST):
        """Init of a session object with the list of emails"""

        # Destruction of an older session if exists
        REQUEST.SESSION['search_results'] = ()

        email_prop = self.getMailingListsEmailProperty()
        entry = list.getEntry(id_list)

        # Update Search Session
        if entry:
            REQUEST.SESSION['search_results'] = entry[email_prop]

    def getCurrentAddressBookName(self, addressbook_name='', REQUEST=None):
        """Get the ID of the addressbook in request"""
        if not addressbook_name:
            addressbook_name = REQUEST.get('addressbook_name', None)
        if addressbook_name  == '_private':
            bookname = self.getPrivAddressBookName()
        else:
            bookname = self.getAddressBookName()
        return bookname

    def getCurrentAddressBook(self, addressbook_name='', REQUEST=None):
        # This method is only called from the CPS3 scripts, so I will
        # completely ignore any CPS2 support here. Beware!
        # Find the global adressbook:
        dtool = getToolByName(self, 'portal_directories')
        bookid = self.getCurrentAddressBookName(addressbook_name, REQUEST)
        return dtool[bookid]

    security.declareProtected(UseWebMailPermission, "addressBookSearch")
    def addressBookSearch(self, addressbook='', REQUEST=None):
        book = self.getCurrentAddressBook(addressbook, REQUEST)
        res = book.listEntryIds()
        return res

    def getAddressBookEntry(self, entryid, addressbook='', REQUEST=None):
        book = self.getCurrentAddressBook(addressbook, REQUEST)
        return book.getEntry(entryid)


InitializeClass(WebMailTool)
