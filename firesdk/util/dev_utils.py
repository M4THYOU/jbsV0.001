from firesdk.firebase_functions.basefirebase import *
from firesdk.user_classes.users import XLSUser
from .utils import user_to_dict, org_names_filter, encode_email
from firesdk.firebase_functions.firebaseconn import add_user, set_availability, get_demo_schedules_ref, get_demo_user_list

from firesdk.models import MetricEvent

import csv
from random import randint


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

    user_dict = user_to_dict(position, departments, email, first_name, last_name, is_pt, account_type, 'active')
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


def generate_demo_data():
    demo_schedules = get_demo_schedules_ref()

    date_keys = [
        '29/12/2019', '30/12/2019', '31/12/2019', '01/01/2020', '02/01/2020', '03/01/2020', '04/01/2020', '05/01/2020',
        '06/01/2020', '07/01/2020', '08/01/2020', '09/01/2020', '10/01/2020', '11/01/2020', '12/01/2020', '13/01/2020',
        '14/01/2020', '15/01/2020', '16/01/2020', '17/01/2020', '18/01/2020', '19/01/2020', '20/01/2020', '21/01/2020',
        '22/01/2020', '23/01/2020', '24/01/2020', '25/01/2020', '26/01/2020', '27/01/2020', '28/01/2020', '29/01/2020',
        '30/01/2020', '31/01/2020', '01/02/2020', '02/02/2020', '03/02/2020', '04/02/2020', '05/02/2020', '06/02/2020',
        '07/02/2020', '08/02/2020'
    ]

    user_list = get_demo_user_list()
    email_list = list(user_list['email_name_key'])
    positions = ['Developer', 'Cashier', 'Sales Rep', 'Cook', 'Waiter', 'Janitor', 'Window Cleaner', 'Baker']
    shift_times = ['9:00 am - 5:00 pm', '9:00 am - 1:00 pm', '1:00 pm - 5:00 pm', '4:00 pm - 8:00 pm']

    actual_schedules = {}
    for key in demo_schedules.keys():
        demo_schedule = {'exactTimes': {}, 'positions': {}}
        for date_string in date_keys:
            demo_schedule['exactTimes'][date_string] = {}
            demo_schedule['positions'][date_string] = {}

            # 1-3 users per day
            for _ in range(0, randint(1, 4)):
                email = email_list[randint(0, len(email_list) - 1)]
                position = positions[randint(0, len(positions) - 1)]
                time = shift_times[randint(0, len(shift_times) - 1)]

                demo_schedule['exactTimes'][date_string][email] = time
                demo_schedule['positions'][date_string][email] = position

        actual_schedules[key] = demo_schedule

    demo_schedules['a'].set(actual_schedules['a'])
    demo_schedules['b'].set(actual_schedules['b'])
    demo_schedules['c'].set(actual_schedules['c'])
