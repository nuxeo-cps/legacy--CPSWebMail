##parameters=IMAPName, REQUEST
## Script (Python) "change_folder.py"

#
# Redirection to the fetching form in the new
#
REQUEST.RESPONSE.redirect(context.portal_url()
    + '/webmail_fetch?IMAPName=' + IMAPName)

