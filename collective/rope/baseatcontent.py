from Products.Archetypes import WebDAVSupport
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.interfaces.base import IBaseContent as z2IBaseContent
from Products.Archetypes.interfaces.referenceable import IReferenceable as z2IReferenceable
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.History import Historical
from Products.CMFCore import permissions

from collective.rope.baseportalcontent import BasePortalContent

from zope.interface import implements

# begin
# copy from Archetypes.BaseContent 

class BaseContentMixin(BasePortalContent,
                       BaseObject,
                       CatalogMultiplex,
                       Historical):
    """A not-so-basic CMF Content implementation that doesn't
    include Dublin Core Metadata"""

    __implements__ = z2IBaseContent, z2IReferenceable, BasePortalContent.__implements__
    implements(IBaseContent, IReferenceable)

    security = ClassSecurityInfo()
    manage_options = BasePortalContent.manage_options + Historical.manage_options

    isPrincipiaFolderish = 0
    isAnObjectManager = 0
    __dav_marshall__ = True

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

    def _notifyOfCopyTo(self, container, op=0):
        """OFS.CopySupport notify
        """
        BaseObject._notifyOfCopyTo(self, container, op=op)
        # keep reference info internally when op == 1 (move)
        # because in those cases we need to keep refs
        if op==1:
            self._v_cp_refs = 1

    security.declareProtected(permissions.ModifyPortalContent, 'PUT')
    PUT = WebDAVSupport.PUT

    security.declareProtected(permissions.View, 'manage_FTPget')
    manage_FTPget = WebDAVSupport.manage_FTPget

    security.declarePrivate('manage_afterPUT')
    manage_afterPUT = WebDAVSupport.manage_afterPUT

InitializeClass(BaseContentMixin)

__all__ = ('BaseContentMixin', )

# end
# copy from Archetypes.BaseContent 

