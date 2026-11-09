# variable qui peut changer
from .models import *
import json
from django.core.serializers.json import DjangoJSONEncoder
'''
taxe etat : taxe default==4
prix du fer : prixfer
loterance : prixfer*10 //calcul
taux de transaction : taux default==0.04

diametre de diametre
prixfer = prixFer/12000

m6 :2200
m8 : 2900
m10 : 4500
m12 : 6300
m14 : 7500
m16 : 8200
m20 : 10000
m24 : 12000
m27 : 12500
m30 : 14000
m32 : 14500
'''

CLES_DIAMETRES = ['m6', 'm8', 'm10', 'm12', 'm14', 'm16', 'm20', 'm24', 'm27', 'm30', 'm32']


def constante_global(request):
    """Constantes des anciens calculateurs, en UNE requête.
    Une ligne manquante dans FerPrice ne fait plus planter toutes les pages (valeur 0)."""
    lignes = {fp.diametre: fp for fp in FerPrice.objects.filter(diametre__in=['taux', 'taxe'] + CLES_DIAMETRES)}
    constante = {
        'taux': lignes['taux'].prix if 'taux' in lignes else 0,
        'taxe': lignes['taxe'].prix if 'taxe' in lignes else 0,
    }
    for cle in CLES_DIAMETRES:
        constante[cle] = lignes[cle].prix_utile if cle in lignes else 0
    # conversion a deux chiffre apres la virgule
    constante_arrondies = {k: round(v or 0, 2) for k, v in constante.items()}
    return {
        'constantes': json.dumps(constante_arrondies)
    }

# // Convertir les données Python en JSON utilisable par JavaScript
#     const donnees = JSON.parse('{{ donnees_json|safe|escapejs }}');
#     console.log(donnees);

# // Exemple d'utilisation
#     console.log("Clé 1 :", donnees.cle1);
#     console.log("Clé 3 :", donnees.cle3);