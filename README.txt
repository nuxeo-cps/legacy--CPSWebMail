--------------------------------------------------
CPSWebMail README
--------------------------------------------------

$Id$

Authors:
- Anahide Tchertchian (at@nuxeo.com)

--------------------------------------------------
Summary
--------------------------------------------------

- Introduction
- Features
- Installation
- How to setup address books

--------------------------------------------------
Introduction
--------------------------------------------------

    This is a tool to support the reading of emails via IMAP and the sending of
	mails via SMTP together with Nuxeo CPS system.

    It also provides address books support using the CPSDirectory product.


--------------------------------------------------
Features
--------------------------------------------------

    - Each user has a link in its personal box to open the webmail,
      provided that all users have accounts on the same mail server.

    - Messages handling:
      - Messages can be displayed in a table, sortable by subject, sender
        and date. The table has the following columns : an icon displaying
        the 'state' of the message (not read, read, answerd, forwarded,
        deleted), subject, sender, date, size.
        It is possible to view the folder in which messages will be
        retrieved.
        Message scan be deleted or moved to another folder using that
        interface. Deleted messages are coiped into the 'Trash' folder.
      - Messages can be viewed using an interface that provides several
        actions : 'reply', 'replay to all', 'forward'. It is also possible
        to move the message into another folder.
      - Messages can be composed using an interface that provides access
        to the address book contacts. It is also possible to send an
        acknoledment of read with the message, and to attach files to it.
        Messages can be saved as drafts in the 'Draft' folder. When a
        message is sent, it is copied into the 'Sent' folder.
      - Messages can be searched according to different criteria : the
        folder they're in, and words contained in the body of the message,
        the subject, the sender, the recipient(s), and an interval of dates
        can be provided too.
        Messages returned by the search are displayed in a table similar to
        the one discribed above.
      - IMAP folders can be managed through another interface: it is
        possible to add or delete (sub)folders. Folders that are deleted are
        copied into the 'Trash' Folder, as well as the subfolders and
        messages they may contain.

    - Address books handling:

      Address books are CPS Directories.

      It is possible to chose recipients to a message into four kinds of
      address books. Four default addressbooks are set up when installing
      the product, but it is possible to change them or to use existing
      directories, as long as these directories follow the requirements (see
      below how to set up proper address books).

      1. The global address book can be, for instance, the directory of all
         the members using the site, but it can be a different one.
         This address book is not required since version 0.6.0.
      2. The personal address book stores contacts that are only visible to
         the user: the user is able to add/delete/edit its own contacts.
         This address book is personal and is not required: leave the
         'PrivAddressbook_name' property blank if you do not want users to
         have access to this directory.
      3. The personal address book with links stores links towards the
         global address book, so that the user can benefite from the updates
         made on this address book.
         This directory is also personal and is not required: leave the
         'PrivAddressbookLinks_name' property blank if you do not want users
         to have access to this directory.
      4. The mailing lists address books is able to store several names of
         mailing lists, each mailing list being an entry of the directory.
         It is possible to set a list of email addresses attached to the
         mailing list name.
         This directory is also personal and is not required: leave the
         'Mailing_list_name' property blank if you do not want users to
         have access to this directory.

      All these address books are accessible through the 'Address book' link
      on the webmail pages, but they are also accessible through the
      'Directories' link on the site.

      If you do not want to use the address books that are set up during the
      installation, you should delete manually these directories in the ZMI.
      You should also delete the related schemas, layouts and vocabularies.
      See below for more information on how to setup address books.

    - Address books related features:

      There are three other ways to chose recipients to a message, without
      having to use new directories. These features are enabled if you check
      the appropriate properties in the properties tab of the portal_webMail
      tool in the ZMI.

      1. Enable Members Mailing: users will have access to the members
         directory. This is only useful if your global address book is not
         the members directory.

      2. Enable Groups Mailing: users will have access to the list of groups
         defined on the site, and will be able to chose recipients from
         their membership to a group.
         Groups directory choice is configurable.

      3. Enable Workspace Members Mailing: users will have access to a
         search interface and will be able to select all users havins a
         given role in a given workspace (please note that they will not be
         able to select workspaces if they do not have view permission on it).


--------------------------------------------------
Installation
--------------------------------------------------

Please refer to the INSTALL.txt file


--------------------------------------------------
How to setup address books
--------------------------------------------------

    The installer should have installed the four default address books.

    If you chose not to use these address books, you should better delete
    them.

    It is possible to change the schemas and layouts these address books
    use, but all the fields set on the default 'addressbook' schema are
    required for the address book feature to work properly.
    Below is a description of how these address books should be set. Please
    keep in mind the following warnings as you read:

    WARNINGS:
    1. CHANGES MADE ON THE CPS Local Directory WILL NOT BE
       REPERCUTED ON THE PERSONAL DIRECTORIES THAT HAVE ALREADY
       BEEN CREATED.
    2. EXECUTING THE INSTALLER WILL ERASE ALL THE MODIFICATIONS YOU MADE ON
       DIRECTORIES, SCHEMAS AND LAYOUTS SET BY CPSWebMail.
    3. The private address book and the private address book with links
       should use the same schema than the global address book: CPSWebMail
       enable users to copy contacts from the global address book into the
       personal address book, and to add links into the personal address
       book with links, pointing towards entries of the global address
       book.
       This schema should also be similar to the members schema (at least
       concerning the required fields) if you want to use the address books
       related features (see the description of these fetaures above).


    ---------------
    - Directories -
    ---------------

      Go to the cps root, and click on the portal_directories tool in the ZMI.

      The global address book is a CPS ZODB Directory. You can chose to use
      the 'members' directory, but you can use another one by adding a
      directory with this type and give it the name you provided for the
      Addressbook_name property in the portal_webMail tool.

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

      The private address book is a CPS Local Directory, that creates CPS
      ZODB directories in the users'home folders. Add a directory of
      this type and give it the name you provided for the
      PrivAddressbook_name property in the portal_webMail tool.

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
      - Id of local directory:
      - Type of local directory : CPS ZODB Directory (do not change)

      If a given user tries to access his private address book, a CPS ZODB
      Directory will be created in its private area, with the same name and
      the given properties.

      The private address book with links is a CPS Local Directory too, but
      it creates CPS Indirect directories in the users' home folders. Add a
      directory of this type and give it the name you provided for the
      PrivAddressbookLinks_name property in the portal_webMail tool.

      These default values can be used:
      - title: Private address book with links
      - Schema: addressbook
      - Schema for search: addressbook_search
      - Layout: addressbook_links
      - Layout for search: addressbook_search
      - ACL: directory view roles: Manager; Member
      - ACL: entry create roles: Manager; Member
      - ACL: entry delete roles: Manager; Member
      - ACL: entry view roles: Manager; Member
      - ACL: entry edit roles: Manager; Member
      - Field for entry id: id
      - Field for entry title: id
      - Fields with substring search: id
      - Id of local directory: addressbook members
      - Type of local directory : CPS Indirect Directory (do not change)

      If a given user tries to access his private address book, a CPS
      Indirect Directory will be created in its private area, with the same
      name and the given properties.
      If you have chosen to use a global address book directory with a
      different name than 'addressbook' ('members', for instance), you
      have to change the id of the local directory property according to
      it.

      WARNINGS:
      1. CHANGES MADE ON THE CPS Local Directory WILL NOT BE
         REPERCUTED ON THE PERSONAL DIRECTORIES THAT HAVE ALREADY
         BEEN CREATED.
      2. EXECUTING THE INSTALLER WILL ERASE ALL THE MODIFICATIONS YOU MADE ON
         DIRECTORIES, SCHEMAS AND LAYOUTS SET BY CPSWebMail.
      2. The private address book and the private address book with links
         should use the same schema than the global address book: CPSWebMail
         enable users to copy contacts from the global address book into the
         personal address book, and to add links into the personal address
         book with links, pointing towards entries of the global address
         book. These features could break if you use a different schema.


    -------------------------------------
    - Schemas, layouts and Vocabularies -
    -------------------------------------

      Schemas can be handled by going to the cps root, and clicking on the
      portal_schemas tool in the ZMI.
      Layouts can be handled by going to the cps root, and clicking on the
      portal_layouts tool in the ZMI.

      The default address books use the following schemas:
      - addressbook
      - addressbook_search

      They use the following layouts:
      - addressbook
      - addressbook_search
      - addressbook_links

      The 'addressbook' schema has to have the following fields (all using
      the CPS String Field type):
      - email (or the name you provided for the AddressbookEmailProp and the
        PrivAddressbookEmailProp properties in the portal_webMail tool)
      - id
      - givenName
      - sn
      - fullname

      The layout can have the following widgets:
      - A CPS User Identifier Widget for the field id
      - CPS String Widgets for the other fields

      The schema and the layout named 'addressbook_search' can have the same
      fields than the corresponding 'addressbook' schemas and layout, except
      the layout 'fullname', as it is computed from the fields 'givenName'
      and 'sn'.

      The 'addressbook_links' layout is a bit more complicated. It has to be
      like the 'addressbook' layout, except that:
      - All widgets, except 'id', should be hidden in layout modes create
        and edit.
      - The better way to set the widget storing the id is to set it as a
        'CPS Directory Entry Widget', using a vocabulary with type 'CPS Indirect
        Directory Vocabulary', with the name of the indirect directory in the
        'directory' property, and with popup mode 'seach'. This widget will
        present the entries accepted in the directory. It should also
        be 'read only' in edit mode to prevent errors - there is no point in
        editing a reference to the actual entry.

      The addressbook_links vocabulary is set to list all the available
      entries that can be added to the personal address book with links.

      REMINDER:
      If you do not want to use the global address book directory named
      'addressbook', and you chose to use the personal address book with
      links feature, there are three places where you will have to put the
      new directory name:
      - in the portal_Webmail tool, in the 'Addressbook name' property
      - in the portal_directories tool, in the 'Id of local directory'
        property of your local directory with links.
      - in the 'addressbook_links' layout, in the widget named 'id', as it
        will have to use a new vocabulary.

      WARNINGS (Never two without three):
      1. CHANGES MADE ON THE CPS Local Directory WILL NOT BE
         REPERCUTED ON THE PERSONAL DIRECTORIES THAT HAVE ALREADY
         BEEN CREATED.
      2. EXECUTING THE INSTALLER WILL ERASE ALL THE MODIFICATIONS YOU MADE ON
         DIRECTORIES, SCHEMAS AND LAYOUTS SET BY CPSWebMail.
      2. The private address book and the private address book with links
         should use the same schema than the global address book: CPSWebMail
         enable users to copy contacts from the global address book into the
         personal address book, and to add links into the personal address
         book with links, pointing towards entries of the global address
         book. These features could break if you use a different schema.
