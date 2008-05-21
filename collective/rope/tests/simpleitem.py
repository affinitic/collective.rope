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

from Globals import DTMLFile
from Globals import InitializeClass

from OFS.PropertyManager import PropertyManager

from AccessControl import ClassSecurityInfo
from AccessControl.Owned import Owned
from AccessControl.Permissions import view as View

from collective.rope.interfaces import IKeyIdSubobjectSupport
from collective.rope.basesimple import BaseSimpleItem

class RopeSimpleItem(BaseSimpleItem, PropertyManager):

    security = ClassSecurityInfo()

    _properties = ({'id':'title', 'type': 'string'},
                  )
    manage_workspace = PropertyManager.manage_propertiesForm

    manage_options = (PropertyManager.manage_options
        + Owned.manage_options
        + ({'label': 'Interfaces',
           'action': 'manage_interfaces'},
        {'label':'Security',
         'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )
        )

    meta_type = 'Rope Simple Item'

    security.declareProtected(View, 'setTitle')
    def setTitle(self, title):
        self.title = title

    security.declareProtected(View, 'index_html')
    def index_html(self):
        '''call'''
        return '%s (%s)' % (self.id, self.title)

InitializeClass(RopeSimpleItem)

manage_addRopeSimpleItemForm = DTMLFile('simpleAdd', globals())

def manage_addRopeSimpleItem(dispatcher, id, title='', REQUEST=None):
    """Adds a new RopeSimple object with id *id*,
    connected with database .
    """
    class_ = dispatcher.getMapperClass()
    ob = class_()
    keySupport = IKeyIdSubobjectSupport(ob)
    if not keySupport.isSubobject(id):
        raise ValueError, "wrong id"
    ob.id = id
    ob.title = str(title)
    dispatcher._setObject(id, ob)
    ob = ob.__of__(dispatcher)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)
