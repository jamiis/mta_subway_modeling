from sklearn import linear_model
from sklearn.cross_validation import KFold
import numpy as np
import pandas as pd
import util

# read in reformatted, cleaned, augmented dataset
df = pd.read_pickle('augmented/turnstile')

# our model is going to predict exit traffic based on each single hour.
# this will allow us to be more fine grained and robust.
# to find a four-hour interval we will run the model for 4 times and sum the 

# note: unfortunately UNIT's nums are not unique to STATION's
#       so we can't use STATION's as features.
#       also, since we are using regular times, MINUTE will always be 0
target = ['EXITS_PER_INTERVAL']
features = [
    'UNIT',
    'HOUR','MONTH','YEAR',
    'DAYOFYEAR','DAYOFWEEK','WEEKOFYEAR',
]

### clean the data before modeling.
# we don't want to take any risks and we have enough data
# to remove potentially harmful / irregular datapoints.

# train only on the regular 4-hr auditing time periods remove irregular audits
regular_times = df.TIME.isin([
    '00:00:00', '04:00:00', '08:00:00', '12:00:00', '16:00:00', '20:00:00'])
reg_aud = (df.DESC == 'REGULAR')
df_clean = df[regular_times & reg_aud]

# reduce to features and target
df_clean = df_clean.loc[:,features+target]

# remove rows with NaN values
df_clean = df_clean[df_clean.notnull()]

# split into input and target
X = df_clean.loc[:,features]
y = df_clean.loc[:,target]

print '% data retained after cleaning', util.perc_of_total_data(df_clean,df)

import ipdb; ipdb.set_trace();
# calculate k-folds for cross validation
kf = KFold(X.shape[0], n_folds=10, shuffle=True)
import ipdb; ipdb.set_trace();

clf = linear_model.SGDRegressor()
clf.fit(X, y)


"""
# add boolean columns for existence line at station
linenames_uniq = df.LINENAME.unique().tolist()
lines = list(set("".join(linenames_uniq)))
for line in lines:
    print line
    df[line] = df.LINENAME.str.contains(line)

regular_times = df.TIME.isin([
    '00:00:00', '04:00:00', '08:00:00', 
    '12:00:00', '16:00:00', '20:00:00',
])
"""
