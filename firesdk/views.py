from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from firesdk.firebaseconn import *
from firesdk.serializers import UserSerializer
from firesdk.utils import *
from firesdk.user_classes.UserClass import UserClass
# Create your views here.


def temp_home(request):
    return render(request, 'coming_soon_base.html', {})


def show_users(request):
    users = get_all_users()

    return render(request, 'show_users.html', {'user_list': users})


class GetSchedule(APIView):

    @csrf_exempt
    def get(self, request, weeks=1):
        # and now you return all the stuff.
        if request.method == 'GET':
            users = generate_schedule(weeks)
            serializer = UserSerializer(users, many=True).data
            return Response(serializer)


class Company(APIView):
    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company_dict = company_to_dict(data['name'], data['departments'])
        add_company(company_dict)

        return Response({'data': data})


class User(APIView):
    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = data['company']
        department = data['department']
        position = data['position']
        email = data['email']
        first_name = data['name']['first']
        last_name = data['name']['last']
        is_part_time = data['isPartTime']

        if type(is_part_time) is not bool:
            raise ValueError("Invalid is_part_time value.")

        user_dict = user_to_dict(position, email, first_name, last_name, is_part_time)

        add_user(user_dict, company, department)

        return Response({'data': data})


class Availability(APIView):
    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = data['company']
        department = data['department']
        email = data['userEmail']

        sunday = data['sunday']
        monday = data['monday']
        tuesday = data['tuesday']
        wednesday = data['wednesday']
        thursday = data['thursday']
        friday = data['friday']
        saturday = data['saturday']

        availability_days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

        availability_dict = availability_to_dict(availability_days)

        set_availability(availability_dict, company, department, email)

        return Response({'data': data})
