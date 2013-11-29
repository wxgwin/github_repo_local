r'''Parse Test Link automation file and test case file
This classes:
  -- ParseTLautoFile() is class for parsing Test Link automation file
  -- ParseTLcaseFile() is class for parsing test case file
'''
import copy

#import globalVariable
from  staticMethods import *

class ParseTLautoFile(object):
    '''ParseTLautoFile(Test Link file, system logger)
    This functions:
    -- getCasefileName() : Add absolute path and name of test case file to 
                           global variable. 
    '''

    def __init__(self,file_name,logger_obj):
        self.file_name = file_name
        self.logger_obj = logger_obj

    def getCasefileName(self):
        'Get parameter value tl_auto_cfgSave from file c:\TL_AESDK.txt'

        try:
            file_fp = open(self.file_name,'r')
            file_content = file_fp.readlines()

            #Get test case file path from test link auto file 
            for lines in file_content:
                tl_uf_file = re.search('tl_auto_cfgSave\s+=\s+(.*)', lines, re.I)
                
                if tl_uf_file:
                    self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLautoFile]',\
                                                'Get parameter from TL_AUTO'))
                    globalVariable.serial_config['case_fldr'] = \
                    os.path.dirname(tl_uf_file.groups()[0])
                    return tl_uf_file.groups()[0].strip().replace('\n','')

            # Error for failed to get test case file . 
            self.logger_obj.warn(LogMsgFormat.setSysLogFmt('[ParseTLautoFile]',\
                                       'Failed to get parameter from TL_AUTO,'+ \
                                       'check parameter {tl_auto_cfgSave} if '+ \
                                       'exists in file TL_AUTO.txt'))
            sys_exitfunc(-12,self.logger_obj)

        except Exception ,e:
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[ParseTLautoFile]',e))
            sys_exitfunc(-10,self.logger_obj)
        finally:
            file_fp.close()

class ParseTLcaseFile(object):
    '''ParseTLcaseFile(test case file, system logger)
    This functions:
    -- getCaseSection(line number) : Get a group of test case.
    -- getCaseInfo(start num, end num) : Get basic info of a group of test case.
    -- getINinfo(IN line, searched flag) : Get IN info of a pair of IN/OUT
    -- getOUTinfo(OUT start num, end num, searched flag) : Get OUT info of 
       a pair of IN/OUT
    -- getUnitTO(line num, searched flag) : Get timeout variable for specify 
       IN info
    -- getInOutInfo(start num, end num) : Get execute list of all IN/OUT info
    -- rewriteFile(start num, end num) : Refresh state of a group of test case
       in a real time. (p:pass; f:fail; b:block)
    '''
    
    count = 0
    def __init__(self,tl_case_file,logger_obj):
        'initialize class '
        self.logger_obj = logger_obj
        self.file_name  = tl_case_file
        self.lines = ''

        if not os.path.exists(tl_case_file):
            logger_obj.error(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                            'TestCaseInfo file does not exist.'))
            sys_exitfunc(-22,logger_obj)

        # Read all test case information.
        try:
            tl_case_file_p = open(self.file_name,'r')
            # Transform unicode to string.
            globalVariable.serial_config['file_lines'] = \
            [str(line) for line in tl_case_file_p.readlines()]
            logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                                                    'Get TestCase information'))
        except Exception,e:
            logger_obj.error(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',e))
            sys_exitfunc(-20,logger_obj)

        finally:
            logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                                                'Close TestCaseInfo file'))
            tl_case_file_p.close()
        self.lines = globalVariable.serial_config['file_lines']

    def getCaseSection(self, gcs_start_no):
        'Get case section of IN/OUT segment'

        start_no = 0
        end_no = 0
        start_kw_fg = False
        self.count += 1

        for line_no in range(gcs_start_no,len(self.lines)-1):
            if re.search(r'#\(Case_\d+',self.lines[line_no]):
                if not start_kw_fg:
                    start_no = line_no
                    start_kw_fg = True
                else:
                    end_no = line_no - 1
                    break
            elif start_kw_fg and re.search(r'#StepsEnd',self.lines[line_no]):
                end_no = line_no
                break

        if start_kw_fg and not end_no:
            end_no = line_no
        self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                                                'Get section of each testcase\n'))
        
        if not start_no and self.count == 1:
            self.logger_obj.warn(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                                'There is not Test Case Information in file '+\
                                'TestCaseInfo.txt, You need to select a ' + \
                                'automatic test case at least.\n'))
        return start_no,end_no

    def getCaseInfo(self,start_no, end_no):
        
        globalVariable.serial_config['case_name']  = ''
        globalVariable.serial_config['exec_type']  = ''
        globalVariable.serial_config['exec_times'] = ''
        # Initial variable of storing case title 
        globalVariable.serial_config['case_title'] = ''
        
        globalVariable.serial_config['exec_list'] = ''

        for single_line in self.lines[start_no:end_no+1]:
            '''Change test case name with CaseID keyword. 
            srch_cs_name = re.search(r"^#\((Case_.*)\)",single_line)
            ''' 
            srch_cs_name = re.search(r"^#CaseID:.*",single_line)
            srch_exec_type = re.search(r"^#Exec_type",single_line)
            srch_exec_times = re.search(r"^#Exec_times(\s+|)=",single_line)
            
            # Search case title from case info file
            srch_cs_title = re.search(r"^#Title:",single_line)

            '''Change test case name with CaseID keyword. 
            if srch_cs_name:
                tc_name = srch_cs_name.groups()[0].strip()
                globalVariable.serial_config['case_name'] = tc_name
                self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',\
                                            'Get testcase name {%s}' %tc_name))
            '''
            if srch_cs_name:
                tc_name = single_line.split(":", 1)[1].strip()
                globalVariable.serial_config['case_name'] = tc_name
                self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                    'Get testcase name {%s}' %tc_name))
            elif srch_exec_type:
                globalVariable.serial_config['exec_type'] = \
                single_line.split('=',1)[-1].strip()
                self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                    'Get execute type of testcase {%s}' %
                                    globalVariable.serial_config['case_name']))
            elif srch_exec_times:
                globalVariable.serial_config['exec_times'] = \
                single_line.split('=',1)[-1].strip()
                if globalVariable.serial_config['exec_times'] != '':
                    globalVariable.serial_config['exec_times'] = \
                    int(globalVariable.serial_config['exec_times'])
                self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                    'Get running times of testcase {%s}' %
                                    globalVariable.serial_config['case_name']))
            elif srch_cs_title:
                globalVariable.serial_config['case_title'] = \
                single_line.split(':',1)[-1].strip()
        return (\
                {'tc_id':globalVariable.serial_config['case_name']})

    def rewriteFile(self, start_no, end_no, result, note=''):
        're-write new test case info to test case file yourFileName.txt'

        try:
            #fp_out = open(outfile_name,'w+')
            fp_out = open(self.file_name, 'w+')
            for line_no in range(start_no, end_no):
                if re.search(r'#\(ExResult', self.lines[line_no]):
                    self.lines[line_no] = '#(ExResult:'+ result + ')\n'
                    continue
                if re.search(r'#\(Notes:', self.lines[line_no]):
                    self.lines[line_no] = '#(Notes:' + note + ')\n'
                    break
            if not self.lines:
                print 'This Case does not contain IN/OUT segment'
            else:
                lines_str = string.join([line.lstrip(' ') for line in self.lines])
                fp_out.write(lines_str.replace('\n ','\n'))
        except Exception,e:
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                 'Failed rewrite test case info to file ' + \
                                 'TestCaseInfo.txt : {%s}' %e))
            sys_exitfunc(-24,self.logger_obj)
        finally:
            fp_out.close()

    def rewirteMailList(self):
        try:
            user_mail = ''
            #fp_out = open(outfile_name,'w+')
            for line_no in range(0, 10):
                def_mail_addr = re.search(r'^email =(.*)', 
                                          self.lines[line_no])
                if def_mail_addr:
                    break

            if globalVariable.USER_MAIL_LIST:
                def_mail_addr = \
                def_mail_addr.groups()[0].replace('\'','').strip()

                user_mail_list = globalVariable.USER_MAIL_LIST.split(',')

                user_mail = filter(lambda um: not re.search(um, def_mail_addr), 
                                   user_mail_list)
            if user_mail:
                self.lines[line_no] = 'email = \'%s,%s\'\n' \
                %(def_mail_addr, 
                      ','.join(user_mail))
                lines_str = string.join([line.lstrip(' ') for line in self.lines])
                fp_out = open(self.file_name, 'w+')
                fp_out.write(lines_str.replace('\n ','\n'))
        except Exception,e:
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                 'Failed rewrite mail addr to file ' + \
                                 'TestCaseInfo.txt : {%s}' %e))
            sys_exitfunc(-26,self.logger_obj)
        finally:
            def isset(v):  
                try:  
                    type (eval(v))  
                except:  
                    return 0  
                else:  
                    return 1  

            if isset('fp_out') and isinstance(fp_out, file):
                fp_out.close()