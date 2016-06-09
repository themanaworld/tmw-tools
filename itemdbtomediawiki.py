#!/usr/bin/python
#Licensed under GNU General Public License

# Add tags to item.xml
# Remember to use dyecmd to create images

import sys, os, xml.dom.minidom;

debug=0

health_titles = ["Image","Name","ID","HP Bonus","SP Bonus",
                 "Price<BR />BUY/Sell","Weight","Description"]
status_titles = ["Image","Name","ID","Spell name","Parameter 1","Parameter 2",
                 "Price<BR />BUY/Sell","Weight","Description"]
weapon_titles = [" Image","Name","ID","Damage<BR />(Range)",
                 "Price<BR />BUY/Sell","Weight","Description"]
armor_titles = ["Image", "Name", "ID", "Defense", 
              "Price<BR />BUY/Sell", "Weight","Description"]
other_titles = ["Image","Name","ID","Price<BR />BUY/Sell",
                "Weight","Description "]

imagesused = set()

class whatever: pass

log = []

# parseitems(file)
## Returns list with items from eathena item_db file.

def saveint(string, altval = 0):
    a = 0
    try:
        a = int(string)
    except:
        a = altval
    return a
        
def parsescript(s):
    # Assumes that there's only one call of each method, otherwise it would need to know
    # how to combine those function calls. In practice, the latter call would prevail.
    script = {}
    scriptentry = ""
    parentry = ""
    mode = 0
    for a in s:
        if mode == 0: # looking for method
            if a.isalpha(): 
                mode = 1
                scriptentry += a
            elif a == '}': mode = 9
        elif mode == 1: # reading method name
            if a in " ;}":
                if a == " ": mode = 2
                elif a == ";": mode = 1
                elif a == "}": mode = 9
                parentry = ""
                script[scriptentry] = []
            else: scriptentry += a
        elif mode == 2: #looking for param
            if a == " ": pass
            elif a == ";": 
                mode = 0
                scriptentry = ""
            else:
                mode = 3
                parentry = a
        elif mode == 3: #reading param
            if a in (" ", ",", ";"):
                script[scriptentry].append(parentry)
                parentry = ""
                if a == ';': 
                    mode = 0
                    scriptentry = ""
                else: mode = 2
            else: 
                parentry += a
        elif mode == 9: #finished
            pass

    # Convert all possible parameters to integers
    for i in script.keys():
        for j in range(len(script[i])):
            try:
                script[i][j] = int(script[i][j])
            except:
                #print script[i][j]
                pass
    return script
    

def parseitems(file):
    objects = []
    for line in file:
        s = line[:line.find('//')].strip().replace('\t','')
        if s:
            #Replace commas inbetween {} with |, so we can use split
            mode = 0
            sout = ""
            for a in s:
                if mode == 0: #Out of {}
                    if a == '{': mode = 1
                    sout += a
                elif mode == 1: #Inside {}
                    if a == ',': sout += '|'
                    else:
                        sout += a
                        if a == '}': mode = 0

            values = sout.split(',')
            if line[0] == '#':
                if debug:
                    log.append("FOUND COMMENT LINE: %s" % str(values))
                continue
            if len(values) != 19:
                log.append("item_db: Warning, item-line with ID %s has %d values instead of 19" % (values[0], len(values)))
                if debug:
                    log.append("  line was %s" % str(values))
                sys.exit(2)

            o = whatever()
            o.id        = int(values[0])
            o.name      = values[1]
            o.jname     = values[2]
            o.type      = saveint(values[3])
            o.price     = saveint(values[4])
            o.sell      = saveint(values[5])
            o.weight    = saveint(values[6])
            o.atk       = saveint(values[7])
            o.defense   = saveint(values[8])
            o.range     = saveint(values[9])
            o.mbonus    = saveint(values[10])
            o.slot      = saveint(values[11],-1)
            o.gender    = saveint(values[12],-1)
            o.loc       = saveint(values[13],-1)
            o.wlv       = saveint(values[14])
            o.elv       = saveint(values[15])
            o.view      = saveint(values[16],-1)
            o.usescript = parsescript(values[17].replace('|',','))
            o.equipscript = parsescript(values[18].replace('|',','))
            objects.append(o)

    return objects


# parsexmlitems(file)
## Creates a dictionary containing the values of a client items.xml
## Yeah, there are XML parsers in the standard python libraries, but they're too object
## oriented and thus don't fit the style of this program.
def parsexmlitems(file):
    items = {}
    attrs = ["id", "image", "name", "description", "type", "weight", "slot"]
    items_xml = xml.dom.minidom.parse(file)
    allitems = items_xml.getElementsByTagName("item")
    for item in allitems:
        curitem = {}

        for attrs in item.attributes.keys():
            curitem[attrs] = item.attributes[attrs].value

        if ('id' in item.attributes.keys()):
            items[curitem['id']] = curitem

    return items
        

# addclientinformation(items, citems)
## Entends the item data with the data collected from the client items.xml. Adding imageurls,
## client-name and -description

def addclientinformation(items,citems):
    for i in items:
        if i.id in citems:
            i.imagename=citems[i.id]["image"]
            url=i.imagename[0].upper() + i.imagename[1:]
            i.imgurl = "[[Image:"+ url + "]]"
            imagesused.add( citems[i.id]["image"])
            i.description = citems[i.id]["description"]
            i.clientname = citems[i.id]["name"]
        else:
            i.imgurl = ''
            i.description = ''
            i.clientname = ''



# gettypedir (items)
## Returns sorted lists of items by itemtype
def gettypedir(items):
    items.sort(key=lambda x: x.price+x.sell)

    typedir = whatever()
    typedir.healthy = []
    typedir.status = []
    typedir.inspiring = []
    typedir.weapons = []
    typedir.combos = []
    typedir.armor = []
    typedir.other = []
    for item in items:
        print item.type

    typedir.weapons.sort(key=lambda x: x.atk)
    typedir.armor.sort(key=lambda x: x.defense)
    typedir.combos.sort(key=lambda x: x.defense+x.atk)

    typedir.healthy.sort(key=lambda x: int(x.usescript["itemheal"][0]))
    typedir.inspiring.sort(key=lambda x: int(x.usescript["itemheal"][1]))
    #typedir.other.sort(key=lambda x: x.price+x.sell)
    typedir.status.sort(key=lambda x: x.price+x.sell)

    return typedir
    

            
# printlog()
## Prints the global variable log to stdout
def printlog():
    global log
    if len(log) > 0:
        print '\n---------------------------------------'
    for line in log:
        print line


# print<>items(items, title)
## Creates the table in wikicode, depending on what kind of item is being printed

def getmoneystring(buy, sell):
    return '| align="right" | %d GP<br>%d gp\n' % (buy,sell)
def getidstring(id):
    return '| align="center" | [%d]\n' % id
    
def printhealitems(items,title):
    print '==%s==' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'
    # Print labels
    for title in health_titles:
        print '! style="background:#efdead;" | %s' % title
        
    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        print '| align="center" | %d' % i.usescript["itemheal"][0]
        print '| align="center" | %d' % i.usescript["itemheal"][1]
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| align="center!" | %d' % i.weight
        print '| %s' % i.description
    print '|}\n'
            
def printstatusitems(items,title):
    print '==%s==\n' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"\n'
    # Print labels
    for title in status_titles:
        print '! style="background:#efdead;" | %s' % title
        
    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        print '| align="center" | %s' % i.usescript["sc_start"][0]
        print '| align="center" | %s' % i.usescript["sc_start"][1]
        print '| align="center" | %s' % i.usescript["sc_start"][2]
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| align="center!" | %d' % i.weight
        print '| %s' % i.description
    print '|}\n'
            

def printweaponitems(items, title):
    print '==%s==\n' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"\n'
    # Print labels
    for title in weapon_titles:
        print '! style="background:#efdead;" | %s\n' % title

    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        print '| align="center" | %d (%d)' % (i.atk,i.range)
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| align="center!" | %d' % i.weight
        print '| %s' % i.description
    print '|}\n'
    
def printarmoritems(items, title):
    print '==%s==' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'
    print '! style="background:#efdead;" | Image'
    print '! style="background:#efdead;" | Name'
    print '! style="background:#efdead;" | ID'
    print '! style="background:#efdead;" | Defense'
    print '! style="background:#efdead;" | Price<br>BUY/Sell'
    print '! style="background:#efdead;" | Description'
    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        print '| align="center" | %d' % i.defense
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| %s' % i.description
    print '|}\n'

def printcomboitems(items, title):
    print '==%s==' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'
    print '! style="background:#efdead;" | Image'
    print '! style="background:#efdead;" | Name'
    print '! style="background:#efdead;" | ID'
    print '! style="background:#efdead;" | Damage<br>(Range)'
    print '! style="background:#efdead;" | Defense'
    print '! style="background:#efdead;" | Price<br>BUY/Sell'
    print '! style="background:#efdead;" | Description'
    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        print '| align="center" | %d (%d)' % (i.atk,i.range)
        print '| align="center" | %d' % i.defense
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| %s' % i.description
    print '|}\n'

def getpropertystring(item):
    s = ""
    s += "Weight: %d, " % item.weight
    s += "Slot: %d, " % item.slot
    s += "Gender: %d, " % item.gender
    s += "Loc: %d, " % item.loc
    s += "wLV: %d, " % item.wlv
    s += "eLV: %d, " % item.wlv
    s += "View: %d " % item.view
    return s


def printotheritems(items, title):
    print '==%s==' % title
    print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'
    print '! style="background:#efdead;" | Image'
    print '! style="background:#efdead;" | Name'
    print '! style="background:#efdead;" | ID'
    #print '! style="background:#efdead;" | Type'
    #print '! style="background:#efdead;" | Properties'
    print '! style="background:#efdead;" | Price<br>BUY/Sell'
    print '! style="background:#efdead;" | Description'
    for i in items:
        print '|-'
        print '| align="center" | %s' % i.imgurl
        #print '| %s' % i.jname.replace('_',' ')
        print '| %s' % i.clientname
        sys.stdout.write( getidstring(i.id) )
        #print '| align="center" | %d' % i.type
        #print '| align="center" | %s' % getpropertystring(i)
        sys.stdout.write( getmoneystring(i.price,i.sell) )
        print '| %s' % i.description
    print '|}\n'



def printunuseditems(title):
    ids = []
    if len(ids):
        print '==%s==' % title
        print '{| border="1" cellspacing="0" cellpadding="5" width="100%" align="center"'
        print '|',
        print '\n|}\n'

    

#####################################################################
#  MAIN
#####################################################################

try:
    if len(sys.argv) == 1:
        item_db = "item_db.txt"
        item_xml = "items.xml"
    elif len(sys.argv) == 3:
        item_db = sys.argv[1]
        item_xml = sys.argv[2]
    else: 
        item_db = ''
        item_xml = ''
        print "Wrong number of arguments"
    # Should be 3rd argument
    # image_path="" 

    if item_db and not os.path.isfile(item_db):
        print "File does not exist: %s" % item_db
        item_db = ''
    if item_xml and not os.path.isfile(item_xml):
        print "File does not exist: %s" % item_xml
        item_db = ''
    
    if not (item_db and item_xml):
        print "\nUSAGE:"
        print "dbtowiki without any arguments will use item_db.txt and items.xml in the current directory."
        print "to specify custom files, call: dbtowiki <item_db> <item_xml>"
        exit(-1);
    else:
        log.append("Item-list [item_db] = %s" % item_db)
        log.append("Item-list [item_xml] = %s" % item_xml)
        f = open(item_db)
        items = parseitems(f);
        f = open(item_xml)
        citems = parsexmlitems(f);

        addclientinformation(items, citems)

        typedir = gettypedir(items)

        if len(typedir.healthy) > 0: printhealitems(typedir.healthy, "Health")
        if len(typedir.status) > 0: printstatusitems(typedir.status, "Status")
        if len(typedir.inspiring) > 0: printhealitems(typedir.inspiring, "Mana")
        if len(typedir.weapons) > 0: printweaponitems(typedir.weapons, "Weapons")
        if len(typedir.armor) > 0: printarmoritems(typedir.armor, "Armor")
        if len(typedir.combos) > 0: printcomboitems(typedir.combos, "Combos")
        if len(typedir.other) > 0: printotheritems(typedir.other, "Other")

        print "\n"

finally:
    printlog()
