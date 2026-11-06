---
description: Compare une offre d'emploi à ton CV et propose un plan pour combler les manques
argument-hint: "[url-de-l-offre] [chemin-du-cv]"
---

Charge le skill `analyse-offre-vs-cv`.

Lis $ARGUMENTS :
- une URL → l'offre à analyser
- un chemin de fichier (.pdf, .docx) → le CV

Sans CV dans les arguments, suivre l'étape 0 du skill : demander d'abord le CV de l'utilisateur (fichier joint, chemin ou texte collé). Si l'offre manque aussi, la demander dans le même message.
