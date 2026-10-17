"""Télécharge un livret de règles et dit en une ligne ce qui a été reçu.

    python -I -X utf8 telecharger.py "<lien>" "<dossier de travail>"

- Lien Google Drive (…/file/d/<id>/view, open?id=…) : téléchargement direct, page « fichier trop gros pour
  être analysé » passée automatiquement.
- Fichier enregistré sans modification : <dossier>/telechargement.pdf (ou .html / .bin si ce n'est pas un PDF).
- Bilan : nombre de pages et nom de fichier d'origine (en-tête Content-Disposition), ou « page HTML reçue »
  quand le site demande d'être connecté (à télécharger alors avec Chrome ou par l'utilisateur).
Le fichier reçu n'est jamais ouvert autrement que par pymupdf, ni exécuté.
"""
import email.message, re, sys, urllib.parse, urllib.request
from pathlib import Path

import lxml.html
import pymupdf


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


def main(url, dossier):
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    try:
        donnees, entetes, final = recevoir(lien_direct(url))
    except urllib.error.HTTPError as e:
        sys.exit(f"REFUSÉ : erreur {e.code} ({e.reason}) — site qui refuse la lecture simple ou demande d'être "
                 f"connecté : télécharger avec Chrome, sinon par l'utilisateur.")
    except urllib.error.URLError as e:
        sys.exit(f"ÉCHEC : site injoignable ({e.reason}).")
    if not donnees.startswith(b"%PDF") and "google.com" in final:
        suite = confirmation_drive(donnees, final)
        if suite:
            donnees, entetes, final = recevoir(suite)
    nom = nom_origine(entetes)
    if donnees.startswith(b"%PDF"):
        sortie = dossier / "telechargement.pdf"
        sortie.write_bytes(donnees)
        with pymupdf.open(sortie) as d:
            print(f"PDF : {sortie} — {d.page_count} pages — {len(donnees) // 1024} Ko"
                  f" — nom d'origine : {nom or '(non fourni)'}")
        return
    html = b"<html" in donnees[:2000].lower() or b"<!doctype html" in donnees[:2000].lower()
    sortie = dossier / ("telechargement.html" if html else "telechargement.bin")
    sortie.write_bytes(donnees)
    if html:
        sys.exit(f"PAS UN PDF : page HTML reçue ({final}) — connexion demandée ou lien vers une page, "
                 f"pas vers le fichier. Enregistrée dans {sortie}.")
    sys.exit(f"PAS UN PDF : fichier de type {entetes.get('Content-Type', 'inconnu')}"
             f" (nom d'origine : {nom or '(non fourni)'}), enregistré dans {sortie}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
