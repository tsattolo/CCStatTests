#!/usr/bin/env python3

from functools import partial
from scapy.all import *
import pdb, sys, os
import numpy as np
import pickle as pkl
import argparse
import library as lib

# Dataset has 121733 TCP ISN and 9275031 IP ID

def main():

    field_fns = { 
                 'ip_id'   :   get_ip_id,
                 'ip_ttl'  :   get_ip_ttl,
                 'tcp_isn' :   get_tcp_isn
                }
                
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default='carrier.pkl')
    parser.add_argument('-p', '--pcap_folder', default='pcap/')
    parser.add_argument('-f', '--field', choices=field_fns.keys(), default='ip_id')
    parser.add_argument('-i', '--iterations', type=int, default=1000)
    parser.add_argument('-j', '--jump', type=int, default=1)
    parser.add_argument('-n', '--nbytes', type=int, default=256)
    args = parser.parse_args()

    #Skip if file is already there
    if os.path.isfile(args.output):
        return

    #Determine how many elements are needed 
    ids_per_iter = args.nbytes * args.jump * 8 * 2 #for dummy
    ids_total = ids_per_iter * args.iterations

    all_ids = []
    
    #Use pcap files in pcap folder
    pcap_files = [args.pcap_folder + pf for pf in os.listdir(args.pcap_folder) if pf.endswith('.pcap')]
    #Stop when we have enough elements
    stop_filter = lambda _: len(all_ids) == ids_total
    
    sniff(offline=pcap_files, 
         prn=partial(field_fns[args.field], all_ids), 
         store=0, 
         stop_filter= stop_filter)
    
    #Abort if there weren't enough packets
    assert stop_filter(None), '%d ids available, %d needed' % (len(all_ids), ids_total)

    #Randomize across iterations:
    #Each iteration gets a block off fields from a random locations in the dataset, 
    #but the elements of each block are sequnetial in the original data.
    np.random.seed(20 + lib.seed)
    id_iter = [all_ids[i*ids_per_iter:(i+1)*ids_per_iter] for i in range(args.iterations)]
    np.random.shuffle(id_iter)

    #Get real and dummy block for each iteration, some tests require dummy ids for comparison
    real_id_iter = [a[:len(a) // 2] for a in id_iter]
    dummy_id_iter = [a[len(a) // 2:] for a in id_iter]

    #Sanity check
    assert(all([len(a) == ids_per_iter / 2 for a in real_id_iter + dummy_id_iter]))
    
    #Dump file and include commad line arguments so inject fails fast when using wrong carrier
    with open(args.output, 'wb') as f:
       pkl.dump((real_id_iter, dummy_id_iter, args), f)

def get_ip_id(ids, pkt):
    if IP in pkt:
        ids.append(pkt['IP'].fields['id'])

def get_ip_ttl(ids, pkt):
    if IP in pkt:
        ids.append(pkt['IP'].fields['ttl'])

def get_tcp_isn(ids, pkt):
    # S flag means this is the start segment
    if TCP in pkt and pkt['TCP'].flags == 'S':
        ids.append(pkt['TCP'].seq)

if __name__ == "__main__":
    main()
