import xlwt

wbk = None

class CreateExcel():
    
    def __init__(self):
        self.wbk = xlwt.Workbook()
        self.sheet = self.wbk.add_sheet('BSP_Auto_Sheet', cell_overwrite_ok=True)

    def getWbk(self):
        return self.wbk

    def getSheetins(self):
        return self.sheet

    def createSheetAndTitle(self):
    
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 0x00fd
    
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
    
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 24
        
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THICK
        borders.right = xlwt.Borders.THICK
        borders.top = xlwt.Borders.THICK
        borders.bottom = xlwt.Borders.THICK
    
        font2 = xlwt.Font()
        font2.name = 'Times New Roman'
        font2.bold = True
        font2.height = 0x00ed
    
    
        sheet_style_title = xlwt.XFStyle()
        
        sheet_style_title.font = font
        
        self.selfWrite(0,0,'BSP Automation Statistic', sheet_style_title)
        
        #Add title
        sheet_style_title.font = font2
        sheet_style_title.borders = borders
        sheet_style_title.pattern = pattern
        sheet_style_title.alignment = alignment
        
        
        self.selfWrite(3,0,'State', sheet_style_title)
        self.selfWrite(3,1,'Case ID', sheet_style_title)
        self.selfWrite(3,2,'Priority', sheet_style_title)
        self.selfWrite(3,3,'Module', sheet_style_title)
        self.selfWrite(3,4,'Case Name', sheet_style_title)
        self.selfWrite(3,5,'Note', sheet_style_title)
    
    
    def selfWrite(self, start_pos, end_pos, content, style):
        self.sheet.write(start_pos, end_pos, content, style)
    
    
    def addCentent(self, start_pos, content):
        
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_JUSTIFIED
        
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.DOTTED
        borders.right = xlwt.Borders.DOTTED
        borders.top = xlwt.Borders.DOTTED
        borders.bottom = xlwt.Borders.DOTTED
    
        font2 = xlwt.Font()
        font2.name = 'Times New Roman'
        
        style = xlwt.XFStyle()
        style.font = font2
        style.borders = borders
        style.alignment = alignment
    
        self.selfWrite(start_pos, 0, content[0], style)
        self.selfWrite(start_pos, 1, content[1], style)
        self.selfWrite(start_pos, 2, content[2], style)
        self.selfWrite(start_pos, 3, content[3], style)
        self.selfWrite(start_pos, 4, content[4], style)
        self.selfWrite(start_pos, 5, content[5], style)
    
    def saveExcel(self, excel_name):
        self.wbk.save(excel_name)

def main():
    create_sheet = CreateExcel()
    create_sheet.createSheetAndTitle()

    create_sheet.addCentent(4,['bsp1aaaaaaaaaaaaaaaa','cccc','dddd','eee','ffff'])
    create_sheet.addCentent(5,['bsp1aaaaaaaaaaaaaaaa','cccc','dddd','eee','wwww'])
    
    create_sheet.saveExcel('./xxx.xls')


if __name__ == '__main__':
    main()
    print 'finished'

