##parameters=REQUEST
## Script (Python) "save_to_draft.py"

#
# saving the current message in session object
#
context.portal_webMail.saveMailSession(REQUEST)

#
# saving the current message in the draft IMAP folder
#
context.portal_webMail.saveDraft(REQUEST)
context.portal_webMail.endMailSession(REQUEST)

#
# Redirection to the fecthing form
#
IName = REQUEST.form.get('IMAPName', "INBOX")
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/webmail_show?IMAPName=' + IName)

