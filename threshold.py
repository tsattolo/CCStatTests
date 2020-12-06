#!/usr/bin/env python3

import sys
import pandas as pd
import numpy as np
import pdb
from sklearn.linear_model import LogisticRegression
from scipy import stats

test = 'rep'
n_iter = 100

# Determine optimal threshold for detecting a covert channel
# Works for one test on one header field with one message size
# The appropriate dataframe (output from inject.py) should
# be supplied as the only command-line argument.

def main():
    df_file = sys.argv[1]
    df = pd.read_pickle(df_file)
    
    xp = (1 - df[test][1]) * 32
    xn = (1 - df[test][0]) * 32

    examples = np.concatenate((np.array(xp), np.array(xn))).reshape(-1,1) 
    labels = np.concatenate((np.ones(len(xp)), np.zeros(len(xp))))

    N = len(examples)
    split = int(0.7*N)
    assert(len(examples) == len(labels))

    acclist = []
    threshlist = []

    for i in range(n_iter):
        p = np.random.permutation(N)
        
        train_ex = examples[p][:split].copy()
        train_lb = labels[p][:split].copy()
        test_ex = examples[p][split:].copy()
        test_lb = labels[p][split:].copy()

        clf = LogisticRegression(solver='lbfgs').fit(train_ex,  train_lb)
        
        accuracy = clf.score(test_ex, test_lb)
        acclist.append(accuracy)

        predictions = clf.predict(np.array(range(32)).reshape(-1,1))
        threshlist.append(np.argmax(np.diff(predictions)) + 1)

    print('mean: %f' % np.mean(acclist))
    print('std:  %f' % np.std(acclist))
    print('threshold:  %f' % np.mean(threshlist))

if __name__ == "__main__":
    main()
