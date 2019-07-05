from django.test import TestCase

import functools

from ml_scheduler.create_data.schedule_data import *

json_path = '/Users/matthewwolfe/Documents/JBS/test_data/Schedule JSON/'
csv_path = '/Users/matthewwolfe/Documents/JBS/test_data/'
# json_schedules_to_csv_by_date(json_path, csv_path)

json_schedules_to_csv_by_shift(json_path, csv_path)

# start_end_int_to_12_hr_time(7, 15)  # 7:00 am - 4:00 pm
# start_end_int_to_12_hr_time(0, 11)  # 12:00 am - 12:00 pm (Midnight to Noon)
# start_end_int_to_12_hr_time(13, 16)  # 1:00 pm - 5:00 pm
# start_end_int_to_12_hr_time(18, 23)  # 6:00 pm - 12:00 am
