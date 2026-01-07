
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

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
    path('larue/', admin.site.urls),   
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
