from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.deform',
      version=version,
      description="Little helper to make deform work with zope",
      long_description="\n".join([
          open("README.rst").read(),
          open(os.path.join("docs", "index.rst")).read(),
          open("CHANGES.txt").read()]),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://git.github.com/do3cc/collective.deform',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      'collective.js.jqueryui',
        'deform',
        'five.grok',
        'setuptools',
        'WebOb',
        'z3c.autoinclude',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
