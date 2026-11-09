from django.urls import path
from .views import *

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('deconnexion/', logoutPage, name='logout'),
    path('creer-un-compte/', register, name='register'),
    path('mot-de-passe-oublier/', ResetPasswordView.as_view(), name='resetpass'),
    path('mot-de-passe-oublier/envoye/', ResetPasswordDoneView.as_view(), name='password_reset_done'),
    path('reinitialiser/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('reinitialiser/termine/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),
    path("verification-email/<uidb64>/<token>/", verify_email, name="verify_email"),
    
    path("changer-le-mot-de-passe", change_password, name="change_password"),
    path("verification-email/", resend_verification_email, name="send_email_verify"),
]
