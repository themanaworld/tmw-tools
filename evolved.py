#! /usr/bin/env python3
# -*- coding: utf8 -*-
#
# Copyright (C) 2010-2011  Evol Online
# Copyright (C) 2018-2021  TMW-2
# Copyright (C) 2022       The Mana World
# Author: Andrei Karas (4144)
# Author: Jesusalva

import datetime
import sys, traceback

wikia=open("Items.md", "w")
wikib=open("Monsters.md", "w")
aegis=open("../world/map/db/const-aegis.txt", "w")

# the TYPEs we use to determine where to pack things
IT_HEALING=[]
IT_ETC=[]
IT_USABLE=[]
IT_AMMO=[]
IT_CARD=[]
IT_PETEGG=[]
IT_WEAPON={ 'HAND_2': [],           # TWO HAND (LR)
            'HAND_1':[]}            # WEAPONS (R)
IT_ARMOR={  'MISC': [],             # FOR FAILURE
            'EQP_ACC_L': [],        # ACCESSORY LEFT
            'EQP_ACC_R': [],        # ACCESSORT RIGHT
            'EQP_HEAD_MID': [],     # CHEST
            'EQP_SHOES': [],        # FEET
            'EQP_GARMENT': [],      # GLOVES
            'EQP_HEAD_LOW':[],      # PANTS
            '1024': [],             # NECKLACES (should be EQP_COSTUME_HEAD_TOP instead of number)
            '2048': [],             # RINGS (should be EQP_COSTUME_HEAD_MID instead of number)
            'EQP_MOUNT':[],         # MOUNTS (ie. EQP_SHADOW_SHOES)
            'EQP_HEAD_TOP':[],      # HATS/HELMETS
            'EQP_HAND_L': []}       # SHIELDS

Mobs1=[]
Mobs2=[]
Mobs3=[]
Mobs4=[]
Mobs5=[]
Mobs6=[]
MobsA=[]

SysDrops=[]


def printSeparator():
    print("--------------------------------------------------------------------------------")

def showHeader():
    print("TMW2 Wiki Generator")
    ##print "Evol client data validator."
    print("Run at: " + datetime.datetime.now().isoformat())
    print("Usage: ./wikigen.py [<path_to_serverdata> <path_to_clientdata>]")
    ##print "https://gitlab.com/evol/evol-tools/blob/master/testxml/testxml.py"
    printSeparator()

def showFooter():
    #pass
    #printSeparator()
    print("Done.")






class Mob:
  def __init__(self):
    # Basic
    self.id="0"
    self.aegis="UnknownMonster" # SpriteName is not used anywhere, we are using its ID
    self.name="Unknown Monster Name"
    self.view="1"
    self.chch=False
    self.boss=False
    self.race="0" # TODO Convert RC_*
    self.elem="0" # TODO Convert Ele_*
    self.mode="0" # TODO Convert MD_* and fields

    # General
    self.mobpt="0" # Mob Points “Level”
    self.hp="0"
    self.sp="0"
    self.xp="0"
    self.jp="0"

    # Defensive
    self.st=""
    self.df="0"
    self.mdf="0"

    # Stats
    self.str="0"
    self.agi="0"
    self.int="0"
    self.vit="0"
    self.dex="0"
    self.luk="0"

    # Offensive
    self.atk="[0, 0]"
    self.range="0"
    self.chase="1"
    self.move="0"
    self.delay="0"
    self.drops=[]

def MobAlloc(ab):
    try:
        maab=int(ab.mobpt)
    except:
        maab=9901

    aegis.write("%s %s\n" % (ab.aegis, ab.id))
    if maab <= 20:
        Mobs1.append(ab)
    elif maab <= 40:
        Mobs2.append(ab)
    elif maab <= 60:
        Mobs3.append(ab)
    elif maab <= 80:
        Mobs4.append(ab)
    elif maab <= 100:
        Mobs5.append(ab)
    elif maab <= 150:
        Mobs6.append(ab)
    elif maab != 9901:
        MobsA.append(ab)
    else:
        print("WARNING, Disregarding \"%s\" (ID: %s) as invalid mob" % (ab.name, ab.id))

def testMobs():
    print("\nGenerating Mob Wiki...")
    if len(sys.argv) >= 2:
        src=open(sys.argv[1]+"/db/pre-re/mob_db.conf", "r")
    else:
        src=open("../world/map/db/mob_db.conf", "r")

    start=False
    dropper=False
    x=Mob() # Only for pyflakes2

    for a in src:
        # Evol2-only scripts
        if "@EVOL2" in a:
            continue
        if "@TMWA" in a:
            a=a.replace("//", "").replace("@TMWA", "")
        # Initiate the script
        if a == "{\n":
            if start:
                MobAlloc(x)
            else:
                start=True
            x=Mob()

        if "	Id:" in a:
            x.id=stp(a)
        elif "	SpriteName:" in a:
            x.aegis=stp(a)
        elif "	Name:" in a:
            x.name=stp(a)
        elif "	Hp:" in a:
            x.hp=stp(a)
        elif "	Sp:" in a:
            x.sp=stp(a)
        elif "	Lv:" in a:
            x.mobpt=stp(a)
        elif "	Exp:" in a:
            x.xp=stp(a)
        elif "	JExp:" in a:
            x.jp=stp(a)
        elif "	Def:" in a:
            x.df=stp(a)
        elif "	Mdef:" in a:
            x.mdf=stp(a)
        elif "	Attack:" in a:
            x.atk=stp(a)
        elif "	AttackRange:" in a:
            x.range=stp(a)
        elif "	MoveSpeed:" in a:
            x.move=stp(a)
        elif "	ViewRange:" in a:
            x.view=stp(a)
        elif "	ChaseRange:" in a:
            x.chase=stp(a)
        elif "	AttackDelay:" in a:
            x.delay=stp(a)
        elif "	Boss: true" in a:
            x.boss=True
        elif "	Looter: true" in a:
            x.st+="Lot,"
        elif "	Assist: true" in a:
            x.st+="Ass,"
        elif "	Aggressive: true" in a:
            x.st+="Agr,"
        elif "	ChangeChase: true" in a:
            x.chch=True
        elif 'Drops: ' in a:
            dropper=True
        elif dropper and '}' in a:
            dropper=False
        elif dropper:
            x.drops.append(stp(a).split(": "))
        elif "\tStr: " in a:
            x.str=stp(a)
        elif "\tAgi: " in a:
            x.agi=stp(a)
        elif "\tVit: " in a:
            x.vit=stp(a)
        elif "\tDex: " in a:
            x.dex=stp(a)
        elif "\tInt: " in a:
            x.int=stp(a)
        elif "\tLuk: " in a:
            x.luk=stp(a)
    # Write last entry
    MobAlloc(x)

    src.close()

def stp(x):
    return x.replace('\n', '').replace('|', '').replace('(int, defaults to ', '').replace(')', '').replace('basic experience', '').replace('"','').replace("    ","").replace("\t","").replace('(string', '').replace('SpriteName: ','').replace('Name: ','').replace('AttackDelay: ', '').replace('MoveSpeed: ', '').replace('AttackRange: ', '').replace('ViewRange: ','').replace('ChaseRange: ','').replace('Attack: ','').replace('ViewRange: ','').replace('Hp: ','').replace('Sp: ','').replace('Id: ','').replace('Lv: ','').replace('view range','').replace('attack range','').replace('move speed','').replace('health','').replace('(int','').replace('attack delay','atk.').replace("Str:", "").replace("Agi:", "").replace("Vit:", "").replace("Int:", "").replace("Dex:", "").replace("Luk:", "").replace("Mdef:","").replace("Def:","")




def mb_rdmisc(mb):
    buff=""
    if "agr" in mb.st.lower():
        buff+="View Range: %s\n" % (mb.view)
    buff+="Attack Range: %s\n" % (mb.range)
    buff+="Move speed: %s ms\n" % (mb.move)
    return buff

def mb_rdrw(mb):
    buff=""
    buff+="MobPoints: %s\n" % (mb.mobpt)
    buff+="%s\n" % (mb.xp)
    buff+="%s\n" % (mb.jp)
    return buff

def mb_rddrop(mb):
    buff=""
    # sorted
    try:
        for ax in sorted(mb.drops, key=lambda xcv: float(xcv[1]), reverse=True):
            # Ignore disabled drops
            if ax[0].startswith("//"):
                continue

            # Write drop
            try:
                buff+=ax[0]+': ' + str(int(ax[1])/100.0) + ' %\n'
            except IndexError:
                print("Fatal: invalid %s mob with %s drops" % (mb.name, str(ax)))
                exit(1)
            except:
                print("[Warning] %s incorrect drop: %s" % (mb.name, str(ax)))
                buff+=ax[0]+': ' + ax[1] + ' ppm\n'

            # Save to SysDrops
            SysDrops.append([ax[0], ax[1], mb.name])
    except:
        traceback.print_exc()
        print("Offender: %s" % mb.name)

    return buff


class It:
  def __init__(self):
    # Basic
    self.id="0"
    self.aegis="UnknownItem"
    self.name="Unknown Item Name"
    self.price="0" # Sell price, of course
    self.weight="0"
    self.type="IT_ETC" # default type
    self.loc=""

    # Offensive/Defensive
    self.atk="0"
    self.matk="0"
    self.range="0"
    self.defs="0"

    # Restrictions (EquipLv)
    self.lvl="0"
    self.drop=True
    self.trade=True
    self.sell=True
    self.store=True

    # Special settings
    self.rare=False         # DropAnnounce
    self.script=False

    # Visual
    self.sl="0" # Slots
    self.ac=False # Allow Cards

    # Script settings
    self.minheal="0"
    self.maxheal="0"
    self.delheal="0"
    self.typheal="0"
    self.rarheal="0"

def ItAlloc(it):
    if (it.sl == "0" and it.ac) or (it.sl in ["1","2","3","4"] and not it.ac):
        print("WARNING, item id "+it.id+" invalid dye/card setting!")
    if (len(it.sl) > 1):
        print("WARNING, item id "+it.id+" bad slots length: %d (%s)" % (len(it.sl), it.sl))
    #if it.ac:
    #    wikic.write(it.id + ": " + it.name + "\n")

    a=it.type
    if "IT_HEALING" in a:
        IT_HEALING.append(it)
    elif "IT_ETC" in a:
        IT_ETC.append(it)
    elif "IT_USABLE" in a:
        IT_USABLE.append(it)
    elif "IT_AMMO" in a:
        IT_AMMO.append(it)
    elif "IT_CARD" in a:
        IT_CARD.append(it)
    elif "IT_PETEGG" in a:
        IT_PETEGG.append(it)

    elif "IT_WEAPON" in a:
        if "HAND_L" in it.loc or "EQP_ARMS" in it.loc:
            IT_WEAPON["HAND_2"].append(it)
        elif "HAND_R" in it.loc:
            IT_WEAPON["HAND_1"].append(it)
        else:
            raise Exception("Invalid location for weapon: %s" % it.loc)

    elif "IT_ARMOR" in a:
        if 'EQP_ACC_L' in it.loc:
            IT_ARMOR['EQP_ACC_L'].append(it)
        elif 'EQP_ACC_R' in it.loc:
            IT_ARMOR['EQP_ACC_R'].append(it)
        elif 'EQP_HEAD_MID' in it.loc:
            IT_ARMOR['EQP_HEAD_MID'].append(it)
        elif 'EQP_SHOES' in it.loc:
            IT_ARMOR['EQP_SHOES'].append(it)
        elif 'EQP_GARMENT' in it.loc:
            IT_ARMOR['EQP_GARMENT'].append(it)
        elif 'EQP_HEAD_LOW' in it.loc:
            IT_ARMOR['EQP_HEAD_LOW'].append(it)
        elif 'EQP_HEAD_TOP' in it.loc:
            IT_ARMOR['EQP_HEAD_TOP'].append(it)
        elif 'EQP_HAND_L' in it.loc:
            IT_ARMOR['EQP_HAND_L'].append(it)
        elif '1024' in it.loc:
            IT_ARMOR['1024'].append(it)
        elif '2048' in it.loc:
            IT_ARMOR['2048'].append(it)
        elif 'EQP_SHADOW_SHOES' in it.loc:
            IT_ARMOR['EQP_MOUNT'].append(it)
        elif 'EQP_ARMOR' in it.loc:
            IT_ARMOR['EQP_ACC_R'].append(it) # Not really
        else:
            raise Exception("Invalid Loc for ID %s: %s" % (it.id, it.loc))

    if "i" in it.id:
        print("Invalid item: %s" % it.id)
        return

    ## Save the Aegis ID
    aegis.write("%s %s\n" % (it.aegis, it.id))

def newItemDB():
    print("\nGenerating Item Wiki...")
    if len(sys.argv) >= 2:
        src=open(sys.argv[1]+"/db/pre-re/item_db.conf", "r")
    else:
        src=open("../world/map/db/item_db.conf", "r")

    x=It()
    for a in src:
        # Evol2-only scripts
        if "@EVOL2" in a:
            continue
        if "@TMWA" in a:
            a=a.replace("//", "").replace("@TMWA", "")
        # Initiate the script
        if a == "{\n":
            ItAlloc(x)
            x=It()

        # sti() block
        if "	Id:" in a:
            x.id=sti(a)
        elif "	AegisName:" in a:
            x.aegis=sti(a)
        elif "	Name:" in a:
            x.name=stin(a)
        elif "	Sell:" in a:
            x.price=sti(a)
        elif "	Weight:" in a:
            x.weight=sti(a)
        elif "	Type:" in a:
            x.type=sti(a)
        elif "	Loc:" in a:
            x.loc=sti(a)
        elif "	Atk:" in a:
            x.atk=sti(a)
        elif "	Matk:" in a:
            x.matk=sti(a)
        elif "	Range:" in a:
            x.range=sti(a)
        elif "	Def:" in a:
            x.defs=sti(a)
        elif "	EquipLv:" in a:
            x.lvl=sti(a)
        elif "	Slots:" in a:
            x.sl=sti(a)
        elif "	AllowCards:" in a:
            x.ac=True
        # Write booleans
        elif "DropAnnounce: true" in a:
            x.rare=True
        elif "nodrop: true" in a:
            x.drop=False
        elif "notrade: true" in a:
            x.trade=False
        elif "noselltonpc: true" in a:
            x.sell=False
        elif "nostorage: true" in a:
            x.store=False
        elif "Script" in a:
            x.script=True
        # For healing items
        elif "@min " in a:
            x.minheal=sti(a)
        elif "@max " in a:
            x.maxheal=sti(a)
        elif "@delay" in a:
            x.delheal=sti(a)
        elif "@type" in a:
            x.typheal=sti(a)
            try:
                x.minheal=str(int(x.rarheal) * (int(x.typheal)*1 + 1)) + " %"
                x.maxheal=str(int(x.rarheal) * (int(x.typheal)*2 + 1)) + " %"
                if (x.delheal == "0"):
                    x.delheal=int(x.typheal)*2 + 1
            except:
                x.delheal="ERROR"
                pass
        elif "@rarity" in a:
            x.rarheal=sti(a)
            x.minheal=str(int(x.rarheal) * (int(x.typheal)*1 + 1)) + " %"
            x.maxheal=str(int(x.rarheal) * (int(x.typheal)*2 + 1)) + " %"

    # Write last entry
    ItAlloc(x)

    src.close()

def sti(x):
    return x.replace('\n', '').replace('|', '').replace(')', '').replace('Id: ', '').replace('"','').replace("    ","").replace("\t","").replace('AegisName: ', '').replace('Name: ','').replace('Sell: ', '').replace('Weight: ', '').replace('Type: ', '').replace('Loc: ', '').replace('Atk: ', '').replace('Matk: ', '').replace('Range: ', '').replace('Def: ', '').replace('EquipLv: ', '').replace('Slots: ','').replace(" ", "").replace('@min=','').replace('@max=','').replace('@delay=','').replace('@type=','').replace('@rarity=','').replace(';','')

def stin(x):
    return x.replace('\n', '').replace('|', '').replace(')', '').replace('Id: ', '').replace('"','').replace("    ","").replace("\t","").replace('Name: ','').replace(';','')















def save_mobs():
    global Mobs1, Mobs2, Mobs3, Mobs4, Mobs5, Mobs6, MobsA
    return
    ## Mobs
    with open ("../world/map/db/mob_db_0_19.txt", "w") as f:
        f.write("//THIS FILE IS GENERATED AUTOMATICALLY\n//DO NOT EDIT IT DIRECTLY\n//Edit mob_db.conf instead!\n")
        f.write("//ID,   Name,                   Jname,                  LV,     HP,     SP,     EXP,    JEXP,   Range1, ATK1,   ATK2,   DEF,    MDEF,   STR,    AGI,    VIT,    INT,    DEX,    LUK,    Range2, Range3, Scale,  Race,   Element,Mode,   Speed,  Adelay, Amotion,Dmotion,Drop1id,Drop1per,Drop2id,Drop2%, Drop3id,Drop3%, Drop4id,Drop4%, Drop5id,Drop5%, Drop6id,Drop6%, Drop7id,Drop7%, Drop8id,Drop8%, Item1,  Item2,  MEXP,   ExpPer, MVP1id, MVP1per,MVP2id, MVP2per,MVP3id, MVP3per,mutationcount,mutationstrength\n")
        for m in Mobs1:
            #Adelay, Amotion,Dmotion,Drop1id,Drop1per,Drop2id,Drop2%, Drop3id,Drop3%, 
            #Drop4id,Drop4%, Drop5id,Drop5%, Drop6id,Drop6%, Drop7id,Drop7%, Drop8id,Drop8%, 
            #Item1,  Item2,  MEXP,   ExpPer, MVP1id, MVP1per,MVP2id, MVP2per,MVP3id, 
            #MVP3per,mutationcount,mutationstrength
            f.write("""%s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s, %s, %s, 1, %s, %s, %s, %s,  
\n""" % (m.id, m.aegis, m.aegis, m.mobpt, m.hp, m.sp,
m.xp, m.jp, m.range, m.atk.replace('[','').split(",")[0], m.atk.replace(']','').split(",")[1], m.df, m.mdf, m.str, m.agi, m.vit,
m.int, m.dex, m.luk, m.view, m.chase, "Race", "Element", "Mode", self.move,
        ))
            continue

    return












showHeader()

testMobs()
newItemDB()

save_mobs()

wikia.close()
wikib.close()
aegis.close()
#print(str(SysDrops))

showFooter()
exit(0)
