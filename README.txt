CPSWebMail

	This is a tool to support the reading of emails via IMAP and the sending of
	mails via SMTP together with Nuxeo CPS system.

Requirements

  - Zope-2.5.1 or later.

  - A special WebMail from Maxime Raffin (Included)

  - CPS3.1

Installation

  Unpack the relase in the Products directory, and rename it from
  CPSWebMail-<version> to CPSWebMail. Included in the release is the required
  version of WebMail. Unpack this file in the Products directory as
  well. Restart Zope.

  In the cps root, create an External Method object called cpswebmail_update
  or something similar. The settings should be:
  	Module Name:   CPSWebMail.install
  	Function Name: install

  After creating, open the External Method object and click the "Test" tab to
  run it. The output should look similar to this:

        Starting CPSWebMail update

         Checking available languages
          Checking installable languages
            Available languages: ('en', 'fr')
            Importing en.po into 'en' locale
            Importing fr.po into 'fr' locale
        Verifying skins
         FS Directory View 'cpswebmail_default'
          Creating skin
         FS Directory View 'cpswebmail_images'
          Creating skin
         Fixup of skin Basic
        Resetting skin cache
        Verifying tool portal_webMail
         Adding
         Setting up action
         Setting up schemas and layouts
         Schema emailaddress
          Installing.
           Field email.
           Field name.
           Field index.
         Layout emailaddress
          Installing.
           Widget email
           Widget name
           Widget index
        End of specific CPSWebmail updates

	CPSWebMail is now installed.

    Go to the cps root, and click on the portal_webMail tool in the
    ZMI. Change the default parameters set on the properties tab.

         title
         IMAPServer
         IMAPPort
         SMTPServer
         SMTPPort
         Addressbook_name
         AddressbookEmailProp
         PrivAddressbook_name
         PrivAddressbookEmailProp
         Mailing_list_name
         MailingEmailsProp

    Each user will have to set its "imap_login" and "imap_password" in its
    preferences storred in the members directory to have access to its
    mails.


Features

- Each user has a link in its personal box to open the webmail
- Page that displays messages
- Page to compose a message
- Page to search through mails
- Address book
- Folders
- Delete facility
- "Move to" facility
- Mail icon to see if the message has been read
- 
