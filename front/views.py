from django.shortcuts import render

# Create your views here.
def index(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'index.html',context)

def cgv(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'cgv.html',context)

def about(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'about.html',context)

def services(request):
    current_url = request.get_full_path()
    context = {

        'current_url':current_url,
    }
    return render(request, 'service.html',context)

def get_politique(request):
    return render(request,'politique.html')

def get_domaine_expertise(request):
    return render(request, 'expertise/ingnerie.html')

def get_boutique_expertise(request):
    return render(request, 'expertise/boutique.html')

def get_fa_armature_expertise(request):
    return render(request, 'expertise/fa-armature.html')

def get_pose_armature_expertise(request):
    return render(request, 'expertise/pose-armature.html')