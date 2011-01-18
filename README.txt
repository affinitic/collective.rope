collective.rope
===============

Zope2, CMF and Archetypes base classes to store content in relational
databases through SQLAlchemy.

Functionality
-------------

``collective.rope`` provides helps to build Zope2 content that is stored in
relational databases (RDB).

Data is stored in RDB through the use of SQLAlchemy mappers.

``collective.rope`` provides base classes with various levels of support of 
Zope2/Plone systems.  
There are classes for basic Zope2 support, for CMF content with DCWorkflow
support, and for Plone Archetypes support.

Zope2 base class uses SQLAlchemy mappers that include pickle columns that hold
Zope2 specific ``__roles__``, ``__provides__``, ``__zope_permissions__``
and ``__ac_local_roles__`` values.

To support DCWorkflow, the mappers used by the CMF base class also needs to 
include a ``workflow_history`` pickle column.

Archetypes base class requires mappers with ``_at_uid`` and ``at_references``
columns.

Credits
-------

Original work funded by Tabellio, project by "Parlement de la Communaute
Francaise de Belgique" and "Parlement francophone bruxellois" (Belgium).
