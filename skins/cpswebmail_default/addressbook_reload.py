##parameters=REQUEST
## Script (Python) "addressbook_reload.py"

# Deleting session if exists
try:
    del REQUEST.SESSION['search_results']
except KeyError:
    pass

# Redirection to the addressbok main view
REQUEST.RESPONSE.redirect(context.portal_url() + '/addressBook_form')

