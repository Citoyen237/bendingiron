from django import forms
from .models import CustomUser as User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


class RegisterForm(forms.Form):
    first_name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'nom'}))
    last_name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'prenom'}))
    email=forms.CharField(widget=forms.EmailInput(attrs={"class":"form-control",'placeholder': 'email'}))
    phone=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'numero de telephone'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder': 'mot de passe'}))
    pwd_confirm=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder': 'confirmer le mot de passe'}))

    # username=forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={"class":"form-control"}))
    # pwd=forms.CharField(label='Mots de passe',widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        pwd_confirm = cleaned_data.get("pwd_confirm")
        email = cleaned_data.get("email")

        if password != pwd_confirm:
            self.add_error('pwd_confirm', "Les mots de passe ne correspondent pas.")

        if User.objects.filter(email=email).exists():
            self.add_error('email', "Cet email est déjà utilisé.")
        return cleaned_data
class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
class LoginForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'mot de passe'}))
    email=forms.CharField(widget=forms.EmailInput(attrs={"class":"form-control",'placeholder':'email'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        UserModel = get_user_model()
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Email ou mot de passe incorrect")
            except UserModel.DoesNotExist:
                raise forms.ValidationError("Email ou mot de passe incorrect")
        
        return self.cleaned_data