# $Id$
# this should be used instead of cpsupdate
# note that cpsupdate is still required

import os
from App.Extensions import getPath

cpsversion = 0
try:
    import Products.NuxCPS
    cpsversion = 2
except ImportError:
    pass
try:
    import Products.CPSCore
    cpsversion = 3
except ImportError:
    pass

if not cpsversion:
    raise ImportError('NuxWebMail install script requires CPS Version 2 or 3')

def webmailupdate(self):
    log = []
    pr = log.append
    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("<html><head><title>NUXWEBMAIL UPDATE</title></head><body><pre>")

    pr("Starting NuxWebMail update")

    pr("")

    portal = self.portal_url.getPortalObject()

    # importing .po files
    if cpsversion == 2:
        mcat = portal.portal_messages
    else:
        mcat = portal.Localizer.default
    pr(" Checking available languages")
    podir = os.path.join('Products', 'NuxWebMail')
    popath = getPath(podir, 'Install')
    if popath is None:
        pr(" !!! Unable to find .po dir")
    else:
        pr("  Checking installable languages")
        langs = []
        for file in os.listdir(popath):
            if file.endswith('.po'):
                lang = '.'.join(file.split('.')[:-1])
                pr("   Found language %s" % (lang, ))
                langs.append(lang)
        avail_langs = mcat.get_languages()

        append_langs = [lang for lang in langs if lang not in avail_langs]
        if append_langs:
            pr("  Will add %s to portal_messages" % (', '.join(append_langs), ))
        for lang in append_langs:
            pr("   Adding %s" % (lang, ))
            mcat.manage_addLanguage(lang)
        if langs:
            pr("  Will import dictionaries for %s" % (', '.join(langs), ))
        for lang in langs:
            pr("   Importing %s.po" % (lang, ))
            lang_po_path = os.path.join(popath, lang+'.po')
            lang_file = open(lang_po_path)
            mcat.manage_import(lang, lang_file)

    # Setup skins
    skins = ('cps_nuxwebmail',)
    if cpsversion == 2:
        paths = {
            'cps_nuxwebmail': 'Products/NuxWebMail/skins',
        }
    else:
        paths = {
            'cps_nuxwebmail': 'Products/NuxWebMail/skins/cps_nuxwebmail',
        }
    skin_installed = 0
    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            skin_installed = 1
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
            pr("  Creating skin")

    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        pr(" Fixup of skin %s" % skin_name)
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path:
            try:
                index = path.index('custom') + 1 # Put it just after "custom"
            except ValueError: # custom not in path. Put our skins first.
                index = 0
            path = path[:index] + list(skins) + path[index:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
    pr(" Resetting skin cache")
    portal._v_skindata = None
    portal.setupCurrentSkin()

    # Creating tool
    pr(" Adding Tool")
    if 'portal_webMail' not in portal.objectIds():
        portal.manage_addProduct["NuxWebMail"].manage_addTool('Portal WebMail Tool')

    # Adding action
    pr(" Setting up action")
    portal['portal_actions'].addAction(
        id='webmail',
        name='_list_mail_',
        action='string: ${portal_url}/webmail_show',
        condition='',
        permission='View',
        category='user')

    if cpsversion == 3:
        # Add to member schemas
        pr(" Setting up schemas and layouts")
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
            pr(" Schema %s" % id)
            if id in stool.objectIds():
                prok()
            else:
                pr("  Installing.")
                schema = stool.manage_addCPSSchema(id)
                for field_id, fieldinfo in info.items():
                    pr("   Field %s." % field_id)
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
            pr(" Layout %s" % id)
            if id in ltool.objectIds():
                prok()
            else:
                pr("  Installing.")
                layout = ltool.manage_addCPSLayout(id)
                for widget_id, widgetinfo in info['widgets'].items():
                    pr("   Widget %s" % widget_id)
                    widget = layout.manage_addCPSWidget(widget_id, widgetinfo['type'],
                                                        **widgetinfo['data'])
                layout.setLayoutDefinition(info['layout'])
                layout.manage_changeProperties(**info['layout'])

    pr("End of specific NuxWebmail updates")

    pr("</pre></body></html>")
    return '\n'.join(log)
