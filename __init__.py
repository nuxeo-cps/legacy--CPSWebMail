#
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com>
# See LICENSE.TXT for licensing information
#

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

import WebMailTool

tools = (WebMailTool.WebMailTool,)

registerDirectory('skins/cpswebmail_default', globals())
registerDirectory('skins/cpswebmail_images', globals())


def initialize(registrar):
    """ Register the WebMailTool class """
    utils.ToolInit("CPS WebMail Tool",
        tools=tools,
        product_name='CPSWebMail',
        icon='tool.gif',
    ).initialize(registrar)

