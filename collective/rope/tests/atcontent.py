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
    """A not-so-basic CMF Content implementation with Dublin Core
    Metadata included"""

    implements(IBaseContent, IReferenceable)

    schema = BaseContentMixin.schema

    manage_options = BaseContentMixin.manage_options + \
        PropertyManager.manage_options

    meta_type = portal_type = "Rope AT Content"

    def __init__(self, oid, **kwargs):
        BaseContentMixin.__init__(self, oid, **kwargs)

    def getId(self):
        return IKeyIdSubobjectSupport(self).makeIdFromKey(self.key)

    def __setId(self, id):
        self.key = IKeyIdSubobjectSupport(self).makeKeyFromId(id)

    id = property(getId, __setId)

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
