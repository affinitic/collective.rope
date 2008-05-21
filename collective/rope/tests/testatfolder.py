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

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import setupPloneSite

from Products.CMFCore.utils import getToolByName

from collective.rope.tests.layer import RopePloneSite
from collective.rope.tests.layer import setupDatabase
from collective.rope.tests.layer import DB_UTILITY_NAME
from collective.rope.tests.layer import AT_CONTENT_MAPPER

FOLDER_ID = 'rope'

setupPloneSite(extension_profiles=['collective.rope.tests:ropeonat'])

class ATFolderTests(PloneTestCase):
    layer = RopePloneSite

    def afterSetUp(self):
        setupDatabase()
        self.setRoles(['Manager'])
        self.tt = getToolByName(self.portal, 'portal_types')
        self.wt = getToolByName(self.portal, 'portal_workflow')
        self.tt.constructContent('Folder', self.portal, 'folder')
        self.folder = self.portal.folder

    def testInstantiateFolder(self):
        self.tt.constructContent('Rope AT Folder', self.folder, FOLDER_ID, None,
            dbUtilityName=DB_UTILITY_NAME, mapperName=AT_CONTENT_MAPPER)
        self.failUnless(FOLDER_ID in self.folder.objectIds())

    def testDeleteFolder(self):
        self.tt.constructContent('Rope AT Folder', self.folder, FOLDER_ID, None,
            dbUtilityName=DB_UTILITY_NAME, mapperName=AT_CONTENT_MAPPER)
        self.folder.manage_delObjects([FOLDER_ID])
        self.failIf(FOLDER_ID in self.folder.objectIds())

    def testGetObError(self):
        self.tt.constructContent('Rope AT Folder', self.folder, FOLDER_ID, None,
            dbUtilityName=DB_UTILITY_NAME, mapperName=AT_CONTENT_MAPPER)
        rope = getattr(self.folder, FOLDER_ID)
        self.assertRaises(AttributeError, rope._getOb, 'notfound')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ATFolderTests))
    return suite
