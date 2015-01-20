# deploy-commander

> Continuous Integration Deployments to rule all your applications !

A tool for setting up a different environments most used for managing DTAP flows.
Deploy commander is build directly on python/fabric, but can be used for any project.

Main goal of this system is to configure your deployment, and not programm it.
There are other flavors for setting up your dtap... we're focussing on simplicity and transparancy. 

Next to that we want to create a centralized system to manage `different deployments` (applications) for `multiple apps` build in `different languages` on `different servers`.

We're building a lot if handy features for sysadmins and developers that will make your life easier. 


 

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


> For more information about the configuration options please see the examples in ./config in the example github repo.

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
