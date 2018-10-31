from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from firesdk.firebase_functions.firebaseconn import *
from firesdk.firebase_functions.firebaseauth import *
from firesdk.serializers import *
from firesdk.util.utils import *
# Create your views here.


def temp_home(request):
    return render(request, 'coming_soon_base.html', {})


class Company(APIView):
    """
    Handles specific companies.
    """

    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = org_names_filter(data['name'])
        departments = []

        for department in data['departments']:
            departments.append(org_names_filter(department))

        company_dict = company_to_dict(company, departments)
        add_company(company_dict)

        return Response({'data': data})


class User(APIView):
    """
    Handles specific users in a company department.
    """

    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])
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

    @csrf_exempt
    def get(self, request, company, department, encoded_email):
        if request.method == 'GET':
            user = get_user(company, department, encoded_email)

            serializer = UserSerializer(user).data

            return Response({'user': serializer})


class Users(APIView):
    """
    Handles all users in a company department.
    """

    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            users = get_users(company, department)

            serializer = UserSerializer(users, many=True).data
            # can't use this one because availability might not be set yet.
            # serializer = UserSerializerWithAvailability(users, many=True).data

            return Response({'users': serializer})


class Availability(APIView):
    """
    Handles the availability of specific users in a company department.
    """

    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])
        email = encode_email(data['userEmail'])

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

    @csrf_exempt
    def get(self, request, company, department, encoded_email):
        if request.method == 'GET':
            user = get_user(company, department, encoded_email)

            serializer = AvailabilitySerializer(user).data

            return Response(serializer)


class Needs(APIView):
    """
    Handles the needs of a specific department in a company.
    """

    parser_classes = (JSONParser,)

    @csrf_exempt
    def post(self, request):
        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])

        shift_length = data['shiftLength']

        sunday = data['sunday']
        monday = data['monday']
        tuesday = data['tuesday']
        wednesday = data['wednesday']
        thursday = data['thursday']
        friday = data['friday']
        saturday = data['saturday']

        needs_days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

        needs_dict = needs_to_dict(needs_days, shift_length)

        set_needs(needs_dict, company, department)

        return Response({'data': data})

    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            needs = get_needs(company, department)

            serializer = NeedsSerializer(needs).data

            return Response(serializer)


class CompanyCode(APIView):

    @csrf_exempt
    def get(self, request, company_code):
        if request.method == 'GET':
            is_valid = is_valid_company_code(company_code)

            return Response(is_valid)
