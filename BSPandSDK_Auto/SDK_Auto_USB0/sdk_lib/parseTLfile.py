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
                    globalVariable.serial_config['case_fldr'] = os.path.dirname(tl_uf_file.groups()[0])
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


    def getINinfo(self,item_no,srch_in):

        if srch_in:
            tmp_in_info = self.lines[item_no].split('=',1)[-1].strip()
            # Remove needless whitespace in middle of string
            in_info = re.sub(' +', ' ', tmp_in_info)
            globalVariable.serial_config['in_list'].append(in_info)
            self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                'Get IN info of testcase {%s}' %
                                globalVariable.serial_config['case_name']))

            return in_info

    def getOUTinfo(self,item_no,end_no,srch_out):

        out_list = []
        if srch_out:
            if '{' in self.lines[item_no]:
                for sub_time_no in range(item_no,end_no):
                    if '}' in self.lines[sub_time_no]:
                        if item_no == sub_time_no:
                            out_line = \
                            self.lines[item_no].split('{',1)[-1].replace('}','').strip()
                            out_list.append(out_line)
                            globalVariable.serial_config['out_list'].append(out_line)
                            break
                        else:
                            out_list = [x[1:] for x in self.lines[item_no+1:sub_time_no]]
                            globalVariable.serial_config['out_list'].append(out_list)
                            break
                return out_list,sub_time_no
            else:
                out_line = self.lines[item_no].split('=',1)[-1].strip()
                out_list.append(out_line) 
                globalVariable.serial_config['out_list'].append(out_list)

                self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                    'Get OUT info of testcase {%s}' %
                                    globalVariable.serial_config['case_name']))
                return out_list,item_no

    def getUnitTO(self,item_no,srch_unitto):
        '''Get timeout argument of unit IN/OUT
        '''
        if srch_unitto:
            tmp_unitto = 0
            self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                'Get Unit timeout info of testcase {%s}' %
                                globalVariable.serial_config['case_name']))
            tmp_unitto = int(self.lines[item_no].split('=', 1)[-1].strip())
            if 0 == tmp_unitto or '' == tmp_unitto:
                return None
            else:
                return tmp_unitto


    def getUnitWT(self, item_no, srch_waittms):
        '''Get waitting times of unit IN/OUT
        '''
        if srch_waittms:
            tmp_waittms = 0
            self.logger_obj.info(LogMsgFormat.setSysLogFmt('[ParseTLcaseFile]',
                                'Get delay times info of testcase {%s}' %
                                globalVariable.serial_config['case_name']))
            tmp_waittms = int(self.lines[item_no].split('=', 1)[-1].strip())
            if 0 == tmp_waittms or '' == tmp_waittms:
                return None
            else:
                return tmp_waittms

    def getInOutInfo(self, start_no, end_no):
        'Get information of IN/OUT'

        globalVariable.serial_config['in_list']  = []
        
        globalVariable.serial_config['out_list'] = []
        globalVariable.serial_config['exec_list'] = copy.deepcopy([])
        avl_lines = copy.deepcopy({})
        get_rbtflg = False
        get_unitto = False
        get_waittms = False

        item_no = start_no
        
        while item_no >= start_no and item_no <= end_no:
            srch_in  = re.search(r"^#IN(\s+|)=.*", self.lines[item_no], re.I)
            srch_out = re.search(r"^#OUT(\s+|)=.*", self.lines[item_no], re.I)
            srch_subtms = re.search(r"^#SubRuntimes(\s+|)=.*",
                                    self.lines[item_no], re.I)
            srch_rbtflg = re.search(r"^#Rebootflag(\s+|)=(\s+|)yes",
                                    self.lines[item_no], re.I)
            srch_unitto = re.search(r"^#UnitTimeout(\s+|)=(\s+|).*",
                                    self.lines[item_no], re.I)
            srch_waittms = re.search(r"^#WaitingTime(\s+|)=(\s+|).*",
                                    self.lines[item_no], re.I)
            in_info = ''
            out_info = []

            sub_times = ''

            if srch_subtms:
                sub_times = self.lines[item_no].split('=',1)[-1].strip()
                if sub_times != '':
                    avl_lines = {}
                    avl_lines['IN'] = []
                    avl_lines['OUT'] = []
                    avl_lines['subtms'] = sub_times
                    avl_lines['rbtflg'] = []
                    avl_lines['unitto'] = []
                    avl_lines['waittms'] = []

                    sub_get_rbtflg = False
                    sub_in_info = ''
                    sub_out_info = []
                    sub_unitto = None
                    sub_waittms = None

                    sub_time_no = item_no + 1

                    while sub_time_no <= end_no :
                        sub_srch_rbtflg = re.search(r"^#Rebootflag(\s+|)=(\s+|)yes",
                                                    self.lines[sub_time_no], 
                                                    re.I)
                        sub_srch_in  = re.search(r"^#IN(\s+|)=", 
                                                 self.lines[sub_time_no], 
                                                 re.I)
                        sub_srch_out = re.search(r"^#OUT(\s+|)=.*", 
                                                 self.lines[sub_time_no], 
                                                 re.I)
                        sub_srch_unitto = re.search(r"^#UnitTimeout\s*=.*",
                                                self.lines[sub_time_no], 
                                                re.I)

                        sub_srch_waittms = re.search(r"^#WaitingTime\s*=.*",
                                                     self.lines[sub_time_no], 
                                                     re.I)

                        if sub_srch_rbtflg:
                            sub_get_rbtflg |= True
                        #else:
                        #    sub_get_rbtflg |= False
                        
                        if sub_srch_unitto:
                            sub_unitto = self.getUnitTO(sub_time_no, 
                                                        sub_srch_unitto)

                        if sub_srch_waittms:
                            sub_waittms = self.getUnitWT(sub_time_no, 
                                                             sub_srch_waittms)

                        if sub_srch_in:
                            sub_in_info = self.getINinfo(sub_time_no, 
                                                         sub_srch_in)
                            avl_lines['IN'].append(sub_in_info)
                            
                            avl_lines['rbtflg'].append(sub_get_rbtflg)
                            avl_lines['unitto'].append(sub_unitto)
                            avl_lines['waittms'].append(sub_waittms)
                            sub_get_rbtflg = False
                            sub_unitto = None
                            sub_waittms = None

                        elif sub_srch_out:

                            sub_out_info,sub_time_no = \
                            self.getOUTinfo(sub_time_no, end_no,sub_srch_out)

                            avl_lines['OUT'].append(sub_out_info)
                            sub_get_rbtflg = False
                            sub_unitto = None
                            sub_waittms = None

                        if re.search('SubRuntimesEnd', 
                                     self.lines[sub_time_no], 
                                     re.I):
                            globalVariable.serial_config['exec_list'].append(avl_lines)
                            globalVariable.serial_config['exec_list'] = \
                            copy.deepcopy(globalVariable.serial_config['exec_list'])
                            item_no = sub_time_no
                            break
                        sub_time_no += 1
            elif srch_unitto:
                get_unitto = True
                unitto = self.getUnitTO(item_no, srch_unitto)
            elif srch_waittms:
                get_waittms = True
                waittms = self.getUnitWT(item_no, srch_waittms)
            elif srch_in:
                if avl_lines.has_key('subtms'):
                    del avl_lines['subtms']
                if get_rbtflg:
                    avl_lines['rbtflg'] = True
                else:
                    avl_lines['rbtflg'] = False
                
                if get_unitto:
                    avl_lines['unitto'] = [unitto]
                else:
                    avl_lines['unitto'] = [None]

                if get_waittms:
                    avl_lines['waittms'] = [waittms]
                else:
                    avl_lines['waittms'] = [None]

                avl_lines['IN'] = []
                in_info = self.getINinfo(item_no, srch_in)
                avl_lines['IN'].append(in_info)
                get_rbtflg = False
                get_unitto = False
                get_waittms = False

            elif srch_out:
                avl_lines['OUT'] = []
                out_info,item_no = self.getOUTinfo(item_no, end_no, srch_out)
                avl_lines['OUT'].append(out_info)
                globalVariable.serial_config['exec_list'].append(avl_lines)
                globalVariable.serial_config['exec_list'] = \
                copy.deepcopy(globalVariable.serial_config['exec_list'])
                get_rbtflg = False
                get_unitto = False
                get_waittms = False

            elif srch_rbtflg:
                avl_lines = {}
                avl_lines['rbtflg'] = True

                globalVariable.serial_config['exec_list'].append(avl_lines)
                globalVariable.serial_config['exec_list'] = \
                copy.deepcopy(globalVariable.serial_config['exec_list'])
            item_no += 1

        #print 'execlist-----',globalVariable.serial_config['exec_list']

    def rewriteFile(self, start_no, end_no, result):
        're-write new test case info to test case file yourFileName.txt'

        try:
            #fp_out = open(outfile_name,'w+')
            fp_out = open(self.file_name,'w+')
            for line_no in range(start_no,end_no):
                if re.search(r'#\(ExResult',self.lines[line_no]):
                    self.lines[line_no] = '#(ExResult:'+result+')\n'
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
