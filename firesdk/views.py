from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from firesdk.firebaseconn import *
from firesdk.serializers import UserSerializer
# Create your views here.

def temp_home(request):
    return render(request, 'coming_soon_base.html', {})

def show_users(request):
    users = get_all_users()

    return render(request, 'show_users.html', {'user_list':users})

class GetSchedule(APIView):

    def get(self, request, weeks=1):
        #and now you return all the stuff.
        if request.method == 'GET':
            users = generate_schedule(weeks)
            serializer = UserSerializer(users, many=True).data
            return Response(serializer)

