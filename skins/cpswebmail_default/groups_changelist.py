##parameters=REQUEST
## Script (Python) "addressbook_changelist.py"

try:
    del REQUEST.SESSION['search_results']
except:
    pass

group_name = REQUEST.form.get('group_name', '')
portal_url = context.portal_url()
url = ''

if group_name == "":
    url = '/addressBook_form'
else:
    url = '/addressBook_view_groups?addressbook_name=_groups&group_name=' + group_name

REQUEST.RESPONSE.redirect(portal_url + url)
