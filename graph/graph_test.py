#!/usr/bin/env python3


import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import pdb
from tabulate import tabulate

# Generate graphs showing effect size of tests for different traces
# First argument should point to a folder containing appropriate dataframes (output of inject.py)
# Second argument in the folder where generated graphs are stored

# List of tests included
tests = ['lzma', 'lz77', 'lz78', 'lzc', 'foe', 'cce', 'rep', 'cov', 'ks', 'wcx', 'spr', 'reg']

# Dataframes used, must exist in folder provided as 1st argument
filenames = ['1.df',  '16.df',  '256.df']
# Point style and label for each dataframe
styles = ['r.', 'g+', 'bx'] 
names = ['1-byte Message',  '16-byte Message',  '256-byte Message'] 

plt.rcParams.update({'font.size': 16})
plt.rcParams.update({'figure.autolayout': True})

rows = [
        'LZMA Compression',
        'LZ77 Compression',
        'LZ78 Compression',
        'Lempel-Ziv Complexity',
        'First-Order Entropy',
        'Corrected Conditional Entropy',
        'Repetition',
        'Autocovariance',
        'Kolmogorov-Smirnov Test',
        'Wilcoxon Signed Rank',
        'Spearman Correlation',
        'Regularity'
        ]

columns = ['1-bit Trace Effect Size', 'Minimum Effect Size', 'Minimum Effect Size Trace']

def main():
    df_files = [sys.argv[1] + fn for fn in filenames]

    df_list = [pd.read_pickle(e) for e in df_files]
    assert(len(styles) >= len(df_list))

    table = []
    max_xtick_labels = 16
    for t in tests:
        plt.figure()
        for (df, style, name) in zip(df_list, styles, names):
            dft = df[t]
            dfnz = dft.loc[:,1:]
            dfnz -= pd.concat([dft[0]] * len(dfnz.columns), axis='columns').values # Subtract zero column from the others

            
            sd = ((dfnz.var() + dft[0].var())/2).pow(0.5)
            cohend = (dfnz.mean() / sd).abs()
            if '1-byte' in name: cohend = cohend[:8]
           
            table.append([cohend[1], cohend.min(), cohend.idxmin()])
            
            plt.plot(cohend, style, label=name)
            plt.xticks(dfnz.columns[::max(1,round((len(dfnz.columns)/max_xtick_labels)))])
            plt.legend()
            plt.ylim(0,20)
            plt.xlabel('Bits / Element')
            plt.ylabel('Effect Size')

        folder = sys.argv[2]
        os.makedirs(folder, exist_ok=True)
        plt.savefig('%s/%s.pdf' %  (folder, t)) 
        plt.savefig('%s/%s.png' %  (folder, t)) 
    
if __name__ == "__main__":
    main()
