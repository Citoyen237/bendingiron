from django.shortcuts import render

# Create your views here.
def index(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'partenaire.html', context)

def detail_projet(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'detail-projet.html', context)