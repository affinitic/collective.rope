from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFUid', quiet=1)
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

# Check for layer support
try:
    import zope.testing.testrunner
except ImportError:
    USELAYER = 0
else:
    USELAYER = 1

# Check for Zope3 interfaces
try:
    from zope.interface.interfaces import IInterface
except ImportError:
    Z3INTERFACES = 0
else:
    from Testing.ZopeTestCase.interfaces import IPortalTestCase
    Z3INTERFACES = IInterface.providedBy(IPortalTestCase)

from Testing.ZopeTestCase import transaction
from Testing.ZopeTestCase import portal_name
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
from time import time
from Globals import PersistentMapping

portal_owner = 'portal_owner'
default_user = ZopeTestCase.user_name
default_password = ZopeTestCase.user_password

default_base_profile = 'Products.CMFDefault:default'
default_extension_profiles = ()

def setupPortal(id=portal_name,
                   quiet=0,
                   with_default_memberarea=1,
                   base_profile=default_base_profile,
                   extension_profiles=default_extension_profiles):
    '''Creates a CMF Default site.'''
    if USELAYER:
        quiet = 1
        cleanupPortal(id)
    PortalSetup(id, quiet, with_default_memberarea,
              base_profile, extension_profiles).run()

if USELAYER:
    import layer
    setupPortal = layer.onsetup(setupPortal)


def cleanupPortal(id):
    '''Removes a site.'''
    PortalCleanup(id).run()

if USELAYER:
    import layer
    cleanupPortal = layer.onteardown(cleanupPortal)


class PortalSetup:
    '''Creates a CMF site.'''

    def __init__(self, id, quiet, with_default_memberarea,
                 base_profile, extension_profiles):
        self.id = id
        self.quiet = quiet
        self.with_default_memberarea = with_default_memberarea
        self.base_profile = base_profile
        self.extension_profiles = tuple(extension_profiles)

    def run(self):
        self.app = self._app()
        try:
            uf = self.app.acl_users
            if uf.getUserById(portal_owner) is None:
                # Add portal owner
                uf.userFolderAddUser(portal_owner, default_password, ['Manager'], [])
            if not hasattr(aq_base(self.app), self.id):
                # Add site
                self._login(uf, portal_owner)
                self._optimize()
                self._setupSite()
                self._setupRegistries()
            if hasattr(aq_base(self.app), self.id):
                # Configure site
                self._login(uf, portal_owner)
                self._placefulSetUp()
                self._setupProfiles()
        finally:
            self._abort()
            self._placefulTearDown()
            self._close()
            self._logout()

    def _setupSite(self):
        '''Creates the site.'''
        start = time()
        # Add Plone site
        factory = self.app.manage_addProduct['CMFDefault']
        factory.addConfiguredSite(site_id=portal_name,
            profile_id="Products.CMFDefault:default")
        self._commit()
        self._print('done (%.3fs)\n' % (time()-start,))

    def _setupRegistries(self):
        '''Installs persistent registries.'''
        portal = getattr(self.app, self.id)
        if not hasattr(portal, '_installed_profiles'):
            portal._installed_profiles = PersistentMapping()
            self._commit()

    def _setupProfiles(self):
        '''Imports extension profiles into the site.'''
        portal = getattr(self.app, self.id)
        setup = getattr(portal, 'portal_setup', None)
        if setup is not None:
            for profile in self.extension_profiles:
                if not portal._installed_profiles.has_key(profile):
                    start = time()
                    self._print('Adding %s ... ' % (profile,))
                    profile_id = 'profile-%s' % (profile,)
                    setup.runAllImportStepsFromProfile(profile_id)
                    portal._installed_profiles[profile] = 1
                    self._commit()
                    self._print('done (%.3fs)\n' % (time()-start,))

    def _placefulSetUp(self):
        '''Sets the local site/manager.'''
        portal = getattr(self.app, self.id)
        _placefulSetUp(portal)

    def _placefulTearDown(self):
        '''Resets the local site/manager.'''
        _placefulTearDown()

    def _optimize(self):
        '''Applies optimizations to the PortalGenerator.'''
        _optimize()

    def _app(self):
        '''Opens a ZODB connection and returns the app object.'''
        return ZopeTestCase.app()

    def _close(self):
        '''Closes the ZODB connection.'''
        ZopeTestCase.close(self.app)

    def _login(self, uf, name):
        '''Logs in as user 'name' from user folder 'uf'.'''
        user = uf.getUserById(name).__of__(uf)
        newSecurityManager(None, user)

    def _logout(self):
        '''Logs out.'''
        noSecurityManager()

    def _commit(self):
        '''Commits the transaction.'''
        transaction.commit()

    def _abort(self):
        '''Aborts the transaction.'''
        transaction.abort()

    def _print(self, msg):
        '''Prints msg to stderr.'''
        if not self.quiet:
            ZopeTestCase._print(msg)


class PortalCleanup(PortalSetup):
    '''Removes a site.'''

    def __init__(self, id):
        self.id = id

    def run(self):
        self.app = self._app()
        try:
            if hasattr(aq_base(self.app), self.id):
                self._placefulSetUp()
                self.app._delObject(self.id)
                self._commit()
        finally:
            self._abort()
            self._close()
            self._placefulTearDown()


def _placefulSetUpHandler(event):
    '''Subscriber for ISiteManagerCreatedEvent.
       Sets the local site/manager.
    '''
    portal = event.object
    _placefulSetUp(portal)


def _placefulSetUp(portal):
    '''Sets the local site/manager.'''
    from zope.app.component.hooks import setHooks, setSite
    setHooks()
    setSite(portal)


def _placefulTearDown():
    '''Resets the local site/manager.'''
    from zope.app.component.hooks import resetHooks, setSite
    resetHooks()
    setSite()

def _optimize():
    '''Significantly reduces portal creation time.'''
    # Don't compile expressions on creation
    def __init__(self, text):
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    # Don't clone actions but convert to list only
    def _cloneActions(self):
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions

