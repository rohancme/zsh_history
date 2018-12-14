#!/usr/local/bin/python3

import os
import sqlite3
import argparse

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


def backup(history_path=None, db_name='zsh_history.db'):
    """Backup zsh history to a sqlite db."""
    if (history_path is None):
        history_path = default_hist_location

    if not (os.path.exists(history_path) and os.path.isfile(history_path)):
        print("Invalid path to zsh history:" + history_path)
        exit(-1)
    cmd_dict = {}
    with open(history_path, "r", encoding="ISO-8859-1") as f:
        for line in f.readlines():
            line = line.rstrip('\n\t')
            arr = line.split(';')
            metadata = arr[0]
            cmd = arr[1] if len(arr) > 1 else ""
            # Handle empty lines
            if cmd != "":
                try:
                    timestamp = int(metadata.split(': ')[1].split(':')[0])
                    cmd_dict[cmd] = (line, timestamp)
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


def restore(history_path=None, db_name=None, max_lines=None):
    """Append history from a sqlite db to the given history file."""
    """Creates the file if it doesn't exist"""
    if (history_path is None):
        history_path = default_hist_location
    if (db_name is None):
        db_name = default_db_location

    cmd_dict = {}
    prev_file_lines = []
    if os.path.isfile(history_path):
        with open(history_path) as history_file:
            for line in history_file:
                line = line.rstrip('\n\t')
                arr = line.split(';')
                cmd = arr[1] if len(arr) > 1 else ""
                cmd_dict[cmd] = line
                prev_file_lines += [line + '\n']

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + default_table_name +
                   " ORDER BY timestamp desc")
    prev_history = cursor.fetchall()
    new_lines = -1
    if (max_lines is not None):
        new_lines = max_lines - len(prev_file_lines)
    file_lines = []
    for cmd, line, timestamp in prev_history:
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