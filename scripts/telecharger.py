"""Télécharge un livret de règles et dit en une ligne ce qui a été reçu.

    python -I -X utf8 telecharger.py "<lien>" "<dossier de travail>"
    python -I -X utf8 telecharger.py "<image 1>" "<image 2>" […] "<dossier de travail>"

- Lien Google Drive (…/file/d/<id>/view, open?id=…) : téléchargement direct, page « fichier trop gros pour
  être analysé » passée automatiquement.
- Lien de dossier Google Drive (…/drive/folders/<id>) : liste des fichiers du dossier (nom et lien), rien
  n'est téléchargé ; relancer ensuite avec les liens choisis.
- Règles publiées en images (JPEG, PNG) : une ou plusieurs images, assemblées dans l'ordre donné en un seul
  PDF, une image par page, sans modification ; taille de chaque image indiquée (alerte si elle est petite).
- Résultat : <dossier>/telechargement.pdf (ou .html / .bin si ce n'est ni un PDF ni une image).
- Bilan : nombre de pages et nom de fichier d'origine (en-tête Content-Disposition), ou « page HTML reçue »
  quand le site demande d'être connecté (à télécharger alors avec Chrome ou par l'utilisateur).
Le fichier reçu n'est jamais ouvert autrement que par pymupdf, ni exécuté.
"""
import email.message, re, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

import lxml.html
import pymupdf

IMAGES = {b"\xff\xd8\xff": "jpg", b"\x89PNG": "png"}
PETITE = 1200  # pixels sur le grand côté : en dessous, texte probablement difficile à lire


def lien_direct(url):
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:.*&)?id=)([\w-]+)", url)
    return f"https://drive.google.com/uc?export=download&id={m.group(1)}" if m else url


def recevoir(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), r.headers, r.geturl()


def confirmation_drive(html, base):
    """Page Drive « impossible d'analyser ce fichier » : lien du formulaire « Télécharger quand même »."""
    d = lxml.html.fromstring(html, base_url=base)
    for f in d.xpath('//form[@id="download-form"]'):
        champs = {i.get("name"): i.get("value", "") for i in f.xpath(".//input[@name]")}
        return urllib.parse.urljoin(base, f.get("action")) + "?" + urllib.parse.urlencode(champs)
    return None


def nom_origine(entetes):
    cd = entetes.get("Content-Disposition")
    if not cd:
        return ""
    m = email.message.Message()
    m["Content-Disposition"] = cd
    nom = m.get_filename() or ""
    try:  # Drive envoie le nom en UTF-8 brut, lu comme du latin-1
        return nom.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return nom


def type_image(donnees):
    return next((t for debut, t in IMAGES.items() if donnees.startswith(debut)), None)


def obtenir(url):
    """Données, en-têtes, adresse finale et nom d'origine d'un lien ; arrêt avec un message clair en cas d'échec."""
    try:
        donnees, entetes, final = recevoir(lien_direct(url))
        if not donnees.startswith(b"%PDF") and not type_image(donnees) and "google.com" in final:
            suite = confirmation_drive(donnees, final)
            if suite:
                donnees, entetes, final = recevoir(suite)
    except urllib.error.HTTPError as e:
        sys.exit(f"REFUSÉ : erreur {e.code} ({e.reason}) pour {url} — site qui refuse la lecture simple ou "
                 f"demande d'être connecté : télécharger avec Chrome, sinon par l'utilisateur.")
    except urllib.error.URLError as e:
        sys.exit(f"ÉCHEC : site injoignable ({e.reason}) pour {url}.")
    nom = nom_origine(entetes) or Path(urllib.parse.unquote(urllib.parse.urlparse(final).path)).name
    return donnees, entetes, final, nom


def lister_dossier(url, id_dossier):
    donnees, _, final = recevoir(f"https://drive.google.com/embeddedfolderview?id={id_dossier}")
    d = lxml.html.fromstring(donnees, base_url=final)
    fichiers = [(" ".join(a.text_content().split()), a.get("href")) for a in d.xpath("//a[@href]")
                if re.search(r"/(file/d|drive/folders)/", a.get("href"))]
    if not fichiers:
        sys.exit(f"DOSSIER vide ou non public : {url}")
    print(f"DOSSIER : {len(fichiers)} élément(s) — relancer avec les liens choisis")
    for nom, lien in fichiers:
        print(f"- {nom} : {lien.split('?')[0]}" + ("  (sous-dossier)" if "/folders/" in lien else ""))


def pas_un_pdf(donnees, entetes, final, nom, dossier):
    html = b"<html" in donnees[:2000].lower() or b"<!doctype html" in donnees[:2000].lower()
    sortie = dossier / ("telechargement.html" if html else "telechargement.bin")
    sortie.write_bytes(donnees)
    if html:
        sys.exit(f"PAS UN PDF : page HTML reçue ({final}) — connexion demandée ou lien vers une page, "
                 f"pas vers le fichier. Enregistrée dans {sortie}.")
    sys.exit(f"PAS UN PDF : fichier de type {entetes.get('Content-Type', 'inconnu')}"
             f" (nom d'origine : {nom or '(non fourni)'}), enregistré dans {sortie}.")


def assembler(urls, dossier):
    """Images (une par page, dans l'ordre donné) → un seul PDF, images gardées telles quelles."""
    pdf = pymupdf.open()
    for i, url in enumerate(urls, 1):
        donnees, entetes, final, nom = obtenir(url)
        t = type_image(donnees)
        if not t:
            pas_un_pdf(donnees, entetes, final, nom, dossier)
        with pymupdf.open(stream=donnees, filetype=t) as img:
            rect = img[0].rect
        pix = pymupdf.Pixmap(donnees)
        pdf.new_page(width=rect.width, height=rect.height).insert_image(rect, stream=donnees)
        alerte = "  ALERTE : petite image, texte peut-être difficile à lire" if max(pix.width, pix.height) < PETITE else ""
        print(f"Page {i} : {nom} — {pix.width}×{pix.height} px{alerte}")
    sortie = dossier / "telechargement.pdf"
    pdf.save(sortie, deflate=True)
    print(f"PDF : {sortie} — {pdf.page_count} pages (images assemblées)")


def main(urls, dossier):
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    if len(urls) == 1:
        m = re.search(r"drive\.google\.com/drive/(?:u/\d+/)?folders/([\w-]+)", urls[0])
        if m:
            return lister_dossier(urls[0], m.group(1))
        donnees, entetes, final, nom = obtenir(urls[0])
        if donnees.startswith(b"%PDF"):
            sortie = dossier / "telechargement.pdf"
            sortie.write_bytes(donnees)
            with pymupdf.open(sortie) as d:
                print(f"PDF : {sortie} — {d.page_count} pages — {len(donnees) // 1024} Ko"
                      f" — nom d'origine : {nom or '(non fourni)'}")
            return
        if not type_image(donnees):
            pas_un_pdf(donnees, entetes, final, nom, dossier)
    assembler(urls, dossier)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1:-1], sys.argv[-1])
