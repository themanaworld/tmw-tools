import { SQLHandler } from "./sql.ts";

class AccregParser {
    private reg_line =
    "^" +
    "(?<account_id>[0-9]+)\t" +
    "(?<variables>((?<var_name>[^,]+),(?<value>[-0-9]+) )*)" + // some chars have negative variables (overflows)
    "$";
    private vars_line = "(?<var_name>[^,]+),(?<value>[-0-9]+) ";
    private reg_regex: RegExp;
    private reg_regex_vars: RegExp;
    private encoder: TextEncoder;

    constructor () {
        this.reg_regex = new RegExp(this.reg_line);
        this.reg_regex_vars = new RegExp(this.vars_line, "g");
        this.encoder = new TextEncoder();
    }

    private parseLine (line: string) {
        const match = this.reg_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("\nline does not match the reg regex:", line);
            throw new SyntaxError();
        }

        const groups = (match as any).groups;
        let variables = [];

        if (groups.variables.length > 1) {
            let match_vars = this.reg_regex_vars.exec(groups.variables);

            while (match_vars !== null) {
                variables.push((match_vars as any).groups);
                match_vars = this.reg_regex_vars.exec(groups.variables);
            }
        }

        groups.variables = variables;

        Deno.write(Deno.stdout.rid, this.encoder.encode(`\r⌛ processing variables of account ${groups.account_id}...`));
        return groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("\r                                                          \nwalking through accreg.txt...");
        const file = await Deno.open("world/save/accreg.txt");
        const buf = new Uint8Array(1024);
        let accumulator = "";

        while (true) {
            const nread = await Deno.read(file.rid, buf);

            if (nread === null) {
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

class AccregSQL {
    private sql: SQLHandler;

    constructor (sql: SQLHandler) {
        this.sql = sql;
    }

    async write (acc: any) {
        for (const variable of acc.variables) {
            await this.sql.do("INSERT INTO `acc_reg` ?? values?", [
                ["account_id", "name", "value"],
                [acc.account_id, variable.var_name, variable.value]
            ]);
        }
    }
}

export {
    AccregParser,
    AccregSQL,
}
