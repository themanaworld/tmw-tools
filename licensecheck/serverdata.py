#! /usr/bin/env python2.7
# -*- coding: utf8 -*-
#
# Copyright (C) 2018  TMW-2
# Author: Jesusalva

import os

sv="../../server-data/npc/"
erp=[]
err=0

print("Checking license info for second level NPCs")

for mp in os.listdir(sv):

    # we actually should read scripts and imports, but this script is designed to be dumb
    if "." in mp or mp == "dev":
        continue

    for script in os.listdir(sv+mp):
        if (not ".txt" in script) and (not ".conf" in script):
            continue
        if ("~" in script) or ("#" in script) or ("mapflags.txt" in script):
            continue

        a=open(sv+mp+'/'+script, 'r')
        ok=False
        for line in a:
            if 'tmw2 script' in line.lower() or 'tmw-2 script' in line.lower() or 'tmw 2 script' in line.lower() or 'This file is generated automatically' in line:
                ok=True
                break

        a.close()
        if not ok:
            erp.append(mp+'/'+script)
            err+=1

if len(erp) > 0:
    print("-----------------------------------------------------------------------")

for i in sorted(erp):
    print(i)

print("-----------------------------------------------------------------------")
print("Serverdata license check result")
print("Errors: %d" % (err))
