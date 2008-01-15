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

import sqlalchemy

from Testing.ZopeTestCase.ZopeLite import installPackage

import Products.Five

from zope.configuration.xmlconfig import XMLConfig
from zope.component import provideUtility
from zope.component import getUtility
from zope.component import getSiteManager

import collective.lead
from collective.lead import Database
from collective.lead.interfaces import IDatabase

from collective.rope.basesimple import makeDictionary
from collective.rope.basesimple import compareDictionary

SIMPLE_ITEM_MAPPER = 'm_simpleitem'
PORTAL_CONTENT_MAPPER = 'm_portalcontent'
DB_UTILITY_NAME='test.database'

class TestDatabase(Database):
    @property
    def _url(self):
        return sqlalchemy.engine.url.URL(drivername='sqlite',
                database=":memory:",
                host="")
    
    @property
    def _engine_properties(self):
        return {"echo":False}

    def _setup_tables(self, metadata, tables):
        tables['t_data'] = sqlalchemy.Table('t_data', metadata,
               sqlalchemy.Column('key', sqlalchemy.TEXT, 
                    primary_key=True),
               sqlalchemy.Column('title', sqlalchemy.TEXT),
               sqlalchemy.Column('field1', sqlalchemy.TEXT, index=True),
               sqlalchemy.Column('field2', sqlalchemy.TEXT, index=True),
               sqlalchemy.Column('field3', sqlalchemy.TEXT),
               sqlalchemy.Column('field4', sqlalchemy.TEXT),
               sqlalchemy.Column('field5', sqlalchemy.TEXT),
               )
        PickleDict = sqlalchemy.PickleType(comparator=compareDictionary)
        tables['t_simpleitem'] = sqlalchemy.Table('t_simpleitem', metadata,
               sqlalchemy.Column('key', sqlalchemy.TEXT,
                    sqlalchemy.ForeignKey('t_data.key'),
                    primary_key=True),
               # for Zope
               sqlalchemy.Column('__roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__ac_local_roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__zope_permissions__', PickleDict,
                    default=makeDictionary),
               )
        tables['t_portalcontent'] = sqlalchemy.Table('t_portalcontent', metadata,
               sqlalchemy.Column('key', sqlalchemy.TEXT,
                    sqlalchemy.ForeignKey('t_data.key'),
                    primary_key=True),
               # for Zope
               sqlalchemy.Column('__roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__ac_local_roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__zope_permissions__', PickleDict,
                    default=makeDictionary),
               # for DCWorkflow
               sqlalchemy.Column('workflow_history', PickleDict,
                    default=makeDictionary),
               )

    def _setup_mappers(self, tables, mappers):
        t_data = tables['t_data']
        t_simpleitem = tables['t_simpleitem']
        j = sqlalchemy.sql.join(t_data, t_simpleitem)
        from collective.rope.tests.simpleitem import RopeSimpleItem
        mappers[SIMPLE_ITEM_MAPPER] = sqlalchemy.orm.mapper(RopeSimpleItem, j)
        
        t_portalcontent = tables['t_portalcontent']
        j = sqlalchemy.sql.join(t_data, t_portalcontent)
        from collective.rope.tests.portalcontent import RopePortalContent
        mappers[PORTAL_CONTENT_MAPPER] = sqlalchemy.orm.mapper(RopePortalContent, j)


from zope.testing.cleanup import cleanUp as _cleanUp

def cleanUp():
    '''Cleans up the component architecture.'''
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0


def setDebugMode(mode):
    '''Allows manual setting of Five's inspection of debug mode
       to allow for ZCML to fail meaningfully.
    '''
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode


def safe_load_site():
    '''Loads entire component architecture (w/ debug mode on).'''
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    setDebugMode(0)


def safe_load_site_wrapper(func):
    '''Wraps func with a temporary loading of entire component
       architecture. Used as a decorator.
    '''
    def wrapped_func(*args, **kw):
        safe_load_site()
        value = func(*args, **kw)
        cleanUp()
        return value
    return wrapped_func

_deferred_setup = []
_deferred_cleanup = []


class ZCML:
    def setUp(cls):
        '''Sets up the CA by loading etc/site.zcml.'''
        safe_load_site()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        cleanUp()
    tearDown = classmethod(tearDown)

def onsetup(func):
    '''Defers a function call to PloneSite layer setup.
       Used as a decorator.
    '''
    def deferred_func(*args, **kw):
        _deferred_setup.append((func, args, kw))
    return deferred_func


def onteardown(func):
    '''Defers a function call to PloneSite layer tear down.
       Used as a decorator.
    '''
    def deferred_func(*args, **kw):
        _deferred_cleanup.append((func, args, kw))
    return deferred_func


# Derive from ZopeLite layer if available
try:
    from Testing.ZopeTestCase.layer import ZopeLite
except ImportError:
    pass
else:
    ZCML.__bases__ = (ZopeLite,)

class Rope(ZCML):
    @classmethod
    def setUp(cls):
        XMLConfig('configure.zcml', Products.Five)()
        XMLConfig('configure.zcml', collective.lead)()
        XMLConfig('meta.zcml', Products.GenericSetup)()
        XMLConfig('configure.zcml', Products.GenericSetup)()
        installPackage('collective.rope')
        testDb = TestDatabase()
        provideUtility(testDb, name=DB_UTILITY_NAME, provides=IDatabase)
        setupDatabase()

    @classmethod
    def tearDown(cls):
        sqlalchemy.orm.clear_mappers()
        sm = getSiteManager()
        sm.unregisterUtility(name=DB_UTILITY_NAME, provided=IDatabase)

class Portal(ZCML):
    @classmethod
    def setUp(cls):
        for func, args, kw in _deferred_setup:
            func(*args, **kw)

    @classmethod
    def tearDown(cls):
        for func, args, kw in _deferred_cleanup:
            func(*args, **kw)

class RopePortal(Rope):
    @classmethod
    def setUp(cls):
        for func, args, kw in _deferred_setup:
            func(*args, **kw)
    
    @classmethod
    def tearDown(cls):
        for func, args, kw in _deferred_cleanup:
            func(*args, **kw)

def setupDatabase():
    database = getUtility(IDatabase, name=DB_UTILITY_NAME)
    metadata = database.metadata
    metadata.drop_all()
    metadata.create_all()
