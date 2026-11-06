# Skills Claude — Analyse offre vs CV

**Propriétaire** : Augustin Beaumont

Skills Claude orientés carrière et recherche d'emploi. Chaque skill guide Claude à travers une méthode qui produit un livrable concret, pas une fiche de connaissances.

## Philosophie

- Chaque skill produit un résultat visible (analyse, comparatif, document, plan). Ce que Claude sait déjà n'a pas sa place.
- La fenêtre de contexte est un bien commun : n'inclure que ce que Claude ne sait pas déjà.
- Transmettre une méthode, pas des scripts. Les scripts dans `scripts/` restent l'exception ; les modèles éprouvés vont dans `references/`.
- Suivre la spécification officielle des plugins Claude Code.

## Organisation

`plugins/<plugin>/skills/<skill>/` : un dossier par plugin et par skill. À la racine, `.claude-plugin/` contient **uniquement** `marketplace.json` (un `plugin.json` à la racine ferait passer tout le dépôt pour un plugin). `README.md` est la présentation publique. `LICENSE` est sous MIT. Les dossiers font foi : ce fichier ne liste ni plugins, ni skills, ni compteurs.

Un plugin contient `.claude-plugin/plugin.json` (name, version, description, author), `.claude-plugin/icon.png` (carré, 512 à 2048 px) et découvre automatiquement ses `skills/`. Chaque skill est aussi appelable en commande slash `/<nom-du-skill>` : ne pas créer de dossier `commands/` qui le doublerait. Les tests du plugin vont dans `evals/`.

## Ajouter un plugin

1. `mkdir -p plugins/mon-plugin/{.claude-plugin,skills,evals}`
2. Créer `.claude-plugin/plugin.json` :
   ```json
   {
     "name": "mon-plugin",
     "version": "1.0.0",
     "description": "Ce que fait le plugin.",
     "author": { "name": "Augustin Beaumont", "url": "https://github.com/augustinbmt" }
   }
   ```
3. Ajouter les skills dans `plugins/mon-plugin/skills/`, chacun avec son SKILL.md.
4. Ajouter une entrée dans `.claude-plugin/marketplace.json` :
   ```json
   { "name": "mon-plugin", "description": "...", "source": "./plugins/mon-plugin", "category": "productivity" }
   ```
5. Ajouter une icône `.claude-plugin/icon.png`.
6. Mettre à jour le tableau du README.md.

**Catégories** : `development`, `design`, `productivity`, `testing`, `security`, `database`, `monitoring`, `deployment`

## Créer un skill

[`SKILL_SHAPE.md`](SKILL_SHAPE.md) est le guide de rédaction de référence. Pour démarrer : le [skill-creator d'Anthropic](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), ou demander à Claude « Crée un nouveau skill pour [cas d'usage] ».

- **Tout ce qui est critique va dans SKILL.md.** Si l'agent ne doit pas sauter une étape, elle est dans le corps du skill, pas dans `references/`.
- **Le reste** : `scripts/` pour les outils exécutés sans être lus, `references/` pour les variantes ou la doc optionnelle, `assets/` pour les modèles copiés dans le projet de l'utilisateur.
- **Frontmatter** : `name` identique au nom du dossier, `description` sans chevrons et avec des phrases déclencheuses ; clés optionnelles : `license`, `compatibility`, `allowed-tools`, `metadata`.

## Fichiers partagés entre skills

Le modèle du brief de lettre existe en deux exemplaires : `lettre-motivation/SKILL.md` (canonique) et `analyse-offre-vs-cv/references/brief-lettre.md` (copie, pour que l'analyse marche seule). Toute modification se fait dans les deux ; `bin/skill-lint` échoue s'ils diffèrent.

## Versions

Augmenter `version` dans `plugins/<plugin>/.claude-plugin/plugin.json` à chaque changement visible par les utilisateurs (correctif : 1.0.1, nouvelle fonction : 1.1.0, changement de comportement incompatible : 2.0.0), sinon les installations existantes ne voient pas la mise à jour. `claude plugin tag plugins/<plugin> --push` crée le tag de version correspondant.

## Niveau de qualité

Avant de commiter un skill :
- `./bin/skill-lint` passe sans erreur ;
- `./bin/test-detecteur` passe (détecteur de texte caché, nécessite `pypdf` et `python-docx`) ;
- `claude plugin validate --strict .` et `claude plugin validate --strict plugins/<plugin>` passent ;
- après un changement de comportement, les evals tournent : `claude plugin eval ./plugins/<plugin> --scaffold --allow-tools Bash WebSearch` ;
- il produit un livrable concret ;
- il a été testé sur un cas réel ;
- il est assez précis pour que l'agent n'ait pas à improviser.

## Installer les plugins

Via le marketplace : voir « Démarrage rapide » dans le README. La CI (`.github/workflows/skill-lint.yml`) lance skill-lint, test-detecteur et la validation stricte à chaque push. En local, sans installation : `claude --plugin-dir ./plugins/carriere`. Redémarrer Claude Code après une installation.
