# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='deploy-commander',
    version='0.0.1',
    author=u'Ference van Munster',
    author_email='info@munstermedia.nl',
    packages=['fabric'],
    url='http://github.com/munstermedia/deploy-commander',
    license='Free',
    description='Simple command line tool to command your deployments',
    long_description=open('README.txt').read(),
    zip_safe=False,
)