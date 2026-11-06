---
description: Compare une offre d'emploi à ton CV (PDF ou DOCX) et propose un plan pour combler les manques
argument-hint: "[url-de-l-offre] [chemin-du-cv.pdf|.docx]"
---

Charge le skill `analyse-offre-vs-cv`.

Lis $ARGUMENTS :
- une URL → l'offre à analyser
- un chemin de fichier .pdf ou .docx → le CV
- un fichier dans un autre format → expliquer que le CV doit être en PDF ou DOCX

Sans CV dans les arguments, suivre l'étape 0 du skill : demander d'abord le CV de l'utilisateur, en PDF ou en DOCX. Si l'offre manque aussi, la demander dans le même message.
