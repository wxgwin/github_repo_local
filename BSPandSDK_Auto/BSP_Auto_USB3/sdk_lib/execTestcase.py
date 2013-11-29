r'''Execute a group of IN/OUT
This Classes or functions
  -- execitem(serial instance, system logger ins, start line of test case ,
              end line of test case)
              : Execute a pair of IN/OU
  -- execCase(serial instance, system logger ins, start line of test case ,
              end line of test case)
              : Execute a group of test case
'''

import os
import copy
import time
import connectSerial


#import globalVariable
from staticMethods import *


def unmountBefReboot(serial_ins, logger_obj):
    serial_ins.rwSerial('cd /', kw='')
    for chk_time in range(0,3):
        if checkCLI(serial_ins, 'umount /mnt', 
                    'fail', 
                    logger_obj, positive=False):
            break
        else:
            time.sleep(2)
    serial_ins.rebootTarget()


def checkCLI(serial_ins, cli, result, logger_obj, positive=True, kw=''):
    output = serial_ins.rwSerial(cli, kw=kw)

    if filter(lambda kw:re.search(result, kw, re.I), output):
        if positive:
            logger_obj.info(LogMsgFormat.setSysLogFmt('[InitENV]',
                'Successfully execute cli on target, cli:{%s}\n output:{%s}' %
                (cli, result)))
            return True
        else:
            logger_obj.error(LogMsgFormat.setSysLogFmt('[InitENV]',
                            'Failed to execute target, cli:{%s}\n output:{%s}' %
                            (cli, result)))
            return False
    else:
        if positive:
            logger_obj.error(LogMsgFormat.setSysLogFmt('[InitENV]',
                            'Failed to execute target, cli:{%s}\n output:{%s}' %
                            (cli, result)))
            return False
        else:
            logger_obj.info(LogMsgFormat.setSysLogFmt('[InitENV]',
                            ('Successfully execute cli on target,'
                             ' cli:{%s}\n output:{%s}' %
                             (cli, result))))
            return True


def initEnv(serial_ins, logger_obj):
    ''' Initial environment, contains mount, udhcpc operations
    '''
    if checkCLI(serial_ins, 'mount -o rw /dev/sda1 /mnt', 
                 'No such', 
                 logger_obj, positive=False)\
    and checkCLI(serial_ins, 'udhcpc', 
                 'obtained, lease time', 
                 logger_obj, positive=True):
        logger_obj.info(LogMsgFormat.setSysLogFmt('[InitENV]',
                ('Successfully mount usb to local')))
        return True
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[InitENV]',
                ('Failed to execute all cli on target, check it by manual')))
        sys_exitfunc(-52, logger_obj)
        return False

def sshConn(serial_ins, logger_obj):
    '''Interactive with SVN server.
        -- ssh connect SVN server
        -- svn update
        -- scp operation
        -- sync operation
        -- chmod operation
        -- access case path
    '''
    output = serial_ins.rwSerial('ssh %s@%s' %(globalVariable.LU_USER,
                                           globalVariable.SVN_SERVER),
                                 kw=['yes', 'password'])

    if filter(lambda line: re.search('yes', line, re.I), output):
        output = serial_ins.rwSerial('yes', kw='password')


    if filter(lambda line: re.search('password:', line, re.I), output):
        output = serial_ins.rwSerial(globalVariable.LU_PASSWD, kw='Last login')

        logger_obj.info(LogMsgFormat.setSysLogFmt('[InitENV]',
                        'Successfully ssh to SVN server'))
        if not filter(lambda line: re.search('Last login', line, re.I), output):
            logger_obj.error(LogMsgFormat.setSysLogFmt('[InitENV]',
                            'Failed to ssh to SVN server'))
            sys_exitfunc(-58, logger_obj)
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[InitENV]',
                ('SSH prompt is incorrect')))
        sys_exitfunc(-54, logger_obj)

    if checkCLI(serial_ins, 
                'cd /home/lium/test_shell/', 
                 '', 
                 logger_obj, 
                 positive=True, 
                 kw='bjdevel03'):
        pass
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[sshConn]',
                        'Failed to access folder /home/lium/test_shell/'))
    

    output = serial_ins.rwSerial('svn up --username %s --password %s'\
                  %(globalVariable.SVN_USER, globalVariable.SVN_PASSWD), 
                  kw=['yes','bjdevel03'])
    if filter(lambda line: re.search('yes', line, re.I), output):
        output = serial_ins.rwSerial('yes',kw='bjdevel03')
    if filter(lambda line: re.search('bjdevel03', line, re.I), output):
        pass
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[sshConn]',
                        'Failed to svn update.'))
        sys_exitfunc(-58, logger_obj)

    if checkCLI(serial_ins, 'exit', 
                 '', 
                 logger_obj, positive=True):
        pass
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[sshConn]',
                        'Failed to exit from svn server.'))
        sys_exitfunc(-56, logger_obj)
    
    checkCLI(serial_ins, 'rm -rf /mnt/shell/*', 
                 'No such', 
                 logger_obj, positive=False)
    
    if os.path.normpath(globalVariable.SVN_RLTV_PATH.strip()) == '.':
        case_path = '/home/lium/test_shell/*'
    else:
        case_path = os.path.join(
                        '/home/lium/test_shell/',
                        os.path.normpath(globalVariable.SVN_RLTV_PATH.strip()))
    
    output = serial_ins.rwSerial(('scp -r %s@%s:%s'
                                  ' /mnt/shell') %(globalVariable.LU_USER, 
                                                   globalVariable.SVN_SERVER,
                                                   case_path),
                                 kw=['yes', 'password'])

    if filter(lambda line: re.search('yes', line, re.I), output):
        output = serial_ins.rwSerial('yes',kw='password')
        serial_ins.rwSerial(globalVariable.LU_PASSWD)
    if filter(lambda line: re.search('password', line, re.I), output):
        serial_ins.rwSerial(globalVariable.LU_PASSWD)
    else:
        logger_obj.error(LogMsgFormat.setSysLogFmt('[sshConn]',
                        'Failed to scp file to target.'))
        sys_exitfunc(-58, logger_obj)
    time.sleep(5)
    checkCLI(serial_ins, 'sync','failed',
            logger_obj, positive=False)
    checkCLI(serial_ins, 'chmod -R 777 /mnt/shell','failed', 
            logger_obj, positive=False)
    checkCLI(serial_ins, 'cd /mnt/shell','failed', 
            logger_obj, positive=False)
    return True

def execShell(serial_ins, shell_file, failed_output=''):

    act_result = serial_ins.rwSerial(shell_file, 
                                     time_out=globalVariable.MAX_EXEC_TIME)

    note_info = ''
    result = None

    if filter(lambda kw : re.search(globalVariable.RIGHT_RESULT, kw, re.I), 
              act_result):
        result = True
    else:
        failed_infos = filter(lambda kw : re.search(globalVariable.WRONG_RESULT, kw, re.I)\
                          or re.search(failed_output, kw, re.I), 
                          act_result)
        for failed_case in failed_infos:
            search_ins = re.search('%s(.*)' %globalVariable.WRONG_RESULT, failed_case, re.I)
            if globalVariable.WRONG_RESULT in failed_case:
                note_info = search_ins.groups()[0]
                break
        
        result = False

    CaseLogSetting.addExecTmsTOBody()
    CaseLogSetting.addBodytoLog(None, shell_file, 
                                globalVariable.RIGHT_RESULT,
                                act_result, result)
    #CaseLogSetting.addSplitLine()
    return (result, note_info)


def execCase(serial_ins, logger_obj, exec_item):

#Initial base information
    exec_shell = ''
    rig_rel_count = 0
    wro_rel_count = 0
    ts_note_info = ''

    globalVariable.serial_config['act_list'] = []
    globalVariable.serial_config['skw_list'] = copy.deepcopy({})

    #Add title to case log
    CaseLogSetting.addTitletoLog()

    #Assign case running times to variable
    if globalVariable.serial_config['exec_times'] != '':
        exec_time = globalVariable.serial_config['exec_times']
    else:
        exec_time = globalVariable.serial_config['df_exec_times']

    #Running each test case
    for i in range(0,exec_time):
        logger_obj.info(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                        'Execute test case {%s} on the %dth times \n' %
                        (globalVariable.serial_config['case_name'], i+1)))

        #Execute case through execution list
        exec_shell = './' + exec_item

        case_result,ts_note_info = execShell(serial_ins, exec_shell)

        if case_result :
            pass
        elif not case_result:
            wro_rel_count += 1
            unmountBefReboot(serial_ins, logger_obj)
            checkCLI(serial_ins, 'mount -o rw /dev/sda1 /mnt', 
                         'No such', 
                         logger_obj, positive=False)
            checkCLI(serial_ins, 'cd /mnt/shell','failed', 
                         logger_obj, positive=False)
            if exec_time == 1 and globalVariable.FAILED_CASE_EXEC_TIMES:
                for j in xrange(0,globalVariable.FAILED_CASE_EXEC_TIMES):
                    if execShell(serial_ins, exec_shell)[0]:
                        rig_rel_count += 1
                    else:
                        wro_rel_count += 1
                        unmountBefReboot(serial_ins, logger_obj)
                        if j < globalVariable.FAILED_CASE_EXEC_TIMES:
                            checkCLI(serial_ins, 'mount -o rw /dev/sda1 /mnt', 
                                     'No such', 
                                     logger_obj, positive=False)
                            checkCLI(serial_ins, 'cd /mnt/shell','failed', 
                                     logger_obj, positive=False)

    CaseLogSetting.addSplitLine()
    if wro_rel_count:
        CaseLogSetting.addEndtolog(False)
    else:
        CaseLogSetting.addEndtolog(True)

    #Refresh test case information file. (p:pass , f:fail , b:block)
    globalVariable.serial_config['case_num']['total'] += 1
    if wro_rel_count == 0:
        globalVariable.serial_config['case_num']['passed'] += 1
        return ('Passed', ts_note_info)
    else:
        globalVariable.serial_config['case_num']['failed'] += 1
        return ('Failed', ts_note_info)


