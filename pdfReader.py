import PyPDF2

keywords = ['.cpp', '.h', '.*']

def GetDeliverables(path):
    pdfobject = open(path,'rb')
    pdfreader = PyPDF2.PdfFileReader(pdfobject)
    pages = pdfreader.numPages
    count = 0
    # while count < pages:
    #     pageobj = pdfreader.getPage(count)
    #     text = pageobj.extractText()
    #     if text == '':
    #         continue
    #     print(text)
    #     count +=1 

    pageobj = pdfreader.getPage(7)
    text = pageobj.extractText()
    print(text)


GetDeliverables(r'C:\Users\user\Desktop\CS225_Assignemnt2\specification\Assignment_02.pdf')