##parameters=REQUEST
## Script (Python) "addressbook_changelist.py"

try:
    del REQUEST.SESSION['search_results']
except:
    pass

list_name = REQUEST.form.get('list_name', '')
portal_url = context.portal_url()
url = ''

if list_name == "":
    url = '/addressBook_form'
else:
    url = '/addressBook_view_list?addressbook_name=_mailing&list_name=' + list_name

REQUEST.RESPONSE.redirect(portal_url + url)
