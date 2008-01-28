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

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

from Globals import DTMLFile
from Globals import InitializeClass

from OFS.Folder import Folder

from zope.component.factory import Factory

from collective.rope.baseportalfolder import BasePortalFolder

manage_addRopeFolderForm = DTMLFile('folderAdd', globals())

class RopePortalFolder(BasePortalFolder):

    security = ClassSecurityInfo()
    
    manage_options=(
        ({'label':'Contents', 'action':'manage_main',},
         ) + Folder.manage_options[1:]
        )

    security.declareProtected(view_management_screens,
                              'manage_main')
    manage_main = DTMLFile('contents', globals())

    meta_type = 'Rope Portal Folder'

    portal_type = meta_type

InitializeClass(RopePortalFolder)

def manage_addPortalFolder(dispatcher, id, dbUtilityName, mapperName, title='', REQUEST=None):
    """Adds a new PortalFolder object with id *id*.
    """
    _RopePortalFolderFactory(id, dbUtilityName, mapperName, title)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)

def _RopePortalFolderFactory(id, dbUtilityName, mapperName, title=''):
    ob = RopePortalFolder()
    ob.id = id
    ob.title = str(title)
    ob.dbUtilityName = dbUtilityName    
    ob.mapperName = mapperName
    return ob

RopePortalFolderFactory = Factory(_RopePortalFolderFactory)
