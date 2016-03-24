import numpy as np
import pandas as pd
import os, glob
import multiprocessing
cores = multiprocessing.cpu_count()
pool = multiprocessing.Pool(cores)

# create station-information lookup dict based on C/A and Unit
cols_stations = ['UNIT','CA', 'STATION', 'LINENAME', 'DIVISION']
df_stations_lookup = pd.read_csv("Remote-Booth-Station.csv", header=None, names=cols_stations)

keys = df_stations_lookup.CA + df_stations_lookup.UNIT
values = df_stations_lookup.loc[:,['STATION','LINENAME','DIVISION']].to_dict('records')
station_lookup = dict(zip(keys,values))

def lookup(key, col):
    '''lookup function to use with pandas to which you can partially apply which key you'd like to lookup'''
    try:
        return station_lookup[key][col]
    except KeyError as err:
        return np.nan

cols_old = [
    'CA','UNIT','SCP',
    'DATE1','TIME1','DESC1','ENTRIES1','EXITS1',
    'DATE2','TIME2','DESC2','ENTRIES2','EXITS2',
    'DATE3','TIME3','DESC3','ENTRIES3','EXITS3',
    'DATE4','TIME4','DESC4','ENTRIES4','EXITS4',
    'DATE5','TIME5','DESC5','ENTRIES5','EXITS5',
    'DATE6','TIME6','DESC6','ENTRIES6','EXITS6',
    'DATE7','TIME7','DESC7','ENTRIES7','EXITS7',
    'DATE8','TIME8','DESC8','ENTRIES8','EXITS8']
cols_new = [
    'CA','UNIT','SCP', 'STATION','LINENAME','DIVISION',
    'DATE','TIME','DESC','ENTRIES','EXITS']
cols_final = cols_new + ['DATETIME']

def save_df(df, filename):
    '''save dataframe as pickled obj to formatted/ directory'''
    # construct the output filename
    basename = os.path.basename(filename)
    outname = os.path.join('formatted', basename)
    # save pickled dataframe
    df.to_pickle(outname)

def read_new(filename):
    '''read new-MTA-format file into pandas.dataframe'''
    # TODO remove header
    df = pd.read_csv(filename, header=1, names=cols_new)
    # parse date and time into DAY and DATETIME
    datetime = df.DATE + ' ' + df.TIME
    df['DATETIME'] = pd.to_datetime(datetime, format='%m/%d/%Y %H:%M:%S')
    # TODO lookup station name?
    return df

def read_old(filename):
    '''read old-MTA-format file into pandas.dataframe. returns in new-MTA-format'''
    # use old column names defined in ts_Field_Description_pre-10-18-2014.txt
    df_old = pd.read_csv(filename, header=None, names=cols_old)

    # add missing station-information columns
    station_lookup_keys = df_old.CA + df_old.UNIT
    df_old['STATION']  = station_lookup_keys.apply(lookup, col='STATION')
    df_old['LINENAME'] = station_lookup_keys.apply(lookup, col='LINENAME')
    df_old['DIVISION'] = station_lookup_keys.apply(lookup, col='DIVISION')

    def extract_column_range(i):
        '''not every row has all columns filled so this function pulls out 
        those rows who are not null for col 'i', and pre-pends CA,UNIT,SCP'''
        c = str(i)
        cols_select = ['CA','UNIT','SCP','STATION','LINENAME','DIVISION',
            'DATE'+c,'TIME'+c,'DESC'+c,'ENTRIES'+c,'EXITS'+c]
        df_notnull = df_old[df_old['DATE'+c].notnull()].loc[:,cols_select]
        # re-name columns to new-MTA-format
        df_notnull.columns = cols_new
        return df_notnull

    # restructure old format data to have one data point per row
    df_restructured = pd.concat(extract_column_range(i) for i in range(1,9)) 

    # make DATETIME column from date and time columns 
    datetime = df_restructured.DATE + ' ' + df_restructured.TIME
    df_restructured['DATETIME'] = pd.to_datetime(datetime, format='%m-%d-%y %H:%M:%S', coerce=True)

    # reorder columns to final output format
    df_restructured = df_restructured.loc[:,cols_final]
    return df_restructured


def subtract_prev(rows):
    if len(rows) != 2: return np.nan
    prev, curr = rows
    # prev > curr means the odometer has been reset
    return rows[1] - rows[0] if prev > curr else curr
subtract_prev_for_series = lambda ser: ser.rolling(window=2).apply(subtract_prev)


def is_old_format(filename):
    return os.path.basename(filename) < 'turnstile_141018.txt'

# load and reformat raw data and save the dataframes out to disk
# IMPORTANT: saving the reformatted dataframes to disk allows for faster loading in the future.
#            reformatting and writing out to disk takes around 10 minutes on my macbook pro.
if False:
    turnstile_files = glob.glob(os.path.join('data', '*.txt'))
    #turnstile_files = [f for f in turnstile_files if not is_old_format(f)]
    #turnstile_files = [f for f in turnstile_files if f == 'data/turnstile_100807.txt']

    for f in turnstile_files:
        print 'old' if is_old_format(f) else 'new', f
        df = read_old(f) if is_old_format(f) else read_new(f)
        # now that we have a common format, we're going to augment the data
        # with features that will be useful down the road

        save_df(df,f)

    def read_and_save_file(f):
        print 'old' if is_old_format(f) else 'new', f
        df = read_old(f) if is_old_format(f) else read_new(f)

    map(read_and_save_file, turnstile_files)
