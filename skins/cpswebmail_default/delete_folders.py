##parameters=REQUEST
## Script (Python) "delete_folders.py"

IMAPNames = REQUEST.get('IMAPNames')
if IMAPNames is not None:
    context.portal_webMail.deleteIMAPFolders(IMAPNames)

#
# redirection to the compose folders_edit_form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/folders_edit_form')

