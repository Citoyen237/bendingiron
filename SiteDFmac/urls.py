
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('front.urls')),
    path('auth/', include('auth_app.urls')),
    path('produits/',include('produits.urls')),
    path('mes-commandes/',include('usesOrders.urls')),
    path('dashboard/',include('admin_site.urls')),
    path('contact/',include('contact.urls')),
    path('admin/', admin.site.urls),   
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
