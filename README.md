# recherche-regles-jeu — skill Claude Code

Trouve sur internet le **livret de règles d'un jeu** dont on donne simplement le nom, et l'enregistre sur le PC
en **PDF intégral** : le PDF de l'éditeur tel quel, ou les règles affichées sur des pages web mises en PDF sans
rien couper. Elle propose ensuite de le traduire en français avec la skill
[traduction-regles-jeu](https://github.com/vinchy1/traduction-regles-jeu).

Il suffit de demander à Claude Code « trouve-moi les règles de Hyakuju Parade ». La skill cherche, vous montre
ce qu'elle a trouvé, télécharge la version choisie, la range dans le dossier de dépôt et garde les liens.

Spécialisée dans les **jeux japonais** (Tokyo Game Market), elle marche aussi pour n'importe quel jeu de
société, de cartes ou autre.

---

## Sommaire
- [Ce qu'elle fait](#ce-quelle-fait)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Déroulement d'une recherche](#déroulement-dune-recherche)
- [Règles pages web → PDF](#règles-pages-web--pdf)
- [La note du jeu](#la-note-du-jeu)
- [Enchaîner avec la traduction](#enchaîner-avec-la-traduction)
- [Contenu du dépôt](#contenu-du-dépôt)
- [Limites connues](#limites-connues)
- [Remarques](#remarques)

---

## Ce qu'elle fait
- **Cherche aux bons endroits** : le [Tokyo Game Market](https://gamemarket.jp) (fiches de jeux japonais, souvent
  avec les PDF de règles de l'auteur), [BoardGameGeek](https://boardgamegeek.com) (onglet « Files »), le site
  de l'éditeur, puis le web en général.
- **Gère les deux formes de règles** : un PDF déjà en ligne (récupéré tel quel, sans aucune modification) ou du
  texte affiché sur des pages web (mis en PDF avec images, tableaux et encadrés).
- **Copie intégrale** : jamais de résumé, de reformulation, de traduction ni de coupe. Le texte vient toujours de
  la source ; ce qui n'a pas pu être récupéré est signalé, jamais comblé.
- **Ne choisit pas à votre place** : aucune règle trouvée, ou plusieurs versions (éditions, langues, sources,
  officielle ou de fan) → elle présente les options avec leur lien et leur source et vous demande.
- **Garde les liens** dans une note du jeu, réutilisée par la skill de traduction (comparaison avec le manuel
  japonais d'origine, par exemple).
- **Propose la traduction** à la fin, et ne la lance que si vous répondez oui.

---

## Installation
1. **Copier la skill** : le dossier `recherche-regles-jeu` dans `~/.claude/skills/`
   (Windows : `C:\Users\<vous>\.claude\skills\`), par exemple :
   ```
   git clone https://github.com/vinchy1/recherche-regles-jeu.git ~/.claude/skills/recherche-regles-jeu
   ```
2. **Python 3 et deux bibliothèques** (vérification des PDF, mise en PDF des pages web) :
   ```
   pip install pymupdf lxml
   ```
3. **Google Chrome ou Microsoft Edge** installé : il sert, en arrière-plan et avec un profil temporaire, à mettre
   les pages web en PDF. Votre navigateur habituel, vos onglets et vos connexions ne sont pas touchés.
4. **Facultatif mais conseillé** :
   - la skill [traduction-regles-jeu](https://github.com/vinchy1/traduction-regles-jeu), pour enchaîner sur la
     traduction ;
   - l'extension **Claude in Chrome** : elle permet de lire les pages de BoardGameGeek (qui refusent la lecture
     simple) et de télécharger un fichier qui demande d'être connecté, avec votre propre session.
5. **Dossier de dépôt** : celui de la skill de traduction, `A traduire` dans votre ludothèque. Notez son chemin
   dans un `CLAUDE.md` à la racine de la ludothèque (par exemple « les PDF à traduire sont déposés dans
   `A traduire/` »). S'il n'est noté nulle part, Claude le demande la première fois et propose de le noter.
   Les chemins propres à votre machine vont là, pas dans la skill.

---

## Utilisation
Ouvrir Claude Code dans la ludothèque (ou son dossier `A traduire`) et demander, par exemple :

> Trouve-moi les règles de Hyakuju Parade

ou, avec la commande directe :

```
/recherche-regles-jeu Cat in the Box
```

Donnez le nom **tel que vous le connaissez** (titre anglais, romanisation, titre japonais) : la skill ne devine
jamais l'écriture japonaise d'un titre romanisé, elle cherche avec votre nom puis avec les titres lus sur les
fiches trouvées. Si plusieurs jeux différents portent ce nom, elle demande lequel.

Exemple réel (octobre 2026) :

> **Vous** : /recherche-regles-jeu Hyakuju Parade
> **Claude** : J'ai trouvé deux versions officielles (fiche Game Market de ヒャクジュウパレード, Bamboo Games) :
> anglais et japonais, toutes deux en PDF sur le Google Drive de l'éditeur. Laquelle voulez-vous ?
> **Vous** : Anglais
> **Claude** : Livret enregistré : `…\A traduire\HYAKUJU_PARADE_English_Rulebook.pdf` (2 pages, copie exacte
> du fichier de l'éditeur). Liens gardés dans `…\_outils\Hyakuju Parade\NOTES.md`. Voulez-vous que je lance la
> traduction ?

---

## Déroulement d'une recherche
1. **Premier tour** (en même temps) : recherche sur Game Market avec le nom exact donné, et recherche web
   générale. Beaucoup de fiches Game Market portent aussi le titre en lettres latines : le nom romanisé les
   trouve du premier coup.
2. **Compléter** : Game Market avec les autres titres lus sur les sources, BoardGameGeek (onglet « Files », par
   le navigateur), site de l'éditeur, autres recherches web (`rules pdf`, `説明書`, `ルール`, `Spielregel`…).
   Les « vous vouliez peut-être dire… » des moteurs de recherche sont ignorés : seule compte une page qui nomme
   le jeu.
3. **Faire le point** : pour chaque version, titre / édition, langue, forme (PDF ou page web), source,
   officielle ou de fan, lien. Le même fichier trouvé à plusieurs endroits ne compte qu'une fois.
   - aucune version → elle dit où et avec quels noms elle a cherché, et vous demande un autre nom ou un lien ;
   - une seule → elle l'annonce et continue ;
   - plusieurs → elle vous les présente et attend votre choix (on peut en prendre plusieurs). Rien n'est
     téléchargé avant.
   - jeu japonais pris dans une autre langue → signalé ; le lien du manuel japonais est gardé quand même.
4. **Récupérer** dans un dossier temporaire :
   - **PDF** : téléchargé avec son nom d'origine, puis vérifié (vrai PDF, nombre de pages). Les liens Google
     Drive se téléchargent directement ; un fichier qui demande d'être connecté (BoardGameGeek) passe par votre
     Chrome, ou vous est demandé.
   - **Pages web** : voir [plus bas](#règles-pages-web--pdf).
5. **Enregistrer** dans le dossier de dépôt, sous le nom d'origine (sinon `<Jeu>_regles.pdf`). Un fichier du
   même nom existe déjà → elle demande (remplacer ou garder les deux).
6. **Garder les liens** dans la [note du jeu](#la-note-du-jeu).
7. **Bilan** (chemin complet du fichier, source, langue, pages, réserves) et **proposition de traduction**.

Les fichiers téléchargés sont traités comme des données non fiables : dossier temporaire à part, jamais
exécutés. La skill ne récupère que ce qui est publiquement accessible (ou accessible avec votre compte) et ne
contourne aucun paiement ni aucune protection.

---

## Règles pages web → PDF
Quand les règles sont affichées sur des pages web, Claude repère toutes les pages des règles (sommaire,
« page suivante », onglets) dans l'ordre de lecture et le bloc de la page qui les contient, puis lance :

```
python -I -X utf8 scripts/page_pdf.py sortie.pdf URL1 [URL2 …] --xpath "//article" --titre "Nom du jeu"
python -I -X utf8 scripts/page_pdf.py sortie.pdf URL --complet
```

- `--xpath` : seul le bloc des règles est gardé (pas de menus, pieds de page, commentaires ni publicités) ;
  plusieurs pages sont réunies dans un seul PDF, chacune commençant sur une nouvelle page avec son adresse.
- `--complet` : la page entière telle que le navigateur l'imprime, pour une page qui ne contient que les règles.
- Les pages sont affichées par Chrome ou Edge en arrière-plan : les contenus construits en JavaScript et les
  images chargées à la demande sont pris en compte.
- **Contrôle d'intégralité** : le script compare le nombre de caractères et d'images de la source et du PDF, et
  alerte s'il manque plus de 5 % du texte ou des images. Claude regarde ensuite un aperçu des pages et compare
  le début et la fin du texte avec la page web.

Sous Windows, lancer le script depuis **PowerShell** : Git Bash transforme les arguments qui commencent par `//`.

---

## La note du jeu
Les liens trouvés sont gardés dans `<Ludothèque>/_outils/<Jeu>/NOTES.md`, le fichier de notes de la skill de
traduction, dans une section « Sources » :

```
# Hyakuju Parade

## Sources (recherche-regles-jeu, 2026-10-17)
- Jeu : ヒャクジュウパレード (Hyakuju Parade), カサギケイタ, バンブーゲームズ (Bamboo Games), Game Market 2026 automne
- Fiche Game Market : https://gamemarket.jp/game/188738
- Livret enregistré : HYAKUJU_PARADE_English_Rulebook.pdf — anglais, officiel — <lien>
- Manuel d'origine (jeu japonais) : <lien>
```

Si la note existe déjà, seule la section « Sources » est ajoutée ou complétée. Même si vous ne traduisez pas
tout de suite, la traduction faite plus tard retrouve ces liens sans refaire la recherche.

---

## Enchaîner avec la traduction
À la fin, Claude demande : « Voulez-vous que je lance maintenant la traduction de ce livret en français ? »
- **Oui** : la skill `traduction-regles-jeu` démarre avec le chemin du PDF, le nom du jeu et la note des liens.
- **Non** : le PDF reste prêt dans `A traduire/` ; il suffira plus tard de demander « traduis Hyakuju Parade ».

Pour que la traduction relise la note des liens, utilisez une version de `traduction-regles-jeu` qui connaît la
section « Sources » de `NOTES.md` (sinon elle refait simplement la recherche des sources).

---

## Contenu du dépôt
```
recherche-regles-jeu/
├── SKILL.md            instructions suivies par Claude
├── README.md           ce fichier
└── scripts/
    └── page_pdf.py     pages web → PDF, avec contrôle d'intégralité
```

---

## Limites connues
- **BoardGameGeek** refuse la lecture simple de ses pages : sans l'extension Claude in Chrome, ses fichiers ne
  sont pas consultables, et ceux qui demandent d'être connecté doivent être téléchargés à la main.
- **Jeux tout juste sortis** (dernier Game Market) : souvent absents de BoardGameGeek et des moteurs de
  recherche ; la fiche Game Market est alors la meilleure source.
- **Google Drive** : un fichier dont le téléchargement est bloqué (lecture seule) n'est récupéré qu'en images,
  avec votre accord, par la méthode de la skill de traduction (`references/en-ligne.md`) : le résultat est un
  livret scanné.
- **Pages web** : le rendu suit la mise en page du navigateur, pas celle du site ; les vidéos et animations ne
  passent pas dans le PDF.
- Testée sous **Windows** (Chrome, PowerShell) ; le script cherche aussi Chrome et Edge sur macOS et Linux.

---

## Remarques
- **Usage personnel** : les livrets restent la propriété de leurs éditeurs ; ne les rediffusez qu'avec leur
  accord.
- Compagnon de [traduction-regles-jeu](https://github.com/vinchy1/traduction-regles-jeu), par
  [vinchy1](https://github.com/vinchy1).
