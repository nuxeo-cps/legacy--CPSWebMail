##parameters=REQUEST
## Script (Python) "to_addressbook.py"

#
# Saving the current status of dests
#

mail_structure        = REQUEST.SESSION.get('mail_session', {})
mail_structure['to']  = REQUEST.form.get('to', "")
mail_structure['cc']  = REQUEST.form.get('cc', "")
mail_structure['bcc'] = REQUEST.form.get('bcc', "")

REQUEST.SESSION['mail_session'] = mail_structure

#
# adding the current piece to the SESSION
#
context.portal_webMail.saveMailSession(REQUEST)

#
# Redirection to the addressbook form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/address_book')

