# Changelog

## 0.0.22
-	When calling dicttoconfig (doct to json config) it will order by sequence

## 0.0.23
-	Fixed bug selecting project and environment
-	Added error when config is not set
-	Added nice error when config cannot be read
-	Deploy by running a single command, params project and environment can be set by the go command

## 0.0.24
- 	Added show_config option

## 0.0.25
- 	Added mysql.cleanup_db_backups .. that will remove old backup files from remote
- 	Changed backup_db so it's possible to modify the backup file
-	Changed backup_db that it will create a compressed backup
- 	Added download from tar.gz to local option (download_tar_to_local_file)
-	Changed restore_db that is will restore from a compressed backup