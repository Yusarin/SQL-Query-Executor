
Proprocess.py: Pre-indexing for each csv files. Edit Preprocess.py to pre-index needed csv files. In line 7, change csv filenames if needed.
helperAGAIN.py: helper functions for the query system.
get_query_result.py: main function for running the query system.


HOW TO RUN:
In terminal, use the following command:

python3 Proprocess.py ## generateing needed indexing files
python3 get_query_result.py 'SELECT XX FROM XXX WHERE XXX' ## get query result
