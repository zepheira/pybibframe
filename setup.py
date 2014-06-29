# -*- coding: utf-8 -*-
import sys, os
from distutils.core import setup

versionfile = 'lib/version.py'
exec(compile(open(versionfile, "rb").read(), versionfile, 'exec'), globals(), locals())
__version__ = '.'.join(version_info)

setup(
    name = 'pybibframe',
    version=__version__,
    description = 'Python tools for BIBFRAME (Bibliographic Framework), a Web-friendly framework for bibliographic descriptions in libraries, for example.',
    license = 'License :: OSI Approved :: Apache Software License',
    author = 'Uche Ogbuji',
    author_email = 'uche@ogbuji.net',
    maintainer = 'Zepheira',
    maintainer_email = 'uche@zepheira.com',
    url = 'http://zepheira.com/',
    package_dir={'bibframe': 'lib'},
    packages = ['bibframe', 'bibframe.reader', 'bibframe.writer', 'bibframe.contrib', 'bibframe.plugin'],
    scripts=['exec/marc2bf', 'exec/marcbin2xml'],
    classifiers = [ # From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        #"Environment :: Other Environment",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
    long_description = '''
    '''
)
