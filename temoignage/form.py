from django import forms
from .models import Temoignage

# from tinymce.widgets import TinyMCE

class TemoignageForm(forms.ModelForm):
    # desc = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30, 'class':'form-control'}))
    class Meta:
        model =Temoignage
        fiels = ['name','content','image']
        exclude = ['created_at','updated_at']
        labels= {
            'name':'Nom',
            'image':'Image',
            'content':'Temoignage'
        }
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'content':forms.Select(attrs={'class':'form-select'}),
            'content':forms.Textarea(attrs={'class':'form-control','row':3}),
        }