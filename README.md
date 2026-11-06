# skills-analyse-offre-vs-cv

Skill Claude qui analyse une offre d'emploi par rapport à un CV.

À partir d'un lien d'offre (ou de son texte) et d'un CV (PDF ou DOCX), le skill :

1. **résume l'offre** : poste, lieu, contrat, rémunération, missions, prérequis et date limite de candidature ;
2. **compare les prérequis au CV** dans un tableau (✅ couvert, 🟡 partiel, 🟠 insuffisant, 🔴 absent) ;
3. **propose des solutions** pour combler les manques, à trois échéances : avant la date limite, à moyen terme, et pistes alternatives.

Il gère les sites d'offres qui se chargent en JavaScript (Business France V.I.E, Welcome to the Jungle, LinkedIn…) en passant par le navigateur quand une simple récupération de la page ne suffit pas.

## Contenu

```
analyse-offre-vs-cv/
└── SKILL.md   # instructions du skill
```

## Installation

**Claude (claude.ai / app)** : Paramètres → Capacités → Skills → importer le dossier `analyse-offre-vs-cv` (zippé).

**Claude Code** : copier le dossier dans `~/.claude/skills/` (ou `.claude/skills/` à la racine d'un projet).

## Utilisation

Envoyer à Claude le CV et le lien de l'offre, par exemple :

> Voici mon CV et l'offre https://mon-vie-via.businessfrance.fr/offres/XXXXXX : résume les prérequis, compare avec mon profil et dis-moi comment combler les manques.
