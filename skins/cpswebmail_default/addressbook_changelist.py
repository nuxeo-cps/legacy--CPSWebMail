##parameters=REQUEST
## Script (Python) "addressbook_changelist.py"

try:
    del REQUEST.SESSION['search_results']
except KeyError:
    pass

list = REQUEST.form.get('addressbook_name', '')
list_name = REQUEST.form.get('list_name', '')
group_name = REQUEST.form.get('group_name', '')
search_role = REQUEST.form.get('search_role', '')
search_workspace = REQUEST.form.get('search_workspace', '')
portal_url = context.portal_url()

if list == "":
    # return the full list
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form')
elif list == "_all":
    # Global + Private
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form')
elif list in["_global", "_private", "_private_links", "_members"]:
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form?addressbook_name='+list)
elif list == "_groups":
    if group_name:
        REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_groups?addressbook_name='+list+'&group_name='+group_name)
    else:
        REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_groups?addressbook_name='+list)
elif list == "_mailing":
    if list_name:
        REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_list?addressbook_name='+list+'&list_name='+list_name)
    else:
        REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_list?addressbook_name='+list)
elif list == "_wsmembers":
    if search_role and search_workspace:
        REQUEST.RESPONSE.redirect(portal_url + '/addressbook_search_wsmembers?addressbook_name='+list+'&search_role='+search_role+'&search_workspace='+search_workspace)
    else:
        REQUEST.RESPONSE.redirect(portal_url + '/addressBook_search_wsmembers_form?addressbook_name='+list)
else:
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form')
