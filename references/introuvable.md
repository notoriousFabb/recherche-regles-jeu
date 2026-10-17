# Jeu japonais introuvable par son nom en lettres latines

Cas fréquent pour un jeu du Game Market en cours ou tout juste passé : la fiche n'a que le titre japonais
(« Cosmo Chauffeur » → コスモ・ショーファー) et les moteurs de recherche ne connaissent pas encore le jeu.
Avant de conclure « aucun résultat » :

1. **Index du Game Market** : s'il existe, regarder d'abord
   `<Ludothèque>/_outils/game-market-<année>-<printemps|automne>.md` (`grep -i "<nom>"`).
2. **Vidéos et listes de nouveautés** : chercher le nom **entre guillemets sur YouTube** dans Chrome
   (`https://www.youtube.com/results?search_query=%22<nom>%22`). Les vidéos « Tokyo Game Market preview /
   anticipated » (ThinkerThemer, Crash Octopus…) ont un chapitre par jeu. Aussi : listes BGG « Tokyo Game
   Market preview » (geeklists), blogs de boutiques (Red Goose Games…).
   **Lire les résultats en texte, sans capture d'écran** (JavaScript dans la page : texte des blocs
   `ytd-video-renderer`, chapitres compris) : le titre du chapitre contient souvent le titre japonais
   (« Kubaru Te Miru Me (配る手見る目) »), ce qui évite d'ouvrir la vidéo. Il compte comme « lu sur une source ».
   **Chapitres = index du Game Market** : la description d'une vidéo « top 20 / anticipated » (lue une fois,
   en texte) donne les titres de tous ses jeux. Les garder dans le fichier d'index ci-dessus (tableau : titre
   latin, titre japonais, chapitre, fiche, règles récupérées) ; quand un jeu de l'index est trouvé, compléter
   sa ligne.
3. **Lire le titre sur la boîte** (seulement si le chapitre ne le donne pas) : ouvrir la vidéo au chapitre,
   puis (JavaScript) `v=document.querySelector('video'); v.muted=true; v.currentTime=<secondes>; v.pause()`,
   **une** capture, zoom sur la boîte. Titre, auteur et illustrateur (souvent imprimés en bas) comptent comme
   « lus sur une source ».
4. **Game Market avec ce titre** : chercher aussi un **mot seul et distinctif** du titre, sans `・` ni espaces
   (`ショーファー` plutôt que `コスモ・ショーファー`). Un mot trop courant (`パレード`, `コスモ`) donne trop de
   résultats.
5. Toujours rien : dire où et avec quels noms on a cherché, et demander une piste (titre de la boîte,
   éditeur, auteur, lien, vidéo où le jeu apparaît).
