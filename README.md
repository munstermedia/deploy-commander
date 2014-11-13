#django-dtap

One app to rule all your apps!

A tool for setting up a Development Testing Acceptance and Production flow, build on python/django, but can be used by any codebase

Note : This application is still in it's development phase.

## Goals

This application is intented to easally manage deployments for multiple apps from different codebases with different programming languages.

- Ease of deployments
- Ease of rollbacks
- Simplified deployment by simple configurations
- Based on unix based environments

- - -
#Usage

This is currently a quick command line tool. In the future there will be an visual admin for your deployments.

On a production environment it's best to create a dedicated deployment environment for all your deployments.

## Best practices

- Don't commit config files, especially with credentials
- For production use a dedicated deployment environment 

- - -

#Setup

## Code

Checkout this code in your local environment.

```
git clone git@github.com:munstermedia/django-dtap.git
```

## Ubuntu

You'll need to install the fabric python library. On ubuntu you'll only need to run the command:

```
sudo apt-get install fabric
```

## Setup folders
We'll need to create base folders for the configuration and templates.

```
mkdir ./.config
mkdir ./.templates
```

## Skeleton

There is a skeleton structure available in the ./skeleton folder.
This folder contains different examples you can use for different type of projects

- - -

## Configuration
The configuration files are located in the ./config folder.

These are json structured configs where you can setup stuff like ssh credentials, symlinks, mysql backup and much more...

### Settings
It's important to understand how settings are loaded and which settings are possible.
We've implemented a nice feature to inherit settings based on environments and projects.

When running a deployment for a project it will first load in sequence:

1.    Generic config (default.json)
2.    Generic environment config (production.json)
3.    Project config (project/default.json)
4.    Project environment config (production.json)

#### Main settings

##### ./.config/default.json
This is the base config. Everything will be extended from this config.

##### ./.config/development.json
Main config for development environments. 
This will overwrite the ./.config/default.json

##### ./.config/testing.json
Main config for testing environments. 
This will overwrite the ./.config/default.json

##### ./.config/staging.json
Main config for staging environments. 
This will overwrite the ./.config/default.json

##### ./.config/production.json
Main config for production environments. 
This will overwrite the ./.config/default.json

#### Project settings

##### ./.config/*project*/default.json
Main Config for the development project. 
This will overwrite the ./.config/default.json, and development.json

##### ./.config/*project*/development.json
Config for the development project. 
This will overwrite the ./.config/default.json, default.json and development.json

##### ./.config/*project*/testing.json
Config for the development project. 
This will overwrite the ./.config/default.json, default.json and testing.json

##### ./.config/*project*/staging.json
Config for the development project. 
This will overwrite the ./.config/default.json, default.json and staging.json

##### ./.config/*project*/production.json
Config for the development project. 
This will overwrite the ./.config/default.json, default.json and production.json


For more information about the configuration options please see the examples in ./skeleton

- - -

## Commands


### Install app
	
```
fab project:<project> environment:<env> app.install
```

### Deploy app

```
fab project:<project> environment:<env> tag:<git tagname> app.deploy
```


### Rollback app

```
fab project:<project> environment:<env> tag:<tag> app.rollback:<to_rollback_tag>
```

** Legend **

- project : your own defined project
- environment : [development/testing/staging/production]
- tag : Your git tag
- to_rollback_tag : Tag you want to rollback to