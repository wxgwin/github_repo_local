r'''SDK Automation Tool
Functions:
  -- read C:\TL_AUTO.txt , get test case file path [C:\TL_AUTO\TestCaseInfo.txt]
  -- read c:\BSPAT_sys_log.txt, get test case information
  -- send/receive message through target
  -- verify result of expected result and acutal result
  -- exports system log  c:\BSPAT_sys_log.txt
  -- export report of each test case
  -- refresh C:\TL_AUTO\TestCaseInfo.txt in real time 
'''
import datetime
import os
import re
import sys
import time
import pprint

import sdk_lib

if __name__ == "__main__":
    '''SDK Automation Tool
    Main function.
    '''
    global HUDSON_JOB_NAME
    start_no = 0
    end_no = 0
    case_list = []
    temp_list = []

    if len(sys.argv) == 2 and sys.argv[1]:
        sdk_lib.staticMethods.StatisticsCaseCount.HUDSON_JOB_NAME = sys.argv[1]

    # Create case log folder
    sdk_lib.staticMethods.CaseLogSetting.mkCasedir()

    # Set system log format and prepare to collect logs
    logging_ins = sdk_lib.collectLogs.CollectSysLoging()
    logging_ins.addSysLog(os.path.join(
                    sdk_lib.staticMethods.CaseLogSetting.abs_caselog_dir,
                    'BSPAT_sys_%s.log' % 
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    logger_obj = logging_ins.getLogger()

    # Parse TestLink auto file  'c:\TL_AUTO.txt'
    tl_case_file = os.path.join(os.getcwd(), 'TestCaseInfo.txt')
    sdk_lib.globalVariable.serial_config['case_fldr'] = os.getcwd()

    # Parse configure file
    serial_config = sdk_lib.parseConfig.ParseConfigFile().readConfigFile()

    load_sysfile_ins = sdk_lib.loadSysfile.LoadSysfileToTarget(logger_obj)

    if not sdk_lib.globalVariable.SVN_CODE_VER:
        sdk_lib.globalVariable.SVN_CODE_VER = load_sysfile_ins.getHeadVersion()
    '''
    if sdk_lib.globalVariable.LOAD_BOOT:
        load_sysfile_ins.loadFileToTarget('loader',
                                          sdk_lib.globalVariable.LOAD_BOOT,
                                          serial_config['serial_port'][3:])
    # Load kernel file to target
    if sdk_lib.globalVariable.LOAD_KERNEL and sdk_lib.globalVariable.LOAD_ROOTFS:
        for loadsf_i in range(1, 6):
            if load_sysfile_ins.loadFileToTarget(
                                    serial_config['serial_port'],
                                    sdk_lib.globalVariable.LOAD_NFS_SERVER,
                                    sdk_lib.globalVariable.LOAD_ROOTFS,
                                    sdk_lib.globalVariable.LOAD_KERNEL):

                break
            if loadsf_i == 5:
                sdk_lib.staticMethods.sendNagativeMail(
                            'Failed to load kernel and rootfs to target\n')
                sdk_lib.staticMethods.sys_exitfunc(-60, logger_obj)

    time.sleep(2)
    '''
    # Initial serial port
    conn_ts = sdk_lib.connectSerial.ConnectSerial(serial_config, logger_obj)

    # Initial environment on target
    if not sdk_lib.execTestcase.initEnv(conn_ts, logger_obj):
        logger_obj.error(\
        sdk_lib.staticMethods.LogMsgFormat.setSysLogFmt('[initEnv]',
                                                    'Failed to exec initEnv'))
        sdk_lib.staticMethods.sys_exitfunc(-80, logger_obj)

    if not sdk_lib.execTestcase.sshConn(conn_ts, logger_obj):
        logger_obj.error(\
        sdk_lib.staticMethods.LogMsgFormat.setSysLogFmt('[sshConn]',
                                                    'Failed to exec sshConn'))
        sdk_lib.staticMethods.sys_exitfunc(-82, logger_obj)

    # Get test case list
    ls_result = conn_ts.rwSerial('ls BSP*.sh')
    for bsp_line in \
    filter(lambda line: re.search('BSP.*?.sh', line, re.I), ls_result):
        temp_list.extend(re.findall('BSP[^*]*?.sh', bsp_line, re.I))

    # Sort list
    case_list = sorted(temp_list, key=lambda x:int(x[4:-3]))

    sort_keyword = sdk_lib.globalVariable.CASE_SORTED_KEY
    case_info_list = sdk_lib.staticMethods.getCaseTitleMap(
                                            sort_key=sort_keyword)
    # print case_info_list
    
    def filteExecTc(case_info):
        if sdk_lib.globalVariable.EXECUTION_PRIORITY:
            case_info_list = filter(
                        lambda a:a[1] in sdk_lib.globalVariable.EXECUTION_PRIORITY,
                        case_info)

        if sdk_lib.globalVariable.EXECUTION_MODULE:
            case_info_list = filter(
                        lambda a:a[2] in sdk_lib.globalVariable.EXECUTION_MODULE,
                        case_info)
        case_info_list = filter(lambda a:a[0] + '.sh' in case_list,
                                case_info)
        return case_info_list
    
    case_info_list = filteExecTc(case_info_list)
    # logger_obj.info(sdk_lib.staticMethods.LogMsgFormat.setSysLogFmt('[System]',
    #                                                            case_info_list))

    for bsp_info in case_info_list:
        # Get each test case information
        sdk_lib.globalVariable.serial_config['case_name'] = \
        bsp_shell_name = bsp_info[0] + '.sh'
        note_info = ''
        
        if bsp_shell_name not in case_list:
            continue
        else:
            if (sdk_lib.globalVariable.EXECUTION_PRIORITY  and\
                bsp_info[1] not in sdk_lib.globalVariable.EXECUTION_PRIORITY)\
                or (sdk_lib.globalVariable.EXECUTION_MODULE and \
                    bsp_info[2] not in sdk_lib.globalVariable.EXECUTION_MODULE):
                continue
        
        case_state, note_info = sdk_lib.execTestcase.execCase(conn_ts,
                                                              logger_obj,
                                                              bsp_shell_name)

        sdk_lib.StatisticsCaseCount.wirteCaseStateToFile(case_state,
                                                         bsp_info,
                                                         note_info)
        if sdk_lib.globalVariable.CASE_REBOOT_SWITCH:
            conn_ts.rwSerial('cd /', kw='')
            conn_ts.rwSerial('umount /mnt', kw='')
            conn_ts.rebootTarget()
    
    # Save all case info to txt file
    sdk_lib.staticMethods.StatisticsCaseCount.writeDataToFile()
    
    # Save all case info to html page
    sdk_lib.StatisticsCaseCount.HTML_PAGE.printOut(
                                    sdk_lib.StatisticsCaseCount.HTML_FILE_NAME)
    
    # Save all case info as excel file
    sdk_lib.StatisticsCaseCount.EXCEL_STISTIC_INS.saveExcel(
            os.path.join(
                sdk_lib.staticMethods.CaseLogSetting.abs_caselog_dir,
                sdk_lib.staticMethods.StatisticsCaseCount.EXCEL_STISTIC_PAGE))

    # Send case info by mail
    sdk_lib.staticMethods.StatisticsCaseCount.sendMail()
    
    # Finish test
    logger_obj.info(sdk_lib.staticMethods.LogMsgFormat.setSysLogFmt('[System]',
                                                                    'Finished all test'))
    logging_ins.closeHnadler()
    sys.exit(0)
