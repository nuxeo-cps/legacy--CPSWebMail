##parameters=IMAPName, IMAPId, REQUEST, RESPONSE

# $Id$

# extract attachments and create a Document in provate area with data content

from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

wmtool = getToolByName(context, 'portal_webMail')
mtool = getToolByName(context, 'portal_membership')
vm_session = REQUEST.SESSION.get('vm_session')
folder = wmtool.getInboxFolder(REQUEST)
the_id = vm_session['IMAPId']
message = folder.getIMAPMessage(the_id)

AttachIdlist = REQUEST.get("AttachIdlist", [])

if not AttachIdlist:
    msg = 'cpswebmail_no_attachment_selected'
else:
    res = 1
    for attach_id in AttachIdlist:
        attachment = message.getAttachments()[int(attach_id) - 1]
        res = res and attachment.exportToHomeFolder(context)

    if res:
        msg = 'cpswebmail_attachments_saved'
    else:
        msg = 'cpswebmail_error_export_attachments'

return RESPONSE.redirect(mtool.getHomeUrl()+ '?portal_status_message=' + msg)
