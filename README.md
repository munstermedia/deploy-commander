# deploy-commander

> Continuous Integration Deployments to rule all your applications !

A tool for setting up a different environments most used for managing DTAP flows.
Deploy commander is build directly on python/fabric, but can be used for any project.

Main goal of this system is to configure your deployment, and not programm it.
There are other flavors for setting up your dtap... we're focussing on simplicity and transparancy. Next to that we want to create a centralized system to manage different deployments for multiple apps on different servers.

** Note : This application is still in it's development phase. **

## Soon

- Attach github and bitbucket hooks to automate the deployment process

## So it's not...?

- Puppet
- Chef
- Sys ops server management
- Jenkins
- Capistrano

## Goals

- Ease of deployments
- Ease of rollbacks
- Simplified deployment by simple configurations
- Based on unix based environments
- Continuous integration

- - -

#Usage

This is a command line tool to run on unix based environments.

On a production setup it's best to create a dedicated environment to manage your deployments.


## Best practices


- In production encrypt the config files.
- On unix based machines make sure the user directory (best to use deploy user) is encrypted/secured
- Make sure if you make a backup of copy on your dev, that it's secured.
- For production use a dedicated deployment environment.

- - -

#Quick demo setup

## Requirements

In this quick demo we'll use [virtualbox](https://www.virtualbox.org/) and [vagrant](https://www.vagrantup.com/).

We'll assume you have worked with then...

We only tested this system on unix like machines, like Ubuntu and MacOS.
Currently we don't support other flavors... sorry... (allthough it must work on centos too...)


## Install
We need to install the basic python libraries and the deploy-commander codebase.

```
// On ubuntu type machines
sudo apt-get install python-pip
sudo apt-get install python-dev

// Install the python package
sudo pip install deploy-commander
```

## Setup example

We have examples available for download and it contains a basic setup with the following:

- Vagrant file (for your local dev machine)
- Setup server with puppet
- Encrypted configs
- Configs with different examples
- Main config.dist for main configuration


```
// Clone an example
git clone https://github.com/munstermedia/deploy-commander-php-example.git

// Go into repo
cd deploy-commander-php-example

// Setup main config
mv .config.dist .config

// Load development server, a ubuntu trusty box with ip 192.168.56.111
vagrant up
```

## Lets go...


### Install app
We're gonna install a new app from the defined repo.
Run the command and yust leave the prompt empty... it will use the default settings:

* project : example
* environment : development

```
deploy-commander go run:install-app
```

What just happened?

- This will create base folders and clone the repo into a development enviroment
- We've cloned a repo into `/home/<user>/<env>/repo`
- We've created a database
- We've installed the default install.sql from repo

> Try to enter different environments, in this example they all point to the vagrant box, but for your production it can point to different servers.

### Deploy app

Now we're gonna deploy the source code and use the master branch to do so.

```
deploy-commander go run:deploy-app
```

This wil prompt you with the same like install but it will ask for a tag.
The default tag is the latest from the list.

What just happened?

- We've updated `/home/<user>/<env>/repo`
- We've created `/home/<user>/<env>/source/<tag>` from the repo
- We've backupped the database in `/home/<user>/<env>/db_backup`
- We've created a symlink `/home/<user>/<env>/current` to `/home/<user>/<env>/source/<tag>`

### Rollback app

Now we're gonna rollback the app...

```
deploy-commander go run:rollback-app
```

What just happened?

- We've removed the old symlink `/home/<user>/<env>/current` and linked it to the new tag you've entered.
- If we answered yes to import database, we could rollback the database to another version.

- - -

## Configuration

The configuration files are located in the ./config folder.

These are json structured configs where you can setup stuff like ssh credentials, symlinks, mysql backup and much more...

### Main configurtion

The main configuration file must be located in the root folder and named ".config"
This config file contains json structured params, like your master password.

Don't commit this file to your repo because the master password should be stored elsewhere.

### Encrypted config's

The config files can be encrypted before you want to push them to some repo.
So you can maintain your deploy setup in git without exposing login credentials and other critical information.

There is a main password set in the .config file. Please change this password with a [strong password generator](https://strongpasswordgenerator.com/) (and make sure it's escaped for json :) )

The config files are encrypted with a AES256 encryption. For more technical info see [simple-crypt](https://pypi.python.org/pypi/simple-crypt)

To encrypt all .json config files:

```
deploy-commander encrypt_config
```

To decrypt the .json.encrypt config files:

```
deploy-commander decrypt_config
```

Note that the files are encrypted/decrypted by the master password located in the main configuration file. (.config). Do not expose this password anywhere.

So remember to setup this password on your production server manually...




### Settings
It's important to understand how settings are loaded and which settings are possible.
We've implemented a nice feature to inherit settings based on environments and projects.

When running a deployment for a project it will first load in sequence:

1.    Generic config (default.json)
2.    Generic environment config (production.json)
3.    Project config (project/default.json)
4.    Project environment config (production.json)

Say you have the following:

```
// default.json
{"data":{
	"one":{
		"var_1":"1",
		"var_2":"2"
	},
	"two":{
		"var_3":"3",
		"var_4":"4"
	}
}

// development.json
{"data":{
	"env":"development"
	"one":{
		"var_1":"2",
	},
	"two":{
		"var_3":"4",
	}
}

// project/default.json
{"data":{
	"debug":"False",
	"one":{
		"var_3":"3",
		"var_4":"4"
	},
	"two":{
		"var_2":"2",
		"var_1":"1"
	}
}

// project/development.json
{"data":{
	"debug":"True"
}

```

This will result in the following final setting:

```
{"data":{
	"debug":"True",
	"env":"development",
	"one":{
		"var_1":"2",
		"var_2":"2",
		"var_3":"3",
		"var_4":"4"
	},
	"two":{
		"var_1":"1",
		"var_2":"2",
		"var_3":"4",
		"var_4":"4"
	}
}
```

 
##### Settings structure

The basic foundation of this system are commands and action. You can initiate a command, and these have actions to execute.

This is an example structure that we'll explain later on:


```
{
	"params":{
		"some_param":"param/value"
	},
	"post_params":{
		"dynamic_post_param":"/some/%(some_param)s/path"
	},
	"commands":{
		"deploy":{
			"title":"Deploy project",
			"actions":{
				"your-own-description":{
					"sequence":1,
					"execute":"command.action",
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

* description : General text to parse when executing
* commands : Many command definitions to execute

##### commands

Commands can best be defined as an isolated predefined functions.
We're continuessly developing on these commands to give you as much features.

* sequence : Numeric value in which order the commands will be executed
* command : Main command to execute <package>.<action>
* params : Set of key/values for the command
* confirm (optional) : Asks if you want to execute this command.. you can enter an own question as it's value
* description (optional) : Can be used to describe the command

> You can use generic params in the command params to prevent repetition.
> So if you define a key/value in the 'main' params you can use this like '%(param)s'

### Commands

#### system.symlink
```
"your-own-description":{
	"sequence":1,
	"execute":"system.symlink",
	"params":{
		"source":"/path/where/to/create/symlink",
		"target":"/path/where/the/symlink/should/link"
	}
}
```

Functionality:

- Creates symlink, if symlink allready exists it will remove the existing one.

#### system.command
```
"list-source":{
	"sequence":1,
	"execute":"system.command",
	"params":{
		"command":"ls -las /home"
	}
}
```

Functionality:

- Run command on server

#### system.upload_template
```
"upload-environment-config":{
	"sequence":1,
	"execute":"system.upload_template",
	"params":{
		"source":"some/file/in/the/template/path.ini",
		"target":"/path/where/to/copy/on/the/server.ini",
		"yourvar_1":"whatever",
		"yourvar_2":"you-want"
	}
}
```

Functionality:

- Uploads template from .template folder/file to server.
- Renders the template with params.. you can use {{ param_name }} in the template. In this example the path.ini could contain the param {{ yourvar_1 }}.
- Unlimited own params.. source and target are required


#### system.download_from_remote
```
"download":{
	"sequence":1,
	"execute":"system.download_from_remote",
	"params":{
		"remote_path":"/some/remote/path/*.jpg",
		"local_path":"./templates/tmp"
	}
}
```

Functionality:

- Will download file(s)
- Can use wildcards for files.
- Can download one or more files/folders

#### aptget.install

```
"your-own-description":{
	"sequence":1,
	"execute":"aptget.install",
	"params":{
		"package":"git"
	}
}
```

Functionality:

- Runs 'apt-get install -y (package)'


#### git.install_repo

```
"your-own-description":{
	"sequence":1,
	"execute":"git.install_repo",
	"params":{
		"repo_path":"/full/path/to/repo",
		"repo_url":"https://github.com/munstermedia/demo.git"
	}
}
```
Functionality:

- Checks if repo path exists.. if not it will ask to reinstall and it will reset/remove all existing code in the path.
- Clones the repository to the path



#### git.deploy_tag
```
"your-own-description":{
	"sequence":1,
	"execute":"git.deploy_tag",
	"params":{
		"repo_path":"/full/path/to/repo",
		"tag_path":"/full/path/to/source/%(tag)s",
		("tag":"deploy-0.0.1")
	}
}
```

Functionality:

It will use the code in the repo path to go to a certain branch/tag. This will be copied to a tag path so you'll have versioned codebases living next to each other.

- Tag in params is optional, you should leave it empty by default unless you have a good reason for it.
- If tag it's not set (empty) it will list the available tags and prompt for input.
- If repo path is not existing it will exit. You'll need a valid cloned repo path
- If tag path is allready existing it will remove it and all it's content. And deploy a completely new version.
- Allow updates submodules by running 'git submodule update'


#### mysql.install_mysql
```
"your-own-description":{
	"sequence":1,
	"execute":"mysql.install_server"
}
```

Functionality:

- Runs apt-get -y install mysql-server, with : DEBIAN_FRONTEND='noninteractive' (no prompt)


#### mysql.backup_db
```
"your-own-description":{
	"sequence":1,
	"execute":"mysql.backup_db",
	"params":{
		"host":"localhost",
		"user":"root",
		"password":"root",
		"database":"your-database",
		"backup_file":"/full/path/to/database/backup/path/file.sql"
		("download_tar_to_local_file":"./local/path/db/backup.tar.gz")
	}
}
```

Funcationality:

- Runs mysqldump and creates a mysql sql that will be compressed to tar.gz.
- The generated sql file will be removed. 
- Tries to create the path on remote if it doesn't exist
- If download_tar_to_local_file is given it will download the tar.gz for local backup

#### mysql.cleanup_db_backups
```
"your-own-description":{
	"sequence":1,
	"execute":"mysql.cleanup_db_dumps",
	"params":{
		"path":"/full/path/to/database/backup/path",
		("max_backup_history":"5")
	}
}
```

Funcationality:

- Reads path for *.tar.gz files... and removes the oldest files. (by filesystem)
- max_backup_history is optional, defaults to 5


#### mysql.query
```
"your-own-description":{
	"sequence":1,
	"execute":"mysql.query",
	"params":{
		"host":"localhost",
		"user":"root",
		"password":"root",
		"query":"CREATE DATABASE IF NOT EXISTS your-db-name"
	}
}
```

Functionality:

- Execute a raw query thru the command line


#### mysql.import_file
```
"your-own-description":{
	"sequence":3,
	"execute":"mysql.import_file",
	"params":{
		"host":"localhost",
		"user":"root",
		"password":"root",
		"database":"your-database",
		"import_file":"/full/path/to/repo/.data/install.sql"
	}
}
```

Functionality:

- Executes : 'mysql -h %(host)s -u %(user)s --password='%(password)s' %(database)s  < %(import_file)s'


#### mysql.restore_db
```
"your-own-description":{
	"sequence":2,
	"execute":"mysql.restore_db",
	"params":{
		"host":"localhost",
		"user":"root",
		"password":"password",
		"database":"your-database",
		"backup_path":"/full/path/to/database/backup/path",
		("version":"sql-version")
	}
}
```

Functionality:

- By default the version is left empty, but you can force this.
- It will list the versions and prompt for a version to restore when params is empty.
- Requires valid backup version

### Full default.json example
```
{
	"roledefs":{
		"webserver": {
			"hosts": ["192.168.56.111"],
   			"config": {
				"192.168.56.111":{
					"ssh_password":"vagrant",
					"ssh_user":"vagrant"
				}
			}
		}
	},
	"environments":{
		"development":"dev",
		"production":"prod",
		"staging":"stg",
		"testing":"tst"
	},
	"params":{
		"domain":"demo.com",
		"user":"vagrant"
		"project_database_host":"localhost",
		"project_database_user":"root",
		"project_database_password":"root",
		"project_database_name":"example"
	},
	"post_params":{
		"base_path":"/home/%(user)s/%(environment)s/%(domain)s/deploy"
	},
	"commands":{
		"install-server":{
			"description":"Example setup development server",
			"actions":{
				"install-base":{
					"sequence":1,
					"execute":"aptget.install",
					"params":{
						"package":"git"
					}
				},
				"install-mysql":{
					"sequence":2,
					"execute":"mysql.install_server"
				}
			}
		},
		"install-app":{
			"description":"Install application on server",
			"actions":{
				"git-clone":{
					"sequence":1,
					"execute":"git.clone",
					"description":"First repo cloning...",
					"params":{
						"repo_path":"%(base_path)s/repo",
						"repo_url":"will-be-overwritten-by-project"
					}
				},
				"create-mysql-db":{
					"sequence":2,
					"execute":"mysql.query",
					"params":{
						"host":"%(project_database_host)s",
						"user":"%(project_database_user)s",
						"password":"%(project_database_password)s",
						"query":"CREATE DATABASE IF NOT EXISTS %(project_database_name)s"
					}
				},
				"import-project-db":{
					"sequence":3,
					"execute":"mysql.import_file",
					"params":{
						"host":"%(project_database_host)s",
						"user":"%(project_database_user)s",
						"password":"%(project_database_password)s",
						"database":"%(project_database_name)s",
						"import_file":"%(base_path)s/repo/.data/install.sql"
					}
				}
			}
		},
		"deploy-app":{
			"description":"Deploy project",
			"actions":{
				"git-deploy-tag":{
					"sequence":1,
					"execute":"git.deploy_tag",
					"params":{
						"repo_path":"%(base_path)s/repo",
						"tag_path":"%(base_path)s/source/%(tag)s"
					}
				},
				"upload-environment-config":{
					"sequence":2,
					"execute":"system.upload_template",
					"params":{
						"source":"demo/config.php",
						"target":"%(base_path)s/source/%(tag)s/config.php",
						"dbname":"%(project_database_name)s",
						"dbpassword":"%(project_database_password)s",
						"dbuser":"%(project_database_user)s"
					}
				},
				"mysql-backup":{
					"sequence":3,
					"execute":"mysql.backup_db",
					"params":{
						"host":"%(project_database_host)s",
						"user":"%(project_database_user)s",
						"password":"%(project_database_password)s",
						"database":"%(project_database_name)s",
						"backup_path":"%(base_path)s/db_backup"
					}
				},
				"list-source":{
					"sequence":4,
					"execute":"system.command",
					"params":{
						"command":"ls -las %(base_path)s/source/%(tag)s"
					}
				},
				"symlink-current-folder":{
					"sequence":5,
					"execute":"system.symlink",
					"params":{
						"source":"%(base_path)s/current",
						"target":"%(base_path)s/source/%(tag)s"
					}
				}
			}
		},
		"rollback-app":{
			"description":"Rollback application",
			"input_params":{
				"tag":{
					"param":"tag",
					"prompt":"Rollback to which tag?"
				}
			},
			"actions":{
				"symlink-current-folder":{
					"sequence":1,
					"execute":"system.symlink",
					"params":{
						"source":"%(base_path)s/current",
						"target":"%(base_path)s/source/%(tag)s"
					}
				},
				"mysql-import":{
					"sequence":2,
					"execute":"mysql.restore_db",
					"confirm":"Restore a database backup?",
					"params":{
						"host":"$(project_database_host}s",
						"user":"$(project_database_user}s",
						"password":"$(project_database_password}s",
						"database":"$(project_database_name}s",
						"backup_path":"%(base_path)s/db_backup"
					}
				}
			}
		}
	}
}
```

#### Main settings

##### ./config/default.json
This is the base config. Everything will be extended from this config.

##### ./config/*environment*.json
Main config for development environments. 
This will overwrite the ./config/default.json

#### Project settings

##### ./config/*project*/default.json
Main Config for the development project. 
This will overwrite the ./config/default.json, and development.json

##### ./config/*project*/*environment*.json
Config for the development project. 
This will overwrite the ./config/default.json, default.json and development.json


> For more information about the configuration options please see the examples in ./config in the github repo.

To view the configuration from the command line you can run:

```
deploy-commander go show_config
```

- - -

## Templates

You can place your templates in a template folder in the root of your deployment app.

```
./template/[your/path/to/file.txt]
```

So when using the system.upload_template command you can enter the [your/path/to/file.txt] part as your source


# Source code setup

If you wan't to help developing... you can follow the next steps.

## Checkout

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


## Code

###/fabfile/

This folder contains the main init files that will setup the base of the system.
One of the main features is the settings.py that will load the configs
Utils are generic utils that can be used by all commands

###/command/

This folder containts the commands. These are mapped <filename>.<method> in the config.
