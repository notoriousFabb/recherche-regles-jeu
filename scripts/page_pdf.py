"""Met en PDF les règles affichées sur une ou plusieurs pages web, sans rien couper.

    python -I -X utf8 page_pdf.py sortie.pdf URL [URL ...] --xpath "//article" [--titre "Nom"]
    python -I -X utf8 page_pdf.py sortie.pdf URL --complet

--xpath : bloc(s) de chaque page qui contiennent les règles (le reste de la page est laissé de côté).
--complet : la page entière, telle que le navigateur l'imprime.
Le navigateur (Chrome, sinon Edge) tourne en arrière-plan avec un profil temporaire : il ne touche pas à
celui de l'utilisateur. À la fin, bilan caractères / images de la source et du PDF.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

import lxml.html
import pymupdf

NAVIGATEURS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
               r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
               r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
               "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
               "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
RETIRER = "//script | //noscript | //style | //link | //iframe | //form | //button"
CSS = """
body { font-family: "Segoe UI", "Yu Gothic", "Meiryo", "Microsoft YaHei", "Malgun Gothic", sans-serif;
       font-size: 11pt; line-height: 1.45; color: #000; margin: 0; }
img, svg, video { max-width: 100%; height: auto; }
table { border-collapse: collapse; max-width: 100%; margin: .5em 0; }
td, th { border: 1px solid #888; padding: 3px 6px; vertical-align: top; }
pre, code { white-space: pre-wrap; }
h1, h2, h3, h4 { break-after: avoid; }
img, table, figure { break-inside: avoid; }
.source { font-size: 8pt; color: #555; margin: 0 0 1em; word-break: break-all; }
.page + .page { break-before: page; }
@page { size: A4; margin: 15mm 14mm; }
"""


def navigateur():
    for p in NAVIGATEURS:
        if os.path.exists(p):
            return p
    for nom in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "chrome", "msedge"):
        if shutil.which(nom):
            return shutil.which(nom)
    sys.exit("ERREUR : ni Chrome ni Edge trouvé.")


def lancer(nav, profil, args, timeout=120):
    cmd = [nav, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--disable-extensions", f"--user-data-dir={profil}", "--virtual-time-budget=15000", *args]
    r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return r.stdout.decode("utf-8", "replace")


def compter(texte):
    return len(re.sub(r"\s+", "", texte))


def nettoyer(el):
    for x in el.xpath(RETIRER):
        x.drop_tree()
    for img in el.xpath(".//img"):
        # images chargées à la demande : la vraie adresse est souvent dans data-src
        for a in ("data-src", "data-lazy-src", "data-original", "data-orig-file"):
            if img.get(a):
                img.set("src", img.get(a))
                break
        for a in ("srcset", "data-srcset", "loading", "sizes"):
            img.attrib.pop(a, None)
    for x in el.iter():
        if isinstance(x.tag, str):
            for a in ("style", "class", "width", "height") if x.tag != "img" else ("style", "class"):
                x.attrib.pop(a, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sortie")
    ap.add_argument("urls", nargs="+")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--xpath")
    g.add_argument("--complet", action="store_true")
    ap.add_argument("--titre", default="")
    a = ap.parse_args()

    nav = navigateur()
    sortie = Path(a.sortie).resolve()
    travail = Path(tempfile.mkdtemp(prefix="page_pdf_"))
    profil = travail / "profil"
    try:
        if a.complet:
            if len(a.urls) > 1:
                sys.exit("ERREUR : --complet n'accepte qu'une page ; pour plusieurs pages, utiliser --xpath.")
            dom = lancer(nav, profil, ["--dump-dom", a.urls[0]])
            doc = lxml.html.fromstring(dom or "<html></html>")
            for x in doc.xpath(RETIRER):
                x.drop_tree()
            n_txt, n_img = compter(doc.text_content()), len(doc.xpath("//img"))
            lancer(nav, profil, [f"--print-to-pdf={sortie}", "--no-pdf-header-footer", a.urls[0]])
        else:
            blocs, n_txt, n_img = [], 0, 0
            for url in a.urls:
                dom = lancer(nav, profil, ["--dump-dom", url])
                if not dom.strip():
                    sys.exit(f"ERREUR : page vide ou inaccessible : {url}")
                doc = lxml.html.fromstring(dom, base_url=url)
                doc.make_links_absolute(url)
                trouves = doc.xpath(a.xpath)
                if not trouves:
                    sys.exit(f"ERREUR : l'XPath ne trouve rien sur {url}")
                html = []
                for el in trouves:
                    nettoyer(el)
                    n_txt += compter(el.text_content())
                    n_img += len(el.xpath(".//img[@src]"))
                    html.append(lxml.html.tostring(el, encoding="unicode"))
                source = "" if url.startswith("file:") else f'<p class="source">Source : {url}</p>'  # fichier local : sa source est dans le fichier
                blocs.append(f'<div class="page">{source}{"".join(html)}</div>')
            titre = f"<title>{a.titre}</title>" if a.titre else ""
            page = travail / "regles.html"
            page.write_text(f'<!doctype html><html><head><meta charset="utf-8">{titre}<style>{CSS}</style>'
                            f'</head><body>{"".join(blocs)}</body></html>', encoding="utf-8")
            lancer(nav, profil, [f"--print-to-pdf={sortie}", "--no-pdf-header-footer", page.as_uri()])

        if not sortie.exists():
            sys.exit("ERREUR : le navigateur n'a pas produit de PDF.")
        d = pymupdf.open(sortie)
        p_txt = compter("".join(p.get_text() for p in d))
        p_img = len({x[0] for p in d for x in p.get_images()})
        print(f"PDF : {sortie} — {d.page_count} pages")
        print(f"Texte : source {n_txt} caractères, PDF {p_txt}")
        print(f"Images : source {n_img}, PDF {p_img}")
        if n_txt and p_txt < 0.95 * n_txt:
            print("ALERTE : le PDF contient nettement moins de texte que la source.")
        if p_img < n_img:
            print("ALERTE : des images de la source manquent peut-être dans le PDF.")
    finally:
        shutil.rmtree(travail, ignore_errors=True)


if __name__ == "__main__":
    main()
