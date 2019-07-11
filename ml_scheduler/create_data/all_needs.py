import matplotlib.pyplot as plt
import os
import json
import math
from statistics import median

from firesdk.firebase_functions.firebaseconn import get_needs


def needs_from_past_schedules(path_to_schedules):
    """
    :param path_to_schedules: String path to directory containing the JSON schedule files.
    :return: A tuple of needs based on the average AND median of each day/hour.
    """
    json_schedules = os.listdir(path_to_schedules)

    raw_needs_dict = {
        'sunday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'monday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'tuesday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'wednesday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'thursday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'friday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
        'saturday': [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    }

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

            # add counts to raw_needs_dict
            day_names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            for day_name in day_names:
                for index, user_list in schedule_data[day_name].items():
                    raw_needs_dict[day_name][int(index)].append(len(user_list))

    avg_processed_needs_dict = {
        'sunday': [],
        'monday': [],
        'tuesday': [],
        'wednesday': [],
        'thursday': [],
        'friday': [],
        'saturday': []
    }

    med_processed_needs_dict = {
        'sunday': [],
        'monday': [],
        'tuesday': [],
        'wednesday': [],
        'thursday': [],
        'friday': [],
        'saturday': []
    }

    for day_name, user_list in raw_needs_dict.items():
        for hours_list in user_list:
            average_needs = sum(hours_list) / len(hours_list)

            if (float(average_needs) % 1) >= 0.5:
                rounded_average_needs = math.ceil(average_needs)
            else:
                rounded_average_needs = round(average_needs)

            median_needs = median(hours_list)

            avg_processed_needs_dict[day_name].append(rounded_average_needs)
            med_processed_needs_dict[day_name].append(median_needs)

    return avg_processed_needs_dict, med_processed_needs_dict


def get_needs_methods(path_to_schedules):
    """
    :param path_to_schedules: String path to directory containing the JSON schedule files.
    :return: Tuple. (manual_needs, auto_avg_needs, auto_median_needs)
    """
    manual_needs = get_needs('sobeys', 'deli')
    auto_avg_needs, auto_median_needs = needs_from_past_schedules(path_to_schedules)

    return manual_needs, auto_avg_needs, auto_median_needs


def compare_needs_methods(path_to_schedules):
    """
    Compares the department needs from various sources on a graph for each day of the week: Manually inputted needs,
    needs generated from past schedules averaged, and needs generated from past schedules as a median.
    """
    manual_needs, auto_avg_needs, auto_median_needs = get_needs_methods(path_to_schedules)
    manual_day_needs = manual_needs['needs']

    plt.style.use('seaborn-whitegrid')
    x_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

    n_rows = 3
    n_cols = 3

    fig = plt.figure(figsize=(18, 10))

    ax = fig.add_subplot(n_rows, n_cols, 1)
    ax.plot(x_values, manual_day_needs['sunday'], label='Manual')
    ax.plot(x_values, auto_avg_needs['sunday'], label='Avg')
    ax.plot(x_values, auto_median_needs['sunday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Sunday')
    plt.legend()

    ax2 = fig.add_subplot(n_rows, n_cols, 2, sharey=ax)
    ax2.plot(x_values, manual_day_needs['monday'], label='Manual')
    ax2.plot(x_values, auto_avg_needs['monday'], label='Avg')
    ax2.plot(x_values, auto_median_needs['monday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Monday')
    plt.legend()

    ax3 = fig.add_subplot(n_rows, n_cols, 3, sharey=ax)
    ax3.plot(x_values, manual_day_needs['tuesday'], label='Manual')
    ax3.plot(x_values, auto_avg_needs['tuesday'], label='Avg')
    ax3.plot(x_values, auto_median_needs['tuesday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Tuesday')
    plt.legend()

    ax4 = fig.add_subplot(n_rows, n_cols, 4, sharey=ax)
    ax4.plot(x_values, manual_day_needs['wednesday'], label='Manual')
    ax4.plot(x_values, auto_avg_needs['wednesday'], label='Avg')
    ax4.plot(x_values, auto_median_needs['wednesday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Wednesday')
    plt.legend()

    ax5 = fig.add_subplot(n_rows, n_cols, 5, sharey=ax)
    ax5.plot(x_values, manual_day_needs['thursday'], label='Manual')
    ax5.plot(x_values, auto_avg_needs['thursday'], label='Avg')
    ax5.plot(x_values, auto_median_needs['thursday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Thursday')
    plt.legend()

    ax6 = fig.add_subplot(n_rows, n_cols, 6, sharey=ax)
    ax6.plot(x_values, manual_day_needs['friday'], label='Manual')
    ax6.plot(x_values, auto_avg_needs['friday'], label='Avg')
    ax6.plot(x_values, auto_median_needs['friday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Friday')
    plt.legend()

    ax7 = fig.add_subplot(n_rows, n_cols, 7, sharey=ax)
    ax7.plot(x_values, manual_day_needs['saturday'], label='Manual')
    ax7.plot(x_values, auto_avg_needs['saturday'], label='Avg')
    ax7.plot(x_values, auto_median_needs['saturday'], label='Median')
    plt.xticks(range(len(x_values)), x_values)
    plt.title('Saturday')
    plt.legend()

    plt.show()
