import { DOMParser, Element } from "https://deno.land/x/deno_dom@v0.1.2-alpha3/deno-dom-wasm.ts";
import { itemsXML } from "./itemsXML.ts";

class ManaMarketHandler {
    private stats_html: string = "";
    items: Map<number, any> = new Map();
    private itemsXML: itemsXML;

    constructor (server: string = "https://server.themanaworld.org") {
        this.stats_html = `${server}/manamarket_stats.html`;
        this.itemsXML = new itemsXML();
    }

    async init () {
        console.log("Fetching ManaMarket stats...");

        const res = await fetch(this.stats_html);
        const html = await res.text();

        await this.itemsXML.init();

        this.parseHTML(html);
    }

    private parseHTML (html: string) {
        console.log("\r                                                                                                  \rParsing ManaMarket stats...                ");

        const domparser = new DOMParser();
        const root = domparser.parseFromString(html, "text/html")!;
        const rows = root.querySelectorAll("tr:nth-of-type(n+3)");

        for (const row of rows) {
            const el = row as Element;
            const name = el.children[0].innerHTML as string;
            const xml = this.itemsXML.getItem(name);

            if (!xml) {
                console.warn(`Cannot find item \`${name}\` in the item xml files`);
                continue;
            }

            const item = {
                name: name,
                id: xml.id,
                totalSold: +el.children[1].innerHTML.split(",").join(""),
                minValue: +el.children[2].innerHTML.split(",").join(""),
                maxValue: +el.children[3].innerHTML.split(",").join(""),
                averageValue: {
                    week: +el.children[4].innerHTML.split(",").join(""),
                    month: +el.children[5].innerHTML.split(",").join(""),
                    overall: +el.children[6].innerHTML.split(",").join(""),
                },
                lastSold: new Date(el.children[7].innerHTML),
            };

            this.items.set(item.id, item);
        }
    }
}

export {
    ManaMarketHandler,
}
