import csv
import os
import matplotlib.pyplot as plt

"""
Create the ratios for both the shifts predictor and user predictor.
"""


def count_shifts_by_day_of_week(path_to_csv):
    """
    :param path_to_csv: Filepath to the csv file with list of shifts generated by the schedule JSON files.
    schedule_by_shift.csv
    :return: Dict of days of week, containing a dict of shifts for that day, containing
    """
    shifts_for_days = {
        # 'sunday': {'4:00 pm - 8:00 pm': 5} -> 4-8 shift occurs on 5 sundays.
        'sunday': {},  # using dicts not lists to prevent duplicates.
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    with open(path_to_csv, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')

        next(reader)  # skips header line of the csv.
        for row in reader:
            day_of_week = row[1]
            time_24_hr = row[2]
            time_12_hr = row[3]

            """ # Use this statement to catch any oddities you may notice
            if time_24_hr == '15:00 - 16:00':
                error_file = row[4]
                print(time_24_hr, time_12_hr, day_of_week, '********************************************', error_file)
            """

            # add the shift to every day of the week, starting at zero if not exists already.
            for day in shifts_for_days.keys():
                if time_24_hr not in shifts_for_days[day] and day == day_of_week:
                    shifts_for_days[day][time_24_hr] = 1
                elif time_24_hr not in shifts_for_days[day]:
                    shifts_for_days[day][time_24_hr] = 0
                elif day == day_of_week:
                    shifts_for_days[day][time_24_hr] += 1
                else:  # not a primary day, it already exists in the dict though. So don't add anything.
                    pass

    return shifts_for_days


def get_json_schedules(path_to_json_dir):
    json_schedules_raw = os.listdir(path_to_json_dir)
    json_schedules_filtered = []
    for schedule in json_schedules_raw:
        if schedule.endswith('.json'):
            json_schedules_filtered.append(schedule)

    return json_schedules_filtered


def get_shift_occurrence_ratio(shifts_count_for_day, schedule_count):
    shift_ratios_for_days = {
        # 'sunday': {'4:00 pm - 8:00 pm': 0.5} -> 4-8 shift occurs on 50% of sundays.
        'sunday': {},  # using dicts not lists to prevent duplicates.
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    for day_of_week, shifts_dict in shifts_count_for_day.items():
        for shift_string, shift_count in shifts_dict.items():
            shift_ratio = shift_count / schedule_count

            shift_ratios_for_days[day_of_week][shift_string] = shift_ratio

    return shift_ratios_for_days


def graph_shift_ratio_for_day(day_dict, title):
    """
    Plots the shift ratios for a single day.
    :param day_dict: Dict from get_shift_occurrence_ratio[title]
    :param title: Day of the week, all lowercase. Ex. 'sunday'.
    """
    y_scale = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    shifts = list(day_dict.keys())
    ratios = list(day_dict.values())

    plt.bar(shifts, ratios)
    plt.yticks(y_scale)
    plt.xticks(shifts, rotation=90)

    plt.title(title)
    plt.tight_layout()

    plt.show()


def graph_shift_ratio_for_week(shift_ratios):
    """
    Plots the shift ratios for each day of the week.
    :param day_dict: Dict from get_shift_occurrence_ratio(). Assumes keys are lower case days of the week.
    :param title: Day of the week, all lowercase. Ex. 'sunday'.
        """
    day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    plt.style.use('seaborn-whitegrid')
    y_scale = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    n_rows = 3
    n_cols = 3

    fig, ax = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(18, 10))
    day_name_index = 0
    for row in ax:
        for column in row:
            day_name = day_names[day_name_index]
            day_dict = shift_ratios[day_name]

            shifts = list(day_dict.keys())
            ratios = list(day_dict.values())

            column.bar(shifts, ratios)
            column.set_yticks(y_scale)
            column.set_xticks(range(len(shifts)))
            column.set_xticklabels(shifts, rotation=90)
            column.set_title(day_name.title())

            day_name_index += 1
            if day_name_index > 6:
                break

    fig.delaxes(ax[2][2])
    fig.delaxes(ax[2][1])
    plt.tight_layout()
    plt.show()


def create_shift_ratios(path_to_csv, path_to_json_dir):
    shifts_count_for_day = count_shifts_by_day_of_week(path_to_csv)

    # There may be some small bias in using this method. Does not account for days where the store is closed (Holidays).
    # consider counting only open days. More accurate but also more expensive.
    schedule_count = len(get_json_schedules(path_to_json_dir))

    shift_ratios = get_shift_occurrence_ratio(shifts_count_for_day, schedule_count)

    # graph_shift_ratio_for_day(shift_ratios['sunday'], 'sunday'.title())
    # graph_shift_ratio_for_week(shift_ratios)

    return shift_ratios

# Shift Predictor
########################################################################################################################
# User Predictor


def create_user_ratios(path_to_csv, path_to_json_dir):
    # first divide up shifts csv into a dict of shifts per user.

    shifts_per_day_per_user = {
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }
    shift_count_per_user = {}
    with open(path_to_csv, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')

        next(reader)  # skips header line of the csv.
        for row in reader:
            email = row[0]
            day_of_week = row[1]
            time_24_hr = row[2]
            time_12_hr = row[3]
            schedule_file = row[4]
            schedule_start_date = row[5]
            schedule_end_date = row[6]

            shift_item = {
                'time_24_hr': time_24_hr,
                'time_12_hr': time_12_hr,
                'schedule_file': schedule_file,
                'schedule_start_date': schedule_start_date,
                'schedule_end_date': schedule_end_date
            }

            need to check if the user is still active in the user list!!!

            # add the shift to the appropriate user and day of week.
            if email in shifts_per_day_per_user[day_of_week]:
                shifts_per_day_per_user[day_of_week][email].append(shift_item)
            else:
                shifts_per_day_per_user[day_of_week][email] = [shift_item]

            # increase the count of shifts

    print(shifts_per_day_per_user)
    for email, shift_list in shifts_per_day_per_user.items():
        print(email, shift_list)

    # loop over every shift each user has
