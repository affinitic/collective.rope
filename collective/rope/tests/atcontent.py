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

from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable

from Globals import InitializeClass
from OFS.PropertyManager import PropertyManager

from zope.interface import implements

from zope.component import getUtility
from zope.component.factory import Factory

from collective.lead.interfaces import IDatabase

from collective.rope.baseatcontent import BaseContentMixin
from collective.rope.interfaces import IKeyIdSubobjectSupport

class RopeATContent(BaseContentMixin,
              PropertyManager):
    """Tests Rope AT content"""

    implements(IBaseContent, IReferenceable)

    schema = BaseContentMixin.schema

    manage_options = BaseContentMixin.manage_options + \
        PropertyManager.manage_options

    meta_type = portal_type = "Rope AT Content"

    def __init__(self, oid, **kwargs):
        BaseContentMixin.__init__(self, oid, **kwargs)

InitializeClass(RopeATContent)

def _RopeATFactory(id, dbUtilityName, mapperName, title=''):
    db = getUtility(IDatabase, dbUtilityName)
    class_ = db.mappers[mapperName].class_
    ob = class_(id)
    keySupport = IKeyIdSubobjectSupport(ob)
    if not keySupport.isSubobject(id):
        raise ValueError, "wrong id"
    ob.id = id
    ob.title = str(title)
    return ob

RopeATFactory = Factory(_RopeATFactory)
