##parameters=name, IMAPId, AttachId, IMAPName, REQUEST
# $Id$

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

wmtool = getToolByName(context, 'portal_webMail')
attachment = wmtool.getAttachment(IMAPId, AttachId, IMAPName, REQUEST)

return attachment
