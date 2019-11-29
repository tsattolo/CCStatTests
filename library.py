complexity_tests = ['lzma', 'lz77', 'lz78', 'lzc', 'foe', 'cce', 'rep']
distribuitonal_tests = ['cov', 'ks', 'wcx', 'spr', 'reg']
all_tests =  complexity_tests + distribuitonal_tests

full_test_names= {
        'lzma' : 'LZMA Compression',
        'lz77' : 'LZ77 Compression',
        'lz78' : 'LZ78 Compression',
        'lzc'  : 'Lempel-Ziv Complexity',
        'foe'  : 'First-Order Entropy',
        'cce'  : 'Corr. Cond. Entropy',
        'rep'  : 'Repetition',
        'cov'  : 'Autocovariance',
        'ks'   : 'Kolm.-Smirnov Test',
        'wcx'  : 'Wilcoxon Signed Rank',
        'spr'  : 'Spearman Correlation',
        'reg'  : 'Regularity'
        }


field_sizes = { 
                'ip_id'   :   16,
                'ip_ttl'  :   8,
                'tcp_isn' :   32
              }
                
seed = 7
