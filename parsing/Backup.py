'''
Created on Apr 27, 2013

@author: Lubo
'''
#Function used to cut output from parser into list of strings
def cut_tuple(input_tuple,data_struct):
    
    #Not sure if this line is required in python, might recheck later
    my_list = data_struct
    #String we're working with
    temp = ""
    #Index: position in tuple
    index = 0
    #indent level
    indent = 0
    
    for k in input_tuple:
        #Check for special "codebreakers"
        if str(k) != "classdef" and str(k) != "funcdef":
            #Check whether k is tuple = we want to output whole string, not tuples
            if isinstance(k,tuple):
                temp_otp = ""
                temp_otp = tuple_to_string(k, temp_otp, 0, True, False)
                temp += temp_otp      
            else:
                #Class and def are handled separately since we removed the whitespace
                if str(k) == "class":
                    temp += str(k)+" "
                elif str(k) == "def":
                    temp += str(k)+" "
                else:
                    temp += str(k)
        else:
            #Append what's in temp if it's not empty
            if (temp != ""):
                temp_list = [temp]
                my_list.append(temp_list)
            temp = ""
            ''''Not sure about these test = [] lines, might recheck later TODO
                Basic idea: call function on tuple with class/def
            '''
            test = []
            help = input_tuple[index+1]
            input_tuple = input_tuple[index+2:]
            index = index + 2
            nieco = cut_tuple(help,test)
            my_list.append(nieco)
            test = []
            test = cut_tuple(input_tuple, test)
            if (len(test) > 1):
                for i in test:
                    my_list.append(i)
            else:
                #my_list.append(cut_tuple(input_tuple, test))
                my_list.append(test)
            break
        index += 1
    if temp != "":
        my_list.append(temp)
    return my_list

def generate_indent(num):
    result = ""
    for x in range(0,num):
        result += '\t'
    return result    
    
def tuple_to_string(input_tuple, result, ind, w_i_new, w_i_ind):
    if isinstance(input_tuple,tuple):
        indent_level = ind
        temp = ""
        w_new = w_i_new
        w_ind = w_i_ind
        
        for i in input_tuple:
            if isinstance(i, tuple):     
                if str(i[0]) != "funcdef" and str(i[0]) != "classdef":
                    temp_otp = tuple_to_string(i, temp, indent_level, w_new, w_ind)
                else:
                    temp_otp = tuple_to_string(i[1], temp, indent_level, w_new, w_ind)
                result += temp_otp
            else:
                #print("A",str(i))
                temp_otp = ""
                if str(i) == "def" or str(i) == "class":
                    temp_otp = str(i)+" "
                else:
                    temp_otp = str(i)
                    
                if str(i) == "\t":
                    indent_level += 1
                elif str(i) == "ded":
                    indent_level -= 1
                elif str(i) == "\n":
                    w_new = True
                    w_ind = False
                    result += temp_otp
                else: 
                    if w_new:
                        if w_ind:
                            result += temp_otp
                        else:
                            result += generate_indent(indent_level)+temp_otp
                            w_new = False
                            w_ind = True
                    else:
                        result += temp_otp
    return result


#FUNGUJE

def create_list_of_strings(input_lexer,input_data,input_list):
    c_my_list = input_list
    c_lexer = input_lexer
    c_data = input_data
    c_lexer.input(c_data)
    c_line_number = 1
    c_indent_level = 0
    c_temp = ""
    c_global_output = ""
    
    for tok in c_lexer:
        #print(tok)
        if tok.type == "INDENT":
            c_indent_level += 1
        elif tok.type == "DEDENT":
            c_indent_level -= 1
        else:
            c_tok_value = ""
            if tok.value == "class" or tok.value == "def":
                c_my_list.append(c_global_output)
                c_tok_value = tok.value+" "
            elif tok.value == "end":
                c_tok_value = ""
            else:
                c_tok_value = tok.value
            
            if tok.lineno == c_line_number:
                c_temp += c_tok_value
            else:
                c_global_output += c_temp
                c_temp = ""
                c_temp += generate_indent(c_indent_level)+c_tok_value
                c_line_number = tok.lineno
    #c_global_output += c_temp
    c_my_list.append(c_global_output)
    return c_my_list

#==============================
def create_list_of_strings(input_lexer,input_data,input_list):
    c_my_list = input_list
    c_lexer = input_lexer
    c_data = input_data
    c_lexer.input(c_data)
    c_line_number = 1
    c_indent_level = 0
    current_line = ""
    current_scope = ""
    c_tok_value = ""
    previous_token_type = None
    was_def_or_class = False
    
    for tok in c_lexer:
        if tok.type == "INDENT":
            c_indent_level += 1
        elif tok.type == "DEDENT":
            c_indent_level -= 1
        elif tok.value == "end":
            c_tok_value = ""
        elif tok.value == ":" and was_def_or_class:
            #print("DOSIEL COLON")
            current_scope += current_line+":"
            current_line = ""
            if current_scope != "":
                c_my_list.append(current_scope)
            current_scope = ""
            was_def_or_class = False
        elif tok.value == "class" or tok.value == "def":
            #print("PRISLA CLASS",current_scope)
            current_scope += current_line
            current_line = ""
            if (c_indent_level == 0):
                c_tok_value = generate_indent(c_indent_level)+tok.value+" "
            else:
                c_tok_value = generate_indent(c_indent_level)+tok.value+" "
            if current_scope != "":
                c_my_list.append(current_scope)
            current_scope = ""+c_tok_value
            was_def_or_class = True
        else:
            c_tok_value = tok.value
            if tok.lineno == c_line_number:
                current_line += c_tok_value
            else:
                current_scope += current_line
                current_line = ""
                if previous_token_type != "DEF" and previous_token_type != "CLASS":
                    current_line = generate_indent(c_indent_level)+c_tok_value
                else:
                    current_line = c_tok_value
                c_line_number = tok.lineno
        previous_token_type = tok.type
    #c_global_output += c_temp
    #print(current_scope, current_line)
    if current_scope != "":
        c_my_list.append(current_scope)
    
    if current_line != "":
        c_my_list.append(current_line)
    
    return c_my_list

def get_indent_level(input_string):
    inp = input_string
    inp = inp.replace("\n", "")
    counter = 0
    while inp[0:1] == "\t":
        counter += 1
        inp = inp.replace("\t","",1)
    return counter

def our_check(input_list):
    output_list = []
    my_str = ""
    for i in input_list:
        if isinstance(i,str):
            #print("JE TO STRING")
            if i[0:5] == "class":
                print("class")
            else:
                output_list.append(i)
            print(input_list)
            #print(get_indent_level(i))
        else:
            return []
    return output_list

#asuidhgjkadgasuydgbhjasdkgadsg
def cut_tuple(input_tuple,data_struct):
    
    #Not sure if this line is required in python, might recheck later
    my_list = data_struct
    #String we're working with
    temp = ""
    #Index: position in tuple
    index = 0
    #indent level
    indent = 0
    
    for k in input_tuple:
        #Check for special "codebreakers"
        if str(k) != "classdef" and str(k) != "funcdef":
            #Check whether k is tuple = we want to output whole string, not tuples
            if isinstance(k,tuple):
                print("K",k)
                if k[0] == "funcdef" or k[0] == "classdef":
                    #print("AAA")
                    tet = []
                    tet = cut_tuple(k[1],tet)
                    my_list.append(tet[0])
                else:
                    #print("BBB")
                    tuple_complete = ""
                    for i in k:
                        tuple_complete += str(i)
                    print("A",tuple_complete)
                    #temp = tuple_complete
                    my_list.append([tuple_complete])
            else:
                #Class and def are handled separately since we removed the whitespace
                if str(k) == "class":
                    temp += str(k)+" "
                elif str(k) == "def":
                    temp += str(k)+" "
                else:
                    temp += str(k)
        else:
            #Append what's in temp if it's not empty
            if (temp != ""):
                temp_list = [temp]
                my_list.append(temp_list)
            temp = ""
            ''''Not sure about these test = [] lines, might recheck later TODO
                Basic idea: call function on tuple with class/def
            '''
            test = []
            help = input_tuple[index+1]
            input_tuple = input_tuple[index+2:]
            index = index + 2
            
            print(help)
            test_string = help[0]+" "+help[1]+help[2]+help[3]+help[4][0]+help[4][1]
            print(test_string)
            
            vysledok = []
            vysledok.append([test_string])
            
            nieco = cut_tuple(help[4][2],test)
            vysledok.append(nieco)
            my_list.append(vysledok)
            test = []
            test = cut_tuple(input_tuple, test)
            if (len(test) > 1):
                for i in test:
                    my_list.append(i)
            else:
                #my_list.append(cut_tuple(input_tuple, test))
                my_list.append(test)
            break
        index += 1
    if temp != "":
        my_list.append(temp)
    return my_list

#adhg uisjgnasdg
def another_function(input_lexer, input_data):
    return_list = []
    lexer = input_lexer
    data = input_data
    lexer.input(data)
    temp = ""    
    indent_level = 0
    after_newline = True
    
    for tok in lexer:
        #print(tok)
        if tok.type == "INDENT":
            indent_level += 1
        elif tok.type == "DEDENT":
            indent_level -= 1
            #if indent_level == 0:
            return_list.append(temp)
            temp = ""
        elif tok.type == "NEWLINE":
            temp += tok.value
            after_newline = True
        elif tok.type == "ENDMARKER":
            temp += ""
        elif tok.value != "class" and tok.value != "def":
            if after_newline:
                temp += generate_indent(indent_level)+tok.value
                after_newline = False
            else:
                temp += tok.value
        else:
            return_list.append(temp)
            temp = ""
            if after_newline:
                temp += generate_indent(indent_level)+tok.value+" "
                after_newline = False
            else:
                temp += tok.value+" "
    if temp != "":
        return_list.append(temp)
    return return_list
    
def iterate_trough_list(input_list):
    output_list = []
    input = input_list
    for i in input:
        c = i.replace("\t","")
        if c[0:5] == "class" or c[0:3] == "def":
            print("AAAA")
        else:
            output_list.append(i)
    return output_list

my_lexer = MyLexer1.PythonLexer()
nieco = another_function(my_lexer, data)
print(nieco)
print("========")
print_my_list(nieco)
nieco2 = iterate_trough_list(nieco)
print("========")
print(nieco2)