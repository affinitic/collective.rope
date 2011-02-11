import unittest

from plone.testing import z2

from collective.rope.zopetestcasecompat import user_name


class PTCCompatTestCase(unittest.TestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.afterSetUp()

    def setRoles(self, roles):
        userFolder = self.portal['acl_users']
        z2.setRoles(userFolder, user_name, roles)

    def afterSetUp(self):
        pass

    def tearDown(self):
        self.beforeTearDown()

    def beforeTearDown(self):
        pass
