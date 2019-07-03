class ItemDB {
    private item_line =
    "^" +
    "(?<id>[0-9]+),[ \t]*" +
    "(?<name>[^ \t,]+),[ \t]*" +
    "(?<type>[0-9]+),[ \t]*" +
    "(?<price>[0-9]+),[ \t]*" +
    "(?<sell>[0-9]+),[ \t]*" +
    "(?<weight>[0-9]+),[ \t]*" +
    "(?<atk>[0-9]+),[ \t]*" +
    "(?<def>[0-9]+),[ \t]*" +
    "(?<range>[0-9]+),[ \t]*" +
    "(?<mbonus>[0-9-]+),[ \t]*" +
    "(?<slot>[0-9]+),[ \t]*" +
    "(?<gender>[0-9]+),[ \t]*" +
    "(?<loc>[0-9]+),[ \t]*" +
    "(?<wlvl>[0-9]+),[ \t]*" +
    "(?<elvl>[0-9]+),[ \t]*" +
    "(?<view>[0-9]+),[ \t]*" +
    "\{(?<usescript>[^\}]*)\},[ \t]*" +
    "\{(?<equipscript>[^\}]*)\}[ \t]*" +
    "$";
    private item_regex: RegExp;

    constructor () {
        this.item_regex = new RegExp(this.item_line);
    }

    private parseLine (line) {
        const match = this.item_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("line does not match the item db regex:", line);
            throw new SyntaxError();
        }

        return (match as any).groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("reading tmwa-map.conf...");
        const file = await Deno.readFile("world/map/conf/tmwa-map.conf");
        const data = decoder.decode(file).split("\n");
        const db_regex = new RegExp("^item_db: *(?<path>[A-Za-z0-9_\./]+)$");

        for (const line of data) {
            const match = db_regex.exec(line);
            if (!(match instanceof Object)) continue;
            const path = (match as any).groups.path;

            console.info(`reading world/map/${path}...`)
            const db = await Deno.readFile(`world/map/${path}`);

            for (const item of decoder.decode(db).split("\n")) {
                if (item.startsWith("//") || item.length < 2) {
                    continue;
                }

                yield this.parseLine(item);
            }
        }
    }
}

export {
    ItemDB
}
