##parameters=REQUEST
## Script (Python) "create_folders.py"

#
# Creation of the new IMAP folder
#
res_create = context.portal_webMail.createIMAPFolder(REQUEST.title, REQUEST.IMAPName)

if res_create == 0:
    #creation sucessfull
    msg = "imap_folder_creation_successfull"
else:
    #creation unsucessfull
    msg = "imap_folder_creation_unsuccessfull"

# Redirection to the folders edit form
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/folders_edit_form?portal_status_message=' + msg)

