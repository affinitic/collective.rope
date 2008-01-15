##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

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
    _RopePortalContentFactory()
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)

def _RopePortalContentFactory(id, dbUtilityName, mapperName, title=''):
    db = getUtility(IDatabase, dbUtilityName)
    class_ = db.mappers[mapperName].class_
    ob = class_()
    keySupport = IKeyIdSubobjectSupport(ob)
    if not keySupport.isSubobject(id):
        raise ValueError, "wrong id"
    ob.id = id
    ob.title = str(title)
    return ob

RopePortalContentFactory = Factory(_RopePortalContentFactory)
