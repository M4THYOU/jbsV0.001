import os
import tarfile
from six.moves import urllib
from zlib import crc32

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn

from sklearn.model_selection import StratifiedShuffleSplit, cross_val_score, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

import joblib  # to save models

HOUSING_URL = 'https://raw.githubusercontent.com/ageron/handson-ml/master/datasets/housing/housing.tgz'
HOUSING_TGZ = 'housing.tgz'
HOUSING_CSV = 'housing.csv'

urllib.request.urlretrieve(HOUSING_URL, HOUSING_TGZ)
housing_tgz = tarfile.open(HOUSING_TGZ)
housing_tgz.extractall()
housing_tgz.close()

housing_data = pd.read_csv(HOUSING_CSV)

""" # Display data in different ways.
print(housing_data.head())
print(housing_data.info())
print(housing_data.describe())

housing_data.hist(bins=50, figsize=(8, 8))
plt.show()
"""

########################################################################################################################


def split_train_test(data, test_ratio):
    """
    Splits the data into training and testing sets.
    :param data: Pandas DataFrame of the data.
    :param test_ratio: Decimal representing the percentage of data to be used in the testing set.
    :return: training_dataframe, testing_dataframe
    """
    shuffled_index = np.random.permutation(len(data))
    test_set_size = int(len(data) * test_ratio)

    train_indices = shuffled_index[test_set_size:]
    test_indices = shuffled_index[:test_set_size]

    return data.iloc[train_indices], data.iloc[test_indices]


def test_set_check(identifier, test_ratio):
    """
    CRC = Cyclic redundancy check. Error detecting code.
    In this case, the function computes the hash of each instance in the data (from its UID/identifier).
    Then, put that instance in the test set if it is lower or equal to test_ratio%.
    """
    return crc32(np.int64(identifier)) & 0xffffffff < test_ratio * 2**32


def split_train_test_by_id(data, test_ratio, id_column):
    """
    Splits the data into training and testing sets. Ensures that the same test set is used in every run.
    :param data: Pandas DataFrame of the data.
    :param test_ratio: Decimal representing the percentage of data to be used in the testing set.
    :param id_column: String
    :return:
    """
    ids = data[id_column]
    # Check if the instance should be in the test set.
    in_test_set = ids.apply(lambda id_: test_set_check(id_, test_ratio))

    # If in_test_set, place it in test set and not in training set. Vice versa for !in_test_set
    return data.loc[~in_test_set], data.loc[in_test_set]

########################################################################################################################


# Basic way to split training and testing data.
# training_housing_data, testing_housing_data = split_train_test(housing_data, 0.2)  # basic way
#
# ensures the same test set is used every run to prevent model from training on this set by creating an id by index.
housing_data_with_id = housing_data.reset_index()  # creates an 'index' column
# ensures the same test set is used every run to prevent model from training on this set by creating an id from stable
# features like latitude and longitude.
# This one does not correctly get the intended 20%. Some duplicate id's generate from latitude and longitude.
housing_data_with_id['id'] = housing_data['longitude'] * 1000 + housing_data['latitude']
training_housing_data, testing_housing_data = split_train_test_by_id(housing_data_with_id, 0.2, 'index')

# ## Another way.

# Use stratified sampling. Bucketize a column then ensure each column is accurately represented in train and test data.

housing_data['income_category'] = pd.cut(housing_data['median_income'], bins=[0., 1.5, 3.0, 4.5, 6., np.inf],
                                         labels=[1, 2, 3, 4, 5])
# housing_data['income_category'].hist()
# plt.show()

# StratifiedShuffleSplit is from sklearn.model_selection
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=50)
for training_index, testing_index in split.split(housing_data, housing_data['income_category']):
    strat_train_set = housing_data.loc[training_index]
    strat_test_set = housing_data.loc[testing_index]

# measure how much each strata is represented as a ratio to the entire set.
print(strat_test_set['income_category'].value_counts() / len(strat_test_set))

# finally, remove the income_category feature because its only purpose is the help divide train/test sets.
for set_ in (strat_train_set, strat_test_set):
    set_.drop('income_category', axis=1, inplace=True)

# Copy training data to be free in playing around.
housing_data = strat_train_set.copy()

# housing_data.plot(kind='scatter', x='longitude', y='latitude', alpha=0.4, s=housing_data['population']/100,
# label='population', figsize=(10, 7), c='median_house_value', cmap=plt.get_cmap('jet'), colorbar=True)
# plt.show()

# Not THIS way. Use a custom transformer instead, for easy testing.
# housing_data['rooms_per_household'] = housing_data['total_rooms'] / housing_data['households']
# housing_data['bedrooms_per_room'] = housing_data['total_bedrooms'] / housing_data['total_rooms']
# housing_data['population_per_household'] = housing_data['population'] / housing_data['households']

corr_matrix = housing_data.corr()
print(corr_matrix['median_house_value'].sort_values(ascending=False))

# Get features and labels
housing_features = housing_data.drop('median_house_value', axis=1)
housing_labels = housing_data['median_house_value'].copy()

# total_bedrooms has missing values. We must fix this.
# housing_data.dropna(subset=['total_bedrooms'])  # get rid of entire instance if the value is missing.
# housing_data.drop('total_bedrooms', axis=1)  # get rid of the feature itself, for all instances.
# median = housing_data['total_bedrooms'].median()
# housing_data['total_bedrooms'].fillna(median, inplace=True)  # replace the na's with the median. Can use other fillers
# OR use sklearn.impute's SimpleImputer to get the median to fill the values.

imputer = SimpleImputer(strategy='median')
# Imputer fills in missing values of all columns with, in this case, the median. Does not work for discrete bc words.
housing_num = housing_features.drop('ocean_proximity', axis=1)  # drop non-numeric columns
imputer.fit(housing_num)
filled_features_np_array = imputer.transform(housing_num)
filled_features_dataframe = pd.DataFrame(filled_features_np_array, columns=housing_num.columns)

# handle categorical/text features
housing_cat = housing_features[['ocean_proximity']]
# numeric them with sklearn.preprocessing's OrdinalEncoder. Turns them into values from 0 to n (n=number of categories).
ordinal_encoder = OrdinalEncoder()
housing_cat_encoded = ordinal_encoder.fit_transform(housing_cat)
# print(housing_cat_encoded[:10])
# print(ordinal_encoder.categories_)
# numeric them with one-hot encoding! This way is better.
one_hot_encoder = OneHotEncoder()
housing_cat_encoded_1hot = one_hot_encoder.fit_transform(housing_cat)
# print(housing_cat_encoded_1hot[:10])
# print(one_hot_encoder.categories_)

########################################################################################################################
# All those transformation take too long. Combine it all with a pipeline.

# create a custom transformer
rooms_index, bedrooms_index, population_index, households_index = 3, 4, 5, 6


class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
    """
    Sample Usage:

    ###
    attr_adder = CombinedAttributesAdder(add_bedrooms_per_person=False)
    housing_extra_attribs = attr_adder.transform(housing.values)
    ###

    This kind of class allows for the easy implementation of synthetic features.
    Gives the ability to add/remove certain synthetic features to see difference in loss via a simple boolean flag.

    """
    def __init__(self, add_bedrooms_per_room=True):
        self.add_bedrooms_per_room = add_bedrooms_per_room

    def fit(self, X, y=None):
        return self  # we ain't got nothing better to do.

    def transform(self, X, y=None):
        rooms_per_household = X[:, rooms_index] / X[:, households_index]
        population_per_household = X[:, population_index] / X[:, households_index]

        if self.add_bedrooms_per_room:
            bedrooms_per_room = X[:, bedrooms_index] / X[:, rooms_index]
            return np.c_[X, rooms_per_household, population_per_household, bedrooms_per_room]
        else:
            return np.c_[X, rooms_per_household, population_per_household]


# And now the Pipeline
# For numeric columns only.
num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('attribs_adder', CombinedAttributesAdder()),
    ('std_scaler', StandardScaler()),
])
# This Pipeline sequentially applies each transformation to numeric columns with just a single call.

# now combine numerical and categorical pipelines
num_attribs = list(housing_num)
cat_attribs = ['ocean_proximity']

full_pipeline = ColumnTransformer([
    ('num', num_pipeline, num_attribs),
    ('cat', OneHotEncoder(), cat_attribs),
])
"""
ColumnTransformer takes a list of tuples.
Each tuple contains whatever name I want, a transformer to apply, and a list of column names to apply the transformer to
Column names not specified will be dropped.
Use 'drop' in the transformer field to explicitly drop those columns.
Use 'passthrough' in the transformer field to do nothing with those columns 
"""

prepared_housing_features = full_pipeline.fit_transform(housing_features)

# Train the model.
linear_regressor = LinearRegression()
linear_regressor.fit(prepared_housing_features, housing_labels)
# now try it on some TRAINing data.
linear_training_predictions = linear_regressor.predict(prepared_housing_features)
linear_mse = mean_squared_error(housing_labels, linear_training_predictions)
linear_rmse = np.sqrt(linear_mse)
print('Linear RMSE:', linear_rmse)

tree_regressor = DecisionTreeRegressor()
tree_regressor.fit(prepared_housing_features, housing_labels)
tree_training_predictions = tree_regressor.predict(prepared_housing_features)
tree_rmse = np.sqrt(mean_squared_error(housing_labels, tree_training_predictions))
print('Tree RMSE:', tree_rmse)  # gets zero error!? Yeah, that's overfitting.

forest_regressor = RandomForestRegressor(n_estimators=10)
forest_regressor.fit(prepared_housing_features, housing_labels)
forest_training_predictions = forest_regressor.predict(prepared_housing_features)
forest_rmse = np.sqrt(mean_squared_error(housing_labels, forest_training_predictions))
print('Forest RMSE:', forest_rmse)


def display_scores(scores):
    print('\nScores:', scores)
    print('Mean:', scores.mean())
    print('Standard Deviation:', scores.std())


# instead, try cross-validation.
# Split training data into 10 subsets then trains/evaluates the model 10 times.
# Each run, it picks a new subset to validate on and uses the other 9 for training. Returns array.

cross_val_linear_scores = cross_val_score(linear_regressor, prepared_housing_features, housing_labels,
                                          scoring='neg_mean_squared_error', cv=10)
linear_rmse_scores = np.sqrt(-cross_val_linear_scores)
display_scores(linear_rmse_scores)

cross_val_tree_scores = cross_val_score(tree_regressor, prepared_housing_features, housing_labels,
                                        scoring='neg_mean_squared_error', cv=10)
tree_rmse_scores = np.sqrt(-cross_val_tree_scores)
display_scores(tree_rmse_scores)

cross_val_forest_scores = cross_val_score(forest_regressor, prepared_housing_features, housing_labels,
                                          scoring='neg_mean_squared_error', cv=10)
forest_rmse_scores = np.sqrt(-cross_val_forest_scores)
display_scores(forest_rmse_scores)

# use a grid search to find optimal hyperparameters

param_grid = [
    {'n_estimators': [3, 10, 30], 'max_features': [2, 4, 6, 8]},
    {'bootstrap': [True], 'n_estimators': [20, 40], 'max_features': [10, 12, 14]}
]

new_forest_regressor = RandomForestRegressor(n_estimators=10)
grid_search = GridSearchCV(new_forest_regressor, param_grid, cv=5, scoring='neg_mean_squared_error',
                           return_train_score=True)
grid_search.fit(prepared_housing_features, housing_labels)
print(grid_search.best_params_)
print()
grid_search_results = grid_search.cv_results_
for mean_score, params in zip(grid_search_results['mean_test_score'], grid_search_results['params']):
    print(np.sqrt(-mean_score), params)

# determine importance of each feature. Kind of like a correlation matrix except after training??
feature_importances = grid_search.best_estimator_.feature_importances_

extra_attribs = ['rooms_per_hhold', 'pop_per_hhold', 'bedrooms_per_room']
cat_encoder = full_pipeline.named_transformers_['cat']  # get column names of 'cat'(egories)
cat_one_hot_attribs = list(cat_encoder.categories_[0])
attributes = num_attribs + extra_attribs + cat_one_hot_attribs
print(sorted(zip(feature_importances, attributes), reverse=True))

# evaluate the system on test data.
final_model = grid_search.best_estimator_
test_features = strat_test_set.drop('median_house_value', axis=1)
test_labels = strat_test_set['median_house_value']

# fit_transform is only used on training. Don't wanna fit to training data.
prepared_test_features = full_pipeline.transform(test_features)
final_predictions = final_model.predict(prepared_test_features)

final_rmse = np.sqrt(mean_squared_error(test_labels, final_predictions))

########################################################################################################################

# to save a model
# joblib.dump(forest_regressor, 'forest_regressor.pkl')
# to load a saved model
# loaded_model = joblib.load('forest_regressor.pkl')

########################################################################################################################

""" Multilabel classifier
is_large_target = (train_targets >= 7)  # if the number is 7 or higher.
is_odd_target = (train_targets % 2 == 1)
multilabel_target = np.c_[is_large_target, is_odd_target]

k_neighbors_classifier = KNeighborsClassifier()
# k_neighbors_classifier.fit(train_examples, multilabel_target)
k_neighbors_prediction = cross_val_predict(k_neighbors_classifier, train_examples, multilabel_target, cv=2)

print(k_neighbors_classifier.predict([sample_digit]))  # outputs 2 labels
print(multilabel_target[0])
print(train_targets[0])
# f1 score across ALL labels. Assumes all labels are of equal importance.
# use average='weighted' to give greater weight to label with greater number of occurrences.
print(f1_score(multilabel_target, k_neighbors_prediction, average='macro'))

"""

"""
from sklearn.ensemble import RandomForestClassifier

from sklearn.datasets import make_moons
from sklearn.metrics import accuracy_score

data = make_moons(10000, noise=0.2)
examples = data[0]
targets = data[1]

train_examples, train_targets, test_examples, test_targets = examples[:8000], targets[:8000], examples[8000:], targets[8000:]

rand_forest_classifier = RandomForestClassifier(n_estimators=500, max_leaf_nodes=16, n_jobs=-1)
rand_forest_classifier.fit(train_examples, train_targets)

predictions = rand_forest_classifier.predict(test_examples)
print(accuracy_score(test_targets, predictions))

# identify feature importance
for name, score in zip(['X value', 'Y value'], rand_forest_classifier.feature_importances_):
    print(name, score)
"""

"""
def test(path_to_csv, path_to_json_dir, company, department):
    (prepared_train_features, prepared_train_targets,
     prepared_test_features, prepared_test_targets,
     interpretation_keys) = prepare_features_targets(path_to_csv, path_to_json_dir, company, department,
                                                     needs_type='manual', ratio_cleaner_val=None, random_state=None,
                                                     remove_ratios=False, remove_needs=False)

    ##########

    kn_classifier = KNeighborsClassifier()

    print('K-Neighbors Classifier')
    kn_classifier.fit(prepared_train_features, prepared_train_targets)
    kn_train_predictions = kn_classifier.predict(prepared_train_features)
    print_model_analysis(kn_train_predictions, prepared_train_targets)

    kn_test_predictions = kn_classifier.predict(prepared_test_features)
    print_model_analysis(kn_test_predictions, prepared_test_targets)
    print('\n')

    ##########

    radius_classifier = RadiusNeighborsClassifier()

    print('Radius Neighbors Classifier')
    radius_classifier.fit(prepared_train_features, prepared_train_targets)
    radius_train_predictions = radius_classifier.predict(prepared_train_features)
    print_model_analysis(radius_train_predictions, prepared_train_targets)

    radius_test_predictions = radius_classifier.predict(prepared_test_features)
    print_model_analysis(radius_test_predictions, prepared_test_targets)
    print('\n')

    ##########

    rand_forest_classifier = RandomForestClassifier(n_estimators=500, max_leaf_nodes=16, n_jobs=1)

    print('Random Forest Classifier')
    rand_forest_classifier.fit(prepared_train_features, prepared_train_targets)
    rand_forest_train_predictions = rand_forest_classifier.predict(prepared_train_features)
    print_model_analysis(rand_forest_train_predictions, prepared_train_targets)

    rand_forest_test_predictions = rand_forest_classifier.predict(prepared_test_features)
    print_model_analysis(rand_forest_test_predictions, prepared_test_targets)
    print('\n')

    ##########

    precision_threshold(rand_forest_test_predictions, prepared_test_targets, threshold=0.75)
    precision_threshold(rand_forest_train_predictions, prepared_train_targets, threshold=0.75)
"""
