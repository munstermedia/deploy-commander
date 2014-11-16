#deploy-commander

> One app to rule all your apps!

A tool for setting up a different environments like a DTAP.
Deploy commander is build on python/fabric, but can be used for any project.

** Note : This application is still in it's development phase. **

## Goals

This application is intented to easally manage deployments for multiple apps from different codebases with different programming languages.

- Ease of deployments
- Ease of rollbacks
- Simplified deployment by simple configurations
- Based on unix based environments

- - -

#Usage

This is a command line tool to run on unix based environments.

On a production setup it's best to create a dedicated environment to manage your deployments.

## General command
	
```
deploy-commander go run:<action>
```

> You'll be asked for the project and the environment when you run the command.

## Best practices

- Don't commit credentials in the config files, especially with passwords.
- For production use a dedicated deployment environment.

- - -

#Quick demo setup

## Requirements

In this quick demo we'll use [virtualbox](https://www.virtualbox.org/) and [vagrant](https://www.vagrantup.com/).

We'll assume you're known with these systems.

## Install
```
// On unix type machines
pip install deploy-commander
```


## Start vagrant

[Download vagrant file](https://github.com/munstermedia/deploy-commander/blob/master/Vagrantfile)

```
// Run in root
vagrant up
```

This will start a ubuntu box with ip 192.168.56.111 which we can use to deploy to.

## Lets go...

### Install server
The newly created ubuntu box need some stuff to be installed.
To do this we've created an action called `install-server`

```
deploy-commander go run:install-server
```

### Install app
We're gonna install a new app from the defined repo.
Run the command and yust leave the prompt empty... it will use the default settings:

* project : example
* environment : development

```
deploy-commander go run:install-app
```

This will create base folders and clone the repo into a development enviroment

> Try to enter different environments, in this example they all point to the vagrant box, but for your production it can point to different servers.

### Deploy app

Now we're gonna deploy the source code and use the master branch to do so.

```
deploy-commander go run:deploy-app
```

This wil prompt you with the same like install but it will ask for a tag.
The default tag is `master`

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


##### Settings structure

The basic foundation of this system are actions and commands. You can execute actions, and these actions have commands to execute.

This is an example structure that we'll explain later on:


```
{
	"environments":{
		"development":{},
		"production":{},
		"staging":{},
		"testing":{}
	},
	"params":{
		"some_param":"param/value"
	},
	"post_params":{
		"dynamic_post_param":"/some/%(some_param)s/path"
	},
	"actions":{
		"deploy":{
			"title":"Deploy project",
			"commands":{
				"your-unique-id:{
					"sequence":1,
					"command":"command.action",
					"params":{
						"dynamic_param":"%(dynamic_param)s/repo",
						"dynamic_post_param":"%(dynamic_post_param)s/source/%(tag)s"
					}
				}
			}
		}	
	}
}
```

##### environments

Contains self defined environments, normally this is a standard dtap environment.
These key's are used when executing the main run command

##### params

Params can be (re)used in post param values and command param values.
This is an easy way to manage central 'constants' that can be used by different commands

* key : key/value

##### post_params

These params are build/formatted with the param values. This is an easy way to generate generic reusable params for your commands.
In the example we used a path, this is a good way to manage base path's for your commands

* key : key/value

##### actions

Actions define a set of commands to execute. This is one of the core elements of the system. The key defined will be usable in the command line execute. (fab go run:<action>)

* title : General text to parse when executing
* commands : Many command definitions to execute

##### commands

Commands can best be defined as an isolated predefined functions.
We're continuessly developing on these commands to give you as much features.

* sequence : Numeric value in which order the commands will be executed
* command : Main command to execute <package>.<action>
* params : Set of key/values for the command

> You can use generic params in the command params to prevent repetition



#### Main settings

##### ./.config/default.json
This is the base config. Everything will be extended from this config.

##### ./.config/*environment*.json
Main config for development environments. 
This will overwrite the ./.config/default.json

#### Project settings

##### ./.config/*project*/default.json
Main Config for the development project. 
This will overwrite the ./.config/default.json, and development.json

##### ./.config/*project*/*environment*.json
Config for the development project. 
This will overwrite the ./.config/default.json, default.json and development.json


> For more information about the configuration options please see the examples in ./config

- - -

# Source code setup

## Code

Checkout this code in your local environment.

```
git clone git@github.com:munstermedia/deploy-commander.git
```

## Ubuntu

You'll need to install the fabric python library. 
On linux based system you'll need to run:

```
// Ubuntu
sudo apt-get install fabric

// Mac
sudo pip install fabric
```


## Setup folders
We'll need to create base folders for the configuration and templates.

There is a structure available in the ./config folder.
This folder contains different examples you can use for different type of projects.

Copy the example structure to get started.

> Please take a look at the settings and try to understand what is stored in these files.
> More information can be found further on in this document.


