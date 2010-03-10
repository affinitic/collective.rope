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
from Products.Five import zcml
from Products.Five import fiveconfigure

from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig
from zope.component import getSiteManager


import z3c.saconfig
import collective.rope
from collective.rope.utils import makeDictionary
from collective.rope.utils import compareDictionary
from collective.rope.utils import makeReferenceBag

from Products.CMFTestCase.layer import onsetup as cmf_onsetup
from Products.PloneTestCase.layer import onsetup as plone_onsetup
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


def _setUpRope():
    XMLConfig('configure.zcml', Products.Five)()
    XMLConfig('meta.zcml', Products.GenericSetup)()
    XMLConfig('configure.zcml', Products.GenericSetup)()
    XMLConfig('meta.zcml', z3c.saconfig)()
    xmlconfig(StringIO("""
    <configure xmlns="http://namespaces.zope.org/db">
       <engine name="dummy" url="sqlite:///:file.db"
               setup="collective.rope.tests.layer.setupDatabase"/>
       <session name="" engine="dummy" />
    </configure>
    """))


def _tearDownRope():
    sqlalchemy.orm.clear_mappers()
    sm = getSiteManager()


def setup_product():
    """Set up additional products and ZCML required to test this product.
    """

    # Load the ZCML configuration for this package and its dependencies

    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.rope)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    installPackage('collective.rope')

# The plone_onsetup decorator causes the execution of this body to be deferred
# until the setup of the Plone site testing layer.
setup_plone_product = plone_onsetup(setup_product)
# The cmf_onsetup decorator causes the execution of this body to be deferred
# until the setup of the CMF site testing layer.
setup_cmf_product = cmf_onsetup(setup_product)

from Products.CMFTestCase.layer import CMFSite


class Rope(CMFSite):

    @classmethod
    def setUp(cls):
        _setUpRope()

    @classmethod
    def tearDown(cls):
        _tearDownRope()


class Portal(CMFSite):
    pass


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
