# Copyright (c) 2008
# Authors: Project Contributors (see docs/CREDITS.txt)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or higher
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
import unittest
import transaction

from zope.container.tests.test_icontainer import BaseTestIContainer

from collective.rope.testing import ROPE_INTEGRATION
from collective.rope.testing import ROPE_FUNCTIONAL

from plone.bbb_testing.zopetestcasecompat import user_name
from plone.bbb_testing.zopetestcasecompat import user_password
from plone.bbb_testing.zopetestcasecompat import ZTCCompatTestCase

from collective.rope.testing import SIMPLE_ITEM_MAPPER
from collective.rope.folder import manage_addFolder

FOLDER_ID = 'rope'
ITEM_ID = ITEM_KEY = 'rope_first_rf'

# The order here is important: We first call the deferred function and then
# let ZopeTestCase install it

class FolderTests(ZTCCompatTestCase):
    layer = ROPE_INTEGRATION


    def testInstantiateFolder(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        self.failUnless(FOLDER_ID in self.folder.objectIds())

    def testDeleteFolder(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        self.folder.manage_delObjects([FOLDER_ID])
        self.failIf(FOLDER_ID in self.folder.objectIds())

    def testGetObError(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        rope = getattr(self.folder, FOLDER_ID)
        self.assertRaises(AttributeError, rope._getOb, 'notfound')

try:
    from zope.app.container.tests.test_icontainer import BaseTestIContainer
except ImportError:
    from zope.container.tests.test_icontainer import BaseTestIContainer


class IContainerTests(ZTCCompatTestCase, BaseTestIContainer):
    layer = ROPE_INTEGRATION

    def makeTestObject(self):
        if hasattr(self.folder, FOLDER_ID):
            self.folder.manage_delObjects([FOLDER_ID])
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        return getattr(self.folder, FOLDER_ID)

    def makeTestData(self):
        self.__container = self.makeTestObject()
        class_ = self.__container.getMapperClass()
        dataSet = []
        for i in range(0, 10):
            item_id = u"%s_icontainer_rf" % i
            ob = class_()
            ob.id = item_id
            dataSet.append((item_id, ob))
        return dataSet

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']


class FolderBrowserTests(ZTCCompatTestCase):
    layer = ROPE_FUNCTIONAL

    def afterSetUp(self):
        self.setRoles(['Manager'])
        transaction.commit()
        import plone.testing.z2
        self.browser = plone.testing.z2.Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization',
                'Basic %s:%s' % (user_name, user_password))
        self.folder_path = self.folder.absolute_url()

    def testAddRopeFolder(self):
        browser = self.browser
        browser.open(self.folder_path)
        url = (self.folder_path +
                '/manage_addProduct/collective.rope/folderAdd')
        browser.open(url)
        ctl = browser.getControl(name='id')
        ctl.value = FOLDER_ID
        ctl = browser.getControl(name='itemClass')
        ctl.value = SIMPLE_ITEM_MAPPER
        browser.getControl(name="submit").click()
        self.failUnless(FOLDER_ID in self.folder.objectIds())
        rope = getattr(self.folder, FOLDER_ID)
        self.assertEquals('Rope Folder', rope.meta_type)

    def testViewRopeFolder(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        transaction.commit()
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_main' % FOLDER_ID)
        self.failUnless('Rope Folder' in browser.contents)

    def testDeleteRopeFolder(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        transaction.commit()
        browser = self.browser
        browser.open(self.folder_path + '/manage_main')
        ctl = browser.getControl(name='ids:list')
        ctl.value = [FOLDER_ID]
        browser.getControl(name='manage_delObjects:method').click()
        self.failIf(FOLDER_ID in self.folder.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTests))
    suite.addTest(unittest.makeSuite(IContainerTests))
    suite.addTest(unittest.makeSuite(FolderBrowserTests))
    return suite
