# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com/>
# $Id$

"""
Redirection Installer

You should have installed CPSWebmail before using this script.
See file install.py.

Howto use the Redirection installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpswebmail_redirection_install (or whatever)
     title         : CPSWebMail Redirection Install (or whatever)
     Module Name   : CPSWebMail.mailredirection
     Function Name : mailredirection

 - save it
 - then click on the test tab of this external method
"""

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CPSWebMail.Extensions.install import CPSWebMailInstaller

def mailredirection(self):

    installer = CPSWebMailInstaller(self)

    # LDAP schema modification
    installer.log(" Setting up LDAP schema items")
    acl = installer.portal.acl_users
    try:
        acl.manage_addLDAPSchemaItem('mailForwardingAddress',
                                     friendly_name='Mail forwarding address',
                                     )
        acl.manage_addLDAPSchemaItem('deliveryMode',
                                     friendly_name='Delivery mode',
                                     )
        acl.manage_addLDAPSchemaItem('mail',
                                     public_name='email',
                                     )
        installer.log("LDAP schema has been modified")
        installer.log("Warning: LDAP schema item 'mail' should be mapped to 'email'")
    except:
        installer.log("LDAP Schema could not be modified.\n Please Check if your LDAP User Folder is correctly installed")

    # Members schema modification
    installer.log(" Setting up members schema items")
    portal = installer.portal
    stool = portal.portal_schemas
    memberschema = stool.members
    fields = memberschema.objectIds()
    pmd = portal.portal_memberdata
    for each in ('mailForwardingAddress', 'deliveryMode'):
        if not 'f__' + each in fields:
            memberschema.addField(each, 'CPS String Field',
                                  acl_write_roles_str='Manager, Owner')
            if not pmd.hasProperty(each):
                pmd.manage_addProperty(each, '', 'string')

    installer.log(" Setting up members layout items")
    ltool = portal.portal_layouts
    memberlayout = ltool.members
    widgets = memberlayout.objectIds()
    layout_def = memberlayout.getLayoutDefinition()
    if not 'w__mailForwardingAddress' in widgets:
        memberlayout.addWidget('mailForwardingAddress',
                               'String Widget',
                               fields='mailForwardingAddress',
                               label='label_mailForwardingAddress',
                               label_edit='label_mailForwardingAddress',
                               is_i18n=1,
                               display_width=30,
                               size_max=0,
                               )
        layout_def['rows'] += [[{'ncols': 1, 'widget_id': 'mailForwardingAddress'}]]

    if not 'w__deliveryMode' in widgets:
        memberlayout.addWidget('deliveryMode',
                               'Generic Select Widget',
                               fields='deliveryMode',
                               label='label_deliveryMode',
                               label_edit='label_deliveryMode',
                               help='deliveryMode_help',
                               is_required=1,
                               is_i18n=1,
                               vocabulary='deliveryMode',
                               render_format='select',
                               )
        layout_def['rows'] += [[{'ncols': 1, 'widget_id': 'deliveryMode'}]]

    memberlayout.setLayoutDefinition(layout_def)

    # Setup vocabulary needed in the deliveryMode widget
    installer.log("Setting up vocabulary needed in the deliveryMode widget")
    deliveryMode_vocabulary = {
        'data': {
            'tuples': (
                ('noforward', 'No forward'),
                ('forwardonly', 'Forward only'),
                ('local', 'Local'),
                ),
            },
        }
    vocabulary = {
        'deliveryMode': deliveryMode_vocabulary,
        }
    installer.verifyVocabularies(vocabulary)

    return installer.logResult()
