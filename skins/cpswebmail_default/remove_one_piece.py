##parameters=idpiece, IMAPName, REQUEST
## Script (Python) "remove_one_piece.py"

#
# Deleting this piece from the session object
#
context.portal_webMail.saveMailSession(REQUEST)
context.portal_webMail.removeOnePiece(REQUEST)

#
# Redirection to the compose form
#
portal_url = context.portal_url()
IName = REQUEST.form.get('IMAPName', "INBOX")
REQUEST.RESPONSE.redirect(portal_url
    + '/edit_message?IMAPName=' + IMAPName)

