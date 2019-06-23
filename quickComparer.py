import os
from os.path import isfile, join
import difflib as diff
import hashlib as hashl

class ComparerObject:
    def __init__(self, sourceOutputDir):
        self.sourceOutputDir =sourceOutputDir
        self.sourceOutput = []
        for dirpath, dirs, filesnames in os.walk(sourceOutputDir):
            for file in filesnames:
                if file.endswith('.txt'):
                    self.sourceOutput.append(join(dirpath,file))

    def CompareTextFilesInDirectory(self, inputDir):
        result = []
        inputfiles = []
        #Retrieve all texts
        for dirpath, _, filenames in os.walk(inputDir):
            for file in filenames:
                if file.endswith('.txt'):
                    inputfiles.append(join(dirpath,file))
        # compare source and input
        print(self.sourceOutput)
        for so in self.sourceOutput:
            test = True
            for io in inputfiles:
                difflines = []
                with open(so, 'r', newline="\r\n") as fso:
                    with open(io, 'r', newline="\r\n") as iso:
                        f1content = fso.readlines()
                        f2content = iso.readlines()
                        linecount = len(f1content) if (len(f1content) < len(f2content)) else len(f2content)
                        for i in range(0, linecount):
                            f1 = f1content[i]
                            f2 = f2content[i]
                            hashobj = hashl.sha256(f1.encode()).digest()
                            hashobj2 = hashl.sha256(f2.encode()).digest()
                            if hashobj != hashobj2:
                                test = False
                                difflines.append((f1,f2))
                ok = 'O'
                if not test:
                    if len(difflines) > 0:
                        ok = 'X'
                    result.append((so,io, ok,difflines))
                else:
                    result.append((so,io, ok,difflines))
        return result

    # def DiffTextFiles(self, inputDir):