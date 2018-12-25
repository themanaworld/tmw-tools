#! /usr/bin/env python2.7
# -*- coding: utf8 -*-
#
# Copyright (C) 2018  TMW-2
# Author: Jesusalva

# Bad command:
# ls --recursive --hyperlink=always --format=single-column ../../server-data/npc/|grep txt

# Initialize stuff
import subprocess
import sys
erp=[]

# Clear previous NPC list
try:
    subprocess.call("rm npcs.txt", shell=True)
except:
    pass

# Determine correct path
PATH="../../server-data/npc/"
if len(sys.argv) == 2:
    PATH=sys.argv[1]

# Generate NPC list
subprocess.call("find "+PATH+" txt > npcs.txt", shell=True)
npcs=open("npcs.txt", "r")

# Begin
print("Checking license info for NPCs")
print("Source is at: "+PATH)

for mpa in npcs:
    mp=mpa.replace('\n','')
    # Skip mapflags
    if "mapflag" in mp:
      continue
    # Skip bad files
    if not '.txt' in mp:
      continue
    # Skip certain folders
    if  "/dev/" in mp or "/00000SAVE/" in mp or "/test/" in mp:
      continue

    a=open(mp, 'r')
    #print("Verify %s" % mp)
    ok=False
    for line in a:
        if 'tmw2 script' in line.lower() or 'tmw-2 script' in line.lower() or 'tmw 2 script' in line.lower() or 'tmw2/lof script' in line.lower() or 'This file is generated automatically' in line or 'author' in line.lower() or 'tmw2 function' in line.lower() or 'tmw-2 function' in line.lower() or 'tmw 2 function' in line.lower():
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

