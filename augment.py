import glob, os
import numpy as np
import pandas as pd
import util

# get all reformatted data in one dataframe in a common format, 
reformatted_files = glob.glob(os.path.join('reformatted', '*.txt'))
# reformatted_files = [f for f in reformatted_files if util.is_above(f)]
# TODO delete this ^
df = pd.concat(pd.read_pickle(f) for f in reformatted_files)

# we're going to augment the data with features that will be useful
# first sort values by Station then Turnstile and last by Datetime and reset the indices
df = df.sort_values(['STATION','CA','UNIT','SCP','DATETIME']).reset_index()

# this will make life easier
df['TURNSTILE'] = df['CA'] + '-' + df['UNIT'] + '-' + df['SCP']

# calculate ENTRIES_PER_INTERVAL and EXITS_PER_INTERVAL
# basically, don't depend on odometer reading which is very nice
def subtract_prev(rows):
    if len(rows) != 2:
        return np.nan
    prev, curr = rows
    # prev > curr means the odometer has been reset
    return curr - prev if prev <= curr else curr
subtract_prev_rolling = lambda ser: ser.rolling(window=2).apply(subtract_prev)
# TODO in ipython notebook show graph of odometer resetting
# use rolling window to calculate per-interval entries and exits
df_grouped_turnstile = df.groupby(['TURNSTILE','STATION'])
df['ENTRIES_PER_INTERVAL'] = df_grouped_turnstile['ENTRIES'].apply(subtract_prev_rolling)
df['EXITS_PER_INTERVAL']   = df_grouped_turnstile['EXITS'].apply(subtract_prev_rolling)

# there is a problem with wonky turnstile odometer readings that fall over time.
# to handle: no *individual* turnstile should have even close to 1 million 
# in traffic within a 4 hour interval. cap per_intervals at 1,000,000 to remove crummy data.
def cap(val, amount):
    if val >= amount:
        return np.nan
    return val
df['ENTRIES_PER_INTERVAL'] = df['ENTRIES_PER_INTERVAL'].apply(cap, amount=1000000)
df['EXITS_PER_INTERVAL']   = df['EXITS_PER_INTERVAL'].apply(cap, amount=1000000)


# add column for busyness which is entries + exits
# this is now very easy given we have <ENTRIES/EXITS>_PER_INTERVAL
df['BUSYNESS_PER_INTERVAL'] = df.ENTRIES_PER_INTERVAL + df.EXITS_PER_INTERVAL

# add any date information that might be important for modeling
# do now so we don't have to redo everytime we tweak our model
df['MINUTE'] = df['DATETIME'].dt.minute
df['HOUR'] = df['DATETIME'].dt.hour
df['MONTH'] = df['DATETIME'].dt.month
df['YEAR'] = df['DATETIME'].dt.year
df['DAYOFWEEK'] = df['DATETIME'].dt.dayofweek
df['DAYOFYEAR'] = df['DATETIME'].dt.dayofyear
df['WEEKOFYEAR'] = df['DATETIME'].dt.weekofyear

# TODO add month busyness?

# TODO descriptive statistics???!
# http://pandas.pydata.org/pandas-docs/stable/api.html#computations-descriptive-stats
# remember, have to have them available at time of prediciton

df.to_csv('augmented.csv')
# save entire dataframe
util.save_df(df, 'turnstile', 'augmented')
