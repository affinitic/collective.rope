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

from zope.interface import implements
from zope.component.factory import Factory

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore import permissions

from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IReferenceable

from collective.rope.baseatfolder import BaseFolderMixin

# begin
# copy from Archetypes.BaseFolder


class RopeATFolder(BaseFolderMixin, ExtensibleMetadata):
    """A not-so-basic Folder implementation, with Dublin Core
    Metadata included"""

    implements(IBaseFolder, IBaseObject, IReferenceable, IContentish)

    schema = BaseFolderMixin.schema + ExtensibleMetadata.schema

    security = ClassSecurityInfo()

    meta_type = "Rope AT Folder"

    portal_type = meta_type

    def __init__(self, oid, **kwargs):
        # Call skinned first cause baseobject will set new defaults on
        # those attributes anyway
        BaseFolderMixin.__init__(self, oid, **kwargs)
        ExtensibleMetadata.__init__(self)

    security.declareProtected(permissions.View,
                              'Description')

    def Description(self, **kwargs):
        """We have to override Description here to handle arbitrary
        arguments since PortalFolder defines it."""
        return self.getField('description').get(self, **kwargs)

    security.declareProtected(permissions.ModifyPortalContent,
                              'setDescription')

    def setDescription(self, value, **kwargs):
        """We have to override setDescription here to handle arbitrary
        arguments since PortalFolder defines it."""
        self.getField('description').set(self, value, **kwargs)

InitializeClass(RopeATFolder)

RopeATFolderSchema = RopeATFolder.schema

# end
# copy from Archetypes.BaseFolder
import types


def _my_import(item_class):
    if type(item_class) == types.ClassType:
        return item_class
    components = item_class.split('.')
    mod = __import__('.'.join(components[0:-1]))
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def manage_addAttFolder(dispatcher, id,
        itemClass,
        sessionName='',
        title='',
        REQUEST=None):
    """Adds a new ATFolder object with id *id*.
    """
    _RopeATFolderFactory(id, itemClass, sessionName, title)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)


def _RopeATFolderFactory(id, itemClass, sessionName='', title=''):
    ob = RopeATFolder(id)
    ob.title = str(title)
    ob.item_class = _my_import(itemClass)
    ob.session_name = sessionName
    return ob

RopeATFolderFactory = Factory(_RopeATFolderFactory)
