from django.shortcuts import render
from django.conf import settings


def default_map(request):
    return render(request, 'map_default.html',
                  { 'mapbox_access_token' : settings.MAPBOX_ACCESS_TOKEN })

def signup(request):
    return render(request, 'signup.html', {})

def profile(request):
    return render(request, 'profile.html', {})

def privacy(request):
    return render(request, 'privacy.html', {})

def signin(request):
    return render(request, 'signin.html', {})

def index(request):
    return render(request, 'index.html', {})

def product(request):
    return render(request, 'product.html',
                  { 'mapbox_access_token' : settings.MAPBOX_ACCESS_TOKEN })