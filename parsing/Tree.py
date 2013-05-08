'''
Created on Apr 22, 2013

@author: Lubo
'''

def tree(var, level=1, outstr=''):
    #Takes a var, prints it out as nested aligned list

    if var is None:
        #Just return a new line:
        #outstr+=' \n'
        return ""
    elif isinstance(var, (int, float, complex, str, bool)):
        #Single value, simply add the fucker
        outstr+=' '+str(var)
        outstr+=' \n'
    elif isinstance(var, (list, tuple)):
        #List with some specified order, print in order
        outstr+='\n'
        k=0    #Manually index this
        for valchild in var:
            for tab in range(level-1):    # Print key
                outstr+='\t'
            outstr+='['+str(k)+'] => '
            k+=1    #Increment index
            newlevel = level + 1
            outstr = tree(valchild,newlevel,outstr)
    elif isinstance(var,(dict)):
        #List with keys and values, no order
        outstr+='\n'
        for k,valchild in sorted(var.iteritems()):
            for tab in range(level-1):    # Print key
                outstr+='\t'
            outstr+='['+str(k)+'] => '
            newlevel = level + 1
            outstr = tree(valchild,newlevel,outstr)
    else:
        #It doesn't qualify as any of the above cases
        outstr+=' '+str(var)
        outstr+=' \n'
    return outstr

def treeprint(var):
    #Wrapper for tree
    outstr = tree(var)
    print (outstr)
    return outstr    #Available to caller for wider use