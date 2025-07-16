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
        
        # Filtrer les utilisateurs avec is_partenaire=True
        self.fields['user'].queryset = User.objects.filter(is_partenaire=True)

        # Appliquer Bootstrap à tous les autres champs sauf date_debut/date_fin déjà stylés
        for field_name, field in self.fields.items():
            if field_name not in ['date_debut', 'date_fin']:
                field.widget.attrs.update({'class': 'form-control'})