from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user_email):
    subject = 'Bienvenue sur notre site'
    message = 'Votre compte a été créé avec succès. Nous sommes ravis de vous compter parmi nous.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

def send_custom_email(subject, template_name, context, recipient_list):
    """
    Envoie un email personnalisé.

    :param subject: Sujet de l'email
    :param template_name: Nom du fichier de template HTML pour l'email
    :param context: Contexte pour rendre le template
    :param recipient_list: Liste des destinataires de l'email
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = 'prodistributionltd237@gmail.com'
    
    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )

