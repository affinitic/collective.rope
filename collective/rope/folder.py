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

from collective.rope.basefolder import BaseFolder

manage_addFolderForm = DTMLFile('folderAdd', globals())

def manage_addFolder(dispatcher, id, dbUtilityName, mapperName, title='', REQUEST=None):
    """Adds a new Folder object with id *id*.
    """
    id = str(id)
    ob = Folder(id)
    ob.title = str(title)
    ob.dbUtilityName = dbUtilityName
    ob.mapperName = mapperName
    dispatcher._setObject(id, ob)
    ob = dispatcher._getOb(id)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)

class Folder(BaseFolder):

    security = ClassSecurityInfo()
    
    manage_options=(
        ({'label':'Contents', 'action':'manage_main',},
         ) + Folder.manage_options[1:]
        )

    security.declareProtected(view_management_screens,
                              'manage_main')
    manage_main = DTMLFile('contents', globals())

    meta_type = 'Rope Folder'

InitializeClass(Folder)
