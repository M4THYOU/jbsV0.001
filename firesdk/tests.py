import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "firebase_testing.settings")
application = get_wsgi_application()

"""
json_path = '/Users/matthewwolfe/Documents/JBS/test_data/Schedule JSON/'
csv_path = '/Users/matthewwolfe/Documents/JBS/test_data/'

from ml_scheduler.create_data.shift_predictor.schedule_data import *

json_schedules_to_csv_by_date(json_path, csv_path)

json_schedules_to_csv_by_shift(json_path, csv_path)

# start_end_int_to_12_hr_time(7, 15)  # 7:00 am - 4:00 pm
# start_end_int_to_12_hr_time(0, 11)  # 12:00 am - 12:00 pm (Midnight to Noon)
# start_end_int_to_12_hr_time(13, 16)  # 1:00 pm - 5:00 pm
# start_end_int_to_12_hr_time(18, 23)  # 6:00 pm - 12:00 am

########################################################################################################################

# from onboarding.onboard import create_new_client

# sample_company_location = '/Users/matthewwolfe/Documents/JBS/onboarding_process/sample_company.csv'
# create_new_client(sample_company_location)

########################################################################################################################

# from ml_scheduler.create_data.experimental import * XXX Moved into ml_scheduler.create_data.all_needs

# json_path = '/Users/matthewwolfe/Documents/JBS/test_data/Schedule JSON/'
# compare_needs_methods(json_path)

########################################################################################################################

# from ml_scheduler.create_data.shifts_per_day import *

# csv_path = '/Users/matthewwolfe/Documents/JBS/test_data/schedule_by_shift.csv'
# json_dir_path = '/Users/matthewwolfe/Documents/JBS/test_data/Schedule JSON/'
# create_shift_ratios(csv_path, json_dir_path)

########################################################################################################################

# from ml_scheduler.create_data.create_data import *

# data = get_shift_data(csv_path + 'schedule_by_shift.csv', json_path, 'Sobeys', 'Deli', needs_type='manual')

# if data is not None:
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#         print(data)
#     print(data)

########################################################################################################################

# from ml_scheduler.ml_pipeline.shift_predictor import predict_week_shifts

# predict_week_shifts(csv_path + 'schedule_by_shift.csv', json_path, 'Sobeys', 'Deli', needs_type='manual',
#                     remove_ratios=False, remove_needs=False)

########################################################################################################################

from ml_scheduler.create_data.user_predictor.all_avail import test

test('Sobeys', 'Deli')
"""

from firesdk.util.dev_utils import generate_demo_data
generate_demo_data()
