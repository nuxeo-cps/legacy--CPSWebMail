##parameters=to, REQUEST
## Script (Python) "write_addbook.py"

#
# init of session object for pieces
#
context.portal_webMail.beginMailSession(REQUEST)
mail_session = {}
mail_session = REQUEST.SESSION.get('mail_session',{})
mail_session['to'] = to
REQUEST.SESSION['mail_session'] = mail_session

#
# Redirection to the compose form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message')

