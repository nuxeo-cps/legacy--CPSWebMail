##parameters=REQUEST
## Script (Python) "search_engine.py"

#
# Searching....
#
sortmail = context.portal_webMail.searchMail(REQUEST)
IMAPName = REQUEST.form.get('IMAPName', "INBOX")

if sortmail == 1:
    #
    # Error during search process
    #
    REQUEST.RESPONSE.redirect(portal_url + '/search_form')
else:
    #
    # Redirection to the fetching interface with results
    #
    portal_url = context.portal_url()
    REQUEST.RESPONSE.redirect(portal_url
        + '/webmail_show?sortmail=' + sortmail
        + '&IMAPName=' + IMAPName)

