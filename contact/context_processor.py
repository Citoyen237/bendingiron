from .models import Contact

def unread_messages(request):
    pass
    unread_messages =Contact.get_unread_messages()
    return {
        'unread_messages_count': unread_messages.count(),
        'unread_messages': unread_messages,
    }
