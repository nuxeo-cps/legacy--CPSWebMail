##parameters=REQUEST
## Script (Python) "addressbook_groupdelete.py"

#
# Take the default address book
#
addressbook_name = getattr(REQUEST,'addressbook_name','_private')
addressbook  = context.portal_webMail.getCurrentAddressBook(addressbook_name)

#
# Deleting the chosen entries
#
context.portal_webMail.addressbookGroupDelete(addressbook, REQUEST)
#
# Redirection to the addressbook form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form?addressbook_name='+addressbook_name)

