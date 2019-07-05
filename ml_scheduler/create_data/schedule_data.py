import os
import json
import csv

from itertools import groupby
from operator import itemgetter

# path_to_schedules = '/Users/matthewwolfe/Documents/JBS/test_data/Schedule JSON/'
# destination_path = '/Users/matthewwolfe/Documents/JBS/test_data/'

def json_schedules_to_csv_by_date(path_to_schedules, destination_path):
    json_schedules = os.listdir(path_to_schedules)

    # create the schedule csv
    csv_path = destination_path + 'schedule_by_date.csv'
    with open(csv_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        # headers for csv
        writer.writerow([
            'number_of_users', 'company', 'department', 'start_date', 'end_date',

            'sunday_0', 'sunday_1', 'sunday_2', 'sunday_3', 'sunday_4', 'sunday_5', 'sunday_6', 'sunday_7', 'sunday_8',
            'sunday_9', 'sunday_10', 'sunday_11', 'sunday_12', 'sunday_13', 'sunday_14', 'sunday_15', 'sunday_16',
            'sunday_17', 'sunday_18', 'sunday_19', 'sunday_20', 'sunday_21', 'sunday_22', 'sunday_23',

            'monday_0', 'monday_1', 'monday_2', 'monday_3', 'monday_4', 'monday_5', 'monday_6', 'monday_7', 'monday_8',
            'monday_9', 'monday_10', 'monday_11', 'monday_12', 'monday_13', 'monday_14', 'monday_15', 'monday_16',
            'monday_17', 'monday_18', 'monday_19', 'monday_20', 'monday_21', 'monday_22', 'monday_23',

            'tuesday_0', 'tuesday_1', 'tuesday_2', 'tuesday_3', 'tuesday_4', 'tuesday_5', 'tuesday_6', 'tuesday_7',
            'tuesday_8', 'tuesday_9', 'tuesday_10', 'tuesday_11', 'tuesday_12', 'tuesday_13', 'tuesday_14',
            'tuesday_15', 'tuesday_16','tuesday_17', 'tuesday_18', 'tuesday_19', 'tuesday_20', 'tuesday_21',
            'tuesday_22', 'tuesday_23',

            'wednesday_0', 'wednesday_1', 'wednesday_2', 'wednesday_3', 'wednesday_4', 'wednesday_5', 'wednesday_6',
            'wednesday_7', 'wednesday_8', 'wednesday_9', 'wednesday_10', 'wednesday_11', 'wednesday_12', 'wednesday_13',
            'wednesday_14', 'wednesday_15', 'wednesday_16', 'wednesday_17', 'wednesday_18', 'wednesday_19',
            'wednesday_20', 'wednesday_21', 'wednesday_22', 'wednesday_23',

            'thursday_0', 'thursday_1', 'thursday_2', 'thursday_3', 'thursday_4', 'thursday_5', 'thursday_6',
            'thursday_7', 'thursday_8', 'thursday_9', 'thursday_10', 'thursday_11', 'thursday_12', 'thursday_13',
            'thursday_14', 'thursday_15', 'thursday_16', 'thursday_17', 'thursday_18', 'thursday_19', 'thursday_20',
            'thursday_21', 'thursday_22', 'thursday_23',

            'friday_0', 'friday_1', 'friday_2', 'friday_3', 'friday_4', 'friday_5', 'friday_6', 'friday_7', 'friday_8',
            'friday_9', 'friday_10', 'friday_11', 'friday_12', 'friday_13', 'friday_14', 'friday_15', 'friday_16',
            'friday_17', 'friday_18', 'friday_19', 'friday_20', 'friday_21', 'friday_22', 'friday_23',

            'saturday_0', 'saturday_1', 'saturday_2', 'saturday_3', 'saturday_4', 'saturday_5', 'saturday_6',
            'saturday_7', 'saturday_8', 'saturday_9', 'saturday_10', 'saturday_11', 'saturday_12', 'saturday_13',
            'saturday_14', 'saturday_15', 'saturday_16', 'saturday_17', 'saturday_18', 'saturday_19', 'saturday_20',
            'saturday_21', 'saturday_22', 'saturday_23',
        ])

        # loop over every json file in given directory
        for schedule in json_schedules:
            schedule_path = path_to_schedules + schedule

            if not schedule.endswith('.json'):
                continue

            # open json file and parse data into dict
            with open(schedule_path) as json_file:
                try:
                    schedule_data = json.load(json_file)
                except json.decoder.JSONDecodeError:
                    print('Error parsing:', schedule)
                    continue

                print(schedule_data)

                writer.writerow([
                    schedule_data['numberOfUsers'], schedule_data['company'], schedule_data['department'],
                    schedule_data['startDate'], schedule_data['endDate'],

                    ','.join(schedule_data['sunday']['0']), ','.join(schedule_data['sunday']['1']),
                    ','.join(schedule_data['sunday']['2']), ','.join(schedule_data['sunday']['3']),
                    ','.join(schedule_data['sunday']['4']), ','.join(schedule_data['sunday']['5']),
                    ','.join(schedule_data['sunday']['6']), ','.join(schedule_data['sunday']['7']),
                    ','.join(schedule_data['sunday']['8']), ','.join(schedule_data['sunday']['9']),
                    ','.join(schedule_data['sunday']['10']), ','.join(schedule_data['sunday']['11']),
                    ','.join(schedule_data['sunday']['12']), ','.join(schedule_data['sunday']['13']),
                    ','.join(schedule_data['sunday']['14']), ','.join(schedule_data['sunday']['15']),
                    ','.join(schedule_data['sunday']['16']), ','.join(schedule_data['sunday']['17']),
                    ','.join(schedule_data['sunday']['18']), ','.join(schedule_data['sunday']['19']),
                    ','.join(schedule_data['sunday']['20']), ','.join(schedule_data['sunday']['21']),
                    ','.join(schedule_data['sunday']['22']), ','.join(schedule_data['sunday']['23']),

                    ','.join(schedule_data['monday']['0']), ','.join(schedule_data['monday']['1']),
                    ','.join(schedule_data['monday']['2']), ','.join(schedule_data['monday']['3']),
                    ','.join(schedule_data['monday']['4']), ','.join(schedule_data['monday']['5']),
                    ','.join(schedule_data['monday']['6']), ','.join(schedule_data['monday']['7']),
                    ','.join(schedule_data['monday']['8']), ','.join(schedule_data['monday']['9']),
                    ','.join(schedule_data['monday']['10']), ','.join(schedule_data['monday']['11']),
                    ','.join(schedule_data['monday']['12']), ','.join(schedule_data['monday']['13']),
                    ','.join(schedule_data['monday']['14']), ','.join(schedule_data['monday']['15']),
                    ','.join(schedule_data['monday']['16']), ','.join(schedule_data['monday']['17']),
                    ','.join(schedule_data['monday']['18']), ','.join(schedule_data['monday']['19']),
                    ','.join(schedule_data['monday']['20']), ','.join(schedule_data['monday']['21']),
                    ','.join(schedule_data['monday']['22']), ','.join(schedule_data['monday']['23']),

                    ','.join(schedule_data['tuesday']['0']), ','.join(schedule_data['tuesday']['1']),
                    ','.join(schedule_data['tuesday']['2']), ','.join(schedule_data['tuesday']['3']),
                    ','.join(schedule_data['tuesday']['4']), ','.join(schedule_data['tuesday']['5']),
                    ','.join(schedule_data['tuesday']['6']), ','.join(schedule_data['tuesday']['7']),
                    ','.join(schedule_data['tuesday']['8']), ','.join(schedule_data['tuesday']['9']),
                    ','.join(schedule_data['tuesday']['10']), ','.join(schedule_data['tuesday']['11']),
                    ','.join(schedule_data['tuesday']['12']), ','.join(schedule_data['tuesday']['13']),
                    ','.join(schedule_data['tuesday']['14']), ','.join(schedule_data['tuesday']['15']),
                    ','.join(schedule_data['tuesday']['16']), ','.join(schedule_data['tuesday']['17']),
                    ','.join(schedule_data['tuesday']['18']), ','.join(schedule_data['tuesday']['19']),
                    ','.join(schedule_data['tuesday']['20']), ','.join(schedule_data['tuesday']['21']),
                    ','.join(schedule_data['tuesday']['22']), ','.join(schedule_data['tuesday']['23']),

                    ','.join(schedule_data['wednesday']['0']), ','.join(schedule_data['wednesday']['1']),
                    ','.join(schedule_data['wednesday']['2']), ','.join(schedule_data['wednesday']['3']),
                    ','.join(schedule_data['wednesday']['4']), ','.join(schedule_data['wednesday']['5']),
                    ','.join(schedule_data['wednesday']['6']), ','.join(schedule_data['wednesday']['7']),
                    ','.join(schedule_data['wednesday']['8']), ','.join(schedule_data['wednesday']['9']),
                    ','.join(schedule_data['wednesday']['10']), ','.join(schedule_data['wednesday']['11']),
                    ','.join(schedule_data['wednesday']['12']), ','.join(schedule_data['wednesday']['13']),
                    ','.join(schedule_data['wednesday']['14']), ','.join(schedule_data['wednesday']['15']),
                    ','.join(schedule_data['wednesday']['16']), ','.join(schedule_data['wednesday']['17']),
                    ','.join(schedule_data['wednesday']['18']), ','.join(schedule_data['wednesday']['19']),
                    ','.join(schedule_data['wednesday']['20']), ','.join(schedule_data['wednesday']['21']),
                    ','.join(schedule_data['wednesday']['22']), ','.join(schedule_data['wednesday']['23']),

                    ','.join(schedule_data['thursday']['0']), ','.join(schedule_data['thursday']['1']),
                    ','.join(schedule_data['thursday']['2']), ','.join(schedule_data['thursday']['3']),
                    ','.join(schedule_data['thursday']['4']), ','.join(schedule_data['thursday']['5']),
                    ','.join(schedule_data['thursday']['6']), ','.join(schedule_data['thursday']['7']),
                    ','.join(schedule_data['thursday']['8']), ','.join(schedule_data['thursday']['9']),
                    ','.join(schedule_data['thursday']['10']), ','.join(schedule_data['thursday']['11']),
                    ','.join(schedule_data['thursday']['12']), ','.join(schedule_data['thursday']['13']),
                    ','.join(schedule_data['thursday']['14']), ','.join(schedule_data['thursday']['15']),
                    ','.join(schedule_data['thursday']['16']), ','.join(schedule_data['thursday']['17']),
                    ','.join(schedule_data['thursday']['18']), ','.join(schedule_data['thursday']['19']),
                    ','.join(schedule_data['thursday']['20']), ','.join(schedule_data['thursday']['21']),
                    ','.join(schedule_data['thursday']['22']), ','.join(schedule_data['thursday']['23']),

                    ','.join(schedule_data['friday']['0']), ','.join(schedule_data['friday']['1']),
                    ','.join(schedule_data['friday']['2']), ','.join(schedule_data['friday']['3']),
                    ','.join(schedule_data['friday']['4']), ','.join(schedule_data['friday']['5']),
                    ','.join(schedule_data['friday']['6']), ','.join(schedule_data['friday']['7']),
                    ','.join(schedule_data['friday']['8']), ','.join(schedule_data['friday']['9']),
                    ','.join(schedule_data['friday']['10']), ','.join(schedule_data['friday']['11']),
                    ','.join(schedule_data['friday']['12']), ','.join(schedule_data['friday']['13']),
                    ','.join(schedule_data['friday']['14']), ','.join(schedule_data['friday']['15']),
                    ','.join(schedule_data['friday']['16']), ','.join(schedule_data['friday']['17']),
                    ','.join(schedule_data['friday']['18']), ','.join(schedule_data['friday']['19']),
                    ','.join(schedule_data['friday']['20']), ','.join(schedule_data['friday']['21']),
                    ','.join(schedule_data['friday']['22']), ','.join(schedule_data['friday']['23']),

                    ','.join(schedule_data['saturday']['0']), ','.join(schedule_data['saturday']['1']),
                    ','.join(schedule_data['saturday']['2']), ','.join(schedule_data['saturday']['3']),
                    ','.join(schedule_data['saturday']['4']), ','.join(schedule_data['saturday']['5']),
                    ','.join(schedule_data['saturday']['6']), ','.join(schedule_data['saturday']['7']),
                    ','.join(schedule_data['saturday']['8']), ','.join(schedule_data['saturday']['9']),
                    ','.join(schedule_data['saturday']['10']), ','.join(schedule_data['saturday']['11']),
                    ','.join(schedule_data['saturday']['12']), ','.join(schedule_data['saturday']['13']),
                    ','.join(schedule_data['saturday']['14']), ','.join(schedule_data['saturday']['15']),
                    ','.join(schedule_data['saturday']['16']), ','.join(schedule_data['saturday']['17']),
                    ','.join(schedule_data['saturday']['18']), ','.join(schedule_data['saturday']['19']),
                    ','.join(schedule_data['saturday']['20']), ','.join(schedule_data['saturday']['21']),
                    ','.join(schedule_data['saturday']['22']), ','.join(schedule_data['saturday']['23']),
                ])


def json_schedules_to_csv_by_shift(path_to_schedules, destination_path):
    json_schedules = os.listdir(path_to_schedules)

    # create the schedule csv
    csv_path = destination_path + 'schedule_by_shift.csv'
    with open(csv_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        # headers for csv
        writer.writerow([
            'email',
            'day_of_week',
            '24_hr_time',
            '12_hr_time'
        ])

        # loop over every json file in given directory
        for schedule in json_schedules:
            schedule_path = path_to_schedules + schedule

            if not schedule.endswith('.json'):
                continue

            # open json file and parse data into dict
            with open(schedule_path) as json_file:
                try:
                    schedule_data = json.load(json_file)
                except json.decoder.JSONDecodeError:
                    print('Error parsing:', schedule)
                    continue

                # add users to a dict for their day of the week with the shift they work that day.
                # No shift, then they are not in the dict.
                user_working_indexes_dict = {
                    'sunday': {},
                    'monday': {},
                    'tuesday': {},
                    'wednesday': {},
                    'thursday': {},
                    'friday': {},
                    'saturday': {},
                }

                # sunday
                for hour_index, users in schedule_data['sunday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['sunday']:
                            user_working_indexes_dict['sunday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['sunday'][email].append(int(hour_index))
                    
                # monday        
                for hour_index, users in schedule_data['monday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['monday']:
                            user_working_indexes_dict['monday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['monday'][email].append(int(hour_index))
                            
                # tuesday      
                for hour_index, users in schedule_data['tuesday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['tuesday']:
                            user_working_indexes_dict['tuesday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['tuesday'][email].append(int(hour_index))
                            
                # wednesday      
                for hour_index, users in schedule_data['wednesday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['wednesday']:
                            user_working_indexes_dict['wednesday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['wednesday'][email].append(int(hour_index))
                            
                # thursday      
                for hour_index, users in schedule_data['thursday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['thursday']:
                            user_working_indexes_dict['thursday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['thursday'][email].append(int(hour_index))
                            
                # friday      
                for hour_index, users in schedule_data['friday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['friday']:
                            user_working_indexes_dict['friday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['friday'][email].append(int(hour_index))
                            
                # saturday      
                for hour_index, users in schedule_data['saturday'].items():
                    for email in users:
                        if email not in user_working_indexes_dict['saturday']:
                            user_working_indexes_dict['saturday'][email] = [int(hour_index)]
                        else:
                            user_working_indexes_dict['saturday'][email].append(int(hour_index))

                for day_of_week, shifts_dict in user_working_indexes_dict.items():
                    for email, hours_index_list in shifts_dict.items():
                        sorted_hours_index_list = shift_hours_sorter(hours_index_list)

                        start_int = sorted_hours_index_list[0]
                        end_int = sorted_hours_index_list[-1]

                        time_24_hr, time_12_hr = start_end_int_to_time(start_int, end_int)

                        writer.writerow([
                            email, day_of_week, time_24_hr, time_12_hr
                        ])


def start_end_int_to_24_hr_time(start_time_int, end_time_int):
    start_int = start_time_int
    end_int = end_time_int + 1

    start_string = str(start_int) + ':00'
    end_string = str(end_int) + ':00'

    if len(start_string) < 5:
        start_string = '0' + start_string

    if len(end_string) < 5:
        end_string = '0' + end_string

    time_24_hr = start_string + ' - ' + end_string

    return time_24_hr


def start_end_int_to_12_hr_time(start_time_int, end_time_int):
    start_int = start_time_int
    end_int = end_time_int + 1

    # values must be from 0-23, continuously. The value after 23 is zero.
    if end_int > 23:
        end_int = 0

    if start_int > 12:
        start_int = start_int - 12
        start_suffix = 'pm'
    elif start_int == 12:
        start_suffix = 'pm'
    elif start_int == 0:
        start_int = 12
        start_suffix = 'am'
    else:
        start_suffix = 'am'

    if end_int > 12:
        end_int = end_int - 12
        end_suffix = 'pm'
    elif end_int == 12:
        end_suffix = 'pm'
    elif end_int == 0:
        end_int = 12
        end_suffix = 'am'
    else:
        end_suffix = 'am'

    start_string = str(start_int) + ':00 ' + start_suffix
    end_string = str(end_int) + ':00 ' + end_suffix

    time_12_hr = start_string + ' - ' + end_string

    return time_12_hr


def start_end_int_to_time(start_time_int, end_time_int):
    """

    :param start_time_int: Int representing the start index of a shift.
    :param end_time_int: Int representing the end index of a shift
    :return: Tuple (24_hour_time_string, 12_hour_time_string)
    """
    time_24_hr = start_end_int_to_24_hr_time(start_time_int, end_time_int)
    time_12_hr = start_end_int_to_12_hr_time(start_time_int, end_time_int)
    return time_24_hr, time_12_hr


def shift_hours_sorter(shift_list):
    new_list = []
    for k, g in groupby(enumerate(shift_list), lambda x: x[0]-x[1]):
        group = (map(itemgetter(1), g))
        group = list(map(int, group))
        new_list.append(group)

    if len(new_list) == 2:
        first_element_max = max(new_list[0])
        second_element_max = max(new_list[1])

        if first_element_max < second_element_max:
            return new_list[1] + new_list[0]
        elif first_element_max > second_element_max:
            return new_list[0] + new_list[1]
        else:
            return shift_list

    else:
        return shift_list
