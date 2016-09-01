# Changelog

## 0.1.23
- 	Moved slack hook into "hook"  config var
- 	Added extra hook config for triggering tasks

## 0.1.22
- 	Small encryption and decryption fix

## 0.1.21
- 	Catch exception for invalid config on encryption and decryption

## 0.1.20
- 	Catch exception for slack hook when request fails

## 0.1.19
- 	slack hook bigfix

## 0.1.18
- 	Add slack hook

## 0.1.17
- 	Remove insecure config request from api

## 0.1.16
- 	Add path to encrypt or decrypt functionality

## 0.1.15
- 	Fixed issue with executing tasks from the bibucket hook. (if process was running it started a new one next to it, this is fixed by adding a lockfile)
- 	Removed old bitbucket hook request.

## 0.1.14
- 	Fixed bug in command upload_to_remote

## 0.1.13
- 	Add new system command: upload_to_remote
- 	Add new system command: multi_local_command

## 0.1.12
- 	Add more user data to outgoing deployment email.
- 	Add secure option to system and multi system commands.

## 0.1.11
- 	Add new command multi_command, which can be used to run multiple commands based on a json list
- 	Add deprecated notifications for old commands
- 	Only encrypt/decrypt config files ending with 'crypt.json'

## 0.1.10
-	Add new hook /api/v1/bitbucket/webhook because /api/v1/bitbucket/pullrequestposthook is deprecated

## 0.1.9
-	Update fabric
-	Print error fix
 
## 0.1.8
-	Set default port of webserver to 8687
-	Added new task, stopserver
-	Made startserver a background task
-	Cleanup some documentation

## 0.1.7
-	Fixed path of log folder to cleanup html and text logs

## 0.1.6
-	Modified runserver so the webserver can be configured
- 	Added documentation for the webserver

## 0.1.5
-	Fixed bug in post hook
-	Check if deploy commander file is available
-	New hook log in mail and text, and optimalisation of this logging
- 	Changed routing in post hook with right versioning

## 0.1.4
-	runserver added virtualenv path
-	Inline documentation
- 	Initial unit tests

## 0.1.3
-	Added falcon api
- 	requirements.txt
- 	Vagrant file for devbox
-	some setup upgrades
-	Added env.home_path, to replace getcwd and added home_path task
- 	Working bitbucket hook (still need to cleanup)
- 	Added runserver task
-	Added mail of console
-	Moved files to other location
-	Updated documentation

## 0.1.2
-	Removed git branch and tag listing, with prompt in git.deploy.
-	Small typo change in input_params prompt
-	Added docu for input_params
-	Added system.cleanup_old_files
-	Removed README docu

## 0.1.1
-	Renamed/refactored commands in config to tasks
- 	Renamed/refactored the execute to command in actions
- 	Add show_tasks functionality
-	Refactored config strategy
-   More documentation

## 0.1.0
-	Prepping for a final release
-	Format params of git command after branch input is requested
-	Refactored git functionality, new params, added required checks
- 	Added global params util, to reuse general params
-	Removed apt-get, this is something that should be solved with puppet or chef
-	Updated README

## 0.0.27
- 	Added overwrite of config loading with config_strategy
-	Changed config of root from '.config' to 'config.json'
- 	Mysql import, if file does not exist... show a warning, but continue....
-	Removed output setting in config
-	Removed output setting on ensure_path

## 0.0.26
-	Added validation for repo_url and repo path to git.install_repo
- 	Added ensure path command
-	Changed git.deploy_tag to git.deploy
- 	Changed params for git.deploy tag to branch and target_path
-	Refactored some code for git.deploy (made it nicer)
-	system.upload_template use_sudo defaults to false
- 	Added sudo option to system.command
-	git.install_repo forwarded to git.clone

## 0.0.25
- 	Added mysql.cleanup_db_backups .. that will remove old backup files from remote
- 	Changed backup_db so it's possible to modify the backup file
-	Changed backup_db that it will create a compressed backup
- 	Added download from tar.gz to local option (download_tar_to_local_file)
-	Changed restore_db that is will restore from a compressed backup

## 0.0.24
- 	Added show_config option

## 0.0.23
-	Fixed bug selecting project and environment
-	Added error when config is not set
-	Added nice error when config cannot be read
-	Deploy by running a single command, params project and environment can be set by the go command

## 0.0.22
-	When calling dicttoconfig (doct to json config) it will order by sequence


## < 0.0.22
-	Initial versions created!