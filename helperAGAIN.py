import csv
import pandas as pd
import numpy as np
import operator
import re
import time
import json
pd.options.mode.chained_assignment = None  # default='warn'

def parentheses(conditions,connections):
	length=len(conditions)
	newConditions=[None for y in range(length)]
	newConnections=[None for y in range(length-1)]
	pairOfConditions=[[None for y in range(2)] for x in range(length+1)]
	pairOfConnections=[[None for y in range(2)] for x in range(length)]
	for i in range(length):
			numberOfLeftParen=conditions[i].count("(")
			numberOfRightParen=conditions[i].count(")")
			if i==0:
				pairOfConditions[i]=[1+numberOfLeftParen,0]
				pairOfConditions[i+1]=[pairOfConditions[i][0]-numberOfRightParen-0.01,i+1]
				pairOfConnections[i]=[pairOfConditions[i][0]-numberOfRightParen-0.005,i]
			else:
				pairOfConditions[i][0]+=numberOfLeftParen-0.01
				pairOfConditions[i+1]=[pairOfConditions[i][0]-numberOfRightParen-0.01,i+1]
				pairOfConnections[i]=[pairOfConditions[i][0]-numberOfRightParen-0.005,i]
	pairOfConditions=pairOfConditions[:length]
	pairOfConnections=pairOfConnections[:length-1]
	#print(pairOfConditions)
	#print(pairOfConnections)
	newPairOfConditions=sorted(pairOfConditions,key=lambda x:-x[0])
	newPairOfConnections=sorted(pairOfConnections,key=lambda x:-x[0])
	#print(newPairOfConditions)
	#print(newPairOfConnections)
	for i in range(length):
		line=conditions[newPairOfConditions[i][1]].replace("(","")
		newConditions[i]=line.replace(")","")
	for i in range(length-1):
		newConnections[i]=connections[newPairOfConnections[i][1]]
	return newConditions,newConnections


def split_input(input):
    sfw = re.split("SELECT|FROM|WHERE", input)
    selectClause = (sfw[1].replace(' ', ''))
    fromClause = sfw[2].replace(' ', '')

    if len(sfw) == 4:
        whereClause = sfw[3].strip()
    else:
        whereClause = True
    if 'DISTINCT' in selectClause:
        distinct = True
        selectClause =re.split('DISTINCT',selectClause)[1]
        listOfSelection =selectClause.split(",")

    else:
        distinct = False
        listOfSelection = selectClause.split(",")

    listOfTablesInFrom = fromClause.split(",")

    rename = []
    for i in range(len(listOfTablesInFrom)):
        if listOfTablesInFrom[i].split('csv')[1] != '':
            rename.append(listOfTablesInFrom[i].split('csv')[1])
            listOfTablesInFrom[i] = listOfTablesInFrom[i][
                                    0:(len(listOfTablesInFrom[i]) - len(listOfTablesInFrom[i].split('csv')[1]))]
    return listOfSelection, listOfTablesInFrom, whereClause, rename, distinct


def split_conditions(whereClause, connection, where_conditions):
    Conditions = re.split('(AND|OR)', whereClause)
    for i in range(1, len(Conditions), 2):
        connection.append(Conditions[i])
    eval_attributes = {}
    actual_eval = {}
    eval_from_table = {}
    for i in range(0, len(Conditions), 2):
        where_conditions.append(Conditions[i].strip())
        eval_attributes[int(i / 2)] = []
        actual_eval[int(i / 2)] = []
        eval_from_table[int(i / 2)] = []
    newwhere_conditions, newconnection = parentheses(where_conditions, connection)
    return newwhere_conditions, newconnection, eval_attributes, actual_eval, eval_from_table


def find_attributes(table_name_called, listOfTablesInFrom,listOfSelection, where_conditions, eval_attributes, actual_eval, eval_from_table):
    attr = {}
    need_attributes = {}
    selection_rename = []
    for t in range(len(table_name_called)):
        attr[table_name_called[t]] = []
        need_attributes[table_name_called[t]] = []
        # filename = name + '.csv'
        header = list(pd.read_csv(listOfTablesInFrom[t], nrows=1).columns.values)
        upper_header = [x.upper() for x in header]
        for select_name in listOfSelection:
            if select_name == '*':
                attr[table_name_called[t]] = header
                need_attributes[table_name_called[t]] = header
            else:
                if select_name.upper() in upper_header:
                    index = upper_header.index(select_name.upper())
                    attr[table_name_called[t]].append(header[index])
                    need_attributes[table_name_called[t]].append(header[index])
                    selection_rename.append(header[index])
                elif '.' in list(select_name) and select_name.split('.')[0] == table_name_called[t]:
                    index = upper_header.index((select_name.split('.')[1]).upper())
                    attr[table_name_called[t]].append(header[index])
                    if select_name.split('.')[1] not in need_attributes[table_name_called[t]]:
                        need_attributes[table_name_called[t]].append(header[index] + '_table_' + str(t + 1))
                    selection_rename.append(header[index] + '_table_' + str(t + 1))
        if where_conditions != []:
            for i in range(0, len(where_conditions)):
                if 'NOT' in (where_conditions[i].strip()).split() and 'LIKE' not in where_conditions[i]:
                    condition = where_conditions[i].split('NOT')[1]
                    condition = re.split('=|>|<|>=|<=|<>|\\+|-|\\*|/|', condition)
                    tmp = [tt.replace(" ", "") for tt in condition]
                elif 'NOT' not in where_conditions[i] and 'LIKE' in where_conditions[i]:
                    tmp = where_conditions[i].split()
                elif 'NOT' in where_conditions[i] and 'LIKE' in where_conditions[i]:
                    condition = where_conditions[i].split('NOT')[1]
                    condition = re.split('(LIKE)', condition)
                    tmp = [tt.replace(" ", "") for tt in condition]
                else:
                    condition = re.split('=|>|<|>=|<=|<>|\\+|-|\\*|/', where_conditions[i])
                    tmp = [tt.replace(" ", "") for tt in condition]

                for j in tmp:
                    if j.upper() in upper_header:
                        index = upper_header.index(j.upper())
                        if header[index] not in attr[table_name_called[t]]:
                            attr[table_name_called[t]].append(header[index])
                        if header[index] not in need_attributes[table_name_called[t]]:
                            need_attributes[table_name_called[t]].append(header[index])
                        eval_attributes[i].append(header[index])
                        actual_eval[i].append(header[index])
                        eval_from_table[i].append(t)
                    elif '.' in list(j) and j.split('.')[0] == table_name_called[t]:
                        index = upper_header.index((j.split('.')[1]).upper())
                        if header[index] not in attr[table_name_called[t]]:
                            attr[table_name_called[t]].append(header[index])
                        if header[index] in need_attributes[table_name_called[t]]:
                            pos = need_attributes[table_name_called[t]].index(header[index])
                            need_attributes[table_name_called[t]][pos] = header[index] + '_table_' + str(t + 1)
                        else:
                            need_attributes[table_name_called[t]].append(header[index] + '_table_' + str(t + 1))
                        eval_attributes[i].append(header[index] + '_table_' + str(t + 1))
                        actual_eval[i].append(j)
                        eval_from_table[i].append(t)
        need_attributes[table_name_called[t]] = [l for l in set(need_attributes[table_name_called[t]])]
    return attr, need_attributes, selection_rename, eval_attributes, actual_eval, eval_from_table

def deserializaiton(input):
    connection = []
    where_conditions = []
    join = False
    merge_on_attributes = []

    ## split input string
    listOfSelection, listOfTablesInFrom, whereClause, rename, distinct = split_input(input)

    ## check self join
    if len(listOfTablesInFrom) > 1:
        join = True

    ## split where clause
    if whereClause != True:
        new_where_conditions, connection, eval_attributes, actual_eval, eval_from_table  = split_conditions(whereClause, connection, where_conditions)
    else:
        new_where_conditions = where_conditions
        eval_attributes = {}
        actual_eval = {}
        eval_from_table = {}
    ## check rename
    if rename == []:
        table_name_called = [i.split('.csv')[0] for i in listOfTablesInFrom]
    else:
        table_name_called = rename

    ##find all needed attributes
    attr, need_attributes, selection_rename, eval_attributes, actual_eval, eval_from_table = find_attributes(table_name_called, listOfTablesInFrom,listOfSelection, new_where_conditions, eval_attributes, actual_eval, eval_from_table)

    if whereClause != True:
    ## change '=' to '=='
        for i in range(len(new_where_conditions)):
            for j in range(len(eval_attributes[i])):
                new_where_conditions[i] = new_where_conditions[i].replace(actual_eval[i][j], eval_attributes[i][j])

            if '=' in list(new_where_conditions[i]) and ('>' not in list(new_where_conditions[i]) and '<' not in list(new_where_conditions[i])):
                pos = new_where_conditions[i].find("=")
                new_where_conditions[i] = new_where_conditions[i][:pos] + '=' + new_where_conditions[i][pos:]
            if '<>' in new_where_conditions[i]:
                new_where_conditions[i] = new_where_conditions[i].replace('<>', '!=')

        ## find merge_on_attributes
        if join:
            for i in range(len(new_where_conditions)):
                if '==' in new_where_conditions[i]:
                    if len(eval_attributes[i]) == 2 and len(np.unique(eval_from_table[i])) == 2:
                        if (eval_attributes[i][0]).split('_table_')[0] not in merge_on_attributes:
                            merge_on_attributes.append((eval_attributes[i][0]).split('_table_')[0])
                            if eval_attributes[i][0] != eval_attributes[i][1]:
                                if (eval_attributes[i][1]).split('_table_')[0] not in merge_on_attributes:
                                    merge_on_attributes.append((eval_attributes[i][1]).split('_table_')[0])


    return attr,need_attributes, eval_attributes, connection, listOfSelection, selection_rename, listOfTablesInFrom, table_name_called, new_where_conditions, eval_from_table, join, merge_on_attributes, distinct
    # print(listOfAttributesInSelect)
    # print(listOfTablesInFrom)
    # print(listOfConditionsInWhere)

def isMatch(input_text, pattern):
    text = str(input_text)
    memo = {}
    pattern = pattern.replace("%", ".*")
    pattern = pattern.replace("_", ".")
    def dp(i, j):
        if (i, j) not in memo:
            if j == len(pattern):
                ans = i == len(text)
            else:
                first_match = i < len(text) and pattern[j] in {text[i], '.'}
                if j+1 < len(pattern) and pattern[j+1] == '*':
                    ans = dp(i, j+2) or first_match and dp(i+1, j)
                else:
                    ans = first_match and dp(i+1, j+1)

            memo[i, j] = ans
        return memo[i, j]

    return dp(0, 0)

def detect_type(condition, keylist):
    right = condition.split()[len(condition.split())-1].strip()

    #    new_keylist = [str(a) for a in keylist]
        #condition = condition.replace(right, '"' + right + '"')
    #else:
        #new_keylist = keylist
    return condition, keylist


def is_float(string):
  try:
    return float(string) and '.' in string  # True if string is a number contains a dot
  except ValueError:  # String is not a number
    return False

#####################################################################################################
def single_attribute_eval(condition,c, eval_attributes, shape, need_index, need_keylist):
    if 'NOT' in condition and 'LIKE' in condition:
        new_condition = re.sub('"', '', condition)
        pattern = new_condition.split('LIKE')[1].strip()
        like_result = []
        for k in need_keylist:
            text = k
            if not isMatch(text, pattern) or text == '':
                like_result.extend(need_index[k])
        return like_result

    elif 'NOT' not in condition and 'LIKE' in condition:
        condition = re.sub('"', '', condition)
        pattern = condition.split('LIKE')[1].strip()
        result = []
        for k in need_keylist:
            text = k
            if text != '' and isMatch(text, pattern):
                result.extend(need_index[k])
        return result

    elif 'NOT' in condition and 'LIKE' not in condition:
        var_name = eval_attributes[c][0]
        condition, new_keylist = detect_type(condition, need_keylist)
        if is_float(new_keylist[0]):
            new_keylist = [float(l) for l in new_keylist]
        elif new_keylist[0].isdigit():
            new_keylist = [int(l) for l in new_keylist]
        vars()[var_name] = np.array(new_keylist)
        new_condition = condition.split('NOT')[1]
        key_pos = list(np.where(eval(new_condition))[0])
        result = []
        for k in key_pos:
            result.extend(need_index[need_keylist[k]])
        all = range(shape)
        not_result = np.setdiff1d(all, result)
        return not_result
    else:
        var_name = eval_attributes[c][0]
        condition, new_keylist = detect_type(condition, need_keylist)
        if is_float(new_keylist[0]):
            new_keylist = [float(l) for l in new_keylist]
        elif new_keylist[0].isdigit():
            new_keylist = [int(l) for l in new_keylist]

        vars()[var_name] = np.array(new_keylist)
        key_pos = list(np.where(eval(condition))[0])
        result = []
        for k in key_pos:
            result.extend(need_index[need_keylist[k]])
        return result

def single_table_eval(condition, c, eval_attributes, shape, index, keylist):
    for var_name in eval_attributes[c]:
        subset1 = keylist[var_name.split('_table_')[0]]
        vars()[var_name] = np.array(subset1)

    if 'NOT' in condition:
        condition = condition.split('NOT')[1]
        all = range(shape)
        #condition = detect_type(condition)
        key_pos = list(np.where(eval(condition))[0])
        result = [i in index[keylist[j]] for j in key_pos]
        not_result = np.setdiff1d(all, result)
        return not_result
    else:
        #condition = detect_type(condition)
        key_pos = list(np.where(eval(condition))[0])
        result = [i in index[keylist[j]] for j in key_pos]
        return result



def multi_table_eval(condition,c, eval_attributes, eval_from_table, shape, need_index, need_keylist):
    selected_row = {}
    attr1 = eval_attributes[c][0].split('_table_')[0]
    attr2 = eval_attributes[c][1].split('_table_')[0]
    tab1 = int(eval_attributes[c][0].split('_table_')[1])-1
    tab2 = int(eval_attributes[c][1].split('_table_')[1])-1
    if len(need_keylist[tab1][attr1]) > len(need_keylist[tab2][attr2]):
        subset1 = np.array(need_keylist[tab1][attr1])
        var_name = eval_attributes[c][tab2]
        var_set = eval_attributes[c][tab1]
        vars()[var_set] = subset1
        all = list(range(shape[eval_from_table[c][tab1]]))
        ## record: table with smaller index
        ## record1: table with larger index
        record = tab2
        record1 = tab1
        #condition = detect_type(condition)
        selected_row[record] = {}
        selected_row[record1] = {}
        if '==' in condition:
            if 'NOT' in condition:
                need_check = list(set(need_keylist[tab1][attr1]) - set(need_keylist[tab2][attr2]))
            else:
                need_check = list(np.intersect1d(need_keylist[tab2][attr2],need_keylist[tab1][attr1]))
        elif '!=' in condition:
            if 'NOT' in condition:
                need_check = list(np.intersect1d(need_keylist[tab2][attr2],need_keylist[tab1][attr1]))
            else:
                need_check = list(set(need_keylist[tab1][attr1]) - set(need_keylist[tab2][attr2]))
        else:
            need_check = need_keylist[tab2][attr2]

    else:
        subset1 = np.array(need_keylist[tab2][attr2])
        var_name = eval_attributes[c][tab1]
        var_set = eval_attributes[c][tab2]
        vars()[var_set] = subset1
        all = range(shape[eval_from_table[c][tab2]])
        record = tab1
        record1 = tab2
        #condition = detect_type(condition)
        selected_row[record] = []
        selected_row[record1] = []
        if '==' in condition:
            if 'NOT' in condition:
                need_check = list(set(need_keylist[tab2][attr2]) - set(need_keylist[tab1][attr1]))
            else:
                need_check = list(np.intersect1d(need_keylist[tab2][attr2],need_keylist[tab1][attr1]))
        elif '!=' in condition:
            if 'NOT' in condition:
                need_check = list(np.intersect1d(need_keylist[tab2][attr2],need_keylist[tab1][attr1]))
            else:
                need_check = list(set(need_keylist[tab2][attr2]) - set(need_keylist[tab1][attr1]))
        else:
            need_check = need_keylist[tab1][attr1]

    if '==' in condition or '!=' in condition:
        #for key in need_check:
        #    for k in need_index[record1][var_name.split('_table_')[0]][key]:
        #        selected_row[record1][k] = need_index[record][var_set.split('_table_')[0]][key]
        #    for l in need_index[record][var_set.split('_table_')[0]][key]:
        #        selected_row[record][l] = need_index[record1][var_name.split('_table_')[0]][key]
        #value1 = {key: need_index[record1][var_name.split('_table_')[0]][key] for key in need_check}
        #value = {key: need_index[record][var_set.split('_table_')[0]][key] for key in need_check}

        #selected_row[record1] = {value1[key][l]: value[key] for l in range(len(value1[key])) for key in need_check}
        #selected_row[record] = {value[key][g]: value1[key] for g in range(len(value[key])) for key in need_check}
        selected_row[record1] = [need_index[record1][var_name.split('_table_')[0]][key] for key in need_check]
        #selected_row[record1] = [item for sublist in result for item in sublist]
        selected_row[record] = [need_index[record][var_set.split('_table_')[0]][key]for key in need_check]
        #selected_row[record] = [item for sublist in result1 for item in sublist]
    else:
        for key in need_check:
            vars()[var_name] = key
            if 'NOT' in condition:
                condition = condition.split('NOT')[1]
                key_pos = list(np.where(eval(condition))[0])
                result = []
                for k in key_pos:
                    result.extend(need_index[record1][need_keylist[record1][k]])
                not_result = list(np.setdiff1(range(shape[record1], result)))
                if len(result) != 0 and len(result) != all:
                    selected_row[record1] = selected_row[record1] + not_result
                    selected_row[record] = selected_row[record] + need_index[record][need_keylist[record]]

            else:
                key_pos = list(np.where(eval(condition))[0])
                result = []
                for k in key_pos:
                    l = need_keylist[record1][var_set.split('_table_')[0]]
                    result.extend(need_index[record1][var_name.split('_table_')[0]][l[k]])
                if len(result) != 0:
                    selected_row[record1] = selected_row[record1] + result
                    selected_row[record] = selected_row[record] + need_index[record][var_name.split('_table_')[0]][key]

    return record, record1, selected_row

def Eval(index, keylist, shape, eval_attributes, Conditions,eval_from_table, join, merge_on_attributes):
    if Conditions == []:
        ## no where clause present
        selected_row = {}
        for table, row in shape.items():
            selected_row[table] = range(row)
        return selected_row
    elif join:
        selected_row = {}
        for c in range(len(Conditions)):
            print(c)
            selected_row[c] = {}
            if '==' in Conditions[c]:
                if len(eval_attributes[c]) == 1:
                    t = eval_from_table[c][0]
                    need_index = index[t][(eval_attributes[c][0]).split('_table_')[0]]
                    need_keylist = keylist[t][(eval_attributes[c][0]).split('_table_')[0]]
                    condition = Conditions[c]
                    result = single_attribute_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                    selected_row[c][eval_from_table[c][0]] = result
                elif len(eval_attributes[c]) >= 2 and len(np.unique(eval_from_table[c])) == 1:
                    t = eval_from_table[c][0]
                    need_index = {k: index[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                    need_keylist = {k: keylist[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                    condition = Conditions[c]
                    result = single_table_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                    selected_row[c][eval_from_table[c][0]] = result

            else:
                if len(eval_attributes[c]) == 1:
                    t = eval_from_table[c][0]
                    need_index = index[t][(eval_attributes[c][0]).split('_table_')[0]]
                    need_keylist = keylist[t][(eval_attributes[c][0]).split('_table_')[0]]
                    condition = Conditions[c]
                    result = single_attribute_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                    selected_row[c][eval_from_table[c][0]] = result

                elif len(eval_attributes[c]) >= 2 and len(np.unique(eval_from_table[c])) == 1:
                    t = eval_from_table[c][0]
                    need_index = {k: index[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                    need_keylist = {k: keylist[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                    condition = Conditions[c]
                    result = single_table_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                    selected_row[c][eval_from_table[c][0]] = result

                elif len(eval_attributes[c]) >= 2 and len(np.unique(eval_from_table[c])) > 1:
                    condition = Conditions[c]
                    need_index = {}
                    need_keylist = {}
                    for t in eval_from_table[c]:
                        need_index[t] = {k: index[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c] if int(j.split('_table_')[1])==t+1]}
                        need_keylist[t] = {k: keylist[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c] if int(j.split('_table_')[1])==t+1]}
                    record, record1, result = multi_table_eval(condition, c, eval_attributes, eval_from_table, shape, need_index, need_keylist)
                    selected_row[c][record] = result[record]
                    selected_row[c][record1] = result[record1]
        return selected_row

    else:
        ## single table
        selected_row = {}
        for c in range(len(Conditions)):
            selected_row[c] = {}
            if len(eval_attributes[c]) == 1:
                t = eval_from_table[c][0]
                need_index = index[t][(eval_attributes[c][0]).split('_table_')[0]]
                need_keylist = keylist[t][(eval_attributes[c][0]).split('_table_')[0]]
                condition = Conditions[c]
                result = single_attribute_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                selected_row[c][eval_from_table[c][0]] = result

            elif len(eval_attributes[c]) >= 2 and len(np.unique(eval_from_table[c])) == 1:
                t = eval_from_table[c][0]
                need_index = {k: index[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                need_keylist = {k: keylist[t][k] for k in [j.split('_table_')[0] for j in eval_attributes[c]]}
                condition = Conditions[c]
                result = single_table_eval(condition, c, eval_attributes, shape[t], need_index, need_keylist)
                selected_row[c][eval_from_table[c][0]] = result
        return selected_row


########################################################################################################################
##### Combine pos

def self_combine(pos, selected_row, connection):
    ##single table
    pos[0] = selected_row[0][0]
    for i in range(0, int(len(connection))):
        con = connection[i]
        if list(pos[0]) == [] and list(selected_row[i+1][0]) != 0:
            pos[0] = selected_row[i+1]

        if list(pos[0]) != [] and list(selected_row[i+1][0]) != []:
            if con == 'AND':
                pos[0] = np.intersect1d(pos[0], selected_row[i + 1][0])
            else:
                pos[0] = np.union1d(selected_row[i][0], selected_row[i + 1][0])
    return pos

def combine_multi(pos, selected_row, listOfTablesInFrom, eval_from_table, connection, shape):
    check = []
    for t in range(len(listOfTablesInFrom)):
        if t in eval_from_table[0] and selected_row[0] != {}:
            pos[t] = selected_row[0][t]
            check.append(t)
        else:
            pos[t] = []
    if len(selected_row[0].keys()) > 0:
        appear_together = True
    else:
        appear_together = False

    for i in range(len(connection)):
        con = connection[i]
        if con == 'AND':
            if selected_row[i+1] != {}:
                if (list(set(eval_from_table[i + 1]) - set(eval_from_table[i])) == eval_from_table[i + 1] or list(set(eval_from_table[i + 1]) - set(eval_from_table[i])) == []):
                ### if two conditions are not using any same table
                    if list(set(check) - set(eval_from_table[i + 1])) != check:
                        ## means the eval table has appeared before
                        eval_table = eval_from_table[i + 1]
                        if appear_together:
                            position = {}
                            for t in eval_table:
                                position[t] = []
                                for l in range(len(pos[t])):
                                    x = pos[t][l]
                                    if x in selected_row[i + 1][t]:
                                        position[t].append(l)

                            final_position = position[eval_table[0]]
                            for num in range(1, len(eval_table)):
                                final_position = np.intersect1d(final_position, position[eval_table[num]])

                            for t in check:
                                pos[t] = [pos[t][d] for d in final_position]
                        else:
                            pos[eval_table[0]] = list(np.intersect1d(pos[eval_table[0]], selected_row[i+1][eval_table[0]]))
                            # position = {}
                            # for t in eval_table:
                            #     position[t] = []
                            #     for l in range(len(pos[t])):
                            #         x = pos[t][l]
                            #         if x in selected_row[i + 1][t]:
                            #             position[t].append(l)
                            #
                            # final_position = position[eval_table[0]]
                            # for num in range(1, len(eval_table)):
                            #     final_position = np.intersect1d(final_position, position[eval_table[num]])
                            #
                            # for t in eval_table:
                            #     pos[t] = [pos[t][d] for d in final_position]

                    else:
                        ## if the eval table has never appeared
                        for t in eval_from_table[i + 1]:
                            if pos[t] == []:
                                pos[t] = selected_row[i + 1][t]
                            else:
                                pos[t] = [l for l in range(len(pos[t])) if pos[t][l] in selected_row[i + 1][t]]
                            check.append(t)
                else:
                    ## if two conditions are using some same table
                    for t in eval_from_table[i+1]:
                        if list(pos[t]) == []:
                            pos[t] = list(selected_row[i+1][t])

                    position = {}
                    position1 = {}
                    other_table = list(set(eval_from_table[i+1]) - set(eval_from_table[i]))
                    same_table = list(set(eval_from_table[i+1]) - set(other_table))
                    check = check + [table for table in other_table]
                    for t in same_table:
                        position[t] = []
                        position1[t] = []
                        for l in range(len(pos[t])):
                            x = pos[t][l]
                            if x in selected_row[i + 1][t]:
                                position[t].append(l)
                                other_position = [j for j in range(len(selected_row[i + 1][t])) if selected_row[i + 1][t][j] == x]
                                if other_position != position1[t][(len(position1[t]) - len(other_position)):len(position1[t])]:
                                    position1[t] = position1[t] + other_position

                    final_position = position[same_table[0]]
                    final_position1 = position1[same_table[0]]
                    for num in range(1, len(same_table)):
                        final_position = np.intersect1d(final_position, position[same_table[num]])
                        final_position1 = np.intersect1d(final_position1, position1[same_table[num]])

                    if len(eval_from_table[i]) < len(eval_from_table[i+1]):
                        for t in eval_from_table[i+1]:
                            pos[t] = [pos[t][d] for d in final_position1]
                    else:
                        for t in eval_from_table[i]:
                            pos[t] = [pos[t][d] for d in final_position]

                        for t1 in other_table:
                            pos[t1] = [pos[t1][d] for d in final_position1]
        else:
            if list(set(eval_from_table[i + 1]) - set(eval_from_table[i])) == eval_from_table[i + 1] or list(set(eval_from_table[i + 1]) - set(eval_from_table[i])) == []:
                other_table = list(set(check) - set(eval_from_table[i+1]))

                eval_table = eval_from_table[i + 1]
                for t in eval_table:
                    if list(pos[t]) == []:
                        pos[t] = selected_row[i+1][t]
                    else:
                        if other_table != []:
                            for t1 in other_table:
                                for l in range(len(selected_row[i+1][t])):
                                    x = selected_row[i+1][t][l]
                                    if x not in pos[t]:
                                        pos[t] = pos[t] + [x]*len(range(shape[t1]))
                                        pos[t1] = pos[t1] + list(range(shape[t1]))
                        else:
                            for l in range(len(selected_row[i + 1][t])):
                                x = selected_row[i + 1][t][l]
                                if x not in pos[t]:
                                    pos[t] = np.append(pos[t],x)

            else:
                eval_table = eval_from_table[i + 1]
                for t in eval_table:
                    if list(pos[t]) == []:
                        pos[t] = selected_row[i+1][t]
                    else:
                        for l in range(len(selected_row[i + 1][t])):
                            x = selected_row[i + 1][t][l]
                            if x not in pos[t]:
                                pos[t] = pos[t] + [x]

    return pos


def Combine_Condition(selected_row, connection, listOfTablesInFrom, eval_from_table, join, shape):
    pos = {}
    if connection == []:
        for t in range(len(listOfTablesInFrom)):
            pos[t] = selected_row[t]
        return pos
    elif join:
        pos = combine_multi(pos, selected_row, listOfTablesInFrom, eval_from_table, connection, shape)
        return pos
    else:
        pos = self_combine(pos, selected_row, connection)
        return pos

####################################################################################################


def Adjust_row(pos, table1, table2):
    length1 = len(pos[table1])
    length2 = len(pos[table2])
    new_pos = {}
    new_pos[table1] = list(pos[table1])*length2
    new_pos[table2] = list(pos[table2])*length1
    return new_pos

### UNCOMMENT FOR METHOD NOT READING CSV
def WHERE(pos, listOfTablesInFrom, join, attr, table_name_called, shape, need_attributes, merge_on_attributes, connection):
    if connection == []:
        final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]])
        return final_R
    elif join:
        if pos[0] != []:
            skip_pos = list(np.setdiff1d(range(shape[0]), pos[0])+1)
            final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]], skiprows=skip_pos)
        else:
            final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]])

        col_names = final_R.columns.values
        for i in range(len(need_attributes[table_name_called[0]])):
            need_name = need_attributes[table_name_called[0]][i]
            if '_table_' in need_name:
                if need_name.split('_table_')[0] not in merge_on_attributes:
                    name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
                    final_R = final_R.rename(columns={col_names[name_pos]: need_name})
                else:
                    if need_name.split('_table_')[0] != merge_on_attributes[0]:
                        name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
                        final_R = final_R.rename(columns={col_names[name_pos]: merge_on_attributes[0]})
            else:
                name_pos = np.where(col_names == need_name)[0][0]
                final_R = final_R.rename(columns={col_names[name_pos]: need_name})

        for t in range(1,len(listOfTablesInFrom)):
            #if t+1 < len(listOfTablesInFrom):
            #    if len(pos[t]) != len(pos[t+1]):
            #        new_pos = Adjust_row(pos, t, t+1)
            if pos[t] != []:
                skip_pos = list(np.setdiff1d(range(shape[t]), pos[t])+1)
                R = pd.read_csv(listOfTablesInFrom[t], usecols=attr[table_name_called[t]], skiprows=skip_pos)

            else:
                R = pd.read_csv(listOfTablesInFrom[t], usecols = attr[table_name_called[t]])

            col_names = R.columns.values
            for i in range(len(need_attributes[table_name_called[t]])):
                need_name = need_attributes[table_name_called[t]][i]
                if '_table_' in need_name:
                    if need_name.split('_table_')[0] not in merge_on_attributes:
                        name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
                        R = R.rename(columns={col_names[name_pos]: need_name})
                    else:
                        if need_name.split('_table_')[0] != merge_on_attributes[0]:
                            name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
                            R = R.rename(columns={col_names[name_pos]: merge_on_attributes[0]})
                else:
                    name_pos = np.where(col_names == need_name)[0][0]
                    R = R.rename(columns={col_names[name_pos]: need_name})
            #R = R.loc[new_pos[t]]
            #final_R = pd.concat([final_R.reset_index(drop= True),R.reset_index(drop = True)], axis = 1)
            final_R = final_R.merge(R, on = merge_on_attributes)
        return final_R
    else:
        ## single table
        skip_pos = list(np.setdiff1d(range(shape[0]), pos[0])+1)
        R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]], skiprows=skip_pos)

        col_names = R.columns.values
        for i in range(len(need_attributes[table_name_called[0]])):
            need_name = need_attributes[table_name_called[0]][i]
            if '_table_' in need_name:
                name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
                R = R.rename(columns={col_names[name_pos]: need_name})
            else:
                name_pos = np.where(col_names == need_name)[0][0]
                R = R.rename(columns={col_names[name_pos]: need_name})
        return R

# ### THIS IS USING READ CSV FILE METHOD
# def WHERE(pos, listOfTablesInFrom, join, attr, table_name_called, shape, need_attributes, merge_on_attributes, connection, in_memory):
#     if connection == []:
#         #final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]])
#         final_R = in_memory[listOfTablesInFrom[0]][attr[table_name_called[0]]]
#         return final_R
#     elif join:
#         if pos[0] != []:
#             #skip_pos = list(np.setdiff1d(range(shape[0]), pos[0])+1)
#             #final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]], skiprows=skip_pos)
#             final_R = in_memory[listOfTablesInFrom[0]][attr[table_name_called[0]]].loc[pos[0]]
#         else:
#             #final_R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]])
#             final_R = in_memory[listOfTablesInFrom[0]][attr[table_name_called[0]]]
#         col_names = final_R.columns.values
#         for i in range(len(need_attributes[table_name_called[0]])):
#             need_name = need_attributes[table_name_called[0]][i]
#             if '_table_' in need_name:
#                 if need_name.split('_table_')[0] not in merge_on_attributes:
#                     name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
#                     final_R = final_R.rename(columns={col_names[name_pos]: need_name})
#                 else:
#                     if need_name.split('_table_')[0] != merge_on_attributes[0]:
#                         name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
#                         final_R = final_R.rename(columns={col_names[name_pos]: merge_on_attributes[0]})
#             else:
#                 name_pos = np.where(col_names == need_name)[0][0]
#                 final_R = final_R.rename(columns={col_names[name_pos]: need_name})
#
#         for t in range(1,len(listOfTablesInFrom)):
#             #if t+1 < len(listOfTablesInFrom):
#             #    if len(pos[t]) != len(pos[t+1]):
#             #        new_pos = Adjust_row(pos, t, t+1)
#             if pos[t] != []:
#                 #skip_pos = list(np.setdiff1d(range(shape[t]), pos[t])+1)
#                 #R = pd.read_csv(listOfTablesInFrom[t], usecols=attr[table_name_called[t]], skiprows=skip_pos)
#                 R = in_memory[listOfTablesInFrom[t]][attr[table_name_called[t]]].loc[pos[t]]
#             else:
#                 #R = pd.read_csv(listOfTablesInFrom[t], usecols = attr[table_name_called[t]])
#                 R = in_memory[listOfTablesInFrom[t]][attr[table_name_called[t]]]
#
#             col_names = R.columns.values
#             for i in range(len(need_attributes[table_name_called[t]])):
#                 need_name = need_attributes[table_name_called[t]][i]
#                 if '_table_' in need_name:
#                     if need_name.split('_table_')[0] not in merge_on_attributes:
#                         name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
#                         R = R.rename(columns={col_names[name_pos]: need_name})
#                     else:
#                         if need_name.split('_table_')[0] != merge_on_attributes[0]:
#                             name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
#                             R = R.rename(columns={col_names[name_pos]: merge_on_attributes[0]})
#                 else:
#                     name_pos = np.where(col_names == need_name)[0][0]
#                     R = R.rename(columns={col_names[name_pos]: need_name})
#             #R = R.loc[new_pos[t]]
#             #final_R = pd.concat([final_R.reset_index(drop= True),R.reset_index(drop = True)], axis = 1)
#             final_R = final_R.merge(R, on = merge_on_attributes)
#             #final_R = final_R.merge(R)
#
#         return final_R
#     else:
#         ## single table
#         #skip_pos = list(np.setdiff1d(range(shape[0]), pos[0])+1)
#         #R = pd.read_csv(listOfTablesInFrom[0], usecols=attr[table_name_called[0]], skiprows=skip_pos)
#         R = in_memory[listOfTablesInFrom[0]][attr[table_name_called[0]]].loc[pos[0]]
#         col_names = R.columns.values
#         for i in range(len(need_attributes[table_name_called[0]])):
#             need_name = need_attributes[table_name_called[0]][i]
#             if '_table_' in need_name:
#                 name_pos = np.where(col_names == need_name.split('_table_')[0])[0][0]
#                 R = R.rename(columns={col_names[name_pos]: need_name})
#             else:
#                 name_pos = np.where(col_names == need_name)[0][0]
#                 R = R.rename(columns={col_names[name_pos]: need_name})
#         return R

##############################################################################################################################
def SELECT(attributes, selection_rename, final_R, join, merge_on_attributes, distinct):
    if '*' in attributes:
        return final_R
    elif join:
        col_names = final_R.columns.values
        for i in range(len(col_names)):
            if col_names[i] in selection_rename:
                pos = selection_rename.index(col_names[i])
                final_R = final_R.rename(columns={col_names[i]: attributes[pos]})
            elif col_names[i] in merge_on_attributes:
                    for rename in selection_rename:
                        if '_table_' in rename and col_names[i] == rename.split('_table_')[0]:
                            pos = selection_rename.index(rename)
                            final_R = final_R.rename(columns={col_names[i]: attributes[pos]})

        if distinct:
            D = pd.DataFrame(np.unique(final_R[attributes]), columns = attributes)
            return D
        else:
            return final_R[attributes]
    else:
        ## single table
        col_names = final_R.columns.values
        for i in range(len(col_names)):
            if '_table_' in col_names[i]:
                if col_names[i].split('_table_')[0] in selection_rename:
                    pos = selection_rename.index(col_names[i].split('_table_')[0])
                    final_R = final_R.rename(columns={col_names[i]: attributes[pos]})
                elif col_names[i] in selection_rename:
                    pos = selection_rename.index(col_names[i])
                    final_R = final_R.rename(columns={col_names[i]: attributes[pos]})

            else:
                if col_names[i] in selection_rename:
                    pos = selection_rename.index(col_names[i])
                    final_R = final_R.rename(columns={col_names[i]: attributes[pos]})

        if distinct:
            D = pd.DataFrame(np.unique(final_R[attributes]), columns = attributes)
            return D
        else:
            return final_R[attributes]


def find_index_order(listOfTablesInFrom, attr, table_name_called, merge_on_attributes, eval_attributes):
    index = {}
    keylist = {}
    shape = {}
    eval_need = [j.split('_table_')[0] for i in range(len(eval_attributes.keys())) for j in eval_attributes[i]]

    for t in range(len(listOfTablesInFrom)):
        csv_file = listOfTablesInFrom[t]
        index[t] = {}
        keylist[t] = {}
        for wanted in attr[table_name_called[t]]:
            if wanted not in merge_on_attributes and wanted in eval_need:
                indexing = json.load(open(csv_file+'_'+wanted+'_indexing.json'))
                index[t][wanted] = indexing
                keylist[t][wanted] = list(indexing.keys())
        shape[t] = json.load(open(csv_file+'_shape.json'))['0']
    return index, keylist, shape
