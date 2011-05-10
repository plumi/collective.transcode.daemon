import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.8'

long_description = (
    read('README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('docs/CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs/CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )

setup(name='collective.transcode.daemon',
      version=version,
      description="Video transcoding daemon",
      long_description=long_description,
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Video :: Conversion',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='video transcoding flv mp4 ogg plone zope twisted',
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
          'hashlib',
          'Twisted',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
