##parameters=REQUEST
# $Id: #

from zLOG import LOG, DEBUG

#
# Take the default address book
#
addressbook_name = getattr(REQUEST, 'addressbook_name', '_global')
if addressbook_name == '_groups':
    addressbook  = context.portal_webMail.getCurrentAddressBook('_members')
else:
    addressbook  = context.portal_webMail.getCurrentAddressBook(addressbook_name)
addressbook  = context.portal_webMail.getCurrentAddressBook(addressbook_name)
list_to_add = getattr(REQUEST, 'to_add_to_privbooklinks', [])

#
# Adding the selected entries
#
context.portal_webMail.addressbookAddContactsLinksToPrivBook(addressbook, list_to_add)

#
# Redirection to the addressbook form
#
portal_url = context.portal_url()
context.addressbook_changelist(REQUEST)
