
CPSWebMail

    This is a tool to support the reading of emails via IMAP and the sending of
	mails via SMTP together with Nuxeo CPS system.
    It also provides address books support using the CPSDirectory product.

Requirements

  - Zope-2.5.1 or later.

  - CPS3.1

Installation

    Unpack the relase in the Products directory, and rename it from
    CPSWebMail-<version> to CPSWebMail. Restart Zope.

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
         Setting up default address book directories
         Directory .addressbook
         Directory addressbook
        Address book directories added
        Verifiying schemas
         Adding schema addressbook
          Field givenName.
          Field sn.
          Field id.
          Field email.
          Field fullname.
         Adding layout addressbook_search
          Widget sn
          Widget id
          Widget givenName
          Widget fullname
          Widget email
         Adding layout addressbook
          Widget sn
          Widget id
          Widget givenName
          Widget fullname
          Widget email
        Schemas and layouts related to address book directories added
        Setting up default mailing lists directory
         Directory mailinglists
        Mailing lists directory added
        Verifiying schemas
         Adding schema mailinglists
          Field emails.
          Field id.
         Adding layout mailinglists_search
          Widget id
          Widget emails
         Adding layout mailinglists
          Widget id
          Widget emails
        Schemas and layouts related to mailing lists directory added
        End of specific CPSWebmail updates

	CPSWebMail is now installed.

    Go to the cps root, and click on the portal_webMail tool in the
    ZMI. Change the default parameters set on the properties tab.

    - title
    - IMAPServer: localhost
    - IMAPPort: 25
    - SMTPServer: localhost
    - SMTPPort: 143
    - Addressbook_name: addressbook
    - AddressbookEmailProp: email
    - PrivAddressbook_name: .addressbook
    - PrivAddressbookEmailProp: email
    - Mailing_list_name: mailinglists
    - MailingEmailsProp: emails

    Each user will have to set its "imap_login" and "imap_password" in its
    preferences storred in the members directory to have access to its
    mails.


How to setup address books

    Address books are directories. We will explain how to set up default
    address books, with their schema and layout.
    The installer should have installed a default address book and a default
    private address book.
    Go to the cps root, and click on the portal_directories tool in the ZMI.

    The "global" address book is a simple CPS ZODB Directory. Add a directory
    of this type and give it the name you provided for the Addressbook_name
    property in the portal_webMail tool.
    These default values can be used:
    - title: Address book
    - Schema: addressbook
    - Schema for search: addressbook_search
    - Layout: addressbook
    - Layout for search: addressbook_search
    - ACL: directory view roles: Manager; Member
    - ACL: entry create roles: Manager
    - ACL: entry delete roles: Manager
    - ACL: entry view roles: Manager; Member
    - ACL: entry edit roles: Manager
    - Field for entry id: id
    - Field for entry title: id
    - Fields with substring search: id givenName email sn fullname
    - Field for password:

    The "private" address book is a CPS Local Directory. Add a directory of
    this type and give it the name you provided for the PrivAddressbook_name
    property in the portal_webMail tool.
    These default values can be used:
    - title: Private address book
    - Schema: addressbook
    - Schema for search: addressbook_search
    - Layout: addressbook
    - Layout for search: addressbook_search
    - ACL: directory view roles: Manager; Member
    - ACL: entry create roles: Manager; Member
    - ACL: entry delete roles: Manager; Member
    - ACL: entry view roles: Manager; Member
    - ACL: entry edit roles: Manager; Member
    - Field for entry id: id
    - Field for entry title: id
    - Fields with substring search: id givenName email sn fullname
    - Id of local directory: .addressbook (for instance, or the name you
      provided for the PrivAddressbook_name property in the portal_webMail
      tool)
    If a given user tries to access his private address book, a local
    directory will be created in its private area, with the given
    properties.

    We used a schema named "addressbook" and a layout also named
    "addressbook" in these directories.

    The schema has to have the following fields (all using the CPS String
    Field type):
    - email (or the name you provided for the AddressbookEmailProp and the
      PrivAddressbookEmailProp properties in the portal_webMail tool)
    - id
    - givenName
    - sn
    - fullname

    The layout can have the following widgets:
    - a CPS User Identifier Widget for the field id
    - CPS String Widgets for the other fields

    The schema and layouts named 'addressbook_search' can have the same
    fields than the corresponding 'addressbook' schemas and layout, except
    the layout 'fullname', as it is computed from the fields 'givenName'
    and 'sn'.

Features

- Each user has a link in its personal box to open the webmail
- Page that displays messages in a table
- Page to compose a message
- Page to search through mails
- Address book
- Folders
- Delete facility
- "Move to" facility
- Mail icon to see if the message has been read or answered
