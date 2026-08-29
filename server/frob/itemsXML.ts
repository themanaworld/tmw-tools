import { DOMParser, Element } from "https://deno.land/x/deno_dom@v0.1.2-alpha3/deno-dom-wasm.ts";

class itemsXML {
    private repo: string = "";
    private encoder: TextEncoder;
    private decoder: TextDecoder;
    private items_by_name: Map<string, number> = new Map();
    private items_by_id: Map<number, any> = new Map();

    constructor (repo: string = "client-data") {
        this.repo = repo;
        this.encoder = new TextEncoder();
        this.decoder = new TextDecoder("utf-8");
    }

    async init () {
        console.log("Fetching items xml files from client-data...");

        await this.fetchFile("items.xml");
    }

    private async fetchFile (path: string) {
        const raw = await Deno.readFile(`${this.repo}/${path}`);
        const xml = this.decoder.decode(raw);

        await this.parseXML(path, xml);
    }

    private async parseXML (path: string, xml: string) {
        Deno.write(Deno.stdout.rid, this.encoder.encode(`                                                                            \r⌛ parsing ${path}...`));

        const domparser = new DOMParser();

        if (xml.startsWith("<?")) {
            // remove the xml doctype
            xml = xml.split("\n").slice(1).join("\n");
        }

        if (xml.startsWith("<items>\n  <its:")) {
            // translation stuff
            xml = "<items>\n" + xml.split("\n").slice(7).join("\n");
        }

        const root = domparser.parseFromString(xml, "text/html")!;

        if (root) {
            const items = root.querySelectorAll("item");
            const includes = root.querySelectorAll("include");

            for (const el of includes) {
                const tag: Element = el as Element;
                await this.fetchFile(tag.attributes.name);
            }

            for (const el of items) {
                const tag: Element = el as Element;

                const item = {
                    id: +tag.attributes.id,
                    name: tag.attributes.name,
                    type: tag.attributes.type,
                };

                this.items_by_id.set(item.id, item);
                this.items_by_name.set(item.name, item.id);
            }
        }
    }

    getItem (item: string | number) {
        if (typeof item === "string") {
            const id = this.items_by_name.get(item);

            if (id) {
                return this.items_by_id.get(id) || null;
            }
        } else if (typeof item === "number") {
            return this.items_by_id.get(item) || null;
        }

        return null;
    }
}

export {
    itemsXML,
}
