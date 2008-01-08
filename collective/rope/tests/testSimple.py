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

from urllib2 import HTTPError

from Testing.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import user_name, user_password
from Testing.ZopeTestCase import FunctionalTestCase

from Products.Five.testbrowser import Browser

from collective.rope.tests.layer import RopeTestLayer
from collective.rope.tests.layer import setupDatabase 
from collective.rope.tests.layer import DB_UTILITY_NAME
from collective.rope.tests.layer import SIMPLE_MAPPER_NAME
from collective.rope.tests.folder import manage_addRopeFolder
from collective.rope.tests.item import manage_addRopeSimpleItem

FOLDER_ID = 'rope'
ITEM_KEY = 'first'
ITEM_ID = '%s_rf' % ITEM_KEY
ITEM_TITLE = 'First Rope Simple'
ITEM_VIEW = '%s (%s)' % (ITEM_ID, ITEM_TITLE)

class FolderTests(ZopeTestCase):
    layer = RopeTestLayer

    def afterSetUp(self):
        setupDatabase()

    def testInstantiateFolder(self):
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        self.failUnless(FOLDER_ID in self.folder.objectIds())

    def testDeleteFolder(self):
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        self.folder.manage_delObjects([FOLDER_ID])
        self.failIf(FOLDER_ID in self.folder.objectIds())

class SimpleItemBase(ZopeTestCase):
    layer = RopeTestLayer

    def afterSetUp(self):
        setupDatabase()
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        self.rope = getattr(self.folder, FOLDER_ID)

class SimpleItemTests(SimpleItemBase):

    def testInstantiateSimpleItem(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        self.failUnless(ITEM_ID in rope.objectIds())
        item = getattr(rope, ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

    def testDeleteSimpleItem(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        rope.manage_delObjects([ITEM_ID])
        self.failIf(rope.objectIds())

    def testFolderGetAttr(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        item = getattr(rope, ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

    def testFolderUnrestrictedTraverse(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        item = rope.unrestrictedTraverse(ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

class SimpleItemTestsWithCommits(SimpleItemBase):
    
    def beforeTearDown(self):
        transaction.abort()
        folderid = self.folder.getId()
        if folderid in self.app.objectIds():
            self.app.manage_delObjects([folderid])
            transaction.commit()

    def testDeleteSimpleItemWithCommits(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        transaction.commit()
        rope.manage_delObjects([ITEM_ID])
        transaction.commit()
        self.failIf(rope.objectIds())

    def testInstantiateSimpleItemWithCommit(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        transaction.commit()
        self.failUnless(ITEM_ID in rope.objectIds())

class FolderBrowserTests(FunctionalTestCase):
    layer = RopeTestLayer

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s'%(user_name, user_password))
        self.folder_path = 'http://localhost/' + self.folder.absolute_url(1)

    def testAddRopeFolder(self):
        browser = self.browser
        browser.open(self.folder_path + '/manage_addProduct/collective.rope/folderAdd')
        ctl = browser.getControl(name='id')
        ctl.value = FOLDER_ID
        ctl = browser.getControl(name='databaseName')
        ctl.value = DB_UTILITY_NAME
        ctl = browser.getControl(name='mapperName')
        ctl.value = SIMPLE_MAPPER_NAME
        browser.getControl(name="submit").click()
        self.failUnless(FOLDER_ID in self.folder.objectIds()) 
        rope = getattr(self.folder, FOLDER_ID)
        self.assertEquals('Rope Folder', rope.meta_type)

    def testViewRopeFolder(self):
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_main' % FOLDER_ID)
        self.failUnless('Rope Folder' in browser.contents) 

    def testDeleteRopeFolder(self):
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        browser = self.browser
        browser.open(self.folder_path + '/manage_main')
        ctl = browser.getControl(name='ids:list')
        ctl.value = [FOLDER_ID] 
        browser.getControl(name='manage_delObjects:method').click()
        self.failIf(FOLDER_ID in self.folder.objectIds()) 

class ItemBrowserTests(FunctionalTestCase):
    layer = RopeTestLayer

    def afterSetUp(self):
        setupDatabase()
        self.setRoles(['Manager'])
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s'%(user_name, user_password))
        self.folder_path = 'http://localhost/' + self.folder.absolute_url(1)
        manage_addRopeFolder(self.folder,
            FOLDER_ID, DB_UTILITY_NAME, SIMPLE_MAPPER_NAME)
        self.rope = getattr(self.folder, FOLDER_ID)
        self.item_path = self.folder_path + '/%s/%s' % (FOLDER_ID, ITEM_ID)

    def testAdd(self):
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_addProduct/collective.rope/simpleAdd' % FOLDER_ID)
        ctl = browser.getControl(name='id')
        ctl.value = ITEM_ID
        browser.getControl(name="submit").click()
        self.failUnless(ITEM_ID in self.rope.objectIds()) 
        item = getattr(self.rope, ITEM_ID)
        self.assertEquals('Rope Simple Item', item.meta_type)

    def testEdit(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        browser = self.browser
        browser.open(self.item_path + '/manage_workspace')
        ctl = browser.getControl(name='title:UTF-8:string')
        ctl.value = ITEM_TITLE
        browser.getControl(name="manage_editProperties:method").click()
        self.failUnless(ITEM_TITLE in browser.contents) 
        browser.open(self.item_path)
        self.assertEquals(browser.contents, ITEM_VIEW)

    def testDelete(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_main' % FOLDER_ID)
        ctl = browser.getControl(name='ids:list')
        ctl.value = [ITEM_ID] 
        browser.getControl(name='manage_delObjects:method').click()
        self.failIf(FOLDER_ID in self.rope.objectIds()) 

    def testPermission(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        browser = self.browser
        browser.open(self.item_path)
        self.assertEquals('200 OK', browser.headers['status'])
        # browser used by 'anonymous'
        anonymous = Browser()
        # anonymous can access
        anonymous.open(self.item_path)
        self.assertEquals('200 OK', anonymous.headers['status'])
        # change security to deny anonymous
        browser.open(self.item_path + '/manage_permissionForm?permission_to_manage=View')
        ctl = browser.getControl(name='roles:list')
        ctl.value = ['Manager']
        ctl = browser.getControl(name='acquire')
        ctl.value = False
        browser.getControl(name='submit').click()
        # anonymous cannot access anymore
        self.assertRaises(HTTPError, anonymous.open, self.item_path)
        # store View permission on item instead of acquiring it
        browser.open(self.item_path + '/manage_permissionForm?permission_to_manage=View')
        ctl = browser.getControl(name='roles:list')
        ctl.value = ['Manager', 'Anonymous']
        ctl = browser.getControl(name='acquire')
        ctl.value = False
        browser.getControl(name='submit').click()
        # anonymous can access again
        anonymous = Browser()
        anonymous.open(self.item_path)
        self.assertEquals('200 OK', anonymous.headers['status'])

    def testLocalRole(self):
        uf = self.app.acl_users
        uf._addUser('other', 'other', 'other', [], ())
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        # browser used by 'other'
        other = Browser()
        other.addHeader('Authorization', 'Basic %s:%s'%('other', 'other'))
        # other cannot access properties page
        self.assertRaises(HTTPError, other.open, self.item_path + '/manage_workspace')
        # give Owner local role to other
        browser = self.browser
        browser.open(self.item_path + '/manage_listLocalRoles')
        ctl = browser.getControl(name='roles:list')
        ctl.value = ['Manager']
        ctl = browser.getControl(name='userid')
        ctl.value = ['other']
        browser.getControl(name='submit').click()
        # other can access properties page
        other.open(self.item_path + '/manage_workspace')
        self.assertEquals('200 OK', other.headers['status'])
        # remove local role
        browser = self.browser
        browser.open(self.item_path + '/manage_listLocalRoles')
        ctl = browser.getControl(name='userids:list')
        ctl.value = ['other']
        form = browser.getForm(index=0)
        form.getControl(name='submit').click()
        # other cannot access properties page anymore
        self.assertRaises(HTTPError, other.open, self.item_path + '/manage_workspace')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTests))
    suite.addTest(unittest.makeSuite(SimpleItemTests))
    suite.addTest(unittest.makeSuite(SimpleItemTestsWithCommits))
    suite.addTest(unittest.makeSuite(FolderBrowserTests))
    suite.addTest(unittest.makeSuite(ItemBrowserTests))
    return suite

