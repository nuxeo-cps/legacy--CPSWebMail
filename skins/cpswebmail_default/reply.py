##parameters=REQUEST
## Script (Python) "reply.py"

#
# Init of session object for a new mail
#
context.portal_webMail.createMailSession(REQUEST)
context.portal_webMail.createReplySession(REQUEST, all=0)

#
# Redirection to the edit message form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message')
