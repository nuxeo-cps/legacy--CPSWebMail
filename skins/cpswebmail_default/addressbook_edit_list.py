##parameters=REQUEST
## Script (Python) "addressbook_edit_list.py"

portal_url = context.portal_url()
mailing_list_name = context.portal_webMail.getMailingListName()

list_id = REQUEST.form.get('id', '')

#
# return to the create list form
# of the mailing list object
#
REQUEST.RESPONSE.redirect(portal_url
    + '/cpswebmail_directory_entry_edit_form?dirname=' + mailing_list_name
    + '&id=' + list_id)


