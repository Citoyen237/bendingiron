from django import forms
from .models import *


class SelectAvecOptionsGrisees(forms.Select):
    """Liste déroulante dont certaines options sont affichées mais non sélectionnables."""

    def __init__(self, *args, indisponibles=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.indisponibles = set(indisponibles)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value in self.indisponibles:
            option["label"] = f"{label} (indisponible)"
            option["attrs"]["disabled"] = True
        return option

class OrderUserInfoForm(forms.ModelForm):
    """Formulaire de confirmation d'une commande client.

    pour_soi_possible=True (client connecté) : ajoute le choix « pour moi /
    pour un autre client ». « Pour moi » : nom et téléphone viennent du
    compte (côté serveur), seuls l'adresse et le mode de livraison sont saisis.
    pour_soi_possible=False (admin) : les infos du client sont toujours saisies.
    """
    POUR_MOI = 'moi'
    POUR_AUTRE = 'autre'
    RETRAIT_USINE = 'retrait en usine'

    class Meta:
        model = OrderUserInfo
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
    )

    CHOICES3 = [
        ('', ''),
        ('orange', 'Orange money'),
        ('mtn', 'MTN momo'),
    ]

    mode_payement = forms.ChoiceField(
        choices=CHOICES3,
        label="Moyen de paiement",
        required=True,  # Champ requis
        widget=SelectAvecOptionsGrisees,
    )

    @staticmethod
    def mtn_disponible():
        from paiements.services import MTN_DISPONIBLE
        return MTN_DISPONIBLE

    def clean_mode_payement(self):
        mode = self.cleaned_data['mode_payement']
        if mode == 'mtn' and not self.mtn_disponible():
            raise forms.ValidationError("MTN Mobile Money est indisponible pour le moment. Utilisez Orange Money.")
        return mode

    CHOICES4 = [
        ('', ''),
        ('integrale', 'La totalite'),
        ('tranche', '30%'),
    ]

    reglement = forms.ChoiceField(
        choices=CHOICES4,
        label="Mode de reglement",
        required=True,  # Champ requis
    )

    telephone_pay = forms.FloatField(
        label="Numero de telephone pour paiement",
        required=True,  # Champ requis
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
        })
    )

    pour_qui = forms.ChoiceField(
        choices=[(POUR_MOI, "Cette commande est pour moi"),
                 (POUR_AUTRE, "Pour un autre client")],
        initial=POUR_MOI,
        label="La commande est-elle pour vous ?",
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, pour_soi_possible=False, **kwargs):
        super(OrderUserInfoForm, self).__init__(*args, **kwargs)
        self.pour_soi_possible = pour_soi_possible
        if not self.mtn_disponible():
            self.fields['mode_payement'].widget.indisponibles = {'mtn'}
        if not pour_soi_possible:
            del self.fields['pour_qui']
        # Vérifiés dans clean() selon le choix « pour qui » et le mode de livraison
        for name in ('nom', 'telephone', 'adresse'):
            self.fields[name].required = False
        for name, field in self.fields.items():
            if name != 'pour_qui':
                field.widget.attrs.update({'class': 'form-control'})

    @property
    def pour_moi(self):
        return self.pour_soi_possible and self.cleaned_data.get('pour_qui') == self.POUR_MOI

    def clean(self):
        cleaned = super().clean()
        if not self.pour_moi:
            for name in ('nom', 'telephone'):
                if not (cleaned.get(name) or '').strip():
                    self.add_error(name, "Ce champ est obligatoire.")
        if cleaned.get('mode_livraison') == self.RETRAIT_USINE:
            cleaned['adresse'] = cleaned.get('adresse') or "Retrait en usine"
        elif not (cleaned.get('adresse') or '').strip():
            self.add_error('adresse', "Ce champ est obligatoire pour une livraison.")
        return cleaned

    def infos_client(self, user):
        """Nom, téléphone et adresse à enregistrer sur la commande."""
        data = self.cleaned_data
        if self.pour_moi:
            nom = f"{user.last_name} {user.first_name}".strip() or user.email
            telephone = user.phone_number
        else:
            nom, telephone = data['nom'].strip(), data['telephone'].strip()
        return {"nom": nom, "telephone": telephone, "adresse": data['adresse'],
                "mode_livraison": data['mode_livraison']}

class DistributeurForm(forms.ModelForm):
    class Meta:
        model = CodePromo
        fields = ['client', 'remise','expiration', 'nb_utilidation']
        labels = {
            'client': "Nom complet du client :",
            'remise': "Remise :",
            'expiration': "Expiration (en Mois) :",
            'nb_utilidation':"Nombre d'utilisation",
        }
    
    def __init__(self, *args, **kwargs):
        super(DistributeurForm, self).__init__(*args, **kwargs)
        from django.db.models import Exists, OuterRef

        self.fields['client'].queryset = CustomUser.objects.annotate(
            has_code=Exists(CodePromo.objects.filter(client=OuterRef('pk')))
        ).filter(has_code=False)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})