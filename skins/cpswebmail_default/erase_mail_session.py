##parameters=REQUEST
## Script (Python) "erase_mail_session.py"

#
# Erasing object session
#
context.portal_webMail.endMailSession(REQUEST)

#
# Redirection to the edit message form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IName)

