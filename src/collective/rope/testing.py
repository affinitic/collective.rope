import unittest

import AccessControl.Permissions

import zope.configuration

import plone.testing.z2
import plone.testing.zca

import collective.rope


folder_name = 'test_folder_1_'
user_name = 'test_user_1_'
user_password = 'secret'
user_role = 'test_role_1_'
standard_permissions = [AccessControl.Permissions.access_contents_information,
    AccessControl.Permissions.view]


class ZTCCompatTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = self.layer['folder']
        self.afterSetUp()

    def afterSetUp(self):
        pass

    def setRoles(self, roles):
        plone.testing.z2.setRoles(self.folder.acl_users, user_name, roles)

    def tearDown(self):
        self.beforeTearDown()

    def beforeTearDown(self):
        pass


class ZTCCompatMixin(object):

    def setUpCompat(self):
        self._setupFolder()
        self._setupUserFolder()
        self._setupUser()
        plone.testing.z2.login(self['folder'].acl_users, user_name)

    def _setupFolder(self):
        '''Creates and configures the folder.'''
        app = self['app']
        from OFS.Folder import manage_addFolder
        manage_addFolder(app, folder_name)
        folder = getattr(app, folder_name)
        folder._addRole(user_role)
        folder.manage_role(user_role, standard_permissions)
        self['folder'] = folder

    def _setupUserFolder(self):
        '''Creates the user folder.'''
        from AccessControl.User import manage_addUserFolder
        manage_addUserFolder(self['folder'])

    def _setupUser(self):
        '''Creates the default user.'''
        uf = self['folder'].acl_users
        uf.userFolderAddUser(user_name, user_password, [user_role], [])

    def tearDownCompat(self):
        del self['folder']


class ZTCCompatIntegration(plone.testing.z2.IntegrationTesting,
ZTCCompatMixin):
    """ZopeTestCase compatibility"""

    def testSetUp(self):
        super(ZTCCompatIntegration, self).testSetUp()
        self.setUpCompat()

    def testTearDown(self):
        self.tearDownCompat()
        super(ZTCCompatIntegration, self).testTearDown()


class ZTCCompatFunctional(plone.testing.z2.FunctionalTesting,
ZTCCompatMixin):
    """ZopeTestCase compatibilty"""

    def testSetUp(self):
        super(ZTCCompatFunctional, self).testSetUp()
        self.setUpCompat()

    def testTearDown(self):
        self.tearDownCompat()
        super(ZTCCompatFunctional, self).testTearDown()


class Rope(plone.testing.Layer):

    defaultBases = (plone.testing.z2.STARTUP, )

    def setUp(self):
        # Create a new global registry
        plone.testing.zca.pushGlobalRegistry()

        zope.configuration.xmlconfig.file(
            'testing.zcml', package=collective.rope,
            context=self['configurationContext'])
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.uninstallProduct(app, 'collective.rope')
        # Pop the global registry
        plone.testing.zca.popGlobalRegistry()


ROPE_FIXTURE = Rope(name="Rope")

ROPE_INTEGRATION = plone.testing.z2.IntegrationTesting(bases=(ROPE_FIXTURE,),
    name="Rope:Integration")

ROPE_FUNCTIONAL = plone.testing.z2.FunctionalTesting(bases=(ROPE_FIXTURE,),
name="Rope:Functional")

ZTC_ROPE_INTEGRATION = ZTCCompatIntegration(
    bases=(ROPE_FIXTURE, ),
    name='ZTC:Rope:Integration')

ZTC_ROPE_FUNCTIONAL = ZTCCompatFunctional(
    bases=(ROPE_FIXTURE, ),
    name='ZTC:Rope:Functional')
