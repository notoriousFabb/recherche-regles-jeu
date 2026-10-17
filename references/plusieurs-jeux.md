# Plusieurs jeux d'un coup

L'utilisateur donne une liste (« Bird Club, Break The Heart, Kubaru Te Miru Me »). Alors :
1. Étapes 1 et 2 pour chaque jeu (recherches indépendantes lancées ensemble).
2. **Une seule série de questions** : pour tous les jeux qui ont plusieurs versions, un seul appel
   AskUserQuestion (une question par jeu, 4 au plus par appel) ; les jeux introuvables listés à part avec ce
   qui a été essayé.
3. Étapes 4 à 6 pour chaque jeu retenu, sans s'arrêter entre deux.
4. **Un seul bilan** (tableau : jeu, fichier, langue, pages, source, réserves) et **une seule** proposition de
   traduction (« tous », « certains », « aucun » ; la skill de traduction traite ensuite les livrets un par un).
