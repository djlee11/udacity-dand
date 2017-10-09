#!/usr/bin/python

import sys
import pickle
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


# Create the data structure using Pandas Dataframe

df = DataFrame.from_dict(data_dict, orient='index')

float_list = ['salary', 'deferral_payments', 'total_payments', 
'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income', 
'total_stock_value', 'expenses', 'exercised_stock_options', 'other', 
'long_term_incentive', 'restricted_stock', 'director_fees', 
'to_messages', 'from_poi_to_this_person', 'from_messages', 
'from_this_person_to_poi', 'shared_receipt_with_poi']

df[float_list] = df[float_list].astype(float)

###	Plot histogram for salary and inspect for outliers

#plt.hist(df['salary'].dropna())
#print df[df['salary'] > 2.0e+07]

#plt.hist(df['total_payments'].dropna())
##print df[df['total_payments'] > 1.0e+07]

#plt.hist(df['deferral_payments'].dropna())
##print df[df['deferral_payments'] < 0]

#plt.hist(df['from_messages'].dropna())
##print df[df['from_messages'] > 4000]

plt.hist(df['restricted_stock_deferred'].dropna())
print df[df['restricted_stock_deferred'] > 0.0]

#plt.hist(df['deferred_income'].dropna())
##print df[df['deferred_income'] > 0.0]

plt.show()
1