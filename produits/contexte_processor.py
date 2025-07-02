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

def constante_global(request):
    taux=FerPrice.objects.filter(diametre='taux').first()
    taxe=FerPrice.objects.filter(diametre='taxe').first()
    m6=FerPrice.objects.filter(diametre='m6').first()
    m8=FerPrice.objects.filter(diametre='m8').first()
    m10=FerPrice.objects.filter(diametre='m10').first()
    m12=FerPrice.objects.filter(diametre='m12').first()
    m14=FerPrice.objects.filter(diametre='m14').first()
    m16=FerPrice.objects.filter(diametre='m16').first()
    m20=FerPrice.objects.filter(diametre='m20').first()
    m24=FerPrice.objects.filter(diametre='m24').first()
    m27=FerPrice.objects.filter(diametre='m27').first()
    m30=FerPrice.objects.filter(diametre='m30').first()
    m32=FerPrice.objects.filter(diametre='m32').first()
    constante= {
            'taux':taux.prix,
            'taxe':taxe.prix,
            'm6':m6.prix_utile,
            'm8':m8.prix_utile,
            'm10':m10.prix_utile,
            'm12':m12.prix_utile,
            'm14':m14.prix_utile,
            'm16':m16.prix_utile,
            'm20':m20.prix_utile,
            'm24':m24.prix_utile,
            'm27':m27.prix_utile,
            'm30':m30.prix_utile,
            'm32':m32.prix_utile,
    }
    # conversion a deux chiffre apres la virgule
    constante_arrondies = {k: round(v, 2) for k, v in constante.items()}
    return {
        'constantes': json.dumps(constante_arrondies)
    }

# // Convertir les données Python en JSON utilisable par JavaScript
#     const donnees = JSON.parse('{{ donnees_json|safe|escapejs }}');
#     console.log(donnees);

# // Exemple d'utilisation
#     console.log("Clé 1 :", donnees.cle1);
#     console.log("Clé 3 :", donnees.cle3);