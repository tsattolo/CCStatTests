#!/usr/bin/env python3

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb
from scipy import stats

# Generate graphs showing effect size of tests for different traces
# First argument should point to a folder containing appropriate dataframes (output of inject.py)
# Second argument in the folder where generated graphs are stored

# Test included, each key is compared to each test in the adjoining list
tests = {'lz77':['lzma', 'foe', 'lz78', 'rep', 'lz77'], 
         'rep':['lzma', 'foe', 'lz78', 'rep', 'lz77']}

# Dataframes used, must exist in folder provided as 1st argument
filenames = ['256.df', '64.df', '16.df', '4.df', '1.df']
# Number of bits for labelling graphs for each dataframe
nbits = [256, 64, 16, 4, 1]

def main():
    df_files = [sys.argv[1] + fn for fn in filenames]
    df_list = [pd.read_pickle(e) for e in df_files]

    folder = sys.argv[2]
    os.makedirs(folder, exist_ok=True)

    for df,nb in zip(df_list, nbits):
        for ct,tl in tests.items():
            for t in tl:
                plt.figure()
                x = df[t][1] - df[t][0]
                y = df[ct][1] - df[ct][0]
                
                plt.scatter(x, y)
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                plt.plot(x, slope*x + intercept)
                
                # plt.savefig('%.eps' %  t) 
                plt.savefig('%s/%d_%s_%s.png' %  (folder, nb, t, ct)) 
                plt.savefig('%s/%d_%s_%s.pdf' %  (folder, nb, t, ct)) 
                plt.close()

                print('Corr %s %s: %f' % (t, ct, np.corrcoef(x,y)[0][1]))

if __name__ == "__main__":
    main()
