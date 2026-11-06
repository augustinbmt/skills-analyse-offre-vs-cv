# Skills Claude — Analyse offre vs CV

Skills Claude orientés carrière et recherche d'emploi. Chaque skill guide Claude à travers une méthode qui produit un livrable concret : une analyse, un comparatif, un plan d'action.

## Démarrage rapide

```bash
# Ajouter le marketplace (une seule fois)
/plugin marketplace add augustinbmt/skills-analyse-offre-vs-cv

# Installer le plugin
/plugin install carriere@augustin-skills
```

Ensuite, il suffit de demander à Claude : les skills installés se déclenchent automatiquement à partir du langage naturel. Tu peux aussi les appeler par leur commande slash.

## Plugins

### Carrière

| Plugin | Skills | Ce qu'il fait |
|---|---|---|
| carriere | analyse-offre-vs-cv | Résume les prérequis d'une offre d'emploi, les compare au CV dans un tableau ✅/🟡/🟠/🔴 et propose un plan pour combler les manques avant la date limite |

## Skills

### analyse-offre-vs-cv

**Entrées** : le lien d'une offre (Business France V.I.E, LinkedIn, Welcome to the Jungle, Indeed…) ou son texte, et **ton** CV en PDF, en DOCX ou en texte collé.

Le skill marche pour n'importe quel métier et ne présuppose aucun profil. Si tu ne donnes pas ton CV, Claude te le demande avant de commencer. Si un CV a déjà été utilisé dans la conversation, il te demande s'il faut le reprendre ou en prendre un autre : tu peux changer de CV (version mise à jour, autre métier visé) à tout moment.

**Sortie** :
1. **L'offre en bref** : poste, lieu, contrat, rémunération, date limite et jours restants, missions, prérequis (obligatoires ou souhaités).
2. **Comparatif** : tableau prérequis / profil / niveau, avec des preuves tirées du CV et un verdict honnête.
3. **Comment combler les manques** : actions faisables avant la date limite, montée en compétences à moyen terme, pistes alternatives.

**Phrases qui le déclenchent** : « compare mon CV à cette offre », « est-ce que je corresponds à ce poste ? », « qu'est-ce qui me manque pour ce job ? »

**Commande** : `/analyse-offre-vs-cv https://… ./mon-cv.pdf`. Sans le chemin du CV, Claude te le demande.

Les sites qui se chargent en JavaScript sont lus via le navigateur quand une simple récupération de la page ne suffit pas.

## Autres installations

**Claude Code, sans marketplace** : copier `plugins/carriere/skills/analyse-offre-vs-cv/` dans `~/.claude/skills/`, ou charger le plugin en local avec `claude --plugin-dir ./plugins/carriere`.

**Claude (claude.ai / app)** : zipper le dossier `analyse-offre-vs-cv` et l'importer dans Paramètres → Capacités → Skills.

## Philosophie

**Chaque skill produit quelque chose.** Pas de fiches de connaissances : uniquement des méthodes de travail qui aboutissent à un livrable.

**Transmettre une méthode, pas des scripts.** Les skills décrivent quoi faire ; Claude adapte l'exécution à ton environnement.

## Créer son propre skill

Utilise le [skill-creator officiel d'Anthropic](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) ou demande à Claude : « Crée un nouveau skill pour [cas d'usage] ».

Voir [SKILL_SHAPE.md](SKILL_SHAPE.md) pour la forme attendue d'un skill et [CLAUDE.md](CLAUDE.md) pour les conventions du dépôt. Avant de commiter, lance `./bin/skill-lint`.

## Licence

MIT
