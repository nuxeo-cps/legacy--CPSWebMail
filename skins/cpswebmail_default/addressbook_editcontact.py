##parameters=REQUEST
## Script (Python) "addressbook_addcontact.py"

from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

#
# Reinit of session if on exist
#
try:
    del REQUEST.SESSION['search_results']
except KeyError:
    pass

#
# Redirection to the directory edit entry
#
portal_url  = context.portal_url()
addressbook_name = REQUEST.get('addressbook_name', '')

addressbook_id = context.portal_webMail.getCurrentAddressBookName(addressbook_name, REQUEST=REQUEST)
id = REQUEST.get('id', '')
dtool = getToolByName(context, 'portal_directories', None)
addressbook = getattr(dtool, addressbook_id)
if addressbook.portal_type == 'CPS Indirect Directory':
    try:
        id = id.split('/')[1]
    except IndexError:
        pass

url = portal_url + '/cpswebmail_directory_entry_edit_form?dirname=' + addressbook_id + '&id=' + id
REQUEST.RESPONSE.redirect(url)
