# -*- coding: iso-8859-15 -*-
######################################################################
#
# IMAPMessage, manage IMAP messages for Webmail product
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

# XXX AT: the IMAPMessage class could be based on the email and MIME
# handling package (python 2.3) which also deals with attachments
# (see fileAttachment.py)
#
# The email  package is a library for managing email messages, including MIME
# and other RFC 2822-based message documents. Unlike smtplib and poplib  which
# actually send and receive messages, the email package has a complete toolset
# for building or decoding complex message structures (including attachments)
# and for implementing internet encoding and header protocols.


from IMAPGateway import *
from IMAPMessage import *
import cStringIO
import mimetools
import MimeWriter
import mimify
import re
import string
from DocumentTemplate.DT_Util import html_quote
from DocumentTemplate.DT_Var import newline_to_br

from stripogram import html2safehtml, html2text

from zLOG import LOG, DEBUG

class IMAPMessage:
    """ IMAP message
    """

    def __init__(self, IMAPId="", flags={}, sender=[], size=0, date="",
                 subject="[no subject]", body="", recipients={'to': [], 'cc': [], 'bcc': []}, attachments=[], headers={}):
        """ constructor
        """

        self.headers = headers
        self.IMAPId = IMAPId
        self.flags = flags
        self.sender = sender
        self.size = size
        self.date = date
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.attachments = attachments

    def getIMAPId(self):
        """ return IMAP Id fo the message
        """
        return self.IMAPId

    def isRead(self):
        """ return the value of flag Seen (= Read)
        """
        Senderf.flags['read']

    def isAnswered(self):
        """ return the value of the flag Answered
        """
        return self.flags['answered']

    def isForwarded(self):
        """ return the value of the flag Forwarded
        """
        return self.flags['forwarded']

    def isDeleted(self):
        """ return the value of the flag Deleted
        """
        return self.flags['deleted']

    def isFlagged(self):
        """ return the value of the flag Flagged
        """
        return self.flags['flagged']

    def getSize(self):
        """ return the size of the message
        """
        return self.size

    def getDate(self):
        """ return readable date of the message
        """
        return self.date

    def setDate(self, date):
	""" set the date
        """
        self.date = date

    def getSubject(self):
        """ return the subject
        """
        return self.subject

    def setSubject(self, subject):
        """ set the subject
        """
        self.subject=subject

    def getSenderName(self):
        """ return the sender name
        """
        return string.replace(self.sender[0], "\"", '')
        #return self.sender[0]

    def getSenderMail(self):
        """ return the sender mail
        """
        return string.replace(self.sender[1], "\"", '')
        #return self.sender[1]

    def setSender(self, sender):
	""" set the sender
        """
	self.sender = sender

    def getTo(self):
        """ return the 'to' field (list)
        """
        return self.recipients['to']

    def setTo(self, to):
        """ set to value
        """
        self.recipients['to'] = to

    def getCC(self):
        """ return the 'cc' field (list)
        """
        return self.recipients['cc']

    def setCC(self, cc):
        """ set cc value
        """
        self.recipients['cc'] = cc

    def getBCC(self):
        """ return the 'bcc' field (list)
        """
        return self.recipients['bcc']

    def setBCC(self, bcc):
        """ set bcc value
        """
        self.recipients['bcc'] = bcc

    def getBody(self):
        """ return the body of the message
        """
        return self.body

    def setBody(self, body):
        """ set the message body
        """
        self.body = body

    def setRecipients(self, recipients):
        """ set recipients values
        """
        self.recipients = recipients

    def getAttachments(self):
        """ return the attachment list
        """
        return self.attachments

    def setAttachments(self, attachments):
	""" set the attachments list
        """
        self.attachments = attachments

    def edit(self, body, subject, date, sender, attachment, to, cc, bcc, copy_to_folder, save_draft):
        """ edit a message
        """
        self.setBody(body)
        self.setSubject(subject)
        self.setDate(date)
        self.setSender(sender)
        self.setAttachments(attachment)
        self.setTo(to)
        self.setCC(cc)
        self.setBCC(bcc)

    def delAttachment(self, id):
        """ delete an attachment
        """
        #to do
	pass

    #
    # Adding reception flag on mail header
    #
    def raw_message(self, ack_read=0, is_draft=0):
        """Render an RFC822 compliant message"""

        rendered_message = cStringIO.StringIO()
        writer = MimeWriter.MimeWriter(rendered_message)
        sender = "%s <%s>" % (self.sender[0], self.sender[1])
        writer.addheader('From', sender)
        date = self.headers.get('date')
        if not date:
            date = DateTime().rfc822()
        writer.addheader('Date', date)

        for header_key in self.headers.keys():
            if header_key == 'copy-to-folder':
                continue
            if header_key == 'subject' and self.headers['subject']:
                suj = self.headers['subject']
                import quopri
                from cStringIO import StringIO
                infp = StringIO(suj)
                outfp = StringIO()
                quopri.encode(infp, outfp, 1)
                subject = outfp.getvalue()
                subject = string.replace(subject, "\n", "")
                subject = string.replace(subject, " ", "_")
                if string.find(subject, "?") == -1:
                    subject = "=?iso-8859-1?Q?" + subject + "?="
                else:
                    subject = string.replace(subject, "?", "=3F")
                    subject = "=?iso-8859-1?Q?"+subject+"?="
                writer.addheader(header_key, subject)
            else:
                writer.addheader(header_key, self.headers[header_key])

        if is_draft:
            accepted_recipients = ['to', 'cc', 'bcc']
        else:
            accepted_recipients = ['to', 'cc']
        for address_field in accepted_recipients:
            if self.recipients[address_field]:
                for address in self.recipients[address_field]:
                    writer.addheader(string.capitalize(address_field),
                                     mimify.mime_encode_header(address))

        if ack_read == 1:
            writer.addheader('Disposition-Notification-To', sender)

        if self.getAttachments():
            writer.addheader('Mime-Version', '1.0')

        writer.addheader('X-Mailer',
                         'CPSWebMail Nuxeo (http://www.nuxeo.com)')

        writer.flushheaders()

        if self.getAttachments():
            writer.startmultipartbody('mixed')
            mime_part = writer.nextpart()
            mime_part_writer = mime_part.startbody('text/plain',
                                                   [('charset', 'ISO-8859-1')])
            mimetools.copyliteral(cStringIO.StringIO(self.body),
                                  mime_part_writer)

            for attachment in self.getAttachments():
                mime_part = writer.nextpart()
                mime_part.addheader('Content-Transfer-Encoding',
                                                'base64')

                # ?FIXME?
                # Let the attachment encoding decide?
                # tmp_headers = {'content-transfer-encoding':
                                            ##'base64'}
                # tmp_headers.update(attachment.headers)
                mime_part_writer = mime_part.startbody(
                    attachment.content_type,
                    [('filename',
                      attachment.filename),
                     ('name', attachment.filename)],
                    1)
                mime_part_writer.write(attachment.encode())
            else:
                writer.lastpart()
        else:
            writer._fp.write('Content-Transfer-Encoding: \
            quoted-printable\n')

            body_writer = writer.startbody('text/plain', \
                                           [('charset', 'ISO-8859-1')],
                                           {'Content-Transfer-\
                                           Encoding':\
                                            'quoted-printable'})
            self.body='\n'+self.body
            body = cStringIO.StringIO(self.body)
            body.seek(0)

            mimetools.copyliteral(body, body_writer)

        return rendered_message.getvalue()

    def setRead(self, value):
        """ set read (Seen) flag
        """
        pass

    def setAnswered(self, folderName):
        """ set Answered flag
        """
        pass

    def setForwarded(self, folderName):
        """ set Forwarded flag
        """
        pass

    def setDeleted(self, value):
        """ set deleted flag
        """
        pass

    def existAttachment(self):
        """ return true if message have one or more attachment
        """
        return len(self.attachments)

    def render_body(self, body, version='text'):
        """ replace hexadecimal character with ascii
        """

        mess = mimify.mime_decode(body)
        mess = string.replace(mess, "=\r\n", "")

        if version == "enriched":
            mess = re.sub(r'<param>([\S]*)</param>', r' ', mess)
            for tag in ['<color>', '</color>', '<bold>', '</bold>', '<bigger>', '</bigger>', '<underline>', '</underline>', '<italic>', '</italic>', '<smaller>', '</smaller>', '<center>', '</center>', '<paraindent>', '</paraindent>', '<excerpt>', '</excerpt>','<fontfamily>', '</fontfamily>']:
                mess = string.replace(mess, tag, '')

        if version == 'text' or version == 'enriched':
            mess = html_quote(mess)
            mess = re.sub(r'(http://\S*)(&quot;)', r'\1 \2 ', mess)
            mess = re.sub(r'(http://\S*)', r'<a href="\1" target="_blank">\1</a>', mess)
            mess = string.replace(mess, '/a> &quot; &gt;', '/a>&quot; &gt;')
            mess = re.sub(r'(https://\S*)', r'<a href="\1" target="_blank">\1</a>', mess)

        mess = re.sub(r'(==.*)(REL|ALT)(.*)(\n|\r)(Content-.*\n|\r){1,3}([\S\s]*)(--=.*)(REL|ALT)(?!--)([\S\s]*)', r'\6', mess)

        return mess

    def get_parsed_body(self):
        """Return the parsed body"""
        content_type = string.lower(self.headers['content-type'])
        if string.find(content_type, 'text/html') != (-1):
            new_body = self.render_body(self.getBody(), 'html')
            return self.match_url(new_body)

        elif string.find(content_type, 'text/enriched') != (-1):
            render_body = self.render_body(self.getBody(), 'enriched')
            new_body = newline_to_br(string.replace(render_body, '  ', '&nbsp; '))
            return self.match_url(new_body)
        else:
            render_body = self.render_body(self.getBody(), 'text')
            new_body = newline_to_br(string.replace(render_body, '  ', '&nbsp; '))
            return self.match_url(new_body)

    def display_body(self):
        """Return the body for HTML display on internet pages"""
        valid_tags = [
            'A',
            'ABBR',
            'ACRONYM',
            'ADDRESS',
            'B',
            'BASE',
            'BASEFONT',
            'BDO',
            'BIG',
            'BLOCKQUOTE',
            'BR',
            'BUTTON',
            'CAPTION',
            'CENTER',
            'CITE',
            'COL',
            'COLGROUP',
            'DD',
            'DEL',
            'DFN',
            'DIR',
            'DIV',
            'DL',
            'DT',
            'EM',
            'FIELDSET',
            'FONT',
            'FORM',
            'FRAME',
            'FRAMESET',
            'H1',
            'H2',
            'H3',
            'H4',
            'H5',
            'H6',
            'HR',
            'I',
            'IFRAME',
            'IMG',
            'INPUT',
            'INS',
            'ISINDEX',
            'LABEL',
            'LEGEND',
            'LI',
            'LINK',
            'MENU',
            'OBJECT',
            'OL',
            'OPTGROUP',
            'OPTION',
            'P',
            'PARAM',
            'PRE',
            'Q',
            'S',
            'SELECT',
            'SMALL',
            'SPAN',
            'STRIKE',
            'STRONG',
            'STYLE',
            'TABLE',
            'TBODY',
            'TD',
            'TEXTAREA',
            'TFOOT',
            'TH',
            'THEAD',
            'TR',
            'TT',
            'U',
            'UL',
            ]
        # not sure stripogram handles lower letters...
        lower_valid_tags = []
        for tag in valid_tags:
            lower_valid_tags.append(string.lower(tag))
        valid_tags.extend(lower_valid_tags)

        body = self.getBody()
        body = mimify.mime_decode(body)
        # turn mailto: tags into http link
        body = self.match_url(body)
        # XXX stripogram is not a good HTML parser
        # need to find another solution
##         safe_body = html2safehtml(body, valid_tags=valid_tags)
##         if safe_body:
##             # no HTMLParseError
##             body = safe_body
        return body

    def get_body_for_reply(self):
        body = self.getBody()
        body = mimify.mime_decode(body)
        safe_body = html2safehtml(body,valid_tags=())
        if safe_body:
            # no HTMLParseError
            body = safe_body
        body = string.replace(body, '&nbsp;', ' ',)
        body = string.strip(body)
        return body

    def getHeaders(self):
        """ """
        return self.headers

    def is_reception_flag(self, raw_imap_message):
        """ Return logical value """
        p = re.search('Disposition-Notification-To', raw_imap_message)
        try:
            p.group(0)
            r = 1
        except:
            r = 0
        return r

    def match_url(self, body):
        """
        Matching the mail address
        replace with a href link
        """

        def repl(matchobj):
            """ For the single address mail """
            if matchobj.group(0):
               the_matched_pattern = matchobj.group(0)
               the_matched_pattern = string.strip(the_matched_pattern)
               return  """<a href="write_addbook?to=%s">%s</a>""" % \
                                                   (the_matched_pattern,
                                                   the_matched_pattern)

        #
        # Clear the mailto notation
        #
        compiled = re.compile(r'mailto', re.IGNORECASE)
        body = re.sub(compiled, '', body)

        #
        # Address like somethin@something.st
        #
        compiled = re.compile(r'([a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+)',
                              re.IGNORECASE)
        body = re.sub(compiled, repl, body)
        return body

