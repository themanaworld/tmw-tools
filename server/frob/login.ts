class LoginParser {
    private login_line =
    "^" +
    "(?<account_id>[0-9]+)\t" +
    "(?<userid>[^\t]+)\t" +
    "(?<pass>(?:!(?<salt>.{5})\\$(?<hash>[a-f0-9]{24}))|(?:!1a2b3c4d\\+))\t" + // KILL IT WITH FIRE!
    "(?<lastlogin>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\t" + // YYYY-mm-dd HH:MM:SS.sss
    "(?<sex>M|F|S|N)\t" +
    "(?<logincount>[0-9]+)\t" +
    "(?<state>[0-9]+)\t" +
    "(?<email>[^@]+@[^\t]+)\t" +
    "-\t" + // unused error_message
    "0\t" + // unused
    "(?<ip>[^\t]+)\t" +
    "(?<memo>[-!])\t" + // ! means salted hash, - means ???
    "(?<ban_until_time>[0-9]+)\t" +
    "$";
    private login_regex: RegExp;
    private encoder;

    constructor () {
        this.login_regex = new RegExp(this.login_line);
        this.encoder = new TextEncoder();
    }

    private inet_aton(ip: string) {
        const a = ip.split('.');
        const dv = new DataView(new ArrayBuffer(4));
        dv.setUint8(0, +a[0]);
        dv.setUint8(1, +a[1]);
        dv.setUint8(2, +a[2]);
        dv.setUint8(3, +a[3]);
        return dv.getUint32(0);
    }

    private parseLine (line: string) {
        const match = this.login_regex.exec(line);

        if (!(match instanceof Object) || !Reflect.has(match, "groups")) {
            console.error("\nline does not match the account regex:", line);
            throw new SyntaxError();
        }

        const groups = (match as any).groups;

        if (+groups.logincount === 0) {
            groups.lastlogin = null;
        } else {
            groups.lastlogin = new Date(groups.lastlogin).toISOString().slice(0, 19).replace("T", " ");
        }

        if (groups.memo !== "!") {
            console.warn(`\nunsupported password mode (${groups.memo}) for account ${groups.account_id}`);
            return null;
        }

        if (groups.email === "a@a.com") {
            groups.email = null;
        }

        groups.ip = this.inet_aton(groups.ip);

        if (+groups.ban_until_time >= 0xFFFFFFFF) {
            groups.ban_until_time = 0;
            groups.state = 5; // perma ban instead
        }

        Deno.write(Deno.stdout.rid, this.encoder.encode(`\r⌛ processing login data of account ${groups.account_id}...`));
        return groups;
    }

    public async * readDB () {
        const decoder = new TextDecoder("utf-8");
        console.info("\r                                                          \nwalking through account.txt...");
        const file = await Deno.open("login/save/account.txt");
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
                        if (accumulator.slice(0, 2) !== "//") {
                            yield this.parseLine(accumulator);
                        }
                        break;
                    } else {
                        accumulator += c;
                    }
                }
                break;
            }

            for (let c of str) {
                if (c === "\n") {
                    if (accumulator.slice(0, 2) !== "//") {
                        yield this.parseLine(accumulator);
                    }
                    accumulator = "";
                } else {
                    accumulator += c;
                }
            }
        }
    }
}

class LoginSQL {
    private sql;

    constructor (sql) {
        this.sql = sql;
    }

    async write (acc: any) {
        if (acc === null) {
            return Promise.resolve(false);
        }

        await this.sql.do("INSERT INTO `login` ?? values?", [
            ["account_id", "userid", "user_pass", "lastlogin", "logincount", "state", "email", "last_ip", "unban_time"],
            [+acc.account_id, acc.userid, acc.pass, acc.lastlogin, +acc.logincount, +acc.state, acc.email, acc.ip, acc.ban_until_time]
        ]);
    }
}

export {
    LoginParser,
    LoginSQL,
}
