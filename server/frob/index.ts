// this script removes specified items from inventories and storage
import { SQLHandler } from "./sql.ts";
import { ManaMarketHandler } from "./manamarket.ts";
import { LoginParser, LoginSQL } from "./login.ts";
import { CharParser, CharWriter, CharSQL } from "./char.ts";
import { AccregParser, AccregSQL } from "./accreg.ts";
import { PartyParser, PartySQL } from "./party.ts";
import { StorageParser, StorageWriter, StorageSQL } from "./storage.ts";
import { ItemDB } from "./itemdb.ts";

const args: string[] = Deno.args.slice(1);
const to_remove: Set<number> = new Set();
const sql = new SQLHandler();
const manamarket = new ManaMarketHandler();
const login_parser = new LoginParser();
const char_parser = new CharParser();
const accreg_parser = new AccregParser();
const party_parser = new PartyParser();
const storage_parser = new StorageParser();
const char_writer = new CharWriter();
const char_SQL = new CharSQL(sql);
const login_SQL = new LoginSQL(sql);
const accreg_SQL = new AccregSQL(sql);
const party_SQL = new PartySQL(sql);
const storage_writer = new StorageWriter();
const storage_SQL = new StorageSQL(sql);
const item_db = new ItemDB();

// at which value an item is considered SSR
const rare_threshold = 3000000;
const hoarders: Map<number, any> = new Map();

const stats = {
    inventory: {
        removed: 0,
        pruned: 0,
        stub: 0,
        chars: 0,
    },
    storage: {
        removed: 0,
        pruned: 0,
        stub: 0,
        wiped: 0,
        synced: 0,
        accounts: 0,
    },
};

const flags = {
    dry_run: false,
    sql: false,
    stats: false,
};


(async () => {
    const items_by_id = new Map(); // holds full item info
    const items_by_name = new Map(); // holds references to the former

    // TODO: split the hoarder stuff into hoarders.ts
    const getHoarder = (account_id: number) => {
        let hoarder = hoarders.get(account_id);

        if (!hoarder) {
            hoarder = hoarders.set(account_id, {
                value: {
                    items: 0,
                    //gp: 0,
                },
                storage: {},
                inventories: {},
            }).get(account_id);
        }

        return hoarder;
    };

    const maybeAddToHoarders = (account_id: number, char_name: string, char_id: number, item: number, qty: number = 1) => {
        // make sure all values are the expected format (Deno is weird sometimes)
        [account_id, char_id, item, qty] = [+account_id, +char_id, +item, +qty];

        const data = manamarket.items.get(item);
        let value = data ? data.averageValue.overall : 0;

        if (value < rare_threshold) {
            return;
        }

        const hoarder = getHoarder(account_id);

        item = (items_by_id.get(item)).name;

        if (char_id && char_name) {
            if (!Reflect.has(hoarder.inventories, char_name)) {
                hoarder.inventories[char_name] = new Map();
            }

            const had = hoarder.inventories[char_name][item] || 0;
            hoarder.inventories[char_name][item] = had + qty;
        } else {
            const had = hoarder.storage[item] || 0;
            hoarder.storage[item] = had + qty;
        }

        hoarder.value.items += value;
    };

    for await (let item of item_db.readDB()) {
        items_by_id.set(+item.id, item);
        items_by_name.set(item.name, +item.id);
    }

    const itemToNumber = (name: string|number): number => {
        if (isNaN(name as number)) {
            const item_id = items_by_name.get(name);

            if (item_id) {
                return +item_id;
            } else {
                console.error(`cannot find item '${name}' in the item db`);
                throw new Error("item not found");
            }
        } else {
            return +name;
        }
    }

    const itemToString = (id: string|number): string => {
        if (isNaN(id as number)) {
            return `${id}`;
        } else {
            const item = items_by_id.get(+id);

            if (item) {
                return item.name;
            } else {
                console.error(`cannot find item ID ${id} in the item db`);
                throw new Error("item not found");
            }
        }
    }

    if (args.length < 1) {
        throw new RangeError("no items given!");
    }

    // flag parsing
    for (const opt of args.slice()) {
        if (opt.startsWith("--")) {
            switch (opt.slice(2)) {
            case "dry":
            case "dry-run":
                flags.dry_run = true;
                break;
            case "dump":
            case "sql":
                flags.sql = true;
                break;
            case "stats":
                flags.stats = true;
                break;
            case "clean":
            case "clean-only":
                break;
            default:
                throw new SyntaxError(`unknown flag: ${opt}`);
            }

            args.shift();
        } else {
            break; // no more flags
        }
    }

    // item parsing
    for (let arg of args.join(",").split(",")) {
        if (arg === null || arg.length < 1)
            continue;

        if (arg.includes("-") || arg.includes("..")) {
            const range = arg.split("-").join("..").split("..");
            let from = itemToNumber(range[0]), to = itemToNumber(range[1]);

            if (from > to) {
                [from, to] = [to, from];
            }

            for (let i = from; i <= to; ++i) {
                to_remove.add(i);
            }
        } else {
            to_remove.add(itemToNumber(arg));
        }
    }

    if (to_remove.size > 0) {
        console.info("\nThe following items will be removed:");
        for (let item of to_remove) {
            console.info(`[${item}]: ${itemToString(item)}`);
        }
    }

    if (flags.sql) {
        console.log("");
        await sql.init();
    }

    if (flags.stats) {
        console.log("");
        await manamarket.init();
    }

    console.log("");

    // account:
    if (flags.sql) {
        for await (const acc of login_parser.readDB()) {
            if (acc === null
                || acc.logincount < 1 // don't keeep accounts that never logged in
                || +acc.state === 5 // don't keep permabanned accounts
                ) {
                continue;
            }
            await login_SQL.write(acc);
        }
    }

    if (!flags.dry_run) {
        char_writer.init();
    }

    // inventory:
    for await (let char of char_parser.readDB()) {
        let items_filtered = []; // this is not a Set because some items don't stack
        let mod = false;

        for (let item of char.items) {
            if (!items_by_id.has(+item.nameid)) {
                console.log(`\rremoving ${+item.amount || 1}x non-existant item ID ${item.nameid} from inventory of character ${char.name} [${char.account_id}:${char.char_id}]`);
                stats.inventory.pruned += +item.amount;
                mod = true;
            } else if (+item.amount < 1) {
                console.log(`\rremoving stub of item ${itemToString(item.nameid)} [${item.nameid}] from inventory of character ${char.name} [${char.account_id}:${char.char_id}]`);
                stats.inventory.stub++;
                mod = true;
            } else if (to_remove.has(+item.nameid)) {
                console.log(`\rremoving ${item.amount}x ${itemToString(item.nameid)} [${item.nameid}] from inventory of character ${char.name} [${char.account_id}:${char.char_id}]`);
                stats.inventory.removed += +item.amount;
                mod = true;
            } else {
                items_filtered.push(item);
            }

            if (flags.stats) {
                maybeAddToHoarders(+char.account_id, char.name, +char.char_id, +item.nameid, +item.amount || 1);
            }
        }

        if (mod)
            stats.inventory.chars++;

        char.items = items_filtered;
        await char_writer.write(char);

        if (flags.sql)
            await char_SQL.write(char);
    }

    await char_writer.finalize();

    // char-server-bound account variables
    if (flags.sql) {
        for await (const acc of accreg_parser.readDB()) {
            await accreg_SQL.write(acc);
        }
    }

    // party and party leaders
    if (flags.sql) {
        for await (const party of party_parser.readDB()) {
            await party_SQL.write(party);
        }
    }

    if (!flags.dry_run) {
        storage_writer.init();
    }

    // storage:
    for await (let storage of storage_parser.readDB()) {
        let items_filtered = []; // this is not a Set because some items don't stack
        let mod = false;

        for (let item of storage.items) {
            if (!items_by_id.has(+item.nameid)) {
                console.log(`\rremoving ${+item.amount || 1}x non-existant item ID ${item.nameid} from storage of account ${storage.account_id}`);
                stats.storage.pruned += +item.amount;
                storage.storage_amount--;
                mod = true;
            } else if (+item.amount < 1) {
                console.log(`\rremoving stub of item ${itemToString(item.nameid)} [${item.nameid}] from storage of account ${storage.account_id}`);
                stats.storage.stub++;
                storage.storage_amount--;
                mod = true;
            } else if (to_remove.has(+item.nameid)) {
                console.log(`\rremoving ${item.amount}x ${itemToString(item.nameid)} [${item.nameid}] from storage of account ${storage.account_id}`);
                stats.storage.removed += +item.amount;
                storage.storage_amount--;
                mod = true;
            } else {
                items_filtered.push(item);
            }

            if (flags.stats) {
                maybeAddToHoarders(+storage.account_id, "", 0, +item.nameid, +item.amount || 1);
            }
        }

        if (mod)
            stats.storage.accounts++;

        storage.items = items_filtered;

        if (+storage.storage_amount !== storage.items.length) {
            const old_sync = +storage.storage_amount;
            storage.storage_amount = storage.items.length;
            console.log(`fixing sync of storage for account ${storage.account_id}: ${old_sync} => ${storage.storage_amount}`);
            stats.storage.synced++;
        }

        if (storage.storage_amount >= 1) {
            await storage_writer.write(storage);

            if (flags.sql) {
                await storage_SQL.write(storage);
            }
        } else {
            console.log(`storage of account ${storage.account_id} is now empty: removing it from the storage db`);
            stats.storage.wiped++;
        }
    }

    await storage_writer.finalize();
    await sql.close();

    if (flags.stats) {
        function partition(all: any[], left: number, right: number) {
            var pivot   = all[Math.floor((right + left) / 2)], //middle element
                i       = left, //left pointer
                j       = right; //right pointer
            while (i <= j) {
                while (all[i][1].value.items < pivot[1].value.items) {
                    i++;
                }
                while (all[j][1].value.items > pivot[1].value.items) {
                    j--;
                }
                if (i <= j) {
                    [all[i], all[j]] = [all[j], all[i]]; // swap them
                    i++;
                    j--;
                }
            }
            return i;
        }

        function quickSort(all: any[], left: number, right: number) {
            if (all.length > 1) {
                const index = partition(all, left, right); //index returned from partition
                if (left < index - 1) { //more elements on the left side of the pivot
                    quickSort(all, left, index - 1);
                }
                if (index < right) { //more elements on the right side of the pivot
                    quickSort(all, index, right);
                }
            }
            return all;
        }

        console.log("Sorting hoarders...");
        const entries = Array.from(hoarders.entries());
        const sorted = quickSort(entries, 0, entries.length - 1).reverse();
        const json = JSON.stringify(sorted, null, "\t");
        const encoder = new TextEncoder();

        console.log("Writing hoarders.json...");
        await Deno.mkdir("log", {recursive: true});
        await Deno.writeTextFile("log/hoarders.json", json);
    }

    console.info("\r                                                            \n=== all done ===");
    console.info(`removed ${stats.inventory.removed} existant, ${stats.inventory.pruned} non-existant and ${stats.inventory.stub} stub items from the inventory of ${stats.inventory.chars} characters`);
    console.info(`removed ${stats.storage.removed} existant, ${stats.storage.pruned} non-existant and ${stats.storage.stub} stub items from the storage of ${stats.storage.accounts} accounts`);
    console.info(`removed ${stats.storage.wiped} empty storage entries from the storage db`);
    console.info(`fixed storage sync of ${stats.storage.synced} accounts`);

    if (flags.dry_run) {
        console.warn("(DRY RUN) no file modified");
    }

    Deno.exit(0);
})()
