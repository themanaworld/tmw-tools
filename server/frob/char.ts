import { SQLHandler } from "./sql.ts";

class CharParser {
    private char_line =
    "^" +
    "(?<char_id>[0-9]+)\t" +
    "(?<account_id>[0-9]+),(?<char_num>[0-9]+)\t" +
    "(?<name>[^\t]+)\t" +
    "(?<species>[0-9]+),(?<base_level>[0-9]+),(?<job_level>[0-9]+)\t" +
    "(?<base_exp>[0-9]+),(?<job_exp>[0-9]+),(?<zeny>[0-9]+)\t" +
    "(?<hp>[0-9]+),(?<max_hp>[0-9]+),(?<sp>[0-9]+),(?<max_sp>[0-9]+)\t" +
    "(?<str>[0-9]+),(?<agi>[0-9]+),(?<vit>[0-9]+),(?<int>[0-9]+),(?<dex>[0-9]+),(?<luk>[0-9]+)\t" +
    "(?<status_point>[0-9]+),(?<skill_point>[0-9]+)\t" +
    "(?<option>[0-9]+),(?<karma>[0-9]+),(?<manner>[0-9]+)\t" +
    "(?<party_id>[0-9]+),[0-9]+,[0-9]+\t" +
    "(?<hair>[0-9]+),(?<hair_color>[0-9]+),(?<clothes_color>[0-9]+)\t" +
    "(?<weapon>[0-9]+),(?<shield>[0-9]+),(?<head_top>[0-9]+),(?<head_mid>[0-9]+),(?<head_bottom>[0-9]+)\t" +
    "(?<last_map>[^,]+),(?<last_x>[0-9]+),(?<last_y>[0-9]+)\t" +
    "(?<save_map>[^,]+),(?<save_x>[0-9]+),(?<save_y>[0-9]+),(?<partner_id>[0-9]+)\t" +
    "(?<sex>[FMNS])\t" + // <= ignore S to ignore server accounts
    "(?<items>([0-9]+,(?<nameid>[0-9]+),(?<amount>[0-9]+),(?<equip>[0-9]+),[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+ )*)\t" + // inventory
    "\t" + // cart
    "(?<skills>((?<skill_id>[0-9]+),(?<skill_lv>[0-9]+) )*)\t" +
    "(?<variables>((?<var_name>[^,]+),(?<value>[-0-9]+) )*)\t" + // some chars have negative variables (overflows)
    "$";
    private char_items_line = "[0-9]+,(?<nameid>[0-9]+),(?<amount>[0-9]+),(?<equip>[0-9]+),[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+ ";
    private char_skills_line = "(?<skill_id>[0-9]+),(?<skill_lv>[0-9]+) ";
    private char_vars_line = "(?<var_name>[^,]+),(?<value>[-0-9]+) ";
    private char_regex: RegExp;
    private char_regex_items: RegExp;
    private char_regex_skills: RegExp;
    private char_regex_vars: RegExp;
    private encoder: TextEncoder;

    constructor () {
        this.char_regex = new RegExp(this.char_line);
        this.char_regex_items = new RegExp(this.char_items_line, "g");
        this.char_regex_skills = new RegExp(this.char_skills_line, "g");
        this.char_regex_vars = new RegExp(this.char_vars_line, "g");
        this.encoder = new TextEncoder();
    }

    private parseLine (line: string) {
        const match = this.char_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("line does not match the char regex:", line);
            throw new SyntaxError();
        }

        const groups = (match as any).groups;
        let items = [];
        let skills = [];
        let variables = [];

        if (groups.items.length > 1) {
            let match_items = this.char_regex_items.exec(groups.items);

            while (match_items !== null) {
                items.push((match_items as any).groups);
                match_items = this.char_regex_items.exec(groups.items);
            }
        }

        groups.items = items;

        if (groups.skills.length > 1) {
            let match_skills = this.char_regex_skills.exec(groups.skills);

            while (match_skills !== null) {
                skills.push((match_skills as any).groups);
                match_skills = this.char_regex_skills.exec(groups.skills);
            }
        }

        groups.skills2 = skills;

        if (groups.variables.length > 1) {
            let match_vars = this.char_regex_vars.exec(groups.variables);

            while (match_vars !== null) {
                variables.push((match_vars as any).groups);
                match_vars = this.char_regex_vars.exec(groups.variables);
            }
        }

        groups.variables2 = variables;

        Deno.write(Deno.stdout.rid, this.encoder.encode(`\r                                                          \r⌛ processing char ${groups.char_id}...`));
        return groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("\r                                                          \nwalking through athena.txt...");
        const file = await Deno.open("world/save/athena.txt");
        const buf = new Uint8Array(1024);
        let accumulator = "";

        while (true) {
            const nread = await Deno.read(file.rid, buf);

            if (nread === null) {
                break;
            }

            const str = decoder.decode(buf);

            for (let c of str) {
                if (c === "\n") {
                    if (accumulator.length === 14) {
                        // this is the newid line
                        break;
                    }
                    yield this.parseLine(accumulator);
                    accumulator = "";
                } else {
                    accumulator += c;
                }
            }
        }
    }
}

class CharWriter {
    private file?: Deno.File;
    private highest: number = 0;
    private encoder: TextEncoder;

    constructor () {
        this.encoder = new TextEncoder();
    }

    async init () {
        try {
            await Deno.remove("world/save/athena.txt.tmp");
        } catch {
            // ignore this
        }
        this.file = await Deno.open("world/save/athena.txt.tmp", {append: true, create: true});
    }

    async write (char: any) {
        if (!this.file) {
            return;
        }

        let line =
        `${char.char_id}\t` +
        `${char.account_id},${char.char_num}\t` +
        `${char.name}\t` +
        `${char.species},${char.base_level},${char.job_level}\t` +
        `${char.base_exp},${char.job_exp},${char.zeny}\t` +
        `${char.hp},${char.max_hp},${char.sp},${char.max_sp}\t` +
        `${char.str},${char.agi},${char.vit},${char.int},${char.dex},${char.luk}\t` +
        `${char.status_point},${char.skill_point}\t` +
        `${char.option},${char.karma},${char.manner}\t` +
        `${char.party_id},0,0\t` +
        `${char.hair},${char.hair_color},${char.clothes_color}\t` +
        `${char.weapon},${char.shield},${char.head_top},${char.head_mid},${char.head_bottom}\t` +
        `${char.last_map},${char.last_x},${char.last_y}\t` +
        `${char.save_map},${char.save_x},${char.save_y},${char.partner_id}\t` +
        `${char.sex}\t`;

        for (let item of char.items) {
            line += `0,${item.nameid},${item.amount},${item.equip},1,0,0,0,0,0,0,0 `;
        }

        line += `\t`; // end of items
        line += `\t`; // cart
        line += `${char.skills}\t`;
        line += `${char.variables}\t`;
        line += `\n`;

        await Deno.write(this.file.rid, this.encoder.encode(line));

        if (+char.char_id > this.highest) {
            this.highest = +char.char_id;
        }
    }

    async finalize () {
        console.info("\rappending %newid%...                                                     ");

        if (!this.file) {
            return;
        }

        await Deno.write(this.file.rid, this.encoder.encode(`${this.highest + 1}\t%newid%\n`));
        this.file.close();

        console.info("overwriting athena.txt...");
        await Deno.rename("world/save/athena.txt", "world/save/athena.txt_pre-frob");
        await Deno.rename("world/save/athena.txt.tmp", "world/save/athena.txt");
    }
}

class CharSQL {
    private sql: SQLHandler;

    constructor (sql: SQLHandler) {
        this.sql = sql;
    }

    async write (char: any) {
        char.name = this.sql.escape(char.name);
        await this.sql.do("INSERT INTO `char` ?? values?", [
            ["char_id","account_id","char_num","name","class","base_level","job_level","base_exp","job_exp","zeny","str","agi","vit","int","dex","luk","status_point","skill_point","party_id","hair","hair_color","partner_id","sex"],
            [char.char_id,char.account_id,char.char_num,char.name,char.species,char.base_level,char.job_level,char.base_exp,char.job_exp,char.zeny,char.str,char.agi,char.vit,char.int,char.dex,char.luk,char.status_point,char.skill_point,char.party_id,char.hair,char.hair_color,char.partner_id,char.sex],
        ]);

        for (const item of char.items) {
            await this.sql.do("INSERT INTO `inventory` ?? values?", [
                ["char_id", "nameid", "amount", "equip"],
                [char.char_id, item.nameid, item.amount, item.equip]
            ]);
        }

        for (const variable of char.variables2) {
            // those are always char variables since acc vars are in accreg.txt
            await this.sql.do("INSERT INTO `char_reg` ?? values?", [
                ["char_id", "name", "value"],
                [char.char_id, variable.var_name, variable.value]
            ]);
        }
    }
}

export {
    CharParser,
    CharWriter,
    CharSQL,
}
