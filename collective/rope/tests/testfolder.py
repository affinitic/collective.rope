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

from Testing.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import user_name, user_password
from Testing.ZopeTestCase import FunctionalTestCase

from Products.Five.testbrowser import Browser
from collective.rope.tests.layer import Rope
from collective.rope.tests.layer import SIMPLE_ITEM_MAPPER

from collective.rope.folder import manage_addFolder

FOLDER_ID = 'rope'


class FolderTests(ZopeTestCase):
    layer = Rope

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


class FolderBrowserTests(FunctionalTestCase):
    layer = Rope

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization',
                'Basic %s:%s'%(user_name, user_password))
        self.folder_path = 'http://localhost/' + self.folder.absolute_url(1)

    def testAddRopeFolder(self):
        browser = self.browser
        browser.open(self.folder_path + \
                '/manage_addProduct/collective.rope/folderAdd')
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
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_main' % FOLDER_ID)
        self.failUnless('Rope Folder' in browser.contents)

    def testDeleteRopeFolder(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        browser = self.browser
        browser.open(self.folder_path + '/manage_main')
        ctl = browser.getControl(name='ids:list')
        ctl.value = [FOLDER_ID]
        browser.getControl(name='manage_delObjects:method').click()
        self.failIf(FOLDER_ID in self.folder.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTests))
    suite.addTest(unittest.makeSuite(FolderBrowserTests))
    return suite
