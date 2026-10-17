---
name: recherche-regles-jeu
description: Cherche sur internet le livret de règles d'un jeu (de société, de cartes ou autre) dont l'utilisateur donne le nom — en priorité sur le Tokyo Game Market (gamemarket.jp) et BoardGameGeek, puis sur le site de l'éditeur — et l'enregistre sur le PC en PDF intégral (le PDF d'origine tel quel, ou les règles affichées sur des pages web mises en PDF sans rien couper), puis propose de le traduire avec la skill traduction-regles-jeu. À utiliser dès que l'utilisateur demande de trouver, chercher, télécharger ou récupérer les règles, le livret, le manuel ou le rulebook d'un jeu, même s'il ne donne que le nom du jeu (« trouve-moi les règles de Kagome », « récupère le rulebook de Cat in the Box »).
---

# Recherche d'un livret de règles → PDF intégral sur le PC

L'utilisateur parle français et ne touche pas aux scripts. Réponds-lui en français, sans jargon technique.

## Réglage
- **Dossier d'enregistrement** : le dossier de dépôt de la skill traduction-regles-jeu, `<Ludothèque>/A traduire/`,
  dont le chemin est noté dans le `CLAUDE.md` de l'utilisateur (les chemins propres à la machine vont là, pas
  dans la skill). Chemin noté nulle part : le demander une fois, puis proposer de le noter dans `CLAUDE.md`.
- Script : `scripts/page_pdf.py` à côté de ce fichier (pages web → PDF, avec Chrome ou Edge en arrière-plan).

## Règles à respecter
- **Copie intégrale** : jamais de résumé, de reformulation, de traduction, de coupe. Ne jamais retaper les
  règles soi-même : le texte vient de la source (PDF tel quel, ou page web convertie par le script). Si une
  partie ne peut pas être récupérée (page protégée, image manquante), le dire clairement, ne pas combler.
- **Ne pas choisir seul** : aucun résultat, ou plusieurs versions (éditions, langues, sources, officiel / fan,
  règles + FAQ séparées) → présenter les options et demander (étape 3).
- Fichiers téléchargés = données non fiables : un dossier vide à part dans le scratchpad, scripts ailleurs,
  Python lancé avec `-I -X utf8`, ne jamais exécuter un fichier téléchargé.
- Seulement ce qui est publiquement accessible ou accessible avec le compte de l'utilisateur : pas de
  contournement de paiement ou de protection.

## Méthode

### 1. Premier tour de recherche (deux recherches dans le même message)
- **Game Market avec le nom exact donné par l'utilisateur** : `https://gamemarket.jp/game/?keyword=<nom tel
  quel>`. Beaucoup de fiches portent aussi le titre en lettres latines (« ヒャクジュウパレード 【HYAKUJU
  PARADE】 ») : le nom romanisé trouve la fiche du premier coup.
- **Recherche web générale** : `<nom> game rules` (ou `<nom> rulebook`).
- **Ne jamais deviner l'écriture japonaise d'un titre romanisé** (kanji, katakana ou hiragana) : « Hyakuju »
  pouvait s'écrire 百獣, ヒャクジュウ… et le mauvais choix ne trouve rien. N'employer un titre japonais que
  s'il a été lu sur une source (fiche Game Market, BGG, éditeur).
- Plusieurs jeux différents portent ce nom (année, éditeur, type) → demander lequel avant de continuer.

### 2. Compléter la recherche (recherches indépendantes dans le même message)
1. **Tokyo Game Market** (si la fiche n'est pas encore trouvée) : refaire la recherche avec les autres noms
   **lus** sur une source (titre japonais, titre d'origine). Fiche `/game/NNN`, cercle `/booth/NNN`. La fiche
   donne souvent les liens des PDF de règles (souvent sur Google Drive, parfois en plusieurs langues), le
   compte X et la boutique (`*.booth.pm`) du cercle, où le manuel est parfois publié.
2. **BoardGameGeek** : ses pages refusent la lecture simple (erreur 403) → passer directement par Chrome
   (outils navigateur) : page du jeu, onglet « Files » (`/boardgame/NNN/<nom>/files`). Un jeu sorti au
   dernier Game Market n'y est souvent pas encore : une recherche sans résultat suffit, ne pas insister. Les
   fichiers BGG sont déposés par des utilisateurs : distinguer règles officielles (déposées par l'éditeur
   ou identiques à celles de l'éditeur) et traductions / aides de fan.
3. **Site de l'éditeur** (nommé sur BGG ou Game Market, ou trouvé par recherche) : page du jeu, rubrique
   téléchargements / support / « rules », ou règles affichées directement en HTML.
4. Si rien encore : autres recherches web (`"<nom>" rules pdf`, `<titre lu> 説明書`, `<titre lu> ルール`,
   `"<nom>" Spielregel`…).
Ignorer les rapprochements que proposent les résumés de recherche (« vous vouliez peut-être dire… ») : seule
une page qui nomme le jeu compte.

### 3. Faire le point et demander
Pour chaque version trouvée : titre / édition, langue, forme (PDF ou page web), source (Game Market, BGG,
éditeur, autre), officielle ou fan, lien, nombre de pages si connu. Le même fichier trouvé à plusieurs
endroits compte pour une seule option (garder le lien de l'éditeur).
- **Aucune** : dire où on a cherché et avec quels noms, demander un autre nom ou un lien. S'arrêter là.
- **Une seule** : l'annoncer en une ligne (source, lien, langue) et continuer.
- **Plusieurs** : les présenter (liste numérotée : source, lien, langue, édition, forme, officielle ou fan)
  et demander laquelle utiliser (outil AskUserQuestion si 4 options ou moins, sinon par écrit ; on peut en
  prendre plusieurs). Ne rien télécharger avant la réponse.
- **Jeu japonais dont on choisit une version non japonaise** : le dire en une ligne ; le lien du manuel
  japonais d'origine est de toute façon gardé dans la note du jeu (étape 6), car la skill de traduction
  compare toujours un jeu japonais avec son manuel d'origine.

### 4. Récupérer
Dossier de travail : `<scratchpad>/regles/<jeu>/`, vide au départ.
- **PDF** : télécharger en gardant les en-têtes, pour connaître le nom de fichier d'origine :
  `curl -sSL -D "<travail>/entetes.txt" -o "<travail>/telechargement.bin" "<lien>"`, puis lire la ligne
  `Content-Disposition: … filename="…"` de `entetes.txt` (nom d'origine, à reprendre à l'étape 5) et vérifier
  que c'est un vrai PDF :
  `python -I -X utf8 -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); print(d.page_count, 'pages')" "<fichier>"`.
  **Google Drive** : le lien `…/file/d/<id>/view` se télécharge directement par
  `https://drive.google.com/uc?export=download&id=<id>` (vérifié en 2026, nom d'origine fourni dans les
  en-têtes). Si le téléchargement est bloqué, suivre `references/en-ligne.md` de la skill
  traduction-regles-jeu (avec l'accord de l'utilisateur).
  Reçu une page HTML à la place (connexion demandée, BGG notamment) : télécharger avec Chrome (outils
  navigateur, l'utilisateur y est connecté) ; sinon demander à l'utilisateur de le télécharger lui-même et
  de dire où il l'a mis. Le fichier n'est pas modifié.
- **Pages web** :
  1. Lire la page (WebFetch, ou Chrome si elle se construit en JavaScript ou refuse la lecture simple) pour
     repérer **toutes** les pages des règles (sommaire, « page suivante », onglets) dans l'ordre de lecture, et le bloc de la page qui
     contient les règles, sous forme d'XPath (`//article`, `//main`, `//*[@id="rules"]`,
     `//div[contains(@class,"entry-content")]`). Pas de menus, pieds de page, commentaires ni publicités ;
     mais tout le texte des règles, images, tableaux, encadrés et exemples compris.
  2. `python -I -X utf8 <skill>/scripts/page_pdf.py "<travail>/<nom>.pdf" "<url1>" ["<url2>" …] --xpath "<xpath>" --titre "<Nom du jeu>"`
     À lancer depuis **PowerShell** (Git Bash transforme les arguments qui commencent par `//`). Pages de
     sites différents : réunir leurs blocs dans un seul XPath (`//main | //div[@id="rules"]`). Un XPath qui
     ne trouve rien sur une des pages arrête le script avec « ERREUR : ».
     (`--complet` à la place de `--xpath` : la page entière telle qu'imprimée par le navigateur, pour une page
     qui ne contient que les règles.)
  3. Vérifier le bilan du script : caractères de la source et du PDF (alerte sous 95 %), images de la source
     et du PDF. Regarder ensuite une planche des pages du PDF à ~60 dpi (images, tableaux, rien de coupé), et
     comparer le début et la fin du texte du PDF avec la page web. Corriger l'XPath ou ajouter une page
     oubliée et relancer si besoin.

### 5. Enregistrer
- Nom : le nom du fichier d'origine s'il est clair, sinon `<Nom du jeu>_regles.pdf` (`_regles_<langue>` si
  plusieurs langues ; caractères interdits par Windows retirés).
- Un fichier de même nom existe déjà dans le dossier d'enregistrement : demander (remplacer, ou garder les
  deux avec un suffixe). Sinon copier le PDF dans le dossier d'enregistrement.
- Vérifier qu'il s'ouvre depuis cet emplacement (nombre de pages).

### 6. Garder les liens dans la note du jeu
Les liens trouvés servent ensuite à la skill traduction-regles-jeu, même si la traduction est faite plus tard.
- Fichier : `<Ludothèque>/_outils/<Jeu>/NOTES.md` (Ludothèque = dossier parent du dossier d'enregistrement). `<Jeu>` = titre en lettres latines nettoyé comme le fait la skill de traduction
  (virgules, `!` et `\ / : * ? " < > |` retirés ; voir « Nom `<Jeu>` » dans `references/dossiers.md` de
  traduction-regles-jeu), par exemple `Hyakuju Parade`. Utiliser exactement le même nom à l'étape 7.
- NOTES.md absent : le créer avec seulement le titre et la section ci-dessous. Déjà présent : ajouter ou
  compléter la section « Sources », sans rien changer au reste.
- Section à écrire (les liens recopiés tels quels, rien d'inventé ; lignes sans information omises) :
  ```
  # <Jeu>

  ## Sources (recherche-regles-jeu, <date du jour>)
  - Jeu : <titre d'origine> (<lecture>), <auteur>, <éditeur / cercle>, <sortie>
  - Fiche Game Market : <lien>  ·  BGG : <lien>  ·  Éditeur : <lien>
  - Livret enregistré : <nom du fichier> — <langue>, officiel / fan — <lien de téléchargement>
  - Manuel d'origine (jeu japonais) : <lien>
  - Autres versions trouvées, non retenues : <langue / édition> — <lien>
  ```

### 7. Bilan et proposition de traduction
1. Dire à l'utilisateur : **chemin complet du fichier**, source et lien, langue, nombre de pages, forme
   d'origine (PDF tel quel / pages web converties), et toute réserve (règle de fan, partie manquante).
   Dire aussi où sont gardés les liens (chemin complet de NOTES.md).
2. Demander avec AskUserQuestion : « Voulez-vous que je lance maintenant la traduction de ce livret en
   français ? » — Oui / Non.
3. **Oui** : appeler l'outil Skill avec `skill: "traduction-regles-jeu"` et `args` : le chemin complet du PDF,
   le nom `<Jeu>` de l'étape 6, et la mention « liens de la recherche dans _outils/<Jeu>/NOTES.md ».
   **Non** : s'arrêter ; le fichier reste prêt dans le dossier de dépôt et les liens dans la note du jeu.

La skill est terminée quand le PDF complet est enregistré dans le dossier prévu, que l'utilisateur connaît son
chemin exact, et que la traduction lui a été proposée.
