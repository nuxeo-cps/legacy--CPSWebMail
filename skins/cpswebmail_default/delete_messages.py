##parameters=REQUEST
## Script (Python) "delete_messages.py"

#
# Deleting selected messages
#
context.portal_webMail.deleteMessages(REQUEST)

#
# Redirection to the fetching form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/webmail_show?IMAPName=' + IName)

