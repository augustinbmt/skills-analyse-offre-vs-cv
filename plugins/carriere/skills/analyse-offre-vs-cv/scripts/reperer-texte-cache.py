#!/usr/bin/env python3
"""Repère le texte caché d'un CV PDF ou DOCX : ce qu'un humain ne voit pas mais qu'une IA lit.

Usage : python3 reperer-texte-cache.py <cv.pdf|cv.docx>

Sortie : une ligne par passage suspect, « [type] où : « extrait » », des lignes « [info] »
sur la méthode utilisée, puis un total.
Codes de sortie :
  0  contrôle complet, rien de caché ;
  1  au moins un passage caché trouvé (le contrôle peut être partiel, voir [info]) ;
  2  contrôle impossible ou partiel, et rien trouvé (voir [info] pour installer ce qui manque).

PDF, méthode principale (OCR) : chaque page est rendue en image (pdftoppm) et lue par OCR
(tesseract). Tout passage présent dans le texte extrait du fichier (pypdf et pdftotext)
mais absent de l'image est invisible pour un humain : texte blanc, minuscule, hors page,
en mode de rendu invisible, sous une image, de la couleur du fond… quelle que soit la technique.
Sans tesseract ni pdftoppm, une méthode de secours analyse les couleurs, tailles, positions et
modes de rendu (nécessite pypdf), et le signale.

DOCX : lu avec la bibliothèque standard de Python, sans dépendance. Corps, en-têtes,
pieds de page, notes, zones de texte, styles et couleurs de thème sont pris en compte ;
un texte blanc n'est signalé que s'il est sur un fond clair.

Dépendances PDF : poppler (pdftoppm, pdftotext, pdfinfo), tesseract (langues fra et eng),
pypdf recommandé. Le script ne modifie jamais le fichier et n'accède pas au réseau.
"""
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

INVISIBLES = re.compile("[\U000E0000-\U000E007F​-‏⁠-⁤﻿]")
SEUIL_TAILLE = 4.0       # points : en dessous, illisible à l'œil
SEUIL_CONTRASTE = 1.5    # rapport de contraste WCAG : en dessous, invisible ou presque
LONGUEUR_META = 60       # caractères : au-delà, un champ de métadonnées est signalé
MIN_MOTS_CACHES = 3      # mots significatifs absents de l'OCR pour signaler un passage

infos = []


def info(msg):
    infos.append(msg)


def extrait(texte, n=400):
    texte = " ".join(texte.split())
    return texte if len(texte) <= n else texte[:n] + "…"


def decode_tags(texte):
    """Rend lisibles les caractères Unicode « tags » (U+E0020–U+E007E)."""
    return "".join(chr(ord(c) - 0xE0000) for c in texte if 0xE0020 <= ord(c) <= 0xE007E)


def signaler_invisibles(texte, ou, trouves):
    if INVISIBLES.search(texte or ""):
        cache = decode_tags(texte)
        detail = f" — texte encodé : « {extrait(cache)} »" if cache.strip() else ""
        trouves.append(("unicode-invisible", f"{ou}{detail}"))


# ---------------------------------------------------------------- couleurs
def luminance(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(c1, c2):
    l1, l2 = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def hexa_valide(v):
    return bool(v) and re.fullmatch(r"[0-9A-Fa-f]{6}", v) is not None


# ================================================================ PDF
def outil(nom):
    return shutil.which(nom) is not None


def normaliser(mot):
    mot = unicodedata.normalize("NFKD", mot)
    mot = "".join(c for c in mot if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", mot)


def mots(texte):
    """Liste de (mot d'origine, mot normalisé), en écartant les caractères invisibles."""
    texte = INVISIBLES.sub("", texte or "")
    return [(m, normaliser(m)) for m in re.findall(r"\S+", texte) if normaliser(m)]


def langues_tesseract():
    try:
        sortie = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return "eng"
    dispo = set(sortie.split())
    choisies = [l for l in ("fra", "eng") if l in dispo]
    if "fra" not in dispo:
        info("tesseract n'a pas la langue française (fra) : l'OCR des accents sera moins précis")
    return "+".join(choisies) or "eng"


def nombre_pages(chemin):
    try:
        sortie = subprocess.run(["pdfinfo", str(chemin)], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"^Pages:\s+(\d+)", sortie, re.M)
        return int(m.group(1)) if m else 1
    except Exception:
        return 1


def textes_extraits(chemin, n_pages):
    """Texte de chaque page selon chaque extracteur disponible : {extracteur: [texte_page1, ...]}."""
    sources = {}
    try:
        from pypdf import PdfReader
        lecteur = PdfReader(str(chemin))
        sources["pypdf"] = [p.extract_text() or "" for p in lecteur.pages]
    except ImportError:
        info("pypdf absent : seul pdftotext extrait le texte (pip install pypdf pour un contrôle plus complet)")
    except Exception as e:
        info(f"pypdf n'a pas pu lire le fichier : {e}")
    if outil("pdftotext"):
        pages = []
        for i in range(1, n_pages + 1):
            r = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-raw", str(chemin), "-"],
                               capture_output=True, text=True, timeout=60)
            pages.append(r.stdout)
        sources["pdftotext"] = pages
    return sources


def ocr_pages(chemin, n_pages, langues, dossier):
    pages = []
    subprocess.run(["pdftoppm", "-r", "300", "-png", str(chemin), str(Path(dossier) / "p")],
                   check=True, capture_output=True, timeout=300)
    images = sorted(Path(dossier).glob("p-*.png"), key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
    for img in images[:n_pages]:
        r = subprocess.run(["tesseract", str(img), "-", "-l", langues, "--psm", "3"],
                           capture_output=True, text=True, timeout=300)
        pages.append(r.stdout)
    return pages


def present_dans_ocr(norm, vocab_ocr):
    """Le mot apparaît-il dans l'OCR ? Tolère une petite erreur de lecture sur les mots longs."""
    if norm in vocab_ocr:
        return True
    if len(norm) < 6:
        return False
    proches = [v for v in vocab_ocr if abs(len(v) - len(norm)) <= 1 and v[0] == norm[0]]
    return bool(difflib.get_close_matches(norm, proches, n=1, cutoff=0.85))


def passages_absents(texte, vocab_ocr):
    """Lignes (ou morceaux de ligne) du texte extrait dont les mots significatifs sont absents de l'OCR."""
    passages = []
    for ligne in (texte or "").splitlines():
        extraits = mots(ligne)
        # mots significatifs : 4 lettres ou plus, ou contenant un chiffre
        sig = [len(n) >= 4 or any(c.isdigit() for c in n) for _, n in extraits]
        absent = [s_ and not present_dans_ocr(n, vocab_ocr) for (_, n), s_ in zip(extraits, sig)]
        n_sig, n_abs = sum(sig), sum(absent)
        if n_abs < MIN_MOTS_CACHES:
            continue
        if n_abs / n_sig >= 0.6:
            # la ligne entière est invisible
            passages.append(INVISIBLES.sub("", ligne).strip())
            continue
        # sinon, chercher un morceau invisible collé à du texte visible sur la même ligne
        i = 0
        while i < len(extraits):
            if not absent[i]:
                i += 1
                continue
            debut = fin = i
            total = absents = 0
            j = i
            while j < len(extraits):
                if sig[j]:
                    total += 1
                    if absent[j]:
                        absents += 1
                        fin = j
                    elif absents / total < 0.6:
                        break
                j += 1
            if absents >= MIN_MOTS_CACHES:
                passages.append(" ".join(m for m, _ in extraits[debut:fin + 1]))
            i = fin + 1
    return passages


def metadonnees_pdf(chemin, trouves):
    if not outil("pdfinfo"):
        info("pdfinfo absent : métadonnées non contrôlées (installer poppler)")
        return
    sortie = subprocess.run(["pdfinfo", str(chemin)], capture_output=True, text=True, timeout=30).stdout
    for ligne in sortie.splitlines():
        cle, _, val = ligne.partition(":")
        val = val.strip()
        if cle in ("Title", "Subject", "Keywords", "Author", "Creator", "Producer"):
            if len(val) > LONGUEUR_META:
                trouves.append(("métadonnées", f"{cle} : « {extrait(val)} »"))
            signaler_invisibles(val, f"métadonnées {cle}", trouves)


def analyser_pdf_ocr(chemin, trouves):
    n = nombre_pages(chemin)
    sources = textes_extraits(chemin, n)
    if not sources:
        info("aucun extracteur de texte disponible (installer poppler ou pypdf)")
        return False
    langues = langues_tesseract()
    with tempfile.TemporaryDirectory() as dossier:
        ocr = ocr_pages(chemin, n, langues, dossier)
    info(f"méthode OCR : texte extrait ({', '.join(sources)}) comparé à la page rendue lue par tesseract ({langues})")
    texte_total = 0
    for num in range(1, n + 1):
        vocab = {norm for _, norm in mots(ocr[num - 1] if num - 1 < len(ocr) else "")}
        vus = []
        for nom, pages in sources.items():
            texte = pages[num - 1] if num - 1 < len(pages) else ""
            texte_total += len(texte.strip())
            signaler_invisibles(texte, f"page {num} ({nom})", trouves)
            for passage in passages_absents(texte, vocab):
                cle = {normaliser(m) for m in passage.split()}
                if any(len(cle & v) >= 0.7 * len(cle) for v in vus):
                    continue  # déjà signalé par l'autre extracteur
                vus.append(cle)
                trouves.append(("invisible", f"page {num} : « {extrait(passage)} »"))
    if texte_total == 0:
        info("aucune couche de texte : CV en image, aucun texte caché possible dans le fichier, "
             "mais les phrases visibles sur l'image restent à lire avec attention")
    return True


def analyser_pdf_secours(chemin, trouves):
    """Sans OCR : couleurs, tailles, positions et mode de rendu, page par page (nécessite pypdf)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        info("ni OCR ni pypdf : contrôle du contenu impossible, seules les métadonnées sont vérifiées")
        return False
    info("méthode de secours (OCR indisponible) : texte blanc, minuscule, hors page et en mode invisible ; "
         "un texte gris très clair ou caché sous une image peut passer inaperçu. "
         "Installer poppler et tesseract pour le contrôle complet.")
    lecteur = PdfReader(str(chemin))
    for num, page in enumerate(lecteur.pages, 1):
        x0, y0, x1, y1 = [float(v) for v in page.mediabox]
        etat = {"couleur": "000000", "mode": 0, "chemin": []}
        aplats = []  # rectangles remplis : (x0, y0, x1, y1, couleur), dans l'ordre du dessin
        morceaux = {"blanc": [], "minuscule": [], "hors-page": [], "mode-invisible": []}

        def fond_sous(x, y):
            """Couleur du dernier aplat dessiné sous ce point (blanc par défaut)."""
            for ax0, ay0, ax1, ay1, coul in reversed(aplats):
                if ax0 <= x <= ax1 and ay0 <= y <= ay1:
                    return coul
            return "FFFFFF"

        def visiteur_op(op, args, cm, tm):
            try:
                if op == b"rg" and len(args) == 3:
                    etat["couleur"] = "".join(f"{int(float(a) * 255):02X}" for a in args)
                elif op == b"g" and len(args) == 1:
                    etat["couleur"] = f"{int(float(args[0]) * 255):02X}" * 3
                elif op == b"k" and len(args) == 4:
                    c, m, j, n = (float(a) for a in args)
                    etat["couleur"] = "".join(f"{int(255 * (1 - v) * (1 - n)):02X}" for v in (c, m, j))
                elif op == b"Tr" and args:
                    etat["mode"] = int(args[0])
                elif op == b"Q":
                    etat["mode"] = 0
                elif op == b"re" and len(args) == 4:
                    x, y, w, h = (float(a) for a in args)
                    xa, ya = cm[0] * x + cm[4], cm[3] * y + cm[5]
                    xb, yb = cm[0] * (x + w) + cm[4], cm[3] * (y + h) + cm[5]
                    etat["chemin"].append((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)))
                elif op in (b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*"):
                    for r in etat["chemin"]:
                        aplats.append((*r, etat["couleur"]))
                    etat["chemin"] = []
                elif op in (b"n", b"S", b"s"):
                    etat["chemin"] = []
            except (ValueError, TypeError):
                pass

        def visiteur_texte(texte, cm, tm, police, taille):
            if not texte.strip():
                return
            taille_reelle = abs(taille * (tm[0] or 1) * (cm[0] or 1))
            x = tm[4] * cm[0] + cm[4]
            y = tm[5] * cm[3] + cm[5]
            if etat["mode"] in (3, 7):
                morceaux["mode-invisible"].append(texte)
            elif contraste(etat["couleur"], fond_sous(x, y)) < SEUIL_CONTRASTE:
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
    info("en méthode de secours, le fond n'est connu que s'il est dessiné en aplat de couleur : "
         "un texte clair sur une image de fond peut être signalé à tort, à vérifier visuellement")
    return True


def analyser_pdf(chemin):
    trouves = []
    metadonnees_pdf(chemin, trouves)
    complet = False
    if outil("pdftoppm") and outil("tesseract"):
        try:
            complet = analyser_pdf_ocr(chemin, trouves)
        except subprocess.TimeoutExpired:
            info("OCR trop long, abandonné : passage à la méthode de secours")
        except subprocess.CalledProcessError as e:
            info(f"rendu de la page impossible ({e}) : passage à la méthode de secours")
    else:
        manquants = [o for o in ("pdftoppm", "tesseract") if not outil(o)]
        info(f"OCR indisponible ({', '.join(manquants)} manquant)")
    if not complet:
        analyser_pdf_secours(chemin, trouves)
    return trouves, complet


# ================================================================ DOCX (bibliothèque standard)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WPS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "a": A, "wps": WPS, "wp": WP,
      "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
      "dc": "http://purl.org/dc/elements/1.1/"}


def q(tag):
    pre, nom = tag.split(":")
    return f"{{{NS[pre]}}}{nom}"


SURLIGNAGES = {"yellow": "FFFF00", "green": "00FF00", "cyan": "00FFFF", "magenta": "FF00FF", "blue": "0000FF",
               "red": "FF0000", "darkBlue": "000080", "darkCyan": "008080", "darkGreen": "008000",
               "darkMagenta": "800080", "darkRed": "800000", "darkYellow": "808000", "darkGray": "808080",
               "lightGray": "C0C0C0", "black": "000000", "white": "FFFFFF"}
THEME_ALIAS = {"text1": "dk1", "background1": "lt1", "text2": "dk2", "background2": "lt2",
               "dark1": "dk1", "light1": "lt1", "dark2": "dk2", "light2": "lt2", "hyperlink": "hlink",
               "followedHyperlink": "folHlink"}


class Docx:
    def __init__(self, chemin):
        self.z = zipfile.ZipFile(str(chemin))
        self.noms = set(self.z.namelist())
        self.theme = self._theme()
        self.styles, self.defaut = self._styles()

    def xml(self, nom):
        return ET.fromstring(self.z.read(nom)) if nom in self.noms else None

    def _theme(self):
        couleurs = {}
        racine = self.xml("word/theme/theme1.xml")
        if racine is None:
            return couleurs
        schema = racine.find(".//a:clrScheme", NS)
        for el in list(schema) if schema is not None else []:
            nom = el.tag.split("}")[1]
            srgb, sysc = el.find("a:srgbClr", NS), el.find("a:sysClr", NS)
            if srgb is not None:
                couleurs[nom] = srgb.get("val")
            elif sysc is not None:
                couleurs[nom] = sysc.get("lastClr")
        return couleurs

    def couleur_theme(self, nom):
        return self.theme.get(THEME_ALIAS.get(nom, nom))

    def _props(self, rpr):
        """Propriétés utiles d'un w:rPr : masqué, couleur, taille (points), fond."""
        p = {}
        if rpr is None:
            return p
        for tag in ("w:vanish", "w:specVanish", "w:webHidden"):
            el = rpr.find(tag, NS)
            if el is not None:
                p["masque"] = el.get(q("w:val"), "true") not in ("0", "false")
        col = rpr.find("w:color", NS)
        if col is not None:
            theme = col.get(q("w:themeColor"))
            val = self.couleur_theme(theme) if theme else col.get(q("w:val"))
            if hexa_valide(val):
                p["couleur"] = val.upper()
            elif val == "auto":
                p["couleur"] = "auto"
        sz = rpr.find("w:sz", NS)
        if sz is not None and (sz.get(q("w:val")) or "").isdigit():
            p["taille"] = int(sz.get(q("w:val"))) / 2
        fond = self._fond(rpr)
        if fond:
            p["fond"] = fond
        return p

    def _fond(self, ppr_ou_rpr):
        if ppr_ou_rpr is None:
            return None
        hl = ppr_ou_rpr.find("w:highlight", NS)
        if hl is not None and hl.get(q("w:val")) in SURLIGNAGES:
            return SURLIGNAGES[hl.get(q("w:val"))]
        shd = ppr_ou_rpr.find("w:shd", NS)
        if shd is not None:
            theme = shd.get(q("w:themeFill"))
            val = self.couleur_theme(theme) if theme else shd.get(q("w:fill"))
            if hexa_valide(val):
                return val.upper()
        return None

    def _styles(self):
        styles, defaut = {}, {}
        racine = self.xml("word/styles.xml")
        if racine is None:
            return styles, defaut
        rd = racine.find("w:docDefaults/w:rPrDefault/w:rPr", NS)
        defaut = self._props(rd)
        for st in racine.findall("w:style", NS):
            sid = st.get(q("w:styleId"))
            base = st.find("w:basedOn", NS)
            styles[sid] = {
                "base": base.get(q("w:val")) if base is not None else None,
                "r": self._props(st.find("w:rPr", NS)),
                "fond_p": self._fond(st.find("w:pPr", NS)),
            }
        return styles, defaut

    def chaine(self, sid, cle="r"):
        """Propriétés d'un style, héritage compris (du plus général au plus précis)."""
        pile, vus = [], set()
        while sid and sid in self.styles and sid not in vus:
            vus.add(sid)
            pile.append(self.styles[sid])
            sid = self.styles[sid]["base"]
        res = {}
        for st in reversed(pile):
            if cle == "r":
                res.update(st["r"])
            elif st["fond_p"]:
                res["fond"] = st["fond_p"]
        return res


def analyser_docx(chemin):
    trouves = []
    try:
        d = Docx(chemin)
    except zipfile.BadZipFile:
        raise ValueError("ce n'est pas un DOCX valide (archive illisible)")

    # Métadonnées (core.xml et propriétés personnalisées)
    core = d.xml("docProps/core.xml")
    if core is not None:
        for el in core:
            nom, val = el.tag.split("}")[1], (el.text or "")
            if nom in ("subject", "keywords", "description", "title", "category") and len(val) > LONGUEUR_META:
                trouves.append(("métadonnées", f"{nom} : « {extrait(val)} »"))
            signaler_invisibles(val, f"métadonnées {nom}", trouves)
    custom = d.xml("docProps/custom.xml")
    if custom is not None:
        for prop in custom:
            val = "".join(prop.itertext())
            if len(val) > LONGUEUR_META:
                trouves.append(("métadonnées", f"propriété {prop.get('name')} : « {extrait(val)} »"))

    fond_page = "FFFFFF"
    doc = d.xml("word/document.xml")
    if doc is not None:
        bg = doc.find("w:background", NS)
        if bg is not None and hexa_valide(bg.get(q("w:color"))):
            fond_page = bg.get(q("w:color")).upper()

    parties = ["word/document.xml"] + sorted(n for n in d.noms if re.match(r"word/(header|footer)\d*\.xml$", n)) \
        + [n for n in ("word/footnotes.xml", "word/endnotes.xml") if n in d.noms]
    tout_le_texte = []

    for partie in parties:
        racine = d.xml(partie)
        if racine is None:
            continue
        lieu = {"word/document.xml": "corps", "word/footnotes.xml": "notes de bas de page",
                "word/endnotes.xml": "notes de fin"}.get(partie)
        if lieu is None:
            lieu = ("en-tête" if "header" in partie else "pied de page") + f" ({Path(partie).stem})"
        parent = {enfant: p for p in racine.iter() for enfant in p}

        def ancetre(el, tag):
            while el is not None:
                el = parent.get(el)
                if el is not None and el.tag == q(tag):
                    return el
            return None

        # Texte alternatif des images
        for doc_pr in racine.iter(q("wp:docPr")):
            for attr in ("descr", "title"):
                val = doc_pr.get(attr) or ""
                if len(val) > LONGUEUR_META:
                    trouves.append(("texte-alternatif", f"{lieu}, image « {doc_pr.get('name', '?')} » : « {extrait(val)} »"))

        # Texte supprimé en suivi des modifications (invisible dans la vue finale)
        for dl in racine.iter(q("w:del")):
            texte = "".join(t.text or "" for t in dl.iter(q("w:delText")))
            if texte.strip():
                trouves.append(("texte-supprimé", f"{lieu} (suivi des modifications) : « {extrait(texte)} »"))

        for para in racine.iter(q("w:p")):
            ppr = para.find("w:pPr", NS)
            pstyle = ppr.find("w:pStyle", NS) if ppr is not None else None
            pstyle_id = pstyle.get(q("w:val")) if pstyle is not None else ("Normal" if "Normal" in d.styles else None)
            props_p = dict(d.defaut)
            props_p.update(d.chaine(pstyle_id))
            fond_p = d._fond(ppr) or d.chaine(pstyle_id, "fond").get("fond")
            courant = None  # (type, [textes]) : regroupe les runs consécutifs de même type

            for run in para.findall(".//w:r", NS):
                if ancetre(run, "w:del") is not None:
                    continue
                texte = "".join(t.text or "" for t in run.findall("w:t", NS))
                if not texte:
                    continue
                tout_le_texte.append(texte)
                rpr = run.find("w:rPr", NS)
                rstyle = rpr.find("w:rStyle", NS) if rpr is not None else None
                props = dict(props_p)
                if rstyle is not None:
                    props.update(d.chaine(rstyle.get(q("w:val"))))
                props.update(d._props(rpr))

                fond = props.get("fond") or fond_p
                if not fond:
                    tc = ancetre(run, "w:tc")
                    if tc is not None:
                        fond = d._fond(tc.find("w:tcPr", NS))
                if not fond:
                    forme = ancetre(run, "wps:wsp")
                    if forme is not None:
                        srgb = forme.find("wps:spPr/a:solidFill/a:srgbClr", NS)
                        sch = forme.find("wps:spPr/a:solidFill/a:schemeClr", NS)
                        if srgb is not None:
                            fond = srgb.get("val")
                        elif sch is not None:
                            fond = d.couleur_theme(sch.get("val"))
                fond = (fond or fond_page).upper()

                type_ = None
                if props.get("masque"):
                    type_ = "texte-masqué"
                elif props.get("couleur") not in (None, "auto") and contraste(props["couleur"], fond) < SEUIL_CONTRASTE:
                    type_ = "blanc" if luminance(props["couleur"]) > 0.8 else "même-couleur-que-le-fond"
                elif props.get("taille") and props["taille"] < SEUIL_TAILLE:
                    type_ = "minuscule"

                if type_ and courant and courant[0] == type_:
                    courant[1].append(texte)
                else:
                    if courant:
                        trouves.append((courant[0], f"{lieu} : « {extrait(''.join(courant[1]))} »"))
                    courant = (type_, [texte]) if type_ else None
            if courant:
                trouves.append((courant[0], f"{lieu} : « {extrait(''.join(courant[1]))} »"))

    signaler_invisibles("".join(tout_le_texte), "texte du document", trouves)

    com = d.xml("word/comments.xml")
    if com is not None:
        for c in com.findall("w:comment", NS):
            texte = "".join(t.text or "" for t in c.iter(q("w:t")))
            if texte.strip():
                trouves.append(("commentaire", f"auteur « {c.get(q('w:author'), '?')} » : « {extrait(texte)} »"))
    return trouves, True


# ================================================================ principal
def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    chemin = Path(sys.argv[1])
    if not chemin.is_file():
        print(f"Fichier introuvable : {chemin}")
        return 2
    ext = chemin.suffix.lower()
    try:
        if ext == ".pdf":
            trouves, complet = analyser_pdf(chemin)
        elif ext == ".docx":
            trouves, complet = analyser_docx(chemin)
        else:
            print(f"Format non pris en charge : {ext} (PDF ou DOCX uniquement)")
            return 2
    except Exception as e:  # fichier corrompu, protégé par mot de passe…
        print(f"Erreur de lecture : {e}")
        return 2
    for type_, detail in trouves:
        print(f"[{type_}] {detail}")
    for msg in infos:
        print(f"[info] {msg}")
    if trouves:
        print(f"{len(trouves)} passage(s) caché(s) trouvé(s)" + ("" if complet else " — contrôle partiel"))
        return 1
    if not complet:
        print("Aucun texte caché trouvé, mais le contrôle est partiel (voir [info])")
        return 2
    print("Aucun texte caché trouvé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
