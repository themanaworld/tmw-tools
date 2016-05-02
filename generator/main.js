var fs = require("fs"),
    parse = require("xml-parser"),
    conf = require("./conf.json"),
    mob = require("./monsters"),
    item = require("./items");

function onReadFile(err, raw){
    if (err) throw err;
    var data = parse(raw).root.children;
    data.forEach(function(element, index){
        switch(element.name){
            case "include":
                fs.readFile(conf.dir + element.attributes.name,
                            {encoding:"utf8"}, onReadFile);
                break;
            case "monster":
                mob.parse(element);
                break;
            case "item":
                item.parse(element);
                break;
            default:
                throw "Unknown xml element: " + element.name;
        }
    });
}

mob.emitter.on("converted",function(data){
    console.log(">> Converted mob "+data.id+ " (" +data.name+ ") from xml");
    var values = Object.keys(data).map(function(a){return data[a]});
    fs.appendFileSync(conf.dbs + conf.monsters.db, values.join()+"\n", {encoding:"utf8"});
    console.log("<< Saved     mob "+data.id+ " (" +data.name+ ") in database");
});

function processMobs(){
    console.log("|| Emptying the mob db.");
    fs.writeFileSync(conf.dbs + conf.monsters.db, "", {encoding:"utf8"});
    console.log("|| Generating mobs from xml.");
    fs.readFile(conf.dir + conf.monsters.xml, {encoding:"utf8"}, onReadFile);
}

(function(){
    "use strict";
    if(process.cwd().search(/tmwa-server-data$/) < 0)
        throw "This script must be run from the root of tmwa-server-data";
    processMobs();
})();
