#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# See LICENSE.TXT for licensing information
#


#==================================
#      PATCH of IMAPMessage.py
#==================================

from Products.WebMail.IMAPMessage import IMAPMessage
from Products.WebMail.IMAPFolder import *
from Products.WebMail.IMAPGateway import *

from DocumentTemplate.DT_Var import newline_to_br

import cStringIO
import mimetools
import MimeWriter
import mimify
import re
import string

#
# Adding reception flag on mail header
#
def raw_message(self, flag):
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

        for address_field in ['to', 'cc']:
            if self.recipients[address_field]:
                for address in self.recipients[address_field]:
                    writer.addheader(string.capitalize(address_field),
                                     mimify.mime_encode_header(address))

        if flag != "":
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

                        #tmp_headers = {'content-transfer-encoding':
                                        ##'base64'}
                        ##tmp_headers.update(attachment.headers)
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

def get_parsed_body(self):
    """Return the parsed body"""
    try:
        if string.find(string.lower(self.headers['content-type']),
                       "text/html" != (-1)):
            new_body = self.render_body(self.getBody(), 'html')
            return self.match_url(new_body)

        elif string.find(self.headers['content-type'], 'text/enriched') != (-1):
            new_body = newline_to_br(string.replace(\
                self.render_body(self.getBody(), 'enriched'), '  ', '&nbsp; '))
            return self.match_url(new_body)

        else:
            new_body = newline_to_br(string.replace(self.render_body(\
                self.getBody(), 'text'), '  ', '&nbsp; '))
            return self.match_url(new_body)
    except:
        new_body = newline_to_br(
            string.replace(
                self.render_body(self.getBody(), 'text'),
                '  ', '&nbsp; '))
        return self.match_url(new_body)


#=========================
#     APPLY PATCHES
#=========================

IMAPMessage.raw_message = raw_message
IMAPMessage.getHeaders = getHeaders
IMAPMessage.is_reception_flag = is_reception_flag
IMAPMessage.get_parsed_body = get_parsed_body
IMAPMessage.match_url = match_url


from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

import WebMailTool

tools = (WebMailTool.WebMailTool,)

registerDirectory('skins/cpswebmail_default', globals())
registerDirectory('skins/cpswebmail_images', globals())


def initialize(registrar):
    """ Register the WebMailTool class """
    utils.ToolInit("CPS WebMail Tool",
        tools=tools,
        product_name='CPSWebMail',
        icon='tool.gif',
    ).initialize(registrar)

