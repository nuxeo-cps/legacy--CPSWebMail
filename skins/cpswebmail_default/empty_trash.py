##parameters=REQUEST
## Script (Python) "empty_trash.py"

#
# Clear the Trash Folder
#
context.portal_webMail.emptyTrash()

#
# Redirection to the fetching Page
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()                                              
REQUEST.RESPONSE.redirect(portal_url + '/webmail_show?IMAPName=' + IName)

