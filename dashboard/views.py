from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View

from .forms import LoginForm

from firesdk.firebase_functions.firebaseconn import *

from dashboard.custom.auth_utils import *

# Create your views here.


class BaseDashboardView(View):

    @staticmethod
    def get_base_dict(request):
        session = request.session

        name = session['first_name'] + ' ' + session['last_name']
        position = session['position']

        base_dict = {'name': name, 'position': position}
        return base_dict


class Login(View):
    login_form = LoginForm

    def get(self, request):
        if is_authenticated(request):
            return HttpResponseRedirect('/hive/')

        form = self.login_form()

        return render(request, 'dashboard/login.html', {'login_form': form})

    def post(self, request):
        form = self.login_form(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            token = cd['token']
            email = cd['email']
            company_id = cd['company_id']

            request.session['tk'] = token
            request.session['email'] = email
            request.session['company_id'] = company_id

            company_name = get_company_name_by_company_code(company_id)
            user = get_user(company_name, encode_email(email))

            first_name = user['name']['first']
            last_name = user['name']['last']
            position = user['position']
            account_type_int = user['account_type']

            print(user)

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

        print('logging out...')

        try:
            del request.session['tk']
        except KeyError:
            pass

        try:
            del request.session['email']
        except KeyError:
            pass

        try:
            del request.session['company_id']
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

        return render(request, 'dashboard/logout.html', {})


class Home(BaseDashboardView):

    def get(self, request):
        if not is_authenticated(request):
            return HttpResponseRedirect('/hive/login/')

        try:
            account_type_int = request.session['account_type']
        except KeyError:
            raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING')

        if account_type_int == 0:
            return render(request, 'dashboard/basic/index.html', self.get_base_dict(request))
        elif account_type_int == 1:
            return render(request, 'dashboard/manager/index.html', self.get_base_dict(request))
        else:
            raise ValueError('CHANGE THIS SHIT TO A 404 OR SOMETHING 222')


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
        set_availability()
