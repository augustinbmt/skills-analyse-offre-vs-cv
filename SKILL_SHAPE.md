# Forme d'un skill

Comment écrire un `SKILL.md` que Claude lit comme un contrat (objectif, méthode, critère de réussite) et non comme un tutoriel.

Ce guide applique la [spécification Agent Skills](https://agentskills.io/specification) et le [skill-creator d'Anthropic](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) aux conventions de ce dépôt. En cas de doute, la spécification fait foi.

## Principes

**Économiser le contexte.** Une fois activé, tout le corps du skill entre dans le contexte de Claude. Pour chaque phrase : *Claude se tromperait-il sans elle ?* Si non, la couper. Ne pas expliquer ce que Claude sait déjà.

**Des méthodes plutôt que des réponses.** Un skill enseigne comment traiter une classe de problèmes, pas la réponse à un cas précis.

**Adapter la précision à la fragilité.** Laisser de la liberté là où plusieurs approches se valent ; être prescriptif là où l'ordre compte ou bien là où une erreur coûte cher (commandes exactes, séquences, formats de sortie).

**Des choix par défaut, pas des menus.** Quand plusieurs outils conviennent, en imposer un par défaut et citer brièvement l'alternative.

**Expliquer pourquoi.** Une règle justifiée permet à Claude de l'appliquer aux cas imprévus. Réserver les « toujours » et « jamais » aux vraies contraintes.

**Partir d'une vraie expérience.** Écrire le skill après avoir réellement fait la tâche, avec les corrections de l'utilisateur. Puis le tester sur un cas réel et le réviser.

## Le champ `description`

C'est le seul champ que Claude lit avant de décider d'activer le skill. Claude a tendance à sous-déclencher : la description doit être *insistante*, pas neutre.

```yaml
# Trop neutre
description: Compare une offre d'emploi et un CV.

# Insistante : se déclenche même sans le mot « analyse »
description: Compare une offre d'emploi et un CV... Utiliser dès que l'utilisateur partage une offre avec son CV, ou demande « est-ce que je corresponds à ce poste », « qu'est-ce qui me manque »...
```

Commencer par ce que fait le skill et quand l'utiliser, puis ajouter les phrases que l'utilisateur tape réellement. 1024 caractères maximum, sans chevrons.

## Le corps

Pas de structure imposée. La plupart des skills de ce dépôt contiennent :

- un court chapeau sous le titre (à quoi sert le skill) ;
- des étapes à l'impératif ;
- la structure exacte du livrable ;
- les pièges connus ;
- ce qui définit un résultat réussi.

## Organisation en plusieurs fichiers

```
mon-skill/
├── SKILL.md        # obligatoire, moins de 500 lignes
├── references/     # variantes, documentation optionnelle
├── assets/         # modèles copiés dans le projet de l'utilisateur
└── scripts/        # outils exécutés sans être lus
```

Tout ce qui est indispensable reste dans SKILL.md.

## Check-list de rédaction

- [ ] `name` en kebab-case, identique au nom du dossier, 64 caractères maximum
- [ ] `description` insistante, avec phrases déclencheuses, sans chevrons, 1024 caractères maximum
- [ ] Étapes critiques présentes dans SKILL.md
- [ ] Moins de 500 lignes
- [ ] Testé sur au moins un cas réel
- [ ] `./bin/skill-lint` passe
