##parameters=REQUEST
## Script (Python) "create_folders.py"

#
# Creation of the new IMAP folder
#
context.portal_webMail.createIMAPFolder(REQUEST)

#
# Redirection to the folders edit form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/folders_edit_form')

