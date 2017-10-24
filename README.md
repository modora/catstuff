[TOC]

# Usage

	`catstuff <command> [options] <args>`
 

## Import
Imports files into the archive

	`catstuff import [options] <path>`

 Argument | Description
 ---------|------------
 path | Either a directory or a file. If the path is a file, then only the single file will be run through the play. If the path is a directory, then all files within the directory are added to the play queue.


Option | Default | Description 
--------|:--------:|------------
-c, --config | Default config file to load
 -R, --recursive | False | Applies only when the path is a directory. Recursively queue all files found
 --include [paths] | * | Files to import represented as a comma separated list (supports file globbing)
 --exclude [paths] | none | Exclude files to import represented as a comma separated list (supports file globbing)
 -g, --group [group] | none | Explicitly identify the group level the imported files belong to

### Example
To import a single file named 'foo.ext' in the current directory,  simply run 
	
	`catstuff import foo.ext `

If the 

## Search
Searches the main database for entries matching some query

	`catstuff search [options] <query>`

## Config
Manage the user config file
	
	`catstuff config [options] <action>

Action | Description
--------|------------
check | Verifies that the config file is syntactically correct
dry-run | Verifies that all tasks listed in the config have all the necessary dependencies 
edit | Opens the config in the default editor

## Version
Gets the version number of the catstuff

	`catstuff version`