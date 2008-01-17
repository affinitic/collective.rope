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
from Globals import InitializeClass
from Globals import DTMLFile

from OFS.PropertyManager import PropertyManager

from Products.CMFCore.permissions import View

from zope.component import getUtility
from zope.component.factory import Factory

from collective.lead.interfaces import IDatabase

from collective.rope.baseportalcontent import BasePortalContent
from collective.rope.interfaces import IKeyIdSubobjectSupport

class RopePortalContent(BasePortalContent,
    PropertyManager):

    security = ClassSecurityInfo()

    _properties = ({'id':'title', 'type': 'string'},
                  )

    meta_type = "Rope Portal Content"

    portal_type = meta_type

    security.declareProtected(View, 'index_html')
    def index_html(self):
        '''call'''
        return '%s (%s)' % (self.id, self.title)

    security.declareProtected(View, 'setTitle')
    def setTitle(self, title):
        self.title = title

    security.declareProtected(View, 'Title')
    def Title(self):
        return self.title

    def getId(self):
        return IKeyIdSubobjectSupport(self).makeIdFromKey(self.key)

    def __setId(self, id):
        self.key = IKeyIdSubobjectSupport(self).makeKeyFromId(id)

    id = property(getId, __setId)

InitializeClass(RopePortalContent)

manage_addPortalContentForm = DTMLFile('simpleAdd', globals())

def manage_addPortalContent(dispatcher, id, title='', REQUEST=None):
    """Adds a new PortalContent object with id *id*.
    """
    _RopeFactory()
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)

def _RopeFactory(id, dbUtilityName, mapperName, title=''):
    db = getUtility(IDatabase, dbUtilityName)
    class_ = db.mappers[mapperName].class_
    ob = class_()
    keySupport = IKeyIdSubobjectSupport(ob)
    if not keySupport.isSubobject(id):
        raise ValueError, "wrong id"
    ob.id = id
    ob.title = str(title)
    return ob

RopeFactory = Factory(_RopeFactory)
