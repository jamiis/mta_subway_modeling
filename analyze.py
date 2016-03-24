from __future__ import print_function
import glob, os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

pickled_files = glob.glob(os.path.join('formatted', '*.txt'))

# TODO delete these
in_range = lambda f: f < 'formatted/turnstile_100619.txt' or f > 'formatted/turnstile_160220.txt.' 
is_above = lambda f: f > 'formatted/turnstile_160100.txt.' 
pickled_files = [f for f in pickled_files if is_above(f)]
#print pickled_files
#print len(pickled_files)

dfs = map(pd.read_pickle, pickled_files)
df = pd.concat(dfs)

### data analysis

# grab data that lies within the day and sort by datetime
# TODO TODO change date to August 1, 2013
dayrange = (df.DATETIME >= datetime(2016, 1, 8)) & \
           (df.DATETIME <  datetime(2016, 1, 9))
df_day = df[dayrange].sort_values('DATETIME')


### 1
print("1. What is the total number of entries & exits across",
      "the subway system for August 1, 2013?")
# get first/last readings of each unique turnstile")
grouped = df_day.groupby(['CA','UNIT','SCP','STATION'])
first, last = grouped.first(), grouped.last()
# subtract the "odometer" readings to get the totals for the day
entries = last.ENTRIES - first.ENTRIES
exits   = last.EXITS   - first.EXITS
print("Total traffic numbers for August 1st, 2013")
print("Entries {:,}".format(entries.sum()))
print("Exits   {:,}".format(exits.sum()))
print






### 2
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
busyness_turnstile = busyness.groupby(level=['CA','UNIT','SCP','STATION']).sum()
print("The busiest turnstile on Aug 1st, 2013 was {} and saw traffic of {:,}".format(
        busyness_turnstile.idxmax(),
        busyness_turnstile.max()))


### 3
print("3. What were the busiest and least-busy stations in the system over all of July 2013?")
# get data withing July and sort by datetime
# TODO TODO change year to 2013
julyrange = (df.DATETIME >= datetime(2016, 1, 1)) & \
            (df.DATETIME <  datetime(2016, 2, 1))
df_july = df[julyrange].sort_values('DATETIME')

def subtract_prev(rows):
    if len(rows) != 2: return np.nan
    prev, curr = rows
    # prev > curr means the odometer has been reset
    return rows[1] - rows[0] if prev > curr else curr
subtract_prev_for_series = lambda ser: ser.rolling(window=2).apply(subtract_prev)

dff = df[julyrange].sort_values(['STATION','CA','UNIT','SCP','DATETIME']).reset_index()
dff_grouped_turnstile = dff.groupby(['CA','UNIT','SCP','STATION'])
dff['ENTRIES_'] = dff_grouped_turnstile['ENTRIES'].apply(subtract_prev_for_series)
dff['EXITS_']   = dff_grouped_turnstile['EXITS'].apply(subtract_prev_for_series)


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

import ipdb; ipdb.set_trace();
