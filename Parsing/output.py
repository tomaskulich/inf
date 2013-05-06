'''
Created on Apr 22, 2013

@author: Lubo
'''
import string

def tree(var, level=1, outstr=''):
    
    if var is None:
        #Just return a new line:
        outstr+='D: \n'
        #return ""
    elif isinstance(var, (int, float, complex, str, bool)):
        #Single value, simply add the fucker
        #print("TOTO: ","'",str(var),"'")
        outstr+='A: '+str(var)
        outstr+=' \n'
    elif isinstance(var, (list, tuple)):
        #List with some specified order, print in order
        outstr+='C:'+str(len(var))+'\n'
        k=0    #Manually index this
        newlevel = level + 1
        for valchild in var:
            for tab in range(level-1):    # Print key
                outstr+='\t'
            outstr+='['+str(k)+'] => '
            k+=1    #Increment index
            outstr = tree(valchild,newlevel,outstr)

    else:
        #It doesn't qualify as any of the above cases
        outstr+='B: '+str(var)
        outstr+=' \n'
    return outstr

def treeprint(var):
    #Wrapper for tree
    outstr = tree(var)
    print (outstr)
    return outstr