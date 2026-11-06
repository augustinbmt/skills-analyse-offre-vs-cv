---
name: analyse-offre-vs-cv
description: Résume les prérequis d'une offre d'emploi (URL ou texte collé), la compare au CV de l'utilisateur dans un tableau couvert/partiel/manquant et propose un plan concret pour combler les écarts avant la date limite. Fonctionne pour tout métier ; commence par demander le CV de l'utilisateur s'il ne l'a pas fourni. Utiliser dès que l'utilisateur partage une offre (V.I.E, CDI, stage, alternance, LinkedIn, Welcome to the Jungle, Indeed, Business France), avec ou sans son CV, ou demande « est-ce que je corresponds à ce poste », « compare mon CV à cette offre », « qu'est-ce qui me manque », « mes chances pour ce job », même sans dire « analyse ».
license: MIT
---

# Analyse offre d'emploi vs CV

À utiliser quand l'utilisateur veut savoir s'il correspond à une offre d'emploi et comment combler l'écart. Le skill marche pour n'importe quel métier et n'importe quel profil : il ne présuppose rien sur la personne avant d'avoir lu son CV.

Réponse dans la langue de l'utilisateur (français par défaut), directement dans le chat. Pas de fichier, sauf demande explicite.

## 0. Demander le CV en premier

L'analyse repose entièrement sur le CV de la personne qui utilise le skill. Ne jamais s'appuyer sur un profil supposé, sur un exemple ou sur le CV d'une autre personne.

- **Aucun CV fourni** : avant toute autre action, demander le CV en une question courte. Accepter un PDF ou un DOCX joint, un chemin de fichier, ou le texte collé (un profil LinkedIn copié convient aussi). Demander l'offre dans le même message si elle manque aussi. Ne pas commencer l'analyse sans CV : une comparaison sans profil n'a pas de valeur.
- **Un CV a déjà été donné plus tôt dans la conversation** : demander s'il faut utiliser ce CV ou un autre (CV mis à jour, version adaptée à un autre métier, CV d'une autre personne qu'on aide). Si l'utilisateur dit vouloir changer de CV ou de profil, utiliser le nouveau et oublier l'ancien pour la suite.
- **Seule l'offre est fournie** : la lire pendant que l'utilisateur répond, mais attendre le CV pour comparer.

## 1. Récupérer les deux sources (en parallèle)

**CV**
- PDF : `pdftotext -layout "<chemin>" -`. Si la commande n'existe pas, utiliser `pypdf` en Python. Si le texte sort vide (CV scanné ou en image), lire le PDF visuellement avec Read.
- DOCX : l'extraire avec les outils documentaires disponibles.
- Noter : diplômes et dates, expériences (durée, missions, chiffres), compétences techniques, langues (avec score s'il y en a un), localisation, disponibilité ou type de contrat recherché.

**Offre**
- Essayer d'abord WebFetch sur l'URL.
- Si la page renvoie « Loading... » ou un contenu vide (sites en JavaScript comme mon-vie-via.businessfrance.fr, Welcome to the Jungle, LinkedIn, Indeed), ouvrir l'URL dans le navigateur préféré de l'utilisateur et lire le texte (get_page_text). Charger d'abord la skill du navigateur concerné.
- Si rien ne marche, demander à l'utilisateur de coller le texte de l'offre.
- Relever : intitulé, entreprise, lieu, type de contrat (CDI, V.I.E, stage…), durée, date de début, rémunération, télétravail, **date limite de candidature**, missions, profil demandé (diplôme, années d'expérience, outils, langues, savoir-être). Distinguer ce qui est obligatoire de ce qui est « idéalement » ou « un plus ».

## 2. Structure de la réponse

Commencer par une ou deux phrases qui disent franchement si le profil correspond (bien, en partie, ou peu).

### L'offre en bref
- Une ligne en gras : intitulé, entreprise, lieu, contrat, durée, rémunération. Mettre en évidence la date limite et le nombre de jours restants (calculé depuis la date du jour).
- **Les missions** : 4 à 7 puces, reformulées.
- **Les prérequis** : liste, en séparant l'obligatoire du « idéalement ».

### Comparatif
Tableau `| Prérequis | Ton profil | Niveau |` avec :
- ✅ couvert
- 🟡 partiel ou transposable (dire pourquoi)
- 🟠 insuffisant
- 🔴 absent

Citer des preuves précises tirées du CV (chiffres, outils, projets). Repérer les compétences transférables, même si elles ne portent pas le même nom (par exemple gestion d'un portefeuille clients → relation grands comptes, encadrement d'une équipe en restauration → management d'équipe, supervision d'un parc informatique → observabilité en production).

Terminer par **En résumé** : un décompte approximatif (X critères couverts, Y partiels, Z manquants) et une estimation honnête des chances. Ne pas gonfler l'adéquation.

### Comment combler les manques
Trois horizons :
1. **Avant la date limite** : actions faisables en quelques jours. Une ou deux réalisations démontrables, dans le format qui compte pour ce métier (dépôt GitHub pour un développeur, book pour un designer, étude de cas pour un commercial ou un consultant, mémoire ou article pour un profil recherche), si possible liées à l'expérience actuelle du candidat. Des cours courts et gratuits (citer les vrais noms). Une adaptation du CV et de la lettre, dans la langue de l'offre : accroche, section projets, compétences transférables reformulées, et suppression des mentions qui ne collent pas avec le contrat (par exemple « recherche CDI » pour un V.I.E).
2. **À moyen terme** : certifications pertinentes, de préférence dans la continuité de ce que le candidat maîtrise déjà, et compétences complémentaires.
3. **Stratégie alternative** si l'écart est grand : offres plus alignées, y compris chez la même entreprise, et postes passerelle.

Ajouter les points d'éligibilité propres au contrat si c'est pertinent (V.I.E : moins de 29 ans au départ et JDC effectuée ; visa ; permis).

## 3. Règles
- Être honnête et précis, sans démotiver : chaque manque est suivi d'une action concrète.
- Ne jamais conseiller d'inventer de l'expérience. Le CV peut être reformulé, pas falsifié.
- Paraphraser l'offre plutôt que la recopier.
- Finir par une proposition de suite (monter un projet, réécrire le CV ou la lettre pour cette offre).
