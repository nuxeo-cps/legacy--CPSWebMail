# -*- coding: iso-8859-15 -*-
######################################################################
#
# IMAPFolder, manage IMAP Folders for Webmail product
#
# This software is governed by a license. See 
# LICENSE.txt for the terms of this license.
#
# Developped by: Université de Savoie, France (http://www.univ-savoie.fr)
# Main developper : Maxime RAFFIN (ticeuds@chez.com)
# Team : Benoit CHARLES, Steve GIRAUD, Eric BRUN
# Thanks to : Bernard CARON, Christian MARTEL
#
######################################################################
#
# Copyright (c) 2004 Nuxeo SARL <http://www.nuxeo.com>
# See LICENSE.TXT for licensing information
#
######################################################################
# $ Id: $

from IMAPMessage import *
import IMAPGateway
import RFC822MessagesTools
from DateTime import DateTime

class IMAPFolder:
    """ Implemetation of the IMAP MailBox
    """

    def __init__(self,
                 IMAPName,
                 readableName,
                 webMail,
                 type='INBOX'):
        """ constructor
        """
        self.IMAPName = IMAPName
        self.readableName = readableName
        self.type = type
        self.webMail = webMail

    def getImapName(self):
        """ return the imap name
        """
        return self.IMAPName

    def getReadableName(self):
        """ return the readable name
        """
        return self.readableName

    def getWebMail(self):
        """ return WebMail instance
        """
        return self.webMail

    def moveIMAPMessages(self, folderdest, imapids, copy=1):
        """ move the message imapid to the dolderdest folder
        """
        if folderdest == "deleting":
            # move message to trash
            _folderNameDest = self.getWebMail().getTrashFolder().getImapName()
        else:
            # move message to folder folderdest
            _folderNameDest = folderdest

        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())

        if not copy:
            # delete trash message, no copy to another folder
            con.selectFolder(self.getImapName())

        res = 0
        for IMAPId in imapids:
            if copy:
                # move message to folder _folderNameDest
                res = con.copy(folderNameSrc = self.getImapName(),
                               folderNameDest = _folderNameDest,
                               IMAPId = IMAPId)
            else:
                res = 1

            if res == 1 or (res == 2 and folderdest == "deleting"):
                # if copy is sucessfull or we want delete message when quota is over, we delete message
                con.setFlag(IMAPId = IMAPId, flag = "delete")

        con.expunge()
        con.logout()

    def getNumberOfIMAPMessage(self, REQUEST=None):
        """ return the number of mail in this mailbox
        """
        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())
        sortmail = self.getWebMail().getSortMail(REQUEST)

        if string.find(sortmail, "search") != (-1):
            #number of messages from a search in one folder
            res = con.getNumberOfMessage(self.getImapName(), search = sortmail)
        else:
            #number of messages in the folder
            res = con.getNumberOfMessage(self.getImapName())
        con.logout()

        return res

    def getNumberOfUnreadIMAPMessage(self, REQUEST=None):
        """ return the number of not read mails in this mailbox
        """
        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())
        res = con.getNumberOfUnreadMessage(self.getImapName())
        con.logout()

        return res

    def getIMAPMessagesHeaders(self, sortmail="", sort="date", order='desc', start=1, end=0, listing_size=0, REQUEST=None, RESPONSE=None):
        """ return the liste of headers
            between start and end
            or between start and start + listingsize
            with the sort sort sortmail
        """
        parsed_res = []

        self.getWebMail().setSortMail(sortmail, REQUEST,RESPONSE)

        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())
        res = con.listMessagesHeaders(folderName = self.getImapName(),
                                      sortmail = self.getWebMail().getSortMail(REQUEST),
                                      start = start,
                                      end = end,
                                      listing_size = listing_size)
        con.logout()
        for header in res:
            parsed_res.append(
                RFC822MessagesTools.parse_RFCHeaders(
                    header,
                   self.getWebMail().getNbCharSubject()
                )
            )

        sorted_keys = []
        sorted_parsed_res = []

        # sort available on date, subject, and from
        # XXX sort is only made on the messages displayed, not on all
        # the messages in the given imap folder
        if sort not in ["date", "subject", "from"]:
            sort = "date"

        def makeDateTime(datetime):
            # datetime = '%d/%m/%y %H:%M'
            try:
                datetime2 = datetime.split(' ')
                dmy = datetime2[0].split('/')
                day = int(dmy[0])
                month = int(dmy[1])
                year = int(dmy[2])
                hm = datetime2[1].split(':')
                hour = int(hm[0])
                minutes = int(hm[1])
                res = DateTime(year, month, day, hour, minutes)
            except ValueError, IndexError:
                res = DateTime(datetime)
            return res

        if sort == "date":
            # second criteria: subject
            sorted_keys = [(makeDateTime(x['date']), x['subject'], x) for x in parsed_res]
        elif sort == "subject":
            # second_criteria: date
            sorted_keys = [(x['subject'], makeDateTime(x['date']), x) for x in parsed_res]
        elif sort == "from":
            # second_criteria: date
            # compatibility with what is displayed in webmail_fetch
            if sortmail == 'FROM':
                sorted_keys = [(x['mail_sender'], makeDateTime(x['date']), x) for x in parsed_res]
            else:
                sorted_keys = [(x['sender'], makeDateTime(x['date']), x) for x in parsed_res]

        sorted_keys.sort()
        sorted_parsed_res = [x[2] for x in sorted_keys]

        # order
        if order == 'desc':
            sorted_parsed_res.reverse()

        return sorted_parsed_res

    def getIMAPMessage(self, imapid="", is_draft=0):
        """ return the message from its imapid
        """
        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())

        res, direct_body, flags = con.getMessage(folderName = self.getImapName(),
                                                 IMAPId = imapid)
        con.logout()

        imap_message = RFC822MessagesTools.parse_RFCMessage(
                           mess = res,
                           direct_body = direct_body,
                           flags = flags,
                           imapid = imapid,
                           is_draft = is_draft)

        return imap_message

    def getRawIMAPMessage(self,imapid):
        """ return the message without parsing
        """
        con = IMAPGateway.IMAPGateway()
        con.connect(self.getWebMail(),
                    server = self.getWebMail().getIMAPServer(),
                    port = self.getWebMail().getIMAPPort())
        con.login(self.getWebMail().getIMAPLogin(),
                  self.getWebMail().getIMAPPassword())
        res, direct_body, flags = con.getMessage(folderName = self.getImapName(),
                                                 IMAPId = imapid)
        con.logout()
        return res

    def getIMAPSubFolders(self):
        """ return the IMAP subfolders
        """
        wmtool = self.getWebMail()
        folders = wmtool.getIMAPFolders()
        res = []
        name = self.getImapName()
        for folder in folders:
            fname = folder.getImapName()
            if fname.startswith(name) and fname != name:
                res.append(folder)
        return res

    def getIMAPDirectSubFolders(self):
        """ return the IMAP subfolders
        """
        wmtool = self.getWebMail()
        folders = wmtool.getIMAPFolders()
        res = []
        name = self.getImapName()
        dots = len(name.split('.'))
        for folder in folders:
            fname = folder.getImapName()
            fdots = len(fname.split('.'))
            if fname.startswith(name) and fname != name and fdots == (dots+1):
                res.append(folder)
        return res

    def getType(self):
        """ return the type of this folder
        """

    def emptyTrash(self):
        """ delete all the message of this folder
            if this folder'stype is trash
        """

