##parameters=listing_size, IMAPName, sortmail, start, sort, order, REQUEST
# $Id$

context.portal_webMail.setListingSizeSession(listing_size, REQUEST)

#
# Redirection to the previous page, but back to start=0 page so
# that the batch message and its links are ok
#
portal_url = context.portal_url()
url = '/webmail_fetch?IMAPName=' + IMAPName +\
      '&sortmail=' + sortmail + '&start=0' +\
      '&sort=' + sort + '&order=' + order

REQUEST.RESPONSE.redirect(portal_url+url)
