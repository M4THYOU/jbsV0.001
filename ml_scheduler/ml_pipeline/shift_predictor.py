from ml_scheduler.create_data.create_data import get_shift_data, create_shift_ratios, get_needs_methods, \
    create_features_for_single_example, custom_min_max_scaler
from firesdk.util.utils import military_to_standard_time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


class NumericColumnsRemover(BaseEstimator, TransformerMixin):
    def __init__(self, remove_ratios=False, remove_needs=False, ratios=[], needs=[]):
        self.remove_ratios = remove_ratios
        self.remove_needs = remove_needs

        self.ratios = ratios
        self.needs = needs

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if self.remove_ratios:
            X.drop(self.ratios, axis=1, inplace=True)
        if self.remove_needs:
            X.drop(self.needs, axis=1, inplace=True)

        return X


class DayOfWeekOneHotEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        print(X['day_of_week'])
        return X


def ratio_cleaner(data, min_ratio_value=1.0):
    """
    Remove ratios that do not meet a certain threshold. Also, remove these same targets from the outputs.
    :param data: Pandas DataFrame of all features and targets.
    :param min_ratio_value: The cutoff point for ratios to be removed from the data. The max, 7.0, removes all ratios.
    The min, 0.0 removes none. Recommended values to experiment with are 2.0, 1.5, and 1.0.
    :return: Pandas DataFrame, the processed data with cleaned ratios..
    """
    ratio_attribs = []
    for attrib in list(data):
        if attrib.endswith('_chance'):
            ratio_attribs.append(attrib)

    indices_to_remove = []
    for attrib in ratio_attribs:
        all_non_zero_ratios_for_shift = []
        all_ratios_for_shift = []
        for ratio in data[attrib]:
            all_ratios_for_shift.append(ratio)
            if ratio > 0:
                all_non_zero_ratios_for_shift.append(ratio)

        number_of_ratios = len(all_ratios_for_shift)
        number_of_non_zero_ratios = len(all_non_zero_ratios_for_shift)

        ratios_per_day_of_week = number_of_ratios / 7

        split_time = attrib.replace('_chance', '').split(' - ')
        military_start_time = split_time[0]
        military_end_time = split_time[1]

        non_zero_ratios_per_day_of_week = number_of_non_zero_ratios / ratios_per_day_of_week  # 0.0 - 7.0 (more clear)
        # scaled_non_zero_ratios_per_day_of_week = number_of_non_zero_ratios / number_of_ratios  # 0.0 - 1.0

        if non_zero_ratios_per_day_of_week < min_ratio_value:
            attrib_as_shift = attrib.replace('_chance', '')
            index_to_remove = data['shifts_key'].iloc[0].index(attrib_as_shift)
            indices_to_remove.append(index_to_remove)

            data.drop(attrib, axis=1, inplace=True)

    sorted_indices_to_remove = sorted(indices_to_remove, reverse=True)
    cleaned_shifts_key = data['shifts_key'].iloc[0]
    for index in sorted_indices_to_remove:
        cleaned_shifts_key.pop(index)

    # set every shifts_key row to the newly updated one.
    data['shifts_key'] = [cleaned_shifts_key] * len(data['shifts_key'])
    for index, row in data.iterrows():
        for removal_index in sorted_indices_to_remove:
            row['shifts_targets'].pop(removal_index)

    return data


def accuracy_per_shift(predictions, targets):
    """
    Gets the accuracy of the entire model. The sklearn built in accuracy function evaluates if the schedule for each day
     is correct or not. This one will instead calculate accuracy based on if each shift on each schedule is correct or
     not. This is a much more accurate test of accuracy, specific to this model.
    :param predictions: Numpy array. Predictions made by the classifier.
    :param targets: Numpy array. Targets for the supplied predictions. The proper labels.
    :return: Float value representing accuracy of the model.
    """
    examples_accuracies = []
    for pred, targ in zip(predictions, targets):

        correct_predictions_for_example = 0
        for shift_pred, shift_targ in zip(pred, targ):
            if shift_pred - shift_targ == 0:
                correct_predictions_for_example += 1

        example_accuracy = correct_predictions_for_example / len(pred)
        examples_accuracies.append(example_accuracy)

    overall_accuracy = sum(examples_accuracies) / len(examples_accuracies)

    return overall_accuracy


def custom_confusion_matrix(predictions, targets):
    """
    Creates a confusion matrix because sklearn's implementation can't deal with multilabel data.
    :param predictions: Numpy array. Predictions made by the classifier.
    :param targets: Numpy array. Targets for the supplied predictions. The proper labels.
    :return: Numpy array with structure: [[True positive count, False positive count], [False negative count, True
    negative count]]
    """
    tp, fp, fn, tn = [], [], [], []

    for pred, targ in zip(predictions, targets):
        for shift_pred, shift_targ in zip(pred, targ):
            if shift_pred == 1 and shift_targ == 1:  # True positive
                tp.append(1)
            elif shift_pred == 1 and shift_targ == 0:  # False positive
                fp.append(1)
            elif shift_pred == 0 and shift_targ == 1:  # False negative
                fn.append(1)
            elif shift_pred == 0 and shift_targ == 0:  # True negative:
                tn.append(1)

    tp_count = len(tp)
    fp_count = len(fp)
    fn_count = len(fn)
    tn_count = len(tn)

    conf_matrix = np.array([
        [tp_count, fp_count],
        [fn_count, tn_count]
    ])

    return conf_matrix


def precision_recall(conf_matrix):
    """
    Calculate the precision and recall of the model from the confusion matrix.
    :param conf_matrix: Numpy array with structure: [[True positive count, False positive count], [False negative count,
     True negative count]].
    :return: Tuple of floats (precision, recall).
    """
    tp_count, fp_count, fn_count, tn_count = conf_matrix[0][0], conf_matrix[0][1], conf_matrix[1][0], conf_matrix[1][1]

    precision = tp_count / (tp_count + fp_count)
    recall = tp_count / (tp_count + fn_count)

    return precision, recall


def print_model_analysis(predictions, targets, print_conf_matrix=False):
    """
    Prints key metrics of the given model.
    :param predictions: Numpy array. Predictions made by the classifier.
    :param targets: Numpy array. Targets for the supplied predictions. The proper labels.
    :param print_conf_matrix: Bool flag whether or not to print the confusion matrix as this is not always needed.
    """
    accuracy = accuracy_per_shift(predictions, targets)
    built_in_accuracy = accuracy_score(targets, predictions)

    conf_matrix = custom_confusion_matrix(predictions, targets)

    precision, recall = precision_recall(conf_matrix)

    print('Accuracy:', accuracy)
    print('Built-in accuracy:', built_in_accuracy)
    if print_conf_matrix:
        print('Confusion Matrix:\n', conf_matrix)
    print('Precision:', precision)
    print('Recall:', recall)

    print()


def display_predictions_vs_targets(predictions, targets):
    for pred, targ in zip(predictions, targets):
        print(pred)
        print(targ)
        print()


def precision_threshold(predictions, targets, threshold=0.7):
    """
    Shows the ratio of predictions that achieved a precision greater than the supplied threshold
    :param predictions: Numpy array. Predictions made by the classifier.
    :param targets: Numpy array. Targets for the supplied predictions. The proper labels.
    :param threshold:
    :return:
    """
    number_of_examples_meeting_threshold = 0

    for pred, targ in zip(predictions, targets):
        total_positive_guesses = sum(pred)
        correct_positive_guesses = 0

        for shift_pred, shift_targ in zip(pred, targ):
            if shift_pred == 1 and shift_targ == 1:
                correct_positive_guesses += 1

        example_precision = correct_positive_guesses / total_positive_guesses
        if example_precision > threshold:
            number_of_examples_meeting_threshold += 1

    print(number_of_examples_meeting_threshold)
    examples_meeting_threshold_ratio = number_of_examples_meeting_threshold / len(predictions)
    print(examples_meeting_threshold_ratio)


def create_pipeline(numeric_attribs, categoric_attribs, remove_ratios, remove_needs):
    """
    Creates a ColumnTransformer pipeline to transform the feature DataFrame into model compatible form.
    :param numeric_attribs: List of strings which are column titles that make up numerical values.
    :param categoric_attribs: List of strings which are column titles that make up categorical values.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :return: ColumnTransformer Pipeline.
    """
    # get a list of ratio and need column titles, independently, from numeric_attribs.
    ratio_attribs = []
    need_attribs = []
    for attrib in numeric_attribs:
        if attrib.endswith('_chance'):
            ratio_attribs.append(attrib)
        elif attrib.endswith('_need'):
            need_attribs.append(attrib)

    cats = [['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']] * len(categoric_attribs)

    transformation_pipeline = ColumnTransformer([
        ('numeric', NumericColumnsRemover(remove_ratios=remove_ratios, remove_needs=remove_needs, ratios=ratio_attribs,
                                          needs=need_attribs), numeric_attribs),
        ('categoric', OneHotEncoder(categories=cats), categoric_attribs)
    ])

    return transformation_pipeline


def prepare_features_targets(path_to_csv, path_to_json_dir, company, department, needs_type='manual',
                             ratio_cleaner_val=None, random_state=None, remove_ratios=False, remove_needs=False):
    """
    Splits shift data into a train and test set then prepares it for use in an sklearn model.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param needs_type: String. Specifies type of needs to use. 'manual', 'avg', or 'median'.
    :param ratio_cleaner_val: The cutoff point for ratios to be removed from the data. The max, 7.0, removes all ratios.
    The min, 0.0 removes none. Recommended values to experiment with are 2.0, 1.5, and 1.0. Use None to ignore this.
    :param random_state: Int. Seed to remember the split of the data in StratifiedShuffleSplit.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :return: Tuple of prepared training features, training targets, testing features, testing targets, and
    interpretation keys dict, in that order.
    """
    schedules_data, max_scale_value = get_shift_data(path_to_csv, path_to_json_dir, company, department,
                                                     needs_type=needs_type)

    if ratio_cleaner_val is not None:
        schedules_data = ratio_cleaner(schedules_data, min_ratio_value=ratio_cleaner_val)

    # ensure days of the week are represented proportionally to the total data. Stratified.
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=random_state)
    for train_index, test_index in split.split(schedules_data, schedules_data['day_of_week']):
        strat_train_df = schedules_data.loc[train_index]
        strat_test_df = schedules_data.loc[test_index]

    train_features = strat_train_df.drop(['shifts_targets', 'shifts_key'], axis=1)
    train_targets = strat_train_df['shifts_targets']
    test_features = strat_test_df.drop(['shifts_targets', 'shifts_key'], axis=1)
    test_targets = strat_test_df['shifts_targets']

    # get a list of numerical column titles and categorical column titles.
    numeric_attribs = list(train_features.drop('day_of_week', axis=1))
    categoric_attribs = ['day_of_week']

    transformation_pipeline = create_pipeline(numeric_attribs, categoric_attribs, remove_ratios, remove_needs)

    # Process the features into a numpy array to be used by the model.
    prepared_train_features = transformation_pipeline.fit_transform(train_features)
    prepared_train_targets = np.array([np.array(row) for row in train_targets.values.tolist()])
    prepared_test_features = transformation_pipeline.fit_transform(test_features)
    prepared_test_targets = np.array([np.array(row) for row in test_targets.values.tolist()])

    # Use for interpretation of the final results. Pass it to the second stage of the system.
    train_shifts_key = strat_train_df['shifts_key'].iloc[0]  # all rows the same, so just pick the first.
    test_shifts_key = strat_test_df['shifts_key'].iloc[0]  # all rows the same, so just pick the first.
    day_of_week_key = transformation_pipeline.named_transformers_['categoric'].categories_[0]

    interpretation_keys = {
        'train_shifts_key': train_shifts_key,
        'test_shifts_key': test_shifts_key,
        'day_of_week_key': day_of_week_key,
        'max_scale_value': max_scale_value
    }

    return (prepared_train_features, prepared_train_targets,
            prepared_test_features, prepared_test_targets,
            interpretation_keys)


def train_model_for_prediction(path_to_csv, path_to_json_dir, company, department, classifier_id='random_forest',
                               needs_type='manual', ratio_cleaner_val=None, random_state=None, remove_ratios=False,
                               remove_needs=False):
    """
    Trains the specified model to make predictions to be used in production.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param classifier_id: String. The classifier to use for training and prediction. 'random_forest', 'k_neighbors', or
     'radius_neighbors'.
    :param needs_type: String. Specifies type of needs to use. 'manual', 'avg', or 'median'.
    :param ratio_cleaner_val: The cutoff point for ratios to be removed from the data. The max, 7.0, removes all ratios.
    The min, 0.0 removes none. Recommended values to experiment with are 2.0, 1.5, and 1.0. Use None to ignore this.
    :param random_state: Int. Seed to remember the split of the data in StratifiedShuffleSplit.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :return: Tuple of an instance of a trained RandomForestClassifier, KNeighborsClassifier, or
    RadiusNeighborsClassifier, AND the interpretation_keys.
    """
    (prepared_train_features, prepared_train_targets,
     prepared_test_features, prepared_test_targets,
     interpretation_keys) = prepare_features_targets(path_to_csv, path_to_json_dir, company, department,
                                                     needs_type=needs_type, ratio_cleaner_val=ratio_cleaner_val,
                                                     random_state=random_state, remove_ratios=remove_ratios,
                                                     remove_needs=remove_needs)

    if classifier_id == 'random_forest':
        classifier = RandomForestClassifier(n_estimators=500, max_leaf_nodes=16, n_jobs=1)
    elif classifier_id == 'k_neighbors':
        classifier = KNeighborsClassifier()
    elif classifier_id == 'radius_neighbors':
        classifier = RadiusNeighborsClassifier()
    else:
        raise ValueError('Invalid classifier_id specified:', classifier_id + '.',
                         'Must be of type \'random_forest\', \'k_neighbors\', or \'radius_neighbors\'.')

    classifier.fit(prepared_train_features, prepared_train_targets)

    # run the test data through it to gauge effectiveness.
    test_predictions = classifier.predict(prepared_test_features)
    print_model_analysis(test_predictions, prepared_test_targets)

    return classifier, interpretation_keys


def get_day_of_week_shift_prediction(classifier, day_of_week, shift_ratios, needs, remove_ratios, remove_needs,
                                     max_scale_value):
    """
    Predicts the shifts to be had for given day of the week.
    :param classifier: Instance of a trained sklearn classifier to predict the shifts.
    :param day_of_week: String of the name of a day of the week, lowercase. ex. 'sunday'.
    :param shift_ratios: Dict of shift ratios for each day of the week. Every day of the week contains the same shifts
    but independently calculated ratios. Ex. sunday 3-8 will probably have a different ratio than tuesday 3-8.
    :param needs: Dict of needs for each day of the week.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :param max_scale_value: Float with the highest value found in needs training data in a week. Recursive.
    :return: Numpy array containing the prediction to be processed.
    """
    current_needs = needs[-1]
    # any day works for the key of shift_ratios, they all have the same keys.
    all_possible_shifts = list(shift_ratios['sunday'].keys())
    data = {'day_of_week': [day_of_week]}

    shift_ratios_chance, x_needs, _ = create_features_for_single_example(
        shift_ratios, current_needs, day_of_week, 0, all_possible_shifts
    )
    # the shift key for the output will always be the same as the original test/train data (I think, probably).

    for key, ratio in shift_ratios_chance.items():
        data[key] = [ratio]
    for key, need in x_needs.items():
        data[key] = [need]

    features_df = pd.DataFrame(data)
    # scale the dataframes' needs to MinMaxScaler
    needs_columns = [
        '0_need', '1_need', '2_need', '3_need', '4_need', '5_need', '6_need',
        '7_need', '8_need', '9_need', '10_need', '11_need', '12_need', '13_need',
        '14_need', '15_need', '16_need', '17_need', '18_need', '19_need', '20_need',
        '21_need', '22_need', '23_need'
    ]
    features_df[needs_columns] = custom_min_max_scaler(features_df[needs_columns], 0.0, max_scale_value)

    numeric_attribs = list(features_df.drop('day_of_week', axis=1))
    categoric_attribs = ['day_of_week']

    transformation_pipeline = create_pipeline(numeric_attribs, categoric_attribs, remove_ratios, remove_needs)
    prepared_input = transformation_pipeline.fit_transform(features_df)

    prediction = classifier.predict(prepared_input)

    return prediction[0]


def get_week_prediction(classifier, shift_ratios, needs, remove_ratios, remove_needs,
                        max_scale_value):
    """
    Predicts the shifts to be had for given day of the week.
    :param classifier: Instance of a trained sklearn classifier to predict the shifts.
    :param shift_ratios: Dict of shift ratios for each day of the week. Every day of the week contains the same shifts
    but independently calculated ratios. Ex. sunday 3-8 will probably have a different ratio than tuesday 3-8.
    :param needs: Dict of needs for each day of the week.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :param max_scale_value: Float with the highest value found in needs training data in a week. Recursive.
    :return: Numpy array containing the prediction to be processed.
    """
    days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    predictions = {}
    for day in days_of_week:
        prediction = get_day_of_week_shift_prediction(
            classifier, day, shift_ratios, needs, remove_ratios, remove_needs, max_scale_value
        )
        predictions[day] = prediction

    return predictions


def interpret_predictions(predictions, shifts_key):
    """
    For testing only. Displays the predictions in a readable format.
    :param predictions: Dict of predictions list for each day of the week.
    :param shifts_key: Ordered list of all possible shifts.
    """
    for day_name, prediction in predictions.items():
        print(day_name.title())
        for index, shift in enumerate(prediction):
            if shift == 1:
                military_split_time = shifts_key[index].split(' - ')
                start_time = military_to_standard_time(military_split_time[0])
                end_time = military_to_standard_time(military_split_time[1])

                print('\t', start_time, '-', end_time)


def predict_week_shifts(path_to_csv, path_to_json_dir, company, department, needs_type='manual', remove_ratios=False,
                        remove_needs=False):
    """
    Predicts the shifts to be had in a week.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param path_to_json_dir: String. Path to a directory containing all json schedules.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param needs_type: String. Specifies type of needs to use. 'manual', 'avg', or 'median'.
    :param remove_ratios: Bool. Whether or not the remove the ratios from the features.
    :param remove_needs: Bool. Whether or not the remove the needs from the features.
    :return: Tuple of (predictions, shifts_key).
    """
    classifier, interpretation_keys = train_model_for_prediction(path_to_csv, path_to_json_dir, company, department,
                                                                 classifier_id='random_forest', needs_type=needs_type,
                                                                 ratio_cleaner_val=None, random_state=None,
                                                                 remove_ratios=remove_ratios, remove_needs=remove_needs)

    shift_ratios = create_shift_ratios(path_to_csv, path_to_json_dir)
    manual_needs, auto_avg_needs, auto_median_needs = get_needs_methods(path_to_json_dir, company, department)

    if needs_type == 'manual':
        needs = manual_needs
    elif needs_type == 'avg':
        needs = auto_avg_needs
    elif needs_type == 'median':
        needs = auto_median_needs
    else:
        raise ValueError('Invalid needs_type: \'' + needs_type + '\'. Must be string \'manual\', \'avg\', or \'median\'.')

    max_scale_value = interpretation_keys['max_scale_value']

    predictions = get_week_prediction(classifier, shift_ratios, needs, remove_ratios, remove_needs, max_scale_value)
    shifts_key = interpretation_keys['train_shifts_key']  # can use this one. It will be the same for all.

    # interpret_predictions(predictions, shifts_key)

    return predictions, shifts_key


# Predict me the shifts for a week. compare that with this weeks actual shifts.
# Pick a day of the week. Generate ratios and needs for that day. Feed it through the model.
