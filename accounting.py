#!/usr/bin/env python

import sys,os
import re
import csv
import posixpath

def main():
    item_names = {}
    with open('./world/map/conf/tmwa-map.conf') as item_dbs:
        for item_db_line in item_dbs:
            if item_db_line.startswith('item_db:'):
                with open(posixpath.join('./world/map/', item_db_line.split(':')[1].strip())) as item_db:
                    for line in item_db:
                        if not line.strip():
                            continue
                        if line.startswith('//'):
                            continue
                        k, v, _ = line.split(',', 2)
                        item_names[int(k)] = v.strip()

#id name    password    last_log    gemder  login_count state   email   error_message   TimeT   last_ip    memo ban_time_until
#    with open('login/save/account.txt') as accounts:
#        for account in csv.reader(accounts, delimiter='	'):
#            if (len(account) == 14):
#                print account
#                sys.exit(2)
    item_counts = {}
    with open('world/save/athena.txt') as characters:
        for character in csv.reader(characters, delimiter='	'):
            if (len(character) > 2):
                for item in character[15].split(' '):
                    item_info = item.split(',')
                    if (len(item_info) > 1):
                        if int(item_info[1]) in item_counts:
                            item_counts[int(item_info[1])] = int(item_info[2].strip()) + int(item_counts[int(item_info[1])])
                        else:
                            item_counts[int(item_info[1])] = int(item_info[2].strip())
    with open('world/save/storage.txt') as storage:
        for items in csv.reader(storage, delimiter='	'):
            for item in items[1].split(' '):
                item_info = item.split(',')
                if (len(item_info) > 1):
                    if int(item_info[1]) in item_counts:
                        item_counts[int(item_info[1])] = int(item_info[2].strip()) + int(item_counts[int(item_info[1])])
                    else:
                        item_counts[int(item_info[1])] = int(item_info[2].strip())
    for item_id in item_names:
        if item_id in item_counts:
            print "%s,%s" % (item_names[item_id], item_counts[item_id])
        else:
            print "%s,0" % (item_names[item_id])

main()
