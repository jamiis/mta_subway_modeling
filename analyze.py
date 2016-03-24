from __future__ import print_function
import glob, os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# TODO delete these
#pickled_files = glob.glob(os.path.join('formatted', '*.txt'))
#pickled_files = [f for f in pickled_files if util.is_above(f)]


### data analysis
df = pd.read_pickle('augmented/df.pkl')

# grab data that lies within the day and sort by datetime
# TODO TODO change date to August 1, 2013
dayrange = (df.DATETIME >= datetime(2016, 1, 8)) & \
           (df.DATETIME <  datetime(2016, 1, 9))
df_day = df[dayrange].sort_values('DATETIME')


### 1
print("1. What is the total number of entries & exits across",
      "the subway system for August 1, 2013?")
# TODO TODO change year to 2013
range_augfirst = (df.DATETIME >= datetime(2016, 1, 8)) & \
                 (df.DATETIME <  datetime(2016, 1, 9))
df_augfirst = df[range_augfirst].reset_index()
entries_augfirst = df_augfirst['ENTRIES_PER_INTERVAL']
exits_augfirst   = df_augfirst['EXITS_PER_INTERVAL']
print("Total traffic numbers for August 1st, 2013")
print("Entries {:,}".format(entries_augfirst.sum()))
print("Exits   {:,}".format(exits_augfirst.sum()))
print

"""
print("1. What is the total number of entries & exits across",
      "the subway system for August 1, 2013?")
# get first/last readings of each unique turnstile")
grouped = df_day.groupby(['TURNSTILE','STATION'])
first, last = grouped.first(), grouped.last()
# subtract the "odometer" readings to get the totals for the day
entries = last.ENTRIES - first.ENTRIES
exits   = last.EXITS   - first.EXITS
print("Total traffic numbers for August 1st, 2013")
print("Entries {:,}".format(entries.sum()))
print("Exits   {:,}".format(exits.sum()))
print
"""






### 2
print ("2. Let's define the busy-ness as sum of entry & exit count. What station was the busiest",
       "on August 1, 2013? What turnstile was the busiest on that date?")
df_augfirst_sum_on_station = df_augfirst.groupby('STATION').sum()
print("The busiest station on Aug 1st, 2013 was {} and saw traffic of {:,}".format(
        df_augfirst_sum_on_station.idxmax(),
        df_augfirst_sum_on_station.max()))
df_augfirst_sum_on_turnstile = df_augfirst.groupby('TURNSTILE').sum()
print("The busiest turnstile on Aug 1st, 2013 was {} and saw traffic of {:,}".format(
        df_augfirst_sum_on_turnstile.idxmax(),
        df_augfirst_sum_on_turnstile.max()))

"""
print ("2. Let's define the busy-ness as sum of entry & exit count. What station was the busiest",
       "on August 1, 2013? What turnstile was the busiest on that date?")
busyness = entries + exits
#df_busyness = pd.DataFrame(busyness).reset_index()
# aggregate on station column
busyness_station = busyness.groupby(level='STATION').sum()
print("The busiest station on Aug 1st, 2013 was {} and saw traffic of {:,}".format(
        busyness_station.idxmax(),
        busyness_station.max()))
# aggregate on unique turnstile (CA,Unit,SCP) and include Station for info
busyness_turnstile = busyness.groupby(level=['TURNSTILE','STATION']).sum()
print("The busiest turnstile on Aug 1st, 2013 was {} and saw traffic of {:,}".format(
        busyness_turnstile.idxmax(),
        busyness_turnstile.max()))
"""


### 3
print("3. What were the busiest and least-busy stations in the system over all of July 2013?")
# get data within July and sum on station groups
# TODO TODO change year to 2013
range_july = (df.DATETIME >= datetime(2016, 1, 1)) & \
             (df.DATETIME <  datetime(2016, 2, 1))
df_july = df[range_july].reset_index()
df_july_sum_by_station = dff.groupby(['STATION']).sum()
print("The busiest station in July, 2013, was {} and saw traffic of {:,}".format(
        df_july_sum_by_turnstile_station.idxmax().values[0],
        df_july_sum_by_turnstile_station.max().values[0]))
print("The least-busy station in July, 2013, was {} and saw traffic of {:,}".format(
        july_busyness_station.idxmin().values[0],
        july_busyness_station.min().values[0]))


"""
# get data within July and sort by datetime
# TODO TODO change year to 2013
julyrange = (df.DATETIME >= datetime(2016, 1, 1)) & \
            (df.DATETIME <  datetime(2016, 2, 1))
df_july = df[julyrange].sort_values('DATETIME')

# use the same method as above
grouped_july = df_july.groupby(['CA','UNIT','SCP','STATION'])
first, last = grouped_july.first(), grouped_july.last()
import ipdb; ipdb.set_trace();
entries = last.ENTRIES - first.ENTRIES
exits   = last.EXITS   - first.EXITS
df_july_busyness = pd.DataFrame(entries + exits).reset_index()
july_busyness_station = df_july_busyness.groupby('STATION').sum()
print("The busiest station in July, 2013, was {} and saw traffic of {:,}".format(
        july_busyness_station.idxmax().values[0],
        july_busyness_station.max().values[0]))

print("The least-busy station in July, 2013, was {} and saw traffic of {:,}".format(
        july_busyness_station.idxmin().values[0],
        july_busyness_station.min().values[0]))

df_grouped_turnstile = dff.groupby(['CA','UNIT','SCP','STATION'])
dff = df[julyrange].sort_values(['STATION','CA','UNIT','SCP','DATETIME']).reset_index()
dff_grouped_turnstile = dff.groupby(['CA','UNIT','SCP','STATION'])
dff['ENTRIES_'] = dff_grouped_turnstile['ENTRIES'].apply(subtract_prev_for_series)
dff['EXITS_']   = dff_grouped_turnstile['EXITS'].apply(subtract_prev_for_series)
"""


### 4
print("Which station had the highest average number of entries between midnight & 4am on Fridays in July 2013?")
fridays = (df.DAYEOFWEEK == 4)
midnight_to_four_am = (df.HOUR >= 0) & (df.HOUR >= 4)
df_late_night_avgs = df_july[fridays & midnight_to_four_am].avg()
print("The station matching the criteria above is {} with average traffic {:,}".format(
    df_late_night_avgs.idxmax(),
    df_late_night_avgs.max()));


### 5
print("What stations have seen the most usage growth/decline in the last year?")
# we'll just grab "last year" which is 2015
range_year = (df.DATETIME >= datetime(2015, 1, 1)) & \
             (df.DATETIME <  datetime(2016, 1, 1))
df_last_year_sum() = df_last_year[range_year].sum()
# TODO graph cumsum
# TODO chart weekly busyness totals and identify by eye?

### 6
print("What dates are the least busy? Could you identify days on which",
      "stations were not operating at full capacity or closed entirely?")
# find daily busyness totals
df_day = df.groupby(['YEAR','DAYOFYEAR']).sum(level="BUSYNESS_PER_INTERVAL")

# find X least busy dates across all NYC
df_day_sorted = df_day.sort_values(['BUSYNESS_PER_INTERVAL'])
least_busy_days = df_day_sorted.loc[:,0:10]

# and find 6 least busy dates
# maybe standard deviation on day bsais then find days that fall outside 1 std dev
df_day_on_stations = df.groupby(['YEAR','DAYOFYEAR','STATION']).sum(level="BUSYNESS_PER_INTERVAL")
# not operating
not_operating = (df_day_on_stations.BUSYNESS_PER_INTERVAL == 0)
df_day_on_stations[not_operating].count()

little_traffic = (df_day_on_stations.BUSYNESS_PER_INTERVAL > 0) & \
                 (df_day_on_stations.BUSYNESS_PER_INTERVAL <= 100)
df_day_on_stations[little_traffic].count()

# TODO maybe groupby DAY + YEAR and do a histogram of stations 
# operating at zero or little capacity
