# -*- coding: iso-8859-15 -*-
######################################################################
#
# RFC822MessagesTools, messages and headers parser for WebMail product
#
# This software is governed by a license. See 
# LICENSE.txt for the terms of this license.
#
######################################################################
#
# Copyright (c) 2004 Nuxeo SARL <http://www.nuxeo.com>
# See LICENSE.TXT for licensing information
#
######################################################################
# $ Id: $

import rfc822
import cStringIO
import base64
import string
import mimify
import mimetools
import DateTime
import re
import multifile
import random
import StringIO
from DocumentTemplate.DT_Util import html_quote
from DocumentTemplate.DT_Var import newline_to_br

import mime_message
import IMAPMessage
import Attachment

from zLOG import LOG, DEBUG, INFO

is_quoted_printable = re.compile('=\\?iso-8859-[12]\\?q\\?([^? \t\n]+)\\?=', re.I)
is_base64 = re.compile('=\\?iso-8859-[12]\\?b\\?([^? \t\n]+)\\?=', re.I)

def parse_RFCHeaders(header, nbCharSubject=25):
    """ return dictionnary of parsed header
    """

    message = header['message']
    size = header['size']
    flags = header['flags']
    imapId = header['imapId']

    # f=open("mess.txt", 'w')
    # f.write(message)
    # f.close()
    # fp=open("mess.txt", 'r')

    fp = StringIO.StringIO(message)

    val = rfc822.Message(fp)

    attachment = 0

    #check if attachments

    if val.getheader("Content-Type") is not None:
        ctyp = val.getheader("Content-Type")
        if string.find(ctyp, 'boundary') != -1 or string.find(string.upper(ctyp), 'BOUNDARY') != -1:
            # XXX: this is not the right test to know if there is an attachment...
            attachment = 1

    Exp = [None, None]

    try:
            From = val.getaddr("From")
    except:
            From = [" ", " "]

    Exp[0] = From[0]
    Exp[1] = From[1]

    try:
            if is_quoted_printable.search(From[0]):
                    Exp[0] = mimify.mime_decode_header(From[0])

            if  Exp[0] is not None and Exp[0] != "":
                    sender = Exp[0]
            elif Exp[0] is not None and Exp[0] == "":
                    sender = Exp[1]
            else:
                    sender = " Expéditeur non spécifié "
    except:
            sender = " Expéditeur non spécifié "

    if sender is None:
            sender = " Expéditeur non spécifié "

    if is_quoted_printable.search(sender):
            sender = mimify.mime_decode_header(sender)

    try:
        too = val.getaddr("To")
    except:
        too = ("", " ")

    if  too[0] is not None and too[0] != "":
            to = too[0]
    elif too[0] is not None and too[0] == "":
            to = too[1]
    else:
            to = " "

    subj = val.getheader("Subject")

    if subj is not None:
            subject = render_subject(subj)
    else:
            subject = "[pas de sujet]"

    fp.close()

    if len(subject) > nbCharSubject:
        subject = subject[:nbCharSubject] + '...'

    #render readable size
    if size > 1024 * 1024:
        size = "%.2f MB" % (size / 1024.0 / 1024)
    else:
        size = "%.2f KB" % (size / 1024.0)

    head= {}

    try:
        ddate = render_date(val.getheader("Date"))
    except:
        ddate = " format error "

    try:
        head = {'imap_id': imapId, 'sender': string.capitalize(sender[0:25]), 'mail_sender': Exp[1], 'to': string.capitalize(to), 'size': size,
                'subject': string.capitalize(subject), 'date': ddate, 'read': 0, 'answered': 0, 'deleted': 0, 'flagged': 0, 'attachments': attachment}
    except:
        head = {'imap_id': imapId, 'sender': sender[0:25], 'mail_sender': Exp[1], 'to': to,  'size': size, 'subject': subject,
                'date': ddate, 'read': 0, 'answered': 0, 'deleted': 0, 'flagged': 0, 'attachments': attachment}

    flags = string.lower(flags)

    if string.find(flags, 'seen') != (-1):
        head["read"] = 1
    if string.find(flags, 'deleted') != (-1):
        head["deleted"] = 1
    if string.find(flags, 'answered') != (-1):
        head["answered"] = 1
    if string.find(flags, 'flagged') != (-1):
        head["flagged"] = 1
    if string.find(flags, 'forwarded') != (-1):
        head["forwarded"] = 1
    else:
        head["forwarded"] = 0

    return head


def parse_RFCMessage(mess, direct_body, flags, imapid, is_draft=0):
    """ return message instance of IMAPMessage
    """

    msg = cStringIO.StringIO(mess)
    message = mimetools.Message(msg)

    headers = {}
    parts = []
    body = ''
    attachments = []
    body_base64 = 0

    #building header keys dictionnary for the message
    for key in message.keys():
        subject = render_subject(message[key])
        headers[string.lower(key)] = subject

    # get body and parse attachments if exist
    content_type = string.lower(headers.get('content-type', 'text/plain'))
    body, parts = make_body_and_parts(msg, message, content_type)

    attachments = []
    i = 1

    for part in parts:
        len_at = len(part.data)
        if len_at > 0:
            id = i
            if len_at > 1024 * 1024:
                _size = "%.2f MB" % (len_at / 1024.0 / 1024)
            else:
                _size = "%.2f KB" % (len_at / 1024.0)
            if is_quoted_printable.search(part.filename):
                part.filename = mimify.mime_decode_header(part.filename)
            attachments.append(Attachment.Attachment(id = id,
                                                     filename = part.filename,
                                                     content_type = "%s/%s" % (part.media_type, part.sub_type),
                                                     size = _size,
                                                     data = part.data)
                          )
            i = i + 1

    _date = "pas de date spécifiée"
    if headers.has_key('date'):
        _date = headers['date']
        try:
            _date = render_date(_date)
        except:
            pass

    _to = []
    if headers.has_key('to'):
        _to = headers['to']

    _cc= []
    if headers.has_key('cc'):
        _cc = headers['cc']

    _bcc= []
    # Give the bcc only when the message is in draft folder...
    if headers.has_key('bcc') and is_draft:
        _bcc = headers['bcc']

    _subject = "pas de sujet"
    if headers.has_key('subject'):
        _subject = headers['subject']

    _recipients={'to': _to, 'cc': _cc, 'bcc': _bcc}

    _fromNom = " Expéditeur non spécifié "
    _fromMail = ''
    if headers.has_key('from'):
        if headers['from']:   ## J'ai un from
            if len(string.split(headers['from'], '<')) > 1: ## Je suis dans le cas 'nom < email >'
                _fromNom = string.strip(string.split(headers['from'], '<', 1)[0])
                _fromMail = string.replace(string.split(headers['from'], '<', 1)[1], '>', '')
            else:  ## Je suis dans le cas '<email>' ou 'email'
                _fromMail = string.replace(string.replace(headers['from'], '<', ''), '>', '')
            if is_quoted_printable.search(_fromNom):
                try:
                    _fromNom = string.strip(mimify.mime_decode_header(_fromNom))
                except: ### Encodage inconu
                    pass

    _from = (_fromNom, _fromMail)

    dico_flags = {'read': 0, 'answered': 0, 'deleted': 0, 'flagged': 0, 'forwarded': 0}
    flags = string.lower(flags)
    for item in ['read', 'answered', 'deleted', 'flagged', 'forwarded']:
        if string.find(flags, item) != (-1):
            dico_flags[item] = 1

    #build IMAPMessage
    ref = IMAPMessage.IMAPMessage(IMAPId = imapid,
                                  flags = dico_flags,
                                  sender = _from,
                                  size = 0,
                                  date = _date,
                                  subject = _subject,
                                  body = body,
                                  recipients = _recipients,
                                  attachments = attachments,
                                  headers = headers)
    return ref

def mime_decode(line, isBase64=0):
        if isBase64:
            return base64.decodestring(line)
        else:
            return mimify.mime_decode(line)

def render_date(date):
    """Returns a formatted view of the message date.
    """

    try:
        rep = date
        day = DateTime.DateTime(rep).dd()
        month = DateTime.DateTime(rep).mm()
        year = DateTime.DateTime(rep).yy()
        hour = DateTime.DateTime(rep).TimeMinutes()
        date = "%s/%s/%s %s" % (day, month, year, hour)

    except KeyError:
        date = '__'

    except DateTime.DateTime.DateTimeError, value:
        try:
            rep = re.sub(r'(\(.*\))', r'', date)
            # Hack around some badly formated dates
            # like: "Wed, 24 Mar 2004 11:56:09 +01:00"
            # (should be "... +0100")
            rep = re.sub(r'([0-9]{2,2}):([0-9]{2,2})$', r'\1\2', rep)
            day = DateTime.DateTime(rep).dd()
            month = DateTime.DateTime(rep).mm()
            year = DateTime.DateTime(rep).yy()
            hour = DateTime.DateTime(rep).TimeMinutes()
            date = "%s/%s/%s %s" % (day, month, year, hour)
        except:
            # Some dummy date in the past
            date = '01/01/70 00:00'

    except DateTime.DateTime.SyntaxError, value:
        try:
            rep = re.sub(r'(\(.*\))', r'', date)
            # Hack around some badly formated dates
            # like: "Wed, 24 Mar 2004 11:56:09 +01:00"
            # (should be "... +0100")
            rep = re.sub(r'([0-9]{2,2}):([0-9]{2,2})$', r'\1\2', rep)
            day = DateTime.DateTime(rep).dd()
            month = DateTime.DateTime(rep).mm()
            year = DateTime.DateTime(rep).yy()
            hour = DateTime.DateTime(rep).TimeMinutes()
            date = "%s/%s/%s %s" % (day, month, year, hour)
        except:
            # Some dummy date in the past
            date = '01/01/70 00:00'

    except Exception, value:
        date = 'Unknown exception (%s)' % value

    return date

def render_subject(subject):
    """ convert coded subject to ascii
    """

    if is_quoted_printable.search(subject):
        subject = mimify.mime_decode_header(subject)

    elif is_base64.search(subject):
        subject = string.replace(subject, '=?iso-8859-1?B?', '')
        subject = string.replace(subject, '=?iso-8859-1?b?', '')
        subject = string.replace(subject, '=?iso-8859-2?b?', '')
        subject = string.replace(subject, '=?iso-8859-2?B?', '')
        subject = string.replace(subject, '?=', '')
        encoded = StringIO.StringIO(subject)
        decoded = StringIO.StringIO()
        try:
            base64.decode(encoded, decoded)
            subject = decoded.getvalue()
        except:
            pass
    else:
        subject = mimify.mime_decode(subject)

    return subject


def make_body_and_parts(msg, message, content_type):
    body = ""
    parts = []

    boundary = message.getparam('boundary') or message.getparam('BOUNDARY')
    alternative = 0
    if string.find(content_type, 'multipart/alternative') != (-1):
        alternative = 1
    if boundary:
        parts = get_multipart_message_parts(msg,
                                            message.startofbody,
                                            boundary,
                                            alternative=alternative)
        new_parts = []
        for part in parts:
            parameters = part.getparamnames()
            param_dict = {}
            for param in parameters:
                param_dict[param] = part.getparam(param)
            if part.media_type == 'text':
                body_part = part.data
                if string.find(part.encoding, 'base64') != (-1):
                    body_base64 = 1
                    try:
                        body_part = mime_decode(body_part, 1)
                    except:
                        pass
                if part.sub_type != 'html':
                    body_part = newline_to_br(body_part)
                body += body_part
                if 'filename' in param_dict.keys() or 'name' in param_dict.keys():
                    # part was an attachment : display also as attachment
                    new_parts.append(part)
            else:
                new_parts.append(part)

        # In any case, the rest of the parts are attachments.
        parts = new_parts
    else:
        _body = mime_message.mime_part_parse(message.fp)
        body = _body.data
        if _body.sub_type != 'html':
            body = newline_to_br(body)

    # return body and attachments
    return body, parts


def get_multipart_message_parts(msg, start, boundary, alternative=0):
    msg.seek(start)

    parts = []

    multi_message = multifile.MultiFile(msg)
    multi_message.push(boundary)

    while multi_message.next():
        parsed_attachment = mime_message.mime_part_parse(multi_message)
        new_boundary = parsed_attachment.getparam('boundary') or parsed_attachment.getparam('BOUNDARY')
        if new_boundary is not None:
            new_parts = get_multipart_message_parts(msg, start, new_boundary)
            if parsed_attachment.media_type == 'multipart' and \
               parsed_attachment.sub_type == 'alternative':
                # content-type = mixed/alternative case
                # if all text: get the last one (with more info)
                # else: set all as attachments...
                parts_media_types = []
                for sub_part in new_parts:
                    if sub_part.media_type != 'text':
                        parts_media_types.append(sub_part.media_type)
                if len(parts_media_types) == 0 and len(new_parts) > 0:
                    new_parts = [new_parts[-1]]
            parts.extend(new_parts)
        else:
            parts.append(parsed_attachment)

    multi_message.pop()


    if alternative:
        parts_media_types = []
        for sub_part in parts:
            if sub_part.media_type != 'text':
                parts_media_types.append(sub_part.media_type)
        if len(parts_media_types) == 0 and len(parts) > 0:
            parts = [parts[-1]]

    return parts
