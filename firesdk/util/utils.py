from enum import Enum
from base64 import b64encode


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


def company_to_dict(name, departments):
    company_dict = {
        'name': name,
        'departments': []
    }

    for department in departments:
        company_dict['departments'].append(department)

    return company_dict


def user_to_dict(position, email, first_name, last_name, is_part_time):
    user_dict = {
        'email': email,
        'encoded_email': encode_email(email),
        'name': {
            'first': first_name,
            'last': last_name
        },
        'position': position,
        'is_part_time': is_part_time
    }

    return user_dict


def availability_to_dict(days):
    availability_dict = {}

    for day, day_name in zip(days, Day):
        availability_dict[day_name.value] = {
            'start': day['start'],
            'end': day['end']
        }

    return availability_dict


def needs_to_dict(days, shift_length):
    needs_dict = {
        'shiftLength': shift_length,
        'needs': {}
    }

    for day, day_name in zip(days, Day):
        needs_dict['needs'][day_name.value] = day

    return needs_dict


def org_names_filter(name):
    new_name = name.lower().replace(' ', '_')
    return new_name


def encode_email(email):
    return b64encode(bytes(email, 'utf-8')).decode('utf-8')
