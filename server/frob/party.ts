class PartyParser {
    private party_line =
    "^" +
    "(?<party_id>[0-9]+)\t" +
    "(?<name>[^\t]*)\t" + // bug: name can be empty
    "(?<exp_share>[01]),(?<item_share>(?:[01]|65535))\t" + // bug: item share can be 0xFFFF
    "(?<members>((?<account_id>[0-9]+),(?<leader>[01])\t(?<char_name>[^\t]+)\t)*)" +
    "$";
    private member_line = "(?<account_id>[0-9]+),(?<leader>[01])\t(?<char_name>[^\t]+)\t";
    private party_regex: RegExp;
    private party_regex_members: RegExp;
    private encoder;

    constructor () {
        this.party_regex = new RegExp(this.party_line);
        this.party_regex_members = new RegExp(this.member_line, "g");
        this.encoder = new TextEncoder();
    }

    private parseLine (line: string) {
        const match = this.party_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("\nline does not match the regex:", line);
            throw new SyntaxError();
        }

        const groups = (match as any).groups;
        let members = [];

        if (groups.members.length > 1) {
            let match_members = this.party_regex_members.exec(groups.members);

            while (match_members !== null) {
                members.push((match_members as any).groups);
                match_members = this.party_regex_members.exec(groups.members);
            }
        }

        if (+groups.item_share === 65535) {
            groups.item_share = 1; // old bug that was fixed in tmwa but not in the db
        }

        groups.members = members;

        if (groups.name.length == 0) {
            console.warn(`\rdiscarding party ${groups.party_id}: no name                      `);
            return null;
        } else if (groups.members.length == 0) {
            console.warn(`\rdiscarding party ${groups.party_id}: no members                   `);
            return null;
        }

        Deno.write(Deno.stdout.rid, this.encoder.encode(`\r⌛ processing members of party ${groups.party_id}...`));
        return groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("\r                                                          \nwalking through party.txt...");
        const file = await Deno.open("world/save/party.txt");
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

class PartySQL {
    private sql;

    constructor (sql) {
        this.sql = sql;
    }

    async write (party: any) {
        if (party === null)
            return Promise.resolve(false); // we cannot handle duplicate parties

        party.name = this.sql.escape(party.name);

        await this.sql.do("INSERT INTO `party` ?? values?", [
            ["party_id", "name", "exp_share", "item_share"],
            [party.party_id, party.name, +party.exp_share, +party.item_share]
        ]);

        for (const member of party.members) {
            await this.sql.do("UPDATE `char` SET ?? = ? WHERE ?? = ? AND ?? = ?", [
                    "party_isleader", +member.leader,
                    "party_id", +party.party_id,
                    "account_id", +member.account_id ]);
        }
    }
}

export {
    PartyParser,
    PartySQL,
}
