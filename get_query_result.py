from helperAGAIN import *
import sys
t1 = time.time()
input = sys.argv[1]
attr,need_attributes,eval_attributes,connection, listOfSelection, selection_rename, listOfTablesInFrom, table_name_called, Conditions, eval_from_table, join, merge_on_attributes, distinct = deserializaiton(input)
index, keylist, shape = find_index_order(listOfTablesInFrom, attr, table_name_called, merge_on_attributes, eval_attributes)
t2 = time.time()
print("read query time: ", t2-t1)
selected_row = Eval(index, keylist, shape, eval_attributes, Conditions,eval_from_table, join, merge_on_attributes)
t3 = time.time()
print("select row time: ", t3-t2)
pos = Combine_Condition(selected_row, connection, listOfTablesInFrom, eval_from_table, join, shape)
t4 = time.time()
print("combine pos time: ", t4-t3)
final_R = WHERE(pos, listOfTablesInFrom, join, attr, table_name_called, shape, need_attributes, merge_on_attributes, connection)
t5 = time.time()
print("perfom join time: ", t5-t4)
A = SELECT(listOfSelection, selection_rename, final_R, join, merge_on_attributes, distinct)
t6 = time.time()
print("final selection time: ", t6-t1)
print(A)
print("Total row number is: ", A.shape[0])
###################
