##parameters=REQUEST
## Script (Python) "add_piece.py"

#
# Saving current mail composing
#
context.portal_webMail.saveMailSession(REQUEST)

IMAPName = REQUEST.form.get('IMAPName', "INBOX")

#
# Redirection to the add pieces form
#
REQUEST.RESPONSE.redirect(portal_url+'/add_piece_form?IMAPName='+IMAPName)



