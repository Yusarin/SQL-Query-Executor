Disk Based Query System
- uncomment helperAGAIN.py from line 683-752, comment helperAGAIN.py from line 755-829
- uncomment get_query_result.py line 16, comment get_query_result.py line 18
- In Proprocess_disk.py, change line 7 for needed csv file names

In Python Shell, use the following command.
import sys
sys.argv = ['Preprocess_disk.py', 'arg']
exe(open('Preprocess_disk.py')

input = 'SELECT .. FROM.. WHERE' ## write query here
sys.argv = [‘get_query_result.py', input]
execfile(‘get_query_result.py’)


Main-Memory Based Query System
- uncomment helperAGAIN.py from line 755-829 , comment helperAGAIN.py from line 683-752
- uncomment get_query_result.py line 18, comment get_query_result.py line 16
- In Proprocess.py, change line 7 for needed csv file names

In Python Shell, use the following command.
import sys
sys.argv = ['Preprocess.py', 'arg']
exe(open('Preprocess.py').read())

input = 'SELECT .. FROM.. WHERE' ## write query here
sys.argv = [‘get_query_result.py', input]
exec(open(‘get_query_result.py’).read())