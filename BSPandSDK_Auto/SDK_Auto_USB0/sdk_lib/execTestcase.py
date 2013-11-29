r'''Execute a group of IN/OUT
This Classes or functions
  -- execitem(serial instance, system logger ins, start line of test case ,
              end line of test case)
              : Execute a pair of IN/OU
  -- execCase(serial instance, system logger ins, start line of test case ,
              end line of test case)
              : Execute a group of test case
'''

import copy
import time
import connectSerial



#import globalVariable
from staticMethods import *


def checkKwFromMSG(in_msg, out_msg, logger_obj):

    p_in_msg  = ''
    p_out_msg = []
    
    def checkSKW(msg):
        tmp_msg = msg
        if '@' in msg:
            return ListandStrOperate.replaceSpfyString(tmp_msg)
        else:
            return msg

    p_in_msg = checkSKW(in_msg)

    for p_out_msg_item in out_msg:
        p_out_msg.append(checkSKW(p_out_msg_item))
    #Get in/out message from a specify file
    if 'FILE:' in in_msg:
        p_in_msg = FileOperate.readINFile(in_msg, logger_obj)

    if 'FILE:' in string.join(out_msg):
        p_out_msg = FileOperate.readOUTFile(out_msg, logger_obj)
        
    return (p_in_msg, p_out_msg)

def execUnitINOUT(serial_ins, in_msg, out_msg, unitto, logger_obj):
    act_msg = []
    avl_out_msg = []
    diff_state = True

    if not in_msg or not out_msg[0]:
        if not in_msg:
            in_msg  = 'Imported file of IN does not exist.'
            avl_out_msg = ''
        if not out_msg[0]:
            avl_out_msg = 'Imported file of OUT does not exist.'

        act_msg = []
        diff_state = False
    else:
        #Catch actual output info
        act_msg = serial_ins.rwSerial(in_msg.strip(),unitto)

        avl_out_msg = ListandStrOperate.removeSpyKw(out_msg,'\S+')

        #Compare expected result with actual result
        diff_state = ListandStrOperate.diffList(avl_out_msg, act_msg)

        if not diff_state:
            logger_obj.warn(
                LogMsgFormat.setSysLogFmt(
                    '[ExecTestCase]',
                    'Result is unmatched: Actual result {%s} != '
                    %act_msg[1:] + 'Expected result {%s}\n' %
                    (avl_out_msg)
                                          )
                            )

        else:
            ListandStrOperate.getSpyStrMap(out_msg, act_msg)
            logger_obj.info(
                LogMsgFormat.setSysLogFmt(
                    '[ExecTestCase]',
                    'Result is matched: Actual result {%s} =' 
                    %act_msg[1:] + 'Expected result {%s}\n' %
                    (avl_out_msg)
                                          )
                            )
    return (avl_out_msg, act_msg, diff_state)

def execitem(serial_ins, logger_obj, exec_item, start_no, end_no):

    act_diff_state = True

    #Initial basic information
    if exec_item.has_key('IN'):
        tc_in = exec_item['IN']
    else:
        tc_in = []
    if exec_item.has_key('OUT'):
        tc_out = exec_item['OUT']
    else:
        tc_out = []
    if exec_item.has_key('rbtflg'):
        if isinstance(exec_item['rbtflg'], bool):
            tc_rbt = [exec_item['rbtflg']]
        else:
            tc_rbt = exec_item['rbtflg']
    else:
        tc_rbt = [False]
    if exec_item.has_key('unitto'):
        tc_unitto = exec_item['unitto']
    else:
        tc_unitto = [None]

    if exec_item.has_key('waittms'):
        tc_waittms = exec_item['waittms']
    else:
        tc_waittms = [None]

    if exec_item.has_key('subtms'):
        tc_subtms = exec_item['subtms']
    else:
        tc_subtms = 1
    
    if not tc_in or not tc_out:
        logger_obj.warn(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                        'Test case {%s} does not have IN/OUT any more') %
                        globalVariable.serial_config['case_name'])
        CaseLogSetting.addBodytoLog(casetype = 'No_Info')

        return None
    elif len(globalVariable.serial_config['out_list']) != \
    len(globalVariable.serial_config['in_list']):
        logger_obj.warn(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                        'IN info and OUT info are not in pair! \n' + 
                        'IN = {%s} \n OUT = {%s}' %
                        (globalVariable.serial_config['in_list'] , 
                        globalVariable.serial_config['out_list'])))
        CaseLogSetting.addBodytoLog(casetype = 'No_Pair')
        return None
    elif len(globalVariable.serial_config['out_list']) == \
    len(globalVariable.serial_config['in_list']):

        for i in range(0,int(tc_subtms)):
            if tc_subtms > 1:
                CaseLogSetting.addsSubExecTmsTOBoday(i + 1)
            sub_act_state = True

            for rbt_flg, unitto, waittms, in_msg, out_msg in zip(tc_rbt, 
                                                        tc_unitto, 
                                                        tc_waittms, 
                                                        tc_in, 
                                                        tc_out):
                diff_state = True

                #User-defined reboot
                if True == rbt_flg:
                    logger_obj.info(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                                    'Reboot target by test case ! \n'))
                    CaseLogSetting.addReboottoLog(tc_subtms)
                    serial_ins.rebootTarget()

                if waittms:
                    logger_obj.info(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                                    'Test case is delayed for %d seconds ! \n' % 
                                    waittms))

                    CaseLogSetting.addDelaytimeToLog(waittms, tc_subtms)
                    time.sleep(int(waittms))
                '''
                #Checking if IN info exists keyword @XXX
                if '@' in in_msg:
                    in_msg = ListandStrOperate.replaceSpfyString(in_msg)

                #Get in/out message from a specify file
                if 'FILE:' in in_msg:
                    in_msg = FileOperate.readINFile(in_msg, logger_obj)

                if 'FILE:' in string.join(out_msg):
                    out_msg = FileOperate.readOUTFile(out_msg, logger_obj)
                '''
                in_msg, out_msg = checkKwFromMSG(in_msg, out_msg, logger_obj)
                '''
                if not in_msg or not out_msg[0]:
                    if not in_msg:
                        in_msg  = 'Imported file of IN does not exist.'
                        avl_out_msg = ''
                    if not out_msg[0]:
                        avl_out_msg = 'Imported file of OUT does not exist.'

                    act_msg = []
                    diff_state = False

                else:
                    #Catch actual output info
                    act_msg = serial_ins.rwSerial(in_msg.strip(),unitto)
    
                    avl_out_msg = ListandStrOperate.removeSpyKw(out_msg)
    
                    #Compare expected result with actual result
                    diff_state = ListandStrOperate.diffList(avl_out_msg, act_msg)

                    if not diff_state:
                        logger_obj.warn(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                                        'Result is unmatched: Actual result {%s} != '
                                        %act_msg[1:] + 'Expected result {%s}\n' %
                                        (avl_out_msg)))
                        CaseLogSetting.addBodytoLog(None,in_msg,avl_out_msg,act_msg, diff_state)
                        sub_act_state &= diff_state
                        break
                    else:
                        ListandStrOperate.getSpyStrMap(out_msg,act_msg)
                        logger_obj.info(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                                        'Result is matched: Actual result {%s} =' 
                                        %act_msg[1:] + 'Expected result {%s}\n' %
                                        (avl_out_msg)))
                '''
                (avl_out_msg, act_msg, diff_state) = \
                execUnitINOUT(serial_ins, in_msg, out_msg, unitto, logger_obj)

                #Add IN/OUT information to case log
                CaseLogSetting.addBodytoLog(None, in_msg, avl_out_msg, 
                                            act_msg, diff_state)
                
                if not ''.join(list(set(act_msg))):
                    enter_msg = serial_ins.rwSerial('\n')
                    if filter(lambda kw:re.search('>>>', kw, re.I), enter_msg):
                        pass
                    else:
                        CaseLogSetting.addCrashInfoToLog()
                sub_act_state &= diff_state
                if diff_state or globalVariable.serial_config['flag_ifc']:
                    pass
                else:
                    break

                #globalVariable.serial_config['cmp_result'].append(str(diff_state))
            act_diff_state &= sub_act_state

        if tc_subtms > 1:
            CaseLogSetting.addSubResultToBody(act_diff_state)
        return act_diff_state

def execCase(serial_ins, prsfile_ins, logger_obj, start_no, end_no):

#Initial base information
    result = True
    whl_result = True
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
        sub_result = True

        CaseLogSetting.addExecTmsTOBody()

        logger_obj.info(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                        'Execute test case {%s} on the %dth times \n' %
                        (globalVariable.serial_config['case_name'], i+1)))

        #Branch for IN/OUT is not in pair.
        if not globalVariable.serial_config['exec_list']:
            logger_obj.warn(LogMsgFormat.setSysLogFmt('[ExecTestCase]',
                            'Test case {%s} does not have IN/OUT any more'
                            %globalVariable.serial_config['case_name']))

            CaseLogSetting.addBodytoLog(casetype='No_Info')

            if isinstance(serial_ins,connectSerial.ConnectSerial):
                serial_ins.rebootTarget()
                serial_ins.colseSerialCon()
            whl_result = None
            break

        #Execute case through execution list
        for exec_item in globalVariable.serial_config['exec_list']:

            #Execute reboot operation for case level
            if exec_item.has_key('rbtflg') and \
            True == exec_item['rbtflg'] and \
            1 == len(exec_item):
                if isinstance(serial_ins, connectSerial.ConnectSerial):
                    CaseLogSetting.addReboottoLog(1)
                    serial_ins.rebootTarget()
                    serial_ins.colseSerialCon()
            elif exec_item.has_key('IN') \
            and exec_item.has_key('OUT'):
                sub_result = execitem(serial_ins, logger_obj,
                                      exec_item, start_no, end_no)

                CaseLogSetting.addSplitLine()

                result &= bool(sub_result)
                if sub_result == True \
                or globalVariable.serial_config['flag_ifc']:
                    pass
                else:
                    break
            else:
                logger_obj.warn(LogMsgFormat.setSysLogFmt('[ExecCase]',
                                                          'Not caught way'))

        #Add result information to case log
        CaseLogSetting.addResultToBody(result)
        if sub_result == None:
            whl_result = result
            break
        else:
            whl_result &= result

        #Reboot target of system level
        if isinstance(serial_ins, connectSerial.ConnectSerial):
            serial_ins.rebootTarget()
            pass

    #Add end information to case log
    CaseLogSetting.addEndtolog(whl_result)

    #Refresh test case information file. (p:pass , f:fail , b:block)
    globalVariable.serial_config['case_num']['total'] += 1
    if whl_result == True:
        #prsfile_ins.rewriteFile(start_no, end_no, 'p')
        globalVariable.serial_config['case_num']['passed'] += 1
        return 'Passed'
    elif whl_result == False:
        #prsfile_ins.rewriteFile(start_no, end_no, 'f')
        globalVariable.serial_config['case_num']['failed'] += 1
        return 'Failed'
    elif whl_result == None:
        #prsfile_ins.rewriteFile(start_no, end_no, 'b')
        globalVariable.serial_config['case_num']['blocked'] += 1
        return 'Blocked'

