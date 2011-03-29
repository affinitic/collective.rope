import sqlalchemy

from collective.rope.utils import makeDictionary
from collective.rope.utils import compareDictionary
from collective.rope.utils import makeReferenceBag


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
