import os
import re


Classes = []
constructorregex = '^(?:(\w+):{2}\w+)[(].*[)]\s*(?:[:]|[;]|[{])'
functionregex = '(?:(?:^\s+|)(\w+(?:&{0,2}|\*+)))\s+(?:(\w+)|(?:(\w+):{2}(\w+)))(?:(?:[(](.+)[)])|(?:[(][)]))(?:(?:.*\n)|(?:.*{)|(?:.*;))'

def GetLinesFromFile(inputfile):
    assert os.path.isfile(inputfile), str(inputfile) + " is not a file!"
    with open(inputfile, 'r') as cppfile:
        filecontentlines = cppfile.readlines()
        return filecontentlines


def GetFunctions(inputfile):
    assert os.path.isfile(inputfile), str(inputfile) + " is not a file!"
    results = []
    with open(inputfile, 'r', newline='') as somefile:
        regobj = re.compile(functionregex, flags=re.IGNORECASE|re.M)
        cregeobj = re.compile(constructorregex, flags=re.IGNORECASE|re.M)
        filecontent = somefile.readlines()
        i = 0
        for l in filecontent:
            cres = cregeobj.match(l)
            res = regobj.match(l) if cres == None else cres
            if res != None: 
                results.append((res,i))
            i +=1
    return results

def FilterFunctions(regexResults):
    newresult = []
    for r in regexResults:
        if 'return' in r[0].group(1):
            continue
        newresult.append(r)
        print (r[0].group(1))
    return newresult

inputfile = r"C:\Users\user\Desktop\CS225GRADERSTUFF\Extracted\a.hiaplee_cs225_1\Polygon.cpp"
results = GetFunctions(inputfile)
lines = GetLinesFromFile(inputfile)
results = FilterFunctions(results)
for r in results:
    linenum = r[1]
    if '{' in lines[linenum] and '}' not in lines[linenum]:
        print('Old indentation found {0} in line {1}'.format(lines[linenum],linenum))
    nextline = linenum + 1
    i = 0
    bracketstack = []
    if '{' in lines[nextline]:
        bracketstack.append('{')
        nextline+=1
    while (len(bracketstack) != 0):
        if('}' in lines[nextline]):
            bracketstack.pop()
            nextline+=1
            continue
        elif '{' in lines[nextline]:
            bracketstack.append('{')
        i+=1
        nextline+=1
    print('Lines in function {0}: {1}'.format(r[0], i))
        
        

        

    






