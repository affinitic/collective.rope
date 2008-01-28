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

from Testing.ZopeTestCase import PortalTestCase

from Products.CMFCore.utils import getToolByName

from collective.rope.tests.testfolder import FOLDER_ID
from collective.rope.tests.layer import RopePortal
from collective.rope.tests.layer import Portal
from collective.rope.tests.layer import setupDatabase 
from collective.rope.tests.layer import DB_UTILITY_NAME
from collective.rope.tests.layer import PORTAL_CONTENT_MAPPER
from collective.rope.tests.setup import setupPortal

ITEM_KEY = 'first'
ITEM_ID = '%s_rf' % ITEM_KEY
ITEM_TITLE = 'First Rope PortalContent'
ITEM_VIEW = '%s (%s)' % (ITEM_ID, ITEM_TITLE)

setupPortal(extension_profiles=['collective.rope.tests:ropeoncmf'])

class PortalContentBaseTests(PortalTestCase):
    layer = RopePortal

    def afterSetUp(self):
        setupDatabase()
        self.setRoles(['Manager'])
        self.tt = getToolByName(self.portal, 'portal_types')
        self.wt = getToolByName(self.portal, 'portal_workflow')
        self.tt.constructContent('Folder', self.portal, 'folder')
        self.folder = self.portal.folder
        self.tt.constructContent('Rope Portal Folder', self.folder, FOLDER_ID, None,
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        self.rope = getattr(self.folder, FOLDER_ID)

class PortalTests(PortalTestCase):
    layer = Portal 

    def testPortal(self):
        self.assertEquals(self.portal.meta_type, 'CMF Site')

class PortalContentTests(PortalContentBaseTests):

    def testInstantiate(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        self.failUnless(ITEM_ID in rope.objectIds())
        item = getattr(rope, ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

    def testDeleteSimpleItem(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        rope.manage_delObjects([ITEM_ID])
        self.failIf(rope.objectIds())

    def testFolderGetAttr(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        item = getattr(rope, ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

    def testFolderUnrestrictedTraverse(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        item = rope.unrestrictedTraverse(ITEM_ID)
        self.assertEquals(ITEM_KEY, item.key)
        self.assertEquals(ITEM_ID, item.getId())

    def testInitialState(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        item = getattr(rope, ITEM_ID)
        state = self.wt.getInfoFor(item, 'review_state')
        self.assertEquals(state, 'private') 
        transitions = [action['transition']
            for action in self.wt.listActions(object=item)
            if action['category'] == 'workflow']
        transitionIds = [transition.id for transition in transitions]
        transitionIds.sort()
        self.assertEquals(transitionIds, ['publish', 'submit']) 

    def testWorkflowTransition(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        item = getattr(rope, ITEM_ID)
        state = self.wt.doActionFor(item, 'publish')
        state = self.wt.getInfoFor(item, 'review_state')
        self.assertEquals(state, 'published') 

    def testSearch(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        item = getattr(rope, ITEM_ID)
        item.setTitle(ITEM_TITLE) 
        item.reindexObject()
        ct = getToolByName(self.portal, 'portal_catalog')
        results = ct.searchResults(SearchableText='First')
        ids = [brain.getId for brain in results]
        self.failUnless(ITEM_ID in ids)


class PortalContentTestsWithCommits(PortalContentBaseTests):
    
    def beforeTearDown(self):
        transaction.abort()
        folderid = self.folder.getId()
        if folderid in self.portal.objectIds():
            rope = self.rope
            rope.manage_delObjects(rope.objectIds())
            self.portal.manage_delObjects([folderid])
            transaction.commit()

    def testDeleteSimpleItemWithCommits(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        transaction.commit()
        rope.manage_delObjects([ITEM_ID])
        transaction.commit()
        self.failIf(rope.objectIds())

    def testInstantiateSimpleItemWithCommit(self):
        rope = self.rope
        self.tt.constructContent('Rope Portal Content', rope, ITEM_ID, None, 
            dbUtilityName=DB_UTILITY_NAME, mapperName=PORTAL_CONTENT_MAPPER)
        transaction.commit()
        self.failUnless(ITEM_ID in rope.objectIds())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortalTests))
    suite.addTest(unittest.makeSuite(PortalContentTests))
    suite.addTest(unittest.makeSuite(PortalContentTestsWithCommits))
    return suite

