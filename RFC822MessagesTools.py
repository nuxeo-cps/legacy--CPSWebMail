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


def parse_RFCMessage(mess, direct_body, flags, imapid):
    """ return message instance of IMAPMessage
    """

    msg = cStringIO.StringIO(mess)
    message = mimetools.Message(msg)

    headers = {}
    parts = []
    body = ''
    attachments = []
    boundary = 0
    body_base64 = 0

    boundary = message.getparam('boundary') or '' or message.getparam('BOUNDARY') or ''

    #building header keys dictionnary for the message
    for key in message.keys():

        if is_quoted_printable.search(message[key]) or is_base64.search(message[key]):
            headers[string.lower(key)] = mimify.mime_decode_header(message[key])

            if is_base64.search(message[key]):
                try:
                    subject = string.replace(message[key], '=?iso-8859-1?B?', '')
                    subject = string.replace(subject, '=?iso-8859-1?b?', '')
                    subject = string.replace(subject, '=?iso-8859-2?b?', '')
                    subject = string.replace(subject, '=?iso-8859-2?B?', '')
                    subject = string.replace(subject, '?=', '')
                    encoded = StringIO.StringIO(subject)
                    decoded = StringIO.StringIO()
                    base64.decode(encoded, decoded)
                    headers[string.lower(key)] = decoded.getvalue()
                except:
                    pass
        else:
            headers[string.lower(key)] = mimify.mime_decode(message[key])

    msg.seek(message.startofbody)

    #get and parse attachments if exist
    if boundary:
        try:
            multi_message = multifile.MultiFile(msg)
            multi_message.push(boundary)
            liste_media = []

            while multi_message.next():
                parsed_attachment = mime_message.mime_part_parse(multi_message)
                parts.append(parsed_attachment)
                liste_media.append(parsed_attachment.media_type)

            multi_message.pop()

            if parts[0].media_type == 'text':

                body = parts[0].data

                if string.find(parts[0].encoding, 'base64') != (-1):
                    body_base64 = 1
                    try:
                        body = mime_decode(body, 1)
                    except:
                        pass
                parts = parts[1:]

            elif len(body) == 0 and (parts[1].media_type == 'text' or parts[0].media_type == 'multipart'):

                val = parts[0].data

                comp = re.compile('Content-Transfer-Encoding: base64', re.I)
                if comp.search(val):
                    body_base64 = 1

                body = re.sub(r'(------=_NextPart)([\S\s]*?)(Content-Transfer-Encoding.*)([\S\s]*?)(------=_NextPart?)([\S\s]*)', r'\4', val)

                if body_base64:
                    import base64
                    import StringIO
                    encoded = StringIO.StringIO(body)
                    decoded = StringIO.StringIO()
                    base64.decode(encoded, decoded)
                    body = decoded.getvalue()

                parts = parts[1:]

            # In any case, the rest of the parts are attachments.

            map(attachments.append, parts)
        except :
            pass
    else:
            _body = mime_message.mime_part_parse(message.fp)
            body = _body.data

    try:
        direct_body = re.sub(r'(------=_NextPart)([\S\s]*?)(Content-Transfer-Encoding.*)([\S\s]*?)(------=_NextPart?)([\S\s]*)', r'\4',direct_body)
    except:
        pass

    if body_base64:
        try:
            direct_body = mime_decode(direct_body, 1)
        except:
            pass

    if len(body) < len(direct_body):
        body = direct_body

    attachments = []
    i = 1

    for part in parts:
        id = i
        len_at = len(part.data)
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

    _subject = "pas de sujet"
    if headers.has_key('subject'):
        _subject = headers['subject']
        _subject = render_subject(_subject)

    _recipients={'to': _to, 'cc': _cc, 'bcc': []}

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
