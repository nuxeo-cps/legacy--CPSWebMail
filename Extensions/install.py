# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""
CPSWebMail Installer

Howto use the CPSWebMail installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpswebmail_install (or whatever)
     title         : CPSWebMail Install (or whatever)
     Module Name   : CPSWebMail.install
     Function Name : install

 - save it
 - then click on the test tab of this external method
"""

# this should be used instead of cpsupdate
# note that cpsupdate is still required

import os
from App.Extensions import getPath
from Products.CPSInstaller.CPSInstaller import CPSInstaller

class CPSWebMailInstaller(CPSInstaller):

    product_name = 'CPSWebMail'

    SKINS = {
        'cpswebmail_default': 'Products/CPSWebMail/skins/cpswebmail_default',
        'cpswebmail_images': 'Products/CPSWebMail/skins/cpswebmail_images',
        }

    def install(self):
        self.log("Starting CPSWebMail update")
        self.log("")

        self.setupTranslations()
        self.verifySkins(self.SKINS)
        self.resetSkinCache()
        self.verifyTool('portal_webMail', 'CPSWebMail', 'Portal WebMail Tool')
        action = {
            'id': 'webmail',
            'name': '_list_mail_',
            'action': 'string: ${portal_url}/webmail_show',
            'condition': 'member',
            'permission': 'View',
            'category': 'user',
            }
        self.verifyAction('portal_actions', **action)

        self.setupMembersSchemasAndLayouts()

        self.log("End of specific CPSWebmail updates")


    def setupMembersSchemasAndLayouts(self):
        # Add to member schemas
        self.log(" Setting up schemas and layouts")
        portal = self.portal
        stool = portal.portal_schemas
        memberschema = stool.members
        fields = memberschema.objectIds()
        pmd = portal.portal_memberdata
        for each in ('imap_login', 'imap_password'):
            if not 'f__' + each in fields:
                memberschema.addField(each, 'CPS String Field',
                                      acl_write_roles_str='Manager, Owner')
            if not pmd.hasProperty(each):
                pmd.manage_addProperty(each, '', 'string')

        ltool = portal.portal_layouts
        memberlayout = ltool.members
        widgets = memberlayout.objectIds()
        layout_def = memberlayout.getLayoutDefinition()
        if not 'w__imap_login' in widgets:
            memberlayout.addWidget('imap_login', 'String Widget',
                                   fields='imap_login',
                                   label='label_imap_login',
                                   label_edit='label_imap_login',
                                   is_i18n=1,
                                   display_width=20,
                                   size_max=0,
                                   )
            layout_def['rows'] += [[{'ncols': 1, 'widget_id': 'imap_login'}]]

        if not 'w__imap_password' in widgets:
            memberlayout.addWidget('imap_password', 'Password Widget',
                                   fields='imap_password',
                                   label='label_imap_password',
                                   label_edit='label_imap_password',
                                   is_i18n=1,
                                   display_width=20,
                                   size_max=0,
                                   )
            layout_def['rows'] += [[{'ncols': 1, 'widget_id': 'imap_password'}]]

        memberlayout.setLayoutDefinition(layout_def)

        # Adding the emailaddress schema + layout
        schemas = {
            'emailaddress': {
                'email': {
                    'type': 'CPS String Field',
                    'data': {
                        'default_expr': 'string:',
                        'is_searchabletext': 0,
                        'acl_read_permissions': '',
                        'acl_read_roles': '',
                        'acl_read_expr': '',
                        'acl_write_permissions': '',
                        'acl_write_roles': '',
                        'acl_write_expr': '',
                        'read_ignore_storage': 0,
                        'read_process_expr': '',
                        'read_process_dependent_fields': [],
                        'write_ignore_storage': 0,
                        'write_process_expr': '',
                        },
                    },
                'name': {
                    'type': 'CPS String Field',
                    'data': {
                        'default_expr': 'string:',
                        'is_searchabletext': 0,
                        'acl_read_permissions': '',
                        'acl_read_roles': '',
                        'acl_read_expr': '',
                        'acl_write_permissions': '',
                        'acl_write_roles': '',
                        'acl_write_expr': '',
                        'read_ignore_storage': 0,
                        'read_process_expr': '',
                        'read_process_dependent_fields': [],
                        'write_ignore_storage': 0,
                        'write_process_expr': '',
                        },
                    },
                'index': {
                    'type': 'CPS String Field',
                    'data': {
                        'default_expr': 'python:portal.getUniqueID()',
                        'is_searchabletext': 0,
                        'acl_read_permissions': '',
                        'acl_read_roles': '',
                        'acl_read_expr': '',
                        'acl_write_permissions': '',
                        'acl_write_roles': '',
                        'acl_write_expr': '',
                        'read_ignore_storage': 0,
                        'read_process_expr': '',
                        'read_process_dependent_fields': [],
                        'write_ignore_storage': 1,
                        'write_process_expr': '',
                        },
                    },
                },
            }

        for id, info in schemas.items():
            self.log(" Schema %s" % id)
            if id in stool.objectIds():
                self.log(" Already correctly installed")
            else:
                self.log("  Installing.")
                schema = stool.manage_addCPSSchema(id)
                for field_id, fieldinfo in info.items():
                    self.log("   Field %s." % field_id)
                    schema.manage_addField(field_id, fieldinfo['type'],
                                           **fieldinfo['data'])

        layouts = {
            'emailaddress': {
                'widgets': {
                    'email': {
                        'type': 'Email Widget',
                        'data': {
                            'title': 'Email',
                            'fields': ['email'],
                            'is_required': 0,
                            'label': 'label_email',
                            'label_edit': 'label_email',
                            'description': '',
                            'help': '',
                            'is_i18n': 1,
                            'readonly_layout_modes': [],
                            'hidden_layout_modes': [],
                            'hidden_readonly_layout_modes': [],
                            'hidden_empty': 0,
                            'hidden_if_expr': '',
                            'css_class': '',
                            'display_width': 20,
                            'size_max': 0,
                            },
                        },
                    'name': {
                        'type': 'String Widget',
                        'data': {
                            'title': 'Name',
                            'fields': ['name'],
                            'is_required': 0,
                            'label': 'label_name',
                            'label_edit': 'label_name',
                            'description': '',
                            'help': '',
                            'is_i18n': 1,
                            'readonly_layout_modes': [],
                            'hidden_layout_modes': [],
                            'hidden_readonly_layout_modes': [],
                            'hidden_empty': 0,
                            'hidden_if_expr': '',
                            'css_class': '',
                            'display_width': 20,
                            'size_max': 0,
                            },
                        },
                    'index': {
                        'type': 'String Widget',
                        'data': {
                            'title': '',
                            'fields': ['index'],
                            'is_required': 0,
                            'label': 'index',
                            'label_edit': 'index',
                            'description': '',
                            'help': '',
                            'is_i18n': 0,
                            'readonly_layout_modes': ['search'],
                            'hidden_layout_modes': [],
                            'hidden_readonly_layout_modes': [],
                            'hidden_empty': 0,
                            'hidden_if_expr': '',
                            'css_class': '',
                            'display_width': 20,
                            'size_max': 0,
                            },
                        },
                    },
                'layout': {
                     'style_prefix': 'layout_dir_',
                     'flexible_widgets': [],
                     'ncols': 1,
                     'rows': [
                          [{'ncols': 1, 'widget_id': 'email'},
                           ],
                          [{'ncols': 1, 'widget_id': 'name'},
                           ],
                          [{'ncols': 1, 'widget_id': 'index'},
                           ],
                          ],
                     },
                },
            }

        for id, info in layouts.items():
            self.log(" Layout %s" % id)
            if id in ltool.objectIds():
                self.log(" Already correctly installed")
            else:
                self.log("  Installing.")
                layout = ltool.manage_addCPSLayout(id)
                for widget_id, widgetinfo in info['widgets'].items():
                    self.log("   Widget %s" % widget_id)
                    widget = layout.manage_addCPSWidget(widget_id, widgetinfo['type'],
                                                        **widgetinfo['data'])
                layout.setLayoutDefinition(info['layout'])
                layout.manage_changeProperties(**info['layout'])


def install(self):
    installer = CPSWebMailInstaller(self)
    installer.install()
    return installer.logResult()
