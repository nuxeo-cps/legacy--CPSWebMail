##parameters=listing_size, IMAPName, sortmail, start, sort, order, REQUEST
# $Id$

context.portal_webMail.setListingSizeSession(listing_size, REQUEST)

#
# Redirection to the previous page
#
portal_url = context.portal_url()
url = '/webmail_fetch?IMAPName=' + IMAPName +\
      '&sortmail=' + sortmail + '&start=' + start +\
      '&sort=' + sort + '&order=' + order

REQUEST.RESPONSE.redirect(portal_url+url)
