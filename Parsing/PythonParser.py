'''
Created on May 1, 2013

@author: Lubo
'''
#Imports we will use later on
import MyLexer1
import MyParser1
import Tree
import ast



"Method used to print nested lists"
def print_my_list(my_list,ind_level):
    result = ""
    test = ind_level
    zaciatok = True
    for i in my_list:  
        if isinstance(i,list):
            result += print_my_list(i,test +1)
            zaciatok = True    
        else:
            if zaciatok:       
                my_temp = ""
                for x in range(0,test):
                    my_temp += "\t"
                count = i.count("\n")
                str_temp = i.replace("\n","\n"+my_temp,count-1)
                result += my_temp+str_temp
                zaciatok = False
            else:
                result += i
            if "\n" in i:
                zaciatok= True
    return result
   
"Method converting tuple to string in wanted format"
def tuple_to_string(input_tuple):
    output = ""
    for i in input_tuple:
        if isinstance(i,tuple):
            output += tuple_to_string(i)
        else:
            output += i
    return output  
   
"Method converting tuple of tuples into list"
def first_phase(input_tuple):
    output_list = []
    help_bool = False
    temp = ""
    
    for i in input_tuple:
        if i == "classdef" or i == "funcdef" or i == "conddef":
            help_bool = True
            if temp != "":
                output_list.append([temp])
                temp = ""
        else:
            if help_bool:
                #output_list.append(i)
                test = edit_tuple(i)
                #print(test)
                output_list.append(test)
                help_bool = False
            else:
                if isinstance(i,tuple):
                    temp += tuple_to_string(i)
                else:
                    temp += i
            
    if temp != "":
        output_list.append([temp]) 
    if len(output_list) == 1 and isinstance(output_list, list):
        return output_list[0]
    else:
        return output_list

"Recursive method to work with tuples nested inside of list created in previous method"
def edit_tuple(input_tuple):
    output_list = []
    temp = ""
    #print("INPUT:",input_tuple)
    for i in input_tuple:
        if not isinstance(i,tuple):
            if i == "class" or i == "def":
                temp += i+" "
            elif i == "conddef" or i == "args":
                temp += ""
            else:
                temp += i
        else:
            #TENTO RIADOK NEVIEM NACO JE
            if len(i) >= 3:
                #print("I",i)
                if len(i) > 3:
                    print("POZORRRRR")
                if (i[0] == "\n" and i[1] == "\t"):
                    temp += i[0]
                    if not isinstance(i[2],tuple):
                        output_list.append(temp)
                        output_list.append([i[2]])
                        temp = ""
                        #temp += i[2]
                    else:
                        #print(i[2])
                        my = []
                        tet = ""
                        for k in i[2]:
                            if isinstance(k,tuple):
                                if tet != "":
                                    my.append(tet)
                                    #tet = ""
                                #print("TET",tet)
                                otp_temp = edit_tuple(k)
                                #my.append(otp_temp)
                                #print("AAAA",otp_temp, len(otp_temp))
  
                                tet = ""
                                
                                #TUTO CAST SOM MENIL POSLEDNU
                                #if len(otp_temp) == 1:
                                for k in otp_temp:
                                    my.append(k)
                                #else:
                                    #my.append(otp_temp)                  
                            else:
                                if k != "funcdef" and k != "classdef" and k!= "conddef" and k!="args":
                                    tet += k
                                if k == "\n":
                                    my.append(tet)
                                    tet = ""
                        if tet != "":
                            if len(my) == 0:
                                my.append(tet)
                            else:
                                my.append(tet)
                        if temp != "":        
                            output_list.append(temp)
                            temp = ""
                        if my != []:
                            output_list.append(my)
                else:
                    temp += i[0]
                    if isinstance(i[1],tuple):
                        kuk = edit_tuple(i[1])
                        temp += kuk[0]
                        temp+=i[2]
                    else:
                        temp += i[1]+i[2]
            else:
                #print("KRATKE I",i)
                if i[0] == "args":
                    #print(edit_tuple(i[1]))
                    test = edit_tuple(i[1])
                    temp += test[0]
                else:
                    print("UNEXPECTED BEHAVIOR: 1")
    
    if temp != "":
        output_list.append(temp)
    
    return output_list 

def treeWalk(node):
    print(type(node), node.__dict__)
    for n in ast.iter_child_nodes(node):
        for x in n.__dict__:
            y = getattr(n, x)
            print(x,y)
        #print("synom je:", type(n), n.__dict__)
    for n in ast.iter_child_nodes(node):
        treeWalk(n)

def parsePart(input):
    try:
        input_a = print_my_list(input,1)
        n = ast.parse(input_a)
        return n
    except Exception as error:
        #e = [error.args[1][1],error.args[1][2],error.args[1][3]]
        print("ERROR: ", error)
        return error


def parseWithAst(my_list):
    errors = []
    outputs = []
    if not isinstance(my_list[0], list):
                #print("vynimka")
                input = print_my_list(my_list,1)
                output = parsePart(input)
                if isinstance(output,Exception):
                    errors.append(output)
                else:
                    outputs.append(output)
                return errors, outputs
    for x in my_list:
            input = print_my_list(x,1)     
            output = parsePart(input)
            if isinstance(output,Exception):
                errors.append(output)
                if isinstance(x,list):
                    for y in x:
                        output = parseWithAst(y)
                        #if isinstance(output,Exception):
                        #     errors.append(output)
                        #else:
                        #    outputs.append(output)
                             
            else:
                outputs.append(output)
    return errors, outputs

def traverseAstTrees(my_list):
    for x in my_list:
        print("-----------------------------------")
        treeWalk(x)
        print("-----------------------------------")

"Class to work with, provides methods to parse python code effectively"
class PParser():    
    "Constructor of our class"
    def __init__(self, my_input, is_file):
        #Set tokens used
        self.tokens = MyLexer1.tokens
        
        if is_file:
            #Set filename, open it and read
            self.filename = my_input
            f = open(self.filename)
            self.data = f.read()
        else:
            self.data = my_input
        
        #Create our lexer
        self.lexer = MyLexer1.PythonLexer()
        
        #Lex the input
        self.lexer.input(self.data)
        
        #Parse given folder
        if is_file:
            self.output = MyParser1.ParseFile(self.filename, self.lexer)
        else:
            self.output = MyParser1.ParseInput(self.data, self.lexer)
        #Transfer output into list
        self.output_list = first_phase(self.output)
    
    "Function to print token values"
    def print_tokens(self, filename):
        f = open(self.filename)
        data = f.read()
        self.lexer.input(data)
        for tok in self.lexer:
            print(tok)
    
    "Parse our output and return errors"    
    def parse_with_ast(self):
        self.errors, self.out = parseWithAst(self.output_list)
        return self.errors,self.out
