##parameters=REQUEST
## Script (Python) "addressbook_import.py"

addressbook_name = context.portal_webMail.getCurrentAddressBookName(REQUEST=REQUEST)
addressbook  = context.getCurrentAddressBook(REQUEST=REQUEST)

if REQUEST.form.get('erase', 0):
    context.portal_webMail.deleteAllEntries(addressbook)

file = REQUEST.form.get('file', "")
context.portal_webMail.importMSOaddressbook(addressbook, file)

#
# Redirect to the addressbook default view
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form/')


