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

import logging

from sqlalchemy import select

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.Permissions import access_contents_information

from Globals import InitializeClass

from Acquisition import aq_base

from OFS.Folder import Folder

from zope.component import getUtility
from zope.interface import implements

from collective.lead.interfaces import IDatabase

from interfaces import IRDBFolder
from interfaces import IKeyIdSubobjectSupport

from zope.event import notify
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.contained import notifyContainerModified
from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeRemovedEvent
import OFS.subscribers

logger = logging.getLogger('Rope basefolder')

_marker = object()

class KeyIdSubobjectSupport(object):

    subobjectSuffix = '_rf'

    def __init__(self, context):
        self.context = context

    def makeIdFromKey(self, key):
        """see interfaces"""
        #XXX should support multiple keys
        if not key.endswith(self.subobjectSuffix):
            return key + self.subobjectSuffix
        return key

    def makeKeyFromId(self, id):
        """see interfaces"""
        return id

    def isSubobject(self, id):
        """see interfaces"""
        return id.endswith(self.subobjectSuffix)

class BaseFolder(Folder):
    """subobjects stored outside ZODB through SQLAlchemy"""

    security = ClassSecurityInfo()

    implements(IRDBFolder)

    def _database(self):
        try:
            db = getUtility(IDatabase, self.dbUtilityName)
            db.session
            return db
        except AttributeError:
            return None

    @property
    def _session(self):
        if self._database():
            return self._database().session
        else:
            raise ValueError, 'mapperName or dbUtilityName not set'

    def getMapperClass(self):
        '''mapperClass'''
        if self._database():
            db = self._database()
            return db.mappers[self.mapperName].class_
        else:
            return None

    @property
    def _mapperClass(self):
        return self.getMapperClass()

    def _checkId(self, id, allow_dup=0):
        pass

    security.declareProtected(access_contents_information,
                              'objectIds')
    def objectIds(self):
        '''ids'''
        if self._mapperClass:
            selectQuery = str(select(
                [self._mapperClass.c.key]))
            cursor = self._session.execute(selectQuery)
            try:
                rows = cursor.fetchall()
            finally:
                # While the resources referenced by the ResultProxy will be
                # closed when the object is garbage collected, it's better
                # to make it explicit as some database APIs are very picky
                # about such things
                cursor.close()
            makeIdFromKey = IKeyIdSubobjectSupport(self).makeIdFromKey
            result = [makeIdFromKey(row.key) for row in rows]
            return result
        else:
            return []

    security.declareProtected(access_contents_information,
                              'objectItems')
    def objectItems(self):
        '''items'''
        return [(str(obj.getId()), obj) for obj in self.objectValues()]

    security.declareProtected(access_contents_information,
                              'objectValues')
    def objectValues(self):
        '''values'''
        if self._mapperClass:
            query = self._session.query(self._mapperClass)
            results = [item.__of__(self) for item in query.all()]
            logger.log(logging.INFO, 'query all')
            return results
        else:
            return []

    def __getattr__(self, path):
        if path == '__conform__':
            raise AttributeError
        elif IKeyIdSubobjectSupport(self).isSubobject(path):
            return self.__getObjectFromSA__(path)
        else:
            raise AttributeError

    def _setObject(self, id, object, roles=None, user=None, set_owner=1,
                   suppress_events=False):
        """Set an object into this container.

        Also sends IObjectWillBeAddedEvent and IObjectAddedEvent.
        """
        ob = object # better name, keep original function signature
        v = self._checkId(id)
        if v is not None:
            id = v
        t = getattr(ob, 'meta_type', None)

        # If an object by the given id already exists, remove it.
        makeKeyFromId = IKeyIdSubobjectSupport(self).makeKeyFromId
        key = makeKeyFromId(id)

        query = select([self._mapperClass.c.key], self._mapperClass.c.key == key)
        cursor = self._session.execute(query)
        try:
            rows = cursor.fetchall()
            if len(rows):
                self._delObject(id)
        except:
            pass

        if not suppress_events:
            notify(ObjectWillBeAddedEvent(ob, self, id))

        self._setOb(id, ob)
        ob = self._getOb(id)

        if set_owner:
            # TODO: eventify manage_fixupOwnershipAfterAdd
            # This will be called for a copy/clone, or a normal _setObject.
            ob.manage_fixupOwnershipAfterAdd()

            # Try to give user the local role "Owner", but only if
            # no local roles have been set on the object yet.
            if getattr(ob, '__ac_local_roles__', _marker) is None:
                user = getSecurityManager().getUser()
                if user is not None:
                    userid = user.getId()
                    if userid is not None:
                        ob.manage_setLocalRoles(userid, ['Owner'])

        if not suppress_events:
            notify(ObjectAddedEvent(ob, self, id))
            notifyContainerModified(self)

        OFS.subscribers.compatibilityCall('manage_afterAdd', ob, ob, self)

        return id
    
    def _delObject(self, id, dp=1, suppress_events=False):
        """Delete an object from this container.

        Also sends IObjectWillBeRemovedEvent and IObjectRemovedEvent.
        """
        ob = self._getOb(id)

        OFS.subscribers.compatibilityCall('manage_beforeDelete', ob, ob, self)

        if not suppress_events:
            notify(ObjectWillBeRemovedEvent(ob, self, id))

        self._delOb(id)

        # Indicate to the object that it has been deleted. This is
        # necessary for object DB mount points. Note that we have to
        # tolerate failure here because the object being deleted could
        # be a Broken object, and it is not possible to set attributes
        # on Broken objects.
        try:
            ob._v__object_deleted__ = 1
        except:
            pass

        if not suppress_events:
            notify(ObjectRemovedEvent(ob, self, id))
            notifyContainerModified(self)

    #database access
    def __getObjectFromSA__(self, path):
        if self._mapperClass:
            key = IKeyIdSubobjectSupport(self).makeKeyFromId(path)
            subobject = self._session.get(self._mapperClass, key)
            if subobject is None:
                raise ValueError
            else:
                result = subobject.__of__(self)
                return result
        else:
            raise ValueError, 'mapperName or dbUtilityName not set'

    def __addObjectToSA__(self, ob):
        self._session.save(ob)
        self._session.flush([ob])


    #object access
    def _getOb(self, id, default=_marker):
        try:
            return self.__getObjectFromSA__(id)
        except ValueError:
            if default is _marker:
                raise AttributeError, id
            return default

    def _setOb(self, id, ob):
        self.__addObjectToSA__(ob)

    def _delOb(self, id):
        ob = self._getOb(id)
        # When it was saved in the session, the object could not be acquisition
        # wrapped. Thus, we need to unwrap it before we delete it from the
        # session.
        mapper = aq_base(ob)
        self._session.delete(mapper)
        self._session.flush([mapper])

InitializeClass(BaseFolder)
