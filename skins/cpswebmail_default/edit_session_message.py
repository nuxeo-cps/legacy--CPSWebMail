##parameters=REQUEST
## Script (Python) "edit_session_message.py"

#
# init of session object for pieces
#
context.portal_webMail.beginMailSession(REQUEST)

#
# Redirection to the compose form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IName)


