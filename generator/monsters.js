var Mob = function(id, name){
    // WARNING: the properties need to be in the same order as in the mob db
    this.id = id;
    this.name = name;
    this.jname = this.name;
    this.lv = 0;
    this.hp = 1;
    this.sp = 0;
    this.exp = 0;
    this.jexp = 0;
    this.range1 = 1;
    this.atk1 = 0;
    this.atk2 = 0;
    this.def = 0;
    this.mdef = 0;
    this.str = 0;
    this.agi = 0;
    this.vit = 0;
    this.int = 0;
    this.dex = 0;
    this.luk = 0;
    this.range2 = 1; //unused
    this.range3 = 1; //unused
    this.scale = 1; // unused
    this.race = 0; // unused
    this.element = 0; // check ?
    this.mode = 0;
    this.speed = 1;
    this.adelay = 0;
    this.amotion = 0; // check ?
    this.dmotion = 0; // check ?
    this.drop1id = 0;
    this.drop1per = 0;
    this.drop2id = 0;
    this.drop2per = 0;
    this.drop3id = 0;
    this.drop3per = 0;
    this.drop4id = 0;
    this.drop4per = 0;
    this.drop5id = 0;
    this.drop5per = 0;
    this.drop6id = 0;
    this.drop6per = 0;
    this.drop7id = 0;
    this.drop7per = 0;
    this.drop8id = 0;
    this.drop8per = 0;
    this.item1 = 0; // unused
    this.item2 = 0; // unused
    this.mexp = 0; // unused
    this.expper = 0; // unused
    this.mvp1id = 0; // unused
    this.mvp1per = 0; // unused
    this.mvp2id = 0; // unused
    this.mvp2per = 0; // unused
    this.mvp3id = 0; // unused
    this.mvp3per = 0; // unused
    this.mutcount = 0;
    this.mutstr = 0;
    Object.seal(this); // lock it
}

function parseBuild(mob, child){
    var a = child.attributes;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "level":
                mob.lv = parseInt(a.level);
                break;
            case "element":
                mob.element = parseInt(a.element);
                break;
            case "mode":
                mob.mode = parseInt(a.mode);
                break;
            case "speed":
                mob.speed = parseInt(a.speed);
                break;
            case "hp":
                mob.hp = parseInt(a.hp);
                break;
            case "sp":
                mob.sp = parseInt(a.sp);
                break;
            default:
                throw "Unknown property of build: "+ key;
        }
    });
}

function parseStats(mob, child){
    var a = child.attributes;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "str":
                mob.str = parseInt(a.str);
                break;
            case "agi":
                mob.agi = parseInt(a.agi);
                break;
            case "vit":
                mob.vit = parseInt(a.vit);
                break;
            case "int":
                mob.int = parseInt(a.int);
                break;
            case "dex":
                mob.dex = parseInt(a.dex);
                break;
            case "luk":
                mob.luk = parseInt(a.luk);
                break;
            default:
                throw "Unknown property of stats: "+ key;
        }
    });
}

function parseMutation(mob, child){
    var a = child.attributes;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "count":
                mob.mutcount = parseInt(a.count);
                break;
            case "strength":
                mob.mutstr = parseInt(a.strength);
                break;
            default:
                throw "Unknown property of mutation: "+ key;
        }
    });
}

function parseAttack(mob, child){
    var a = child.attributes;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "min":
                mob.atk1 = parseInt(a.min);
                break;
            case "max":
                mob.atk2 = parseInt(a.max);
                break;
            case "range":
                mob.range1 = parseInt(a.range);
                break;
            case "delay":
                mob.adelay = parseInt(a.delay);
                break;
            default:
                throw "Unknown property of attack: "+ key;
        }
    });
}

function parseDefense(mob, child){
    var a = child.attributes;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "physical":
                mob.def = parseInt(a.physical);
                break;
            case "magical":
                mob.mdef = parseInt(a.magical);
                break;
            default:
                throw "Unknown property of defense: "+ key;
        }
    });
}

function parseKill(mob, child){
    function parseKillDrop(mob, drop, drops){
        var c = drop.attributes;
        Object.keys(c).forEach(function(k){
            switch(k){
                case "item":
                    mob["drop"+drops+"id"] = parseInt(c.item);
                    break;
                case "percent":
                    var percent = (parseFloat(c.percent) * 100);
                    if(percent < 1 || percent > 10000)
                        throw "Invalid drop percentage";
                    mob["drop"+drops+"per"] = percent;
                    break;
                default:
                    throw "Unknown property of kill drop: "+ key;
            }
        });
    }

    var a = child.attributes, drops = 0;
    Object.keys(a).forEach(function(key){
        switch(key){
            case "exp":
                mob.exp = parseInt(a.exp);
                break;
            case "job":
                mob.jexp = parseInt(a.job);
                break;
            default:
                throw "Unknown property of kill: "+ key;
        }
    });
    child.children.forEach(function(drop){
        if(drop.name == "drop"){
            drops++;
            if(drops > 8)
                throw "Too many drops";
            parseKillDrop(mob, drop, drops);
        }
        else{
            throw "Unknown tag of kill: "+ drop;
        }
    });
}

function parse(e){
    if(!e.attributes.hasOwnProperty("short")) return;
    var id = parseInt(e.attributes.id);
    var name = e.attributes.short;
    if(id < 1000 || id > 5000) throw "Invalid mob id: " + id;
    if(name == undefined || name == null || name == "") throw "Invalid mob name: " + name;
    var mob = new Mob(id, name);

    e.children.forEach(function(child, index){
        switch(child.name){
            case "build":
                parseBuild(mob, child);
                break;
            case "stats":
                parseStats(mob, child);
                break;
            case "mutation":
                parseMutation(mob, child);
                break;
            case "attack":
                parseAttack(mob, child);
                break;
            case "defense":
                parseDefense(mob, child);
                break;
            case "kill":
                parseKill(mob, child);
                break;
            case "sprite":
            case "sound": // silently ignore those
                break;
            default:
                console.log("unknown tag: "+child.name);
        }
    });
    module.exports.emitter.emit("converted", mob);
    return;
}

module.exports.emitter = new (require('events').EventEmitter)();
module.exports.parse = parse;
