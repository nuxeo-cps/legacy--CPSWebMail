##parameters=REQUEST
## Script (Python) "add_piece_session.py"

#
# adding the current piece to the SESSION
#
context.portal_webMail.saveMailSession(REQUEST)
res = context.portal_webMail.addPiece(REQUEST)

#
# Redirection to the edit message form
#
portal_url = context.portal_url()
IMAPName = REQUEST.form.get('IMAPName', "INBOX")

err = res[0]
if err:
    args = '?IMAPName=' + IMAPName + '&portal_status_message=' + res[1]
    REQUEST.RESPONSE.redirect(portal_url + '/edit_message' + args)
else:
    REQUEST.RESPONSE.redirect(portal_url + '/edit_message?IMAPName=' + IMAPName)


