##parameters=REQUEST
## Script (Python) "addressbook_create_list.py"

portal_url = context.portal_url()
mailing_list_name = context.portal_webMail.getMailingListName()

#
# return to the create list form
# of the mailing list object
#
url = portal_url + '/cpswebmail_directory_entry_create_form?dirname=' + mailing_list_name
REQUEST.RESPONSE.redirect(url)

