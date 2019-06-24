import os
from os import listdir, walk
from os.path import isfile, join
import copy
import subprocess
from subprocess import Popen, PIPE
import shutil as shu
import time

batfilename = 'build.bat'

vcvarspath = r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
    

compileroptions = ['cl', 'g++']

__all__ = ['ExecuteBatFile']

def RelativePath(pathA, pathB):
    p = pathA,pathB if len(pathA) < len(pathB) else pathB,pathA
    shorterPath = copy.deepcopy(p[0])
    longerPath = copy.deepcopy(p[1])
    result = ''
    while True:
        bname = os.path.basename(os.path.dirname(shorterPath))
        i = longerPath.rfind(bname)
        # print(bname)
        if i != -1:
            i = i+len(bname)
            result = longerPath[i:]
            break
        elif len(shorterPath) > 1:
            j = shorterPath.find(bname)
            shorterPath = shorterPath[:j]
        else:
            break
    # print(result)
    return result

class UserObject:
    def __init__(self, userID,userDir, tb):
        self.userID= userID
        self.mainDir = userDir
        self.score = 100
        self.tbs = tb
        pass

    def ReduceScoreForWrongCompile(self):
        self.score -= 100
    def ReduceScoreForWrongOutput(self):
        self.score -= 20

    def __str__(self):
        return str('UserID:' + str(self.userID) + '\nmainDir:' + str(self.mainDir)
                    + "\nScore: " + str(self.score)) 
    

class TestObject:
    def __init__(self, listofcpps, outputname):
        self.inputlist = listofcpps
        self.outputexe = outputname
        self.objectstring = ''
        self.isExecutable = False
        self.isFailTest = False
        self.isFailCompile = False
        self.isMatchOutput = False
        self.outputresultstringd = {}

    def SetSourceDir(self, source):
        for i in range(len(self.inputlist)):
            cpp = self.inputlist[i]
            for dirpath, dirnames, filenames in os.walk(source):
                if cpp in filenames:
                    cpp = join(dirpath, cpp)
                    self.inputlist[i] = cpp
                    break

    def SetUserMainDir(self, mainDir):
        for i in range(len(self.inputlist)):
            cpp = self.inputlist[i]
            for dirpath, dirnames, filenames in os.walk(mainDir):
                if cpp in filenames:
                    cpp = join(dirpath, cpp)
                    self.inputlist[i] = cpp
                    break
                    
    def Test(self,compileoptions):
        pass

    def __str__(self):
        return str('CPP files:' + str(self.inputlist) + '\nOutputExe:' + str(self.outputexe)
                    + "\n" + "Fail Test: " + str(self.isFailTest) + "\nCompile Fail Test: " + str(self.isFailCompile)
                    + "\nMust Match: " + str(self.isMatchOutput))
        


class BatFile:
    """
    Describes a batfile data!\n
    Attributes:
    ==========
    compileroptd -- A dict of compile options\n
    compilervar -- the compile variable used in the batfile\n
    TestObjects -- the list of tests as dictated in the batfile\n
    sourcedir -- the source dir (deprecated)\n
    """
    def GenerateTestObjects(self, lines):
        """
        1) Searches for the 'compile' variable. That variable name
            will determine if a line contains a TestObject\n
        2) $compile nad $mustmatch are additiona information that is in the batfile to differentiate 
            the different types of tests.
        """
        compilevarz = self.compilervar
        checkerdict = { '$compile' : False, '$mustmatch': False}
        comvar = ''.join(['%',compilevarz,'%'])
        for l in lines:
            sp = l.split()
            if 'REM$' in l:
                for key, _ in checkerdict.items():
                    if key in l:
                        checkerdict[key] = bool(int(sp[2]))
                        break
                continue
            batfilecmd = copy.deepcopy(l)
            for key, val in self.batfilevariablesd.items():
                batfilevar = ''.join(['%', key, '%'])
                batfilecmd = batfilecmd.replace(batfilevar, val)

            if (compilevarz in l):
                splittedbfc = batfilecmd.split()
                cppfiles = []
                outputname =''
                for s in sp:
                    if comvar in s:
                        perce = s.rfind(comvar)
                        if perce == -1:
                            outputname = s
                        else:
                            outputname = s[perce+len(comvar):]

                for s in splittedbfc:
                    if (s[0] != '/') and (('.cpp' in s) or ('.obj' in s)):
                        cppfiles.append(s)
                tb = TestObject(cppfiles, outputname)
                # print(cppfiles)
                tb.isFailCompile = not checkerdict["$compile"]
                tb.isMatchOutput = checkerdict["$mustmatch"]
                
                tb.objectstring = batfilecmd
                # print(batfilecmd)
                self.TestObjects.append(tb)
            elif len(sp) > 0 and ('.exe' in sp[0]):
                testexe = sp[0]
                tb = TestObject([], '')
                tb.outputexe = testexe
                tb.isFailCompile = not checkerdict["$compile"]
                tb.isMatchOutput = checkerdict["$mustmatch"]
                tb.objectstring = batfilecmd
                tb.isExecutable = True
                self.TestObjects.append(tb)
                


    def SearchForCompilerOptions(self, lines):
        """
        Searches for the compiler variable in the batfile.
        Stores the compiler options for later use.
        """
        for l in lines:
            sp = l.split()
            if len(sp) > 1 and 'set ' in l:
                eqop = l.find('=')
                if eqop == -1:
                    continue
                lastsetop = l.find('set')+4
                lastcharnextline = l.rfind('\n')
                batfilevar = l[lastsetop:eqop]
                compileropt = l[eqop+1:lastcharnextline]
                
                compilecmd = compileropt.split()[0]
                if compilecmd in compileroptions:
                    self.compileroptd[compilecmd] = compileropt
                    self.compilervar = batfilevar
                self.batfilevariablesd[batfilevar] = compileropt

    def CallSubprocess(self, compileOps, files, outpath,tb, userobject):
        """
        Opens a command prompt and init the environment with vcvarsall.bat
        Then call the various compiler with compileOps
        """            
        if len(files) == 0:
            return b'No input files\n'
        arg = compileOps + outpath
        arg = arg.split()
        arg = arg + files
        lrawcmdobject = tb.objectstring.split()
        for i in range(1, len(lrawcmdobject)):
            for f in files:
                if lrawcmdobject[i] in f:
                    lrawcmdobject[i] = f
                    # print(lrawcmdobject[i])
        # print(lrawcmdobject)
        myenv = copy.deepcopy(os.environ)
        myenv["PATH"] = myenv["PATH"] +';'+r"C:\cygwin64\bin"+";"

        # init cl environment
        clenv = join(vcvarspath, r"vcvarsall.bat")
        enablecl = os.path.isfile(clenv)
        cmdprog = ['cmd', '/q']
        additionalarg = "\"" + clenv + "\""  + r" x86"
        additionalarg = os.path.normpath(additionalarg)
        
        res = ''
        # for i in range(len(arg)):
            # res = res+ ' ' + arg[i]
            # print(res)
        for i in range(len(lrawcmdobject)):
            res = res + ' ' + lrawcmdobject[i]

        
        p = Popen(cmdprog, stdin=PIPE, stdout=PIPE,stderr=subprocess.STDOUT)
        ##init cl environment
        if enablecl:
            p.stdin.write((additionalarg + "\n").encode())
            p.stdin.flush()

        ## change to user's working dir
        changedircmd = ' '.join(['cd',os.path.dirname(outpath),'\n'])
        p.stdin.write(changedircmd.encode())
        p.stdin.flush()

        ## execute the task
        output= p.communicate((res + "\n").encode())[0]
        # output= p.communicate((lrawcmdobject + "\n").encode())[0]
        print('Command sent ' + res)
        return output


    def RunCompileTasks(self, testCodeDir, userDir,outputDir,userobject, compiler, userfile):
        """
        Run all testobjects on different user directories. Each Userobject contains their
        own set of testobjects.
        """
        newtbs = userobject.tbs
        #copy test code files to userDir
        for dirpath, _, filenames in os.walk(testCodeDir):
            for f in filenames:
                if f.endswith('.bat'):
                    continue
                src = os.path.join(dirpath, f)
                userpath = os.path.join(userDir, f)
                if os.path.exists(userpath):
                    userfile.write("\n-----Warning----\n\n  Existing file:{} found!".format(userpath))
                shu.copy(src, userpath)
        for tb in newtbs:
            if tb.isExecutable:
                continue
            tb.SetSourceDir(userDir)
            # newoutpath = join(outputDir,compiler)
            newoutpath = outputDir
            if not os.path.exists(newoutpath):
                os.makedirs(newoutpath)
            outfullpath = join(newoutpath, tb.outputexe)
            outputtext = self.CallSubprocess(self.compileroptd[compiler], tb.inputlist, outfullpath,tb, userobject)
            tb.outputresultstringd[compiler] = outputtext
            userfile.write("\nCompiler: "+compiler+'\n')
            userfile.write(outputtext.decode('utf-8'))
            print("\nCompiler: "+compiler+'\n')
            print(outputtext.decode('utf-8'))
    
    def ExecuteExe(self, exeFullPath, tb):    
        """
        Executes exe files as dictated in the batfile.
        """ 
        # if not os.path.exists(os.path.normpath(exeFullPath)):
        #     return exeFullPath + ": ERROR: Cannot find executable!", False
        print('---------------------Executing exe-----------------------\n\n')
        rawcmdstring = tb.objectstring.split()[1:]
        # print(rawcmdstring)
        lcmdstring = [exeFullPath] + rawcmdstring
        cmdstring = ' '.join(lcmdstring)
        # print(lcmdstring)
        cmdprog = ['cmd', '/q']
        p = Popen(cmdprog,  stdin =PIPE, stdout=PIPE,stderr=subprocess.STDOUT)
        ## change to user's working dir
        changedircmd = ' '.join(['cd',os.path.dirname(exeFullPath),'\n'])
        p.stdin.write(changedircmd.encode())
        p.stdin.flush()
        
        output = p.communicate((cmdstring +'\n').encode())[0]
        return output.decode('utf-8'), True

    def RunExecTasks(self, outputDir, testCodeDir, userobject, compiler,userfile):
        """
        Executes exe files while checking if the results match the requirements
        of a TestObject.
        We also calculate the score for each userobject
        """
        for tb in userobject.tbs:
            if not tb.isExecutable:
                continue
            
            # compileOutputPath = join(outputDir, compiler)
            compileOutputPath = outputDir
            exefilefullpath = join(compileOutputPath, tb.outputexe)
            
            if tb.isFailCompile:
                if not os.path.exists(exefilefullpath):
                    # ok
                    pass
                else:
                    userobject.ReduceScoreForWrongCompile()
                continue
            elif tb.isMatchOutput:
                namewoExt = tb.outputexe[:tb.outputexe.rfind('.exe')]
                nameOutputText = namewoExt + '.txt'
                nameOutputTextwithDir = join(compileOutputPath, nameOutputText)
                out, ok = self.ExecuteExe(exefilefullpath,tb )
                
                if not ok:
                    userobject.ReduceScoreForWrongCompile()
                # with open(nameOutputTextwithDir, 'w', newline='') as txt:
                userfile.write(out)
                    
    def ExecuteBatFile(self, testCodeDir, userDir,outputDir, outputfilepath = ''):
        """
        Interface for user to run
        """
        tbs = copy.deepcopy(self.TestObjects)
        userid = os.path.basename(userDir).split('_')[0]
        uo = UserObject(userid,userDir, tbs)
        for compiler in self.compileroptd:
            if outputfilepath == '':
                outputfile = open(join(uo.mainDir, uo.userID+".txt"), 'w+')
            else:
                outputfile = open(outputfilepath, 'a+')
            self.RunCompileTasks(testCodeDir, userDir,outputDir,uo, compiler,outputfile)
            self.RunExecTasks(outputDir, testCodeDir,uo, compiler,outputfile)
        outputfile.close()
        return uo
                
    def __init__(self, buildfilepath):
        self.compileroptd = {}
        self.compilervar =''
        self.batfilevariablesd = {}
        self.TestObjects = []
        self.sourcedir = ''
        self.testdrivesNames = []
        if os.path.isfile(buildfilepath):
            with open(buildfilepath, 'r') as batfile:
                lines = []
                while True:
                    line = batfile.readline()
                    if not line:
                        break
                    lines.append(line)                                
                self.SearchForCompilerOptions(lines)
                self.GenerateTestObjects(lines)

def CreateBatFileObject():
    """
    Interface for user to create a batfile. 
    Uses the first batfile it finds, from the directory 
    this script resides in.
    Batfile must use the ext '.bat'\n
    -> BatFile
    """
    currdir = os.path.dirname(__file__)
    batfile = None
    for dir, _, filenames in os.walk(currdir):
        found = False
        if os.path.basename(dir) == 'source':
            for f in filenames:
                if f.endswith('.bat'):
                    batfile = BatFile(join(dir, f))
                    batfile.sourcedir = dir
                    found = True
                    break
        if found:
            break
    return batfile





