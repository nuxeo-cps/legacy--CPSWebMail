##parameters=IMAPId, IMAPName, start, REQUEST
## Script (Python) "view_message.py"

#
# Init of a message view session
#
context.portal_webMail.createViewSession(REQUEST)

#
# Redirection to the view message form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/view_message_form')
