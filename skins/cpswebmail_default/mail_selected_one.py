##parameters=REQUEST
## Script (Python) "mail_selected_one.py"

#
# Init session for selected mails
# Base on NuxWebMail "mail_session" solution
#

context.portal_webMail.beginMailSession(REQUEST)
context.portal_webMail.initGroupMailSession(REQUEST)

#
# Redirection to the compose form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IName)


