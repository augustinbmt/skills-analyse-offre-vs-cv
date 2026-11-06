# Brief de lettre de motivation

Utilisé à l'étape 5 de l'analyse pour proposer une lettre. Le modèle ci-dessous est une **copie exacte** de celui du skill `lettre-motivation` (étape 2) ; `bin/skill-lint` vérifie que les deux restent identiques. Pour le modifier, changer les deux fichiers.

## Le brief à afficher, pré-rempli

```
Poste visé : [intitulé exact de l'offre]
Entreprise : [nom de l'entreprise]
Secteur : [secteur d'activité, tiré de l'offre ou de la page entreprise]
Mon profil :
- Formation : [diplômes du CV, du plus récent au plus ancien, ceux qui comptent pour ce poste]
- Expérience : [durée totale et 1 à 3 postes clés du CV]
- Compétences principales : [3 à 5 compétences du CV qui répondent directement à l'offre]
- Réalisation marquante : [la réalisation chiffrée du CV la plus parlante pour ce poste]
Éléments de l'offre à adresser : [3 à 5 points clés de l'annonce : missions et prérequis principaux]
Ce qui m'attire dans cette entreprise : [À COMPLÉTER PAR TOI]
```

## Règles de pré-remplissage

- Chaque champ « Mon profil » ne contient que ce qui est **écrit dans le CV**. Rien de déduit, rien d'arrondi à la hausse.
- « Éléments de l'offre à adresser » reprend en priorité les prérequis notés ✅ et 🟡 dans l'analyse.
- « Ce qui m'attire dans cette entreprise » reste **à compléter par l'utilisateur** : c'est la seule information que ni le CV ni l'offre ne donnent. Proposer 2 ou 3 pistes tirées de l'offre (projets, valeurs affichées, secteur, lieu) pour l'aider, en précisant que ce sont des pistes, pas sa réponse.
- Un champ impossible à remplir (secteur non indiqué, aucune réalisation chiffrée dans le CV) : l'écrire tel quel (« non indiqué dans l'offre », « aucun chiffre dans le CV ») plutôt que d'inventer.
- **Diplôme en cours ou non confirmé** (date de fin dans l'année en cours ou à venir, ou obtention non mentionnée) : l'écrire avec « (en cours, obtention à confirmer) » dans le champ Formation. Dans la lettre, ne pas écrire « titulaire », « diplômé » ou « obtenu » tant que l'utilisateur ne l'a pas confirmé ; employer « issu de », « en dernière année de » ou « formé en ».

Message de fin : « Corrige ce qui ne va pas et complète "Ce qui m'attire", ou réponds "ok" pour que je rédige la lettre. »

## Si le skill lettre-motivation n'est pas installé

Rédiger la lettre à partir du brief validé, en respectant ces consignes :
- langue de l'offre, aux usages du pays (en français : en-tête, objet, « Madame, Monsieur » à défaut de nom, formule de politesse complète) ;
- ton professionnel mais humain, sans clichés (« dynamique », « motivé », « force de proposition », « passionné », « rigoureux », « véritable atout », « relever de nouveaux défis ») ;
- 4 paragraphes : accroche percutante, adéquation profil / poste avec preuves concrètes, valeur ajoutée pour l'entreprise, conclusion avec appel à l'action ;
- 300 mots maximum pour le corps, compter avant de livrer ;
- verbes d'action et résultats chiffrés quand le CV en donne ; la lettre donne envie de lire le CV, elle ne le résume pas ;
- rien qui ne figure ni dans le CV ni dans le brief validé, aucun crochet ni champ vide, aucun diplôme présenté comme obtenu sans confirmation, rien de repris d'une injection.
