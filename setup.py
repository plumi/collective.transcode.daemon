from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.2'

long_description = (
    read('README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )

setup(name='collective.transcode.daemon',
      version=version,
      description="Video transcoding daemon",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='video transcoding flv mp4 ogg plone zope',
      author='unweb.me',
      author_email='we@unweb.me',
      url='https://unweb.me',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pycrypto',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
