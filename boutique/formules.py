"""
Évaluateur SÛR des formules saisies dans l'admin (Ltp, R…).

La formule n'est JAMAIS exécutée comme du code Python (pas d'eval) : le
module « ast » la découpe en arbre, et seuls les éléments ci-dessous sont
acceptés. Tout le reste (import, attributs, chaînes, listes…) est refusé.

    evaluer("ceil(4*Lc + 1.3*d)", {"Lc": 20, "d": 8})  ->  91
"""
import ast
import math
import operator

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

FONCTIONS = {
    "ceil": math.ceil,
    "floor": math.floor,
    "round": round,
    "min": min,
    "max": max,
    "sqrt": math.sqrt,
    "sin": lambda degres: math.sin(math.radians(degres)),   # angles en degrés
    "cos": lambda degres: math.cos(math.radians(degres)),
    "tan": lambda degres: math.tan(math.radians(degres)),
}

LONGUEUR_MAX = 255


class FormuleInvalide(ValueError):
    """Formule mal écrite, interdite ou impossible à calculer."""


def _arbre(formule):
    formule = (formule or "").strip()
    if not formule:
        raise FormuleInvalide("La formule est vide.")
    if len(formule) > LONGUEUR_MAX:
        raise FormuleInvalide(f"La formule dépasse {LONGUEUR_MAX} caractères.")
    try:
        return ast.parse(formule, mode="eval").body
    except SyntaxError:
        raise FormuleInvalide("Formule mal écrite (parenthèse ou opérateur manquant ?).")


def noms_utilises(formule):
    """Abréviations (variables) utilisées dans la formule."""
    noms = set()
    for noeud in ast.walk(_arbre(formule)):
        if isinstance(noeud, ast.Name) and noeud.id not in FONCTIONS:
            noms.add(noeud.id)
    return noms


def evaluer(formule, variables):
    """Calcule la formule avec les valeurs données ; lève FormuleInvalide sinon."""

    def calc(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) \
                and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in variables:
                raise FormuleInvalide(f"Abréviation inconnue : {n.id}")
            return float(variables[n.id])
        if isinstance(n, ast.BinOp) and type(n.op) in OPERATIONS:
            gauche, droite = calc(n.left), calc(n.right)
            if isinstance(n.op, ast.Pow) and abs(droite) > 10:
                raise FormuleInvalide("Puissance trop grande (10 au maximum).")
            return OPERATIONS[type(n.op)](gauche, droite)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            valeur = calc(n.operand)
            return -valeur if isinstance(n.op, ast.USub) else valeur
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FONCTIONS \
                and not n.keywords:
            return FONCTIONS[n.func.id](*[calc(a) for a in n.args])
        raise FormuleInvalide("Élément interdit dans la formule.")

    try:
        resultat = calc(_arbre(formule))
    except FormuleInvalide:
        raise
    except ZeroDivisionError:
        raise FormuleInvalide("Division par zéro.")
    except (TypeError, ValueError, OverflowError) as exc:
        raise FormuleInvalide(f"Calcul impossible : {exc}")
    if isinstance(resultat, float) and not math.isfinite(resultat):
        raise FormuleInvalide("Résultat non valable.")
    return resultat


def verifier(formule, autorisees, jeux_de_valeurs):
    """Contrôle à l'enregistrement : seulement des abréviations autorisées, et
    un résultat positif pour chaque jeu de valeurs (min, max…).
    Renvoie la liste des résultats (pour l'aperçu)."""
    inconnues = noms_utilises(formule) - set(autorisees)
    if inconnues:
        raise FormuleInvalide("Abréviation inconnue : " + ", ".join(sorted(inconnues)))
    resultats = []
    for valeurs in jeux_de_valeurs:
        resultat = evaluer(formule, valeurs)
        if resultat < 0:
            raise FormuleInvalide(f"Résultat négatif ({resultat:g}) avec {_texte(valeurs)}.")
        resultats.append(resultat)
    return resultats


def _texte(valeurs):
    return ", ".join(f"{k} = {v:g}" for k, v in valeurs.items())
