##parameters=REQUEST
## Script (Python) "reply_to_all.py"

#
# Init of session object for a new mail
#
context.portal_webMail.createMailSession(REQUEST)
context.portal_webMail.createReplySession(REQUEST, all=1)

#
# Redirection to the compose form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message')

