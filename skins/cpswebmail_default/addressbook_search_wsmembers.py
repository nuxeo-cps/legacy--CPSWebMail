##parameters= REQUEST, search_role=None, search_workspace=None
# $Id$

try:
    del REQUEST.SESSION['search_results']
except KeyError:
    pass

list = REQUEST.form.get('addressbook_name', '')
search_role = REQUEST.form.get('search_role', None)
search_workspace = REQUEST.form.get('search_workspace', None)
portal_url = context.portal_url()

psm = '&portal_status_message='
args = 'addressbook_name='+list
if search_role is not None:
    args += '&search_role='+search_role
if search_workspace is not None:
    args += '&search_workspace='+search_workspace

if search_role is None:
    psm += "psm_cpswebmail_chose_role_error"
    return REQUEST.RESPONSE.redirect(portal_url + '/addressBook_search_wsmembers_form?'+args+psm)

if search_workspace is None:
    psm += "psm_cpswebmail_chose_workspace_error"
    return REQUEST.RESPONSE.redirect(portal_url + '/addressBook_search_wsmembers_form?'+args+psm)

portal = context.portal_url.getPortalObject()
workspace = portal.restrictedTraverse(search_workspace)
users = workspace.users_with_local_role(search_role)

# setting results in session
REQUEST.SESSION['search_results'] = users

return REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_wsmembers?'+args)
