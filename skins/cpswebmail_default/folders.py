##parameters=REQUEST
## Script (Python) "folders.py"


# redirection to the compose form
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/folders_edit_form')

