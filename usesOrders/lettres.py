"""Montants en toutes lettres, en français (factures : « Arrêtée la présente facture à la somme de … »).

Règles appliquées (orthographe traditionnelle) :
  - « et » pour 21, 31, 41, 51, 61, 71 (vingt et un, soixante et onze), pas pour 81, 91 ;
  - trait d'union entre dizaines et unités (vingt-deux, quatre-vingt-dix) ;
  - « vingts » et « cents » prennent un s s'ils terminent le nombre ou précèdent
    million / milliard (quatre-vingts, deux cents millions), pas devant « mille »
    ni suivis d'un autre nombre (deux cent mille, deux cent un) ;
  - « mille » est invariable ; « million » et « milliard » prennent un s au pluriel.
"""
from decimal import ROUND_HALF_UP, Decimal

UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
          "onze", "douze", "treize", "quatorze", "quinze", "seize"]
DIZAINES = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante"}


def _moins_de_cent(n, final):
    if n <= 16:
        return UNITES[n]
    if n < 20:
        return "dix-" + UNITES[n - 10]
    dizaine, unite = divmod(n, 10)
    if dizaine in (7, 9):                       # soixante-dix…, quatre-vingt-dix…
        base = "soixante" if dizaine == 7 else "quatre-vingt"
        reste = 10 + unite
        if dizaine == 7 and unite == 1:
            return "soixante et onze"
        return f"{base}-{_moins_de_cent(reste, final)}"
    if dizaine == 8:
        if unite == 0:
            return "quatre-vingts" if final else "quatre-vingt"
        return "quatre-vingt-" + UNITES[unite]
    mot = DIZAINES[dizaine]
    if unite == 0:
        return mot
    if unite == 1:
        return f"{mot} et un"
    return f"{mot}-{UNITES[unite]}"


def _moins_de_mille(n, final):
    """final : le groupe termine le nombre ou précède million(s) / milliard(s)."""
    centaine, reste = divmod(n, 100)
    if centaine == 0:
        return _moins_de_cent(reste, final)
    if centaine == 1:
        mot = "cent"
    else:
        mot = UNITES[centaine] + " cent" + ("s" if reste == 0 and final else "")
    if reste:
        mot += " " + _moins_de_cent(reste, final)
    return mot


def en_lettres(nombre):
    """Entier (ou montant arrondi au franc) -> mots, ex. 5149261 ->
    « cinq millions cent quarante-neuf mille deux cent soixante et un »."""
    n = int(Decimal(str(nombre)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if n < 0:
        return "moins " + en_lettres(-n)
    if n == 0:
        return UNITES[0]

    milliards, n = divmod(n, 1_000_000_000)
    millions, n = divmod(n, 1_000_000)
    milliers, unites = divmod(n, 1000)
    mots = []
    if milliards:
        mots.append(("un milliard" if milliards == 1 else en_lettres(milliards) + " milliards"))
    if millions:
        mots.append("un million" if millions == 1 else _moins_de_mille(millions, True) + " millions")
    if milliers:
        mots.append("mille" if milliers == 1 else _moins_de_mille(milliers, False) + " mille")
    if unites:
        mots.append(_moins_de_mille(unites, True))
    return " ".join(mots)
