#!/usr/bin/env python3


import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb
import library as lib
import tabulate
import argparse
from scipy import stats

tests = lib.complexity_tests 
rows = [t.upper() for t in tests]

#Make dictionary that relates every possible test pair
td =  {t:tests for t in tests}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output')
    parser.add_argument('-d', '--dataframe')
    parser.add_argument('-t', '--table_format', default='simple', choices=tabulate.tabulate_formats)
    parser.add_argument('-b', '--bit', default=1, type=int)
    args = parser.parse_args()

    #Skip if file is already there
    if os.path.isfile(args.output):
        return

    #Open dataframes
    df = pd.read_pickle(args.dataframe)
    table = []
    #For each test pair
    for ct,tl in td.items():
        row = []
        for t in tl:
            #"Plot" tests on a x and y axis
            x = df[t][args.bit] - df[t][0]
            y = df[ct][args.bit] - df[ct][0]
            #Get correlation
            row.append(np.corrcoef(x,y)[0][1])
        table.append(['%.2g' % r for r in row])

    
    #Dump table
    columns = rows 
    with open(args.output, 'w') as f:
        f.write(tabulate.tabulate(table, headers=columns, showindex=rows, tablefmt=args.table_format))
    


if __name__ == "__main__":
    main()
