##parameters=REQUEST
## Script (Python) "address_book.py"

try:
    del REQUEST.SESSION['search_results']
except:
    pass

#
# Redirection to the adressBook form
#
REQUEST.RESPONSE.redirect(context.portal_url() + '/addressBook_form')

