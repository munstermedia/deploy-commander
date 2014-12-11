# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='deploy-commander',
    version='0.0.25',
    author=u'Ference van Munster',
    author_email='info@munstermedia.nl',
    packages=find_packages(),
    install_requires=['pycrypto==2.6.1', 'ecdsa', 'jinja2', 'fabric==1.10.0','simple-crypt'],
    url='http://github.com/munstermedia/deploy-commander',
    license='Free',
    description='Simple command line tool to command your deployments',
    long_description=open('README.txt').read(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'deploy-commander = deploy_commander.main:main',
        ]
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
)