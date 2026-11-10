from django import forms
from .models import CustomUser as User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


class RegisterForm(forms.Form):
    # first_name = prénom, last_name = nom (les textes d'aide étaient inversés)
    first_name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'Votre prénom', 'autocomplete': 'given-name'}))
    last_name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder': 'Votre nom', 'autocomplete': 'family-name'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control",'placeholder': 'email'}))
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

        if email:
            email = email.strip().lower()
            cleaned_data['email'] = email
            if User.objects.filter(email__iexact=email).exists():
                self.add_error('email', "Cet email est déjà utilisé.")

        if password and password == pwd_confirm:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password, User(email=email or '',
                                                 first_name=cleaned_data.get('first_name') or '',
                                                 last_name=cleaned_data.get('last_name') or ''))
            except forms.ValidationError as e:
                self.add_error('password', e)
        return cleaned_data
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm, SetPasswordForm


class PasswordResetForm(DjangoPasswordResetForm):
    """Formulaire Django standard (lien signé à usage unique), avec le style du site."""
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'email', 'autocomplete': 'email'}))


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
class LoginForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'mot de passe'}))
    email=forms.CharField(widget=forms.EmailInput(attrs={"class":"form-control",'placeholder':'email'}))


class ChangePasswordForm(forms.Form):
    oldpassword=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Ancien mot de passe'}))
    newpasspassword=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'nouveau mot passe'}))
    confirmpassword=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'confirmer le nouveau mot de passe'}))
