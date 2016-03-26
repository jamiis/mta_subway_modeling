from sklearn import preprocessing, grid_search
from sklearn.cross_validation import KFold
from sklearn.linear_model import SGDRegressor
import numpy as np
import pandas as pd
import util

# read in reformatted, cleaned, augmented dataset
df = pd.read_pickle('augmented/turnstile')

# our model is going to predict exit traffic based on each single hour.
# this will allow us to be more fine grained and robust.
# to find a four-hour interval we will run the model for 4 times and sum the 

# note: unfortunately UNIT's are not unique to STATION's thus can't use STATION's as features.
#       also, since we are using the regular audit times, MINUTE will always be 0 making useless as a feature.
#       last, UNIT's will be added as a matrix of one-hot-encoded vectors.
features = ['HOUR','MONTH','YEAR','DAYOFYEAR','DAYOFWEEK','WEEKOFYEAR']
target = 'EXITS_PER_INTERVAL'

### clean the data before modeling.
# we don't want to take any risks and we have enough data
# to remove potentially harmful / irregular datapoints.

# train only on the regular 4-hr auditing time periods remove irregular audits
regular_times = df.TIME.isin([
    '00:00:00', '04:00:00', '08:00:00', '12:00:00', '16:00:00', '20:00:00'])
reg_aud = (df.DESC == 'REGULAR')
df_clean = df[regular_times & reg_aud]

# reduce to features and target. UNIT will be dropped in a moment
df_clean = df_clean.loc[:,['UNIT']+features+[target]]
# remove rows with NaN values
df_clean = df_clean.dropna()

# pull out target before scaling features
y = df_clean.loc[:,target].as_matrix()
del df_clean[target]

# one-hot-encode UNIT since it's a categorical variables
np_one_hot_encoded = pd.get_dummies(df_clean.UNIT).as_matrix()
del df_clean['UNIT']

# normalize current set of features to have zero mean and unit variance
np_scaled = preprocessing.scale(df_clean)

# get final input X of scaled scalars and one-hot-encoded categories
X = np.concatenate((np_scaled, np_one_hot_encoded), axis=1)
print '% data retained after cleaning', util.perc_of_total_data(X,df)
del df_clean, df

# setup model. use simple SGD initially
# a major advantage of SGD is its efficiency, which is essentially 
# linear in the number of training examples.
sgdreg = SGDRegressor(
    n_iter= np.ceil(10.0**6 / X.shape[0]), # sklearn recommended
)
parameters = {
    'alpha': 10.0**-np.arange(1,7), # sklearn recommended
    'penalty': ['l2','l1','elasticnet'],
}

import multiprocessing
cores = multiprocessing.cpu_count()

# perform grid search in parallel. need more memory to do full 32-core parallel
num_jobs = cores / 2
print 'grid search in parallel. num cores used:', num_jobs

import time
start = time.time()
clf = grid_search.GridSearchCV(sgdreg, parameters, n_jobs=num_jobs, cv=5)
clf.fit(X, y)
print time.time() - start

# don't forget to save the model!
from sklearn.externals import joblib
joblib.dump(clf, 'estimators/clf.pkl') 
