##parameters=REQUEST
## Script (Python) "delete_folders.py"

context.portal_webMail.deleteIMAPFolders(REQUEST.IMAPNames)

#
# redirection to the compose folders_edit_form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/folders_edit_form')

