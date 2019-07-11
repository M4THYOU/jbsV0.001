from firesdk.firebase_functions.basefirebase import *
from firesdk.user_classes.users import XLSUser
from .utils import user_to_dict, org_names_filter, encode_email
from firesdk.firebase_functions.firebaseconn import add_user, set_availability

from firesdk.models import MetricEvent

import csv


def delete_all_users():
    pass
    # disable this so nobody can use it, for now.
    # for user in auth.list_users().iterate_all():
        # auth.delete_user(user.uid)


def add_known_user(account_type_int):
    last_name = 'lastNameTEST'
    first_name = 'firstNameTEST'
    email = 'test@gmail.com'
    position = 'Store Standards Associate'
    departments = ['Store Standards']
    is_pt = True
    account_type = account_type_int

    user = XLSUser(last_name, first_name, email, position, departments, is_pt, account_type)

    password = 'password'
    auth.create_user(
        email=user.get_email(),
        password=password,
        display_name=user.get_full_name()
    )

    user_dict = user_to_dict(position, departments, email, first_name, last_name, is_pt, account_type)
    add_user(user_dict, org_names_filter('Walmart'))


def create_known_data_set():
    user_dict = create_known_users()  # dict of XLSUsers
    set_user_availability(user_dict)


def create_known_users():
    # 6 users: 1 manager, 1 ft, 4 pt
    position = 'Store Standards Associate'

    val = XLSUser('Duncescu', 'Val', 'val@gmail.com', position, ['Store Standards'], False, 1)  # manager
    aaron = XLSUser('Last', 'Aaron', 'aaron@gmail.com', position, ['Store Standards'], False, 0)  # ft
    shaq = XLSUser('Last', 'Shaq', 'shaq@gmail.com', position, ['Store Standards'], True, 0)
    sun = XLSUser('Last', 'Sun', 'sun@gmail.com', position, ['Store Standards'], True, 0)
    thuvar = XLSUser('Last', 'Thuvar', 'thuvar@gmail.com', position, ['Store Standards'], True, 0)
    matthew = XLSUser('Wolfe', 'Matthew', 'mathyou.wolfe@gmail.com', position, ['Store Standards'], True, 0)

    user_list = [val, aaron, shaq, sun, thuvar, matthew]

    password = 'password'
    for user in user_list:
        auth.create_user(
            email=user.get_email(),
            password=password,
            display_name=user.get_full_name()
        )

        user_dict = user_to_dict(user.get_position(), user.get_departments(), user.get_email(), user.get_first_name(),
                                 user.get_last_name(), user.get_is_pt(), user.get_account_type())
        add_user(user_dict, org_names_filter('Walmart'))

    user_dict = {'manager': val, 'ft': aaron, 'pt1': shaq, 'pt2': sun, 'pt3': thuvar, 'pt4': matthew, }
    return user_dict


def set_user_availability(user_dict):
    ft = user_dict['ft']
    pt1 = user_dict['pt1']
    pt2 = user_dict['pt2']
    pt3 = user_dict['pt3']
    pt4 = user_dict['pt4']

    ft_availability = {
        'hours': {
            'min': 35,
            'max': 40
        },

        'shifts': {
            'min': 5,
            'max': 6
        },

        'sunday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'monday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'tuesday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'wednesday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'thursday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'friday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'saturday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        }
    }

    pt123_availability = {
        'hours': {
            'min': 15,
            'max': 25
        },

        'shifts': {
            'min': 1,
            'max': 4
        },

        'sunday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'monday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'tuesday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'wednesday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'thursday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'friday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'saturday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        }
    }

    pt4_availability = {
        'hours': {
            'min': 15,
            'max': 25
        },

        'shifts': {
            'min': 1,
            'max': 4
        },

        'sunday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        },

        'monday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'tuesday': {
            'is_open': False,
            'is_unavailable': True,
            'start': 0,
            'end': 0
        },

        'wednesday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'thursday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'friday': {
            'is_open': False,
            'is_unavailable': False,
            'start': 16,
            'end': 23
        },

        'saturday': {
            'is_open': True,
            'is_unavailable': False,
            'start': 0,
            'end': 0
        }
    }

    set_availability(ft_availability, org_names_filter('Walmart'), encode_email(ft.get_email()))
    set_availability(pt123_availability, org_names_filter('Walmart'), encode_email(pt1.get_email()))
    set_availability(pt123_availability, org_names_filter('Walmart'), encode_email(pt2.get_email()))
    set_availability(pt123_availability, org_names_filter('Walmart'), encode_email(pt3.get_email()))
    set_availability(pt4_availability, org_names_filter('Walmart'), encode_email(pt4.get_email()))


def metrics_to_csv():
    all_events = MetricEvent.objects.all()

    with open('jbs-metrics.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        headers = ['Email', 'Company', 'Department', 'Account Type', 'Date', 'Time', 'Timezone', 'Event Type',
                   'Session Id', 'Other Data']
        writer.writerow(headers)

        for event in all_events:
            email = event.email
            company = event.company
            department = event.department
            account_type = event.account_type
            date = event.date
            time = event.time
            timezone_abbreviation = event.timezone_abbreviation
            event_type = event.event_type
            session_id = event.session_id
            data = event.data

            row = [email, company, department, account_type, date, time, timezone_abbreviation, event_type, session_id,
                   data]

            writer.writerow(row)

