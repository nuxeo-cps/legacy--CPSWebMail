#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# Julien Anguenot <mailto:ja@nuxeo.com>
# See LICENSE.TXT for licensing information 
#

# Last update 2002/09/06 : JA

__version__ ="0.1"

"""
WebMailSessionInterface 
"""

from Interface import Base

class WebMailSessionInterface(Base):
    """An Interface for the WebMailSession class """
    
    def beginMailSession(self, REQUEST):
        """Begin a New Mail Session"""
        
    def createMailSession(self, REQUEST):
        """Stock a new mail session"""

    def createReplySession(self, REQUEST, all=0):
        """Create a new mail session of reply"""

    def createForwardSession(self, REQUEST):
        """Create a new mail session for forwarding"""
    
    def saveMailSession(self, REQUEST):
        """Save a mail_session_composer"""

    def createDraftSession(self, IMAPId, IMAPName, REQUEST):
        """Create a draft session"""

    def endMailSession(self, REQUEST):
        """Erase current session object"""

    def createViewSession(self, REQUEST):
        """Initialize a new view message session"""

    def initGroupMailSession(self, REQUEST):
        """Init of a grouping mail sending"""

    def setSearchSession(self, addressbook, REQUEST):
        """Init of search result session"""

    def setIndexSearchSession(self, addressbook, begin, REQUEST):
        """Set a search session for an index"""
