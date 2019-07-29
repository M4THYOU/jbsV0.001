from firesdk.firebase_functions.firebaseconn import get_full_avail_and_time_off
from firesdk.util.utils import org_names_filter

# Get the timeoff and availability of users to process after the neural net. For the cross reference stage.


def test(company, department):
    company = org_names_filter(company)
    department = org_names_filter(department)

    department_avails, department_time_offs = get_full_avail_and_time_off(company, department)

    print(department_avails)
    print(department_time_offs)  # time off might be none. If so, set all the ratios to zero.
