##parameters=REQUEST
# $Id$

# to change after search
try:
    del REQUEST.SESSION['search_results']
except KeyError:
    pass

list_name = REQUEST.form.get('list_name_after_search', '')
portal_url = context.portal_url()
url = ''

if list_name == "":
    url = '/addressBook_form'
else:
    url = '/addressBook_view_list?addressbook_name=_mailing&list_name=' + list_name

REQUEST.RESPONSE.redirect(portal_url + url)
