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

import plone.testing.z2

from collective.rope.testing import ZTC_ROPE_INTEGRATION
from collective.rope.testing import ZTC_ROPE_FUNCTIONAL

from collective.rope.zopetestcasecompat import user_name
from collective.rope.zopetestcasecompat import user_password
from collective.rope.zopetestcasecompat import ZTCCompatTestCase

from collective.rope.tests.testfolder import FOLDER_ID
from collective.rope.tests.simpleitem import manage_addRopeSimpleItem
from collective.rope.tests.layer import SIMPLE_ITEM_MAPPER
from collective.rope.folder import manage_addFolder

ITEM_KEY = 'first_rf'
ITEM_ID = '%s' % ITEM_KEY
ITEM_TITLE = 'First Rope Simple'
ITEM_VIEW = '%s (%s)' % (ITEM_ID, ITEM_TITLE)


class SimpleItemBaseTests(ZTCCompatTestCase):
    layer = ZTC_ROPE_INTEGRATION

    def afterSetUp(self):
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        self.rope = getattr(self.folder, FOLDER_ID)


class SimpleItemTests(SimpleItemBaseTests):

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
        self.failUnless(ITEM_ID in rope.objectIds())
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


class SimpleItemTestsWithCommits(SimpleItemBaseTests):

    def beforeTearDown(self):
        transaction.abort()
        folderid = self.folder.getId()
        if folderid in self.app.objectIds():
            rope = self.rope
            rope.manage_delObjects(rope.objectIds())
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


class ItemBrowserTests(ZTCCompatTestCase):
    layer = ZTC_ROPE_FUNCTIONAL

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.folder_path = self.folder.absolute_url()
        manage_addFolder(self.folder,
            FOLDER_ID, SIMPLE_ITEM_MAPPER)
        self.rope = getattr(self.folder, FOLDER_ID)
        self.item_path = self.folder_path + '/%s/%s' % (FOLDER_ID, ITEM_ID)
        transaction.commit()
        self.browser = plone.testing.z2.Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization',
                'Basic %s:%s' % (user_name, user_password))

    def beforeTearDown(self):
        transaction.abort()
        folderid = self.folder.getId()
        if folderid in self.app.objectIds():
            rope = self.rope
            rope.manage_delObjects(rope.objectIds())
            self.app.manage_delObjects([folderid])
            transaction.commit()

    def testAdd(self):
        browser = self.browser
        browser.open(self.folder_path + \
                '/%s/manage_addProduct/collective.rope/simpleAdd' % FOLDER_ID)
        ctl = browser.getControl(name='id')
        ctl.value = ITEM_ID
        browser.getControl(name="submit").click()
        self.failUnless(ITEM_ID in self.rope.objectIds())
        item = getattr(self.rope, ITEM_ID)
        self.assertEquals('Rope Simple Item', item.meta_type)

    def testEdit(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        transaction.commit()
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
        transaction.commit()
        browser = self.browser
        browser.open(self.folder_path + '/%s/manage_main' % FOLDER_ID)
        ctl = browser.getControl(name='ids:list')
        ctl.value = [ITEM_ID]
        browser.getControl(name='manage_delObjects:method').click()
        self.failIf(FOLDER_ID in self.rope.objectIds())

    def testPermission(self):
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        transaction.commit()
        browser = self.browser
        browser.open(self.item_path)
        self.assertEquals('200 OK'.lower(),
                browser.headers['status'].lower())
        # browser used by 'anonymous'
        anonymous = plone.testing.z2.Browser(self.layer['app'])
        # anonymous can access
        anonymous.open(self.item_path)
        self.assertEquals('200 OK'.lower(),
                anonymous.headers['status'].lower())
        # change security to deny anonymous
        browser.open(self.item_path + \
                '/manage_permissionForm?permission_to_manage=View')
        ctl = browser.getControl(name='roles:list')
        ctl.value = ['Manager']
        ctl = browser.getControl(name='acquire')
        ctl.value = False
        browser.getControl(name='submit').click()
        # anonymous cannot access anymore
        self.assertRaises(HTTPError, anonymous.open, self.item_path)
        # store View permission on item instead of acquiring it
        browser.open(self.item_path + \
                '/manage_permissionForm?permission_to_manage=View')
        ctl = browser.getControl(name='roles:list')
        ctl.value = ['Manager', 'Anonymous']
        ctl = browser.getControl(name='acquire')
        ctl.value = False
        browser.getControl(name='submit').click()
        # anonymous can access again
        anonymous = plone.testing.z2.Browser(self.layer['app'])
        anonymous.open(self.item_path)
        self.assertEquals('200 OK'.lower(),
                anonymous.headers['status'].lower())

    def testLocalRole(self):
        uf = self.app.acl_users
        uf._addUser('other', 'other', 'other', [], ())
        rope = self.rope
        manage_addRopeSimpleItem(rope, ITEM_ID)
        transaction.commit()
        # browser used by 'other'
        other = plone.testing.z2.Browser(self.layer['app'])
        other.addHeader('Authorization', 'Basic %s:%s' % ('other', 'other'))
        # other cannot access properties page
        self.assertRaises(HTTPError,
                other.open,
                self.item_path + '/manage_workspace')
        # give Owner local role to other
        browser = self.browser
        browser.open(self.item_path + '/manage_listLocalRoles')
        form = browser.getForm(index=1)
        ctl = form.getControl(name='roles:list')
        ctl.value = ['Manager']
        ctl = form.getControl(name='userid')
        ctl.value = ['other']
        form.getControl(name='submit').click()
        # other can access properties page
        other.open(self.item_path + '/manage_workspace')
        self.assertEquals('200 OK'.lower(),
                other.headers['status'].lower())
        # remove local role
        browser = self.browser
        browser.open(self.item_path + '/manage_listLocalRoles')
        ctl = browser.getControl(name='userids:list')
        ctl.value = ['other']
        form = browser.getForm(index=0)
        form.getControl(name='submit').click()
        # other cannot access properties page anymore
        self.assertRaises(HTTPError,
                other.open,
                self.item_path + '/manage_workspace')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleItemTests))
    suite.addTest(unittest.makeSuite(SimpleItemTestsWithCommits))
    suite.addTest(unittest.makeSuite(ItemBrowserTests))
    return suite
