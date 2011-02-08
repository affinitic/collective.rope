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

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from App.class_init import InitializeClass

from Products.CMFCore import permissions
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import _checkPermission

from Products.Archetypes import WebDAVSupport
from Products.Archetypes.CatalogMultiplex  import CatalogMultiplex
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IReferenceable

from collective.rope.baseportalfolder import BasePortalFolder

# begin
# copy from Archetypes.BaseFolder


class BaseFolderMixin(CatalogMultiplex,
                      BaseObject,
                      BasePortalFolder,
                      ):
    """A not-so-basic Folder implementation, with no Dublin Core
    Metadata"""

    implements(IBaseFolder, IBaseObject, IReferenceable, IContentish)

    security = ClassSecurityInfo()

    # Fix permissions set by CopySupport.py
    __ac_permissions__ = (
        (permissions.ModifyPortalContent,
         ('manage_cutObjects', 'manage_pasteObjects',
          'manage_renameObject', 'manage_renameObjects',)),
        )
    security.declareProtected('Copy or Move', 'manage_copyObjects')

    manage_options = BasePortalFolder.manage_options
    content_icon = "folder_icon.gif"
    use_folder_tabs = 1
    isPrincipiaFolderish = 1
    isAnObjectManager = 1
    __dav_marshall__ = False


    __call__ = PortalContent.__call__.im_func

    # This special value informs ZPublisher to use __call__
    index_html = None

    def __init__(self, oid, **kwargs):
        # Call skinned first cause baseobject will set new defaults on
        # those attributes anyway
        BasePortalFolder.__init__(self, oid)
        BaseObject.__init__(self, oid, **kwargs)

    def _notifyOfCopyTo(self, container, op=0):
        """In the case of a move (op=1) we need to make sure
        references are mainained for all referencable objects within
        the one being moved.

        manage_renameObject calls _notifyOfCopyTo so that the
        object being renamed doesn't lose its references. But
        manage_renameObject calls _delObject which calls
        manage_beforeDelete on all the children of the object
        being renamed which deletes all references for children
        of the object being renamed. Here is a patch that does
        recursive calls for _notifyOfCopyTo to address that
        problem.
        """
        # XXX this doesn't appear to be necessary anymore, if it is
        # it needs to be used in BaseBTreeFolder as well, it currently
        # is not.
        BaseObject._notifyOfCopyTo(self, container, op=op)
        # keep reference info internally when op == 1 (move)
        # because in those cases we need to keep refs
        if op == 1:
            self._v_cp_refs = 1
        for child in self.contentValues():
            if IReferenceable.providedBy(child):
                child._notifyOfCopyTo(self, op)

    security.declarePrivate('manage_afterAdd')

    def manage_afterAdd(self, item, container):
        BaseObject.manage_afterAdd(self, item, container)

    security.declarePrivate('manage_afterClone')

    def manage_afterClone(self, item):
        BaseObject.manage_afterClone(self, item)

    security.declarePrivate('manage_beforeDelete')

    def manage_beforeDelete(self, item, container):
        BaseObject.manage_beforeDelete(self, item, container)
        #and reset the rename flag (set in Referenceable._notifyCopyOfCopyTo)
        self._v_cp_refs = None

    security.declareProtected(permissions.DeleteObjects,
                              'manage_delObjects')

    def manage_delObjects(self, ids=[], REQUEST=None):
        """We need to enforce security."""
        if isinstance(ids, basestring):
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not _checkPermission(permissions.DeleteObjects, item):
                raise Unauthorized(
                    "Do not have permissions to remove this object")
        return BasePortalFolder.manage_delObjects(self, ids, REQUEST=REQUEST)

    security.declareProtected(permissions.ListFolderContents,
                              'listFolderContents')

    def listFolderContents(self, contentFilter=None, suppressHiddenFiles=0):
        """Optionally you can suppress "hidden" files, or files that begin
        with a dot.
        """
        contents = BasePortalFolder.listFolderContents(self,
            contentFilter=contentFilter)
        if suppressHiddenFiles:
            contents = [obj for obj in contents if obj.getId()[:1] != '.']

        return contents

    security.declareProtected(permissions.AccessContentsInformation,
                              'folderlistingFolderContents')

    def folderlistingFolderContents(self, contentFilter=None,
                                    suppressHiddenFiles=0):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission,
        as in CMFDefault.
        """
        return self.listFolderContents(contentFilter=contentFilter,
                                       suppressHiddenFiles=suppressHiddenFiles)

    security.declareProtected(permissions.View, 'Title')

    def Title(self, **kwargs):
        """We have to override Title here to handle arbitrary arguments since
        BasePortalFolder defines it."""
        return self.getField('title').get(self, **kwargs)

    security.declareProtected(permissions.ModifyPortalContent,
                              'setTitle')

    def setTitle(self, value, **kwargs):
        """We have to override setTitle here to handle arbitrary
        arguments since BasePortalFolder defines it."""
        self.getField('title').set(self, value, **kwargs)

    def __getitem__(self, key):
        """Overwrite __getitem__.

        At first it's using the BaseObject version. If the element can't be
        retrieved from the schema it's using BasePortalFolder as fallback which
        should be the ObjectManager's version.
        """
        try:
            return BaseObject.__getitem__(self, key)
        except KeyError:
            return BasePortalFolder.__getitem__(self, key)

    # override "CMFCore.PortalFolder.PortalFolder.manage_addFolder"
    # as it insists on creating folders of type "Folder".
    # use instead "_at_type_subfolder" or our own type.
    security.declareProtected(permissions.AddPortalFolders,
                              'manage_addFolder')

    def manage_addFolder(self,
                         id,
                         title='',
                         REQUEST=None,
                         type_name=None):
        """Add a new folder-like object with id *id*.

        IF present, use the parent object's 'mkdir' alias; otherwise, just add
        a PortalFolder.
        """
        ti = self.getTypeInfo()
        # BBB getMethodURL is part of CMF 1.5 but AT 1.3 should be compatible
        # with CMF 1.4
        try:
            method = ti and ti.getMethodURL('mkdir') or None
        except AttributeError:
            method = None
        if method is not None:
            # call it
            getattr(self, method)(id=id)
        else:
            if type_name is None:
                type_name = getattr(self, '_at_type_subfolder', None)
            if type_name is None:
                type_name = ti and ti.getId() or 'Folder'
            self.invokeFactory(type_name, id=id)

        ob = self._getOb(id)
        try:
            ob.setTitle(title)
        except AttributeError:
            pass
        try:
            ob.reindexObject()
        except AttributeError:
            pass

    def MKCOL_handler(self, id, REQUEST=None, RESPONSE=None):
        """Hook into the MKCOL (make collection) process to call
        manage_afterMKCOL.
        """
        result = BasePortalFolder.MKCOL_handler(self, id, REQUEST, RESPONSE)
        self.manage_afterMKCOL(id, result, REQUEST, RESPONSE)
        return result

    security.declarePrivate('manage_afterMKCOL')

    def manage_afterMKCOL(self, id, result, REQUEST=None, RESPONSE=None):
        """After MKCOL handler.
        """
        pass

    security.declareProtected(permissions.ModifyPortalContent, 'PUT')
    PUT = WebDAVSupport.PUT

    security.declareProtected(permissions.View, 'manage_FTPget')
    manage_FTPget = WebDAVSupport.manage_FTPget

    security.declarePrivate('manage_afterPUT')
    manage_afterPUT = WebDAVSupport.manage_afterPUT

InitializeClass(BaseFolderMixin)

# end
# copy from Archetypes.BaseFolder


__all__ = ('BaseFolder', 'BaseFolderMixin', 'BaseFolderSchema')
