class StorageParser {
    private storage_line =
    "^" +
    "(?<account_id>[0-9]+),(?<storage_amount>[0-9]+)\t" +
    "(?<items>([0-9]+,(?<nameid>[0-9]+),(?<amount>[0-9]+),(?<equip>[0-9]+),[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+ )+)\t$";
    private storage_items_line = "[0-9]+,(?<nameid>[0-9]+),(?<amount>[0-9]+),(?<equip>[0-9]+),[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+ ";
    private storage_regex: RegExp;
    private storage_regex_items: RegExp;

    constructor () {
        this.storage_regex = new RegExp(this.storage_line);
        this.storage_regex_items = new RegExp(this.storage_items_line, "g");
    }

    private parseLine (line: string) {
        const match = this.storage_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("line does not match the storage regex:", line);
            throw new SyntaxError();
        }

        const groups = (match as any).groups;
        let items = [];

        if (groups.items.length > 1) {
            let match_items = this.storage_regex_items.exec(groups.items);

            while (match_items !== null) {
                items.push((match_items as any).groups);
                match_items = this.storage_regex_items.exec(groups.items);
            }
        }

        groups.items = items;
        return groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("\nwalking through storage.txt...");
        const file = await Deno.open("world/save/storage.txt");
        const buf = new Uint8Array(1024);
        let accumulator = "";

        while (true) {
            const nread = await Deno.read(file.rid, buf);

            if (nread === Deno.EOF) {
                break;
            }

            const str = decoder.decode(buf);

            if (nread < 1024) {
                for (let c of str) {
                    if (c === "\n") {
                        yield this.parseLine(accumulator);
                        break;
                    } else {
                        accumulator += c;
                    }
                }
                break;
            }

            for (let c of str) {
                if (c === "\n") {
                    yield this.parseLine(accumulator);
                    accumulator = "";
                } else {
                    accumulator += c;
                }
            }
        }
    }
}

class StorageWriter {
    private file;
    private encoder;

    constructor () {
        try {
            Deno.removeSync("world/save/storage.txt.tmp");
        } catch {
            // ignore this
        }
        this.file = Deno.openSync("world/save/storage.txt.tmp", "a+");
        this.encoder = new TextEncoder();
    }

    async write (storage: any) {
        let line = `${storage.account_id},${storage.storage_amount}\t`;

        for (let item of storage.items) {
            line += `0,${item.nameid},${item.amount},${item.equip},0,0,0,0,0,0,0 `;
        }

        line += `\t`; // end of items
        line += `\n`;

        await Deno.write(this.file.rid, this.encoder.encode(line));
    }

    async finalize() {
        this.file.close();
        console.info("overwriting storage.txt...");
        await Deno.rename("world/save/storage.txt", "world/save/storage.txt_pre-frob");
        await Deno.rename("world/save/storage.txt.tmp", "world/save/storage.txt");
    }
}

export {
    StorageParser,
    StorageWriter,
}
