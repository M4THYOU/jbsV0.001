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
    """

    :param shifts_count_for_day: Dict of number times a shift occurs on each day of the week. Day of week -> shift ->
    shift count.
    :param schedule_count: Number of schedules (weeks) the shifts_count_for_day was generated from.
    :return: Dict of shift ratios. Day of week -> shift -> shift ratio.
    """
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
    """
    Creates the shift ratios from the given schedules. Calculated as the number of occurrences of a shift
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :return: Dict. Structured as {'sunday': {'7:00 - 15:00': 0.234, ... }, ... } (day_of_week -> shift -> shift_ratio)
    """
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


def count_shifts_by_user(path_to_csv, shifts_key):
    """
    Get the 3 user shift counts needed to create the a/b ratios for the user predictor.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :return: Tuple with 3 dicts.
    """
    shifts_per_day_per_user = {  # [day_of_week][email][shift] = shift_count
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    shift_count_per_day_per_user = {  # [day_of_week][email] = total_shift_count (for that day)
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    count_of_each_shift_for_each_day = {  # [day_of_week][shift] = shift_count (for that day & shift)
        'sunday': dict.fromkeys(shifts_key, 0),
        'monday': dict.fromkeys(shifts_key, 0),
        'tuesday': dict.fromkeys(shifts_key, 0),
        'wednesday': dict.fromkeys(shifts_key, 0),
        'thursday': dict.fromkeys(shifts_key, 0),
        'friday': dict.fromkeys(shifts_key, 0),
        'saturday': dict.fromkeys(shifts_key, 0),
    }

    with open(path_to_csv, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')

        next(reader)  # skips header line of the csv.
        for row in reader:
            email = row[0]
            day_of_week = row[1]
            time_24_hr = row[2]
            # time_12_hr = row[3]
            # schedule_file = row[4]
            # schedule_start_date = row[5]
            # schedule_end_date = row[6]

            # add the shift to the appropriate user and day of week.
            actual_shift = time_24_hr
            if email in shifts_per_day_per_user[day_of_week]:

                if actual_shift in shifts_per_day_per_user[day_of_week][email]:
                    shifts_per_day_per_user[day_of_week][email][actual_shift] += 1
                else:
                    shifts_per_day_per_user[day_of_week][email][actual_shift] = 1

            else:
                shifts_per_day_per_user[day_of_week][email] = {actual_shift: 1}

            # increment the number of total shifts each user has for each day of the week
            if email in shift_count_per_day_per_user[day_of_week]:
                shift_count_per_day_per_user[day_of_week][email] += 1
            else:
                shift_count_per_day_per_user[day_of_week][email] = 1

            # increment the number of times this shift occurs on this day
            count_of_each_shift_for_each_day[day_of_week][actual_shift] += 1

    return shifts_per_day_per_user, shift_count_per_day_per_user, count_of_each_shift_for_each_day


def get_ratios(shifts_per_day_per_user, shift_count_per_day_per_user, count_of_each_shift_for_each_day, shifts_key):
    """
    :param shifts_per_day_per_user: Dict generated from count_shifts_by_user.
    :param shift_count_per_day_per_user: Dict generated from count_shifts_by_user.
    :param count_of_each_shift_for_each_day: Dict generated from count_shifts_by_user.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :return: Tuple of Dicts. Structured as {'sunday': {'x@gmail.com': [0.1, 0.56, ... ], ... }, ... } (day_of_week ->
     email -> ratio_list). Two dicts, same structure.
    """
    # Shifts user works at a day & time / all their other shifts
    ratio_a = {  # [day_of_week][email][ratio_list (same order as shifts_key)]
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }
    # Shifts user works at a day & time / all times that shift occurs on that day.
    ratio_b = {  # [day_of_week][email][shift_list]
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }

    # create dicts.
    all_users = {}
    for day_of_week, user_dict in shifts_per_day_per_user.items():
        for email, shifts_dict in user_dict.items():
            if email not in all_users:
                all_users[email] = True
            for shift in shifts_key:
                if shift not in shifts_dict:
                    current_ratio_a = 0
                    current_ratio_b = 0
                else:
                    current_ratio_a = shifts_dict[shift] / shift_count_per_day_per_user[day_of_week][email]
                    current_ratio_b = shifts_dict[shift] / count_of_each_shift_for_each_day[day_of_week][shift]

                if email in ratio_a[day_of_week]:
                    ratio_a[day_of_week][email].append(current_ratio_a)
                else:
                    ratio_a[day_of_week][email] = [current_ratio_a]

                if email in ratio_b[day_of_week]:
                    ratio_b[day_of_week][email].append(current_ratio_b)
                else:
                    ratio_b[day_of_week][email] = [current_ratio_b]

    # some users on not being put in every day of week, because they have no shifts those days.
    # this causes a KeyError later on when trying to find them in the ratios.
    # Solve: loop days of the week and see if the user is listed in it. If not, add them to ratio as empty list.
    for email in all_users.keys():
        for day_of_week in shift_count_per_day_per_user.keys():
            if email not in ratio_a[day_of_week]:
                ratio_a[day_of_week][email] = [0] * len(shifts_key)
            if email not in ratio_b[day_of_week]:
                ratio_b[day_of_week][email] = [0] * len(shifts_key)

    return ratio_a, ratio_b


def create_user_ratios(path_to_csv, shifts_key):
    """
    Creates the two ratios needed for training and prediction of the user predictor.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :return: Tuple of Dicts. Structured as {'sunday': {'x@gmail.com': [0.1, 0.56, ... ], ... }, ... } (day_of_week ->
     email -> ratio_list). Two dicts, same structure.
    """

    shifts_per_day_per_user, shift_count_per_day_per_user, count_of_each_shift_for_each_day = count_shifts_by_user(
        path_to_csv, shifts_key
    )

    ratio_a, ratio_b = get_ratios(shifts_per_day_per_user, shift_count_per_day_per_user,
                                  count_of_each_shift_for_each_day, shifts_key)

    return ratio_a, ratio_b

