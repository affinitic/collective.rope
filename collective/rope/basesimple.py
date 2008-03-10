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

from Acquisition import Implicit

from OFS.SimpleItem import Item

from AccessControl.Role import RoleManager

from zope.interface import implements

from interfaces import IStoredInRDB
from interfaces import IKeyIdSubobjectSupport

_marker = object()

class BaseSimpleItem(object,
                    Item,
                    Implicit,
                    RoleManager):

    implements(IStoredInRDB)
    
    def getId(self):
        key = self.key
        if key:
            return str(IKeyIdSubobjectSupport(self).makeIdFromKey(self.key))
        else:
            return ''

    def __setId(self, id):
        self.key = IKeyIdSubobjectSupport(self).makeKeyFromId(id)

    id = property(getId, __setId)

    __name__ = property(getId, __setId, None, 'Access to id') 
    
    def __getattr__(self, key):
        attr = self.__zope_permissions__.get(key, _marker)
        if attr is _marker:
            raise AttributeError, key
        return attr

    def __setattr__(self, key, value):
        if key.startswith('_') and key.endswith('Permission'):
            self.__zope_permissions__[key] = value
        else:
            object.__setattr__(self, key, value)

    def __delattr__(self, key):
        if key.startswith('_') and key.endswith('Permission'):
            del self.__zope_permissions__[key]
        else:
            del self.__dict__[key]

    __new__ = object.__new__

    #dirty work around CMF 
    def opaqueValues(self):
        return ()
