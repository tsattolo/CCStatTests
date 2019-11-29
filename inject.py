#!/usr/bin/env python3

from scapy.all import *
import sys, os
import pdb
import lzma
from functools import partial
import pandas as pd
import numpy as np
import argparse
import pickle as pkl
import lz78
import math
import library as lib
from itertools import chain
from scipy import stats
from Crypto.Cipher import Salsa20
from Crypto.Cipher import AES
sys.path.append(os.path.join(sys.path[0],'lz77','src'))
from LZ77 import LZ77Compressor
from lempel_ziv_complexity import lempel_ziv_complexity

lz77 = LZ77Compressor() 

tests = lib.all_tests 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', default='message.txt')
    parser.add_argument('-i', '--iterations', type=int)
    parser.add_argument('-o', '--output')
    parser.add_argument('-c', '--carrier_file', default='')
    parser.add_argument('-n', '--nbytes', type=int, default=1000)
    parser.add_argument('-j', '--jump', type=int, default=1)
    parser.add_argument('-f', '--field_size', type=int, default=16)
    parser.add_argument('--encrypt', action='store_true')
    parser.add_argument('--eq_space', action='store_true')
    args = parser.parse_args()
                
    #Skip if file is already there
    if os.path.isfile(args.output):
        return

    #Get carrier and make sure it's arguments are compatible
    with open(args.carrier_file, 'rb') as f:
        real_id_iter, dummy_id_iter, carrier_args = pkl.load(f)
    verify_carrier_args(args, carrier_args)

    #Read message
    with open(args.message, 'rb') as f:
        msg = f.read(args.nbytes)

    # Encrypt message
    if args.encrypt:
        key = b'pTuL7zxs6e3dAFMioJoS01OhBrO9SXGw'
        if args.nbytes % AES.block_size == 0:
            cipher = AES.new(key, AES.MODE_CBC, iv=b'GjfNgnikI8eAShCH')
        else:
            cipher = Salsa20.new(key=key, nonce=b'lj7BbRlB')
        msg = cipher.encrypt(msg)

    # Split message into bits
    bits = [d for c in msg for d in '{0:08b}'.format(c)]
    nbits =  len(bits)

    # Randomly determine which elements will contain covert info
    np.random.seed(10 + lib.seed)
    jumps = np.ones(nbits, dtype=int) if args.jump == 1 else np.random.randint(1, args.jump, size=nbits)

    #Truncate carriers to size required
    ids_needed = np.sum(jumps) 
    real_id_iter = [a[:ids_needed] for a in real_id_iter]
    dummy_id_iter = [a[:ids_needed] for a in dummy_id_iter]

    #Covert field size from bits to bytes
    field_bytes = int(math.ceil(args.field_size / 8))
    res_dict = {t:[] for t in tests}
    for i in range(args.iterations):
        #Embed covert info
        traces = inject(args.field_size, real_id_iter[i], bits, jumps, eq_space=args.eq_space)
        
        #Perform tests
        add_test(res_dict, 'lzma', check_compress, traces, field_bytes)
        add_test(res_dict, 'rep', check_repeat, traces)
        add_test(res_dict, 'foe', check_entropy, traces)
        add_test(res_dict, 'cov', check_covar, traces)
        add_test(res_dict, 'lz78', check_lz78_compress, traces, field_bytes)
        add_test(res_dict, 'lz77', check_lz77_compress, traces, field_bytes)
        add_test(res_dict, 'ks', check_ks, traces, dummy_id_iter[i])
        add_test(res_dict, 'wcx', check_wilcoxon, traces, dummy_id_iter[i])
        add_test(res_dict, 'spr', check_spearman, traces, dummy_id_iter[i])
        add_test(res_dict, 'reg', check_regularity, traces)
        add_test(res_dict, 'cce', check_cce, traces)
        add_test(res_dict, 'lzc', check_lzc, traces, field_bytes)

    
    #Output as dataframe
    df_dict = dict([(k, pd.DataFrame(v).T) for k, v in res_dict.items()])
    df = pd.concat(df_dict).T
    df.to_pickle(args.output)
    
def inject(field_size, carrier, message_bits, jumps, whole_carrier=True, eq_space=False):
    traces = []
    nbits = len(message_bits)
    for bp in range(field_size + 1):
        #Get bits that will be embed in each element
        pktm = get_pktm(message_bits, bp) if not bp == 0 else [0]*nbits

        if whole_carrier and not eq_space:
            pktm.extend([0] * (nbits - len(pktm)))
        elif eq_space:
            pktm = list(chain(*[[e] + [0]*(bp -1) for e in pktm]))

        #Embed info
        jump_mult = 1 if bp == 0 else bp
        pktm = list(chain(*[[e] + [0]*(j - 1) for e, j in zip(pktm, jumps * jump_mult)]))
        mask = ~((1 << bp) - 1)
        trace  = [(b & mask) | m for b, m in zip(carrier, pktm)]
        traces.append(trace)
    return traces

def add_test(res_dict, key, func, traces, *args):
    res_dict[key].append([func(trace, *args) for trace in traces])
    return
    
def check_compress(trace, field_bytes):
    btr = b''.join([e.to_bytes(field_bytes, byteorder='big') for e in trace])
    return len(lzma.compress(btr)) / len(btr)

def check_lz78_compress(trace, field_bytes):
    btr = b''.join([e.to_bytes(field_bytes, byteorder='big') for e in trace])
    return len(lz78.compress(btr)) / len(btr)

def check_lz77_compress(trace, field_bytes):
    btr = b''.join([e.to_bytes(field_bytes, byteorder='big') for e in trace])
    return len(lz77.compress(btr)) / len(btr)

def check_repeat(trace):
    return len(set(trace)) / len(trace)

def check_entropy(trace):
    _, dist = np.unique(trace, return_counts=True)
    return stats.entropy(dist)

def check_covar(trace):
    return onepass_covar(trace)


def check_wilcoxon(trace, dummy_carrier):
    return stats.wilcoxon(trace, dummy_carrier, zero_method='zsplit')[0]


def check_spearman(trace, dummy_carrier):
    return stats.spearmanr(trace, dummy_carrier)[0]

def check_ks(trace, dummy_carrier):
    return stats.ks_2samp(trace, dummy_carrier)[0]


def check_regularity(trace):
    return regularity(trace)

def check_cce(trace):
    return cce(trace)

def check_lzc(trace, field_bytes):
    btr = b''.join([e.to_bytes(field_bytes, byteorder='big') for e in trace])
    return lempel_ziv_complexity(btr)

def check_byte_entropy(trace, field_bytes):
    btr = list(chain(*[e.to_bytes(field_bytes, byteorder='big') for e in trace]))
    _ , dist = np.unique(btr, return_counts=True)
    return stats.entropy(dist)

def check_byte_repeat(trace, field_bytes):
    btr = list(chain(*[e.to_bytes(field_bytes, byteorder='big') for e in trace]))
    return len(set(btr)) / len(btr)

def cce(tr):
    N = len(tr)
    e = [0]
    cce = []
    for L in range(1,N):
        space = [tuple(tr[i:i+L]) for i in range(N-L+1)]
        un,cnt = np.unique(space, return_counts=True, axis=0)
        e.append(stats.entropy(cnt))
        ceL = e[L] - e [L-1]
        percL = un.shape[0] / len(space)
        cce.append(ceL + percL*e[1])
        # print(e[L], percL, ceL, cce[L-1])
        if percL == 1.0: 
            break
    return min(cce)



def regularity(tr):
    n = int(np.ceil(np.sqrt(len(tr))))
    ll = [tr[i:i + n] for i in range(0, len(tr), n)]
    stds = [np.std(l) for l in ll]
    combs = []
    for j in range(len(stds)):
        for i in range(j):
            combs.append(np.abs(stds[i] - stds[j]) / stds[i])
    return np.std(combs)

def onepass_covar(tr, d=1):
    my = C = 0
    mx = np.mean(tr[:d])
    for i in range(len(tr) - d):
        n = i + 1
        dx = tr[i + d] - mx
        mx += dx / n
        my += (tr[i] - my) / n
        C += dx * (tr[i] - my)
    res = C / (len(tr) - d)
    return res

def get_pktm(bits, bits_per): 
    pktb = [bits[i:i+bits_per] for i in range(0, len(bits), bits_per)]
    return [int(''.join(m), 2) for m in pktb]

def verify_carrier_args(this, carrier):
    assert this.iterations <= carrier.iterations
    assert this.nbytes * this.jump <= carrier.nbytes * carrier.jump
    assert this.field_size <= lib.field_sizes[carrier.field]

    

if __name__ == "__main__":
    main()
