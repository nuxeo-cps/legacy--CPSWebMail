##parameters=REQUEST
## Script (Python) "move_message_to.py"

#
# Move the selected message to the selected folder
# Used from the view message interface
#
context.portal_webMail.moveMessages(REQUEST)

#
# Redirection to the fetching form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/webmail_show')

