
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from auth_app.views import admin_login_limite

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', include('front.urls')),
    path('auth/', include('auth_app.urls')),
    path('produits/',include('produits.urls')),
    path('mes-commandes/',include('usesOrders.urls')),
    path('cpanel/',include('admin_site.urls')),
    path('contact/',include('contact.urls')),
    path('partenaire/',include('partenaires.urls')),
    path('dashboard/archives/',include('archives.urls')),
    path('paiements/',include('paiements.urls')),
    path('commande-proforma/',include('proforma.urls')),
    path('boutique/', include('boutique.urls')),   # gabarit universel : calcul en direct, aperçu admin
    # Connexion admin limitée à 5 essais (doit être AVANT admin.site.urls pour être utilisée)
    path('larue/login/', admin_login_limite, name='admin_login_limite'),
    path('larue/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
