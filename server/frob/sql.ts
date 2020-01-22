import { Client } from "https://deno.land/x/mysql/mod.ts";

class SQLHandler {
    private client;
    private hostname;
    private username;
    private password;
    private backslash;

    constructor (hostname: string = "127.0.0.1", username: string = "evol", password: string = "evol") {
        this.client = new Client();
        [this.hostname, this.username, this.password] = [hostname, username, password];

        // escape regexes
        this.backslash = /\\/g;
    }

    async init () {
        await this.client.connect({
            hostname: this.hostname,
            username: this.username,
            password: this.password,
        });

        // INSTALL SONAME 'ha_rocksdb';

        console.log("Initializing database...");
        await this.do("CREATE DATABASE IF NOT EXISTS legacy");
        await this.do("USE legacy");

        console.log("Initializing tables...");
        await this.do("DROP TABLE IF EXISTS `login`");
        await this.do("DROP TABLE IF EXISTS `char`");
        await this.do("DROP TABLE IF EXISTS `inventory`");
        await this.do("DROP TABLE IF EXISTS `storage`");
        await this.do("DROP TABLE IF EXISTS `global_acc_reg`");
        await this.do("DROP TABLE IF EXISTS `acc_reg`");
        await this.do("DROP TABLE IF EXISTS `char_reg`");
        await this.do("DROP TABLE IF EXISTS `party`");
        await this.do(`
            CREATE TABLE \`login\` (
                account_id INT(11) UNSIGNED NOT NULL,
                revolt_id INT(11) UNSIGNED NULL, -- id of the new account on revolt
                userid VARCHAR(23) NOT NULL DEFAULT '',
                user_pass VARCHAR(32) NOT NULL DEFAULT '',
                lastlogin DATETIME NULL,
                -- sex,
                logincount INT(9) UNSIGNED NOT NULL DEFAULT '0',
                state INT(11) UNSIGNED NOT NULL DEFAULT '0',
                email VARCHAR(39) NULL,
                -- error_message,
                -- connect_until_time,
                last_ip INT(4) UNSIGNED NOT NULL DEFAULT 0,
                -- memo,
                unban_time INT(11) UNSIGNED NOT NULL DEFAULT '0',
                PRIMARY KEY (account_id),
                UNIQUE KEY revolt (revolt_id),
                KEY userid (userid)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`char\` (
                char_id INT(11) UNSIGNED NOT NULL,
                revolt_id INT(11) UNSIGNED NULL, -- id of the new char on revolt
                account_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                char_num TINYINT(1) NOT NULL DEFAULT '0',
                \`name\` VARCHAR(30) NOT NULL DEFAULT '',
                class SMALLINT(6) UNSIGNED NOT NULL DEFAULT '0',
                base_level SMALLINT(6) UNSIGNED NOT NULL DEFAULT '1',
                job_level SMALLINT(6) UNSIGNED NOT NULL DEFAULT '1',
                base_exp BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
                job_exp BIGINT(20) UNSIGNED NOT NULL DEFAULT '0',
                zeny INT(11) UNSIGNED NOT NULL DEFAULT '0',
                \`str\` SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                agi SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                vit SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                \`int\` SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                dex SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                luk SMALLINT(4) UNSIGNED NOT NULL DEFAULT '0',
                status_point INT(11) UNSIGNED NOT NULL DEFAULT '0',
                skill_point INT(11) UNSIGNED NOT NULL DEFAULT '0',
                party_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                party_isleader BIT(1) NOT NULL DEFAULT 0,
                hair TINYINT(4) UNSIGNED NOT NULL DEFAULT '0',
                hair_color SMALLINT(5) UNSIGNED NOT NULL DEFAULT '0',
                partner_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                sex ENUM('M','F','N','S') NOT NULL DEFAULT 'N',
                PRIMARY KEY (char_id),
                UNIQUE KEY revolt (revolt_id),
                UNIQUE KEY name_key (name),
                KEY account_id (account_id),
                KEY party_id (party_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`inventory\` (
                id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                char_id INT(11) UNSIGNED NOT NULL,
                nameid INT(11) UNSIGNED NOT NULL DEFAULT '0',
                amount INT(11) UNSIGNED NOT NULL DEFAULT '0',
                equip INT(11) UNSIGNED NOT NULL DEFAULT '0',
                PRIMARY KEY (id),
                KEY char_id (char_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`storage\` (
                id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                account_id INT(11) UNSIGNED NOT NULL,
                nameid INT(11) UNSIGNED NOT NULL DEFAULT '0',
                amount INT(11) UNSIGNED NOT NULL DEFAULT '0',
                PRIMARY KEY (id),
                KEY account_id (account_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`global_acc_reg\` (
                account_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                \`name\` VARCHAR(32) NOT NULL DEFAULT '',
                \`value\` INT(11) NOT NULL DEFAULT '0',
                PRIMARY KEY (account_id,\`name\`),
                KEY account_id (account_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`acc_reg\` (
                account_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                \`name\` VARCHAR(32) NOT NULL DEFAULT '',
                \`value\` INT(11) NOT NULL DEFAULT '0',
                PRIMARY KEY (account_id,\`name\`),
                KEY account_id (account_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`char_reg\` (
                char_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                \`name\` VARCHAR(32) NOT NULL DEFAULT '',
                \`value\` INT(11) NOT NULL DEFAULT '0',
                PRIMARY KEY (char_id,\`name\`),
                KEY char_id (char_id)
            ) ENGINE=ROCKSDB;
        `);
        await this.do(`
            CREATE TABLE \`party\` (
                party_id INT(11) UNSIGNED NOT NULL DEFAULT '0',
                revolt_id INT(11) UNSIGNED NULL, -- id of the new party on revolt
                \`name\` VARCHAR(24) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
                exp_share BIT(1) NOT NULL DEFAULT 0,
                item_share BIT(1) NOT NULL DEFAULT 0,
                PRIMARY KEY (party_id),
                UNIQUE KEY revolt (revolt_id),
                UNIQUE KEY name_key (name)
            ) ENGINE=ROCKSDB;
        `); // some old parties have weird names
    }

    escape (str) {
        // for some reason the deno sql module doesn't escape backslashes
        return str.replace(this.backslash, "\\\\");
    }

    async transaction (fn) {
        return await this.client.transaction(fn);
    }

    async query (...args) {
        return await this.client.query(...args);
    }

    async do (...args) {
        return await this.client.execute(...args);
    }


    async close () {
        return this.client.close();
    }
}

export {
    SQLHandler,
}
