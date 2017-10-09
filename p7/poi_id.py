#!/usr/bin/python

import sys
import pickle
import numpy as np
from pprint import pprint
from pandas import DataFrame

from collections import defaultdict

sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


#Task 1: Select what features you'll use.

	
features_list = ['poi',
				'salary',
				'deferral_payments',
				'total_payments',
				'loan_advances',
				'bonus',
				'restricted_stock_deferred',
				'deferred_income',
				'total_stock_value',
				'expenses',
				'exercised_stock_options',
				'other',
				'long_term_incentive',
				'restricted_stock',
				'director_fees',
				'to_messages',
				#'email_address',
				'from_poi_to_this_person',
				#'from_messages',
				'from_this_person_to_poi',
				'shared_receipt_with_poi',
				#'shared_receipt_with_poi_ratio',
				#'sent_to_poi_ratio',
				#'received_from_poi_ratio'
				]

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


#Task 2: Remove outliers

data_dict.pop( "TOTAL", 0 )
data_dict.pop( "THE TRAVEL AGENCY IN THE PARK", 0)

f_list = ['salary', 'bonus', 'long_term_incentive', 'deferred_income', 'deferral_payments', 
'loan_advances', 'other', 'expenses', 'director_fees', 'total_payments', 'exercised_stock_options', 
'restricted_stock', 'restricted_stock_deferred', 'total_stock_value']

for employee, feature in data_dict.iteritems():

	if employee == 'BHATNAGAR SANJAY':
		j=len(f_list)-1
		while j >= 0:
			feature[f_list[j]] = feature[f_list[j-1]]
			j-=1
		feature['salary'] = 'NaN'

	if employee == 'BELFER ROBERT':
		i=3
		while i < len(f_list)-1:
			feature[f_list[i]] = feature[f_list[i+1]]
			i+=1
		feature[f_list[i]] = 'NaN'

	
#Task 3: Create new feature(s)

e_list = ['to_messages', 'from_messages', 'from_poi_to_this_person', 'from_this_person_to_poi',
'shared_receipt_with_poi', 'received_from_poi_ratio', 'sent_to_poi_ratio']


for employee, feature in data_dict.iteritems():

	# 'from_poi_to_this_person' to 'to_messages' ratio
	if feature['from_poi_to_this_person'] == 'NaN' or feature['to_messages'] == 'NaN':
		feature['received_from_poi_ratio'] = 'NaN'
	else:
		feature['received_from_poi_ratio'] = \
			float(feature['from_poi_to_this_person']) / float(feature['to_messages'])

	# 'from_this_person_to_poi' to 'from_messages' ratio
	if feature['from_this_person_to_poi'] == 'NaN' or feature['from_messages'] == 'NaN':
		feature['sent_to_poi_ratio'] = 'NaN'
	else:
		feature['sent_to_poi_ratio'] = \
			float(feature['from_this_person_to_poi']) / float(feature['from_messages'])

	# 'shared_receipt_with_poi_ratio' to 'to_messages' ratio
	if feature['shared_receipt_with_poi'] == 'NaN' or feature['to_messages'] == 'NaN':
		feature['shared_receipt_with_poi_ratio'] = 'NaN'
	else:
		feature['shared_receipt_with_poi_ratio'] = \
			float(feature['shared_receipt_with_poi']) / float(feature['to_messages'])


my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectKBest

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

# Provided to give you a starting point. Try a variety of classifiers.

# Load pipeline steps into list

steps = [
         # Feature Selection
         ('kbest', SelectKBest()),
         #('minmax', MinMaxScaler()),

         # Classifier 1
         #('svc', SVC())
         
         # Classifier 2
         ('dtc', DecisionTreeClassifier())

         # Classifier 3
         #('rfc', RandomForestClassifier())
         ]

pipeline = Pipeline(steps)

parameters = dict(

                  #kbest__k=[9,10,11,12,13,14,15],
                  kbest__k=['all'],

                  # final runs...

                  #dtc__max_depth=[1, 2, 3, 4, 5, 6],
                  #dtc__min_samples_split=[5,6,7,8,9,10,11,12],
                  #dtc__class_weight=['balanced'],
                  #dtc__min_samples_leaf=[1,2,3],
                  #dtc__splitter=['best','random'],
                  #dtc__max_features=[None, 'auto', 'log2'],
                  #dtc__criterion=['gini','entropy']

                  dtc__criterion=['gini'],
                  dtc__min_samples_leaf=[3],
                  dtc__max_depth=[2],
                  dtc__class_weight=['balanced'],
                  dtc__min_samples_split=[4],
                  dtc__presort=[False],
                  dtc__splitter=['best']

                  # initial run...

				  #svc__C=[1, 1.5, 1.75, 2, 2.25, 2.5],
				  #svc__kernel=['linear', 'sigmoid', 'poly','rbf'],
				  #svc__gamma=['auto'],
				  #svc__class_weight=[None, 'balanced']

                  #dtc__criterion=['gini','entropy'],
                  #dtc__min_samples_leaf=[1,2,3],
                  #dtc__max_depth=[2,3,4],
                  #dtc__class_weight=['balanced']

                  #rfc__n_estimators=[9, 10],
                  #rfc__criterion=['gini','entropy'],
                  #rfc__max_features=['auto', 'sqrt'],
                  #rfc__min_samples_split=[2, 3, 4]

                  )



### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
from operator import itemgetter

# Create training sets and test sets
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3, random_state=42)

# Cross-validation for parameter tuning in grid search 
scv = StratifiedShuffleSplit(
    labels_train,
    n_iter = 20,
    test_size = 0.5,
    random_state = 42
    )

# Create, fit, and make predictions with grid search
grid_search = GridSearchCV(pipeline,
  	              param_grid=parameters,
  	              scoring = 'f1',
  	              cv=scv,
  	              error_score=0)
grid_search.fit(features_train, labels_train)

# Pick the classifier with the best tuned parameters
clf = grid_search.best_estimator_
print "\n", "Best parameters: ", grid_search.best_params_, "\n"

scores = clf.named_steps['kbest'].scores_

# recall that poi is 0 in features_list

k = {}
j = {}
selected_features = []

"""
Obtaining the features important according to the DecisionTreeClassifier parameter.
and SelectKBest() parameter.
"""
for i in clf.named_steps['kbest'].get_support(indices=True):
	selected_features.append(features_list[i+1])
	k[features_list[i+1]] = scores[i]

print "SelectKBest() Scores: "
pprint(sorted(k.items(), key=itemgetter(1), reverse=True))
print "\n"

importances = clf.named_steps['dtc'].feature_importances_

for i in range(len(selected_features)):
	j[selected_features[i]] = importances[i]

print "DecisionTreeClassifier() Feature Importances: "
pprint(sorted(j.items(), key=itemgetter(1), reverse=True))



### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)