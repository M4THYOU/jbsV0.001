from ml_scheduler.ml_pipeline.shift_predictor import predict_week_shifts
from ml_scheduler.ml_pipeline.user_predictor import predict_week_users

from firesdk.util.utils import org_names_filter


def test(path_to_csv, path_to_json_dir, company, department, needs_type='avg', remove_ratios=False,
         remove_needs=False, classifier_id=None, include_manager=False):
    """

    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param needs_type: String. Specifies type of needs to use. 'manual', 'avg', or 'median'.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :param classifier_id: String. The classifier to use for training and prediction of the user predictor.
     'random_forest', 'k_neighbors', 'radius_neighbors' or None. If None, use a neural net from Tensorflow.
    :param include_manager: Bool. Whether or not to include the scheduling manager of the department in the schedule.
    :return:
    """
    company = org_names_filter(company)
    department = org_names_filter(department)

    shifts_predictions, shifts_shifts_key = predict_week_shifts(
        path_to_csv,
        path_to_json_dir,
        company,
        department,
        needs_type=needs_type,
        remove_ratios=remove_ratios,
        remove_needs=remove_needs
    )

    user_predictions, users, shifts_key = predict_week_users(
        path_to_csv,
        company,
        department,
        shifts_shifts_key,
        classifier_id=classifier_id
    )

    print(shifts_predictions)
    print(user_predictions)

    for a, b in zip(shifts_shifts_key, shifts_key):
        if a != b:
            raise ValueError('shifts_keys not aligned')

    for day_of_week, shift_pred in shifts_predictions.items():
        needed_shift_indexes = {}
        for index, shift in enumerate(shift_pred):
            if shift == 1:
                needed_shift_indexes[index] = ''

        # what if a user wins two in one day???
        for shift_index in needed_shift_indexes.keys():
            current_highest = 0
            for email, user_pred in user_predictions[day_of_week].items():
                if user_pred[0][shift_index] > current_highest:
                    current_highest = user_pred[0][shift_index]
                    needed_shift_indexes[shift_index] = email

        print(needed_shift_indexes)

    print(users[0])
