import cv2 
import numpy as np
from skimage.measure import compare_ssim  as sim
import os


picext = ['.jpg', '.bmp', '.png']

def isAPictureFile(filenamepath):
    for ext in picext:
        if filenamepath.endswith(ext):
            return True
    return False

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)

    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def FixDimensions(modelImage, imageB):
    originaldim = modelImage.shape
    return cv2.resize(imageB, (originaldim[0], originaldim[1]), interpolation=cv2.INTER_LINEAR)
    

def CompareTwoImages(original, imageb):
    org = cv2.imread(original)
    ib = cv2.imread(imageb)
    originaldim = org.shape
    bimgdim = ib.shape
    if (originaldim != bimgdim):
        print('Dimension deviation found!')
        ib = FixDimensions(org, ib)
    # convert the images to grayscale
    coriginal = cv2.cvtColor(org, cv2.COLOR_BGR2GRAY)
    cib = cv2.cvtColor(ib, cv2.COLOR_BGR2GRAY)
    # compare with the functions
    try:
        m = mse(coriginal,cib)
        s = sim(coriginal, cib)
    except ValueError as e:
        print (e)
        return (-10.0, -10.0)
    else:
        # print("MSE %.2f, SSIM: %.2f" % (m,s))

        return (m,s)

def FindPictureFilesInDirectory(otherDir):
    sourceFiles = []
    for dirpath, dirs, filenames in os.walk(otherDir):
        for f in filenames:
            if isAPictureFile(f):
                sourceFiles.append(os.path.normpath(os.path.join(dirpath,f)))
    return sourceFiles

def FindPairs(sourceFiles, userFiles):
    pairs = []
    for s in sourceFiles:
        for u in userFiles:
            sfilename = os.path.basename(s)
            ufilename = os.path.basename(u)
            if ((sfilename == ufilename) or 
            (sfilename in ufilename) or (ufilename in sfilename)):
                pairs.append((s, u))
                break
    return pairs


def Compare(sourceOutputDir, userOutputDir):
    sourceFiles = FindPictureFilesInDirectory(sourceOutputDir)
    userFiles = FindPictureFilesInDirectory(userOutputDir)
    pairs = FindPairs(sourceFiles,userFiles)
    # print(pairs)
    for pair in pairs:
        resultpair = CompareTwoImages(pair[0],pair[1])
        print(pair)
        print(resultpair)


class UserObject:
    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.outputdir = kwargs['outputdir']


extractedDir = r"C:\Users\user\Desktop\CS225_Assignemnt2\Extracted"  
sourceDir = r"C:\Users\user\Desktop\CS225_Assignemnt2\output"
# targetDir = r"C:\Users\user\Desktop\CS225_Assignemnt2\Extracted\jingkang.yeo_cs225_2\Output"
# Compare(sourceDir,targetDir)
users = []
usersoutputdir = []
userobjects = []
for dirpath, dirnames, filenames in os.walk(extractedDir):
    for dirname in dirnames:
        users.append(dirname.split('_')[0])
    break
# print(users)
for dirpath, dirnames, filenames in os.walk(extractedDir):
    for dirname in dirnames:
        if dirname == 'Output':
            usersoutputdir.append(os.path.normpath(os.path.join(dirpath,dirname)))
            break
# print(usersoutputdir)
for i in range(len(users)):
    userobjects.append(UserObject(username= users[i], outputdir=usersoutputdir[i]))


for user in userobjects:
    print('--------Testing on ' + user.username + '----------\n\n')
    Compare(sourceDir, user.outputdir)
    print('\n----------end--------------\n')