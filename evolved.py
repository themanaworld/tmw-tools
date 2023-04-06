#! /usr/bin/env python3
# -*- coding: utf8 -*-
#
# Copyright (C) 2010-2011  Evol Online
# Copyright (C) 2018-2021  TMW-2
# Copyright (C) 2022       The Mana World
# Author: Andrei Karas (4144)
# Author: Jesusalva

import datetime
import sys, traceback, re

aegis=open("../world/map/db/const-aegis.txt", "w")

description_m="//ID,   Name,                   Jname,                  LV,     HP,     SP,     EXP,    JEXP,   Range1, ATK1,   ATK2,   DEF,    MDEF,   CRITDEF,STR,    AGI,    VIT,    INT,    DEX,    LUK,    Range2, Range3, Scale,  Race,   Element,Mode,   Speed,  Adelay, Amotion,Dmotion,Drop0id,Drop0%, Drop1id,Drop1%, Drop2id,Drop2%, Drop3id,Drop3%, Drop4id,Drop4%, Drop5id,Drop5%, Drop6id,Drop6%, Drop7id,Drop7%, Drop8id,Drop8%, Drop9id,Drop9%, Item1,  Item2,  MEXP,   ExpPer, MVP1id, MVP1per,MVP2id, MVP2per,MVP3id, MVP3per,mutationcount,mutationstrength"
description_i="//ID,   Name,                   Type,   Price,      Sell,       Weight,     ATK,    DEF,    Range,  Mbonus, Slot,   Gender, Loc,        wLV,    eLV,    View,   Mode,   {UseScript},                                                            {EquipScript}"

# the TYPEs we use to determine where to pack things
IT_HEALING=[]
IT_ETC=[]
IT_USABLE=[]
IT_AMMO=[]
IT_CARD=[]
IT_PETEGG=[]
IT_WEAPON={ 'HAND_2': [],           # TWO HAND (LR)
            'HAND_1': []}           # WEAPONS (R)
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

AllItems={}

#############################################################################################
def printSeparator():
    print("--------------------------------------------------------------------------------")

#############################################################################################
def showHeader():
    print("Evol2->TMWA DB Generator")
    print("Run at: " + datetime.datetime.now().isoformat())
    #print("Usage: ./evolved.py [<path_to_serverdata> <path_to_clientdata>]")
    printSeparator()

#############################################################################################
def showFooter():
    #pass
    #printSeparator()
    print("Done.")

#############################################################################################
def write_to_file(array, outfile, mode, description_count): # mode: 0 = item, 1 = mob

    count=0
    with open (outfile, "w") as f:
        if mode:
            write_mob_header(f)
        else:
            write_item_header(f)
        for i in sorted(array, key=lambda xcv: int(xcv.id)):
            if mode:
                write_mob(i, f)
            else:
                write_item(i, f)

            count+=1
            if count >= description_count:
                count=0
                if mode:
                    f.write(description_m + "\n")
                else:
                    f.write(description_i + "\n")

    return




#    ___________
#   /           \
#  /    Items    \
# /_______________\
# \_______________/

"""
struct Item
{
    Spanned<ItemNameId> id;
    Spanned<ItemName> name;
    Spanned<ItemType> type;
    Spanned<int> buy_price;
    Spanned<int> sell_price;
    Spanned<int> weight;
    Spanned<int> atk;
    Spanned<int> def;
    Spanned<int> range;
    Spanned<int> magic_bonus;
    Spanned<RString> slot_unused;
    Spanned<SEX> gender;
    Spanned<EPOS> loc;
    Spanned<int> wlv;
    Spanned<int> elv;
    Spanned<ItemLook> view;
    ast::script::ScriptBody use_script;
    ast::script::ScriptBody equip_script;
};
enum class SEX : uint8_t
{
    FEMALE = 0,
    MALE = 1,
    // For items. This is also used as error, sometime.
    // TODO switch to Option<SEX> where appropriate.
    UNSPECIFIED = 2,
    NEUTRAL = 3,
    __OTHER = 4, // used in ManaPlus only
};
"""
class It:
  def __init__(self):
    # Basic
    self.id="0"
    self.aegis="UnknownItem"
    self.name="Unknown Item Name"
    self.type="IT_ETC" # default type
    self.buy="0"
    self.sell="0"
    self.weight="0"
    self.atk="0"
    self.matk="0"
    self.df="0"
    self.range="0"
    self.sl="0" # Slots (unused always 0)
    self.gender="2" # default = UNSPECIFIED = 2
    self.loc=""
    self.wlv="0" # 1 for weapons, 0 for all others including ammo
    self.elv="0" # equip lvl
    self.md=0
    self.subtype=""
    self.disabled=False
    # Script settings
    self.usescript=[]
    self.eqscript=[]
    #self.usescript=""
    #self.eqscript=""

    # Special settings
    self.rare=False         # DropAnnounce

    # Visual
    self.ac=False # Allow Cards

    self.gmlvlonly=False

#############################################################################################
def ItAlloc(it):
    if (it.aegis == "UnknownItem"):
        return
    if (it.sl == "0" and it.ac) or (it.sl in ["1","2","3","4"] and not it.ac):
        print("WARNING, item id "+it.id+" invalid dye/card setting!")
    if (len(it.sl) > 1):
        print("WARNING, item id "+it.id+" bad slots length: %d (%s)" % (len(it.sl), it.sl))

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
    if (it.aegis not in []):
        aegis.write("%s %s\n" % (it.aegis, it.id))
    else:
        print("%s: Aegis reused as quest var (please purge)" % it.aegis)
    AllItems[it.aegis]=str(it.id)

#############################################################################################
"""
enum class ItemMode : uint8_t
{
    NONE           = 0,
    NO_DROP        = 1,
    NO_TRADE       = 2,
    NO_SELL_TO_NPC = 4,
    NO_STORAGE     = 8,
};
"""
def newItemDB():
    IT_NO_DROP =         1
    IT_NO_TRADE =        2
    IT_NO_SELL_TO_NPC =  4
    IT_NO_STORAGE =      8
    IT_DROPANNOUNCE =    16

    print("\nGenerating Item Wiki...")
    if len(sys.argv) >= 2:
        src=open(sys.argv[1]+"/db/pre-re/item_db.conf", "r")
    else:
        src=open("../world/map/db/item_db.conf", "r")

    usescripting=False
    eqscripting=False
    useableitem=False
    nouse=False

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
        if "\tId:" in a:
            x.id=sti(a)
        elif "\tAegisName:" in a:
            x.aegis=sti(a)
        elif "\tName:" in a:
            x.name=stin(a)
        elif "\tBuy:" in a:
            x.buy=sti(a)
        elif "\tSell:" in a:
            x.sell=sti(a)
        elif "\tWeight:" in a:
            x.weight=sti(a)
        elif "\tType:" in a:
            x.type=sti(a)
            if x.type == "IT_USABLE":
                useableitem=True
        elif "\tLoc:" in a:
            x.loc=sti(a)
        elif "\tAtk:" in a:
            x.atk=sti(a)
        elif "\tMatk:" in a: # description says ignored in pre-re
            x.matk=sti(a)
        elif "\tRange:" in a:
            x.range=sti(a)
        elif "\tDef:" in a:
            x.df=sti(a)
        elif "\tEquipLv:" in a:
            x.elv=sti(a)
        #elif "\tSlots:" in a: # allways 0 in tmwa atm
            #x.sl=sti(a)
        elif "\tGender:" in a: # allways 2 in tmwa atm
            x.gender=sti(a)
        elif "\tSubtype:" in a:
            x.subtype=sti(a)
        elif "\tDisabled: true" in a:
            x.disabled=True
        elif "\tAllowCards:" in a:
            x.ac=True
        # Write booleans
        elif "\tDropAnnounce: true" in a:
            x.rare=True
            #x.md = x.md | IT_DROPANNOUNCE
        elif "\tnodrop: true" in a:
            #x.drop=False
            x.md = x.md | IT_NO_DROP
        elif "\tnotrade: true" in a:
            #x.trade=False
            x.md = x.md | IT_NO_TRADE
        elif "\tnoselltonpc: true" in a:
            #x.sell=False
            x.md = x.md | IT_NO_SELL_TO_NPC
        elif "\tnostorage: true" in a:
            #x.store=False
            x.md = x.md | IT_NO_STORAGE
        elif "\tNouse:" in a:
            nouse=True
        elif "\toverride:" in a:
            if nouse:
                if sti(a) != "0":
                    x.gmlvlonly=True
        elif "\t}" in a:
            if nouse:
                nouse=False
        # FIXME: Different kind of scripts D:
        elif "\tOnEquipScript:" in a:
            eqscripting=True
        elif "\tScript:" in a:
            if useableitem:
                usescripting=True
            else:
                eqscripting=True
        # FIXME: Nesting D:
        elif (eqscripting or usescripting) and '\t\">' in a:
            eqscripting=False
            usescripting=False
            useableitem=False
        elif eqscripting:
            if re.search(r"^\t+//",a):
                pass
            #elif "bonus bMatkRate" in a: # its not that simple since it can be a bonus in tmwa as well so i must use the Matk: field
                #x.matk=sti(a)
            else:
                x.eqscript.append(stis(a))
            #print("%s" % a)
        elif usescripting:
            if re.search(r"^\t+//",a):
                pass
            else:
                x.usescript.append(stis(a))

    # Write last entry
    ItAlloc(x)

    src.close()

#############################################################################################
def sti(x):
    return x.replace('\n', '').replace('|', '').replace(')', '').replace('Id: ', '').replace('"','').replace(';','').replace("    ","").replace("\t","").replace('AegisName: ', '').replace('Name: ','').replace('Buy: ', '').replace('Sell: ', '').replace('Weight: ', '').replace('Type: ', '').replace('Loc: ', '').replace('Atk: ', '').replace('Matk: ', '').replace('Range: ', '').replace('Def: ', '').replace('EquipLv: ', '').replace('Subtype: ', '').replace('Slots: ', '').replace('Gender: ', '').replace('nodrop: ', '').replace('notrade: ', '').replace('noselltonpc: ', '').replace('nostorage: ', '').replace('override: ', '').replace(" ", "").strip()

#############################################################################################
def stis(x):
    x=re.sub(r'; *//.*$',';',x)
    # handle those with @EVOL2 and @TMWA tags rather?
    x=re.sub(r', EQI_.*;',';',x)
    x=re.sub(r'readparam\(b(.*)\)',r'\1',x)
    x=re.sub(r'callfunc "itheal", (-?[0-9]+), (-?[0-9]+).*',r'heal \1, \2, 1;',x)
    x=re.sub(r'callfunc "RequireStat", b(.*), ([0-9]+).*',r'set @bStat, \1; set @minbStatVal, \2; callfunc "RequireStat";',x)
    x=re.sub(r'callfunc\("SC_Bonus", (-?[0-9]+), SC_PLUSATTACKPOWER, (-?[0-9]+).*',r'sc_start sc_raiseattackstrength, \1, \2;',x)
    x=re.sub(r'callfunc\("SC_Bonus", (-?[0-9]+), SC_ATTHASTE_POTION1, (-?[0-9]+).*',r'sc_start sc_raiseattackspeed0, \1, \2;',x)
    x=re.sub(r'callfunc\("SC_Bonus", (-?[0-9]+), SC_SLOWPOISON, (-?[0-9]+).*',r'sc_start sc_slowpoison, \1, \2;',x) # uses 180k in tmwa files but gets multiplied by 1000 in source if low evolved value is taken
    x=re.sub(r'callfunc\("SC_Bonus", (-?[0-9]+), SC_BLOODING, (-?[0-9]+).*',r'sc_start sc_poison, \1, \2;',x)
    x=re.sub(r' +',' ',x)
    return x.replace('\n', '').replace("\t","").strip()

#############################################################################################
def stin(x):
    return x.replace('\n', '').replace('|', '').replace(')', '').replace('Id: ', '').replace('"','').replace("    ","").replace("\t","").replace('Name: ','').replace(';','')

#############################################################################################
"""
# Type
enum class ItemType : uint8_t
{
    USE     = 0,    // in eA, healing only
    _1      = 1,    // unused
    _2      = 2,    // in eA, other usable items
    JUNK    = 3,    // "useless" items (e.g. quests)
    WEAPON  = 4,    // all weapons
    ARMOR   = 5,    // all other equipment
    _6      = 6,    // in eA, card
    _7      = 7,    // in eA, pet egg
    _8      = 8,    // in eA, pet equipment
    _9      = 9,    // unused
    ARROW   = 10,   // ammo
    _11     = 11,   // in eA, delayed use (special script)
};

# used in tmwa
IT_USABLE
IT_ETC
IT_WEAPON
IT_ARMOR
IT_AMMO

# View
enum class ItemLook : uint16_t
{
    NONE = 0,
    BLADE = 1, // or some other common weapons
    SETZER_AND_SCYTHE = 3,
    STAFF = 10,
    BOW = 11,
    COUNT = 17,
};

// coefficients for each weapon type
// (not all used)
static //const
earray<interval_t, ItemLook, ItemLook::COUNT> aspd_base_0 //=
{{
650_ms,  // 0 NONE
700_ms,  // 1 BLADE or some other common weapons
750_ms,  // 2
610_ms,  // 3 SETZER_AND_SCYTHE
2000_ms, // 4
2000_ms, // 5
800_ms,  // 6 Falchion
2000_ms, // 7
700_ms,  // 8
700_ms,  // 9
650_ms,  //10 STAFF / Sandcutter
900_ms,  //11 BOW
2000_ms, //12
2000_ms, //13
2000_ms, //14
2000_ms, //15
2000_ms, //16
}};

# Loc
enum class EPOS : uint16_t
{
    ZERO     = 0x0000, # 0
    LEGS     = 0x0001, # 1     EQP_HEAD_LOW
    WEAPON1H = 0x0002, # 2     EQP_HAND_R = 1 Hand
    GLOVES   = 0x0004, # 4     EQP_GARMENT
    CAPE     = 0x0008, # 8     EQP_ACC_L (Isis and such)
    MISC1    = 0x0010, # 16    EQP_ARMOR (Amuletts, Mana pearl and such)
    SHIELD   = 0x0020, # 32    EQP_HAND_L
    WEAPON2H = 0x0022, # 34    [EQP_HAND_L,EQP_HAND_R] = 2 Hand (2(EQP_HAND_R)+32(EQP_HAND_L))
    SHOES    = 0x0040, # 64    EQP_SHOES
    MISC2    = 0x0080, # 128   EQP_ACC_R (Rings)
    HAT      = 0x0100, # 256   EQP_HEAD_TOP
    TORSO    = 0x0200, # 512   EQP_HEAD_MID

    ARROW   = 0x8000, # 32768 EQP_AMMO
};

# used in current item_db.conf
    Loc: "EQP_ACC_L"
    Loc: "EQP_ACC_R"
    Loc: "EQP_AMMO"
    Loc: "EQP_ARMOR"
    Loc: "EQP_GARMENT"
    Loc: "EQP_HAND_L"
    Loc: ["EQP_HAND_L", "EQP_HAND_R"]
    Loc: "EQP_HAND_R"
    Loc: "EQP_HEAD_LOW"
    Loc: "EQP_HEAD_MID"
    Loc: "EQP_HEAD_TOP"
    Loc: "EQP_SHOES"
"""
def write_item(i, f):

    ## Type
    if i.type == "IT_USABLE":
        type="0"
    elif i.type == "IT_ETC":
        type="3"
    elif i.type == "IT_WEAPON":
        type="4"
    elif i.type == "IT_ARMOR":
        type="5"
    elif i.type == "IT_AMMO":
        type="10"

    ## View
    if i.aegis == "Setzer" or i.aegis == "Scythe":
        view="3"
    elif i.aegis == "Beheader":
        view="4"
    elif i.aegis == "SandCutter" or i.aegis == "Jackal" or i.aegis == "WoodenStaff" or i.aegis == "SweetTooth":
        view="10"
    elif i.subtype == "W_BOW":
        view="11"
    elif i.type == "IT_WEAPON":
        view="1"
    else:
        view="0"

    ## Loc
    if i.loc == "EQP_HEAD_LOW":
        loc="1"
    elif i.loc == "EQP_HAND_R":
        loc="2"
    elif i.loc == "[EQP_HAND_L,EQP_HAND_R]":
        loc="34"
    elif i.loc == "EQP_GARMENT":
        loc="4"
    elif i.loc == "EQP_ACC_L":
        loc="8"
    elif i.loc == "EQP_ARMOR":
        loc="16"
    elif i.loc == "EQP_HAND_L":
        loc="32"
    elif i.loc == "EQP_SHOES":
        loc="64"
    elif i.loc == "EQP_ACC_R":
        loc="128"
    elif i.loc == "EQP_HEAD_TOP":
        loc="256"
    elif i.loc == "EQP_HEAD_MID":
        loc="512"
    elif i.loc == "EQP_AMMO":
        loc="32768"
    else:
        loc="0"

    if i.disabled:
        i.id="//"+i.id
    if i.gmlvlonly:
        i.eqscript.insert(0, "callfunc \"RestrictedItem\";")

    ## Add spaces
    md=str(i.md)

    i.id=i.id+','+' '*(len(re.findall('//ID, *', description_i)[0])-len(i.id)-1)
    i.aegis=i.aegis+','+' '*(len(re.findall('Name, *', description_i)[0])-len(i.aegis)-1)
    type=type+','+' '*(len(re.findall('Type, *', description_i)[0])-len(type)-1)
    i.buy=i.buy+','+' '*(len(re.findall('Price, *', description_i)[0])-len(i.buy)-1)
    i.sell=i.sell+','+' '*(len(re.findall('Sell, *', description_i)[0])-len(i.sell)-1)
    i.weight=i.weight+','+' '*(len(re.findall('Weight, *', description_i)[0])-len(i.weight)-1)
    i.atk=i.atk+','+' '*(len(re.findall('ATK, *', description_i)[0])-len(i.atk)-1)
    i.df=i.df+','+' '*(len(re.findall('DEF, *', description_i)[0])-len(i.df)-1)
    i.range=i.range+','+' '*(len(re.findall('Range, *', description_i)[0])-len(i.range)-1)
    i.matk=i.matk+','+' '*(len(re.findall('Mbonus, *', description_i)[0])-len(i.matk)-1)
    i.sl=i.sl+','+' '*(len(re.findall('Slot, *', description_i)[0])-len(i.sl)-1)
    i.gender=i.gender+','+' '*(len(re.findall('Gender, *', description_i)[0])-len(i.gender)-1)
    loc=loc+','+' '*(len(re.findall('Loc, *', description_i)[0])-len(loc)-1)
    i.wlv=i.wlv+','+' '*(len(re.findall('wLV, *', description_i)[0])-len(i.wlv)-1)
    i.elv=i.elv+','+' '*(len(re.findall('eLV, *', description_i)[0])-len(i.elv)-1)
    view=view+','+' '*(len(re.findall('View, *', description_i)[0])-len(view)-1)
    md=md+','+' '*(len(re.findall('Mode, *', description_i)[0])-len(md)-1)
    usescriptstr='{'+' '.join(str(x) for x in i.usescript)+'}'
    usescriptstr=usescriptstr+','+' '*(len(re.findall('{UseScript}, *', description_i)[0])-len(usescriptstr)-1)
    eqscriptstr='{'+' '.join(str(x) for x in i.eqscript)+'}'
    #eqscriptstr=eqscriptstr+','+' '*(len(re.findall('{EquipScript}, *', description_i)[0])-len(eqscriptstr)-1)

    ## Write the line
    f.write("""%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n""" % (i.id, i.aegis, type, i.buy, i.sell, i.weight, i.atk, i.df, i.range, i.matk, i.sl, i.gender, loc, i.wlv, i.elv, view, md, usescriptstr, eqscriptstr))
    return

#############################################################################################
def write_item_header(f):
    f.write("//THIS FILE IS GENERATED AUTOMATICALLY\n//DO NOT EDIT IT DIRECTLY\n//Edit item_db.conf instead!\n")
    f.write(description_i + "\n")
    return

#############################################################################################
def save_items():
    global IT_ETC, IT_USABLE, IT_AMMO, IT_WEAPON, IT_ARMOR

    ## Items

    DESCRIPTION_AFTER=20

    WEAPON=IT_WEAPON['HAND_2']+IT_WEAPON['HAND_1']+IT_AMMO
    write_to_file(WEAPON, "../world/map/db/item_db_weapon.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_HEAD_MID'], "../world/map/db/item_db_chest.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_SHOES'], "../world/map/db/item_db_foot.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_GARMENT'], "../world/map/db/item_db_hand.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_HEAD_TOP'], "../world/map/db/item_db_head.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_HEAD_LOW'], "../world/map/db/item_db_leg.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ARMOR['EQP_HAND_L'], "../world/map/db/item_db_offhand.txt", 0, DESCRIPTION_AFTER)
    TRINKLET=IT_ARMOR['EQP_ACC_L']+IT_ARMOR['EQP_ACC_R']
    write_to_file(TRINKLET, "../world/map/db/item_db_trinket.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_USABLE, "../world/map/db/item_db_use.txt", 0, DESCRIPTION_AFTER)
    write_to_file(IT_ETC, "../world/map/db/item_db_generic.txt", 0, DESCRIPTION_AFTER)

    return



#    __________
#   /          \
#  /    Mobs    \
# /______________\
# \______________/

class Mob:
  def __init__(self):
    # Basic
    self.id="0"
    self.aegis="UnknownMonster" # SpriteName is not used anywhere, we are using its ID
    self.name="Unknown Monster Name"
    self.view="1"
    self.chch=False
    self.boss=False
    self.size="1"
    self.race="0" # TODO Convert RC_*
    self.elem="0" # TODO Convert Ele_*
    self.elLv="0" # Element Level
    self.mode="0" # TODO Convert MD_* and fields

    # General
    self.mobpt="0" # Mob Points “Level”
    self.hp="0"
    self.sp="0"
    self.xp="0"
    self.jp="0"

    # MvP
    self.mvp="0"

    # Defensive
    self.st=""
    self.md=0
    self.df="0"
    self.mdf="0"
    self.cdf="0"

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
    self.adelay="0"
    self.amotion="0"
    self.dmotion="0"

    # Misc
    self.mtcnt="0"
    self.mtstr="0"
    self.drops=[]

#############################################################################################
def MobAlloc(ab):
    if ab.name == "Unknown Monster Name":
        return

    try:
        maab=int(ab.mobpt)
    except:
        maab=9901

    aegis.write("%s %s\n" % (ab.aegis, ab.id))
    if maab <= 19:
        Mobs1.append(ab)
    elif maab <= 39:
        Mobs2.append(ab)
    elif maab <= 59:
        Mobs3.append(ab)
    elif maab <= 79:
        Mobs4.append(ab)
    elif maab <= 99:
        Mobs5.append(ab)
    elif maab <= 150:
        Mobs6.append(ab)
    elif maab != 9901:
        MobsA.append(ab)
    else:
        print("WARNING, Disregarding \"%s\" (ID: %s) as invalid mob" % (ab.name, ab.id))

#############################################################################################
def testMobs():
    MD_CANMOVE =           1
    MD_LOOTER =            2
    MD_AGGRESSIVE =        4
    MD_ASSIST =            8
    MD_CASTSENSOR_IDLE =   16
    MD_BOSS =              32
    MD_PLANT =             64
    MD_CANATTACK =         128

    print("\nGenerating Mob Database...")
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

        if "\tId:" in a:
            x.id=stp(a)
        elif "\tSpriteName:" in a:
            x.aegis=stp(a)
        elif "\tName:" in a:
            x.name=stp(a)
        elif "\tHp:" in a:
            x.hp=stp(a)
        elif "\tSp:" in a:
            x.sp=stp(a)
        elif "\tLv:" in a:
            x.mobpt=stp(a)
        elif "\tExp:" in a:
            x.xp=stp(a)
        elif "\tJExp:" in a:
            x.jp=stp(a)
        elif "\tMvpExp: " in a:
            x.mvp=stp(a)
        elif "\tDef:" in a:
            x.df=stp(a)
        elif "\tMdef:" in a:
            x.mdf=stp(a)
        elif "\tCriticalDef:" in a:
            x.cdf=stp(a)
        elif "\tAttack:" in a:
            x.atk=stp(a)
        elif "\tAttackRange:" in a:
            x.range=stp(a)
        elif "\tMoveSpeed:" in a:
            x.move=stp(a)
        elif "\tViewRange:" in a:
            x.view=stp(a)
        elif "\tChaseRange:" in a:
            x.chase=stp(a)
        elif "\tAttackDelay:" in a:
            x.adelay=stp(a)
        elif "\tAttackMotion:" in a:
            x.amotion=stp(a)
        elif "\tDamageMotion:" in a:
            x.dmotion=stp(a)
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
        elif "\tMutationCount: " in a:
            x.mtcnt=stp(a)
        elif "\tMutationStrength: " in a:
            x.mtstr=stp(a)
        elif "\tSize: " in a:
            x.size=stp(a)
        elif "\tRace: " in a:
            x.race=stp(a) # TODO: Conversion
        elif "\tElement: " in a:
            tmp=stp(a).split(",")
            #Element: (type, level)
            x.elem=tmp[0].replace("(","").strip()
            x.elLv=tmp[1].replace(")","").strip()
            try:
                if int(x.elem) in [4, 5]:
                    x.elem = "2"
                elif int(x.elem) in [8, 9, "10"]:
                    x.elem="7"
            except:
                traceback.print_exc()
        elif "\tCanMove: true" in a:
            x.md = x.md | MD_CANMOVE
        elif "\tLooter: true" in a:
            x.md = x.md | MD_LOOTER
        elif "\tAggressive: true" in a:
            x.md = x.md | MD_AGGRESSIVE
        elif "\tAssist: true" in a:
            x.md = x.md | MD_ASSIST
        elif "\tCastSensorIdle: true" in a:
            x.md = x.md | MD_CASTSENSOR_IDLE
        elif "\tBoss: true" in a:
            x.md = x.md | MD_BOSS
        elif "\tPlant: true" in a:
            x.md = x.md | MD_PLANT
        elif "\tCanAttack: true" in a:
            x.md = x.md | MD_CANATTACK
        elif '\tDrops: ' in a:
            dropper=True
        elif dropper and '\t}' in a:
            dropper=False
        elif dropper:
            x.drops.append(stp(a).split(": "))

    # Write last entry
    MobAlloc(x)

    src.close()

#############################################################################################
def stp(x):
    return x.replace('\n', '').replace('|', '').replace('(int, defaults to ', '').replace(')', '').replace('basic experience', '').replace('"','').replace("    ","").replace("\t","").replace('(string', '').replace('SpriteName: ','').replace('Name: ','').replace('AttackDelay: ', '').replace('AttackMotion: ', '').replace('DamageMotion: ', '').replace('MoveSpeed: ', '').replace('AttackRange: ', '').replace('ViewRange: ','').replace('ChaseRange: ','').replace('Attack: ','').replace('Hp: ','').replace('Sp: ','').replace('Id: ','').replace('Lv: ','').replace('view range','').replace('attack range','').replace('move speed','').replace('health','').replace('(int','').replace('attack delay','atk.').replace("Str:", "").replace("Agi:", "").replace("Vit:", "").replace("Int:", "").replace("Dex:", "").replace("Luk:", "").replace("Mdef:","").replace("CriticalDef:","").replace("Def:","").replace("Size:","").replace("Race:", "").replace("Element:","").replace("JExp: ","").replace("MvpExp: ","").replace("Exp: ","").replace("MutationCount: ","").replace("MutationStrength: ","").strip()

#############################################################################################
def write_mob(m, f):
    ## Prepare new drop list
    i=0

    dl=[]
    while i < 10:
        if len(m.drops) > i:
            try:
                it = m.drops[i][0] # TODO: Convert to INT
                ch = m.drops[i][1]
                it = AllItems[it]
                ch = int(ch)
            except ValueError:
                ch = ch.split(",")[0].replace('(','')
            # except (40, "ODG_BASICSTAT") => split more
            except:
                print("ERROR mob %s drop %s" % (m.name, repr(m.drops)))
                traceback.print_exc()
                it = 0
                ch = 0
        else:
            it = 0
            ch = 0
        dl.append(str(it))
        dl.append(str(ch))
        i+=1

    ## Add spaces
    el=str(int("%s%s" % (m.elLv, m.elem)))
    atk1=m.atk.replace('[','').split(",")[0]
    atk2=m.atk.replace(']','').split(",")[1].strip()
    md=str(m.md)
    item1="0"
    item2="0"
    expper="0"
    mvp1id="0"
    mvp1p="0"
    mvp2id="0"
    mvp2p="0"
    mvp3id="0"
    mvp3p="0"

    m.id=m.id+','+' '*(len(re.findall('//ID, *', description_m)[0])-len(m.id)-1)
    m.aegis=m.aegis+','+' '*(len(re.findall('Name, *', description_m)[0])-len(m.aegis)-1)
    m.mobpt=m.mobpt+','+' '*(len(re.findall('LV, *', description_m)[0])-len(m.mobpt)-1)
    m.hp=m.hp+','+' '*(len(re.findall('HP, *', description_m)[0])-len(m.hp)-1)
    m.sp=m.sp+','+' '*(len(re.findall('SP, *', description_m)[0])-len(m.sp)-1)
    m.xp=m.xp+','+' '*(len(re.findall('EXP, *', description_m)[0])-len(m.xp)-1)
    m.jp=m.jp+','+' '*(len(re.findall('JEXP, *', description_m)[0])-len(m.jp)-1)
    m.range=m.range+','+' '*(len(re.findall('Range1, *', description_m)[0])-len(m.range)-1)
    atk1=atk1+','+' '*(len(re.findall('ATK1, *', description_m)[0])-len(atk1)-1)
    atk2=atk2+','+' '*(len(re.findall('ATK2, *', description_m)[0])-len(atk2)-1)
    m.df=m.df+','+' '*(len(re.findall('DEF, *', description_m)[0])-len(m.df)-1)
    m.mdf=m.mdf+','+' '*(len(re.findall('MDEF, *', description_m)[0])-len(m.mdf)-1)
    m.cdf=m.cdf+','+' '*(len(re.findall('CRITDEF, *', description_m)[0])-len(m.cdf)-1)
    m.str=m.str+','+' '*(len(re.findall('STR, *', description_m)[0])-len(m.str)-1)
    m.agi=m.agi+','+' '*(len(re.findall('AGI, *', description_m)[0])-len(m.agi)-1)
    m.vit=m.vit+','+' '*(len(re.findall('VIT, *', description_m)[0])-len(m.vit)-1)
    m.int=m.int+','+' '*(len(re.findall('INT, *', description_m)[0])-len(m.int)-1)
    m.dex=m.dex+','+' '*(len(re.findall('DEX, *', description_m)[0])-len(m.dex)-1)
    m.luk=m.luk+','+' '*(len(re.findall('LUK, *', description_m)[0])-len(m.luk)-1)
    m.view=m.view+','+' '*(len(re.findall('Range2, *', description_m)[0])-len(m.view)-1)
    m.chase=m.chase+','+' '*(len(re.findall('Range3, *', description_m)[0])-len(m.chase)-1)
    m.size=m.size+','+' '*(len(re.findall('Scale, *', description_m)[0])-len(m.size)-1)
    m.race=m.race+','+' '*(len(re.findall('Race, *', description_m)[0])-len(m.race)-1)
    el=el+','+' '*(len(re.findall('Element, *', description_m)[0])-len(el)-1)
    md=md+','+' '*(len(re.findall('Mode, *', description_m)[0])-len(md)-1)
    m.move=m.move+','+' '*(len(re.findall('Speed, *', description_m)[0])-len(m.move)-1)
    m.adelay=m.adelay+','+' '*(len(re.findall('Adelay, *', description_m)[0])-len(m.adelay)-1)
    m.amotion=m.amotion+','+' '*(len(re.findall('Amotion, *', description_m)[0])-len(m.amotion)-1)
    m.dmotion=m.dmotion+','+' '*(len(re.findall('Dmotion, *', description_m)[0])-len(m.dmotion)-1)
    dl[0]=dl[0]+','+' '*(len(re.findall('Drop0id, *', description_m)[0])-len(dl[0])-1)
    dl[1]=dl[1]+','+' '*(len(re.findall('Drop0%, *', description_m)[0])-len(dl[1])-1)
    dl[2]=dl[2]+','+' '*(len(re.findall('Drop1id, *', description_m)[0])-len(dl[2])-1)
    dl[3]=dl[3]+','+' '*(len(re.findall('Drop1%, *', description_m)[0])-len(dl[3])-1)
    dl[4]=dl[4]+','+' '*(len(re.findall('Drop2id, *', description_m)[0])-len(dl[4])-1)
    dl[5]=dl[5]+','+' '*(len(re.findall('Drop2%, *', description_m)[0])-len(dl[5])-1)
    dl[6]=dl[6]+','+' '*(len(re.findall('Drop3id, *', description_m)[0])-len(dl[6])-1)
    dl[7]=dl[7]+','+' '*(len(re.findall('Drop3%, *', description_m)[0])-len(dl[7])-1)
    dl[8]=dl[8]+','+' '*(len(re.findall('Drop4id, *', description_m)[0])-len(dl[8])-1)
    dl[9]=dl[9]+','+' '*(len(re.findall('Drop4%, *', description_m)[0])-len(dl[9])-1)
    dl[10]=dl[10]+','+' '*(len(re.findall('Drop5id, *', description_m)[0])-len(dl[10])-1)
    dl[11]=dl[11]+','+' '*(len(re.findall('Drop5%, *', description_m)[0])-len(dl[11])-1)
    dl[12]=dl[12]+','+' '*(len(re.findall('Drop6id, *', description_m)[0])-len(dl[12])-1)
    dl[13]=dl[13]+','+' '*(len(re.findall('Drop6%, *', description_m)[0])-len(dl[13])-1)
    dl[14]=dl[14]+','+' '*(len(re.findall('Drop7id, *', description_m)[0])-len(dl[14])-1)
    dl[15]=dl[15]+','+' '*(len(re.findall('Drop7%, *', description_m)[0])-len(dl[15])-1)
    dl[16]=dl[16]+','+' '*(len(re.findall('Drop8id, *', description_m)[0])-len(dl[16])-1)
    dl[17]=dl[17]+','+' '*(len(re.findall('Drop8%, *', description_m)[0])-len(dl[17])-1)
    dl[18]=dl[18]+','+' '*(len(re.findall('Drop9id, *', description_m)[0])-len(dl[18])-1)
    dl[19]=dl[19]+','+' '*(len(re.findall('Drop9%, *', description_m)[0])-len(dl[19])-1)
    item1=item1+','+' '*(len(re.findall('Item1, *', description_m)[0])-len(item1)-1)
    item2=item2+','+' '*(len(re.findall('Item2, *', description_m)[0])-len(item2)-1)
    m.mvp=m.mvp+','+' '*(len(re.findall('MEXP, *', description_m)[0])-len(m.mvp)-1)
    expper=expper+','+' '*(len(re.findall('ExpPer, *', description_m)[0])-len(expper)-1)
    mvp1id=mvp1id+','+' '*(len(re.findall('MVP1id, *', description_m)[0])-len(mvp1id)-1)
    mvp1p=mvp1p+','+' '*(len(re.findall('MVP1per, *', description_m)[0])-len(mvp1p)-1)
    mvp2id=mvp2id+','+' '*(len(re.findall('MVP2id, *', description_m)[0])-len(mvp2id)-1)
    mvp2p=mvp2p+','+' '*(len(re.findall('MVP2per, *', description_m)[0])-len(mvp2p)-1)
    mvp3id=mvp3id+','+' '*(len(re.findall('MVP3id, *', description_m)[0])-len(mvp3id)-1)
    mvp3p=mvp3p+','+' '*(len(re.findall('MVP3per, *', description_m)[0])-len(mvp3p)-1)
    m.mtcnt=m.mtcnt+','+' '*(len(re.findall('mutationcount, *', description_m)[0])-len(m.mtcnt)-1)
#    m.mtstr=m.mtstr+','+' '*(len(re.findall('mutationstrength, *', description_m)[0])-len(m.mtstr)-1)

    ## Write the line
    f.write("""%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n""" % (m.id, m.aegis, m.aegis, m.mobpt, m.hp, m.sp,
m.xp, m.jp, m.range, atk1, atk2, m.df, m.mdf, m.cdf, m.str, m.agi, m.vit,
m.int, m.dex, m.luk, m.view, m.chase, m.size, m.race, el, md, m.move,
m.adelay, m.amotion, m.dmotion, dl[0],dl[1], dl[2],dl[3], dl[4],dl[5],
dl[6],dl[7], dl[8],dl[9], dl[10],dl[11], dl[12],dl[13], dl[14],dl[15],
dl[16],dl[17], dl[18],dl[19], item1, item2, m.mvp, expper, mvp1id, mvp1p, mvp2id, mvp2p, mvp3id, mvp3p, m.mtcnt, m.mtstr))
    return

#############################################################################################
def write_mob_header(f):
    f.write("//THIS FILE IS GENERATED AUTOMATICALLY\n//DO NOT EDIT IT DIRECTLY\n//Edit mob_db.conf instead!\n")
    f.write(description_m + "\n")
    return

#############################################################################################
def save_mobs():
    global Mobs1, Mobs2, Mobs3, Mobs4, Mobs5, Mobs6, MobsA

    DESCRIPTION_AFTER=20

    ## Mobs

    write_to_file(Mobs1, "../world/map/db/mob_db_0_19.txt", 1, DESCRIPTION_AFTER)
    write_to_file(Mobs2, "../world/map/db/mob_db_20_39.txt", 1, DESCRIPTION_AFTER)
    write_to_file(Mobs3, "../world/map/db/mob_db_40_59.txt", 1, DESCRIPTION_AFTER)
    write_to_file(Mobs4, "../world/map/db/mob_db_60_79.txt", 1, DESCRIPTION_AFTER)
    write_to_file(Mobs5, "../world/map/db/mob_db_80_99.txt", 1, DESCRIPTION_AFTER)
    write_to_file(Mobs6, "../world/map/db/mob_db_over_100.txt", 1, DESCRIPTION_AFTER)
    write_to_file(MobsA, "../world/map/db/mob_db_over_150.txt", 1, DESCRIPTION_AFTER)

    return




#############################################################################################
showHeader()

newItemDB()
testMobs()

save_items()
save_mobs()

aegis.close()

showFooter()
exit(0)
