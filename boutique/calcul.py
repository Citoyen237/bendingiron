"""
Moteur de calcul UNIQUE du gabarit universel (étape 2).

Il suit exactement LOGIQUE_CALCUL_PRIX.txt (section 4) :

    Ltp   = formule du produit
    Ldf   = Ltp × constante (selon le seuil)            = Ld
    Lt    = arrondi supérieur (Ltp + Ldf)
    R     = formule selon d
    Poids = Lt × poids au cm(d)
    Pv    = Poids × Pvk                (Bending Iron fournit le fer)
          = Poids × (Pvk − Pak)        (le client fournit le fer)
    Ps    = coef(marque, d) × Lt / 100
    Pd    = constante de soudure(d) × Lt
    Pu    = arrondi supérieur [ (Pv + Ps + tolérance + taxe + Pd) × (1 + taux) ]
            tolérance = celle du diamètre (admin « Tolérances par diamètre »),
                        sinon la constante commune « tolerance »

Le serveur fait foi : les prix envoyés par le navigateur ne sont jamais lus.
Rien ici n'est encore branché sur les pages produit (étape 4).
"""
import math
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from .formules import FormuleInvalide, evaluer
from .models import (SOUS_CATEGORIES_AUTORISEES, CoefFaconnage, ConstanteSoudure, ParametresCalcul,
                     PoidsFer, PrixFerTonne, PrtFer, ToleranceDiametre)

FER_BENDING_IRON = "bending iron"
FER_CLIENT = "le client"
CONSTANTES_PRIX = ("tolerance", "taxe", "taux")


class CalculImpossible(ValueError):
    """Saisie invalide ou donnée manquante dans l'admin : le message est affichable au client.
    « champ » : nom du champ concerné (fer, marque_fer, type_fer, diametre, angle,
    dim_<abréviation>, quantite), ou None pour une donnée manquante dans l'admin."""

    def __init__(self, message, champ=None):
        super().__init__(message)
        self.champ = champ


@dataclass
class ResultatCalcul:
    ltp: Decimal
    ldf: Decimal
    lt: int
    r: Decimal
    poids: Decimal
    pak: Decimal
    pvk: Decimal
    pv: Decimal
    ps: Decimal
    pd: Decimal
    pu: int
    quantite: int = 1
    details: dict = field(default_factory=dict)
    variables: dict = field(default_factory=dict)   # valeurs des formules (pour le dessin)

    @property
    def total(self):
        return self.pu * self.quantite

    @property
    def poids_total(self):
        """Poids de toutes les pièces commandées (kg) = poids d'une pièce × quantité."""
        return self.poids * self.quantite


def _decimal(valeur, nom):
    try:
        resultat = Decimal(str(valeur).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        raise CalculImpossible(f"{nom} : valeur invalide.")
    if not resultat.is_finite():
        raise CalculImpossible(f"{nom} : valeur invalide.")
    return resultat


def _depuis_formule(valeur):
    """Résultat d'une formule (float) -> Decimal, arrondi à 6 décimales pour
    éviter qu'une imprécision (90.4000000001) ne fasse monter l'arrondi."""
    return Decimal(str(round(float(valeur), 6)))


def _arrondi_superieur(valeur):
    return int(math.ceil(valeur))


def _constantes_prix(diametre=None):
    """taxe, taux et tolérance ; la tolérance du diamètre remplace la constante commune."""
    from gestion_prix_fer.models import Constante
    valeurs = {c.cle: c.valeur for c in Constante.objects.filter(cle__in=CONSTANTES_PRIX)}
    if diametre is not None:
        tolerance = ToleranceDiametre.objects.filter(diametre=diametre).first()
        if tolerance is not None:
            valeurs["tolerance"] = tolerance.valeur
    manquantes = [c for c in CONSTANTES_PRIX if c not in valeurs]
    if manquantes:
        raise CalculImpossible("Constantes manquantes dans l'admin : " + ", ".join(manquantes) + ".")
    return valeurs


def _une(modele, message, **filtres):
    objet = modele.objects.filter(**filtres).first()
    if objet is None:
        raise CalculImpossible(message)
    return objet


def calculer(config, saisies):
    """
    config  : ConfigProduit
    saisies : dict envoyé par la page produit :
        fer        "bending iron" ou "le client"
        marque_fer nom de la marque (ex. "prometal")
        type_fer   type (ex. "fe500", sans tenir compte des majuscules)
        diametre   ex. 8
        angle      valeur de l'angle (ex. 90) ; obligatoire si le produit propose des angles
        dimensions {abréviation: valeur en cm}  (ex. {"Lc": 20})
        quantite   nombre de pièces (1 par défaut)
    Renvoie un ResultatCalcul ou lève CalculImpossible.
    """
    produit = config.produit
    if produit.sous_categorie not in SOUS_CATEGORIES_AUTORISEES:
        raise CalculImpossible("Ce produit n'utilise pas le gabarit universel.")

    # --- 1) Contrôle des saisies ------------------------------------------ #
    fer = (saisies.get("fer") or "").strip().lower()
    if fer not in (FER_BENDING_IRON, FER_CLIENT):
        raise CalculImpossible("Précisez qui fournit le fer.", "fer")

    marque_nom = (saisies.get("marque_fer") or "").strip()
    if not marque_nom:
        raise CalculImpossible("Choisissez la marque du fer.", "marque_fer")
    type_nom = (saisies.get("type_fer") or "").strip()
    if not type_nom:
        raise CalculImpossible("Choisissez le type de fer.", "type_fer")

    try:
        d = int(saisies.get("diametre"))
    except (TypeError, ValueError):
        raise CalculImpossible("Choisissez un diamètre.", "diametre")
    if d not in config.diametres:
        raise CalculImpossible(f"Le diamètre HA{d} n'est pas proposé pour ce produit.", "diametre")

    angles = {a.valeur: a for a in config.angles.filter(actif=True)}
    if angles:
        try:
            angle = angles[int(saisies.get("angle"))]
        except (TypeError, ValueError, KeyError):
            raise CalculImpossible("Choisissez un angle proposé pour ce produit.", "angle")
        variables_angle = angle.variables()
    else:
        angle = None
        variables_angle = {"angle": 0, "ka": 1.0}

    saisies_dimensions = saisies.get("dimensions") or {}
    dimensions, libelles = {}, {}
    for dim in config.dimensions.all():
        champ = f"dim_{dim.abreviation}"
        if saisies_dimensions.get(dim.abreviation) in (None, ""):
            raise CalculImpossible(f"{dim.libelle} : valeur manquante.", champ)
        try:
            valeur = _decimal(saisies_dimensions[dim.abreviation], dim.libelle)
        except CalculImpossible as exc:
            raise CalculImpossible(str(exc), champ)
        if not (dim.minimum <= valeur <= dim.maximum):
            raise CalculImpossible(f"{dim.libelle} doit être comprise entre "
                                   f"{float(dim.minimum):g} et {float(dim.maximum):g} cm.", champ)
        dimensions[dim.abreviation] = valeur
        libelles[dim.abreviation] = dim.libelle

    try:
        quantite = int(saisies.get("quantite") or 1)
    except (TypeError, ValueError):
        raise CalculImpossible("Quantité invalide.", "quantite")
    if quantite < 1:
        raise CalculImpossible("La quantité doit être d'au moins 1 pièce.", "quantite")

    parametres = ParametresCalcul.actuels()
    if parametres is None:
        raise CalculImpossible("Paramètres de calcul non renseignés dans l'admin.")

    # --- 2 à 5) Longueurs ------------------------------------------------- #
    try:
        r = _depuis_formule(evaluer(config.formule_r_effective(), {"d": d}))
        variables = {**{k: float(v) for k, v in dimensions.items()}, "d": d, **variables_angle, "R": float(r)}
        ltp = _depuis_formule(evaluer(config.formule_ltp, variables))
    except FormuleInvalide as exc:
        raise CalculImpossible(f"Formule du produit invalide : {exc}")
    if ltp < 0:
        raise CalculImpossible("Longueur calculée négative : vérifiez la formule du produit.")

    constante = parametres.constante_ldf_court if ltp <= parametres.seuil_ldf else parametres.constante_ldf_long
    ldf = ltp * constante
    lt = _arrondi_superieur(ltp + ldf)
    variables.update({"Ltp": float(ltp), "Ldf": float(ldf), "Ld": float(ldf), "Lt": lt})   # pour le dessin

    # --- 6) Poids --------------------------------------------------------- #
    poids_cm = _une(PoidsFer, f"Poids au cm du HA{d} non renseigné dans l'admin.", diametre=d)
    poids = Decimal(lt) * poids_cm.kg_par_cm

    # --- 7) Prix du fer --------------------------------------------------- #
    prix = _une(PrixFerTonne,
                f"Prix du fer {marque_nom} {type_nom.upper()} HA{d} non renseigné dans l'admin.",
                type_fer__fournisseur__nom__iexact=marque_nom, type_fer__nom__iexact=type_nom,
                diametre=d)
    prt = _une(PrtFer, f"PrT {marque_nom} HA{d} non renseigné dans l'admin.",
               marque=prix.type_fer.fournisseur, diametre=d).prt
    pak, pvk = prix.pat / prt, prix.pvt / prt
    pv = poids * pvk if fer == FER_BENDING_IRON else poids * (pvk - pak)

    # --- 8) Façonnage ----------------------------------------------------- #
    coef = _une(CoefFaconnage, f"Coefficient de façonnage {marque_nom} HA{d} non renseigné dans l'admin.",
                marque=prix.type_fer.fournisseur, diametre=d)
    ps = coef.coef * Decimal(lt) / 100

    # --- 9) Soudure ------------------------------------------------------- #
    soudure = _une(ConstanteSoudure, f"Constante de soudure du HA{d} non renseignée dans l'admin.", diametre=d)
    pd = soudure.valeur * Decimal(lt)

    # --- 10) Prix unitaire ------------------------------------------------ #
    c = _constantes_prix(d)
    pu = _arrondi_superieur((pv + ps + c["tolerance"] + c["taxe"] + pd) * (1 + c["taux"]))

    details = {
        "fer": fer,
        "marque_fer": prix.type_fer.fournisseur.nom,
        "type_fer": prix.type_fer.nom,
        "diametre": d,
        **({"angle": angle.libelle} if angle else {}),
        **{libelles[k]: f"{float(v):g} cm" for k, v in dimensions.items()},
        **({"rayon_Courbure": float(r)} if config.afficher_r else {}),
        **({"longueur_Depart_et_Fin": float(round(ldf, 2))} if config.afficher_ld else {}),
        "longueur_Total": lt,
        "poids_kg": float(round(poids, 4)),
    }
    return ResultatCalcul(ltp=ltp, ldf=ldf, lt=lt, r=r, poids=poids, pak=pak, pvk=pvk, pv=pv, ps=ps,
                          pd=pd, pu=pu, quantite=quantite, details=details, variables=variables)
