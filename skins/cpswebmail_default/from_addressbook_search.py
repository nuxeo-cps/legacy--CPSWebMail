##parameters=REQUEST
## Script (Python) "from_addressbook_search.py"

addressbook = context.portal_webMail.getCurrentAddressBook(REQUEST=REQUEST)
context.portal_webMail.setSearchSessionCPS3(addressbook, REQUEST)

#
# Redirection to the compose form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + 
    '/addressBook_form?addressbook_name='+REQUEST['addressbook_name'])




