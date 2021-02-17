#!/usr/bin/env python3

import os
import sqlite3
import argparse
import re

home_folder = os.environ['HOME']
default_db_location = '/'.join([home_folder, '.zsh_hist_backup.db'])
default_hist_location = '/'.join([home_folder, '.zsh_history'])
default_table_name = 'CMD_HISTORY'


def init_db(db_name=default_db_location):
    """Create the db if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    table_check = "SELECT name FROM sqlite_master WHERE type=\'table\'"\
                  " AND name=\'" + default_table_name + "\'"
    cursor = conn.cursor()
    cursor.execute(table_check)
    table_exists = True if len(cursor.fetchall()) > 0 else False
    if (not table_exists):
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE " + default_table_name + """
             (command text PRIMARY_KEY UNIQUE, history_line text,
             timestamp UNSIGNED BIG INT)""")
        conn.commit()
        print("table created successfully")
    conn.close()


# BACKUP could pollute DB if bad hist file passed
# TODO - first backup db file to backups dir (run from wrapper script)
def backup(history_path=None, db_name='zsh_history.db'):
    """Backup zsh history to a sqlite db."""
    if (history_path is None):
        history_path = default_hist_location

    if not (os.path.exists(history_path) and os.path.isfile(history_path)):
        print("Invalid path to zsh history:" + history_path)
        exit(-1)
    cmd_dict = {}

    command_pattern = re.compile(': [0-9]{10,11}:[0-9]+;.+?(?=: [0-9]{10,11}:[0-9]+;|$)', re.MULTILINE|re.DOTALL)

    with open(history_path, "r", encoding="ISO-8859-1") as f:
        commands = command_pattern.findall(str(f.read()))
        print(len(commands))
        print(commands[0][0:200])

    for command_entry in commands:
        arr = command_entry.split(';')
        metadata = arr[0]
        # remove metadata section for the "command" string
        cmd = command_entry[(len(metadata)+1):] if len(arr) > 1 else ""
        # Handle empty lines
        if cmd != "":
            print("COMMAND: %s" % cmd)
            print("END============")
            try:
                timestamp = int(metadata.split(': ')[1].split(':')[0])
                # this keps a single occurence of the full multi-line command at the most recently noticed timestamp
                # TODO - check if command exists and if timestamp is newer - we want to record the most recent time we ran this command
                cmd_dict[cmd] = (command_entry, timestamp)
            except:
                # if a cmd can't be parsed ignore it
                pass
                
    rows = []
    for cmd, (line, timestamp) in cmd_dict.items():
        rows = rows + [(cmd, line, timestamp)]
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany(u"REPLACE INTO " + default_table_name +
                       u" ('command','history_line', 'timestamp')" +
                       u" VALUES(?,?,?)", rows)
    conn.commit()
    conn.close()


# RESTORE overwrites the file
# TODO - first copy file to another location (or do this from sh wrapper script)
# TODO - first run backup to temp database (or do this from sh wrapper script)
def restore(history_path=None, db_name=None, max_lines=None):
    """Append history from a sqlite db to the given history file."""
    """Creates the file if it doesn't exist"""
    if (history_path is None):
        history_path = default_hist_location
    if (db_name is None):
        db_name = default_db_location

    cmd_dict = {}
    prev_file_lines = []

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + default_table_name +
                   " ORDER BY timestamp desc")
    prev_history = cursor.fetchall()
    new_lines = -1
    if (max_lines is not None):
        max_lines=int(max_lines)
        new_lines = max_lines - len(prev_file_lines)
    file_lines = []
    for cmd, line, timestamp in prev_history:
        print("COMMAND ENTRY: %s" % line)
        print("END==============")
        if new_lines != -1 and len(file_lines) > new_lines:
            break
        if cmd not in cmd_dict:
            file_lines = file_lines + [line + '\n']

    file_lines = file_lines + prev_file_lines

    with open(history_path, 'w') as history_file:
        history_file.writelines(file_lines)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup/Restore zsh history')
    parser.add_argument('-p', '--path', dest='path',
                        help='path to ZSH history',
                        default=default_hist_location)
    parser.add_argument('-d', '--dbname', dest='dbname',
                        help='SQLite db name', default=default_db_location)
    parser.add_argument('-m', '--maxlines', dest='maxlines',
                        help='maximum size of history file', default=-1)
    parser.add_argument('-b', '--backup', dest='backup', action='store_true')
    parser.add_argument('-r', '--restore', dest='restore', action='store_true')
    args = parser.parse_args()
    init_db(args.dbname)
    if (args.backup):
        backup(args.path, args.dbname)
    elif (args.restore):
        restore(args.path, args.dbname, args.maxlines)
    else:
        parser.print_help()
