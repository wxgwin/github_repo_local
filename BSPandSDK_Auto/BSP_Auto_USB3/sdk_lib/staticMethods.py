r'''All static methods and classes
This functions:
  -- sys_exitfunc(error num, system logger) : Exit SDK Automation Tool
  -- RecycleResource(system logger) : Recycle all source.

This classes:
  -- LogMsgFormat() : Log format of system log 
  -- FileOperate()  : All read/write operation about file.
  -- ListandStrOperate() : All list/string operation.
  -- CaseLogSetting() : All operation about case log.
  -- StatisticsCaseCount() : Statistics report operations.
'''

import sys
import os
import re
import datetime
import string
import fileinput
import subprocess
import shlex
import shutil

import globalVariable
import parseExcel

from parseHtml import * 

def sys_exitfunc(error_no,logger_obj):
    '''sys_exitfunc(error num, system logger)
    Input error number and error information to system log after exit.
    '''
    exit_msg = 'Abort system with exited number (%d)' %error_no
    logger_obj.error(LogMsgFormat.setSysLogFmt('[System]',exit_msg))
    sys.exit(error_no)

def getCaseTitleMap(sort_key='M'):
    abs_ct_file = os.path.join(os.getcwd(), 
                               'case_info', 
                               'case_info.map')
    case_info_list = []
    with open(abs_ct_file,'r') as f:
        for eachline in f:
            case_name, case_pri_tit = eachline.split(' ', 1)

            case_priority, case_mod_tit = case_pri_tit.split(' ', 1)
            if '_' in case_mod_tit:
                case_module, case_title = case_mod_tit.split('_', 1)
            else:
                case_module, case_title = ('No module', case_mod_tit)

            case_info = (case_name.strip(),
                         case_priority.strip(), 
                         case_module.strip(),
                         case_title.strip())
            case_info_list.append(case_info)
            #globalVariable.CASE_TITLE[case_name] = caset_title
        return sortCaseInfo(case_info_list,sort_key)

def sortCaseInfo(case_info, sort_key='M'):
    
    #print case_info
    if sort_key in ('M','m'):
        return sorted(case_info, key=lambda x:(x[2],x[1],x[0][4:]))
    elif sort_key in ('P','p'):
        return sorted(case_info, key=lambda x:(x[1],x[2],x[0][4:]))
    elif sort_key in ('N','n'):
        return sorted(case_info, key=lambda x:(x[0],x[2]))

def execCLI(cmd_line,shell=True):
        cmd_args = shlex.split(cmd_line, posix=False)
        cmd_exec =  subprocess.Popen(cmd_args,bufsize=0,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=shell)
        output,strrout= cmd_exec.communicate()
        cmd_exec.wait()
        return (cmd_exec.returncode, output, strrout)

def sendNagativeMail(mail_mesg):

        sm_cli = ('echo -e "Hi all:\n\t %s"'
                  '| mutt -s "BSP Hudson Automation Failure'
                  ' `date`" xiaogen.wang@availink.com'  % (mail_mesg))

        os.system(sm_cli)

def RecycleResource(logger_obj, 
                    tl_case_file=globalVariable.serial_config['case_name']):
    '''RecycleResource(system logger)
    Close file hander and remove unfinished test case file
    '''
    try:
        logger_obj.info(LogMsgFormat.setSysLogFmt('[RylRsrc]',\
                        'Remove unfinished TestCaseFile'))
        for rm_tims in range(1,6):
            if os.path.exists(tl_case_file):
                #os.remove(tl_case_file)
                #time.sleep(2)
                pass
            else:
                break
    except Exception,e:
        logger_obj.warn(LogMsgFormat.setSysLogFmt('[RylRsrc]',\
                        'Failed to remove TestCaseInfo.txt,' + \
                        'delete it by manual' +\
                        'WindowsError:%s' %(e)))

class LogMsgFormat():
    '''
    This functions:
    -- setSysLogFmt(title, message) : Set format for system log.
    '''

    @staticmethod
    def setSysLogFmt(title,msg):
        return title.ljust(17) + ' -- %s' %msg

class FileOperate():
    '''All read/write operation about file
    This functions:
    -- readFile(file name) : Return all lines of file
    -- readINFile(in message, system logger) : Get all lines from specify file
       within in message.
    -- readOUTFile(out message, system logger) : Get all lines from specify file
       within out message.
    '''

    #Only read one line data from file
    @staticmethod
    def readFile(abs_file):
        try:
            file_fp = open(abs_file, 'r')
            return [line.strip() for line in file_fp.readlines()]
        except Exception,e:
            return [False]
        finally:
            file_fp.close()

    #Get message from a file
    @staticmethod
    def readINFile(in_msg,logger_obj):
        file_name = in_msg.split('FILE:',1)[1].strip()
        abs_file_name = os.path.join(globalVariable.serial_config['case_fldr'],\
                                     'IN_OUT_files\INfiles', file_name)
        logger_obj.info(LogMsgFormat.setSysLogFmt('[FileOperate]',\
                        'Get IN message from file %s.\n' %abs_file_name))
        if os.path.exists(abs_file_name):
            return  string.join(FileOperate.readFile(abs_file_name))
        else:
            logger_obj.error(LogMsgFormat.setSysLogFmt('[FileOperate]',\
                        'Imported file of IN %s does not exist.\n' %abs_file_name))
            return False

    @staticmethod
    def readOUTFile(out_msg,logger_obj):
        file_name = out_msg[0].split('FILE:',1)[1].strip()
        abs_file_name = os.path.join(globalVariable.serial_config['case_fldr'],\
                                     'IN_OUT_files\Outfiles', file_name)
        logger_obj.info(LogMsgFormat.setSysLogFmt('[FileOperate]',\
                        'Get OUT message from file %s.\n' %abs_file_name))

        if os.path.exists(abs_file_name):

            return  FileOperate.readFile(abs_file_name)
        else:
            logger_obj.error(LogMsgFormat.setSysLogFmt('[FileOperate]',\
                        'Imported file of OUT %s does not exist.\n' %abs_file_name))
            return [False]
    
class ListandStrOperate():
    '''All list/string operation.
    This functions:
    -- diffList(base list, dest list) : Compare base list with destination list.
    -- removeSpyKw(string) : Remove specify keyword from string.
    -- getSpyStrMap(org message, act message) : Get keyword dictionary from 
       act message.
    -- searchStrFromList(keywords, sting) : Return True onec keyword is in 
       string, or return False
    -- replaceSpfyString(in list) : Replace @XXX inform with keyword directory 
    '''

    @staticmethod
    def diffList(base_list, dst_list):
        dst_list = ListandStrOperate.removeCharacter(dst_list)
        if isinstance(base_list, list):
            for base_item in base_list:
                cmp_state = False
                
                if '[' in base_item:
                    base_item = base_item.replace('[','\[')
                if ']' in base_item:
                    base_item = base_item.replace(']','\]')

                if '(' in base_item:
                    base_item = base_item.replace('(','\(')
                if ')' in base_item:
                    base_item = base_item.replace(')','\)')

                for dst_item in dst_list:
                    if re.search(base_item.strip(), dst_item, re.I):
                        cmp_state |= True
                        break

                if cmp_state != True:
                    return False
            return True
        else:
            return ListandStrOperate.searchStrFromList(base_list, dst_list)
        
    @staticmethod
    def removeSpyKw(out_msg, rpl_str=''):
        avl_out_msg = [re.sub(r'@[^ $]+', rpl_str, out_msg_item).strip() 
                       for out_msg_item in out_msg]
        return avl_out_msg

    # TODO
    @staticmethod
    def getSpyStrMap(out_msg, act_msg):

        avl_out_msg = ListandStrOperate.removeSpyKw(out_msg, '(\S+)')
        for out_msg_item, avl_msg_item in zip(out_msg, avl_out_msg):
            out_msg_item = out_msg_item.strip()
            if '@' in out_msg_item:
                spy_kw_names = re.findall(r'@[^ $]+',out_msg_item)
                for act_msg_item in act_msg:
                    has_spy_kw = re.search(avl_msg_item, act_msg_item)
                    if has_spy_kw:
                        break
                spy_kw_values = re.search(avl_msg_item, act_msg_item).groups()
                for spy_kw_name, spy_kw_value in zip(spy_kw_names, 
                                                     spy_kw_values):

                    globalVariable.serial_config['skw_list']['%s' %spy_kw_name]\
                     = spy_kw_value.split('=')[-1]
        #print globalVariable.serial_config['skw_list']

    @staticmethod
    def searchStrFromList(src_str,src_list):
        for list_item in src_list:
            if re.search(src_str, list_item, re.I):
                return True
        return False

    @staticmethod
    def removeCharacter(src_list, chars=[""]):
        
        tmp_src = src_list
        
        if isinstance(src_list, list):
            for char_item in chars:
                for list_no in range(0,len(tmp_src)):
                    tmp_src[list_no] = tmp_src[list_no].replace(repr(char_item),"")
        elif isinstance(src_list, str):
            tmp_src = str(tmp_src)
            for char_item in chars:
                tmp_src= tmp_src.replace(char_item, "")
        return tmp_src

    @staticmethod
    def replaceStrOnList(src,repl,list_obj):
        if ListandStrOperate.searchStrFromList(src, list_obj):
            for list_no in range(0,len(list_obj)):
                list_obj[list_no]  = list_obj[list_no].replace(r'%s' %src,repl)

    @staticmethod
    def replaceInInfo(in_list,out_list):
        
        for out_no in range(0,len(out_list)):
            if isinstance(out_list[out_no], list):
                for sub_out_no in range(0,len(out_list[out_no])):
                    spfy_str_srch = re.search(r'(@.*)$', out_list[out_no][sub_out_no])
                    if spfy_str_srch:
                        spfy_str = spfy_str_srch.groups()[0]
                        tmp_str = \
                        out_list[out_no][sub_out_no].replace(r'%s' %spfy_str,'').strip()
                        in_list = \
                        ListandStrOperate.replaceStrOnList(spfy_str, tmp_str, in_list)
                        out_list[out_no][sub_out_no] = tmp_str

            elif isinstance(out_list[out_no], str):
                spfy_str_srch = re.search(r'(@.*)$', out_list[out_no])
                if spfy_str_srch:
                    spfy_str = spfy_str_srch.groups()[0]
                    tmp_str = out_list[out_no].replace(r'%s' %spfy_str,'').strip()
                    in_list = \
                    ListandStrOperate.replaceStrOnList(spfy_str, tmp_str, in_list)
                    out_list[out_no] = tmp_str

        return in_list,out_list
    '''
'''
    @staticmethod
    def replaceSpfyString(in_str):

        tmp_obj = in_str
        
        for item_name , item_value in globalVariable.serial_config['skw_list'].items():
            tmp_obj = tmp_obj.replace('%s' %item_name, item_value)

        return tmp_obj


class CaseLogSetting():
    '''All operation about case log.
    This functions:
    -- getLogname() : Merge a file name with case name and time stamp
    -- addTitletoLog() : Add title to case log.
    -- addSplitLine() : Add splitting line to case log
    -- addExecTmsTOBody() : Add sub IN/OUT running times to case log.
    -- addsSubExecTmsTOBoday() : Add message body of sub case to case log.
    -- addSubResultToBody() : Add result of sub case to case log.
    -- addBodytoLog() : Add message of case to case log.
    -- addResultToBody() : Add case result to case log.
    -- addEndtolog() : Add end line to case log.
    -- addReboottoLog() : Add reboot infomration to case log.
    '''

    count = 0
    sub_count = 1
    log_name = ''
    abs_caselog_dir = ''
    case_log_fd = ''

    @staticmethod
    def mkCasedir():
        CaseLogSetting.case_log_fd = datetime.datetime.now().strftime('%Y%m%d%H%M')
        CaseLogSetting.abs_caselog_dir = os.path.join(
                            globalVariable.serial_config['case_fldr'],
                            'CASE_LOG', 
                            CaseLogSetting.case_log_fd)
        if os.path.exists(CaseLogSetting.abs_caselog_dir):
            pass
        else:
            os.mkdir(CaseLogSetting.abs_caselog_dir)
    @staticmethod
    def getLogname():

        curt_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        case_log_name = os.path.join(
                            CaseLogSetting.abs_caselog_dir,
                            '%s_%s.log' %(
                                globalVariable.serial_config['case_name'],
                                curt_time))

        return case_log_name

    @staticmethod
    def addTitletoLog():

        CaseLogSetting.count = 1
        CaseLogSetting.log_name = CaseLogSetting.getLogname()

        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n'+ '#'*80)
            cl_fp.write('\nCaseName   : %s' %globalVariable.serial_config['case_name'])
            cl_fp.write('\n'+ '#'*80 + '\n')
        except Exception,e:
            print 'addTitletoLog:',e
        finally:
            cl_fp.close()

    @staticmethod
    def addSplitLine():
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n' + '*' * 80 +'\n')
        except Exception,e:
            print 'addSplitLine:',e
        finally:
            cl_fp.close()

    @staticmethod
    def addExecTmsTOBody():

        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n' + '+-' * 40)
            cl_fp.write('\nRunning times : %dth\n' %CaseLogSetting.count)
            cl_fp.write('+-'*40 + '\n')
            #cl_fp.write('\n' + '*'*80)
            CaseLogSetting.count += 1
        except Exception,e:
            print 'addExecTmsTOBody:', e
        finally:
            cl_fp.close()

    @staticmethod
    def addResultToBody(status):
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            #cl_fp.write('\n' + '+-' * 40)
            cl_fp.write('\n\nCase Result: ' + str(status) + '\n')
        except Exception,e:
            print 'addResultToBody', e
        finally:
            cl_fp.close()

    @staticmethod
    def addsSubExecTmsTOBoday(times):
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n' + '.' * 80)
            cl_fp.write('\nSub Running times : %dth\n' %times)
            cl_fp.write('.'*80 + '\n')
            CaseLogSetting.sub_count += 1
        except Exception,e:
            print 'addsSubExecTmsTOBoday:',e
        finally:
            cl_fp.close()
    
    @staticmethod
    def addSubResultToBody(sub_status):
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n' + '.' * 80)
            cl_fp.write('\n\nSub Result: ' + str(sub_status) + '\n')
        except Exception,e:
            print 'addSubResultToBody:',e
        finally:
            cl_fp.close()

    @staticmethod
    def addBodytoLog(casetype = None, *args):
        
        if casetype == None:
            al_in_msg = args[0]
            al_out_msg = args[1]
            al_act_msg = args[2]
            al_diff_status = args[3]

        act_format = ' '*13 + '{0}\n'
        exp_format = ' '*16 + '{0}\n'

        def writeLineFromList(file_fp, msg_list, output_format):

            if type(msg_list) == type(''):
                file_fp.write(msg_list + '\n')
            else:
                file_fp.write(msg_list[0] + '\n')
                if len(msg_list) > 1:
                    for unit_msg in msg_list[1:]:
                        file_fp.write(output_format.format(unit_msg))

        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')

            if  None == casetype:   
                cl_fp.write('\nInput  Msg : %s\n' %al_in_msg)
                cl_fp.write('\nActual Msg : ')
                if globalVariable.serial_config['target_type'] == 'librasd':
                    writeLineFromList(cl_fp, al_act_msg, act_format)
                else:
                    writeLineFromList(cl_fp, al_act_msg, act_format)

                cl_fp.write('\nExpected Msg : ')
                writeLineFromList(cl_fp, al_out_msg, exp_format)

                cl_fp.write('\nCurrent Result : %s\n' %str(al_diff_status))

            elif 'No_Pair' == casetype:
                cl_fp.write('Warning : IN info and OUT info are not in pair! \n')
            elif 'No_Info' == casetype:
                cl_fp.write('Warning : Test case {%s} does not have IN/OUT any more' %
                            globalVariable.serial_config['case_name'])
        except Exception,e:
            print 'writeLineFromList:', e
        finally:
            cl_fp.close()

    @staticmethod
    def addEndtolog(whl_status):

        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            cl_fp.write('\n\n' + '#' * 80)
            cl_fp.write('\n\nAll Result :' + str(whl_status))
            cl_fp.write('\n\n' + '#' * 80)
            cl_fp.write('\nFinished all test of current test case')
            cl_fp.write('\n' + '#' * 80)

        except Exception,e:
            print 'addEndtolog',e
        finally:
            cl_fp.close()

    @staticmethod
    def addReboottoLog(levels=1):
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            if 1 == levels:
                lineseq = '*'
            elif 2 <= levels:
                lineseq = '.'
            #cl_fp.write('\n' + lineseq * 80)
            cl_fp.write('\nTarget is being rebooted ...')
            cl_fp.write('\n\n' + lineseq * 80 + '\n')

        except Exception,e:
            print 'addReboottoLog:',e
        finally:
            cl_fp.close()
            
    @staticmethod
    def addDelaytimeToLog(delaytime, levels=1):
        try:
            cl_fp = open(CaseLogSetting.log_name,'a+')
            if 1 == levels:
                lineseq = '*'
            elif 2 <= levels:
                lineseq = '.'
            cl_fp.write('\nTest case is being delayed for %d seconds ...' % delaytime)
            cl_fp.write('\n\n' + lineseq * 80 + '\n')

        except Exception,e:
            print 'addDelaytimeToLog:',e
        finally:
            cl_fp.close()

class StatisticsCaseCount():
    '''Statistics report operations.
    This functions:
    -- writeDataToFile() : Add statistics info to file BSPAT_stats_report.txt
    '''
    FLAG_EXIST_FILE = False
    CURR_TIME = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    FILE_NAME = os.path.join(os.getcwd(), 'sys_log', 'BSPAT_stats_report%s.txt' 
                             %CURR_TIME)
    CASE_STATE_INMODULE = {}
    
    HTML_FILE_NAME = os.path.join(os.getcwd(), 'CASE_LOG', 'BSPAT_stats_report%s.html' 
                             %CURR_TIME)

    HTML_PAGE = PyH("Automation Report")

    HTML_STISTC_TABLE = ''
    HTML_CASE_DETAIL_TABLE = ''

    EXCEL_STISTIC_INS = parseExcel.CreateExcel()
    EXCEL_STISTIC_INS.createSheetAndTitle()

    EXCEL_STISTIC_PAGE = 'BSPAT_stats_report%s.xls' %CURR_TIME

    EXCEL_START_POS = 4
    HUDSON_JOB_NAME = ''

    @classmethod
    def statisticCaseModule(cls, case_module, case_state):
        if StatisticsCaseCount.CASE_STATE_INMODULE.has_key(case_module):
            if case_state == 'Failed':
                StatisticsCaseCount.CASE_STATE_INMODULE[case_module]['Failed'] \
                += 1
            elif case_state == 'Passed':
                StatisticsCaseCount.CASE_STATE_INMODULE[case_module]['Passed'] \
                += 1
        else:
            StatisticsCaseCount.CASE_STATE_INMODULE[case_module] \
            = {'Failed':0,'Passed':0}
            if case_state == 'Failed':
                StatisticsCaseCount.CASE_STATE_INMODULE[case_module]['Failed'] \
                += 1
            elif case_state == 'Passed':
                StatisticsCaseCount.CASE_STATE_INMODULE[case_module]['Passed'] \
                += 1

    @staticmethod
    def wirteCaseStateToFile(case_state, case_info, note_info):

        if os.path.exists(StatisticsCaseCount.FILE_NAME) and \
        not StatisticsCaseCount.FLAG_EXIST_FILE:
            os.remove(StatisticsCaseCount.FILE_NAME)
            
        try:
            abs_cn_format = '{0:<7} : {1:<12} ${2:<8} {3:<8} {4:2<} {5:4<}\n'

            case_id, case_pri,case_module,case_title = (case_info[0],
                                               case_info[1],
                                               case_info[2],
                                               case_info[3])

            abs_case_name = abs_cn_format.format(case_state, 
                                                 case_id,
                                                 case_pri,
                                                 case_module,
                                                 case_title.strip(),
                                                 note_info)

            stats_fd = open(StatisticsCaseCount.FILE_NAME, 'a+')

            if not StatisticsCaseCount.FLAG_EXIST_FILE:
                # Add title to statistic report of html type
                StatisticsCaseCount.HTML_PAGE <<h1('BSP Automation Report',
                                                   align='center')
                StatisticsCaseCount.HTML_PAGE << div(align='center',id='') << \
                p('Date : %s' %datetime.datetime.now(),id='myp1')
                
                title_table = StatisticsCaseCount.HTML_PAGE \
                << table(width="100%", border=0, cellspacing=0, cellpadding=0)
                
                title_tr = title_table << tr()
                title_tr << td('Job Name : %s' %StatisticsCaseCount.HUDSON_JOB_NAME,align='left')
                title_tr << td('Version : %s' %globalVariable.SVN_CODE_VER,align='right')
                
                #StatisticsCaseCount.HTML_PAGE << div(align='right',id='') << \
                #p('Version : %s' %globalVariable.SVN_CODE_VER, id='myp2')
                
                createEmptyTable(StatisticsCaseCount.HTML_PAGE, 
                                 top=False, 
                                 bottom=False)

                mydiv2 = StatisticsCaseCount.HTML_PAGE << div(id='myDiv2')
                harrt_h5 = h5('Test Case Statistic : ')
                harrt_h5.attributes['align'] = 'center'
                mydiv2 <<harrt_h5

                StatisticsCaseCount.HTML_STISTC_TABLE = createStatisticTable(
                    StatisticsCaseCount.HTML_PAGE)
                
                createEmptyTable(StatisticsCaseCount.HTML_PAGE,
                                 top=True, 
                                 bottom=False)

                mydiv3 = StatisticsCaseCount.HTML_PAGE << div(id='myDiv3')

                mydiv3 <<h5('Detail information :')
                
                StatisticsCaseCount.HTML_CASE_DETAIL_TABLE = \
                createCaseDetailTable(StatisticsCaseCount.HTML_PAGE)

                # Add title to statistic report of document type
                stats_fd.write(abs_cn_format.format('[State]', 
                                                    '[ Case Name ]',
                                                    '[ Prority ]',
                                                    '[ Module ]',
                                                    '[Title]',
                                                    '[Note]'))
                stats_fd.write('-' * 80 + '\n\n')
                StatisticsCaseCount.FLAG_EXIST_FILE = True
            else:
                pass

            # Add case info as excel file
            StatisticsCaseCount.EXCEL_STISTIC_INS.addCentent(
                                    StatisticsCaseCount.EXCEL_START_POS, 
                                    (case_state, 
                                     case_id,
                                     case_pri,
                                     case_module,
                                     case_title.strip(),
                                     note_info))
            StatisticsCaseCount.EXCEL_START_POS += 1

            # Add case info as html page file
            addTbtoSttsTable(StatisticsCaseCount.HTML_CASE_DETAIL_TABLE,
                     case_state,
                     case_id,
                     case_pri,
                     case_module,
                     case_title,
                     os.path.join(
                            CaseLogSetting.case_log_fd,
                            os.path.basename(CaseLogSetting.log_name)),
                    note_info)

            # Add case info as txt log file
            stats_fd.write(abs_case_name)
            StatisticsCaseCount.statisticCaseModule(case_module, case_state)
        except Exception,e:
            print 'wirteCaseStateToFile:',e
        finally:
            def isset(v):  
                try:  
                    type (eval(v))  
                except:  
                    return 0  
                else:  
                    return 1  

            if isset('stats_fd') and isinstance(stats_fd, file):
                stats_fd.close()

    
    @staticmethod
    def writeDataToFile():

        try:
            stats_fd = open(StatisticsCaseCount.FILE_NAME,'a+')
            stats_fd.write('\n' + '#' * 80 + '\n\n')
            abs_mn_format = '{0:<10} : {1:^7} {2:^7} {3:^7}\n'
            stats_fd.write(abs_mn_format.format('Module ',
                                                'Totle ',
                                                'Passed ',
                                                'Failed '))
            stats_fd.write('-' * 80 + '\n')
            module_data = StatisticsCaseCount.CASE_STATE_INMODULE

            for module_name, modue_data_state in module_data.iteritems():
                module_case_total = modue_data_state['Failed'] + \
                                    modue_data_state['Passed']
                stats_fd.write(abs_mn_format.format(module_name,
                                                    module_case_total,
                                                    modue_data_state['Passed'],
                                                    modue_data_state['Failed']))
                addTdToTable(StatisticsCaseCount.HTML_STISTC_TABLE,
                             module_name,
                             str(module_case_total),
                             str(modue_data_state['Passed']),
                             str(modue_data_state['Failed']))
            stats_fd.write('\n'+ '-' * 80 + '\n')
            stats_fd.write(abs_mn_format.format(
                'Total ',
                globalVariable.serial_config['case_num']['total'],
                globalVariable.serial_config['case_num']['passed'],
                globalVariable.serial_config['case_num']['failed']))

            stats_fd.write('-' * 80)
            stats_fd.write('\n\n' + '#' * 80)
            addTdToTable(StatisticsCaseCount.HTML_STISTC_TABLE,
                         'Total',
                         globalVariable.serial_config['case_num']['total'],
                         globalVariable.serial_config['case_num']['passed'],
                         globalVariable.serial_config['case_num']['failed'])
            
            createEmptyTable(StatisticsCaseCount.HTML_PAGE,
                             top=True, 
                             bottom=False)
            mydiv4 = StatisticsCaseCount.HTML_PAGE << div(id='myDiv4')
            harrt_h5 = h5('Generated by : BSP Automation Tool')
            harrt_h5.attributes['align'] = 'center'
            mydiv4 <<harrt_h5

        except Exception,e:
            print 'writeDataToFile :',e
        finally:
            stats_fd.close()
            
    @staticmethod
    def sendMail():

        shutil.move(StatisticsCaseCount.FILE_NAME, 
                    CaseLogSetting.abs_caselog_dir)
        tar_case_log_name =  'caselog_%s.tar.gz' % CaseLogSetting.case_log_fd
        tar_case_log_cmd = 'tar czf %s %s' %(tar_case_log_name,
                                             CaseLogSetting.case_log_fd)

        print tar_case_log_cmd
        os.chdir(os.path.dirname(CaseLogSetting.abs_caselog_dir))
        os.system(tar_case_log_cmd)
        if os.path.exists('./' + tar_case_log_name):
            pass
        else:
            print 'check it by manual'
        if globalVariable.MAIL_LIST:
            sm_cli = ('''echo -e "Hi all:\n\t Attachment is statistic report"'''
                  '''| mutt -s "BSP Hudson Automation Result for'''
                  ''' %s `date`" xiaogen.wang@availink.com -a %s ./%s -c %s'''
                     % (globalVariable.serial_config['target_type'],
                        #StatisticsCaseCount.FILE_NAME,
                        StatisticsCaseCount.HTML_FILE_NAME,
                        tar_case_log_name,
                        globalVariable.MAIL_LIST.replace(',', ' -c ')))


        else:
            sm_cli = ('''echo -e "Hi all:\n\t Attachment is statistic report"'''
                      '''| mutt -s "BSP Hudson Automation Result for '''
                      '''%s `date`" xiaogen.wang@availink.com -a %s ./%s''' 
                      % (globalVariable.serial_config['target_type'],
                         #StatisticsCaseCount.FILE_NAME,
                         StatisticsCaseCount.HTML_FILE_NAME,
                         tar_case_log_name))
        #print "sm_cli", sm_cli
        os.system(sm_cli)
        
