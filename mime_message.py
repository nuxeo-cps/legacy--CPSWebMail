###########################################################################
#
#   Copyright (c) 2000 Morten W. Petersen <morten@esol.no>
#	Copyright (c) 2000 Thingamy Ltd.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
#    MA 02111-1307 USA
#
#
###########################################################################

###########################################################################
#
# Morten's work have been modified by University of Savoie for WebMail product
#
# This software is governed by a license. See 
# LICENSE.txt for the terms of this license.
#
###########################################################################

__author__ = '$Author$'
__version__ = '$Revision$'


import string
import mimify
import mimetools
import re
import cStringIO
import threading


class mime_part_parse(mimetools.Message):

	def __init__(self, fp):

		mimetools.Message.__init__(self, fp)

		self.filename = 'attachment'
		self.headers = {}
		self.media_type, self.sub_type = 'text','plain'
		self.data = ''

		self.encoding=string.strip(string.lower(self.getencoding()))
		
		encoding = self.encoding
		for key in self.keys():
			self.headers[string.lower(key)] = self[key]

		# We prepare the message for retrieval of the
		# body.

		self.fp.seek(self.startofbody)

		if not encoding and self.headers.has_key('content-transfer-encoding'):

			encoding = self.headers['content-transfer-encoding']

		if encoding in ('7bit','8bit',''):

			self.data = self.fp.read()
		else:
			if encoding in mimetools.decodetab.keys():
				tmp = cStringIO.StringIO()
				#mimetools.decode(self.fp, tmp, encoding)
				if encoding=="quoted-printable":
					#if decode is too long, process is stoped
					mythread=threading.Thread(target=mimetools.decode, args=(self.fp, tmp, encoding))
					mythread.start()
					mythread.join(8)
					self.data = tmp.getvalue()
					if len(self.data)==0:
						self.data=self.fp.read()
				else:
					mimetools.decode(self.fp, tmp, encoding)
					self.data = tmp.getvalue()

				del tmp
			else:

				raise 'UnknownEncodingException', encoding

		parameters = self.getparamnames()		

		if 'filename' in parameters:

			self.filename = self.getparam('filename')


		if self.filename=="attachment":
			for item in self.keys():
				if string.find(self.getheader(item), 'filename') != (-1):
					self.filename=re.sub(r'(.+)(lename=")(.+)(")', r'\3', self.getheader(item))			

		if 'name' in parameters:
			self.filename = self.getparam('name')

		if self.maintype and self.subtype:

			self.media_type = string.lower(self.maintype)
			self.sub_type = string.lower(self.subtype)

		else:

			# We'll have to guess if it's binary or not..
			# Should we make use of the content-type guesser?

			if util.binary_regexp.search(self.data):
				self.media_type, self.sub_type = 'binary','octet-stream'

				
		if self.filename=="attachment" and self.media_type=="message"  and self.sub_type == "rfc822":
			self.filename="forwarded_mail.eml"
