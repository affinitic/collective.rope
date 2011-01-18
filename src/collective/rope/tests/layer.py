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
from cStringIO import StringIO

import sqlalchemy

from Testing.ZopeTestCase.ZopeLite import installPackage

import Products.Five

from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig


import z3c.saconfig

import collective.rope
from collective.rope.utils import makeDictionary
from collective.rope.utils import compareDictionary
from collective.rope.utils import makeReferenceBag

from Products.PloneTestCase.layer import PloneSite

SIMPLE_ITEM_MAPPER = 'collective.rope.tests.simpleitem.RopeSimpleItem'
PORTAL_CONTENT_MAPPER = 'collective.rope.tests.portalcontent.RopePortalContent'
AT_CONTENT_MAPPER = 'collective.rope.tests.atcontent.RopeATContent'
DB_UTILITY_NAME = 'test.database'


def _setup_tables(metadata, tables):
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
    tables['t_portalcontent'] = sqlalchemy.Table('t_portalcontent',
           metadata,
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
    tables['t_atcontent'] = sqlalchemy.Table('t_atcontent', metadata,
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
           # for Archetypes
           sqlalchemy.Column('_at_uid', sqlalchemy.TEXT),
           sqlalchemy.Column('at_references', sqlalchemy.PickleType,
                default=makeReferenceBag),
           )


def _setup_mappers(tables, mappers):
    t_data = tables['t_data']
    t_simpleitem = tables['t_simpleitem']
    j = sqlalchemy.sql.join(t_data, t_simpleitem)
    from collective.rope.tests.simpleitem import RopeSimpleItem
    mappers['m_simpleitem'] = sqlalchemy.orm.mapper(RopeSimpleItem, j)

    t_portalcontent = tables['t_portalcontent']
    j = sqlalchemy.sql.join(t_data, t_portalcontent)
    from collective.rope.tests.portalcontent import RopePortalContent
    mappers['m_portalcontent'] = sqlalchemy.orm.mapper(
            RopePortalContent,
            j)

    t_atcontent = tables['t_atcontent']
    j = sqlalchemy.sql.join(t_data, t_atcontent)
    from collective.rope.tests.atcontent import RopeATContent
    mappers['m_atcontent'] = sqlalchemy.orm.mapper(RopeATContent, j)


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
    ZCML.__bases__ = (ZopeLite, )


def _setUpRope():
    XMLConfig('configure.zcml', Products.Five)()
    XMLConfig('meta.zcml', Products.GenericSetup)()
    XMLConfig('meta.zcml', z3c.saconfig)()
    XMLConfig('configure.zcml', Products.GenericSetup)()
    XMLConfig('configure.zcml', collective.rope)()
    installPackage('collective.rope')
    xmlconfig(StringIO("""
    <configure xmlns="http://namespaces.zope.org/db">
       <engine name="dummy" url="sqlite:///:file.db"
               setup="collective.rope.tests.layer.setupDatabase"/>
       <session name="" engine="dummy" />
    </configure>
    """))


def _tearDownRope():
    sqlalchemy.orm.clear_mappers()


class Rope(ZCML):

    @classmethod
    def setUp(cls):
        _setUpRope()

    @classmethod
    def tearDown(cls):
        _tearDownRope()


class Portal(ZCML):

    @classmethod
    def setUp(cls):
        for func, args, kw in _deferred_setup:
            func(*args, **kw)

    @classmethod
    def tearDown(cls):
        for func, args, kw in _deferred_cleanup:
            func(*args, **kw)


class RopePortal(Portal):

    @classmethod
    def setUp(cls):
        _setUpRope()

    @classmethod
    def tearDown(cls):
        _tearDownRope()


class RopePloneSite(PloneSite):

    @classmethod
    def setUp(cls):
        _setUpRope()

    @classmethod
    def tearDown(cls):
        _tearDownRope()


def setupDatabase(engine):
    sqlalchemy.orm.clear_mappers()
    metadata = sqlalchemy.MetaData(engine)
    tables = {}
    _setup_tables(metadata, tables)
    _setup_mappers(tables, {})
    metadata.drop_all()
    metadata.create_all()
