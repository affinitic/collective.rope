from setuptools import setup, find_packages

version = '0.1'

setup(name='collective.rope',
      version=version,
      description=("Zope2, CMF and Archetypes base classes to store content "
          "in relational databases through SQLAlchemy."),
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Godefroid Chapelle',
      author_email='gotcha@bubblenet.be',
      url='',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2',
          'z3c.saconfig',
      ],
      extras_require=dict(
          test=[
               'plone.app.testing',
               ],
      ),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
