##parameters=REQUEST
## Script (Python) "move_selected_message_to.py"

from zLOG import LOG, DEBUG

#
# Update in this case only cause list of checkbox
#
IMAPName     = REQUEST.form.get('IMAPName', "INBOX")
mail_session = {}

if REQUEST.form.has_key('IMAPIds'):
    #
    # If no message selected
    #
    mail_session['IMAPId']   = REQUEST.form['IMAPIds']
    mail_session['IMAPName'] = IMAPName
    f0 = REQUEST.form['move_to_folder']
    f1 = REQUEST.form['move_to_folder1']
    if f0 != "Dossiers" and f1 == "--Dossiers--":
        mail_session['move_to_folder'] = REQUEST.form['move_to_folder']
        #
        # Moving messages to the dest folder
        #
        REQUEST.SESSION['vm_session'] = mail_session
        context.portal_webMail.moveMessages(REQUEST)

    if f0 == "Dossiers" and f1 != "--Dossiers--":
        mail_session['move_to_folder'] = REQUEST.form['move_to_folder1']
        #
        # Moving messages to the dest folder
        #
        REQUEST.SESSION['vm_session'] = mail_session
        context.portal_webMail.moveMessages(REQUEST)

#
# Redirection to the fetching Interface
#
portal_url = context.portal_url()
REQUEST.RESPONSE.redirect(portal_url + '/webmail_show?IMAPName=' + IMAPName)
