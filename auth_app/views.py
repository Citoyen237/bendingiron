from .utils import *
from django.contrib import messages
from .form import *
from django.contrib.auth import get_user_model, login,logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
import string
import random
from .utils import *
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponse
from .models import CustomUser as User
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail


token_generator = PasswordResetTokenGenerator()

# email de verification
def send_verification_email(request,user):
    # user=User.objects.get(id=user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    link = f"http://{request.get_host()}/auth/verification-email/{uid}/{token}/"

    send_mail(
        subject="Vérifiez votre adresse email",
        message=f"Cliquez sur ce lien pour confirmer votre email : {link}",
        from_email="contact@bending-iron.com",
        recipient_list=[user.email],
    )

    template="emails/verified_email.html"
    objet="lVérifiez votre adresse email"
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
    
# Create your views here
def loginPage(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():   
           email = form.cleaned_data.get('email')
           password = form.cleaned_data.get('password')
           UserModel = get_user_model()
           try:
                user = UserModel.objects.get(email=email)
                if user.check_password(password):
                    if not user.is_active:
                        messages.error(request, "Votre compte est bloqué. Veuillez contacter l'administration.")
                    else:
                        login(request,user)
                        messages.success(request, f'Bienvenue {user.first_name}!')
                        return redirect('font.index')  # Remplacez 'home' par le nom de l'URL de votre page d'accueil
                else:  
                    messages.error(request, 'Email ou mot de passe incorrect.')
           except UserModel.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect.')    
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form':form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():   
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username=first_name,first_name=first_name,phone_number=phone,last_name=last_name, email=email, password=password)
            user_group = Group.objects.get(name='simple')
            user.groups.add(user_group)
            if user is not None :
                send_verification_email(request,user)
                messages.success(request,'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter')
                message="Un email de vérification vous a été envoyé. Veuillez consulter votre boîte mail"
                return render(request, 'comfirm-register.html', {'message':message})

            else:
                messages.error('erreur')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form':form})

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def resetpass(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                new_password = generate_random_password()
                user.set_password(new_password)
                user.save()

                send_mail(
                    'Réinitialisation de votre mot de passe',
                    f'Votre nouveau mot de passe est : {new_password}',
                    'prodistributionltd@gmail.com',  # Remplacez par votre email
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Un nouveau mot de passe a été envoyé à votre adresse email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "Aucun utilisateur n'est associé à cet email.")
    else:
        form = PasswordResetForm()

    return render(request, 'resetpass.html', {'form':form})

def logoutPage(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


