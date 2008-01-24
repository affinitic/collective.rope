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
from AccessControl.Permissions import access_contents_information

from Globals import InitializeClass

from Acquisition import aq_base

from OFS.Folder import Folder
from OFS.event import ObjectWillBeRemovedEvent

from zope.component import getUtility
from zope.interface import implements
from zope.event import notify
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.contained import notifyContainerModified

from collective.lead.interfaces import IDatabase

from interfaces import IRDBFolder
from interfaces import IKeyIdSubobjectSupport

logger = logging.getLogger('Rope basefolder')

_marker = object()

class KeyIdSubobjectSupport(object):

    subobjectSuffix = '_rf'

    def __init__(self, context):
        self.context = context

    def makeIdFromKey(self, key):
        """see interfaces"""
        return key + self.subobjectSuffix

    def makeKeyFromId(self, id):
        """see interfaces"""
        return id[:-len(self.subobjectSuffix)]

    def isSubobject(self, id):
        """see interfaces"""
        return id.endswith(self.subobjectSuffix)

class BaseFolder(Folder):
    """subobjects stored outside ZODB through SQLAlchemy"""

    security = ClassSecurityInfo()

    implements(IRDBFolder)

    @property
    def _database(self):
        db = getUtility(IDatabase, self.databaseName)
        db.session
        return db

    @property
    def _session(self):
        return self._database.session

    def getMapperClass(self):
        '''mapperClass'''
        db = self._database
        return db.mappers[self.mapperName].class_

    @property
    def _mapperClass(self):
        return self.getMapperClass()

    def _checkId(self, id, allow_dup=0):
        pass

    security.declareProtected(access_contents_information,
                              'objectIds')
    def objectIds(self):
        '''ids'''
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

    security.declareProtected(access_contents_information,
                              'objectItems')
    def objectItems(self):
        '''items'''
        return [(str(obj.getId()), obj) for obj in self.objectValues()]

    security.declareProtected(access_contents_information,
                              'objectValues')
    def objectValues(self):
        '''values'''
        query = self._session.query(self._mapperClass)
        results = [item.__of__(self) for item in query.all()]
        logger.log(logging.INFO, 'query all')
        return results

    def __getattr__(self, path):
        if path == '__conform__':
            return Folder.__getattr__(self, path)
        elif IKeyIdSubobjectSupport(self).isSubobject(path):
            return self.__getObjectFromSA__(path)
        else:
            return Folder.__getattr__(self, path)

    def __getObjectFromSA__(self, path):
        #XXX should support multiple keys
        key = IKeyIdSubobjectSupport(self).makeKeyFromId(path)
        subobject = self._session.get(self._mapperClass, key)
        if subobject is None:
            raise ValueError
        else:
            result = subobject.__of__(self)
            return result

    def __addObjectToSA__(self, ob):
        self._session.save(ob)
        self._session.flush([ob])

    def _getOb(self, id, default=_marker):
        try:
            return self.__getObjectFromSA__(id)
        except ValueError:
            if default is _marker:
                raise AttributeError, id
            return default

    def _setOb(self, id, ob):
        self.__addObjectToSA__(ob)

    def _delObject(self, id, dp=1, suppress_events=False):
        ob = self._getOb(id)
        
        if not suppress_events:
            notify(ObjectWillBeRemovedEvent(ob, self, id))
      
        # When it was saved in the session, the object could not be acquisition
        # wrapped. Thus, we need to unwrap it before we delete it from the
        # session.
        mapper = aq_base(ob)
        self._session.delete(mapper)
        self._session.flush([mapper])
        
        if not suppress_events:
            notify(ObjectRemovedEvent(ob, self, id))
            notifyContainerModified(self)

InitializeClass(BaseFolder)
