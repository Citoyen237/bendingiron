from .models import Fer

def seuil_critique_count(request):
    seuil_count = sum(1 for fer in Fer.objects.all() if fer.sueil_atteint)
    return {
        'fer_seuil_critique_count': seuil_count
    }