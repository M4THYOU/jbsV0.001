from ml_scheduler.create_data.create_data import get_user_data, create_user_ratios
from firesdk.firebase_functions.firebaseconn import get_users, get_manager_users
from firesdk.util.utils import org_names_filter

import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow import feature_column
from tensorflow import keras

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


def create_pipeline(numeric_attribs, categoric_attribs):
    """
    Creates a ColumnTransformer pipeline to transform the feature DataFrame into model compatible form.
    :param numeric_attribs: List of strings which are column titles that make up numerical values.
    :param categoric_attribs: List of strings which are column titles that make up categorical values.
    :return: ColumnTransformer Pipeline.
    """

    cats = [['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']] * len(categoric_attribs)

    transformation_pipeline = ColumnTransformer([
        ('numeric', 'passthrough', numeric_attribs),
        ('categoric', OneHotEncoder(categories=cats), categoric_attribs)
    ])

    return transformation_pipeline


def with_nn(train_features, train_targets):
    """
    Trains a neural network model on the given data.
    :param train_features: Numpy Array of features.
    :param train_targets: Numpy Array of corresponding targets.
    :return: Tensorflow Sequential model.
    """
    # prepared_train_features.shape[1] -> The number of features being used.
    # prepared_train_targets.shape[1] ->> Number of labels in a label output vector.
    model = keras.Sequential([
        keras.layers.Dense(1000, activation='selu', input_dim=train_features.shape[1]),
        keras.layers.Dense(250, activation='selu'),
        keras.layers.Dense(250, activation='selu'),
        keras.layers.Dense(250, activation='selu'),
        keras.layers.Dense(train_targets.shape[1], activation='sigmoid')
    ])

    sgd = keras.optimizers.SGD(learning_rate=0.08, momentum=0.0, nesterov=True, decay=1e-6)
    model.compile(loss='binary_crossentropy', optimizer=sgd)

    model.fit(train_features, train_targets, batch_size=32, epochs=100)

    return model


def with_alg(train_features, train_targets, classifier_id='random_forest'):
    """
    Trains a algorithmic based model on the given data.
    :param train_features: Numpy Array of features.
    :param train_targets: Numpy Array of corresponding targets.
    :param classifier_id: String. The classifier to use for training and prediction. 'random_forest', 'k_neighbors', or
     'radius_neighbors'.
    :return: Tensorflow Sequential model.
    """
    if classifier_id == 'random_forest':
        classifier = RandomForestClassifier(n_estimators=500, max_leaf_nodes=16, n_jobs=1)
    elif classifier_id == 'k_neighbors':
        classifier = KNeighborsClassifier()
    elif classifier_id == 'radius_neighbors':
        classifier = RadiusNeighborsClassifier()
    else:
        raise ValueError('Invalid classifier_id specified:', classifier_id + '.',
                         'Must be of type \'random_forest\', \'k_neighbors\', or \'radius_neighbors\'.')

    classifier.fit(train_features, train_targets)

    return classifier


def train_model_for_prediction(path_to_csv, company, department, shifts_key, classifier_id=None):
    """
    Trains the specified model to make predictions to be used in production.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :param classifier_id: String. The classifier to use for training and prediction. 'random_forest', 'k_neighbors',
     'radius_neighbors' or None. If None, use a neural net from Tensorflow.
    :return: Tuple of an instance of a trained model AND the days_of_week key from the one hot encode pipeline.
        """
    user_data = get_user_data(path_to_csv, company, department, shifts_key)

    # ensure days of the week are represented proportionally to the total data. Stratified.
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(user_data, user_data['day_of_week']):
        strat_train_df = user_data.loc[train_index]
        strat_test_df = user_data.loc[test_index]

    train_features = strat_train_df.drop(['user_targets'], axis=1)
    train_targets = strat_train_df['user_targets']
    test_features = strat_test_df.drop(['user_targets'], axis=1)
    test_targets = strat_test_df['user_targets']

    numeric_attribs = list(train_features.drop('day_of_week', axis=1))
    categoric_attribs = ['day_of_week']

    pipeline = create_pipeline(numeric_attribs, categoric_attribs)

    # Process the features into a numpy array to be used by the model.
    prepared_train_features = pipeline.fit_transform(train_features)
    prepared_train_targets = np.array([np.array(row) for row in train_targets.values.tolist()])
    prepared_test_features = pipeline.fit_transform(test_features)
    prepared_test_targets = np.array([np.array(row) for row in test_targets.values.tolist()])

    day_of_week_key = pipeline.named_transformers_['categoric'].categories_[0]

    if classifier_id is None:
        model = with_nn(prepared_train_features, prepared_train_targets)
    else:
        model = with_alg(prepared_train_features, prepared_train_targets, classifier_id=classifier_id)

    return model, day_of_week_key


def get_day_of_week_user_prediction(model, day_of_week, ratio_a, ratio_b, email, shifts_key):
    """
    Predicts the chance a user should work each shift for a day of the week
    :param model: A model, either from sklearn or tensorflow, already trained to make predictions.
    :param day_of_week: String. One of the days of the week, lowercase.
    :param ratio_a: First user predictor ratio. Number of shifts user works at x date and y time / number of total
     shifts they have had on that day of the week.
    :param ratio_b: Second user predictor ratio. Number of shifts user works at x date and y time / number of total
     times that same shift occurs on that same day of the week.
    :param email: String. The email address of the user being predicted for.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :return: Numpy array containing the prediction to be processed.
    """
    data = {'day_of_week': [day_of_week]}

    # Possible occurrence: User was just added to the department so they have no shifts in the pipeline therefore they
    # are not in the ratio dicts. If this happens, just assign them an empty ratio list.
    try:
        current_ratio_a = ratio_a[day_of_week][email]
    except KeyError:
        current_ratio_a = [0] * len(shifts_key)

    try:
        current_ratio_b = ratio_b[day_of_week][email]
    except KeyError:
        current_ratio_b = [0] * len(shifts_key)

    for index, shift in enumerate(shifts_key):
        column_title_a = shift + '_ratio_a'
        column_title_b = shift + '_ratio_b'
        user_ratio_a = current_ratio_a[index]
        user_ratio_b = current_ratio_b[index]

        if column_title_a in data:
            data[column_title_a].append(user_ratio_a)
        else:
            data[column_title_a] = [user_ratio_a]

        if column_title_b in data:
            data[column_title_b].append(user_ratio_b)
        else:
            data[column_title_b] = [user_ratio_b]

    features_df = pd.DataFrame(data)

    numeric_attribs = list(features_df.drop('day_of_week', axis=1))
    categoric_attribs = ['day_of_week']

    pipeline = create_pipeline(numeric_attribs, categoric_attribs)

    # Process the features into a numpy array to be used by the model.
    prepared_features = pipeline.fit_transform(features_df)

    prediction = model.predict(prepared_features)

    return prediction


def get_week_prediction(model, ratio_a, ratio_b, company, department, shifts_key):
    """
    Predicts the chance each user should work each shift for each day of the week.
    :param model: A model, either from sklearn or tensorflow, already trained to make predictions.
    :param ratio_a: First user predictor ratio. Number of shifts user works at x date and y time / number of total
     shifts they have had on that day of the week.
    :param ratio_b: Second user predictor ratio. Number of shifts user works at x date and y time / number of total
     times that same shift occurs on that same day of the week.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :return: Nested Dict. Day of week -> email -> predictions vector.
    """
    users = get_users(company, department)
    manager_users = get_manager_users(company, department)
    users += manager_users

    days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    predictions = {
        'sunday': {},
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
    }
    for day in days_of_week:
        for user in users:
            status = user['status']
            email = user['email']

            if status == 'active':
                prediction = get_day_of_week_user_prediction(
                    model, day, ratio_a, ratio_b, email, shifts_key
                )

                predictions[day][email] = prediction

    return predictions, users


def predict_week_users(path_to_csv, company, department, shifts_key, classifier_id=None):
    """
    Predicts the chance of each user having every shift on every day of the week.
    :param path_to_csv: String. Path to csv file of all the shifts.
    :param company: String. Name of the company.
    :param department: String. Name of the department in the company.
    :param shifts_key: List of strings representing every possible shift to be had, in specific order.
    :param classifier_id: String. The classifier to use for training and prediction. 'random_forest', 'k_neighbors',
     'radius_neighbors' or None. If None, use a neural net from Tensorflow.
    :return: Tuple. Nested Dict. Day of week -> email -> predictions vector. AND list of users_dicts. AND shifts_key
    """
    company = org_names_filter(company)
    department = org_names_filter(department)

    model, day_of_week_key = train_model_for_prediction(path_to_csv, company, department, shifts_key, classifier_id=classifier_id)
    ratio_a, ratio_b = create_user_ratios(path_to_csv, shifts_key)

    predictions, users = get_week_prediction(model, ratio_a, ratio_b, company, department, shifts_key)

    return predictions, users, shifts_key
