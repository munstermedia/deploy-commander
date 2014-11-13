django-dtap
===========
One app to rule your dtap environments!

A tool for setting up a Development Testing Acceptance and Production flow, build on python/django, but used by any codebase

This application is still in it's development phase.

[Goals]
....


Setup
=====

Ubuntu
------

	sudo apt-get install fabric


Usage
=====
This is currently a quick command line tool. In the future there will be an visual admin for your deployments.

Configuration
-------------
The configuration is located ind the config folder.
These are json structured configs where you can setup your credentials and project properties



Deploy
------
Command:

	fab project:<project> environment:<env> tag:<git tagname> app.deploy
	
- project : your own defined project
- environment : [dev/testing/staging/production]
- tag : Your git tag

