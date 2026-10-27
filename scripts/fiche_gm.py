"""Tokyo Game Market : recherche et lecture d'une fiche de jeu, depuis le contenu brut des pages.

    python -I -X utf8 fiche_gm.py chercher "<mot ou titre>"    liste des jeux trouvés (titre, lien, cercle)
    python -I -X utf8 fiche_gm.py fiche <numéro ou lien> [--tout]  informations (1 200 premiers caractères,
                                                                tout avec --tout), liens, images et PDF de la fiche,
                                                                site du cercle lu sur sa boutique BOOTH
    python -I -X utf8 fiche_gm.py cercle <numéro ou lien>       jeux d'un cercle (/booth/NNN), titres compris
    python -I -X utf8 fiche_gm.py page <lien>                   liens utiles d'une autre page (billet de blog
                                                                Game Market, page note.com, blog du cercle,
                                                                site de l'éditeur ; site Wix : liste de ses pages)

Plus fiable que le résumé d'une page par l'outil de lecture web : rien n'est réinterprété, et tous les liens
(règles, Drive, Notion, site, X, billets du blog Game Market) sont donnés tels quels.
"""
import re, sys, urllib.parse, urllib.request

import lxml.html

SITE = "https://gamemarket.jp"
LONG = 1200  # caractères de texte de fiche affichés (« --tout » : tout)
TOUT = "--tout" in sys.argv
if TOUT:
    sys.argv.remove("--tout")
# mention d'une autre langue dans le texte (manuel anglais annoncé sans lien, traduction…)
LANGUES = re.compile(r"English|英語|英文|EN版|translat|翻訳|한국어|中文|Français|Deutsch", re.I)
FICHIERS = re.compile(r"drive\.google|docs\.google\.com/(?!forms)|notion\.(site|so)|app\.notion|dropbox|\.pdf\b|"
                      r"img\.gamemarket\.jp|booth\.pm|gamemarket\.jp/blog/\d+", re.I)


def ascii_url(url):
    """Adresse utilisable par urllib même si elle contient du japonais (« …/タイトル.jpg »)."""
    return urllib.parse.quote(url, safe=":/?&=%#+,;@~!$'()*[]")


def lire(url):
    req = urllib.request.Request(ascii_url(url), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def page(url):
    return lxml.html.fromstring(lire(url), base_url=url)


def taille_image(url):
    """(largeur, hauteur) d'une image, ou None."""
    try:
        import pymupdf
        pix = pymupdf.Pixmap(lire(url))
        return pix.width, pix.height
    except Exception:
        return None


def mentions(texte):
    vus = []
    for m in LANGUES.finditer(texte):
        extrait = texte[max(0, m.start() - 40):m.end() + 40].strip()
        if not any(extrait in v or v in extrait for v in vus):
            vus.append(extrait)
    if vus:
        print("\nMentions d'une autre langue (chercher le lien sur les pages liées : note, blog, X) :")
        for v in vus[:6]:
            print(f"- …{v}…")


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
    # messages X recopiés dans la fiche (avis de joueurs) : longs et sans règles
    for x in d.xpath('//blockquote[contains(@class,"twitter")] | //script'):
        x.drop_tree()
    texte = net(d)
    debut, fin = texte.find("ゲーム一覧に戻る"), texte.find("この記事をシェア")  # menus du site laissés de côté
    print(f"Fiche : {url}\n")
    corps = texte[debut + len("ゲーム一覧に戻る"):fin].strip() if 0 <= debut < fin else texte
    # texte coupé (histoire, présentation bilingue…) : les liens, mentions et images suivent quand même
    print(corps if TOUT or len(corps) <= LONG else
          corps[:LONG] + f" …[{len(corps) - LONG} caractères de plus : relancer avec --tout]")
    print("\nLiens :")
    vus = set()
    for a in d.xpath("//a[@href]"):
        h = a.get("href")
        site = urllib.parse.urlparse(h).netloc.endswith("gamemarket.jp")
        # liens du site gardés : cercle (/booth/NNN) et billets de blog (/blog/NNN, souvent « règles ici »)
        if (h in vus or h.startswith(("javascript", "mailto")) or (site and not re.search(r"/(booth|blog)/\d+$", h))
                or re.search(r"twitter\.com/(share|GameMarket_)|line\.me|facebook\.com/sharer|docs\.google\.com/forms", h)):
            continue
        vus.add(h)
        blog = "  ← billet de blog : le lire avec « fiche_gm.py page »" if re.search(r"gamemarket\.jp/blog/\d+", h) else ""
        print(f"- {net(a) or '(sans texte)'} : {h}{blog}")
    boutiques = [h for h in vus if re.search(r"\.booth\.pm/", h)]
    if boutiques:
        sites_boutique(boutiques[0])
    mentions(corps)
    # Livrets parfois publiés en images ou en PDF dans le texte de la fiche (pas toujours en lien)
    zone = d.xpath('//*[contains(text(),"ゲーム詳細")]/ancestor::*[.//img][1]') or [d]
    fichiers = []
    for el in zone[0].xpath(".//img[@src] | .//iframe[@src] | .//embed[@src] | .//object[@data]"):
        u = (el.get("src") or el.get("data")).strip()
        if u not in vus and re.search(r"img\.gamemarket\.jp|\.pdf", u, re.I):
            vus.add(u)
            fichiers.append(u)
    lister_fichiers(fichiers)


AUTRES = re.compile(r"booth\.pm|booth\.pixiv|pixiv\.net|pximg|twitter\.com/(share|intent)|x\.com/(share|intent)|"
                    r"facebook\.com/sharer|line\.me|google\.com/(recaptcha|analytics)|googletagmanager|apple\.com|"
                    r"play\.google|pixivsketch|fanbox\.cc|w3\.org|karakuri\.ai|(x|twitter)\.com/booth_pm", re.I)


def sites_boutique(url):
    """Site du cercle affiché en tête de sa boutique BOOTH (« ホームページ ») : absent de la fiche Game Market et des
    moteurs de recherche, c'est souvent là que sont les règles (Chatlat : site Wix du cercle). La page d'un article
    le montre mieux que l'accueil de la boutique (construit en JavaScript)."""
    try:
        d = page(url)
    except Exception as e:
        print(f"\n(boutique BOOTH illisible : {e})")
        return
    d.make_links_absolute(url)
    sites = []
    for a in d.xpath("//a[@href]"):
        h = a.get("href")
        if h.startswith("http") and not AUTRES.search(h) and h not in sites:
            sites.append(h)
    if sites:
        print("\nSites du cercle (en tête de sa boutique BOOTH ; y chercher la page du jeu avec « fiche_gm.py page ») :")
        for h in sites[:8]:
            print(f"- {h}")


def pages_wix(brut, url):
    """Site Wix : toutes ses pages sont déclarées dans le code (« routes »), même celles absentes du menu ; la page
    d'un jeu est souvent rangée sous /games/<nom> alors qu'une page /<nom> n'est qu'une annonce."""
    routes = re.findall(r'"\.\\?/([^"]{1,80})":\{"type":"Static","pageId":"([0-9a-z]+)"', brut)
    if not routes:
        return
    titres = dict(re.findall(r'"pageId":"([0-9a-z]+)","title":"([^"]{1,80})"', brut))
    m = re.match(r"(https?://[^/]+(?:/[^/]+)?)", url)  # wixsite.com/<site> ou domaine propre
    base = m.group(1) if "wixsite.com" in url else re.match(r"https?://[^/]+", url).group(0)
    systeme = re.compile(r"account|members?|forum|notifications|followers|profile|settings|fullscreen|site-rules|"
                         r"複製|blank", re.I)
    vues = {}
    for chemin, pid in routes:
        chemin = chemin.replace("\\/", "/")
        if not systeme.search(chemin):
            vues.setdefault(chemin, titres.get(pid, "?"))
    print(f"\nPages du site (Wix, {len(vues)}) — la page du jeu est souvent sous /games/ :")
    for chemin, titre in vues.items():
        print(f"- {titre} : {base}/{chemin}")


def lister_fichiers(fichiers):
    """Images et PDF dans l'ordre de la page ; ★ = nom de livret, ◆ = image au format d'une page (portrait,
    proportions A4 / B5 : souvent une page du livret même si son nom ne le dit pas, « protected.png »…)."""
    if not fichiers:
        return
    print("\nImages et PDF du texte (ordre de la page ; ★ = nom de livret, ◆ = format d'une page de livret) :")
    for u in fichiers:
        livret = re.search(r"manual|rule|説明書|ルール|%E8%AA%AC%E6%98%8E", u, re.I)
        t = None if u.lower().endswith(".pdf") else taille_image(u)
        page_ = t and t[0] >= 600 and 1.3 <= t[1] / t[0] <= 1.5
        marque = "★ " if livret else ("◆ " if page_ else "")
        print(f"- {marque}{u}" + (f"  ({t[0]}×{t[1]} px)" if t else ""))


def autre_page(url):
    """Billet de blog Game Market, page note.com, blog d'un cercle : texte utile, liens et fichiers."""
    d = page(url)
    d.make_links_absolute(url)
    for x in d.xpath("//script | //style | //noscript"):
        x.drop_tree()
    brut = lire(url).decode("utf-8", "replace")  # pages construites en JavaScript : liens dans le code (note.com)
    print(f"Page : {url}")
    titre = d.xpath("//title")
    if titre:
        print(f"Titre : {net(titre[0])}")
    texte = net(d)
    print(f"Texte : {len(texte)} caractères")
    liens = []
    for h in d.xpath("//a/@href") + re.findall(r"https?://[^\s\"'<>\\]+", brut):
        h = h.replace("\\u0026", "&").rstrip(".,)")
        if FICHIERS.search(h) and not re.search(r"img\.gamemarket\.jp", h) and h not in liens and h != url:
            liens.append(h)
    print("\nLiens vers des fichiers ou des pages de règles :" if liens else "\nAucun lien Drive / Notion / PDF / blog.")
    for h in liens:
        print(f"- {h}")
    mentions(texte)
    pages_wix(brut, url)
    imgs = []
    for u in d.xpath("//img/@src") + re.findall(r"https?://img\.gamemarket\.jp/[^\s\"'<>\\)]+", brut):
        if "img.gamemarket.jp" in u and "ogp." not in u and u not in imgs:
            imgs.append(u)
    lister_fichiers(imgs)


def cercle(ref):
    n = re.search(r"(\d+)\s*$", ref.rstrip("/"))
    if not n:
        sys.exit("ERREUR : numéro de cercle introuvable.")
    url = f"{SITE}/booth/game/{n.group(1)}"
    d = page(url)
    print(f"Cercle : {SITE}/booth/{n.group(1)}")
    vus = set()
    for a in d.xpath('//a[starts-with(@href,"/game/")]'):
        h = a.get("href")
        if not re.fullmatch(r"/game/\d+", h) or h in vus:
            continue
        vus.add(h)
        bloc = a
        while bloc is not None and not net(bloc):
            bloc = bloc.getparent()
        print(f"- {net(bloc)[:150] if bloc is not None else ''}\n  {SITE}{h}")


if __name__ == "__main__":
    actions = {"chercher": chercher, "fiche": fiche, "cercle": cercle, "page": autre_page}
    if len(sys.argv) != 3 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]](sys.argv[2])
