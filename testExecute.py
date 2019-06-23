import ReadBatFile as rbf


bo = rbf.CreateBatFileObject()

t,_ = bo.ExecuteExe(r"C:\Users\user\Desktop\CS225GRADERSTUFF\Extracted\a.hiaplee_cs225_1\Output\cl\vector2d_test.exe")

t.strip('\r')
print(t.encode())
nameOutputTextwithDir = r"C:\Users\user\Desktop\CS225GRADERSTUFF\Extracted\a.hiaplee_cs225_1\Output\cl\test.txt"
with open(nameOutputTextwithDir, 'w', newline='') as txt:
    txt.write(t)