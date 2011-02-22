from setuptools import setup, find_packages

version = '0.1'

setup(name='collective.rope',
      version=version,
      description="Zope2 support for objects built with SQLAlchemy of data "
                  "stored in relational databases",
      long_description="""\
""",
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Community',
      author_email='plone@plone.org',
      url='http://svn.plone.org/svn/collective/collective.rope',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.saconfig'],
      extras_require=dict(
            test=['zope.testing', 'Products.CMFTestCase']))
