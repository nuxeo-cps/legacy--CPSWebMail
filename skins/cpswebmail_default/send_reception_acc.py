##parameters=REQUEST
## Script (Python) "send_reception_acc.py"

#
# Changing the view flag after sending the mail
#
mail_session = REQUEST.SESSION.get('vm_session', {})
mail_session['view'] = "1"
REQUEST.SESSION['vm_session'] = mail_session

context.portal_webMail.sendReceptionAcc(REQUEST)
 
#
# Redirection to the view_message_form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/view_message_form')


