##parameters=REQUEST
## Script (Python) "addressbook_changelist.py"

try:
    del REQUEST.SESSION['search_results']
except:
    pass

list = REQUEST.form.get('addressbook_name', '')
portal_url = context.portal_url()

if list == "":
    # return the full list
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form')
elif list == "_all":
    # Global + Private
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form')
elif list == "_global" or list == "_private":
    REQUEST.RESPONSE.redirect(portal_url + '/addressBook_form?addressbook_name='+list)
else:
    # XXX Add mailinglist support
    list_name = context.portal_webMail.getMailingListName()
    mailinglist = context.portal_directories[list_name]
    #
    # Session search objet initialize
    #
    context.portal_webMail.setListSearch(list=mailinglist,
                                           id_list=list,
                                           REQUEST=REQUEST)
    REQUEST.RESPONSE.redirect(
        portal_url + '/addressBook_view_list?addressbook_name=' + list)
