#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Licensed under GNU General Public License

import sys, os, datetime, math;


# VARIOUS SETTINGS

# If something seems not to work, set this value to 1 to get more information
debug = 0

# Number of rows between table header
headerafterrow = 10

# Formatting of traits
traitstart = '\'\'<span style="color:#ad1818">'
traitend   = '</span>\'\''

# Formatting of mutations
mutationstart = '\'\'<span style="color:#4a4a4a">'
mutationend   = '</span>\'\''

##########################################
##                                      ##
##  CHANGE THE INTRODUCTORY TEXT BELOW  ##
##                                      ##
##########################################

intro = []

# Each appended line will automatically end with a line break

intro.append("{{Category_monster}}")
intro.append("{{Status_green}}")
intro.append("")
intro.append("'''Page last generated on %s.'''" % datetime.date.today())
intro.append("")
intro.append("'''Warning:''' This reference might be out of date. The python script to generate this page can be found on the discussion page. Please be aware that any manual changes made to this page may be lost when the page is generated anew. Also, this reference might not reflect what is currently in the game. [https://github.com/themanaworld/tmwa-server-data/blob/master/world/map/db/mob_db.txt You can view the most up-to-date version here.]")
intro.append("")
intro.append("The monsters are sorted roughly by their fighting strength, calculated as <code>health_points * (attack_min + attack_max)</code>. For more information on the drops please see the [[item reference]].")
intro.append("")
intro.append("'''Key:''' HP is health points, DEF is defense, ATT is attack, EXP is the calculated base experience, JEXP is the job experience. The others are self-explanatory. Traits (such as aggressive) are written in " + traitstart + "italics" + traitend + ".")
intro.append("")


# Table headers

def printtableheader():
    print '! style="background:#efdead;" | Image'
    print '! style="background:#efdead;" | Name'
    print '! style="background:#efdead;" | ID'
    print '! style="background:#efdead;" | HP'
    print '! style="background:#efdead;" | DEF'
    print '! style="background:#efdead;" | ATT'
    print '! style="background:#efdead;" | EXP'
    print '! style="background:#efdead;" | JEXP'
    print '! style="background:#efdead;" | Drops'
    print '|-'


class whatever: pass

log = []


def saveint(string):
    try:
        return int(string)
    except:
        return 0
        

def parsemonsters(file):
    objects = []
    for line in file:
        s = line[:line.find('//')].strip().replace('\t','')
        if s:
            values = s.split(',')
            if line[0] == 'ID':
                if debug:
                    log.append("FOUND COMMENT LINE: %s" % str(values))
                    log.append("NUMBER OF FIELDS IN COMMENT LINE: %d" % len(values))
                continue
            numberofvalues = 57
            if len(values) != numberofvalues:
                log.append("mob_db: Warning, monster-line with ID %s has %d values instead of %d" % (values[0], len(values), numberofvalues))
                if debug:
                    log.append("  line was %s" % str(values))
                while len(values) < numberofvalues - 1:
                    values.append('')
                while len(values) > numberofvalues - 1:
                    values.pop()

            o = whatever()

            o.id             = saveint(values[0])   # Monster ID
            o.label          =         values[1].strip()    # The label (name) used in GM commands
            o.imgurl         = "[[Image:" + values[1].strip() + ".png]]"   # Name with Img Url
            o.name           =         values[2].strip()    # The name known to the server (not to the client)
            o.level          = saveint(values[3])   # Level
            o.hp             = saveint(values[4])   # Health points
            o.sp             = saveint(values[5])   # SP
            o.experience     = saveint(values[6])   # Experience points
            o.jobexperience  = saveint(values[7])   # Job experience points
            o.range1         = saveint(values[8])   # Range of attack
            o.attackmin      = saveint(values[9])   # Minimum attack damage
            o.attackmax      = saveint(values[10])  # Maximum attack damage
            o.defense        = saveint(values[11])  # Defense (relative in percent)
            o.magicaldefense = saveint(values[12])  # Magical defense (ditto)
            o.strength       = saveint(values[13])  # Strength level
            o.agility        = saveint(values[14])  # Agility level
            o.vitality       = saveint(values[15])  # Vitality level
            o.intelligence   = saveint(values[16])  # Intelligence level
            o.dexterity      = saveint(values[17])  # Dexterity level
            o.luck           = saveint(values[18])  # Luck level
            o.range2         = saveint(values[19])  # Some-other range ???
            o.range3         = saveint(values[20])  # Line-of-sight range ???
            o.scale          = saveint(values[21])  # The size type
            o.race           = saveint(values[22])  # Race
            o.element        = saveint(values[23])  # Element level and type
            o.mode           = saveint(values[24])  # Behaviour type (aggressive etc.)
            o.speed          = saveint(values[25])  # Walking speed (faster for lower values)
            o.attackdelay    = saveint(values[26])  # Attack delay (attack speed is the inverse)
            o.attackmotion   = saveint(values[27])  # Speed of attack animation ???
            o.damagemotion   = saveint(values[28])  # Speed of damage animation ???

            o.drop = [whatever() for i in range(8)]

            o.drop[0].id     = saveint(values[29])  # The following are 8 groups of item IDs and
            o.drop[0].per    = saveint(values[30])  #     drop rates (100 = 1%) for drops 1 to 8
            o.drop[1].id     = saveint(values[31])
            o.drop[1].per    = saveint(values[32])
            o.drop[2].id     = saveint(values[33])
            o.drop[2].per    = saveint(values[34])
            o.drop[3].id     = saveint(values[35])
            o.drop[3].per    = saveint(values[36])
            o.drop[4].id     = saveint(values[37])
            o.drop[4].per    = saveint(values[38])
            o.drop[5].id     = saveint(values[39])
            o.drop[5].per    = saveint(values[40])
            o.drop[6].id     = saveint(values[41])
            o.drop[6].per    = saveint(values[42])
            o.drop[7].id     = saveint(values[43])
            o.drop[7].per    = saveint(values[44])

            o.item1          = saveint(values[45])  # ???
            o.item2          = saveint(values[46])  # ???
            o.mexp           = saveint(values[47])  # ???
            o.expper         = saveint(values[48])  # ???

            o.mvp = [whatever() for i in range(3)]

            o.mvp[0].id      = saveint(values[49])  # The following are 3 groups of item IDs and
            o.mvp[0].per     = saveint(values[50])  #     drop rates (100 = 1%) for what drops ???
            o.mvp[1].id      = saveint(values[51])
            o.mvp[1].per     = saveint(values[52])
            o.mvp[2].id      = saveint(values[53])
            o.mvp[2].per     = saveint(values[54])

            o.mutnr          = saveint(values[55])  # Number of mutations
            o.mutstr         = saveint(values[56])  # Mutation strength

            objects.append(o)

    return objects

def adddropnames(monsters,dropnames):
    for m in monsters:
        for d in m.drop:
            # Only add a dropname if it isn't "default" (id=0)
            if d.id in dropnames and int(d.id):
                d.name = dropnames[d.id]
            else:
                d.name = ''
    

def parseitemnames(file):
    global log
    dic = {}
    for line in file:
        if line[0] == '#' or line[0] == ',':
            continue
        s = line[:line.find('//')].strip()
        if s:
            values = s.split(',')
            if len(values) < 3:
                if len(values) > 0: log.append("mob_db: Warning, item-line with ID %s doesn't even have 3 values. Skipped." % (values[0], len(values)))
            else:
                id = int(values[0])
                dic[id] = "[[" + values[2].strip() + "]]"
    return dic


def printlog():
    if len(log) > 0:
        print '\n---------------------------------------'
    for line in log:
        print line


def getdropstring(monster):
    i = 0
    output = ""
    monster.drop.sort(key=lambda x: x.per, reverse=True)
    for d in monster.drop:
        if d.name: 
            if i != 0:
                output += '<br>'
            s = ""
            if d.per >= 1000:
                s = "%d" % (d.per/100)
            elif d.per >= 100:
                if (d.per % 100) != 0:
                    s = "%1.1f" % (d.per/100.0)
                else:
                    s = "%d"    % (d.per/100)
            else:
                if (d.per % 1000) != 0:
                    s = "%.2f"  % (d.per/100.0)
                else:
                    s = "%.1f"  % (d.per/100.0)
            output += ("%s (%s%%)" % (d.name.replace('\t',''), s))
            i += 1
    return output


def printmonsters(monsters):
    # Key to monster behaviour/trait modes
    #
    # TRAIT            ID    FIELD  =  MODE    COMMENT
    # Moving            0    0x0001       1
    # Looter            1    0x0002       2
    # Aggressor         2    0x0004       4
    # Assister          3    0x0008       8
    # ?                 4    0x0010      16    Currently not used
    # ?                 5    0x0020      32    Used (but what does it do?)
    # ?                 6    0x0040      64    Currently not used
    # ?                 7    0x0080     128    Currently not used
    # ?                 8    0x0100     256    Currently not used
    # ?                 9    0x0200     512    Currently not used
    # ?                10    0x0400    1024    Currently not used
    # ?                11    0x0800    2048    Currently not used
    # ?                12    0x1000    4096    Currently not used
    # Attack master    13    0x2000    8192    Used for summoned monsters

    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'

    i = 0
    for m in monsters:
        if i == headerafterrow:
            i = 0
        if i == 0:
            printtableheader()

        # Image
        print '| align="center" | %s' % m.imgurl

        # Name, Stationary/Assists traits and Mutations
        sys.stdout.write('| %s' % m.name)
        if m.mode >> 0 & 1 == 0:
            sys.stdout.write('<br />' + traitstart + 'Stationary' + traitend)
        if m.mode >> 3 & 1 == 1:
            sys.stdout.write('<br />' + traitstart + 'Assists' + traitend)
        if m.mutnr > 0:
            sys.stdout.write('<br />' + mutationstart + 'May mutate %d attribute' % m.mutnr)
            if m.mutnr > 1:
                sys.stdout.write('s')
            sys.stdout.write(' up to %d%%' % m.mutstr + mutationend)
        #else:
        #    sys.stdout.write('<br />' + mutationstart + 'Does not mutate' + mutationend)
        print

        # ID, Health and Defense
        print '| align="center" | %d'   % m.id
        print '| align="center" | %d'   % m.hp
        print '| align="center" | %d%%' % m.defense

        # Attack and No-attack/Aggressive traits
        if m.mode >> 7 & 1 == 0:
            sys.stdout.write('| align="center" | ' + traitstart + 'N/A' + traitend)
        else:
            if m.attackmin < m.attackmax:
                sys.stdout.write('| align="center" | %d / %d' % (m.attackmin, m.attackmax))
            else:
                sys.stdout.write('| align="center" | %d' % m.attackmin)
            if m.mode >> 2 & 1 == 1:
                sys.stdout.write('<br />' + traitstart + 'Aggro' + traitend)
        print

        # Experience and Job experience, following *tmw-eathena*/src/map/mob.c
        calc_exp = 0

        if m.experience == 0:
            if m.hp <= 1:
                calc_exp = 1

            mod_def = 100 - m.defense

            if mod_def == 0:
                mod_def = 1

            effective_hp = ((50 - m.luck) * m.hp / 50) + (2 * m.luck * m.hp / mod_def)
            attack_factor = (m.attackmin + m.attackmax + m.strength / 3 + m.dexterity / 2 + m.luck) * (1872 / m.attackdelay) / 4
            dodge_factor = (m.level + m.agility + m.luck / 2)**(4 / 3)
            persuit_factor = (3 + m.range1) * (m.mode % 2) * 1000 / m.speed
            aggression_factor = 1

            if False:
                aggression_factor = 10 / 9

            base_exp_rate = 100 # From *tmw-eathena-data*/conf/battle_athena.conf

            calc_exp = int(math.floor(effective_hp * (math.sqrt(attack_factor) + math.sqrt(dodge_factor) + math.sqrt(persuit_factor) + 55)**3 * aggression_factor / 2000000 * base_exp_rate / 100))

            if calc_exp < 1:
                calc_exp = 1
        else:
            calc_exp = m.experience

        print '| align="center" | %d' % calc_exp
        print '| align="center" | %d' % m.jobexperience

        # Drops and Looter trait
        sys.stdout.write('| %s' % getdropstring(m))
        if m.mode >> 1 & 1 == 1:
            sys.stdout.write('<br />' + traitstart + 'Picks up loot' + traitend)
        print

        print '|-'
        i += 1

    print '|}'


#MAIN
try:
    if len(sys.argv) == 1:
        mob_db = "mob_db.txt"
        item_db = "item_db.txt"
    elif len(sys.argv) == 3:
        mob_db = sys.argv[1]
        item_db = sys.argv[2]
    else: 
        mob_db = ''
        item_db = ''
        print "Wrong number of arguments"

    if mob_db and item_db :
        if not os.path.isfile(mob_db):
            print "File does not exist: %s" % mob_db
            mob_db = ''
        if not os.path.isfile(item_db):
            print "File does not exist: %s" % item_db
            item_db = ''
    
    if not (mob_db and item_db):
        print "\nUSAGE:"
        print "%s without any arguments will use item_db.txt and mob_db.txt in the current directory." % sys.argv[0]
        print "to specify custom files, call: %s <mob_db> <item_db>" % sys.argv[0]
        exit(-1);
    else:
        if debug:
            log.append("Monster-list [mob_db] = %s" % mob_db)
            log.append("Item-list [item_db] = %s" % item_db)
        f = open(mob_db)
        monsters = parsemonsters(f);
        f = open(item_db)
        itemnames = parseitemnames(f);

        adddropnames(monsters,itemnames)
        monsters.sort(key=lambda x: x.hp*(x.attackmin+x.attackmax))

        for line in intro:
            print line

        printmonsters(monsters)

finally:
    printlog()
