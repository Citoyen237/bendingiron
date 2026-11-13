"""Statistiques annuelles du tableau de bord (proposition D, 12/11/2026).

Blocs calculés : chiffre d'affaires, encaissements, commandes, clients, produits.
Bénéfice et stock ne sont PAS calculés tant que les préalables ne sont pas faits
(P1 : coût de revient réel enregistré ; P2 : calcul du stock corrigé), sinon les
chiffres seraient faux.

Montants : ceux des factures (net à payer, TTC), comme sur les PDF.
Commandes annulées : retirées du chiffre d'affaires, du nombre de commandes et du
reste à encaisser ; elles ont leur propre bloc (_annulations). Leurs paiements
restent dans les encaissements tant qu'aucun remboursement n'est enregistré
(proposition G).
"""
from collections import Counter, defaultdict
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

MOIS = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]

TYPES = [   # (clé, libellé)
    ("client", "Commandes client"),
    ("proforma", "Proformas"),
    ("projet", "Projets"),
    ("additionnel", "Commandes additionnelles"),
]


def _periode(champ, annee):
    """Filtre « champ dans l'année » sans fonction de date côté MySQL : sans tables
    de fuseaux horaires, MySQL renvoie NULL pour created_at__year (aucun résultat)."""
    from datetime import datetime
    tz = timezone.get_current_timezone()
    debut = timezone.make_aware(datetime(annee, 1, 1), tz)
    fin = timezone.make_aware(datetime(annee + 1, 1, 1), tz)
    return {f"{champ}__gte": debut, f"{champ}__lt": fin}


def _mois(date):
    """Numéro du mois (0 à 11), à l'heure de Douala."""
    if timezone.is_aware(date):
        date = timezone.localtime(date)
    return date.month - 1


def _mode(texte):
    """Mode de paiement saisi à la main -> libellé commun (« om » -> « Orange Money »)."""
    m = (texte or "").strip().lower()
    if not m:
        return "Autre"
    if m in ("om", "orange", "orange money") or "orange" in m:
        return "Orange Money"
    if m in ("momo", "mtn", "mtn momo", "mobile money") or "mtn" in m or "momo" in m:
        return "MTN MoMo"
    if "cash" in m or "esp" in m:
        return "Espèces"
    if "ch" in m and "que" in m:
        return "Chèque"
    if "vir" in m or "banc" in m or "banq" in m:
        return "Virement bancaire"
    return texte.strip().capitalize()


def _entier(valeur):
    return int(round(Decimal(valeur or 0)))


def _evolution(actuel, precedent):
    """Évolution en % par rapport à l'année précédente (None si pas de base)."""
    if not precedent:
        return None
    return round((actuel - precedent) * 100 / precedent, 1)


def _annulees():
    """{type: ensemble des identifiants de commandes annulées}."""
    from usesOrders.models import Annulation
    ids = defaultdict(set)
    for type_commande, commande_id in Annulation.objects.values_list("type_commande", "commande_id"):
        ids[type_commande].add(commande_id)
    return ids


def _commandes_de_l_annee(annee):
    """Commandes de l'année, SANS les commandes annulées."""
    annulees = _annulees()
    cmd = _toutes_les_commandes(annee)
    for cle, type_commande in (("client", "client"), ("proforma", "proforma"),
                               ("additionnel", "additionnel"), ("commandes_projet", "projet")):
        cmd[cle] = [c for c in cmd[cle] if c.id not in annulees[type_commande]]
    return cmd


def _toutes_les_commandes(annee):
    from partenaires.models import OrderAdd, Projet, ProjetOrder
    from proforma.models import OrderPro
    from usesOrders.models import Order

    return {
        "client": list(Order.objects.filter(**_periode("created_at", annee))
                       .select_related("user").prefetch_related("orderitem_set__produit", "payments",
                                                                "traiment_set", "orderuserinfo_set")),
        "proforma": list(OrderPro.objects.filter(**_periode("created_at", annee))
                         .prefetch_related("orderitempro_set__produit", "payments", "orderuserinfopro_set")),
        "projet": list(Projet.objects.filter(**_periode("created_at", annee))
                       .select_related("partenariat").prefetch_related("projetitems__produit", "paiements")),
        "additionnel": list(OrderAdd.objects.filter(**_periode("created_at", annee))
                            .prefetch_related("orderitemadd_set__produit", "payments_add")),
        "commandes_projet": list(ProjetOrder.objects.filter(**_periode("created_at", annee))
                                 .prefetch_related("projet_order_name")),
    }


def _chiffre_affaires(cmd):
    par_mois = {cle: [0] * 12 for cle, _ in TYPES}
    total = {cle: 0 for cle, _ in TYPES}
    ht = tva = remises = 0
    for cle, _ in TYPES:
        for c in cmd[cle]:
            net = _entier(c.net_payer)
            par_mois[cle][_mois(c.created_at)] += net
            total[cle] += net
            tva += _entier(c.montant_tva)
            if cle == "projet":
                ht += _entier(c.montant_apres_remise)
            else:
                ht += _entier(c.get_prix_total)
            if cle == "client":
                remises += _entier(c.montant_remise())
    return {
        "par_mois": par_mois,
        "par_type": total,
        "total": sum(total.values()),
        "ht": ht, "tva": tva, "remises_promo": remises,
    }


def _encaissements(annee, cmd):
    from paiements.models import DemandePaiement
    from partenaires.models import PaiementProjet, PaymentAdd
    from proforma.models import PaymentPro
    from usesOrders.models import Payment

    par_mois = [0] * 12
    modes = Counter()
    for p in Payment.objects.filter(**_periode("created_at", annee)):
        par_mois[_mois(p.created_at)] += _entier(p.amount_paid)
    for p in PaymentPro.objects.filter(**_periode("created_at", annee)):
        par_mois[_mois(p.created_at)] += _entier(p.amount_paid)
        modes[_mode(p.mode_paid)] += _entier(p.amount_paid)
    for p in PaymentAdd.objects.filter(**_periode("created_at", annee)):
        par_mois[_mois(p.created_at)] += _entier(p.amount_paid)
        modes[_mode(p.mode_paid)] += _entier(p.amount_paid)
    for p in PaiementProjet.objects.filter(**_periode("date_paiement", annee)):
        par_mois[_mois(p.date_paiement)] += _entier(p.montant)
        modes[_mode(p.mode_paiement)] += _entier(p.montant)

    # Paiements en ligne des commandes client : opérateur connu par la demande de paiement
    demandes = DemandePaiement.objects.filter(**_periode("created_at", annee))
    for d in demandes.filter(statut=DemandePaiement.Statut.CONFIRME):
        modes[_mode(d.provider)] += _entier(d.montant)
    statuts = dict(demandes.values_list("statut").annotate(n=Count("id")))
    nb_demandes = sum(statuts.values())
    echecs = statuts.get(DemandePaiement.Statut.ECHEC, 0) + statuts.get(DemandePaiement.Statut.EXPIRE, 0)

    # Reste à encaisser sur les commandes de l'année
    reste = 0
    for c in cmd["client"]:
        reste += max(_entier(c.net_payer) - sum(_entier(p.amount_paid) for p in c.payments.all()), 0)
    for c in cmd["proforma"] + cmd["additionnel"]:
        reste += _entier(c.reste_a_payer)
    for p in cmd["projet"]:
        reste += max(_entier(p.net_payer) - sum(_entier(x.montant) for x in p.paiements.all()), 0)

    return {
        "par_mois": par_mois,
        "total": sum(par_mois),
        "reste": reste,
        "modes": sorted(modes.items(), key=lambda m: -m[1]),
        "demandes": nb_demandes,
        "echecs": echecs,
        "taux_echec": round(echecs * 100 / nb_demandes, 1) if nb_demandes else None,
    }


def _delai_jours(traitements):
    """Jours entre le premier traitement et « termine » (None si pas terminée)."""
    traitements = sorted(traitements, key=lambda t: t.created_at)
    fin = next((t for t in traitements if t.statut == "termine"), None)
    if not traitements or fin is None:
        return None
    return (fin.created_at - traitements[0].created_at).total_seconds() / 86400


def _commandes(cmd, ca):
    par_mois = {
        "client": [0] * 12, "proforma": [0] * 12,
        "projet": [0] * 12, "additionnel": [0] * 12,
    }
    for cle in ("client", "proforma", "additionnel"):
        for c in cmd[cle]:
            par_mois[cle][_mois(c.created_at)] += 1
    for c in cmd["commandes_projet"]:   # commandes passées sur les projets
        par_mois["projet"][_mois(c.created_at)] += 1

    delais = [d for d in (_delai_jours(c.traiment_set.all()) for c in cmd["client"]) if d is not None]
    terminees = sum(1 for c in cmd["client"] if c.get_statut_actuel == "termine")
    nb_client = len(cmd["client"])
    return {
        "par_mois": par_mois,
        "nombre": {cle: sum(v) for cle, v in par_mois.items()},
        "total": sum(sum(v) for v in par_mois.values()),
        "projets_crees": len(cmd["projet"]),
        "panier_moyen": round(ca["par_type"]["client"] / nb_client) if nb_client else 0,
        "delai_moyen_jours": round(sum(delais) / len(delais), 1) if delais else None,
        "client_terminees": terminees,
        "client_en_cours": nb_client - terminees,
    }


def _clients(annee, cmd):
    from auth_app.models import CustomUser
    from usesOrders.models import CodePromoUse

    nouveaux = [0] * 12
    for u in CustomUser.objects.filter(**_periode("date_joined", annee), is_staff=False, is_superuser=False):
        nouveaux[_mois(u.date_joined)] += 1

    montants, nb_commandes = defaultdict(int), Counter()
    noms = {}
    for c in cmd["client"]:
        montants[c.user_id] += _entier(c.net_payer)
        nb_commandes[c.user_id] += 1
        noms[c.user_id] = (f"{c.user.first_name} {c.user.last_name}".strip() or c.user.email)
    top = sorted(montants.items(), key=lambda m: -m[1])[:10]

    partenaires = defaultdict(int)
    for p in cmd["projet"]:
        partenaires[p.partenariat.name] += _entier(p.net_payer)

    actifs = len(montants)
    return {
        "nouveaux_par_mois": nouveaux,
        "nouveaux": sum(nouveaux),
        "actifs": actifs,
        "fideles": sum(1 for n in nb_commandes.values() if n >= 2),
        "taux_fideles": round(sum(1 for n in nb_commandes.values() if n >= 2) * 100 / actifs, 1) if actifs else None,
        "top": [{"nom": noms[uid], "montant": m, "commandes": nb_commandes[uid]} for uid, m in top],
        "top_partenaires": sorted(partenaires.items(), key=lambda m: -m[1])[:10],
        "codes_promo": CodePromoUse.objects.filter(**_periode("used_at", annee)).count(),
    }


def _diametre(details):
    """Diamètre lu dans la description de la ligne (ex. 8), ou None."""
    if not isinstance(details, dict):
        return None
    for cle, valeur in details.items():
        if cle.lower() in ("diametre", "diamètre"):
            try:
                return int(float(str(valeur).lower().replace("ha", "").strip()))
            except ValueError:
                return None
    return None


def _produits(cmd):
    quantites, montants, diametres = Counter(), Counter(), Counter()
    lignes = []
    for c in cmd["client"]:
        lignes += list(c.orderitem_set.all())
    for c in cmd["proforma"]:
        lignes += list(c.orderitempro_set.all())
    for c in cmd["additionnel"]:
        lignes += list(c.orderitemadd_set.all())
    for p in cmd["projet"]:
        lignes += list(p.projetitems.all())
    for ligne in lignes:
        nom = ligne.produit.nom
        quantites[nom] += ligne.quantite
        montants[nom] += _entier(ligne.prix_u * ligne.quantite)
        d = _diametre(ligne.details)
        if d:
            diametres[f"HA{d}"] += ligne.quantite
    return {
        "top_quantite": quantites.most_common(10),
        "top_montant": montants.most_common(10),
        "diametres": sorted(diametres.items(), key=lambda x: int(x[0][2:])),
    }


STATUTS_AVANT = {
    "aucun": "Aucun traitement", "en_attente": "En attente", "en_production": "En production",
    "pret_pour_livraison": "Prêt pour livraison", "solde_facture": "Facture soldée",
}


def _annulations(annee):
    """Commandes annulées dans l'année (date d'annulation).

    remboursements à faire / faits et retenues : préparés pour la proposition G
    (None = pas encore géré, affiché « — »).
    """
    from usesOrders.models import Annulation
    annulations = list(Annulation.objects.filter(**_periode("created_at", annee)))
    nombre = {cle: 0 for cle, _ in TYPES}
    montant = {cle: 0 for cle, _ in TYPES}
    par_mois = [0] * 12
    statuts = Counter()
    for a in annulations:
        nombre[a.type_commande] += 1
        montant[a.type_commande] += _entier(a.montant_commande)
        par_mois[_mois(a.created_at)] += 1
        statuts[a.statut_avant] += 1
    gere = any(a.montant_rembourse is not None or a.montant_retenu is not None for a in annulations)
    a_rembourser = rembourse = retenu = None
    if gere:   # proposition G en place
        rembourse = sum(_entier(a.montant_rembourse) for a in annulations)
        retenu = sum(_entier(a.montant_retenu) for a in annulations)
        a_rembourser = max(sum(_entier(a.montant_paye) for a in annulations) - rembourse - retenu, 0)
    return {
        "nombre": nombre,
        "total": len(annulations),
        "montant": montant,
        "montant_total": sum(montant.values()),
        "par_mois": par_mois,
        "par_statut": [(STATUTS_AVANT.get(s, s), n) for s, n in
                       sorted(statuts.items(), key=lambda x: list(STATUTS_AVANT).index(x[0])
                              if x[0] in STATUTS_AVANT else 99)],
        "deja_paye": sum(_entier(a.montant_paye) for a in annulations),
        "a_rembourser": a_rembourser,
        "rembourse": rembourse,
        "retenu": retenu,
    }


def statistiques(annee):
    """Toutes les statistiques d'une année, plus la comparaison avec l'année précédente."""
    cmd = _commandes_de_l_annee(annee)
    ca = _chiffre_affaires(cmd)
    enc = _encaissements(annee, cmd)
    commandes = _commandes(cmd, ca)
    clients = _clients(annee, cmd)

    prec_cmd = _commandes_de_l_annee(annee - 1)
    prec_ca = _chiffre_affaires(prec_cmd)
    prec = {
        "ca": prec_ca["total"],
        "encaisse": _encaissements(annee - 1, prec_cmd)["total"],
        "commandes": _commandes(prec_cmd, prec_ca)["total"],
        "nouveaux": _clients(annee - 1, prec_cmd)["nouveaux"],
    }
    return {
        "annee": annee,
        "mois": MOIS,
        "types": TYPES,
        "ca": ca,
        "encaissements": enc,
        "commandes": commandes,
        "clients": clients,
        "produits": _produits(cmd),
        "annulations": _annulations(annee),
        "precedent": prec,
        "evolution": {
            "ca": _evolution(ca["total"], prec["ca"]),
            "encaisse": _evolution(enc["total"], prec["encaisse"]),
            "commandes": _evolution(commandes["total"], prec["commandes"]),
            "nouveaux": _evolution(clients["nouveaux"], prec["nouveaux"]),
        },
    }


def annees_disponibles():
    """Années qui ont au moins une commande, plus l'année en cours."""
    from usesOrders.models import Order
    from partenaires.models import Projet
    from proforma.models import OrderPro

    annees = {timezone.localdate().year}
    for M in (Order, OrderPro, Projet):
        annees |= {timezone.localtime(d).year for d in M.objects.values_list("created_at", flat=True) if d}
    return sorted(annees, reverse=True)
