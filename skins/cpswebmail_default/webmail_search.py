##parameters=REQUEST
## Script (Python) "search.py"

#
# Redirection to the search form interface
#
portal_url = context.portal_url()
IMAPName = REQUEST.form.get('IMAPName', "INBOX")
REQUEST.RESPONSE.redirect(portal_url + '/webmail_search_form?IMAPName=' + IMAPName)

