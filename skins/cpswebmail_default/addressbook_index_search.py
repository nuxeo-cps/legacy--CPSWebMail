##parameters=begin, REQUEST
## Script (Python) "addressbook_index_search.py"

#
# Take the default address book
#
addressbook_name = context.portal_webMail.getCurrentAddressBookName(REQUEST=REQUEST)
addressbook  = context.getCurrentAddressBook(REQUEST=REQUEST)

#
# Set the search with param
#
context.portal_webMail.setIndexSearchSession(addressbook, begin, REQUEST)

#
# Redirection to the addressbook form
#
REQUEST.RESPONSE.redirect(context.portal_url() + '/addressBook_form')

