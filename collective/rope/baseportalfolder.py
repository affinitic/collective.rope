from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager

from zope.interface import implements

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalFolder import ContentFilter
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.exceptions import zExceptions_Unauthorized

from basefolder import BaseFolder

class BasePortalFolder(BaseFolder):

#    implements(IFolderish)

    security = ClassSecurityInfo()

# begin
# copy from CMFCore.PortalFolder

    security.declarePublic('allowedContentTypes')
    def allowedContentTypes( self ):
        """
            List type info objects for types which can be added in
            this folder.
        """
        result = []
        portal_types = getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self)

        if myType is not None:
            for contentType in portal_types.listTypeInfo(self):
                if myType.allowType( contentType.getId() ):
                    result.append( contentType )
        else:
            result = portal_types.listTypeInfo()

        return filter( lambda typ, container=self:
                          typ.isConstructionAllowed( container )
                     , result )

    def _filteredItems( self, ids, filt ):
        """
            Apply filter, a mapping, to child objects indicated by 'ids',
            returning a sequence of ( id, obj ) tuples.
        """
        # Restrict allowed content types
        if filt is None:
            filt = {}
        else:
            # We'll modify it, work on a copy.
            filt = filt.copy()
        pt = filt.get('portal_type', [])
        if isinstance(pt, basestring):
            pt = [pt]
        types_tool = getToolByName(self, 'portal_types')
        allowed_types = types_tool.listContentTypes()
        if not pt:
            pt = allowed_types
        else:
            pt = [t for t in pt if t in allowed_types]
        if not pt:
            # After filtering, no types remain, so nothing should be
            # returned.
            return []
        filt['portal_type'] = pt

        query = ContentFilter(**filt)
        result = []
        append = result.append
        get = self._getOb
        for id in ids:
            obj = get( id )
            if query(obj):
                append( (id, obj) )
        return result

    #
    #   'IFolderish' interface methods
    #
    security.declarePublic('contentItems')
    def contentItems(self, filter=None):
        # List contentish and folderish sub-objects and their IDs.
        # (method is without docstring to disable publishing)
        #
        ids = self.objectIds()
        return self._filteredItems(ids, filter)

    security.declarePublic('contentIds')
    def contentIds(self, filter=None):
        # List IDs of contentish and folderish sub-objects.
        # (method is without docstring to disable publishing)
        #
        return [ item[0] for item in self.contentItems(filter) ]

    security.declarePublic('contentValues')
    def contentValues(self, filter=None):
        # List contentish and folderish sub-objects.
        # (method is without docstring to disable publishing)
        #
        return [ item[1] for item in self.contentItems(filter) ]

    security.declareProtected(ListFolderContents, 'listFolderContents')
    def listFolderContents(self, contentFilter=None):
        """ List viewable contentish and folderish sub-objects.
        """
        l = []
        for id, obj in self.contentItems(contentFilter):
            # validate() can either raise Unauthorized or return 0 to
            # mean unauthorized.
            try:
                if getSecurityManager().validate(self, self, id, obj):
                    l.append(obj)
            except zExceptions_Unauthorized:  # Catch *all* Unauths!
                pass
        return l

# end
# copy from CMFCore.PortalFolder
