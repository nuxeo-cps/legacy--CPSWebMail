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
addressbook_name = REQUEST.get('addressbook_name', '')
addressbook = context.portal_webMail.getCurrentAddressBookName(addressbook_name, REQUEST=REQUEST)
url = portal_url + '/cpswebmail_directory_entry_create_form?dirname=' + addressbook
REQUEST.RESPONSE.redirect(url)
