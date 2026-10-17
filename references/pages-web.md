# Règles affichées sur des pages web → PDF

1. Lire la page (WebFetch ; Chrome en mode texte — `get_page_text` ou JavaScript — si elle se construit en
   JavaScript ou refuse la lecture simple) pour repérer **toutes** les pages des règles (sommaire, « page
   suivante », onglets) dans l'ordre de lecture.
2. Convertir, **depuis PowerShell** (Git Bash transforme les arguments qui commencent par `//`) :
   - **Par défaut, mise en page du site gardée** :
     `python -I -X utf8 <skill>/scripts/page_pdf.py "<travail>/<nom>.pdf" "<url1>" ["<url2>" …] --fidele --titre "<Nom du jeu>"`
     Site affiché à `--largeur` pixels (1280 par défaut), pages recadrées sur la colonne du contenu, A4,
     fond du site jusqu'en bas, numéros de page. Rien n'est coupé au milieu d'un paragraphe ou d'une image ;
     un bloc insécable (section Google Sites) peut laisser le bas d'une page vide. Images téléchargées à
     part, bannières de cookies retirées, barres épinglées non répétées. Les textes du bandeau pleine largeur
     (nom du site, menu) sont coupés par le recadrage.
   - **Seulement si la page contient beaucoup d'autre chose** (commentaires, publicités, plusieurs jeux) ou si
     le rendu fidèle est raté : `--xpath "<xpath>"` à la place de `--fidele`, seul le bloc des règles est
     gardé, mise en page simple (`//article`, `//main`, `//*[@id="rules"]`,
     `//div[contains(@class,"entry-content")]` ; sites différents : `//main | //div[@id="rules"]`). Le dire
     à l'utilisateur.
   - Dans tous les modes : aucun lien cliquable ni ligne « Source » ; le lien va dans la note du jeu.
   - **Page Notion** (`*.notion.site`, `notion.so`, `app.notion.com`) : ni la lecture de la page ni
     `--fidele` ne donnent tout (chargement au défilement, navigateur en arrière-plan bloqué). Faire :
     `python -I -X utf8 <skill>/scripts/notion_html.py "<lien Notion>" "<travail>/regles.html"`, puis
     `page_pdf.py "<travail>/<nom>.pdf" "file:///<travail>/regles.html" --xpath "//body" --titre "<Nom du jeu>"`.
     Il signale les sous-pages non incluses (à ajouter comme pages de plus) et les blocs d'un type inconnu.
3. Vérifier le bilan du script : caractères source / PDF (alerte sous 95 %, sous 90 % en `--fidele` où la
   source compte aussi menus et bandeau), images source / PDF, images non téléchargées, liens restants.
   Puis regarder **une seule image** : planche de toutes les pages en vignettes (~60 dpi ; images, tableaux,
   rien de coupé, pas de barre répétée), et comparer le début et la fin du texte du PDF avec la page web.
   Corriger (XPath, page oubliée, `--largeur`) et relancer si besoin.
