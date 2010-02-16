from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='collective.transcode.daemon',
      version=version,
      description="Video transcoding daemon",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='video transcoding flv plone zope',
      author='unweb.me',
      author_email='we@unweb.me',
      url='https://unweb.me',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
