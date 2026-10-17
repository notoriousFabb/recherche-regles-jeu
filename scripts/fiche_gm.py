"""Tokyo Game Market : recherche et lecture d'une fiche de jeu, depuis le contenu brut des pages.

    python -I -X utf8 fiche_gm.py chercher "<mot ou titre>"    liste des jeux trouvés (titre, lien, cercle)
    python -I -X utf8 fiche_gm.py fiche <numéro ou lien>        informations et liens de la fiche

Plus fiable que le résumé d'une page par l'outil de lecture web : rien n'est réinterprété, et tous les liens
(règles, Drive, Notion, site, X) sont donnés tels quels.
"""
import re, sys, urllib.parse, urllib.request

import lxml.html

SITE = "https://gamemarket.jp"


def page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return lxml.html.fromstring(r.read(), base_url=url)


def net(el):
    return " ".join(el.text_content().split())


def chercher(mot):
    d = page(f"{SITE}/game/?keyword={urllib.parse.quote(mot)}")
    total = next((net(x) for x in d.xpath('//*[contains(text(),"ゲーム一覧 (")]')), "")
    print(f"Recherche « {mot} » : {total or '?'}")
    vus = set()
    for a in d.xpath('//dt//a[starts-with(@href,"/game/")]'):
        if not re.fullmatch(r"/game/\d+", a.get("href")):
            continue
        lien = SITE + a.get("href")
        if lien in vus:
            continue
        vus.add(lien)
        bloc = a.getparent()
        while bloc is not None and bloc.tag != "dl":
            bloc = bloc.getparent()
        cercle = ""
        if bloc is not None:
            b = bloc.xpath('.//a[starts-with(@href,"/booth/") and not(contains(@href,"/game/"))]')
            cercle = net(b[0]) if b else ""
        print(f"- {net(a)}\n  {lien}" + (f"  ·  cercle : {cercle}" if cercle else ""))


def fiche(ref):
    n = re.search(r"(\d+)\s*$", ref.rstrip("/"))
    if not n:
        sys.exit("ERREUR : numéro de fiche introuvable.")
    url = f"{SITE}/game/{n.group(1)}"
    d = page(url)
    d.make_links_absolute(url)
    texte = net(d)
    debut, fin = texte.find("ゲーム一覧に戻る"), texte.find("この記事をシェア")  # menus du site laissés de côté
    print(f"Fiche : {url}\n")
    print(texte[debut + len("ゲーム一覧に戻る"):fin].strip() if 0 <= debut < fin else texte)
    print("\nLiens :")
    vus = set()
    for a in d.xpath("//a[@href]"):
        h = a.get("href")
        site = urllib.parse.urlparse(h).netloc.endswith("gamemarket.jp")
        if (h in vus or h.startswith(("javascript", "mailto")) or (site and not re.search(r"/booth/\d+$", h))
                or re.search(r"twitter\.com/(share|GameMarket_)|line\.me|facebook\.com/sharer|docs\.google\.com/forms", h)):
            continue
        vus.add(h)
        print(f"- {net(a) or '(sans texte)'} : {h}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("chercher", "fiche"):
        sys.exit(__doc__)
    (chercher if sys.argv[1] == "chercher" else fiche)(sys.argv[2])
