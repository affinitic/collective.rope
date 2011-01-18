from Products.Archetypes import WebDAVSupport
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Field import StringField
from Products.Archetypes.Widget import IdWidget


from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import copy_or_move as permission_copy_or_move

from Globals import InitializeClass
from OFS.History import Historical
from Products.CMFCore import permissions

from collective.rope.baseportalcontent import BasePortalContent

from zope.interface import implements


class KeyIdSubobjectSupport(object):

    subobjectSuffix = '_rf'

    def __init__(self, context):
        self.context = context

    def makeIdFromKey(self, key):
        """see interfaces"""
        #XXX should support multiple keys
        if not key.endswith(self.subobjectSuffix):
            return key + self.subobjectSuffix
        return str(key)

    def makeKeyFromId(self, id):
        """see interfaces"""
        return id

    def isSubobject(self, id):
        """see interfaces"""
        return id.endswith(self.subobjectSuffix)



# begin
# copy from Archetypes.BaseContent


class BaseContentMixin(BasePortalContent,
                       BaseObject,
                       CatalogMultiplex,
                       Historical):
    """A not-so-basic CMF Content implementation that doesn't
    include Dublin Core Metadata"""


    schema = Schema((

    StringField(
        name='id',
        required=0, # Still actually required, but the widget will
                    # supply the missing value on non-submits
        mode='rw',
        permission=permission_copy_or_move,
        accessor='getId',
        mutator='setId',
        default=None,
        widget=IdWidget(
            label=_(u'label_short_name', default=u'Short Name'),
            description=_(u'help_shortname',
                          default=u'Should not contain spaces, underscores or '
                                   'mixed case. Short Name is part of the '
                                   'item\' s web address.'),
            visible={'view': 'invisible'}),
    ),
    ))

    implements(IBaseContent, IReferenceable)

    security = ClassSecurityInfo()
    manage_options = BasePortalContent.manage_options + \
            Historical.manage_options

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
        if op == 1:
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
