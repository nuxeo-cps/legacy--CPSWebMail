##parameters=REQUEST
## Script (Python) "remove_selected_pieces.py"

#
# Clear the session objects
#
context.portal_webMail.saveMailSession(REQUEST)
context.portal_webMail.removeSelectedPieces(REQUEST)

#
# Redirection to the edit message form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IName)
