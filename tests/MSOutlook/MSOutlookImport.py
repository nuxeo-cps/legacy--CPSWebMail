#                                           
# Copyright 2002 Nuxeo SARL                 
# See LICENSE.TXT for licensing information 
#

"""
   MSOutlookImport class
"""

import string
import re

class MSOutlookImport:
    """
    This class allow NuxWebMail user to import an addressbook
    from their outlook to the NuxWebMail one
    """

    def __init__(self, file):
        """ Default Constuctor """
        self.File = file

    def do_list(self):
        """ Return a list of dictionnary """
        all_ligne = self.File.readlines()
        contacts  = [] 
        for line in all_ligne:
            contacts.append(string.split(line, ';'))
            
        res = []
        i   = 0
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
                    if string.strip(j) == "Prénom":
                        fr['vorname'] = k
                    else:
                        #
                        # The only one with non ascii chars
                        #
                        p = re.search('Nom*', j)
                        try:
                            pat = p.group(0)
                        except:
                            pat = 0
                        if pat:
                            fr['name'] = k
                        else:
                            if string.strip(j) == "Adresse de messagerie":
                                fr['mail'] = k
                            
            else:
                #
                # Parsing the contacts
                #
                res.append({'name'    : contact[fr['name']],
                            'vorname' : contact[fr['vorname']],
                            'email'   : contact[fr['mail']]})
            i = i + 1

        return res
