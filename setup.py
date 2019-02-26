from setuptools import setup, find_packages

version = '1.0'

setup(name='example.migration',
      version=version,
      description='A example policy package for migrating from Plone 4 to Plone 5',
      long_description=open("README.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone policy',
      author='Philip Bauer',
      author_email='info@starzel.de',
      url='https://github.com/starzel/example.migration',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['example'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'example.theme',
          'example.contenttype.section',
          'webcouturier.dropdownmenu',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
