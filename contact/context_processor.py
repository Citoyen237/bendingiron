from auth_app.permissions import is_admin
from .models import Contact


def unread_messages(request):
    """Messages non lus : uniquement pour le tableau de bord (jamais envoyés aux pages publiques)."""
    if not is_admin(getattr(request, "user", None)):
        return {}
    unread = Contact.get_unread_messages()
    return {
        'unread_messages_count': unread.count(),
        'unread_messages': unread,
    }
