from django.shortcuts import render

# Create your views here.

def temp_home(request):
    return render(request, 'coming_soon_base.html', {})