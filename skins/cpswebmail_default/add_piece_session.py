##parameters=REQUEST
## Script (Python) "add_piece_session.py"

#
# adding the current piece to the SESSION
#
context.portal_webMail.saveMailSession(REQUEST)
context.portal_webMail.addPiece(REQUEST)

IMAPName = REQUEST.form.get('IMAPName', "INBOX")

#
# Redirection to the edit message form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IMAPName)



