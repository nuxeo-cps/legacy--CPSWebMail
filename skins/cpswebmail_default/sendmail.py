##parameters=REQUEST
## Script (Python) "sendmail.py"

#
# Create a new mail session object
#
context.portal_webMail.createMailSession(REQUEST)

#
# Sending message...
#

read_flag = int(REQUEST.form.get('a_read', 0))

x = context.portal_webMail.sendMail(REQUEST, read_flag)

if x == 0:
    # All is good
    context.portal_webMail.endMailSession(REQUEST)
    return context.webmail_show(REQUEST)
else:
    # To define ?
    # this only happens when the email do not have any recipients
    # so I gusess we should redirect to the edit message form, with
    # a message...
    msg = "cpswebmail_enter_recipient"
    portal_url = context.portal_url()
    REQUEST.RESPONSE.redirect(portal_url + '/edit_message?portal_status_message=' + msg)

    return 1

