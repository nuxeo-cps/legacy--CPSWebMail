##parameters=IMAPName, IMAPId, REQUEST, RESPONSE

# $Id$

# extract attachments and create a Document in provate area with data content

TYPE_NAME = 'File'

from Products.CMFCore.utils import getToolByName

wmtool = context.portal_webMail
vm_session = REQUEST.SESSION.get('vm_session')
folder = wmtool.getInboxFolder(REQUEST)
the_id = vm_session['IMAPId']
message = folder.getIMAPMessage(the_id)

mtool = getToolByName(context, 'portal_membership')
home_folder = mtool.getHomeFolder()

AttachIdlist = REQUEST.get("AttachIdlist", [])
for attach_id in AttachIdlist:
    attachment = message.getAttachments()[int(attach_id) - 1]
    file_name = attachment.getFilename()

    # create a document object into private area
    id = string.replace(file_name, ' ', '_')

    # Only If document with same id dont exist
    if not getattr(home_folder, id, None):
	data = attachment.getData()
	content_type = attachment.getContentType()

	# Create it
	home_folder.invokeFactory(TYPE_NAME, id, mime_type=content_type)
	ob = getattr(home_folder, id)

	# Assign data from attachment
        # FIXME: that's not the right API
	ob.edit(file=data, mime_type=content_type)

    # ELSE ?

return RESPONSE.redirect(mtool.getHomeUrl())
