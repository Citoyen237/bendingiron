from django import forms
from .models import *

# class MultiFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True

# class ContactForm(forms.ModelForm):
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['email', 'nom', 'telephone', 'message', 'type', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 3 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 3 Mo.")
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Le fichier doit être au format PDF.")
        return file

 
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
# class ContactForm(forms.ModelForm):
#     class Meta:
#         model=Contact
#         fiels =['email','nom','message']
#         exclude=['created_at','updated_at','reponse','is_read']
#         labels = {
#             'email':'Email',
#             'message':'Message',
#             'nom':'Nom',
#         }
#         widgets ={
#             'nom':forms.TextInput(attrs={'class':'form-control','placeholder':'votre nom'}),
#             'message':forms.Textarea(attrs={'class':'form-control','row':3}),
#             'email':forms.EmailInput(attrs={'class':'form-control','placeholder':'addresse email'}),
#         }

class ReponseForm(forms.ModelForm):
    class Meta:
        model=Contact
        fiels =['response', 'file_response']
        exclude=['created_at','created_at','email','is_read','message','nom','type','telephone']
        labels = {
            'message':'Message',
        }
        widgets ={
            'reponse':forms.Textarea(attrs={'class':'form-control','row':3}),
            'file_response': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
        }

        def clean_file(self):
            file_response = self.cleaned_data.get('file_response')
            if file_response:
                if file_response.size > 3 * 1024 * 1024:
                    raise forms.ValidationError("Le fichier ne doit pas dépasser 3 Mo.")
                if not file_response.name.lower().endswith('.pdf'):
                    raise forms.ValidationError("Le fichier doit être au format PDF.")
            return file_response