from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
# noinspection PyUnresolvedReferences
from rest_framework.permissions import IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden

import json

from .models import MetricEvent, PermissionBuffer
from rest_framework_simplejwt.authentication import JWTAuthentication

from firesdk.firebase_functions.firebaseconn import *
from firesdk.firebase_functions.firebaseauth import *
from firesdk.firebase_functions.excel_data_handling import parse_json_from_excel
from firesdk.serializers import *
from firesdk.util.utils import *
from firesdk.util.permissions import Permission, check_perms
# Create your views here.


class CheckServer(APIView):
    """
    Used to check whether or not the server is up.
    """

    # any
    @csrf_exempt
    def get(self, request):
        if request.method == 'GET':

            session_id_object = PermissionBuffer.objects.create()
            session_id = str(session_id_object.pk)

            return Response(session_id)


class Company(APIView):
    """
    Handles specific companies.
    """

    parser_classes = (JSONParser,)

    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)

    # superuser - any
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        try:
            check_perms(meta, user, Permission.superuser, None, None)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

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

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]

        return super(User, self).get_permissions()

    def get_authenticators(self):
        if self.request.method == 'POST':
            self.authentication_classes = [JWTAuthentication]

        return super(User, self).get_authenticators()

    # superuser - any
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        try:
            check_perms(meta, user, Permission.superuser, None, None)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        data = request.data

        company = org_names_filter(data['company'])
        departments = data['departments']
        position = data['position']
        email = data['email']
        first_name = data['name']['first']
        last_name = data['name']['last']
        is_part_time = data['isPartTime']
        account_type = data['accountType']
        status = data['status']

        user_dict = user_to_dict(position, departments, email, first_name, last_name, is_part_time, account_type, status)

        add_user(user_dict, company)

        return Response({'data': data})

    # any authenticated user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.any_authenticated, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            user = get_user(company, encoded_email)

            serializer = UserSerializer(user).data

            return Response(serializer)


class Users(APIView):
    """
    Handles all users in a company department.
    """

    # manager users - their department
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.manager, company, department)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

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

    # any basic user - them
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        data = request.data

        company = org_names_filter(data['company'])
        email = encode_email(data['userEmail'])

        try:
            check_perms(meta, user, Permission.basic, company, email)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        sunday = data['sunday']
        monday = data['monday']
        tuesday = data['tuesday']
        wednesday = data['wednesday']
        thursday = data['thursday']
        friday = data['friday']
        saturday = data['saturday']

        min_max_hours = data['hours']
        min_max_shifts = data['shifts']

        availability_days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

        availability_dict = availability_to_dict(availability_days, min_max_hours, min_max_shifts)

        set_availability(availability_dict, company, email)

        return Response({'data': data})

    # any basic user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.basic, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            availability = get_availability(company, encoded_email)

            serializer = AvailabilitySerializer(availability).data

            return Response(serializer)


class FullAvailability(APIView):
    """
    Handles the availability of all users in a company department.
    """

    parser_classes = (JSONParser,)

    # manager user - their department
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.manager, company, department)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            users_ref = get_user_collection_for_department_ref(company, department)
            users = users_ref.get()

            users_dict = {'users': {}}
            for user_doc in users:
                user_dict = user_doc.to_dict()
                email = user_dict['email']
                encoded_email = encode_email(email)

                avaiability_dict = get_availability(company, encoded_email)

                users_dict['users'][email] = avaiability_dict

            # serializer = AvailabilitySerializer(users_dict).data

            return Response(users_dict)


class Needs(APIView):
    """
    Handles the needs of a specific department in a company.
    """

    parser_classes = (JSONParser,)

    # manager user - their department
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])

        try:
            check_perms(meta, user, Permission.manager, company, department)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

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

    # manager user - their department
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.manager, company, department)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            needs = get_department_needs_ref(company, department).get().to_dict()

            serializer = NeedsSerializer(needs).data

            return Response(serializer)


class DepartmentOpenHours(APIView):
    """
    Handles converting a department's day needs into their open hours and returning the results.
    """

    # superuser - any
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.superuser, None, None)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            needs = get_department_needs_ref(company, department).get().to_dict()

            open_hours = needs_to_open_hours(needs)

            serializer = OpenHoursSerializer(open_hours).data

            return Response(serializer)


class CompanyCode(APIView):
    """
    Handles getting whether or not the company code is real.
    """

    # any
    @csrf_exempt
    def get(self, request, company_code):
        if request.method == 'GET':
            is_valid = is_valid_company_code(company_code)
            company_name = get_company_name_by_company_code(company_code)

            return Response({'is_valid': is_valid, 'name': company_name})


class UserLoginBools(APIView):
    """
    Handles getting is_password_changed and is_onboard_complete, from db.
    """

    parser_classes = (JSONParser,)

    # any authenticated user - them
    @csrf_exempt
    def post(self, request):
        data = request.data

        company = org_names_filter(data['company'])
        email = encode_email(data['email'])

        meta = request.META
        user = request.user

        try:
            check_perms(meta, user, Permission.any_authenticated, company, email)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        password_changed = str_int_to_bool(data['is_password_changed'])
        onboard_complete = str_int_to_bool(data['is_onboard_complete'])

        login_bools_dict = login_bools_to_dict(password_changed, onboard_complete)

        set_login_bools(login_bools_dict, company, email)

        return Response(data)

    # any authenticated user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.any_authenticated, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            onboard = get_login_bools(company, encoded_email)

            serializer = LoginBoolsSerializer(onboard).data

            return Response(serializer)


class UserList(APIView):
    """
    Handles the upload of a list of users in JSON format.
    """

    parser_classes = (JSONParser,)

    # superuser - any
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        try:
            check_perms(meta, user, Permission.superuser, None, None)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        data = request.data

        company = org_names_filter(data['company'])
        users_dict = parse_json_from_excel(data['users'])

        register_user_list(company, users_dict)

        return Response(data)


class AccountType(APIView):
    """
    Handles checking the account type of every user. NO POST.
    """

    parser_classes = (JSONParser,)

    # any authenticated user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.any_authenticated, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            user = get_user(company, encoded_email)

            serializer = AccountTypeSerializer(user).data

            return Response(serializer)


class FullSchedule(APIView):
    """
    Handles the full schedule of each department.
    """

    parser_classes = (JSONParser,)

    # manager users - their department
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])

        try:
            check_perms(meta, user, Permission.manager, company, department)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        schedule_exact_times = data['exactTimes']
        schedule_positions = data['positions']
        schedule_days = data['schedules']

        schedule_dict = schedule_to_dict(schedule_days, schedule_exact_times, schedule_positions)

        set_department_schedule(schedule_dict, company, department)
        set_all_users_schedule(schedule_dict, company, department)

        return Response(schedule_dict)

    # manager users - their department
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.manager, company, department)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            schedule = get_full_schedule(company, department)

            serializer = FullScheduleSerializer(schedule).data

            return Response(serializer)


class UserSchedule(APIView):
    """
    Handles the single schedule of a single user.
    """

    parser_classes = (JSONParser,)

    # any basic user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.basic, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            schedule = get_user_schedule(company, encoded_email)

            print(schedule)

            serializer = UserScheduleSerializer(schedule).data

            return Response(serializer)


class TimeOff(APIView):
    """
    Handles all time off of department users.
    """

    parser_classes = (JSONParser,)

    # superuser - any
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        try:
            check_perms(meta, user, Permission.superuser, None, None)
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])
        email = data['email']

        reasons = data['reasons']
        statuses = data['statuses']

        time_off_days_dict = time_off_days_to_dict(reasons, statuses)

        set_department_time_off_requests(time_off_days_dict, company, department, email)
        set_user_time_off_requests(time_off_days_dict, company, email)

        return Response(data)

    # manager users - their department
    @csrf_exempt
    def get(self, request, company, department):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.manager, company, department)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()

            time_off_ref = get_department_time_off_ref(company, department)
            time_off = time_off_ref.get()
            full_time_off_dict = time_off.to_dict()

            time_off_list = full_time_off_dict_to_list(full_time_off_dict)
            time_off_requests = {
                'time_off_requests': time_off_list
            }

            serializer = FullTimeOffSerializer(time_off_requests).data

            return Response(serializer)


class SingleTimeOff(APIView):
    """
    Handles one time off instance of a single user.
    """

    parser_classes = (JSONParser,)

    # any authenticated user - for manager, their department | for basic, them
    @csrf_exempt
    def post(self, request):
        meta = request.META
        user = request.user

        data = request.data

        company = org_names_filter(data['company'])
        department = org_names_filter(data['department'])
        email = data['email']

        try:
            encoded_email = encode_email(email)
            check_perms(meta, user, Permission.any_authenticated_manager_or_basic, company, [encoded_email, department])
        except ValueError as e:
            print(e)
            return HttpResponseForbidden()

        date = data['date']
        reason = data['reason']
        status = data['status']

        actions = data['action']

        should_delete = actions['delete']
        should_save = actions['save']

        is_valid = true_exclusive_or(should_delete, should_save)
        if not is_valid:
            print('Invalid action specified:', actions)
            return Response()

        if should_save:
            time_off_dict = single_time_off_to_dict(date, reason, status)
            set_single_department_time_off_request(time_off_dict, company, department, email)
            set_single_time_off_request(time_off_dict, company, email)
        else:
            delete_department_time_off_request(date, company, department, email)
            delete_time_off_request(date, company, email)

        return Response(data)

    # any basic user - them
    @csrf_exempt
    def get(self, request, company, encoded_email):
        if request.method == 'GET':
            meta = request.META
            user = request.user

            try:
                check_perms(meta, user, Permission.basic, company, encoded_email)
            except ValueError as e:
                print(e)
                return HttpResponseForbidden()
            time_off = get_user_time_off(company, encoded_email)

            print(time_off)

            serializer = TimeOffSerializer(time_off).data

            return Response(serializer)


class Metrics(APIView):
    """
    Handles entire database metrics.
    """

    blacklist = {
        # 'val@gmail.com': True
    }

    def is_blacklisted(self, email):
        try:
            return self.blacklist[email]
        except KeyError:
            return False

    parser_classes = (JSONParser,)

    # any authenticated user - them
    @csrf_exempt
    def post(self, request):
        data = request.data
        events = data['events']

        # not storing metrics in firebase anymore. It takes longer and costs more $$.
        # add_metric_event(events)

        for event in events:
            email = event['email']

            if self.is_blacklisted(email):
                print('Blacklisted:', email)
                break

            company = event['company']
            department = event['department']
            account_type = event['accountType']

            date = event['date']
            time = event['time']
            timezone = event['timeZoneAbbreviation']

            event_type = event['eventType']
            session_id = event['sessionId']
            event_data = event['data']

            event_data_string = json.dumps(event_data)

            MetricEvent.objects.create(email=email, company=company, department=department, account_type=account_type,
                                       date=date, time=time, timezone_abbreviation=timezone,
                                       event_type=event_type, session_id=session_id, data=event_data_string)

        return Response(data)
