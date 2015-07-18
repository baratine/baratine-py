import codecs
import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.rst'), encoding = 'utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name = 'baratine',
    version = '0.9.0',
    license = 'Apache, Version 2.0',
    
    description = 'Python client for Baratine',
    long_description = long_description,
    keywords = 'baratine client',
    
    author = 'Nam Nguyen',
    author_email = 'nam@caucho.com',
    url = 'http://baratine.io/',

    packages = ['baratine'],
    install_requires = ['requests'],
    
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)