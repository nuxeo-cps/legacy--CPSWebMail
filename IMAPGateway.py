######################################################################
#
# IMAPGateway, api to IMAPLibLocal
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

import timeoutsocket

from IMAPMessage import *
import imapLibLocal
import string
import re

timeoutsocket.setDefaultSocketTimeout(10) # 10 seconds timeout on sockets

class IMAPGateway:
    """ IMAP gateway """



    def connect(self, webmail, server="", port=""):
        """ connect to IMAP server"""

        try:
            if port is not None and port != "":
                self.connection = imapLibLocal.IMAP4(server,int(port))
            else:
                self.connection = imapLibLocal.IMAP4(server)
        except:
            try:
                import time
                time.sleep(3)
                if port is not None and port != "":
                    self.connection = imapLibLocal.IMAP4(server,int(port))
                else:
                    self.connection = imapLibLocal.IMAP4(server)

            except:
                raise 'Connection failed'

    def login(self, login, password):
        """ login to IMAP server """

        res=self.connection.login(login, password)
        if res[0]!="OK":
            return "LOG_FAILED"
        try:
            self.connection.select()
        except:
            return "MAILBOX_READ_ONLY"


    def logout(self):
        """ logout to IMAP server """

        self.connection.logout()


    def listFolders(self):
        """ return the list of IMAP folders """

        #val=string.replace(item, '() "." ', '')

        #list=self.connection.list(directory='INBOX%')

        list=self.connection.list()
        IMAPFolders=[]
        for item in list[1]:
            if item is not None:
                try:
                    vl=re.sub(r'(\(.+\))(.+)', r'\2', item)
                    val =string.split(vl, ' ', 2)[2]
                    val=string.strip(string.replace(val,'"', ''))
                    IMAPFolders.append(val)
                except:
                    IMAPFolders.append("folder error")
                ##i=string.find(item, "INBOX")
##                if i!= -1:
##                    val=item[i:]
##                    val=string.replace(val,'"', '')
##                    IMAPFolders.append(val)

        return IMAPFolders


    def selectFolder(self, name):
        """ select an IMAP folder """

        self.connection.select(name)


    def createFolder(self, name):
        """ create a new IMAP folder """


        #utf-7 enconding
        encoded_name=string.replace(name, "&", "&-")
        encoded_name=string.replace(encoded_name, "é", "&AOk-")
        encoded_name=string.replace(encoded_name, "â", "&AOI-")
        encoded_name=string.replace(encoded_name, "à", "&AOA-")
        encoded_name=string.replace(encoded_name, "è", "&AOg-")
        encoded_name=string.replace(encoded_name, "ç", "&AOc-")
        encoded_name=string.replace(encoded_name, "ù", "&APk-")
        encoded_name=string.replace(encoded_name,  "ê", "&AOo-")
        encoded_name=string.replace(encoded_name,  "î", "&AO4-")
        encoded_name=string.replace(encoded_name, "ó", "&APM-")
        encoded_name=string.replace(encoded_name,  "ñ", "&APE-")
        encoded_name=string.replace(encoded_name,  "á", "&AOE-")
        encoded_name=string.replace(encoded_name,  "ô", "&APQ-")
        encoded_name=string.replace(encoded_name,  "É", "&AMk-")
        name=string.replace(encoded_name, "ë", "&AOs-")

        fold_name=name

        name = '"INBOX.' + name + '"'
        try:
            if string.upper(fold_name) != "INBOX":
                return self.connection.create(name)
            else:
                return "NO"
        except:
            return "NO"


    def deleteFolder(self, wmail, name):
        """ delete IMAP folder """

        if name not in['"INBOX"', wmail.getDraftIMAPName(), wmail.getTrashIMAPName(), wmail.getSentMailIMAPName()]:
            delFolder=self.connection.delete('"'+name+'"')

        try:
            if delFolder[0]=="OK":
                return 1
            else:
                return 0
        except:
            return 0



    def getIMAPList(self, folderName, sortmail, start=0, how_many="ALL"):
        """ return the sorted list of IMAP Id """

        self.selectFolder(folderName)

        inverse_result=0
        if sortmail=="date":
            #get messages list on server, no sort
            result = self.connection.uid('SEARCH', how_many)
            inverse_result=1
        elif sortmail in ["DATE", "SUBJECT", "FROM", "SIZE", "TO"]:
            #get sorted messages list
            if sortmail in ["DATE", "SIZE"]:
                inverse_result=1
            if sortmail == "DATE":
                sortmail="(DATE)"
            else:
                sortmail="("+sortmail+" DATE)"

            result=self.connection.uid('SORT', sortmail,'iso-8859-1', how_many)

        elif string.find(sortmail, "search") != (-1):
            #get messages list from search
            sortmail_list=string.split(sortmail, "x2jq")

            # AT: sortmail has the present syntax :
            # search [BODY, SUBJECT, FROM, TO] [ON, SINCE, BEFORE] FLAG sort DATE
            keywords = sortmail_list[1:-3]
            for kw in keywords:
                kw = string.replace(kw, "zz20", " ")
            flagged=0
            if sortmail_list[-3]=="yes":
                flagged=1
            sort=sortmail_list[-1]

            if sort not in ["SUBJECT", "FROM", "TO"]:
                inverse_result=1

            if flagged:
                result=self.connection.uid('SORT', '('+sort+')','iso-8859-1', "FLAGGED", *keywords)
            else:
                result=self.connection.uid('SORT', '('+sort+')','iso-8859-1', *keywords)

            nb=string.split(result[-1][0])
            nb_messages_in_mailbox=len(nb)

        elif sortmail=="FLAGGED":
            result = self.connection.uid('SEARCH', 'FLAGGED')
            inverse_result=1
        else:
            result = self.connection.uid('SEARCH', how_many)
            inverse_result=1

        # set imap list
        liste_res=map(int, string.split(result[-1][-1]))

        if inverse_result:
            liste_res.reverse()

        return liste_res

    def listMessagesHeaders(self, folderName="INBOX", sortmail="", start=0, end=0, listing_size=0):
        """ return headers from a IMAP folder """


        start=int(start)

        if not end:
            end=start+int(listing_size)

        end=int(end)

        liste_res=self.getIMAPList(folderName=folderName, sortmail=sortmail, start=start)

        #limit the number of message in the list to number of messages
        #by page (choose in options)
        liste_res=liste_res[start:end]

        liste_messages=[]
        for IMAPId in liste_res:
            #get flags, size and header for message
            rep=self.connection.uid('FETCH',IMAPId,'(FLAGS RFC822.SIZE RFC822.HEADER)')
            val= rep[-1][0][0]
            flags=re.sub(r'(.+)(FLAGS \()(.+)(\).+)', r'\3', val)
            if string.find(flags, 'UID')!=(-1):
                flags=" "
            taille=int(re.sub(r'(.+)(RFC822.SIZE )(\d+)( .+)', r'\3 ', val))
            liste_messages.append({'message':rep[-1][0][1], 'size':taille, 'flags':flags, 'imapId':IMAPId})

        return liste_messages


    def getFlags(self, folderName, IMAPId):
        """ return flags of a message """

        self.selectFolder(folderName)
        rep = self.connection.uid('FETCH',str(IMAPId),'(FLAGS)')
        val = rep[-1][0]
        flags=re.sub(r'(.+)(FLAGS \()(.+)(\).+)', r'\3', val)
        if string.find(flags, 'UID')!=(-1):
            flags=" "

        return flags

    def setFlag(self, folderName="", IMAPId="", flag=""):
        """ set flag of a message """

        if folderName:
            self.selectFolder(folderName)

        if flag=="delete":
            self.connection.uid('STORE',str(IMAPId),'+FLAGS','(\Deleted)')
        if flag=="anwser":
            self.connection.uid('STORE',str(IMAPId),'+FLAGS','(\Answered)')
        if flag=="+flagged":
            self.connection.uid('STORE',str(IMAPId),'+FLAGS','(\Flagged)')
        if flag=="-flagged":
            self.connection.uid('STORE',str(IMAPId),'-FLAGS','(\Flagged)')
        if flag=="draft":
            self.connection.uid('STORE',str(IMAPId),'+FLAGS','(\Draft)')


    def getMessage(self, folderName="INBOX", IMAPId=""):
        """ get full message """

        if folderName:
            self.connection.select(folderName)

        #self.getBodyStructure(str(IMAPId))

        direct_body=' '
        flags=""

        try:
            direct_body=self.connection.uid('FETCH',str(IMAPId), '(BODY.PEEK[1])')[-1][0][-1]
        except:
            pass

        try:
            message = self.connection.uid('FETCH',str(IMAPId), 'RFC822') [-1][0][1]
       	except:
            return 'DELETED', direct_body, flags

        try:
            flags=self.getFlags(folderName, IMAPId)
        except:
            pass

       	return message, direct_body, flags


    def getPreviousAndNextMessagesIds(self, folderName, sortmail, IMAPId):
        """ get next message on folder (sorted)  """

        res=self.getIMAPList(folderName, sortmail)

        try:
            index=res.index(int(IMAPId))
        except:
            return None, None

        index_next=index+1
        index_prev=index-1

        if index_prev>=0:
            prev=res[index_prev]
        else:
            prev=None

        try:
            next=res[index_next]
        except:
            next=None

        return prev, next

    def copy(self, folderNameSrc, folderNameDest, IMAPId):
        """ copy a message from a folder to another """

        copy_ok=0

        if folderNameSrc:
            self.selectFolder(folderNameSrc)
            _res=self.connection.uid('COPY',str(IMAPId),'"'+folderNameDest+'"')
            try:
                if _res[1][0]=="Over quota":
                    copy_ok=2
            except:
                pass
            res=_res[0]
            if res == "OK" :
                copy_ok=1

        return copy_ok


    def getQuota(self):
        """ return % used quota on mailbox """

        res=self.connection.get_quota_root()
        tab=string.split(res[0])
        return (100*int(tab[-2]))/int(string.replace(tab[-1], ")", ""))

    def getNumberOfMessage(self, folderName, search=""):
        """ return the number of message in a folder """

        if not search:
            #number of messages in folder
            return self.connection.select(folderName)[1][0]
        else:
            #number of messages from a search
            if folderName:
                self.connection.select(folderName)
            sortmail_list=string.split(search, "x2jq")

            # AT: sortmail has the present syntax :
            # search [BODY, SUBJECT, FROM, TO] [ON, SINCE, BEFORE] FLAG sort DATE
            keywords = sortmail_list[1:-3]
            for kw in keywords:
                kw = string.replace(kw, "zz20", " ")
            flagged=0
            if sortmail_list[-3]=="yes":
                flagged=1
            sort=sortmail_list[-1]
            if flagged:
                result=self.connection.uid('SORT', '('+sort+')','iso-8859-1', "FLAGGED", *keywords)
            else:
                result=self.connection.uid('SORT', '('+sort+')','iso-8859-1', *keywords)
            nb=string.split(result[-1][0])
            return len(nb)

    def expunge(self):
        """ expunge ! """

        #delete on IMAP server all messages where flag deleted is on
        self.connection.expunge()

    def writeMessage(self, folderName, raw_message):
        """ wrtite a message in a folder """

        res=self.connection.append(folderName, None , None, raw_message)
        try:
            return string.replace(string.split(res[1][0])[2], ']', '')
        except:
            return ""

    def getBodyStructure(self, IMAPId):
        """ get the body structure of the message """

        a=1
        #body=self.connection.uid('FETCH',str(IMAPId), '(BODY.PEEK[1])')[-1][0][-1]
##        val=self.connection.uid('FETCH',str(IMAPId), 'BODY')
##        print " 1******", val
##        print "3****", val[-1][0]

##        val=str(val[-1][0])

##        for item in string.split(self.connection.uid('FETCH',str(IMAPId), 'BODYSTRUCTURE') [-1][0], ')('):
##            print item
##        print ' '
##        print "222222222222222222222222222222"
        print ' '
        nbParts=0
        v0=self.connection.uid('FETCH',str(IMAPId), 'BODY')
        v=str(v0[-1][0])

        liste=[]
        print v
        v=v[string.find(v, '("')+1:]
        for item in string.split(v, ')('):
            #print ' '
            #print item
            item2=string.replace(item, "(", "")
            item2=string.replace(item2, ")", "")

            v1=string.split(item2, '"')
            #print "v1"
            #print v1
            #print " "

            v2=string.split(item2)
            #print "v2", v2
            liste.append(item2)
            nbParts=nbParts+1
            print " "
            print "type = "+self._strip2Quotes(v2[0])+"/"+self._strip2Quotes(v2[1])

            #"7bit" , "quoted-printable", "base64", "8bit","binary"

            if string.find(item, '"FILENAME"')!=(-1):
                ind=v1.index('FILENAME')
                print "filename =", self._strip2Quotes(v1[ind+2])
            elif string.find(item, '"NAME"')!=(-1):
                ind=v1.index('NAME')
                print "name =", self._strip2Quotes(v1[ind+2])

            if string.find(item, '"BASE64"')!=(-1):
                ind=v2.index('"BASE64"')
                print "taille (base64) =", self._strip2Quotes(v2[ind+1])
            elif string.find(item, '"7BIT"')!=(-1):
                ind=v2.index('"7BIT"')
                print "taille (7bit) =", self._strip2Quotes(v2[ind+1])
            elif string.find(item, '"8BIT"')!=(-1):
                ind=v2.index('"8BIT"')
                print "taille (8bit) =", self._strip2Quotes(v2[ind+1])
            elif string.find(item, '"QUOTED-PRINTABLE"')!=(-1):
                ind=v2.index('"QUOTED-PRINTABLE"')
                print "taille (quoted) =", self._strip2Quotes(v2[ind+1])
            elif string.find(item, '"BINARY"')!=(-1):
                ind=v2.index('"BINARY"')
                print "taille (binary) =", self._strip2Quotes(v2[ind+1])

        print "il y a ", nbParts, "parts"
        #print liste


    def _strip2Quotes(self, s):
        """ Strip double quotes around string <s> if any."""

        try:
            if s[0]==s[-1]=='"':
                s = s[1:-1]
        except:
            pass
        return s
