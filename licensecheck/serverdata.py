#! /usr/bin/env python2.7
# -*- coding: utf8 -*-
#
# Copyright (C) 2018  TMW-2
# Author: Jesusalva

# Bad command:
# ls --recursive --hyperlink=always --format=single-column ../../server-data/npc/|grep txt

# Initialize stuff
import subprocess
erp=[]

# Clear previous NPC list
try:
    subprocess.call("rm npcs.txt", shell=True)
except:
    pass

# Generate NPC list
subprocess.call("find ../../server-data/npc/ txt > npcs.txt", shell=True)
npcs=open("npcs.txt", "r")

# Begin
print("Checking license info for NPCs (this excludes _npcs and mapflags)")

for mpa in npcs:
    mp=mpa.replace('\n','')
    # Skip files prefixed with _ or called mapflags
    if "mapflag" in mp:
      continue
    if "_import" in mp:
      continue
    if "_warps" in mp:
      continue
    if "_mobs" in mp:
      continue
    # Skip bad files
    if not '.txt' in mp:
      continue
    # Skip certain folders
    if  "/dev/" in mp or "/00000SAVE/" in mp or "/test/" in mp:
      continue

    a=open(mp, 'r')
    print("Verify %s" % mp)
    ok=False
    for line in a:
        if 'tmw2 script' in line.lower() or 'tmw-2 script' in line.lower() or 'tmw 2 script' in line.lower() or 'tmw2/lof script' in line.lower() or 'This file is generated automatically' in line:
            ok=True
            break

    a.close()
    if not ok:
        erp.append(mp)

npcs.close()
if len(erp) > 0:
    print("-----------------------------------------------------------------------")

for i in sorted(erp):
    print(i)

print("-----------------------------------------------------------------------")
print("Serverdata license check result")
print("Errors: %d" % (len(erp)))
#if err > 0:
#    os.exit(1)

