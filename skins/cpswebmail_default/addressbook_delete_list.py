##parameters=REQUEST
# $Id$

mailing_list_name = context.portal_webMail.getMailingListName()
mailing_list = context.portal_directories[mailing_list_name]
list_name = getattr(REQUEST, 'list_name', None)

#
# Deleting the chosen list
#
if list_name is not None:
    mailing_list.deleteEntry(list_name)

# Destruction of an older session if exists
REQUEST.SESSION['search_results'] = ()

#
# Redirection to the mailing list form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/addressBook_view_list?addressbook_name=_mailing')
