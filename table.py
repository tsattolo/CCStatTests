#!/usr/bin/env python3

import sys, os
import pandas as pd
import pdb
from itertools import chain
import argparse
import library as lib
import tabulate

tests = lib.all_tests 
rows = [lib.full_test_names[t] for t in tests]
variations = ['Y', 'N']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output')
    parser.add_argument('-d', '--dataframes', nargs='+')
    parser.add_argument('-t', '--table_format', default='simple', choices=tabulate.tabulate_formats)
    parser.add_argument('-b', '--bit', default=1, type=int)
    args = parser.parse_args()

    #Skip if file is already there
    if os.path.isfile(args.output):
        return

    #Figure out display details 
    columns = ['%d-bit Trace' % args.bit, 'Minimum', 'Min. Index']
    undef_symbol = '$\\perp$' if 'latex' in args.table_format else 'nan'
    n_cols = len(columns)

    #Open dataframes
    df_list = [pd.read_pickle(e) for e in args.dataframes]
    n_df = len(df_list)

    #Works for one or two dataframes as input, if there are two it's assumed that they are
    #enrcypted and unencrypted versions of the same thing.
    if n_df == 1:
        table = []
        rows_wb = rows
        columns_wb = columns
    elif n_df == len(variations):
        pre = '\hline\n' if 'latex' in args.table_format else ''
        rows_wb = ['Encrypted?'] +  [pre + rows[0]] + rows[1:]
        columns_wb = chain(*[[c] + ['']*1 for c in columns])     
        table = [variations * n_cols]
    else:
        assert False, 'Number of dataframes does not match number of variations'

    for t in tests:
        row = []
        for df in df_list:
            dft = df[t]
            #Exclude carrier results
            dfnz = dft.loc[:,1:]
            # Subtract carrier column from the others
            dfnz -= pd.concat([dft[0]] * len(dfnz.columns), axis='columns').values 
            #Get joint standard deviations (for all traces)
            sd = ((dfnz.var() + dft[0].var())/2).pow(0.5)
            #Get effect sizes (aka Cohen's D)
            cohend = (dfnz.mean() / sd).abs()
            #Sometimes results in not a number.
            if (cohend != cohend).any():
                vals = [undef_symbol] * n_cols
            else:
                vals = ['%.3g' % cohend[args.bit], '%.3g' % cohend.min(), '%d' % cohend.idxmin()]
            row.append(vals)
        table.append(list(chain(*zip(*row))))

    #Dump results
    with open(args.output, 'w') as f:
        f.write(tabulate.tabulate(table, headers=columns_wb, showindex=rows_wb, tablefmt=args.table_format))
    

if __name__ == "__main__":
    main()
