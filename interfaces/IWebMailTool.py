#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# Julien Anguenot <mailto:ja@nuxeo.com>
# See LICENSE.TXT for licensing information 
#

"""
WebMailToolInterface 
"""

from Interface import Base

class WebMailToolInterface(Base):
    """An Interface for the WebMailTool class """

    def getVersion(self):
        """Return the current version"""
        
    #
    # IMAP FUNCTIONS         
    #
    def getImapName(self, REQUEST=None):                            
        """Return the inbox Folder name"""

    def setSortMail(self, value, REQUEST=None, RESPONSE=None):
        """For compatibility with the orginal WebMail"""

    def getMessage(self, IMAPName="INBOX", IMAPId=""):
        """Return the message instance"""

    def createIMAPFolder(self, title, folder):
        """Create a new Folder on IMAP Server"""

    def deleteIMAPFolders(self, pIMAPNamesToDelete):
        """Delete an IMAP Folder"""

    def emptyTrash(self, pIMAPName):
        """Empty trash"""

    def searchMail(self, REQUEST):
        """Send search request on IMAP server"""

    def getFolder(self, IMAPName):
        """Return a Folder instance"""

    def getInboxFolder(self):
        """Return the inbox folder Id"""

    def getDraftFolder(self):
        """Return the draft folder Id"""

    def getSentMailFolder(self):
        """Return the sent mail folder Id"""

    def getTrashFolder(self):
        """Return the Trash Folder Id """

    def getInboxRdName(self):
        """Return Readable Name for Inbox """

    def getInboxIMAPName(self, REQUEST):
        """Return IMAP name for inbox folder"""

    def getSentMailRdName(self):
        """Return redable name for sent mail folder """

    def getSentMailIMAPName(self):
        """Return IMAP name for Sent Mail Folder"""

    def getDraftRdName(self):
        """Return Readble Name for Draft Folder """

    def getDraftIMAPName(self):
        """Return IMAP Name for Draft Folder """

    def getTrashRdName(self):
        """Return Readble name for Trash Folder """

    def getTrashIMAPName(self):
        """Return the IMAP Trash Folder Name """

    def getIMAPFolders(self):
        """Return IMAP Folders List """

    def getQuota(self):
        """Return % Used Quota on Mailbox """

    def deleteMessages(self, REQUEST):
        """Delete IMAP Message on Mail Server"""
        
    def moveMessages(self, REQUEST):
        """Move Messages From IMAP Folder To Another One """

    def getPreviousAndNextMessagesIds(self, folderName, sortmail, IMAPId):
        """Return next IMAP id for sorted mails """
    
    def saveDraft(self, REQUEST):
        """Save Message in Draft Folder """
        
    #
    # MAIL SENDING
    #
    def addPiece(self, REQUEST):
        """Add a piece in mail session object"""

    def removeOnePiece(self, REQUEST):
        """Remove a piece from the session object"""

    def removeSelectedPieces(self, REQUEST):
        """Remove a piece from the session object"""

    def removeAllPieces(self, REQUEST):
        """Remove all pieces from the current session object"""
    
    def sendMail(self,to='',cc='',bcc='', subject='[pas de sujet]', body='',
                 redirection_url='edit_message', REQUEST=None):
        """Send a mail from the compose interface"""

    def sendReceptionAcc(self, IName, IMAPId, REQUEST):
        """Sending a mail : read flag"""
        
    #
    # VIEW MESSAGE SECTION
    #
    def __bobo_traverse__(self, REQUEST, name):
        """Redefined method for get attachment name when download"""

    def getAttachment(self, IMAPId, AttachId=1, IMAPName="INBOX", REQUEST=None,
                        goback=1):
        """Return the attachment for download"""

    def rangeView(self, start, folder_name, nb_messages):
        """Give the range for viewing message"""

    #
    # ADDRESSBOOK
    #
    def addressbookGroupDelete(self, addressbook, REQUEST):
        """Delete a group of contacts from the addressbook""" 

    def deleteAllEntries(self, addressbook):
         """Delete all addressbook entries

        Used when a user chooses to import an MS Outlook addressbook and
        delete the old entries.
        """
    def importMSOaddressbook(self, addressbook, file):
        """Import the MS Outlook addressbook into the NuxWebMail"""

