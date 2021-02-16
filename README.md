*Thanks to [jcsalterego](https://github.com/jcsalterego) for the idea and who's already implemented the same thing for [bash](https://github.com/jcsalterego/historian)*

### About this fork

- intended to search backups for histories and merge everything into 1 unique commands history for quick documentation
- multi line commands work
- use a new backup db when backing up to insure you don't pollute yours with broken commands
- remove the hist file you wanna restore to before writing to it to insure uniqueness
- maybe add some of these to your zshrc to further insure uniqueness (past 100k things can get quite slow so try to keep your total hist size below 50k)

```
#set history size
export HISTSIZE=100000	        # this must come after sourcing oh-my-zsh!!!
#save history after logout
export SAVEHIST=1000000			# this must come after sourcing oh-my-zsh!!!
#history file
export HISTFILE=$HOME/.zsh_history
#append into history file
setopt INC_APPEND_HISTORY
#save only one command if 2 common are same and consistent
setopt HIST_IGNORE_DUPS
#add timestamp for each entry
setopt EXTENDED_HISTORY   

setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicate entries first when trimming history.
setopt HIST_IGNORE_DUPS          # Don't record an entry that was just recorded again.
setopt HIST_IGNORE_ALL_DUPS      # Delete old recorded entry if new entry is a duplicate.
setopt HIST_FIND_NO_DUPS         # Do not display a line previously found.
setopt HIST_IGNORE_SPACE         # Don't record an entry starting with a space.
setopt HIST_SAVE_NO_DUPS         # Don't write duplicate entries in the history file.
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks before recording entry.
```

### Backup and Restore ZSH history

- Simple python script that can backup and restore your zsh history file to a sqlite db
- Dedups commands, and prepends any commands that were in the db but not in the history file
- Accepts a max length parameter
    - This does not truncate your existing file
    - If max length is <= than the size of your existing file, no new commands will be added to your history file
    - Otherwise, it will pull commands based on their timestamps until max length is reached

### Running it

```
usage: ./src/hist.py [-h] [-p PATH] [-d DBNAME] [-m MAXLINES] [-b] [-r]

Backup/Restore zsh history

optional arguments:
  -h, --help               show this help message and exit
  -p PATH,      --path     PATH  path to ZSH history    (default $HOME/.zsh_history)
  -d DBNAME,    --dbname   DBNAME SQLite db path        (default $HOME/.zsh_hist_backup.db)
  -m MAXLINES,  --maxlines MAXLINES max size of history file (default no limit)
  -b, --backup
  -r, --restore
```

Backup:

```
./src/hist.py -b
```

Restore:
```
./src/hist.py -r
```

### Restoring history every time you open a shell

- Just add the restore command to your ~/.zshrc file! (with the path from $HOME of course)

### Backing up your DB

- I've scheduled a launchd task on my mac to push my db to git every evening. [Here's](https://github.com/rchakra3/Utils/tree/master/scripts/zsh_backup) a link to the scripts


***Feedback and comments welcome!***
