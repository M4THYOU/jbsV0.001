from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views import View

from .forms import LoginForm

from firesdk.firebase_functions.firebaseconn import *
from firesdk.util.utils import availability_to_dict, standard_to_military_time, unfilter_org_names, user_to_dict

from onboarding.onboard import add_single_user, email_single_user

from dashboard.custom.auth_utils import *

import json
from datetime import datetime, timedelta
from collections import defaultdict

# Create your views here.


class BaseDashboardView(View):

    @staticmethod
    def get_base_dict(request):
        session = request.session

        name = session['first_name'] + ' ' + session['last_name']
        position = session['position']
        email = session['email']

        base_dict = {'name': name, 'position': position, 'email': email}
        return base_dict


class Login(View):
    login_form = LoginForm

    def get(self, request):
        if is_authenticated(request):
            return HttpResponseRedirect('/hive/')

        remember_code = False
        try:
            remember_code = request.session['remember_code']
        except KeyError:
            pass

        if remember_code:
            # get company code
            try:
                company_code = request.session['company_id']
            except KeyError:
                company_code = '* Error getting code *'

            form = self.login_form(initial={'company_id': company_code, 'remember_code': True})
        else:
            form = self.login_form()

        return render(request, 'dashboard/login.html', {'login_form': form})

    def post(self, request):
        form = self.login_form(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            token = cd['token']
            email = cd['email']
            company_id = cd['company_id']
            checkbox = cd['remember_code']

            request.session['tk'] = token
            request.session['email'] = email
            request.session['company_id'] = company_id
            request.session['remember_code'] = checkbox

            company_name = get_company_name_by_company_code(company_id)
            user = get_user(company_name, encode_email(email))

            first_name = user['name']['first']
            last_name = user['name']['last']
            position = user['position']
            account_type_int = user['account_type']

            request.session['first_name'] = first_name
            request.session['last_name'] = last_name
            request.session['position'] = position
            request.session['account_type'] = account_type_int

            return HttpResponseRedirect('/hive/')
        else:
            return render(request, 'dashboard/login.html', {'login_form': form})


class Logout(View):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            del request.session['tk']
        except KeyError:
            pass

        try:
            del request.session['email']
        except KeyError:
            pass

        try:
            del request.session['first_name']
        except KeyError:
            pass

        try:
            del request.session['last_name']
        except KeyError:
            pass

        try:
            del request.session['position']
        except KeyError:
            pass

        try:
            if not request.session['remember_code']:
                try:
                    del request.session['company_id']
                except KeyError:
                    pass
        except KeyError:
            pass

        return render(request, 'dashboard/logout.html', {})


class Home(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            return render(request, 'dashboard/basic/index.html', self.get_base_dict(request))
        elif account_type_int == 1:
            return render(request, 'dashboard/manager/index.html', self.get_base_dict(request))
        else:
            raise Http404


class Schedule(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            return render(request, 'dashboard/basic/schedule.html', self.get_base_dict(request))
        elif account_type_int == 1:
            return render(request, 'dashboard/manager/schedule.html', self.get_base_dict(request))
        else:
            raise Http404


class TimeOff(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            raise Http404
        elif account_type_int == 1:
            try:
                company_id = request.session['company_id']
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

            try:
                encoded_email = encode_email(request.session['email'])
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

            company = get_company_name_by_company_code(company_id)
            user = get_user(company, encoded_email)
            department = user['primary_department']

            base_dict = self.get_base_dict(request)
            base_dict['department'] = unfilter_org_names(department)
            return render(request, 'dashboard/manager/timeoff.html', base_dict)
        else:
            raise Http404


class Availability(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            return render(request, 'dashboard/basic/availability.html', self.get_base_dict(request))
        elif account_type_int == 1:
            raise Http404
        else:
            raise Http404


class Needs(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            raise Http404
        elif account_type_int == 1:
            try:
                company_id = request.session['company_id']
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

            try:
                encoded_email = encode_email(request.session['email'])
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

            company = get_company_name_by_company_code(company_id)
            user = get_user(company, encoded_email)
            department = user['primary_department']

            base_dict = self.get_base_dict(request)
            base_dict['department'] = unfilter_org_names(department)

            return render(request, 'dashboard/manager/needs.html', base_dict)
        else:
            raise Http404


class UserList(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            raise Http404
        elif account_type_int == 1:
            try:
                company_id = request.session['company_id']
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

            try:
                encoded_email = encode_email(request.session['email'])
            except KeyError:
                raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

            company = get_company_name_by_company_code(company_id)
            user = get_user(company, encoded_email)

            return render(request, 'dashboard/manager/user_list.html', self.get_base_dict(request))
        else:
            raise Http404


class Settings(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise Http404

        if account_type_int == 0:
            return render(request, 'dashboard/basic/settings.html', self.get_base_dict(request))
        elif account_type_int == 1:
            return render(request, 'dashboard/manager/settings.html', self.get_base_dict(request))
        else:
            raise Http404


class Demo(View):

    def get(self, request):
        return render(request, 'dashboard/demo/demo.html', {})


# START ajax #

def schedule_timeoff(request):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)

    schedule = get_user_schedule(company, encoded_email)
    time_off = get_user_time_off(company, encoded_email)

    schedule_time_off = {
        'schedule': schedule,
        'time_off': time_off
    }

    return JsonResponse(schedule_time_off)


def availability(request):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)

    if request.method == 'GET':
        user_availability = get_availability(company, encoded_email)

        return JsonResponse(user_availability)

    elif request.method == 'POST':
        data = {}
        for key in request.POST.dict().keys():
            data = json.loads(key)

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
        print(availability_days, min_max_hours, min_max_shifts)
        availability_dict = availability_to_dict(availability_days, min_max_hours, min_max_shifts)

        set_availability(availability_dict, company, encoded_email)

        return HttpResponse('Availability successfully updated.')


def day_schedule(request, date_string):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']
    date_string = date_string.replace('-', '/')
    schedule = get_full_schedule(company, department)

    # Provide default schedule if none exists
    if not schedule:
        schedule = {'exactTimes': {}, 'positions': {}}

    exact_times_dict = schedule['exactTimes']
    positions_dict = schedule['positions']

    try:
        exact_times = exact_times_dict[date_string]
    except KeyError:
        print('No users scheduled.')
        return JsonResponse({})
    positions = positions_dict[date_string]

    department_users = get_users(company, department)
    day_schedule_dict = {
        'exact_times': {},
        'positions': {}
    }
    for user in department_users:
        user_email = user['email']
        user_name = user['name']['first'] + ' ' + user['name']['last']

        try:
            time_working = exact_times[user_email]
        except KeyError:
            continue
        position_working = positions[user_email]

        day_schedule_dict['exact_times'][user_name] = time_working
        day_schedule_dict['positions'][user_name] = position_working

    return JsonResponse(day_schedule_dict)


def upcoming_time_off(request, date_string):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    time_off_ref = get_department_time_off_ref(company, department)
    time_off_obj = time_off_ref.get()
    time_off_dict = time_off_obj.to_dict()

    date_string = date_string.replace('-', '/')
    start_date = datetime.strptime(date_string, '%d/%m/%Y').date()
    end_date = start_date + timedelta(days=21)  # next 3 weeks

    department_users = get_users(company, department)
    email_name_key = {}
    name_email_key = {}
    for user in department_users:
        email = user['email']
        name = user['name']['first'] + ' ' + user['name']['last']
        email_name_key[email] = name
        name_email_key[name] = email

    if not time_off_dict:
        time_off_dict = {}

    time_off_current_dict = defaultdict(list)
    for email, time_off in time_off_dict.items():
        for time_off_date_string, status in time_off['statuses'].items():
            actual_date = datetime.strptime(time_off_date_string, '%d/%m/%Y').date()
            if status['approved'] or status['pending']:
                if start_date <= actual_date <= end_date:
                    actual_date_string = actual_date.strftime('%d/%m/%Y')
                    time_off_current_dict[actual_date_string].append({'name': email_name_key[email], 'status': status})

    time_off_current_dict['name_key'] = [name_email_key]

    return JsonResponse(dict(time_off_current_dict))


def update_time_off_request(request):
    data = {}
    for key in request.POST.dict().keys():
        data = json.loads(key)
    print(data)

    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        manager_encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, manager_encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    user_email = data['email']
    time_off_dict = {
        'date': data['date'],
        'status': data['status']
    }

    update_single_time_off_request_no_reason(time_off_dict, company, user_email)
    update_single_department_time_off_request_no_reason(time_off_dict, company, department, user_email)

    response_dict = {
        'date': data['date'],
        'name': data['fullName'],
        'new_status': data['status'],
    }

    return JsonResponse(response_dict)


def needs(request):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    if request.method == 'GET':
        department_needs = get_needs(company, department)

        # Provide default needs if they are not set already.
        if not department_needs:
            department_needs = {
                'needs': {
                    'sunday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'monday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'tuesday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'wednesday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'thursday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'friday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'saturday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                },
                'shiftLength': {
                    'min': 4,
                    'max': 8
                }
            }
        return JsonResponse(department_needs)

    elif request.method == 'POST':
        data = {}
        for key in request.POST.dict().keys():
            data = json.loads(key)

        needs_dict = data
        set_needs(needs_dict, company, department)

        return HttpResponse('Needs successfully updated.')


def full_schedule(request, start_date_string, end_date_string):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    schedule = get_full_schedule(company, department)
    if not schedule:
        schedule = {
            'exactTimes': {},
            'positions': {}
        }

    exact_times_dict = schedule['exactTimes']
    positions_dict = schedule['positions']

    start_date_string = start_date_string.replace('-', '/')
    end_date_string = end_date_string.replace('-', '/')
    start_date = datetime.strptime(start_date_string, '%d/%m/%Y').date()
    end_date = datetime.strptime(end_date_string, '%d/%m/%Y').date()

    current_exact_times_dict = {}
    current_positions_dict = {}
    for working_date, exact_time in exact_times_dict.items():
        real_date = datetime.strptime(working_date, '%d/%m/%Y').date()

        if start_date <= real_date <= end_date:
            current_exact_times_dict[working_date] = exact_time
            current_positions_dict[working_date] = positions_dict[working_date]

    department_users = get_users(company, department)
    email_name_key = {}
    name_email_key = {}
    for user in department_users:
        name = user['name']['first'] + ' ' + user['name']['last']
        email = user['email']
        email_name_key[email] = name
        name_email_key[name] = email

    current_full_schedule_dict = {
        'exact_times': current_exact_times_dict,
        'positions': current_positions_dict,
        'email_name_key': email_name_key,
        'name_email_key': name_email_key
    }

    return JsonResponse(current_full_schedule_dict)


def update_full_schedule(request):
    data = {}
    for key in request.POST.dict().keys():
        data = json.loads(key)

    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        manager_encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, manager_encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    exact_times = data['exactTimes']
    positions = data['positions']
    schedules = {}

    for date_string, working_users in exact_times.items():

        if date_string not in schedules:
            schedules[date_string] = {
                '0': [],  # 0-1
                '1': [],  # 1-2
                '2': [],  # 2-3
                '3': [],  # 3-4
                '4': [],  # 4-5
                '5': [],  # 5-6
                '6': [],  # 6-7
                '7': [],  # 7-8
                '8': [],  # 8-9
                '9': [],  # 9-10
                '10': [],  # 10-11
                '11': [],  # 11-12
                '12': [],  # 12-13
                '13': [],  # 13-14
                '14': [],  # 14-15
                '15': [],  # 15-16
                '16': [],  # 16-17
                '17': [],  # 17-18
                '18': [],  # 18-19
                '19': [],  # 19-20
                '20': [],  # 20-21
                '21': [],  # 21-22
                '22': [],  # 22-23
                '23': [],  # 23-0
            }

        for email, exact_time in working_users.items():
            start_end_times = exact_time.split(' - ')
            start_time = start_end_times[0]
            end_time = start_end_times[1]

            military_start_time = int(standard_to_military_time(start_time).split(':')[0])
            military_end_time = int(standard_to_military_time(end_time).split(':')[0])

            start_index = military_start_time
            end_index = military_end_time - 1

            for index in range(start_index, end_index + 1):
                schedules[date_string][str(index)].append(email)

    schedule_dict = {
        'exactTimes': exact_times,
        'schedules': schedules,
        'positions': positions,
    }

    set_department_schedule(schedule_dict, company, department)
    set_all_users_schedule(schedule_dict, company, department, merge=False)

    return HttpResponse('Schedule successfully updated.')


def get_saved_shifts(request):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    if request.method == 'GET':
        saved_shifts = get_department_saved_shifts(company, department)

        return JsonResponse(saved_shifts)

    elif request.method == 'POST':
        data = {}

        for key in request.POST.dict().keys():
            data = json.loads(key)

        shifts_list = []
        for key, value in data.items():
            shifts_list.append(value)

        shifts_dict = {
            'shifts': shifts_list
        }

        print(shifts_dict)

        set_department_saved_shifts(shifts_dict, company, department)

        return HttpResponse('Saved shifts successfully updated.')


def full_time_off(request, date_string):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    department = user['primary_department']

    time_off_ref = get_department_time_off_ref(company, department)
    time_off_obj = time_off_ref.get()
    time_off_dict = time_off_obj.to_dict()

    date_string = date_string.replace('-', '/')
    current_date = datetime.strptime(date_string, '%d/%m/%Y').date()

    department_users = get_users(company, department)
    email_name_key = {}
    name_email_key = {}
    for user in department_users:
        email = user['email']
        name = user['name']['first'] + ' ' + user['name']['last']
        email_name_key[email] = name
        name_email_key[name] = email

    if not time_off_dict:
        time_off_dict = {}

    past = []
    present = []
    future = []
    for email, time_off in time_off_dict.items():
        for time_off_date_string, status in time_off['statuses'].items():
            time_off_date = datetime.strptime(time_off_date_string, '%d/%m/%Y').date()

            # status = statuses[time_off_date_string]
            reason = time_off['reasons'][time_off_date_string]

            time_off_object = {
                'date': time_off_date_string,

                'email': email,
                'name': email_name_key[email],

                'status': status,
                'reason': reason,
            }

            if time_off_date < current_date:  # past
                past.append(time_off_object)
            elif time_off_date > current_date:  # future
                future.append(time_off_object)
            else:  # today
                present.append(time_off_object)

    all_time_off_dict = {
        'past': past,
        'today': present,
        'upcoming': future
    }

    return JsonResponse(all_time_off_dict)


def user_schedule(request, start_date_string, end_date_string):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 0:
        raise Http404

    schedule = get_user_schedule(company, encoded_email)
    if schedule:
        exact_times_dict = schedule['exact_times']
        positions_dict = schedule['positions']
    else:
        exact_times_dict = {}
        positions_dict = {}

    start_date_string = start_date_string.replace('-', '/')
    end_date_string = end_date_string.replace('-', '/')
    start_date = datetime.strptime(start_date_string, '%d/%m/%Y').date()
    end_date = datetime.strptime(end_date_string, '%d/%m/%Y').date()

    current_exact_times_dict = {}
    current_positions_dict = {}
    for working_date, exact_time in exact_times_dict.items():
        real_date = datetime.strptime(working_date, '%d/%m/%Y').date()

        if start_date <= real_date <= end_date:
            current_exact_times_dict[working_date] = exact_time
            current_positions_dict[working_date] = positions_dict[working_date]

    time_off = get_user_time_off(company, encoded_email)
    if not time_off:
        time_off = {}
    reasons_dict = {}
    statuses_dict = {}
    if 'reasons' in time_off:
        reasons_dict = time_off['reasons']
    if 'status' in statuses_dict:
        statuses_dict = time_off['statuses']

    current_reasons_dict = {}
    current_statuses_dict = {}
    for time_off_date, reason in reasons_dict.items():
        real_date = datetime.strptime(time_off_date, '%d/%m/%Y').date()

        if start_date <= real_date <= end_date:
            current_reasons_dict[time_off_date] = reason
            current_statuses_dict[time_off_date] = statuses_dict[time_off_date]

    current_user_schedule_dict = {
        'exact_times': current_exact_times_dict,
        'positions': current_positions_dict,

        'time_off_reasons': current_reasons_dict,
        'time_off_statuses': current_statuses_dict
    }

    return JsonResponse(current_user_schedule_dict)


def update_user_time_off(request):
    data = {}
    for key in request.POST.dict().keys():
        data = json.loads(key)

    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        email = request.session['email']
        encoded_email = encode_email(email)
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 0:
        raise Http404

    department = user['primary_department']

    set_user_time_off_requests_merge(data, company, email)  # email NOT encoded
    set_department_time_off_requests(data, company, department, email)  # merge=true might break it all??

    return HttpResponse('Schedule successfully updated.')


def get_user_list(request):
    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        encoded_email = encode_email(request.session['email'])
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)
    department = user['primary_department']

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    user_list = get_users(company, department)

    # convert user_list into a dict to be able to parse it into json
    user_dict = {}
    for user in user_list:
        email = user.pop('email')
        user_dict[email] = user

    return JsonResponse(user_dict)


def update_user_status(request):
    data = {}
    for key in request.POST.dict().keys():
        data = json.loads(key)

    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        email = request.session['email']
        encoded_email = encode_email(email)
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    user_email = data['email']
    new_status = data['status']
    set_user_status(company, user_email, new_status)

    response_dict = {
        'message': 'Status successfully updated.',
        'email': user_email,
        'status': new_status
    }
    return JsonResponse(response_dict)


def new_user_on_list(request):
    data = {}
    for key in request.POST.dict().keys():
        data = json.loads(key)

    try:
        company_id = request.session['company_id']
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING111')

    try:
        email = request.session['email']
        encoded_email = encode_email(email)
    except KeyError:
        raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING222')

    company = get_company_name_by_company_code(company_id)
    user = get_user(company, encoded_email)
    department = user['primary_department']

    account_type = user['account_type']
    if account_type != 1:
        raise Http404

    first_name = data['first']
    last_name = data['last']
    email = data['email']
    position = data['position']
    is_pt = data['isPt']

    new_user_dict = {
        'last_name': last_name,
        'first_name': first_name,
        'email': email,
        'position': position,
        'departments': [department],
        'is_pt': is_pt,
        'account_type': 0,
        'status': 'active'
    }

    user_ref = get_user_ref(org_names_filter(company), encode_email(email))
    if user_ref is None:
        email_info_dict = add_single_user(new_user_dict, company)
        email_single_user(email_info_dict, company_id)
        data['message'] = 'New employee successfully added.'
        data['success'] = True
    else:
        data['success'] = False
        data['message'] = 'An employee with that email address already exists.'

    return JsonResponse(data)


# DEMO
def demo_get_saved_shifts(request):
    saved_shifts = get_demo_saved_shifts()

    return JsonResponse(saved_shifts)


def demo_get_user_list(request):
    user_list = get_demo_user_list()

    return JsonResponse(user_list)


def demo_single_schedule(request):
    schedule = get_demo_single_schedule()

    return JsonResponse(schedule)
