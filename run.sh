#!/bin/bash

base_folder='data/'
table_format='simple'
table_loc='tables/'
frame_loc='dataframes/'
filetype='txt'

#Create carriers

carrier_folder=$base_folder'carriers/'
mkdir -p $carrier_folder

./carrier.py -f 'ip_id'   -n 256 -i 1000 -o $carrier_folder'ip_id.pkl' & 
./carrier.py -f 'ip_ttl'  -n 256 -i 1000 -o $carrier_folder'ip_ttl.pkl' & 
./carrier.py -f 'tcp_isn' -n 64  -i 100  -o $carrier_folder'tcp_isn1.pkl' &
./carrier.py -f 'tcp_isn' -n 256 -i 25   -o $carrier_folder'tcp_isn2.pkl' &

wait

#Inject
prepare () {
    framefolder=$base_folder$frame_loc$field'/'
    carrier=$carrier_folder$field'.pkl'
    tablefolder=$base_folder$table_loc$field'/'
    dfs=()
    mkdir -p $framefolder
    mkdir -p $tablefolder
}

run_internal () {
    ./inject.py -c $carrier -n $nbytes -i $iter -f $fieldsize -o $framefolder$nbytes'.df' &
    ./inject.py -c $carrier -n $nbytes -i $iter -f $fieldsize -o $framefolder$nbytes'E.df' --encrypt &
    wait
    ./table.py -b $bit -t $table_format -d $framefolder$nbytes'E.df' $framefolder$nbytes'.df' -o $tablefolder$nbytes'eff.'$filetype &
    ./table_corr.py -b $bit -t $table_format -d $framefolder$nbytes'.df' -o $tablefolder$nbytes'corr.'$filetype &
}

field='ip_id'
fieldsize=16
iter=1000
bit=1
msg_sizes=(256 64 16 4 1)
prepare
for nbytes in ${msg_sizes[*]} 
do
    run_internal&
    dfs+=($framefolder$nbytes'.df') 
done
wait
./table_reg.py -b $bit -t $table_format  -n ${msg_sizes[*]} -d ${dfs[*]} -o $tablefolder'detector.'$filetype & 

field='ip_ttl'
fieldsize=8
iter=1000
bit=8
msg_sizes=(256 64 16 4 1)
prepare
for nbytes in ${msg_sizes[*]} 
do
    run_internal&
    dfs+=($framefolder$nbytes'.df') 
done
wait
./table_reg.py -b $bit -t $table_format  -n ${msg_sizes[*]} -d ${dfs[*]} -o $tablefolder'detector_1bit_trace.'$filetype & 

field='tcp_isn1'
fieldsize=32
iter=100
bit=1
msg_sizes=(64 16 4 1)
prepare
for nbytes in ${msg_sizes[*]} 
do
    run_internal&
    dfs+=($framefolder$nbytes'.df') 
done
wait
./table_reg.py -b $bit -t $table_format  -n ${msg_sizes[*]} -d ${dfs[*]} -o $tablefolder'detector.'$filetype & 

field='tcp_isn2'
fieldsize=32
iter=25
bit=1
msg_sizes=(256 64 16 4 1)
prepare
for nbytes in ${msg_sizes[*]} 
do
    run_internal&
    dfs+=($framefolder$nbytes'.df') 
done
wait
./table_reg.py -b $bit -t $table_format  -n ${msg_sizes[*]} -d ${dfs[*]} -o $tablefolder'detector.'$filetype & 
