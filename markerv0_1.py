import os
from os import listdir, walk
from os.path import isfile, join
from zipfile import ZipFile
import ReadBatFile as rbf
from quickComparer import ComparerObject
import csvReader as pxcsv
import csv

## ASsignment number
assnumber = '2'

zipcounts = 0

csvfilename = 'A2.csv'

originalGradeCSV = 'Assignment2.xlsx'


def RemoveExtension(src):
        ok,basename = checkfilenamesandrename(src)
        if not ok:
                return ''
        i = basename.rfind('.')
        
        return basename[:i]


def GetUser(src):
        """
        src -- string\n
        Get the digipen login id component of the name, 
        ASSUMING it is in the format peixian.c_blahblah_blah.whateverextension 
        :return: -> list
        """
        basename = os.path.basename(src)
        splitz = basename.split('_')
        return splitz[0]


def checkuser_mod_assignmentnumber(src, stringAsgNumber):
        splitz = src.split('_')

        if(len(splitz) is not 3):
                return False
        anumber = splitz[2].split('.')[0]

        if(anumber is not stringAsgNumber):
                return False
    
        if(splitz[1] != 'cs225'):
                return False
        
        return True


def checkfilenamesandrename(src):
        """
        Check the filename by splitting
        Check the ext == .zip
        Next, we call checkuser_mod_assignmentnumber() which is a helper to further 
        check if someone wrote cs225A, wrong assignemnt number, or
        I.E peixian.c_cs225_1.zip when split('_') we should get 3 items
        ['peixian.c', 'cs225', '1.zip']. Anything more, means the name is fucked
        """
        basename = os.path.basename(src)
        res = '_'
        if(basename.endswith('.zip')):
                splitter = basename.split('_')
                lenofsplit = len(splitter)
                lastfew = splitter[lenofsplit-3: lenofsplit]
                res = res.join(lastfew)
                if(checkuser_mod_assignmentnumber(res, assnumber)):
                        return True,res
        return False,res

def GetSourceFilesInPath(batfileobject, path):
        assert os.path.exists(path), 'Path does not exists!'
        testdrivedir = batfileobject.sourcedir;
        filesfullpath= None
        for dirs, _, filenames in os.walk(testdrivedir):
                testdrivefiles = [f for f in filenames if f.endswith('.cpp')]
                break
        for ds, _, filenames in os.walk(path):
                filesinpath = [os.path.join(ds, f) for f in testdrivefiles if f in filenames]
                break

        return filesinpath        


currentdir = os.path.dirname(os.path.realpath(__file__))
maindir = currentdir
allfiles = []

# Retrieve all files in the directory that contains this script
for (dirpath, dirnames, filenames) in walk(maindir):
        allfiles.extend(join(dirpath, filename) for filename in filenames)

namewrongcount = 0
wrongname = []
zipfiles = []
Users = []

# Get all zip files and store in zipfiles[]
# Digipen login ids are also parsed and stored in Users[]
for file in allfiles:
        if(not file.endswith('.zip')):
                continue
        ok, parsedname = checkfilenamesandrename(file)
        user = file.split('_')[0]
        if not ok:
                namewrongcount+=1
                wrongname.append(file)
                Users.append([user,-5])
                continue
        dir = os.path.dirname(file)
        
        Users.append([user,0])
        os.rename(file, join(dir, parsedname))
        file = join(dir,parsedname)
        zipfiles.append(file)
        zipcounts +=1

print('Accounted Zips in dir: ' + str(zipcounts) + '\nWrong Count: ' + str(namewrongcount))
for w in wrongname:
        print(w)

# Create a main directory call Extracted in the same dir as this script
extractdir = join(maindir,'Extracted')
if not os.path.exists(extractdir):
        os.makedirs(extractdir)


studentIDlist = pxcsv.ExtractStudentsToGrade(os.path.normpath(os.path.join(currentdir, originalGradeCSV)))
print(studentIDlist)
# We begin extracting all the zipfiles in to Extracted folder
# Extracted files are extracted into Extracted/digipen.id_cs225_assignmentNo/
extracteddirs = []
for zp in zipfiles:
        with ZipFile(zp, 'r') as zip:
                bname = os.path.basename(zp)
                userid = bname.split('_')[0]
                if userid not in studentIDlist:
                        continue
                print("Student to grade: " + userid)
                bnamenoext = RemoveExtension(bname)

                d = join(extractdir, bnamenoext)
                extracteddirs.append(d)
                zip.extractall(d)

# Generate a BatFileObject
bfo = rbf.CreateBatFileObject()


#Create an Output folder in every Extracted/digipen.id
# I.E Extracted/digipen.id/Output/
for ed in extracteddirs:
        outputdir = join(ed, 'Output')
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
sourcedir = join(os.path.dirname(__file__), 'output')
qc = ComparerObject(sourcedir)


# Run the bat file on each ed (extracted directory)
userobjects=[]

for ed in extracteddirs:
        outputdir = join(ed, 'Output')
        userobject = bfo.ExecuteBatFile(bfo.sourcedir, ed,ed)
        
        userobjects.append(userobject)
        res = qc.CompareTextFilesInDirectory(ed)
        for r in res:
                if r[2] == 'O':
                        print(r)


        t = GetSourceFilesInPath(bfo, ed)
        ## Remove TestDriveFilesFrom directory
        for p in t: os.remove(p)

## do some csv shit
csvfilename = 'A2_test.csv'
with open(csvfilename, 'w', newline='') as csvfile:
        fieldnames = ['Userid', 'Grade']
        dictwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        dictwriter.writeheader()
        spamwriter = csv.writer(csvfile,delimiter = ' ', quoting=csv.QUOTE_MINIMAL)

        for userobject in userobjects:
                spamwriter.writerow([userobject.userID,userobject.score] )

        


