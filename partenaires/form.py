from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class ParteriatForm(forms.ModelForm):
    class Meta:
        model = Partenariats
        fields = ['user', 'name', 'email', 'adresse', 'telephone', 'date_debut', 'date_fin']
        labels = {
            'user': "Nom de l'interimaire",
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

    def __init__(self, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_partenariat(self):
        partenariat = self.cleaned_data.get('partenariat')
        if partenariat and partenariat.is_expired:
            raise ValidationError("Ce partenariat a expiré.")
        return partenariat

class PaiementProjetForm(forms.ModelForm):
    class Meta:
        model = PaiementProjet
        fields = ['tranche', 'mode_paiement']

    def __init__(self, *args, **kwargs):
        self.projet = kwargs.pop('projet')
        super().__init__(*args, **kwargs)

        tranches_payees = self.projet.paiements.values_list('tranche', flat=True)
        self.fields['tranche'].choices = [
            (num, label) for num, label in self.fields['tranche'].choices
            if num not in tranches_payees
        ]

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.projet = self.projet
        return instance if not commit else instance.save() or instance
