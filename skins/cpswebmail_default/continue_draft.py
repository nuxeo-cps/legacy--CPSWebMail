##parameters=IMAPId, IMAPName, start, REQUEST
## Script (Python) "edit_session_message.py"

#
# init of session object 
#
context.portal_webMail.createDraftSession(IMAPId, IMAPName, REQUEST)

IName = REQUEST.form.get('IMAPName', "INBOX")
#
# Redirection to the compose form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url+'/edit_message?IMAPName='+IName)


