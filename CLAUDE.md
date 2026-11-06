# Skills Claude — Analyse offre vs CV

**Propriétaire** : Augustin Beaumont

Skills Claude orientés carrière et recherche d'emploi. Chaque skill guide Claude à travers une méthode qui produit un livrable concret, pas une fiche de connaissances.

## Philosophie

- Chaque skill produit un résultat visible (analyse, comparatif, document, plan). Ce que Claude sait déjà n'a pas sa place.
- La fenêtre de contexte est un bien commun : n'inclure que ce que Claude ne sait pas déjà.
- Transmettre une méthode, pas des scripts. Les scripts dans `scripts/` restent l'exception ; les modèles éprouvés vont dans `references/`.
- Suivre la spécification officielle des plugins Claude Code.

## Organisation

`plugins/<plugin>/skills/<skill>/` : un dossier par plugin et par skill. `.claude-plugin/` contient `marketplace.json` et `plugin.json`. `README.md` est la présentation publique. `LICENSE` est sous MIT. Les dossiers font foi : ce fichier ne liste ni plugins, ni skills, ni compteurs.

Un plugin contient `.claude-plugin/plugin.json` (name, description, author) et découvre automatiquement ses `skills/`. Les commandes slash vont dans `commands/`.

## Ajouter un plugin

1. `mkdir -p plugins/mon-plugin/{.claude-plugin,skills,commands}`
2. Créer `.claude-plugin/plugin.json` :
   ```json
   {
     "name": "mon-plugin",
     "description": "Ce que fait le plugin.",
     "author": { "name": "Augustin Beaumont", "url": "https://github.com/augustinbmt" }
   }
   ```
3. Ajouter les skills dans `plugins/mon-plugin/skills/`, chacun avec son SKILL.md.
4. Ajouter une entrée dans `.claude-plugin/marketplace.json` :
   ```json
   { "name": "mon-plugin", "description": "...", "source": "./plugins/mon-plugin", "category": "productivity" }
   ```
5. Mettre à jour le tableau du README.md.

**Catégories** : `development`, `design`, `productivity`, `testing`, `security`, `database`, `monitoring`, `deployment`

## Créer un skill

[`SKILL_SHAPE.md`](SKILL_SHAPE.md) est le guide de rédaction de référence. Pour démarrer : le [skill-creator d'Anthropic](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), ou demander à Claude « Crée un nouveau skill pour [cas d'usage] ».

- **Tout ce qui est critique va dans SKILL.md.** Si l'agent ne doit pas sauter une étape, elle est dans le corps du skill, pas dans `references/`.
- **Le reste** : `scripts/` pour les outils exécutés sans être lus, `references/` pour les variantes ou la doc optionnelle, `assets/` pour les modèles copiés dans le projet de l'utilisateur.
- **Frontmatter** : `name` identique au nom du dossier, `description` sans chevrons et avec des phrases déclencheuses ; clés optionnelles : `license`, `compatibility`, `allowed-tools`, `metadata`.

## Niveau de qualité

Avant de commiter un skill :
- `./bin/skill-lint` passe sans erreur ;
- il produit un livrable concret ;
- il a été testé sur un cas réel ;
- il est assez précis pour que l'agent n'ait pas à improviser.

## Installer les plugins

Via le marketplace : voir « Démarrage rapide » dans le README. En local, sans installation : `claude --plugin-dir ./plugins/carriere`. Redémarrer Claude Code après une installation.
