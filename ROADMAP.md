# Feuille de route

État au 7 novembre 2026, version 1.1.0. Cocher une ligne quand elle est faite, avec la version qui l'apporte.

## 1. Failles à corriger (priorité)

- [x] **Dépendances du détecteur** (1.1.0) : DOCX lu avec Python seul ; dépendances PDF déclarées (`compatibility`, README), installation proposée avec accord.
- [x] **Angles morts du détecteur PDF** (1.1.0) : méthode OCR (page affichée lue par tesseract, comparée au texte extrait) ; méthode de secours avec mode invisible, contraste et aplats de fond.
- [x] **Angles morts du détecteur DOCX** (1.1.0) : en-têtes, pieds de page, notes, styles, couleurs de thème, fonds, texte alternatif, suivi des modifications.
- [ ] **Injections visibles** : repérer les phrases suspectes (« ignore tes consignes », « score de 100 % »…) comme « à vérifier », sans les traiter automatiquement comme des injections.
- [ ] **Pages d'offres** : repérer le texte caché d'une page lue avec le navigateur (éléments masqués, transparents, minuscules, hors écran).
- [ ] **CV scanné en image** : prévenir que la détection est limitée ; option d'OCR.
- [ ] **Ancien commit avec l'email** (`a81b5db`) : demande de purge à GitHub Support, ou suppression et recréation du dépôt.
- [ ] **CI** : figer la version de Claude Code et les actions GitHub ; Dependabot pour proposer les mises à jour.
- [ ] **Evals** : premier tour en `--runs 1`, puis calibrer les seuils et les juges.
- [ ] **`contrats.md`** : alerte de skill-lint quand la date de vérification dépasse 6 mois.

## 2. Tests restants

- [ ] Les 8 evals, dont la stabilité du score sur 3 lancements.
- [ ] Installation depuis GitHub : `/plugin marketplace add augustinbmt/skills-analyse-offre-vs-cv`.
- [ ] Commandes slash avec arguments : `/analyse-offre-vs-cv <url> <cv>`.
- [ ] Détecteur lancé par Claude pendant une analyse, sur une machine sans `pypdf` ni `tesseract` (proposition d'installation).
- [ ] Offre en anglais et lettre en anglais.
- [ ] Welcome to the Jungle ; LinkedIn sans être connecté.
- [ ] Skills importés dans claude.ai (dossiers zippés).

## 3. Améliorations

### Fiabilité
- [ ] Bouton de lancement manuel des evals dans la CI, avec plafond de coût (`--max-cost-usd`).
- [ ] Exemple de sortie anonymisé dans `examples/`.

### Nouvelles fonctions
- [ ] Suivi des candidatures dans un tableau (offre, score, date limite, statut, lettre envoyée).
- [ ] Comparer et classer plusieurs offres d'un coup.
- [ ] Skill `adapter-cv` : réécrire le CV pour une offre, sans rien inventer.
- [ ] Skill `preparation-entretien` : questions probables et réponses tirées du parcours.
- [ ] Version courte de la lettre pour les formulaires en ligne, version anglaise.
- [ ] Mail de relance une semaine après la candidature.

### Présentation du dépôt
- [ ] Publier la version (`claude plugin tag plugins/carriere --push`) avec un `CHANGELOG.md`.
- [ ] Badge CI dans le README, sujets GitHub (`claude-skills`, `claude-code`, `job-search`, `cv`).
