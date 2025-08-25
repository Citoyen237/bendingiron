from django.urls import path
from .views import *

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('deconnexion/', logoutPage, name='logout'),
    path('creer-un-compte/', register, name='register'),
    path('mot-de-passe-oublier/', resetpass, name='resetpass'),
    path("verification-email/<uidb64>/<token>/", verify_email, name="verify_email"),
    path("verification-email/", resend_verification_email, name="send_email_verify"),
]
