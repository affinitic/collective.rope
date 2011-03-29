import sqlalchemy

from plone.testing import z2
import plone.app.testing.layers

import collective.rope
from collective.rope.utils import makeDictionary
from collective.rope.utils import compareDictionary
from collective.rope.utils import makeReferenceBag

from collective.rope import cmf_layers

SIMPLE_ITEM_MAPPER = 'collective.rope.tests.simpleitem.RopeSimpleItem'
PORTAL_CONTENT_MAPPER = 'collective.rope.tests.portalcontent.RopePortalContent'
AT_CONTENT_MAPPER = 'collective.rope.tests.atcontent.RopeATContent'

ROPE_FIXTURE = plone.testing.zca.ZCMLSandbox(bases=(z2.STARTUP,),
    name="ROPE_FIXTURE",
    filename="testingzope.zcml", package=collective.rope)


class RopeInstall(plone.testing.Layer):

    defaultBases = (ROPE_FIXTURE,)

    def setUp(self):
        with z2.zopeApp() as app:
            z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with z2.zopeApp() as app:
            z2.uninstallProduct(app, 'collective.rope')

ROPE_INSTALL = RopeInstall(name="ROPE_INSTALL")

ROPE_INTEGRATION = z2.IntegrationTesting(bases=(ROPE_FIXTURE,),
    name="ROPE_INTEGRATION")

ROPE_FUNCTIONAL = z2.FunctionalTesting(
    bases=(ROPE_INSTALL, ),
    name="ROPE_FUNCTIONAL")

CMF_ROPE_ZCML_FIXTURE = plone.testing.zca.ZCMLSandbox(
    bases=(ROPE_FIXTURE, ),
    name="CMF_ROPE_ZCML_FIXTURE",
    filename="testingcmf.zcml", package=collective.rope)


class CMFRope(plone.testing.Layer):
    # Rope ZCML must be setup before CMF portal local registry is hooked to a
    # global registry
    defaultBases = (CMF_ROPE_ZCML_FIXTURE, cmf_layers.PORTAL_FIXTURE)

    def setUp(self):
        with cmf_layers.CMFDefaultPortal() as portal:
            cmf_layers.applyProfile(portal,
                'collective.rope.tests:ropeoncmf')

CMF_ROPE_FIXTURE = CMFRope(name="CMF_ROPE_FIXTURE")

CMF_ROPE_INTEGRATION = cmf_layers.IntegrationTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMF_ROPE_INTEGRATION')

CMF_ROPE_FUNCTIONAL = cmf_layers.FunctionalTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMF_ROPE_FUNCTIONAL')

PLONE_ROPE_FIXTURE = plone.app.testing.PloneWithPackageLayer(
    name="PLONE_ROPE_FIXTURE",
    zcml_filename="testingplone.zcml",
    zcml_package=collective.rope,
    gs_profile_id='collective.rope.tests:ropeonat'
    )

PLONE_ROPE_INTEGRATION = plone.app.testing.layers.IntegrationTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC_PLONE_ROPE_INTEGRATION')

PLONE_ROPE_FUNCTIONAL = plone.app.testing.layers.FunctionalTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC_PLONE_ROPE_FUNCTIONAL')


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
    mappers['m_simpleitem'] = sqlalchemy.orm.mapper(RopeSimpleItem, j,
        properties={'key': [t_data.c.key, t_simpleitem.c.key], })
    t_portalcontent = tables['t_portalcontent']
    j = sqlalchemy.sql.join(t_data, t_portalcontent)
    from collective.rope.tests.portalcontent import RopePortalContent
    mappers['m_portalcontent'] = sqlalchemy.orm.mapper(
        RopePortalContent, j,
        properties={'key': [t_data.c.key, t_portalcontent.c.key], })
    t_atcontent = tables['t_atcontent']
    j = sqlalchemy.sql.join(t_data, t_atcontent)
    from collective.rope.tests.atcontent import RopeATContent
    mappers['m_atcontent'] = sqlalchemy.orm.mapper(RopeATContent, j,
        properties={'key': [t_data.c.key, t_atcontent.c.key], })


def setupDatabase(engine):
    sqlalchemy.orm.clear_mappers()
    metadata = sqlalchemy.MetaData(engine)
    tables = {}
    _setup_tables(metadata, tables)
    _setup_mappers(tables, {})
    metadata.drop_all()
    metadata.create_all()
