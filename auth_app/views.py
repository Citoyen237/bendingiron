from .utils import *
from django.contrib import messages
from .form import *
from django.contrib.auth import get_user_model, login,logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponse
from .models import CustomUser as User
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.views.decorators.csrf import ensure_csrf_cookie
# Masque les champs du formulaire (mots de passe) dans les e-mails d'erreur 500
from django.views.decorators.debug import sensitive_post_parameters


token_generator = PasswordResetTokenGenerator()

# email de verification
def send_verification_email(request,user):
    # user=User.objects.get(id=user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    # Lien construit à partir de SITE_URL (https) et non de l'en-tête Host envoyé par le navigateur
    link = settings.SITE_URL + reverse("verify_email", args=[uid, token])

    template="emails/verified_email.html"
    objet="Vérifiez votre adresse email"
    context = {
       'user': user,
       'link':link
    }
    send_custom_email(
            objet,
            template,
            context,
            [user.email]
    )

@login_required
def resend_verification_email(request):
    user=request.user
    if user.email_verified:  # si déjà vérifié
        messages.info(request, "Votre email a déjà été vérifié")
        return redirect("login")
    else:
        send_verification_email(request, request.user)
        message="Un email de vérification vous a été envoyé. Veuillez consulter votre boîte mail"
        return render(request, 'comfirm-register.html', {'message':message})

def verify_email(request,uidb64,token):
    try:
        # Décoder l'ID de l'utilisateur
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Vérifier si l'utilisateur existe et si le token est valide
    if user is not None and token_generator.check_token(user, token):
        user.email_verified = True  # ton champ dans le modèle User
        user.save()
        context = {'user': user}
        send_custom_email(
                 'Bienvenue sur notre site',
                 'emails/confirm_register.html',
                 context,
                 [user.email]
        )
        login(request, user)
        message="Votre email a été vérifié avec succès"
        return render(request, 'comfirm-register.html', {'message':message})
    else:
        message="Lien invalide ou expiré"
        return render(request, 'comfirm-register.html', {'message':message}, status=400)
    
# --- Limitation des tentatives de connexion (anti force brute) ---
MAX_ECHECS = 5
DUREE_BLOCAGE = 15 * 60  # secondes

def _ip(request):
    # Derrière Nginx, l'IP réelle est dans X-Real-IP
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")

def _cle_echecs(request, email):
    return f"login-echecs:{_ip(request)}:{(email or '').lower()}"


@sensitive_post_parameters()
@ensure_csrf_cookie
def loginPage(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '').strip().lower()
            password = form.cleaned_data.get('password')
            cle = _cle_echecs(request, email)

            if cache.get(cle, 0) >= MAX_ECHECS:
                messages.error(request, "Trop de tentatives. Réessayez dans 15 minutes.")
                return render(request, 'login.html', {'form': form}, status=429)

            UserModel = get_user_model()
            user = UserModel.objects.filter(email__iexact=email).first()
            if user is None:
                # Même coût de calcul que pour un compte existant (évite de deviner les e-mails)
                UserModel().set_password(password)
            if user is not None and user.check_password(password):
                if not user.is_active:
                    messages.error(request, "Votre compte est bloqué. Veuillez contacter l'administration.")
                else:
                    cache.delete(cle)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, f'Bienvenue {user.first_name}!')
                    return redirect('font.index')
            else:
                cache.set(cle, cache.get(cle, 0) + 1, DUREE_BLOCAGE)
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form':form})

@sensitive_post_parameters()
@sensitive_post_parameters()
def admin_login_limite(request, extra_context=None):
    """Connexion de l'admin Django (/larue/login/) avec la même limite que le site :
    MAX_ECHECS essais par identifiant et par IP, puis blocage DUREE_BLOCAGE."""
    from django.contrib import admin

    cle = None
    if request.method == "POST":
        cle = "admin-" + _cle_echecs(request, (request.POST.get("username") or "").strip())
        if cache.get(cle, 0) >= MAX_ECHECS:
            return HttpResponse("Trop de tentatives de connexion. Réessayez dans 15 minutes.",
                                status=429, content_type="text/plain; charset=utf-8")

    reponse = admin.site.login(request, extra_context=extra_context)

    if cle:
        if reponse.status_code in (301, 302):   # connexion réussie : redirection vers l'admin
            cache.delete(cle)
        else:                                   # page réaffichée avec l'erreur : échec
            cache.set(cle, cache.get(cle, 0) + 1, DUREE_BLOCAGE)
    return reponse


@sensitive_post_parameters()
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():   
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            # username = e-mail : unique, alors que deux clients peuvent avoir le même prénom
            with transaction.atomic():
                user = User.objects.create_user(username=email, first_name=first_name, phone_number=phone,
                                                last_name=last_name, email=email, password=password)
                user_group, _ = Group.objects.get_or_create(name='simple')
                user.groups.add(user_group)
            send_verification_email(request, user)
            messages.success(request,'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter')
            message="Un email de vérification vous a été envoyé. Veuillez consulter votre boîte mail"
            return render(request, 'comfirm-register.html', {'message':message})
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form':form})

# --- Mot de passe oublié : mécanisme standard de Django ---
# L'utilisateur reçoit un lien signé, à usage unique et limité dans le temps.
# Son mot de passe ne change que lorsqu'il en choisit un nouveau lui-même.
class ResetPasswordView(auth_views.PasswordResetView):
    template_name = 'resetpass.html'
    form_class = PasswordResetForm
    email_template_name = 'emails/password_reset_email.txt'
    html_email_template_name = 'emails/password_reset_email.html'
    subject_template_name = 'emails/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        # Lien construit avec le vrai domaine du site, pas avec l'en-tête Host
        domaine = settings.SITE_URL.split('://', 1)[-1]
        opts = {
            'use_https': settings.SITE_URL.startswith('https'),
            'token_generator': self.token_generator,
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'domain_override': domaine,
        }
        form.save(**opts)
        return redirect(self.get_success_url())


class ResetPasswordDoneView(auth_views.PasswordResetDoneView):
    template_name = 'auth-message.html'
    extra_context = {'titre': 'Mot de passe oublié',
                     'message': "Si un compte existe avec cette adresse, un lien de réinitialisation "
                                "vient d'être envoyé. Pensez à vérifier vos courriers indésirables."}


class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'reset-confirm.html'
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')


class ResetPasswordCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'auth-message.html'
    extra_context = {'titre': 'Mot de passe modifié',
                     'message': "Votre mot de passe a été modifié. Vous pouvez vous connecter."}


def logoutPage(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


def _erreurs_mot_de_passe(motdepasse, user):
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    try:
        validate_password(motdepasse, user)
        return []
    except ValidationError as e:
        return list(e.messages)


@sensitive_post_parameters()
@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            # Récupérer les données du formulaire
            oldpassword = form.cleaned_data.get('oldpassword')
            newpassword = form.cleaned_data.get('newpasspassword')
            confirmpassword = form.cleaned_data.get('confirmpassword')
            # Vérifier si le compte est actif
            if not user.is_active:
                messages.error(
                    request,
                    "Votre compte est bloqué. Veuillez contacter l'administration."
                )
            # Vérifier l'ancien mot de passe
            elif not user.check_password(oldpassword):
                messages.error(
                    request,
                    "L'ancien mot de passe est incorrect."
                )
            # Vérifier que les nouveaux mots de passe correspondent
            elif newpassword != confirmpassword:
                messages.error(
                    request,
                    "Les nouveaux mots de passe ne correspondent pas."
                )
            # Vérifier que le nouveau mot de passe est différent de l'ancien
            elif oldpassword == newpassword:
                messages.error(
                    request,
                    "Le nouveau mot de passe doit être différent de l'ancien."
                )
            elif _erreurs_mot_de_passe(newpassword, user):
                for err in _erreurs_mot_de_passe(newpassword, user):
                    messages.error(request, err)
            else:
                # Enregistrer le nouveau mot de passe
                user.set_password(newpassword)
                user.save()
                # Garder l'utilisateur connecté
                logout(request)
                messages.success(
                    request,
                    "Votre mot de passe a été modifié avec succès."
                )
                return redirect('login')
    else:
        form = ChangePasswordForm()
    return render( request,'change-password.html',{'form': form})

