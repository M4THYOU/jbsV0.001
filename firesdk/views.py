from django.shortcuts import render

from firesdk.firebaseconn import *
# Create your views here.

def temp_home(request):
    return render(request, 'coming_soon_base.html', {})

def show_users(request):
    users = get_all_users()

    return render(request, 'show_users.html', {'user_list':users})

class EmployeeSchedule:
    def get(self, request, format=None):
        #and now you return all the stuff.
        pass
