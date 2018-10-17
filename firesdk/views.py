from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from firesdk.firebaseconn import *
from firesdk.serializers import UserSerializer
# Create your views here.


def temp_home(request):
    return render(request, 'coming_soon_base.html', {})


def show_users(request):
    users = get_all_users()

    return render(request, 'show_users.html', {'user_list':users})


class GetSchedule(APIView):

    @csrf_exempt
    def get(self, request, weeks=1):
        # and now you return all the stuff.
        if request.method == 'GET':
            users = generate_schedule(weeks)
            serializer = UserSerializer(users, many=True).data
            return Response(serializer)


class PostAvailability(APIView):
    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data
        data_availability = data['availability']
        availability_monday = data_availability['monday']

        print(data)
        print(data_availability)
        print(availability_monday)

        return Response({'data': data})

