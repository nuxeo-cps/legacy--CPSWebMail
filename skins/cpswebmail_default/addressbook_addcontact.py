##parameters=REQUEST
## Script (Python) "addressbook_addcontact.py"

#
# Reinit of session if on exist
#
try:
    del REQUEST.SESSION['search_results']
except:
    pass

#
# Redirection to the directory edit entry
#
portal_url  = context.portal_url()
addressbook = context.portal_webMail.getCurrentAddressBookName(REQUEST=REQUEST)
from zLOG import LOG
url = portal_url + '/cpsdirectory_entry_create_form?dirname=' + addressbook
REQUEST.RESPONSE.redirect(url)
