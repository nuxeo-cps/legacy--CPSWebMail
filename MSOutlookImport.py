# -*- coding: iso-8859-15 -*-
#                                           
# Copyright 2002 Nuxeo SARL <http://www.nuxeo.com/>
# See LICENSE.txt for licensing information 
#

"""MSOutlookImport class

FIXME: need some rework to make it fully general"""

import re

class MSOutlookImporter:
    """
    This class allows a NuxWebMail user to import an addressbook
    from their MS-Outlook (r) to the NuxWebMail one
    """

    def __init__(self, file):
        """Default Constuctor"""
        self.file = file

    def getContacts(self):
        """Return a list of dictionnary"""
        lines = self.file.readlines()
        contacts  = [] 
        for line in lines:
            contacts.append(line.split(';'))
            
        res = []
        i = 0
        fr = {}
        for contact in contacts:
            if i == 0:
                #
                # Case if this is the first ligne
                # with the params order
                # Fr version
                #
                k = -1
                for j in contact:
                    k = k + 1
                    if j.strip() == "Prénom":
                        fr['vorname'] = k
                    else:
                        #
                        # The only one with non ascii chars
                        #
                        p = re.search('Nom*', j)
                        if p:
                            fr['name'] = k
                        else:
                            if j.strip() == "Adresse de messagerie":
                                fr['mail'] = k
                            
            else:
                #
                # Parsing the contacts
                #
                res.append({'name': contact[fr['name']],
                            'vorname': contact[fr['vorname']],
                            'email': contact[fr['mail']]})
            i = i + 1

        return res
