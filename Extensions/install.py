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
        self.setupDefaultAddressBooks()

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

    def setupDefaultAddressBooks(self):
        self.log(" Setting up default address book directories")
        addressbook_directory = {
            'type': ' CPS ZODB Directory',
            'data': {
                'title': 'label_address_book',
                'schema': 'addressbook',
                'layout': 'addressbook',
                'layout_search': 'addressbook_search',
                'acl_directory_view_roles': 'Manager; Member',
                'acl_entry_create_roles': 'Manager',
                'acl_entry_delete_roles': 'Manager',
                'acl_entry_view_roles': 'Manager; Member',
                'acl_entry_edit_roles': 'Manager',
                'id_field': 'id',
                'title_field': 'id',
                'search_substring_fields': ['fullname', 'email'],
                },
            }

        privaddressbook_directory = {
            'type': ' CPS Local Directory',
            'data': {
                'title': 'label_personal_addressbook',
                'schema': 'addressbook',
                'layout': 'addressbook',
                'layout_search': 'addressbook_search',
                'acl_directory_view_roles': 'Manager; Member',
                'acl_entry_create_roles': 'Manager; Member',
                'acl_entry_delete_roles': 'Manager; Member',
                'acl_entry_view_roles': 'Manager; Member',
                'acl_entry_edit_roles': 'Manager; Member',
                'id_field': 'id',
                'title_field': 'id',
                'search_substring_fields': ['fullname', 'email'],
                'directory_id': '.addressbook',
                },
            }

        directories = {
            'addressbook': addressbook_directory,
            '.addressbook': privaddressbook_directory,
            }

        self.verifyDirectories(directories)

        self.log("Address book directories added")

        portal = self.portal

        addressbook_schema = {
            'email': {
                'type': 'CPS String Field',
                'data': {
                    'default_expr': 'string:',
                    },
                },
            'fullname': {
                'type': 'CPS String Field',
                'data': {
                    'default_expr': 'string:',
                    'read_ignore_storage': 1,
                    'read_process_expr': """python:(givenName + " " + sn).strip() or id""",
                    'read_process_dependent_fields': ('givenName', 'sn', 'id'),
                    'write_ignore_storage': 1,
                    },
                },
            'id': {
                'type': 'CPS String Field',
                'data': {
                    'default_expr': 'string:',
                    },
                },
            'givenName': {
                'type': 'CPS String Field',
                'data': {
                    'default_expr': 'string:',
                    },
                },
            'sn': {
                'type': 'CPS String Field',
                'data': {
                    'default_expr': 'string:',
                    },
                },
            }

        schemas = {
            'addressbook': addressbook_schema,
            }
        self.verifySchemas(schemas)

        addressbook_layout = {
            'widgets': {
                'fullname': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('fullname',),
                        'is_required': 0,
                        'label': 'label_full_name',
                        'label_edit': 'label_full_name',
                        'is_i18n': 1,
                        'display_width': 30,
                        'size_max': 0,
                        },
                    },
                'id': {
                    'type': 'User Identifier Widget',
                    'data': {
                        'fields': ('id',),
                        'is_required': 1,
                        'label': 'label_user_name',
                        'label_edit': 'label_user_name',
                        'is_i18n': 1,
                        'readonly_layout_modes': ('edit',),
                        'display_width': 30,
                        'size_max': 256,
                        },
                    },
                'givenName': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('givenName',),
                        'is_required': 0,
                        'label': 'label_first_name',
                        'label_edit': 'label_first_name',
                        'is_i18n': 1,
                        'display_width': 20,
                        'size_max': 0,
                        },
                    },
                'sn': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('sn',),
                        'is_required': 1,
                        'label': 'label_last_name',
                        'label_edit': 'label_last_name',
                        'is_i18n': 1,
                        'display_width': 20,
                        'size_max': 0,
                        },
                    },
                'email': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('email',),
                        'is_required': 0,
                        'label': 'label_email',
                        'label_edit': 'label_email',
                        'is_i18n': 1,
                        'display_width': 30,
                        'size_max': 0,
                        },
                    },
                },
            'layout': {
                'style_prefix': 'layout_dir_',
                'flexible_widgets': [],
                'ncols': 2,
                'rows': [
                    [{'ncols': 2, 'widget_id': 'id'},
                     ],
                    [{'ncols': 2, 'widget_id': 'fullname'},
                     ],
                    [{'ncols': 2, 'widget_id': 'email'},
                     ],
                    [{'ncols': 2, 'widget_id': 'givenName'},
                     ],
                    [{'ncols': 2, 'widget_id': 'sn'},
                     ],
                    ],
                },
            }

        addressbook_search_layout = {
            'widgets': {
                'fullname': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('fullname',),
                        'is_required': 0,
                        'label': 'label_full_name',
                        'label_edit': 'label_full_name',
                        'is_i18n': 1,
                        'display_width': 30,
                        'size_max': 0,
                        },
                    },
                'id': {
                    'type': 'User Identifier Widget',
                    'data': {
                        'fields': ('id',),
                        'is_required': 0,
                        'label': 'label_user_name',
                        'label_edit': 'label_user_name',
                        'is_i18n': 1,
                        'readonly_layout_modes': ('edit',),
                        'display_width': 30,
                        'size_max': 256,
                        },
                    },
                'givenName': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('givenName',),
                        'is_required': 0,
                        'label': 'label_first_name',
                        'label_edit': 'label_first_name',
                        'is_i18n': 1,
                        'display_width': 20,
                        'size_max': 0,
                        },
                    },
                'sn': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('sn',),
                        'is_required': 0,
                        'label': 'label_last_name',
                        'label_edit': 'label_last_name',
                        'is_i18n': 1,
                        'display_width': 20,
                        'size_max': 0,
                        },
                    },
                'email': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ('email',),
                        'is_required': 0,
                        'label': 'label_email',
                        'label_edit': 'label_email',
                        'is_i18n': 1,
                        'display_width': 30,
                        'size_max': 0,
                        },
                    },
                },
            'layout': {
                'style_prefix': 'layout_dir_',
                'flexible_widgets': [],
                'ncols': 2,
                'rows': [
                    [{'ncols': 2, 'widget_id': 'id'},
                     ],
                    [{'ncols': 2, 'widget_id': 'fullname'},
                     ],
                    [{'ncols': 2, 'widget_id': 'email'},
                     ],
                    [{'ncols': 2, 'widget_id': 'givenName'},
                     ],
                    [{'ncols': 2, 'widget_id': 'sn'},
                     ],
                    ],
                },
            }

        layouts = {
            'addressbook': addressbook_layout,
            'addressbook_search': addressbook_search_layout,
            }
        self.verifyLayouts(layouts)

        self.log("Schemas and layouts related to address book directories added")


def install(self):
    installer = CPSWebMailInstaller(self)
    installer.install()
    return installer.logResult()
