from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _

# admin.register(Contact)
# Register your models here.
admin.site.site_title = _("bendingiron")
admin.site.site_header = _("bendingiron")
admin.site.index_title = _("bendingiron")