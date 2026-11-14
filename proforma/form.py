
from django import forms
from .models import *

class OrderUserInfoFormPro(forms.ModelForm):
    # TVA décidée par l'admin pour cette proforma (14/11/2026)
    appliquer_tva = forms.BooleanField(label="Appliquer la TVA (19,25 %)", required=False, initial=True)

    class Meta:
        model = OrderUserInfoPro
        fields = ['nom', 'telephone','adresse']
        labels = {
            'nom': "Nom complet du client : ",
            'telephone': "Numero de telephone : ",
            'adresse': "Adresse de livraison : ",
        }
    CHOICES2 = [
        ('', ''),
        ('livraison sur chantier', 'Livraison sur chantier'),
        ('retrait en usine', 'Retrait en usine'),
    ] 
     
    mode_livraison = forms.ChoiceField(
        choices=CHOICES2,
        label="Option de livraison",
        required=True,  # Champ requis
            #initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
                # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    def __init__(self, *args, **kwargs):
        super(OrderUserInfoFormPro, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PaymentProForm(forms.ModelForm):
    MODES = [
        ("", "Choisir…"),
        ("virement bancaire", "Virement bancaire"),
        ("Cheque banquaire", "Cheque banquaire"),
        ("Orange Money", "Orange Money"),
        ("mtn momo", "MTN MoMo"),
        ("Cash", "Cash"),
    ]

    mode_paid = forms.ChoiceField(
        choices=MODES,
        label="Mode de paiement",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = PaymentPro
        fields = ["amount_paid"]
        labels = {"amount_paid": "Montant :"}
        widgets = {
            "amount_paid": forms.NumberInput(attrs={"class": "form-control", "min": 1})
        }

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order

    def clean_amount_paid(self):
        montant = self.cleaned_data["amount_paid"]
        reste = self.order.reste_a_payer

        if montant <= 0:
            raise ValidationError("Le montant doit être supérieur à 0.")
        if reste <= 0:
            raise ValidationError("Cette facture est déjà soldée.")
        if montant > reste:
            raise ValidationError(
                f"Le montant dépasse le reste à payer ({reste:,.0f} FCFA)."
            )
        return montant
#orders
#orderitems
#infor_users
#traitements
#