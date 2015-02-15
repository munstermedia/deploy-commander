# Changelog
## 0.1.3
-	Added falcon api
- 	requirements.txt
- 	Vagrant file for devbox
-	some setup upgrades
-	Added env.home_path, to replace getcwd and added home_path task
- 	Working bibucket hook (still need to cleanup)
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