'''
Created on Apr 24, 2013

@author: Lubo
'''
#Imports we will use later on
import MyLexer1
import MyParser1
import Tree
import ast
#from ply import yacc

#Function to print token values
def print_tokens(input_lexer):
    for tok in input_lexer:
        print(tok)

#Use tokens from our lexer
tokens = MyLexer1.tokens

#We'll define the test input here
filename = "input_for_ply.py"

#Open the file, read it
f = open(filename)
data = f.read()

#Create our lexer
lexer = MyLexer1.PythonLexer()
#Lex the input
lexer.input(data)
#Print the tokens
#print_tokens(lexer)

#Parse input    
output = MyParser1.ParseThis(filename,lexer)

print("O",output)

#Print the tree representing our p values from MyParser1
#Tree.treeprint(output)

def print_my_list(my_list,ind_level):
    result = ""
    test = ind_level
    #print (test)
    for i in my_list:
        #print(type(i))  
        if isinstance(i,list):
            #ind_level += 1
            result += print_my_list(i,test +1)     
        else:
            help = ""
            #a = int(test / 2)+1
            #print(a)
            for x in range(1,test):
                help += "\t"
            count = i.count("\n")
            pomoc = i.replace("\n","\n"+help,count-1)
            result += help+pomoc
    return result
   
def tuple_to_string(input_tuple):
    output = ""
    for i in input_tuple:
        if isinstance(i,tuple):
            output += tuple_to_string(i)
        else:
            output += i
    return output  
   
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
    return output_list

#TODO vpredu je niekedy nic...Treba sa na to pozriet
def edit_tuple(input_tuple):
    output_list = []
    temp = ""
    for i in input_tuple:
        if not isinstance(i,tuple):
            if i == "class" or i == "def":
                temp += i+" "
            else:
                temp += i
        else:
            temp += i[0]
            if not isinstance(i[2],tuple):
                temp += i[2]
            else:
                my = []
                tet = ""
                for k in i[2]:
                    if isinstance(k,tuple):
                        if tet != "":
                            my.append(tet)
                            tet = ""
                        #TOTO SOM MENIL, pozor na to
                        #my.append(edit_tuple(k))
                        otp_temp = edit_tuple(k)
                        for k in otp_temp:
                            my.append(k)                  
                    else:
                        if k != "funcdef" and k != "classdef" and k!= "conddef":
                            tet += k
                if tet != "":
                    if len(my) == 0:
                        my.append(tet)
                    else:
                        my.append(tet)
                if temp != "":        
                    output_list.append(temp)
                if my != []:
                    output_list.append(my)
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

def parseWithAst(list):
    errors = []
    outputs = []
    for x in list:
        print("--------------------")
        print(x)
        print("--------------------")
        try:
            input = print_my_list(x,1)
            print(input)
            n = ast.parse(input)
            outputs.append(n)
            #treeWalk(n)
        except Exception as error:
            e = [error.args[1][1],error.args[1][2],error.args[1][3]]
            errors.append(e)
            print("ERROR")
            print(error)
            print("ERROR")
            # TODO toto je pokus o rekurzivne volanie ked nam to na tej casti padne aby sme to zavolali na vsetkych synov....
            # TODO treba domysliet ako ukladat chyby aby sme vedeli presne v ktorej casti, lebo to ze mame riadok a znak nam nepomoze ked to volame iba na nejakych podlistoch-> ine cisla riadkov...
            if isinstance(x,list):
                for y in x:
                    parseWithAst(y)     
        print("--------------------------------------")
    return errors, outputs

def traverseAstTrees(list):
    for x in list:
        print("-----------------------------------")
        treeWalk(x)
        print("-----------------------------------")

output_strings = []
output_strings = first_phase(output)
#print(output_strings)
#print(str(output_strings))
#aaaa = print_my_list(output_strings,0)
#ast.parse(aaaa)
#print(aaaa)
#print("===================")
#bbb = print_my_list(output_strings[1],1)
#print(len(bbb))
#print(bbb)
er, out = parseWithAst(output_strings)
print("ERORS: ",er)
traverseAstTrees(out)
#ast.parse("de test():")