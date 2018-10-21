from enum import Enum


class Day(Enum):
    sunday = 'sunday'
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'

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
