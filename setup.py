#!/usr/bin/env python 

from distutils.core import setup 
import os 


REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(REPO_ROOT, 'open_municipio')
VERSION_FILE_PATH = os.path.join(PROJECT_ROOT, 'VERSION')


setup(
    name = 'OpenMunicipio',
    version = open(VERSION_FILE_PATH).read().strip(),
    description = """
                  A web platform for increasing transparency in italian municipalities.
                  """, 
    author='OpenPolis & InformaEtica',
    author_email='info@openmunicipio.it',
    url='http://openpolis.github.com/open_municipio/',
    packages=['open_municipio'],
    install_requires=[
        "Django == 1.4.5",
        "South >= 0.7.3",
        "django-extensions==0.9",
        "poster==0.8.1",
        "BeautifulSoup==3.2.1",
        "PIL==1.1.7",
        "pysolr==2.1.0-beta",
        "lxml == 2.3.5",
        "sorl-thumbnail==11.12",
        "docutils==0.9.1",
        "django-tinymce==1.5.1b2",
    ],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Javascript',
    ]
)
