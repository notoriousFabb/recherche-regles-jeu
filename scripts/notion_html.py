"""Page Notion publique → fichier HTML complet, à mettre ensuite en PDF avec page_pdf.py.

    python -I -X utf8 notion_html.py "<lien de la page Notion>" sortie.html

Notion n'affiche que la partie visible d'une page (le reste se charge en défilant) : ni la lecture de la page
ni l'impression par le navigateur ne donnent tout. Ce script lit tous les blocs de la page auprès de Notion
(interface publique, sans compte) et écrit le HTML de la page entière, blocs repliés (toggles) dépliés.
Puis : page_pdf.py sortie.pdf "file:///…/sortie.html" --xpath "//body" --titre "<Nom du jeu>".
"""
import html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

API = "https://www.notion.so/api/v3/"


def appel(point, donnees):
    req = urllib.request.Request(API + point, json.dumps(donnees).encode(), {"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def valeur(rec):
    v = rec.get("value", {})
    return v.get("value", v)  # deux formes selon la version de l'interface


def identifiant(lien):
    m = re.search(r"([0-9a-f]{32})(?:[?#]|$)", lien.replace("-", ""))
    if not m:
        sys.exit("ERREUR : identifiant de page Notion introuvable dans le lien.")
    h = m.group(1)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def charger(page):
    blocs, curseur, n = {}, {"stack": []}, 0
    while True:
        r = appel("loadPageChunk", {"pageId": page, "limit": 100, "cursor": curseur, "chunkNumber": n,
                                     "verticalColumns": False})
        for k, rec in r["recordMap"].get("block", {}).items():
            blocs[k] = valeur(rec)
        curseur, n = r.get("cursor", {"stack": []}), n + 1
        if not curseur.get("stack") or n > 200:
            break
    # blocs enfants pas encore reçus (dans des toggles, colonnes…)
    while True:
        manque = {c for b in blocs.values() for c in b.get("content", []) if c not in blocs}
        if not manque:
            break
        r = appel("syncRecordValues", {"requests": [{"pointer": {"table": "block", "id": i}, "version": -1}
                                                    for i in manque]})
        recus = r.get("recordMap", {}).get("block", {})
        for k, rec in recus.items():
            blocs[k] = valeur(rec)
        if not any(k in manque for k in recus):
            sys.exit(f"ERREUR : {len(manque)} bloc(s) introuvable(s) — page incomplète.")
    return blocs


def texte(riche):
    out = []
    for morceau in riche or []:
        t, styles = morceau[0], (morceau[1] if len(morceau) > 1 else [])
        t = html.escape(t).replace("\n", "<br>")
        for s in styles:
            if s[0] == "b": t = f"<b>{t}</b>"
            elif s[0] == "i": t = f"<i>{t}</i>"
            elif s[0] == "s": t = f"<s>{t}</s>"
            elif s[0] == "_": t = f"<u>{t}</u>"
            elif s[0] == "c": t = f"<code>{t}</code>"
            elif s[0] == "a": t = f'<a href="{html.escape(s[1])}">{t}</a>'
            elif s[0] == "h" and not s[1].endswith("background"): t = f'<span style="color:{s[1]}">{t}</span>'
            elif s[0] == "e": t = f"<code>{html.escape(s[1])}</code>"
        out.append(t)
    return "".join(out)


def image(b):
    src = (b.get("format", {}) or {}).get("display_source") or (b.get("properties", {}).get("source") or [[""]])[0][0]
    if not src:
        return ""
    if src.startswith("attachment:") or "amazonaws.com" in src:
        src = (f"https://www.notion.so/image/{urllib.parse.quote(src, safe='')}"
               f"?table=block&id={b['id']}&cache=v2")
    leg = texte(b.get("properties", {}).get("caption"))
    return f'<figure><img src="{html.escape(src)}">{f"<figcaption>{leg}</figcaption>" if leg else ""}</figure>'


def rendre(ids, blocs):
    out, i = [], 0
    while i < len(ids):
        b = blocs.get(ids[i])
        if not b or not b.get("alive", True):
            i += 1
            continue
        t = b.get("type")
        if t in ("bulleted_list", "numbered_list"):  # regrouper les éléments de liste qui se suivent
            balise, items = ("ul" if t == "bulleted_list" else "ol"), []
            while i < len(ids) and (blocs.get(ids[i]) or {}).get("type") == t:
                items.append(f"<li>{bloc(blocs[ids[i]], blocs)}</li>")
                i += 1
            out.append(f"<{balise}>{''.join(items)}</{balise}>")
            continue
        out.append(bloc(b, blocs, avec_enfants=True))
        i += 1
    return "\n".join(out)


def bloc(b, blocs, avec_enfants=False):
    t, p = b.get("type"), b.get("properties", {})
    titre, enfants = texte(p.get("title")), rendre(b.get("content", []), blocs) if b.get("content") else ""
    if t in ("bulleted_list", "numbered_list"):
        return titre + enfants
    if t == "header": return f"<h1>{titre}</h1>{enfants}"
    if t == "sub_header": return f"<h2>{titre}</h2>{enfants}"
    if t == "sub_sub_header": return f"<h3>{titre}</h3>{enfants}"
    if t == "header_4": return f"<h4>{titre}</h4>{enfants}"
    if t == "text": return f"<p>{titre}</p>{enfants}"
    if t == "quote": return f"<blockquote>{titre}{enfants}</blockquote>"
    if t == "callout":
        ic = (b.get("format", {}) or {}).get("page_icon", "")
        ic = html.escape(ic) + " " if ic and not ic.startswith("http") and len(ic) <= 4 else ""
        return f'<div class="callout">{ic}{titre}{enfants}</div>'
    if t == "toggle": return f"<div class=\"toggle\"><p><b>▾ {titre}</b></p>{enfants}</div>"
    if t == "to_do":
        coche = "☑" if (p.get("checked") or [["No"]])[0][0] == "Yes" else "☐"
        return f"<p>{coche} {titre}</p>{enfants}"
    if t == "divider": return "<hr>"
    if t == "image": return image(b)
    if t == "code": return f"<pre><code>{titre}</code></pre>"
    if t == "equation": return f"<p><code>{titre}</code></p>"
    if t in ("column_list", "column"): return f'<div class="{t}">{enfants}</div>'
    if t == "table":
        cols = (b.get("format", {}) or {}).get("table_block_column_order", [])
        lignes = []
        for rid in b.get("content", []):
            r = blocs.get(rid, {}).get("properties", {})
            lignes.append("<tr>" + "".join(f"<td>{texte(r.get(c))}</td>" for c in cols) + "</tr>")
        return f"<table>{''.join(lignes)}</table>"
    if t == "page": return f"<p><b>{titre}</b> (sous-page)</p>"
    if t == "bookmark": return f'<p><a href="{html.escape((p.get("link") or [[""]])[0][0])}">{titre or "lien"}</a></p>'
    print(f"ATTENTION : bloc de type « {t} » non pris en charge ; texte gardé tel quel.")
    return f"<p>{titre}</p>{enfants}"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    page = identifiant(sys.argv[1])
    blocs = charger(page)
    racine = blocs.get(page)
    if not racine:
        sys.exit("ERREUR : page introuvable ou non publique.")
    titre = texte(racine.get("properties", {}).get("title"))
    corps = rendre(racine.get("content", []), blocs)
    css = (".callout{background:#f3f3f1;border-radius:4px;padding:6px 10px;margin:.5em 0}"
           ".column_list{display:flex;gap:16px}.column{flex:1}"
           "blockquote{border-left:3px solid #999;margin:.5em 0;padding-left:10px}")
    Path(sys.argv[2]).write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>{titre}</title>'
                                 f'<style>{css}</style></head><body><h1>{titre}</h1>\n{corps}</body></html>',
                                 encoding="utf-8")
    sous_pages = [b for b in blocs.values() if b.get("type") == "page" and b.get("id") != page]
    print(f"HTML : {sys.argv[2]} — {len(blocs)} blocs, {sum(1 for b in blocs.values() if b.get('type') == 'image')} images")
    if sous_pages:
        print(f"ATTENTION : {len(sous_pages)} sous-page(s) non incluse(s) : "
              + ", ".join(re.sub('<[^>]+>', '', texte(b.get('properties', {}).get('title'))) for b in sous_pages))


if __name__ == "__main__":
    main()
