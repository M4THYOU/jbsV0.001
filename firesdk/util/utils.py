from enum import Enum
from base64 import b64encode
import datetime


class Day(Enum):
    sunday = 'sunday'
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'


class AccountType(Enum):
    basic = 'basic'
    manager = 'manager'
    master = 'master'


"""
class AccountPermissionLevel(Enum):
    unauthenticated = 'unauthenticated'
    basic = 'basic'
    manager = 'manager'
    superuser = 'superuser'

    unset = 'unset'
"""


def company_to_dict(name, departments):
    company_dict = {
        'name': name,
        'departments': []
    }

    for department in departments:
        company_dict['departments'].append(department)

    return company_dict


def user_to_dict(position, departments, email, first_name, last_name, is_part_time, account_type):
    user_dict = {
        'email': email,
        'encoded_email': encode_email(email),
        'name': {
            'first': first_name,
            'last': last_name
        },
        'position': position,
        'departments': departments,
        'is_part_time': is_part_time,
        'account_type': account_type
    }

    return user_dict


def availability_to_dict(days, min_max_hours, min_max_shifts):
    availability_dict = {
        "hours": {
            "min": min_max_hours['min'],
            "max": min_max_hours['max']
        },

        "shifts": {
            "min": min_max_shifts['min'],
            "max": min_max_shifts['max']
        }
    }

    for day, day_name in zip(days, Day):
        availability_dict[day_name.value] = {
            'is_open': day['isOpen'],
            'is_unavailable': day['isUnavailable'],
            'start': day['start'],
            'end': day['end']
        }

    if day['isOpen'] and day['isUnavailable']:
        raise ValueError('User cannot have both open availability and be unavailable on a single day.')

    return availability_dict


def needs_to_dict(days, shift_length):
    needs_dict = {
        'shiftLength': shift_length,
        'needs': {}
    }

    for day, day_name in zip(days, Day):
        needs_dict['needs'][day_name.value] = day

    return needs_dict


def schedule_to_dict(days, exact_times, positions):
    schedule_dict = {
        'exactTimes': exact_times,
        'schedules': days,
        'positions': positions,
    }

    return schedule_dict


def department_list_to_dict(departments):
    new_departments = []
    for dept in departments:
        department_dict = dept.get().to_dict()
        new_departments.append(department_dict)

    return new_departments


def login_bools_to_dict(is_password_changed, is_onboard_complete):
    login_bools_dict = {
        'is_password_changed': is_password_changed,
        'is_onboard_complete': is_onboard_complete
    }

    return login_bools_dict


def time_off_days_to_dict(reasons_dict, statuses_dict):
    time_off_dict = {
        'reasons': reasons_dict,
        'statuses': {}
    }

    for day, status_dict in statuses_dict.items():
        time_off_dict['statuses'][day] = status_dict

        if not valid_time_off_request(status_dict):
            print('Invalid time off request:', status_dict)
            return {}

    return time_off_dict


def single_time_off_to_dict(date, reason, status_dict):
    time_off_dict = {
        'date': date,
        'reason': reason,
        'status': status_dict
    }

    return time_off_dict


def valid_time_off_request(status_dict):
    pending = status_dict['pending']
    approved = status_dict['approved']
    denied = status_dict['denied']
    expired = status_dict['expired']

    status_list = [pending, approved, denied, expired]
    if not any(status_list):
        return False

    return true_exclusive_or(pending, approved, denied, expired)


def org_names_filter(name):
    new_name = name.lower().replace(' ', '_')
    return new_name


def unfilter_org_names(filtered_name):
    new_name = filtered_name.replace('_', ' ').title()
    return new_name


def encode_email(email):
    return b64encode(bytes(email, 'utf-8')).decode('utf-8')


def str_int_to_bool(str_int):
    int_val = int(str_int)

    if int_val == 0:
        bool_val = False
    elif int_val == 1:
        bool_val = True
    else:
        raise ValueError('Illegal int_val:', int_val)

    return bool_val


# gets first occurrence of 'not 0' in the list
def first_not_zero_index(int_list):
    first_not_zero = None

    for item in int_list:
        if item != 0:
            first_not_zero = int_list.index(item)
            break

    return first_not_zero


# gets last occurrence of 'not 0' in the list
def last_not_zero_index(int_list):
    last_not_zero = None

    for item in int_list[::-1]:
        if item != 0:
            last_not_zero = len(int_list) - 1 - int_list[::-1].index(item)
            break

    return last_not_zero


def needs_to_open_hours(needs_dict):
    open_hours_dict = {
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    for day, hour_list in needs_dict['needs'].items():
        first_hour = first_not_zero_index(hour_list)
        last_hour = last_not_zero_index(hour_list)

        open_hours_dict[day]['first'] = first_hour
        open_hours_dict[day]['last'] = last_hour

    return open_hours_dict


def hour_int_to_time(hour_int):
    delta_time = datetime.timedelta(hours=hour_int)
    real_time = (datetime.datetime.min + delta_time).time()

    return real_time


def int_to_account_type(account_type_int):
    if account_type_int == 0:
        return AccountType.basic
    elif account_type_int == 1:
        return AccountType.manager
    elif account_type_int == 2:
        return AccountType.master


def date_string_to_object(date_string):
    return datetime.datetime.strptime(date_string, '%d/%m/%Y')


def true_exclusive_or(*args):
    return sum(bool(x) for x in args) == 1


def month_delta(date, delta):
    m, y = (date.month+delta) % 12, date.year + (date.month+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)


def full_time_off_dict_to_list(full_time_off_dict):
    time_off_list = []

    for user, user_time_off_dict in full_time_off_dict.items():
        for date_string, reason in user_time_off_dict['reasons'].items():
            status_dict = user_time_off_dict['statuses'][date_string]

            status = 'pending'
            if status_dict['pending']:
                status = 'pending'
            elif status_dict['approved']:
                status = 'approved'
            elif status_dict['denied']:
                status = 'denied'
            elif status_dict['expired']:
                status = 'expired'

            time_off_list_item = {
                'email': user,
                'date': date_string,
                'reason': reason,
                'status': status,
            }

            time_off_list.append(time_off_list_item)

    return time_off_list


def standard_to_military_time(time_string):
    split_time = time_string.split(':')
    hour = int(split_time[0])

    split_minute_time_mode = split_time[1].split(' ')
    minute = split_minute_time_mode[0]
    time_mode = split_minute_time_mode[1]

    if time_mode == 'am':
        if hour == 12:
            new_hour = 0
        else:
            new_hour = hour
    elif time_mode == 'pm':
        if hour == 12:
            new_hour = hour
        else:
            new_hour = hour + 12
    else:
        return 'Invalid Time Mode: ' + time_mode

    military_time = '{}:{}'.format(new_hour, minute)

    return military_time


def military_to_standard_time(time_string):
    split_time = time_string.split(':')
    hour_int = int(split_time[0])
    minute_str = split_time[1]

    if hour_int == 0:
        new_hour = 12
        suffix = 'am'
    elif hour_int < 12:
        new_hour = hour_int
        suffix = 'am'
    elif hour_int == 12:
        new_hour = hour_int
        suffix = 'pm'
    else:
        new_hour = hour_int - 12
        suffix = 'pm'

    standard_time = '{}:{} {}'.format(new_hour, minute_str, suffix)

    return standard_time
