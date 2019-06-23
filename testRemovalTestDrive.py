import ReadBatFile as rbf
import os

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