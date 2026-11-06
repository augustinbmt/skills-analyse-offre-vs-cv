#!/usr/bin/env python3
"""Repère le texte caché d'un CV PDF ou DOCX : ce qu'un humain ne voit pas mais qu'une IA lit.

Usage : python3 reperer-texte-cache.py <cv.pdf|cv.docx>
Sortie : une ligne par passage suspect, « [type] extrait », puis un total.
Code de sortie : 0 si rien de caché, 1 si quelque chose est trouvé, 2 en cas d'erreur.
Dépendances : pypdf pour les PDF, python-docx pour les DOCX.

Ce script ne juge pas le contenu : il signale ce qui est caché. C'est à l'analyse
de dire si le passage s'adresse à une IA. Il ne modifie jamais le fichier.
"""
import re
import sys
import zipfile
from pathlib import Path

INVISIBLES = re.compile("[\U000E0000-\U000E007F​-‏⁠-⁤﻿]")
SEUIL_TAILLE = 4.0      # points : en dessous, illisible à l'œil
SEUIL_BLANC = 0.92      # composantes RGB au-dessus : blanc ou presque


def extrait(texte, n=400):
    texte = " ".join(texte.split())
    return texte if len(texte) <= n else texte[:n] + "…"


def decode_tags(texte):
    """Rend lisibles les caractères Unicode « tags » (U+E0020–U+E007E)."""
    return "".join(chr(ord(c) - 0xE0000) for c in texte if 0xE0020 <= ord(c) <= 0xE007E)


def signaler_invisibles(texte, ou, trouves):
    if INVISIBLES.search(texte):
        cache = decode_tags(texte)
        detail = f" — texte encodé : « {extrait(cache)} »" if cache.strip() else ""
        trouves.append(("unicode-invisible", f"{ou}{detail}"))


# ---------------------------------------------------------------- PDF
def analyser_pdf(chemin):
    from pypdf import PdfReader
    trouves = []
    lecteur = PdfReader(str(chemin))
    meta = lecteur.metadata or {}
    for cle in ("/Subject", "/Keywords", "/Title", "/Creator", "/Producer"):
        val = str(meta.get(cle, "") or "")
        if len(val) > 60:
            trouves.append(("métadonnées", f"{cle[1:]} : « {extrait(val)} »"))
        signaler_invisibles(val, f"métadonnées {cle[1:]}", trouves)

    for num, page in enumerate(lecteur.pages, 1):
        x0, y0, x1, y1 = [float(v) for v in page.mediabox]
        etat = {"blanc": False, "taille": 12.0}
        morceaux = {"blanc": [], "minuscule": [], "hors-page": []}

        def couleur(op, args):
            if op == b"rg" and len(args) == 3:
                etat["blanc"] = all(float(a) >= SEUIL_BLANC for a in args)
            elif op == b"g" and len(args) == 1:
                etat["blanc"] = float(args[0]) >= SEUIL_BLANC
            elif op == b"k" and len(args) == 4:
                etat["blanc"] = all(float(a) <= 1 - SEUIL_BLANC for a in args)

        def visiteur_op(op, args, cm, tm):
            couleur(op, args)

        def visiteur_texte(texte, cm, tm, police, taille):
            if not texte.strip():
                return
            taille_reelle = abs(taille * (tm[0] if tm[0] else 1) * (cm[0] if cm[0] else 1))
            x = tm[4] * cm[0] + cm[4]
            y = tm[5] * cm[3] + cm[5]
            if etat["blanc"]:
                morceaux["blanc"].append(texte)
            elif 0 < taille_reelle < SEUIL_TAILLE:
                morceaux["minuscule"].append(texte)
            elif not (x0 - 5 <= x <= x1 + 5 and y0 - 5 <= y <= y1 + 5):
                morceaux["hors-page"].append(texte)

        texte_page = page.extract_text(visitor_operand_before=visiteur_op, visitor_text=visiteur_texte) or ""
        for type_, liste in morceaux.items():
            joint = " ".join(t.strip() for t in liste if t.strip())
            if joint:
                trouves.append((type_, f"page {num} : « {extrait(joint)} »"))
        signaler_invisibles(texte_page, f"page {num}", trouves)
    return trouves


# ---------------------------------------------------------------- DOCX
def analyser_docx(chemin):
    import docx
    from docx.oxml.ns import qn
    trouves = []
    d = docx.Document(str(chemin))
    cp = d.core_properties
    for nom in ("subject", "keywords", "comments", "title", "category"):
        val = getattr(cp, nom) or ""
        if len(val) > 60:
            trouves.append(("métadonnées", f"{nom} : « {extrait(val)} »"))
        signaler_invisibles(val, f"métadonnées {nom}", trouves)

    corps = d.element.body
    for run in corps.iter(qn("w:r")):
        texte = "".join(t.text or "" for t in run.iter(qn("w:t")))
        if not texte.strip():
            continue
        rpr = run.find(qn("w:rPr"))
        if rpr is None:
            continue
        if rpr.find(qn("w:vanish")) is not None or rpr.find(qn("w:specVanish")) is not None:
            trouves.append(("texte-masqué", f"« {extrait(texte)} »"))
            continue
        c = rpr.find(qn("w:color"))
        if c is not None and (c.get(qn("w:val")) or "").upper() in ("FFFFFF", "FEFEFE", "FDFDFD"):
            trouves.append(("blanc", f"« {extrait(texte)} »"))
            continue
        sz = rpr.find(qn("w:sz"))
        if sz is not None and sz.get(qn("w:val")) and int(sz.get(qn("w:val"))) / 2 < SEUIL_TAILLE:
            trouves.append(("minuscule", f"« {extrait(texte)} »"))

    tout = "\n".join(p.text for p in d.paragraphs)
    for tableau in d.tables:
        for cellule in tableau._cells:
            tout += "\n" + cellule.text
    signaler_invisibles(tout, "corps du document", trouves)

    with zipfile.ZipFile(str(chemin)) as z:
        if "word/comments.xml" in z.namelist():
            xml = z.read("word/comments.xml").decode("utf-8", "replace")
            textes = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
            if textes:
                trouves.append(("commentaire", f"« {extrait(' '.join(textes))} »"))
    return trouves


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    chemin = Path(sys.argv[1])
    ext = chemin.suffix.lower()
    try:
        if ext == ".pdf":
            trouves = analyser_pdf(chemin)
        elif ext == ".docx":
            trouves = analyser_docx(chemin)
        else:
            print(f"Format non pris en charge : {ext} (PDF ou DOCX uniquement)")
            return 2
    except ImportError as e:
        print(f"Dépendance manquante : {e.name}. Contrôle impossible, à signaler dans l'analyse.")
        return 2
    except Exception as e:  # fichier corrompu, protégé…
        print(f"Erreur de lecture : {e}")
        return 2
    for type_, detail in trouves:
        print(f"[{type_}] {detail}")
    print(f"{len(trouves)} passage(s) caché(s) trouvé(s)" if trouves else "Aucun texte caché trouvé")
    return 1 if trouves else 0


if __name__ == "__main__":
    sys.exit(main())
