# Kontrola připravenosti vydání

Datum: 2026-11-17. Tato zpráva se vztahuje ke zdrojovému balíčku uvedenému v release-manifest.json, nikoli k jakékoli budoucí změně nebo libovolné složce původní instalace.

## Ověřeno

- Kompletní upstream Git historie: 3 commity; navíc místní dostupná historie a pracovní soubory aplikace, konfigurace, logy, testy a dokumentace. Porovnány známé lokální klíče v paměti a běžné tokenové vzory. Hodnoty nebyly zveřejněny. Historické credential nálezy: 0.
- Původní soukromá konfigurace obsahuje klíče a původní dokumentace obsahuje lokální cesty. Tyto soubory nebyly kopírovány. Veřejný snapshot vznikl z explicitního seznamu zdrojů, nikoli kopírováním celého pracovního adresáře nebo .git.
- Distribuce nemá původní Git metadata, autorovy lokální konfigurace, transcript data, logy, venv, node_modules ani frontend build. API klíče v .env.example jsou prázdné. Veřejné zdroje neobsahují zjištěné skutečné klíče ani konkrétní absolutní uživatelské cesty.
- Nová čistá instalace Windows 10: izolovaný venv, čerstvé npm ci, cesta s mezerami, žádná sdílená Python závislost, žádné klíče. Instalátor dokončil sestavení Reactu a pip check.
- 15 offline backend testů PASS: blokování všech externích operací, konfigurace, přepínání režimu, validace vstupů, souběh, Socket.IO, oba jazyky výstupů, mockované DNA i scénářové routy a mapování Gemini SDK. Test runner nikdy nenačítá skutečný .env a testy blokují socket.connect.
- Skutečný start aplikace, HTTP health, sestavená stránka a Socket.IO ověřeny. Obsazený preferovaný port vedl k výběru jiného volného portu, bez zásahu do cizí aplikace. Opakovaný start použil stejný proces.
- Prohlížeč: ověřeny Čeština / English, nezávislá volba výstupního jazyka, vložení syntetického textu a přechod ke kontrole přepisů. Chybějící klíče správně blokují online režim a generování. Žádná skutečná analýza ani scénář nevznikly.
- npm audit po opravě závislostí: 0 známých zranitelností. pip-audit zamčených Python závislostí: 0 známých zranitelností. Tyto databázové kontroly nejsou zárukou absence budoucích nebo neznámých chyb.
- Hashová kontrola původní instalace i existujícího copywriting skillu: beze změn. Nic nebylo publikováno ani nahráno na GitHub.

## Zbývající omezení

1. Upstream má pouze MIT deklaraci v README, nikoli samostatný LICENSE v historii. Přidaný standardní text MIT a přesný původ vysvětluje NOTICE.md. Doporučeno potvrdit copyright notice s původním autorem před veřejným vydáním.
2. Živá dostupnost Gemini modelu, Apify Actoru, jejich účtování a skutečné řazení YouTube nebyly testovány externím voláním. To je záměrné; neuvádíme placenou end-to-end cestu jako ověřenou.
3. Ověřená runtime kombinace je Python 3.14 / Node 24 na Windows 10 x64. Minimální podporované verze a jiné počítače vyžadují další ověření. Instalační skripty jsou čitelné, ale nejsou podepsané kódovým certifikátem; bezpečnostní software může vyžadovat kontrolu uživatele. Ochrany se nevypínají.
4. Python verze jsou zamčené, ale requirements nemají kryptografické hashe všech distribučních wheelů. Instalace používá standardní TLS ověřování PyPI; frontend lockfile obsahuje npm integrity hashe.
5. Aplikace je pouze lokální; nemá uživatelské účty, trvalý rozpočtový ledger ani zaručený cenový limit. Přesun na veřejný server vyžaduje samostatný bezpečnostní návrh.

Před publikací nové verze znovu proveďte release_check.py, závislostní audit, offline testy a kontrolu staged diff. Vždy publikujte pouze explicitně připravený zdrojový balíček.

## Affiliate karta Adriana

Distribuce obsahuje samostatnou kartu Adrian Viral AI Marketing pod generátorem, lokální optimalizovaný WebP avatar, český a anglický text a výslovné označení affiliate odkazu. Odkaz se otevírá v nové záložce s rel="sponsored noopener noreferrer". Avatar byl dodán zadavatelem; nepřidává síťové požadavky při načtení stránky. Původní obrázek ani API konfigurace se do distribuce nekopírují.

## Dokumentace a skutečné screenshoty

České README bylo přepracováno a doplněno plnohodnotným README.en.md. Obě verze popisují současný workflow, vlastní API klíče, Windows instalaci, ochranu dat a náklady. Ukázka docs/VIRAL-DNA-EXAMPLE.md je výslovně označená jako ručně vytvořená ilustrace formátu, nikoli reálný výsledek analýzy nebo změřená data.

Kontrola frontend exportů a backend rout potvrzuje pouze TXT výstupy přepisů, DNA a scénářů. Instalovatelný SKILL.md se nevytváří; obě README jej uvádějí jen jako plánované rozšíření.

Tři screenshoty byly zachyceny ze skutečné čisté instalace bez klíčů: české a anglické desktopové rozhraní a mobilní zobrazení. Obsahují funkční affiliate kartu s lokálním avatarem. Mobilní kontrola při šířce 390 px nezjistila horizontální přetečení; načtený avatar má 128 × 128 px. Odkaz nebyl při ověřování otevřen a nebylo voláno žádné externí analytické nebo generativní API.
