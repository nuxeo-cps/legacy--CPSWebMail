##parameters=REQUEST
## Script (python) "webmail_show.py"

#
# For the first call of this method cause REQUEST is empty
#
IMAPName = REQUEST.form.get('IMAPName', "INBOX")
sortmail = REQUEST.form.get('sortmail', "date")
start    = REQUEST.form.get('start', 0)

#
# Redirection to the fetching page
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url
    + '/webmail_fetch?IMAPName=' + IMAPName
    + '&sortmail=' + sortmail
    + "&start=" + str(start))


