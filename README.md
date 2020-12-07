# Evaluation of Statistical Tests for Detecting Storage-Based Covert Channels

This is the code used to perform the experiment described is an eponymous
research paper. It consists of the following files:

*  **carrier.py**: Extracts header fields from captured network packets.
*  **inject.py**: Embeds a message into the extracted header fields and
   applies tests to the resulting data.
*  **table.py**: Creates a table of the effect sizes of each test.
*  **table_corr.py**: Creates a table of the correlation between two tests.
*  **table_reg.py**: Creates a table of the accuracy of a logistic
   regression classifier using some combination of the tests.
*  **library.py**: Not meant to be executed, contains some definitions
   shared by the other files.
*  **run.sh**: Runs all the above python files to generate the tables used
   the paper among others.

Also included is the message that was embedded into the header fields. The
captured packets are not included but can be retrieved
[here](https://www.stratosphereips.org/datasets-normal). The code expects to
find PCAP files with a `.pcap` file extension in a top-level folder named
`pcap/`. By default the output is stored in a folder called `data/`; a
compressed version of this folder with all the tables is included herein.
A list of the non-standard libraries that must be installed in order to run
this code can be found in `requirements.txt`.  

There are also 3 files in the `graph/` folder that are used to generated graphs
from the dataframes output by **inject.py**. These are not used in the original
conference paper but are included in the subsequent thesis. The files in
question are:

* **graph_test.py**: Shows the effect sizes for different traces.
* **graph_comb.py**: Shows correlations between different tests.
* **graph_clust.py**: Shows predictions of a 2-D logistic regression detector.
