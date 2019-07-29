from ml_scheduler.create_data.shifts_per_day import create_shift_ratios, get_json_schedules, create_user_ratios
from ml_scheduler.create_data.shift_predictor.all_needs import get_needs_methods
from ml_scheduler.create_data.shift_predictor.schedule_data import shift_hours_sorter, start_end_int_to_24_hr_time
from firesdk.util.utils import org_names_filter

import pandas as pd
import json
from datetime import datetime, timedelta
import pytz


def custom_min_max_scaler(df, min_, max_, range_=(0, 1)):
    """
    Scales a dataframe's columns to values from 'range' (default (0, 1)) based on the min and max values.
    :param df: The dataframe to be scaled. Numeric inputs only.
    :param min_: Float. Smallest value in the DataFrame, scales to a 0 by default.
    :param max_: Float. Largest value in the DataFrame, scales to a 1 by default.
    :param range_: Tuple of numbers to scale the columns to. (0, 1) by default.
    :return: Scaled DataFrame
    """
    lowest_val, highest_val = range_
    df_std = (df - min_) / (max_ - min_)
    df_scaled = df_std * (highest_val - lowest_val) + lowest_val
    return df_scaled


def needs_for_schedule(schedule_data, sorted_needs, default_need):
    """
    Get needs of each schedule. Store it in needs_to_use and then stop looping.
    :param schedule_data: Dict parsed from the json representation of a schedule.
    :param sorted_needs: List of needs dicts, sorted by last_used (a date), from oldest to most recent.
    :param default_need: The last item in the original needs list if no better need is found.
    :return: Dict of the needs which fits the current schedule the best.
    """
    schedule_end_date_string = schedule_data['endDate']
    schedule_end_date = datetime.strptime(schedule_end_date_string, '%d/%m/%Y')
    schedule_end_date = schedule_end_date.replace(tzinfo=pytz.UTC)

    needs_to_use = default_need
    for need in sorted_needs:
        if schedule_end_date < need['last_used']:
            needs_to_use = need
            break

    return needs_to_use


def sparse_vector_from_schedule_day(schedule_data, day_name, all_possible_shifts):
    """
    Creates a sparse vector of 1's and 0's to use as targets for the given day/row.
    :param schedule_data: Dict of a day of a schedule from the json_schedules.
    :param day_name: String of the day of the week, lowercase. Ex. 'sunday'.
    :param all_possible_shifts: List of strings for every possible shift to be had.
    :return: List of 0's and 1's.
    """
    shifts_list = get_shifts_from_day_dict(schedule_data[day_name])

    sparse_vector = []
    for shift in all_possible_shifts:
        if shift in shifts_list:
            sparse_vector.append(1)
        else:
            sparse_vector.append(0)

    return sparse_vector


def create_features_for_single_example(shift_ratios, needs, day_of_week, current_max_scale_value, all_possible_shifts):
    """
    Create the features for a single example.
    :param shift_ratios: Dict of shift ratios for each day of the week. Every day of the week contains the same shifts
    but independently calculated ratios. Ex. sunday 3-8 will probably have a different ratio than tuesday 3-8.
    :param needs: Dict of needs for each day of the week.
    :param day_of_week: String of the name of a day of the week, lowercase. ex. 'sunday'.
    :param current_max_scale_value: Float with the current highest value found in needs in a week. Recursive.
    :param all_possible_shifts: List of strings, one for each possible shift.
    :return: Tuple. (Dict of shift_ratios_chance. Dict of x_needs. current_max_scale_value)
    """
    # get shift ratios
    shift_ratios_chance = {}
    for shift in all_possible_shifts:
        column_label = shift + '_chance'
        shift_ratios_chance[column_label] = shift_ratios[day_of_week][shift]

    # get needs.
    x_needs = {}
    for index, need in enumerate(needs['needs'][day_of_week]):
        column_label = str(index) + '_need'
        float_need = float(need)

        x_needs[column_label] = float_need

        # is this the new max value?
        if float_need > current_max_scale_value:
            current_max_scale_value = float_need

    return shift_ratios_chance, x_needs, current_max_scale_value


def get_shifts_from_day_dict(day_dict):
    """
    Converts a day dict of form {'0': [], '1': [] ... '9': [chris@gmail.com] ... } into a list of shifts in that day.
    :param day_dict: A schedule instance's day of the
    :return: List of strings in the given 24 hour format: '15:00 - 20:00'
    """

    shifts_int_list_dict = {}
    for hour_index, worker_list in day_dict.items():
        for email in worker_list:
            if email not in shifts_int_list_dict:
                shifts_int_list_dict[email] = [int(hour_index)]
            else:
                shifts_int_list_dict[email].append(int(hour_index))

    shifts_list = []
    for email, hours_index_list in shifts_int_list_dict.items():
        sorted_hours_index_list = shift_hours_sorter(hours_index_list)

        start_int = sorted_hours_index_list[0]
        end_int = sorted_hours_index_list[-1]

        time_24_hr = start_end_int_to_24_hr_time(start_int, end_int)

        shifts_list.append(time_24_hr)

    return shifts_list


def features_targets_from_needs_list(needs, shift_ratios, json_schedules, path_to_json_dir):
    """
    Creates a DataFrame of every scheduled day to use as features and targets for the shift picker model.
    :param needs: List of needs dicts.
    :param shift_ratios: Dict of ratios for every possible shift, by day of week.
    :param json_schedules: List of strings which are the file names of JSON schedules stored in path_to_json_dir.
    :param path_to_json_dir: String of the file path to the directory containing all of the json_schedules.
    :return: Tuple of: Pandas DataFrame. Columns: day_of_week, shifts_targets, shifts_key, shiftX_chance ...
    shiftY_chance, 0_need ... 23_need. AND max_scale_value to be used when predicting the actual schedule.
    """
    # any day works for the key of shift_ratios, they all have the same keys.
    all_possible_shifts = list(shift_ratios['sunday'].keys())
    day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    # last item is always current needs which has no 'last_used'. Set it to far in the future for sorting.
    # this also ensures the current needs will always meet the requirement schedule_end_date < temp_needs_date
    # sort needs list by last_used(a date), from oldest to most recent.
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.UTC)
    needs[-1]['last_used'] = now + timedelta(weeks=700)
    sorted_needs = sorted(needs, key=lambda k: k['last_used'])  # from oldest to newest

    # recursive value, fed into create_features_for_single_example multiple times to find the max.
    max_scale_value = 0.0

    data = {'day_of_week': [], 'shifts_targets': [], 'shifts_key': []}
    for schedule in json_schedules:
        schedule_path = path_to_json_dir + schedule

        # open json file and parse data into dict
        with open(schedule_path) as json_file:
            try:
                schedule_data = json.load(json_file)
            except json.decoder.JSONDecodeError:
                print('Error parsing:', schedule)
                continue

            # Get the needs for each schedule.
            default_need = needs[-1]
            needs_to_use = needs_for_schedule(schedule_data, sorted_needs, default_need)

            for day_name in day_names:
                # create the targets
                sparse_vector = sparse_vector_from_schedule_day(schedule_data, day_name, all_possible_shifts)

                # create ratios and needs
                shift_ratios_chance, x_needs, current_max_scale_value = create_features_for_single_example(
                    shift_ratios, needs_to_use, day_name, max_scale_value, all_possible_shifts
                )
                max_scale_value = current_max_scale_value

                data['day_of_week'].append(day_name)
                data['shifts_targets'].append(sparse_vector)
                data['shifts_key'].append(all_possible_shifts)
                if list(shift_ratios_chance)[0] not in data:
                    for key, ratio in shift_ratios_chance.items():
                        data[key] = [ratio]
                else:
                    for key, ratio in shift_ratios_chance.items():
                        data[key].append(ratio)
                if list(x_needs)[0] not in data:
                    for key, need in x_needs.items():
                        data[key] = [need]
                else:
                    for key, need in x_needs.items():
                        data[key].append(need)

    data_df = pd.DataFrame(data)
    # scale the dataframes' needs to MinMaxScaler
    needs_columns = [
        '0_need', '1_need', '2_need', '3_need', '4_need', '5_need', '6_need',
        '7_need', '8_need', '9_need', '10_need', '11_need', '12_need', '13_need',
        '14_need', '15_need', '16_need', '17_need', '18_need', '19_need', '20_need',
        '21_need', '22_need', '23_need'
    ]
    data_df[needs_columns] = custom_min_max_scaler(data_df[needs_columns], 0.0, max_scale_value)

    return data_df, max_scale_value


def get_shift_data(path_to_csv, path_to_json_dir, company, department, needs_type='manual'):
    """
    Combines all data into a list of tuples (X_df, y_df).
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param needs_type: String. Specifies type of needs to use. 'manual', 'avg', or 'median'.
    :return: Tuple of (list of (features_df, labels_df), max_scale_value).
    """

    company = org_names_filter(company)
    department = org_names_filter(department)

    shift_ratios = create_shift_ratios(path_to_csv, path_to_json_dir)  # this expensive function is called twice in the creation of shift predictor!
    manual_needs, auto_avg_needs, auto_median_needs = get_needs_methods(path_to_json_dir, company, department)

    print(shift_ratios)

    json_schedules = get_json_schedules(path_to_json_dir)

    if needs_type == 'manual':
        needs = manual_needs
    elif needs_type == 'avg':
        needs = auto_avg_needs
    elif needs_type == 'median':
        needs = auto_median_needs
    else:
        raise ValueError('Invalid needs_type: \'' + needs_type + '\'. Must be string \'manual\', \'avg\', or \'median\'.')

    data, max_scale_value = features_targets_from_needs_list(needs, shift_ratios, json_schedules, path_to_json_dir)

    return data, max_scale_value

# Shift Predictor
########################################################################################################################
# User Predictor


def get_user_data(path_to_csv, path_to_json_dir, company, department, shifts_key):
    company = org_names_filter(company)
    department = org_names_filter(department)

    create_user_ratios(path_to_csv, path_to_json_dir)
