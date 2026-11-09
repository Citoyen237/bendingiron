"""
Règles d'accès communes à tout le projet.

Avant, la fonction is_admin() était recopiée dans plusieurs applications et
certaines vues l'oubliaient. Tout passe maintenant par ce module.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

ADMIN_GROUPS = ("admin", "superadmin")


def is_admin(user):
    """Vrai pour un utilisateur connecté membre du groupe admin ou superadmin."""
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.groups.filter(name__in=ADMIN_GROUPS).exists())
    )


def is_superadmin(user):
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.groups.filter(name="superadmin").exists())
    )


def is_partenaire(user):
    return bool(user and user.is_authenticated and (user.is_partenaire or is_admin(user)))


def _role_required(test):
    """Fabrique un décorateur : non connecté -> page de connexion ; connecté sans le rôle -> 403."""
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not test(request.user):
                raise PermissionDenied("Vous n'avez pas accès à cette page.")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


admin_required = _role_required(is_admin)
superadmin_required = _role_required(is_superadmin)
partenaire_required = _role_required(is_partenaire)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """À placer en PREMIER dans la liste des classes parentes d'une vue du cPanel."""
    raise_exception = False  # non connecté -> redirection vers la connexion

    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Vous n'avez pas accès à cette page.")
        return super().handle_no_permission()


# Ancien nom conservé pour ne pas casser les imports existants
AdminOrSuperAdminRequiredMixin = AdminRequiredMixin


def get_owned_or_404(request, model_or_qs, owner_field="user", **lookup):
    """
    Charge un objet en vérifiant qu'il appartient à l'utilisateur connecté.
    Les administrateurs voient tout. Renvoie 404 (et non 403) pour ne pas
    révéler l'existence d'objets appartenant à d'autres.
    """
    qs = model_or_qs._default_manager.all() if hasattr(model_or_qs, "_default_manager") else model_or_qs
    if not is_admin(request.user):
        qs = qs.filter(**{owner_field: request.user})
    return get_object_or_404(qs, **lookup)
