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

from Products.CMFCore.utils import getToolByName

from collective.rope.tests.layer import RopePortal
from collective.rope.tests.layer import PORTAL_CONTENT_MAPPER
from collective.rope.tests.layer import setup_cmf_product
from Products.CMFTestCase import CMFTestCase
from Products.CMFTestCase.setup import setupCMFSite

FOLDER_ID = 'rope'

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_cmf_product()
setupCMFSite(extension_profiles=['collective.rope.tests:ropeoncmf'])


class PortalFolderTests(CMFTestCase.CMFTestCase):
    layer = RopePortal

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.tt = getToolByName(self.portal, 'portal_types')
        self.wt = getToolByName(self.portal, 'portal_workflow')
        self.tt.constructContent('Folder', self.portal, 'folder')
        self.folder = self.portal.folder

    def testInstantiateFolder(self):
        self.tt.constructContent('Rope Portal Folder',
                self.folder,
                FOLDER_ID,
                None,
                itemClass=PORTAL_CONTENT_MAPPER)
        self.failUnless(FOLDER_ID in self.folder.objectIds())

    def testDeleteFolder(self):
        self.tt.constructContent('Rope Portal Folder',
                self.folder,
                FOLDER_ID,
                None,
                itemClass=PORTAL_CONTENT_MAPPER)
        self.folder.manage_delObjects([FOLDER_ID])
        self.failIf(FOLDER_ID in self.folder.objectIds())

    def testGetObError(self):
        self.tt.constructContent('Rope Portal Folder',
                self.folder,
                FOLDER_ID,
                None,
                itemClass=PORTAL_CONTENT_MAPPER)
        rope = getattr(self.folder, FOLDER_ID)
        self.assertRaises(AttributeError, rope._getOb, 'notfound')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortalFolderTests))
    return suite
