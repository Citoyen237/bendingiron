"""
Dessin de la forme à l'échelle.

La forme d'un produit (ConfigProduit.forme) est une liste de segments,
parcourue comme une « tortue » qui avance puis tourne :

    [{"longueur": 0, "angle": 45, "cote": false},            # oriente le départ
     {"longueur": "Ldf/2", "angle": -135, "crochet": true},   # crochet de départ (Ldf)
     {"longueur": "Lc", "angle": -90}, …,
     {"longueur": "Ldf/2", "crochet": true}]                  # crochet de fin

- "longueur" : nombre ou formule (abréviations, d, angle, ka, R, Ltp, Ldf, Lt) ;
- "angle"    : virage APRÈS le segment, en degrés ou formule ; positif = à gauche ;
- "crochet"  : true pour un crochet (Ldf) : il suit l'arrondi du coin (rayon R en
               entier) puis continue en ligne droite sur sa longueur ; sa valeur est
               écrite sur le dessin ;
- "cote"     : false pour ne pas écrire la valeur d'un segment.
  (Ancienne écriture : « cote »: false sans « crochet » = crochet sans valeur.)

Les coins sont arrondis avec le rayon de courbure R (à l'échelle).
Le serveur calcule le tracé ; la page et la miniature (facture) le reprennent.
"""
import math

from .formules import FormuleInvalide, evaluer

SEGMENTS_MAX = 40
CLES_SEGMENT = {"longueur", "angle", "cote", "crochet"}


def _est_crochet(segment):
    """« crochet »: true ; ancienne écriture acceptée : « cote »: false sans « crochet »."""
    if "crochet" in segment:
        return bool(segment["crochet"])
    return segment.get("cote") is False


def _affiche_cote(segment):
    """Valeur écrite sur le dessin, sauf « cote »: false."""
    return segment.get("cote", True) is not False
COULEUR = "#f2a900"        # orange de l'image de référence
TAILLE_MINIATURE = 70      # pixels (facture)


def _valeur(expression, variables, quoi):
    if isinstance(expression, bool):
        raise FormuleInvalide(f"{quoi} : valeur invalide.")
    if isinstance(expression, (int, float)):
        return float(expression)
    if isinstance(expression, str):
        return float(evaluer(expression, variables))
    raise FormuleInvalide(f"{quoi} : valeur invalide.")


def verifier_structure(forme):
    """Contrôle la forme (liste de segments) sans la calculer."""
    if forme in (None, "", []):
        return
    if not isinstance(forme, list):
        raise FormuleInvalide("La forme doit être une liste de segments : [{\"longueur\": \"Lc\", \"angle\": 90}, …]")
    if len(forme) > SEGMENTS_MAX:
        raise FormuleInvalide(f"La forme dépasse {SEGMENTS_MAX} segments.")
    for i, segment in enumerate(forme, start=1):
        if not isinstance(segment, dict) or "longueur" not in segment:
            raise FormuleInvalide(f"Segment {i} : il faut au moins « longueur ».")
        inconnues = set(segment) - CLES_SEGMENT
        if inconnues:
            raise FormuleInvalide(f"Segment {i} : clé inconnue « {', '.join(sorted(inconnues))} ».")
        for cle in ("cote", "crochet"):
            if cle in segment and not isinstance(segment[cle], bool):
                raise FormuleInvalide(f"Segment {i} : « {cle} » vaut true ou false.")


def _n(valeur):
    return f"{round(valeur, 3):g}"


def _virage(cap1, cap2):
    """Angle (degrés, entre -180 et 180) pour passer du cap1 au cap2."""
    return (cap2 - cap1 + 180) % 360 - 180


def _pliages(segments, rayon):
    """Pour chaque pliage i (entre les segments i-1 et i) : virage (degrés, signé),
    rayon réellement utilisé, et longueur prise par l'arc sur chacun des deux segments.

    - entre deux côtés : arrondi classique (rayon R, réduit si un côté est trop court) ;
    - avec un crochet (« cote »: false) : le crochet suit d'abord l'arrondi du coin
      (comme un pliage à 90°), puis continue de plier jusqu'à son angle (ex. 135°) ;
      le côté perd la même longueur qu'à un coin à 90°, et le crochet ne perd RIEN :
      sa longueur droite (Ldf) vient APRÈS l'arc."""
    pliages = [None] * len(segments)
    for i in range(1, len(segments)):
        avant, apres = segments[i - 1], segments[i]
        virage = _virage(avant["cap"], apres["cap"])
        a = abs(virage)
        if rayon <= 0 or a < 0.1 or a > 179:
            pliages[i] = {"virage": virage, "r": 0.0, "pris_avant": 0.0, "pris_apres": 0.0}
            continue
        if avant["cote"] and apres["cote"]:
            t = math.tan(math.radians(a) / 2)
            pris = min(rayon * t, avant["longueur"] / 2, apres["longueur"] / 2)
            pliages[i] = {"virage": virage, "r": pris / t, "pris_avant": pris, "pris_apres": pris}
        else:
            t = math.tan(math.radians(min(a, 90)) / 2)
            cote = avant if avant["cote"] else (apres if apres["cote"] else None)
            pris = rayon * t if cote is None else min(rayon * t, cote["longueur"] / 2)
            r = pris / t
            pliages[i] = {"virage": virage, "r": r,
                          "pris_avant": pris if avant["cote"] else 0.0,
                          "pris_apres": pris if apres["cote"] else 0.0}
    return pliages


def calculer_dessin(forme, variables):
    """Renvoie {"points", "cotes", "chemin", "cadre"} ; coordonnées en cm.

    - « points » : sommets de la forme sans arrondi (y vers le haut) ;
    - « chemin » : tracé SVG réel, coins arrondis au rayon R (y vers le bas) ;
    - « cadre »  : xmin, ymin, largeur, hauteur du tracé réel (y vers le bas).
    Lève FormuleInvalide."""
    verifier_structure(forme)

    # 1) Segments réels (longueur > 0) avec leur cap ; un segment de longueur 0
    #    sert seulement à orienter le départ (pas de pliage sans matière avant).
    segments, cap = [], 0.0
    for i, segment in enumerate(forme or [], start=1):
        longueur = _valeur(segment["longueur"], variables, f"Segment {i}, longueur")
        if longueur < 0:
            raise FormuleInvalide(f"Segment {i} : longueur négative ({longueur:g}).")
        if longueur > 0:
            segments.append({"longueur": longueur, "cap": cap,
                             "cote": not _est_crochet(segment),          # côté « normal » (géométrie)
                             "crochet": _est_crochet(segment),
                             "afficher": _affiche_cote(segment)})       # valeur écrite sur le dessin
        cap += _valeur(segment.get("angle", 0), variables, f"Segment {i}, angle")
    if not segments:
        return {"points": [[0.0, 0.0]], "cotes": [], "chemin": "", "cadre": [0, 0, 0, 0]}

    # 2) Sommets sans arrondi (cotes, tests)
    x = y = 0.0
    points = [[0.0, 0.0]]
    for s in segments:
        rad = math.radians(s["cap"])
        x, y = x + s["longueur"] * math.cos(rad), y + s["longueur"] * math.sin(rad)
        points.append([round(x, 3), round(y, 3)])

    # 3) Tracé réel : parties droites puis arcs de rayon R (y vers le haut)
    pliages = _pliages(segments, float(variables.get("R", 0) or 0))
    pos = (0.0, 0.0)
    cap = segments[0]["cap"]
    echantillons = [pos]
    morceaux = ["M0 0"]
    cotes = []

    def ecran(p):
        return f"{_n(p[0])} {_n(-p[1])}"

    for i, s in enumerate(segments):
        pris_debut = pliages[i]["pris_apres"] if i > 0 else 0.0
        pris_fin = pliages[i + 1]["pris_avant"] if i + 1 < len(segments) else 0.0
        droit = max(s["longueur"] - pris_debut - pris_fin, 0.0)
        rad = math.radians(cap)
        fin = (pos[0] + droit * math.cos(rad), pos[1] + droit * math.sin(rad))
        if s["afficher"]:
            cotes.append({
                "x": round((pos[0] + fin[0]) / 2, 2), "y": round((pos[1] + fin[1]) / 2, 2),
                # perpendiculaire au segment, pour écarter le texte du trait
                "dx": round(-math.sin(rad), 4), "dy": round(math.cos(rad), 4),
                "texte": f"{round(s['longueur'], 1):g}",
                "type": "ldf" if s["crochet"] else "cote",
            })
        pos = fin
        morceaux.append(f"L{ecran(pos)}")
        echantillons.append(pos)

        if i + 1 < len(segments):
            p = pliages[i + 1]
            if p["r"] > 0:
                gauche = 1 if p["virage"] > 0 else -1
                normale = math.radians(cap + 90 * gauche)
                centre = (pos[0] + p["r"] * math.cos(normale), pos[1] + p["r"] * math.sin(normale))
                depart = math.atan2(pos[1] - centre[1], pos[0] - centre[0])
                for k in range(1, 9):                     # points de l'arc (pour le cadre)
                    a = depart + math.radians(p["virage"]) * k / 8
                    echantillons.append((centre[0] + p["r"] * math.cos(a), centre[1] + p["r"] * math.sin(a)))
                pos = echantillons[-1]
                # SVG : sens 1 = sens horaire à l'écran ; un virage à droite (négatif) est horaire
                sens = 1 if p["virage"] < 0 else 0
                morceaux.append(f"A{_n(p['r'])} {_n(p['r'])} 0 0 {sens} {ecran(pos)}")
            cap = segments[i + 1]["cap"]

    xs = [e[0] for e in echantillons]
    ys = [-e[1] for e in echantillons]
    return {
        "points": points,
        "cotes": cotes,
        "chemin": " ".join(morceaux),
        "cadre": [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)],
    }


def svg_miniature(dessin, taille=TAILLE_MINIATURE, couleur=COULEUR):
    """Image SVG carrée (taille × taille pixels), sans texte, comme l'image de
    référence : à importer sur la facture."""
    if not dessin or not dessin.get("chemin"):
        return ""
    x, y, largeur, hauteur = dessin["cadre"]
    cote = max(largeur, hauteur, 1.0)
    marge = cote * 0.12
    # carré centré sur la forme
    x0 = x - (cote - largeur) / 2 - marge
    y0 = y - (cote - hauteur) / 2 - marge
    vue = cote + 2 * marge
    epaisseur = vue * 0.075
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{taille}" height="{taille}" '
        f'viewBox="{_n(x0)} {_n(y0)} {_n(vue)} {_n(vue)}">'
        f'<path d="{dessin["chemin"]}" fill="none" stroke="{couleur}" stroke-width="{_n(epaisseur)}" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
