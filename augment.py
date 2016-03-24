import glob, os
import numpy as np
import util

# get all reformatted data in one dataframe in a common format, 
reformatted_files = glob.glob(os.path.join('reformatted', '*.txt'))
reformatted_files = [f for f in reformatted_files if is_above(f)]
# TODO delete this ^
df = pd.concat(pd.read_pickle(f) for f in reformatted_files)

# we're going to augment the data with features that will be useful
# first sort values by Station then Turnstile and last by Datetime and reset the indices
dfs = df.sort_values(['STATION','CA','UNIT','SCP','DATETIME']).reset_index()

# this will make life easier
df['TURNSTILE'] = df['CA'] + df['UNIT'] + df['SCP']

# calculate ENTRIES_PER_INTERVAL and EXITS_PER_INTERVAL
# basically, don't depend on odometer reading
def subtract_prev(rows):
    if len(rows) != 2: return np.nan
    prev, curr = rows
    # prev > curr means the odometer has been reset
    return rows[1] - rows[0] if prev > curr else curr
subtract_prev_rolling = lambda ser: ser.rolling(window=2).apply(subtract_prev)
# use rolling window to calculate per-interval entries and exits
dfs_grouped_turnstile = dfs.groupby(['CA','UNIT','SCP','STATION'])
dfs['ENTRIES_PER_INTERVAL'] = dfs_grouped_turnstile['ENTRIES'].apply(subtract_prev_rolling)
dfs['EXITS_PER_INTERVAL']   = dfs_grouped_turnstile['EXITS'].apply(subtract_prev_rolling)

# add any date information that might be important for modeling
# do now so we don't have to redo everytime we tweak our model
df['MINUTES'] = df['MINUTE'].dt.hour
df['HOUR'] = df['HOUR'].dt.hour
df['DAYOFWEEK'] = df['DATETIME'].dt.dayofweek
df['DAYOFYEAR'] = df['DATETIME'].dt.dayofyear
df['WEEKOFYEAR'] = df['DATETIME'].dt.weekofyear

# TODO add month busyness?

# TODO descriptive statistics???!
# http://pandas.pydata.org/pandas-docs/stable/api.html#computations-descriptive-stats
# remember, have to have them available at time of prediciton
