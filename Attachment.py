######################################################################
#
# WebMail, a IMAP Webmail for Zope
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

import string
from mimetools import choose_boundary
import mimetools
from ZPublisher import HTTPRangeSupport
from DateTime import DateTime
from cStringIO import StringIO
import cStringIO

class Attachment:
    """ an attachment of a mail """

    def __init__(self,id,filename,content_type='',size='',data=''):
        """ constructor """
        self.id = id
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.data = data

    def __call__(self):
        """ For print preview """
        return self.getFilename()

    def getId(self):
        """ return the id """
        return self.id

    def getFilename(self):
        """ return the filename """
        return self.filename

    def getContentType(self):
        """ return the content type """
        return self.content_type

    def getSize(self):
        """ return the size """
        return self.size


    def getData(self):
        """ return the data of the attachment """
        return self.data

    def setId(self,id):
        """ set the id """
        self.id = id

    def setFilename(self, filename):
        """ set the filename of the attachment """
        self.filename = filename

    def setSize(self,size):
        """ set the size of this attacheent """
        self.size = size

    def setData(self,data):
        """ set the data of the attachment """
        self.data = data


    def encode(self):
            """Returns encoded data."""

            out_file = cStringIO.StringIO()
            in_file = cStringIO.StringIO(self.data)
            in_file.seek(0)

            mimetools.encode(in_file, out_file, 'base64')

            return out_file.getvalue()


    def render_mail_attachment(self):
        """render readable mail passed as attachment"""

        import Products
        from Products.WebMail import *
        
        ref_message =  Products.WebMail.RFC822MessagesTools.parse_RFCMessage(mess=self.getData(), direct_body=" ", flags="", imapid="temp")

        return ref_message
        

    def download(self, REQUEST=None, RESPONSE=None):
        """
        The default view of the contents of a File or Image.
        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """
        # HTTP Range header handling
        range = REQUEST.get_header('Range', None)
        if_range = REQUEST.get_header('If-Range', None)
        if range is not None:
            ranges = HTTPRangeSupport.parseRange(range)

            if ranges:
                # Search for satisfiable ranges.
                satisfiable = 0
                for start, end in ranges:
                    if start < self.size:
                        satisfiable = 1
                        break

                if not satisfiable:
                    RESPONSE.setHeader('Content-Id', self.filename)
                    RESPONSE.setHeader('Content-Range', 
                        'bytes */%d' % self.size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
##                    RESPONSE.setHeader('Last-Modified',
##                        rfc1123_date(self._p_mtime))
                    RESPONSE.setHeader('Content-Type', self.content_type)
                    RESPONSE.setHeader('Content-Length', self.size)
                    RESPONSE.setStatus(416)
                    return ''

                # Can we optimize?
                ranges = HTTPRangeSupport.optimizeRanges(ranges, self.size)
                                
                if len(ranges) == 1:
                    # Easy case, set extra header and return partial set.
                    start, end = ranges[0]
                    size = end - start
                    
##                    RESPONSE.setHeader('Last-Modified',
##                        rfc1123_date(self._p_mtime))
                    RESPONSE.setHeader('Message-id', self.filename)
                    RESPONSE.setHeader('Content-Id', self.filename)
                    RESPONSE.setHeader('Content-Type', self.content_type)
                    RESPONSE.setHeader('Content-Length', size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
                    RESPONSE.setHeader('Content-Range', 
                        'bytes %d-%d/%d' % (start, end - 1, self.size))
                    RESPONSE.setStatus(206) # Partial content

                    data = self.data
                    if type(data) is StringType:
                        return data[start:end]

                    # Linked Pdata objects. Urgh.
                    pos = 0
                    while data is not None:
                        l = len(data.data)
                        pos = pos + l
                        if pos > start:
                            # We are within the range
                            lstart = l - (pos - start)

                            if lstart < 0: lstart = 0
                            
                            # find the endpoint
                            if end <= pos:
                                lend = l - (pos - end)
                                
                                # Send and end transmission
                                RESPONSE.write(data[lstart:lend])
                                break

                            # Not yet at the end, transmit what we have.
                            RESPONSE.write(data[lstart:])

                        data = data.next
                    return ''
                    
                else:
                    # When we get here, ranges have been optimized, so they are
                    # in order, non-overlapping, and start and end values are
                    # positive integers.
                    boundary = choose_boundary()
                    
                    # Calculate the content length
                    size = (8 + len(boundary) + # End marker length
                        len(ranges) * (         # Constant lenght per set
                            49 + len(boundary) + len(self.content_type) + 
                            len('%d' % self.size)))
                    for start, end in ranges:
                        # Variable length per set
                        size = (size + len('%d%d' % (start, end - 1)) + 
                            end - start)
                    RESPONSE.setHeader('Message-id', self.filename)
                    RESPONSE.setHeader('Content-Id', self.filename)
                    RESPONSE.setHeader('Content-Length', size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
##                    RESPONSE.setHeader('Last-Modified',
##                        rfc1123_date(self._p_mtime))
                    RESPONSE.setHeader('Content-Type',
                        'multipart/byteranges; boundary=%s' % boundary)
                    RESPONSE.setStatus(206) # Partial content

                    pos = 0
                    data = self.data

                    for start, end in ranges:
                        RESPONSE.write('\r\n--%s\r\n' % boundary)
                        RESPONSE.write('Content-Type: %s\r\n' %
                            self.content_type)
                        RESPONSE.write(
                            'Content-Range: bytes %d-%d/%d\r\n\r\n' % (
                                start, end - 1, self.size)) 

                        if type(data) is StringType:
                            RESPONSE.write(data[start:end])

                        else:
                            # Yippee. Linked Pdata objects.
                            while data is not None:
                                l = len(data.data)
                                pos = pos + l
                                if pos > start:
                                    # We are within the range
                                    lstart = l - (pos - start)

                                    if lstart < 0: lstart = 0
                                    
                                    # find the endpoint
                                    if end <= pos:
                                        lend = l - (pos - end)
                                        
                                        # Send and loop to next range
                                        RESPONSE.write(data[lstart:lend])
                                        # Back up the position marker, it will
                                        # be incremented again for the next
                                        # part.
                                        pos = pos - l
                                        break

                                    # Not yet at the end, transmit what we have.
                                    RESPONSE.write(data[lstart:])

                                data = data.next

                    RESPONSE.write('\r\n--%s--\r\n' % boundary)
                    return ''


##        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Filename', self.filename)
        RESPONSE.setHeader('Message-id', self.filename)
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

##        hdr_name = "content-disposition"
##        hdr_value = 'attachment; filename="eek.zip" '
##        RESPONSE.setHeader(hdr_name, hdr_value)
        

        data=self.data
        if type(data) is type(''):
            return data

        while data is not None:
            RESPONSE.write(data.data)
            data=data.next
        return ''
        
