##parameters=REQUEST
# $Id$

from zLOG import LOG, DEBUG

#
# Take the default address book
#
addressbook_name = getattr(REQUEST, 'addressbook_name', '_global')
addressbook  = context.portal_webMail.getCurrentAddressBook(addressbook_name)
list_to_add = getattr(REQUEST, 'to_add_to_privbook', [])

#
# Adding the selected entries
#
context.portal_webMail.addressbookAddContactsToPrivBook(addressbook, list_to_add)

#
# Redirection to the addressbook form
#
portal_url = context.portal_url()
context.addressbook_changelist(REQUEST)
