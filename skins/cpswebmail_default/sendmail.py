##parameters=REQUEST
## Script (Python) "sendmail.py"

#
# Create a new mail session object
#
context.portal_webMail.createMailSession(REQUEST)

#
# Sending message...
#

read_flag = REQUEST.form.get('a_read', "")

x = context.portal_webMail.sendMail(REQUEST, read_flag)

if x == 0:
    # All is good
    context.portal_webMail.endMailSession(REQUEST)
    return context.webmail_show(REQUEST)

else:
    # To define ?
    return 1

