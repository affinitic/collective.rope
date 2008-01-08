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

import zope.app.component
from zope.configuration.xmlconfig import XMLConfig
from zope.component import provideUtility
from zope.component import getUtility
from zope.component import getSiteManager

import collective.lead
from collective.lead import Database
from collective.lead.interfaces import IDatabase

from collective.rope.basesimple import makeDictionary
from collective.rope.basesimple import compareDictionary

SIMPLE_MAPPER_NAME = 'm_simple'
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
        tables['t_simple'] = sqlalchemy.Table('t_simple', metadata,
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
        tables['t_zope_simple'] = sqlalchemy.Table('t_zope_simple', metadata,
               sqlalchemy.Column('key', sqlalchemy.TEXT,
                    sqlalchemy.ForeignKey('t_simple.key'),
                    primary_key=True),
               # for Zope
               sqlalchemy.Column('__roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__ac_local_roles__', sqlalchemy.PickleType),
               sqlalchemy.Column('__zope_permissions__', PickleDict,
                    default=makeDictionary),
               )

    def _setup_mappers(self, tables, mappers):
        t_simple = tables['t_simple']
        t_zope = tables['t_zope_simple']
        j = sqlalchemy.sql.join(t_simple, t_zope)
        from collective.rope.tests.item import RopeSimpleItem
        mappers[SIMPLE_MAPPER_NAME] = sqlalchemy.orm.mapper(RopeSimpleItem, j)

class RopeTestLayer:
    @classmethod
    def setUp(cls):
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('configure.zcml', Products.Five)()
        XMLConfig('configure.zcml', collective.lead)()
        XMLConfig('configure.zcml', collective.rope.tests)()
        installPackage('collective.rope')
        testDb = TestDatabase()
        provideUtility(testDb, name=DB_UTILITY_NAME, provides=IDatabase)

    @classmethod
    def tearDown(cls):
        sm = getSiteManager()
        sm.unregisterUtility(name=DB_UTILITY_NAME, provided=IDatabase)

def setupDatabase():
    database = getUtility(IDatabase, name=DB_UTILITY_NAME)
    metadata = sqlalchemy.MetaData(bind=database.engine)
    database._setup_tables(metadata,{})
    metadata.drop_all()
    metadata.create_all()
