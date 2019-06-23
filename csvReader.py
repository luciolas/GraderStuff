import csv
import os
import xlrd

userstomark = []
graderid = 'peixian.c'
def GetNextDifference(seq, startidx = 0, val='',  ignoreEmpty = True):
        """
        :param seq: A list of values
        :param startidx: THe starting index to search from. Defaults to 0
        :param val: The value to search for
        :param ignoreEmpty: Ignore empty cells, or not.
        """
        i = startidx
        seq_ = seq[i:]
        for i in range(len(seq_)):
                cell = seq_[i]
                if cell.ctype == xlrd.XL_CELL_EMPTY:
                        if not ignoreEmpty:
                                break
                elif val not in cell.value:
                        break
        return i + startidx
                        
        

def GetIdxFromSequence(seq, searchVal):
        """
        :param seq: A list to search the value from
        :param searchVal: Value that belongs in the list for comparison. The function uses
        searchVal in seq.values
        """
        idx = 0
        for s in seq:
                if searchVal in s.value:
                        return idx
                idx +=1

def ExtractStudentsToGrade(assignmentExcelPath):
        """
        :param assignmentExcelPath: The xlsx in which Swavak had assigned the students to 
        different graders.
        """
        assert os.path.isfile(assignmentExcelPath), 'Excel file not found!'
        
        workbook = xlrd.open_workbook(assignmentExcelPath)
        worksheet = workbook.sheet_by_index(0)
        labels = worksheet.row(0)
        getgradercolx = GetIdxFromSequence(labels, 'Grader')
        getstdcolx = GetIdxFromSequence(labels, 'Student ID')
        gradercol = worksheet.col(getgradercolx)
        studcol = worksheet.col(getstdcolx)
        getgraderrowx = GetIdxFromSequence(gradercol, graderid)
        getnextdifferencerowx = GetNextDifference(gradercol, getgraderrowx, graderid)
        print(getgraderrowx)
        print(getnextdifferencerowx)

        newlist = [s.value for s in studcol[getgraderrowx:getnextdifferencerowx]] 
        return newlist
        


# currdir = os.path.dirname(__file__)
# ExtractStudentsToGrade(os.path.normpath(os.path.join(currdir, 'Assignment1.xlsx')))