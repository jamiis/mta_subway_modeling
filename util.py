import os

def save_df(df, filename, directory):
    '''save dataframe as pickled obj to directory/ directory'''
    # make dir if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    # construct the output filename
    basename = os.path.basename(filename)
    outname = os.path.join(directory, basename)
    # save pickled dataframe
    df.to_pickle(outname)

def perc_of_total_data(df_new,df_old):
    return float(df_new.shape[0]) / df_old.shape[0]

in_range = lambda f: f < 'cleaned/turnstile_100619.txt' or f > 'cleaned/turnstile_160220.txt.' 
is_above = lambda f: f > 'cleaned/turnstile_160100.txt.' 
