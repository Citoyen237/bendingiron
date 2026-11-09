from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class ParteriatForm(forms.ModelForm):
    class Meta:
        model = Partenariats
        fields = ['user', 'name', 'email', 'adresse', 'telephone', 'date_debut', 'date_fin']
        labels = {
            'user': "Nom de l'referent",
            'name': "Nom de l'entreprise",
            'email': "e-mail de l'entreprise",
            'adresse': "Adresse de l'entreprise",
            'telephone': "Numéro de téléphone de l'entreprise",
            'date_debut': "Date de début du partenariat",
            'date_fin': "Date de fin du partenariat",
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ParteriatForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_partenaire=True)

        # Appliquer Bootstrap à tous les autres champs sauf date_debut/date_fin déjà stylés
        for field_name, field in self.fields.items():
            if field_name not in ['date_debut', 'date_fin']:
                field.widget.attrs.update({'class': 'form-control'})

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['partenariat', 'name','reduction']
        labels = {
            'partenariat': "Choisir le partenaire",
            'name': "Nom du projet",
            'reduction': "Remise (%)"
        }


    MODES = [
        ("personne morale", "Personne morale"),
        ("personne physique", "Personne physique"),
    ]
    
    frais_ingenieurie = forms.ChoiceField(
        choices=MODES,
        label="Frais d'ingenieurie",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    def __init__(self, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_partenariat(self):
        partenariat = self.cleaned_data.get('partenariat')
        if partenariat and partenariat.is_expired:
            raise ValidationError("Ce partenariat a expiré.")
        return partenariat

class OrderAddForm(forms.ModelForm):
    """Partenaire -> Projet. Seul `projet_order` (FK vers Projet) est enregistré ;
    `partenaire` sert uniquement à filtrer la liste des projets."""
 
    partenaire = forms.ModelChoiceField(
        label="Partenaire",
        queryset=Partenariats.objects.order_by("name"),
        empty_label="-- Choisir un partenaire --",
    )
    projet_order = forms.ModelChoiceField(
        label="Projet",
        queryset=Projet.objects.none(),
        empty_label="-- Choisir un projet --",
    )
 
    class Meta:
        model = OrderAdd
        fields = ["projet_order"]
 
    field_order = ["partenaire", "projet_order"]
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        partenaire_id = self.data.get("partenaire", "")
        if partenaire_id.isdigit():
            # Après un POST (erreur de validation) : on recharge la liste filtrée.
            self.fields["projet_order"].queryset = Projet.objects.filter(
                partenariat_id=int(partenaire_id)
            ).order_by("name")
        elif self.instance.pk and self.instance.projet_order_id:
            # Modification d'un OrderAdd existant : on préremplit le partenaire.
            partenariat_id = self.instance.projet_order.partenariat_id
            self.fields["partenaire"].initial = partenariat_id
            self.fields["projet_order"].queryset = Projet.objects.filter(
                partenariat_id=partenariat_id
            ).order_by("name")
 
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
 
    def clean(self):
        cleaned = super().clean()
        partenaire = cleaned.get("partenaire")
        projet = cleaned.get("projet_order")
        if partenaire and projet and projet.partenariat_id != partenaire.pk:
            self.add_error("projet_order", "Ce projet n'appartient pas à ce partenaire.")
        return cleaned

class PaiementProjetForm(forms.ModelForm):
    MODES = [
        ("", "Choisir…"),
        ("virement bancaire", "Virement bancaire"),
        ("Cheque banquaire", "Cheque banquaire"),
        ("Orange Money", "Orange Money"),
        ("mtn momo", "MTN MoMo"),
        ("Cash", "Cash"),
    ]

    mode_paiement = forms.ChoiceField(
        choices=MODES,
        label="Mode de paiement",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = PaiementProjet
        fields = ['tranche', 'mode_paiement']

    def __init__(self, *args, **kwargs):
        self.projet = kwargs.pop('projet')
        super().__init__(*args, **kwargs)

        # Ordre imposé 1 -> 2 -> 3 : seule la prochaine tranche est proposée
        self.prochaine = PaiementProjet.prochaine_tranche(self.projet)
        self.fields['tranche'].choices = [
            (num, f"{label} : {PaiementProjet.montant_prevu(self.projet, num)} FCFA")
            for num, label in PaiementProjet.TRANCHES if num == self.prochaine
        ]
        if self.prochaine:
            self.fields['tranche'].initial = self.prochaine

        # Bootstrap : form-select pour les select, form-control pour le reste
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': css})

    def clean_tranche(self):
        tranche = self.cleaned_data['tranche']
        if self.prochaine is None:
            raise ValidationError("Toutes les tranches de ce projet sont déjà payées.")
        if tranche != self.prochaine:
            raise ValidationError(f"Les tranches se paient dans l'ordre : la prochaine est la tranche {self.prochaine}.")
        return tranche

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.projet = self.projet
        # Montant figé au moment du paiement
        instance.montant = PaiementProjet.montant_prevu(self.projet, instance.tranche)
        if commit:
            instance.save()
        return instance

class PaymentAddForm(forms.ModelForm):
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
        model = PaymentAdd
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
