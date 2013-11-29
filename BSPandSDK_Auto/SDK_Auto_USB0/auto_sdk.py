r'''SDK Automation Tool
Functions:
  -- read C:\TL_AESDK.txt , get test case file path [C:\TL_AUTO\TestCaseInfo.txt]
  -- read c:\SDKAT_sys_log.txt, get test case information
  -- send/receive message through target
  -- verify result of expected result and acutal result
  -- exports system log  c:\SDKAT_sys_log.txt
  -- export report of each test case
  -- refresh C:\TL_AUTO\TestCaseInfo.txt in real time 
'''
import os
import sys
import datetime

import sdk_lib


if __name__ == "__main__":
    '''SDK Automation Tool
    Main function.
    '''


    start_no = 0
    end_no = 0
    
    print 'folder:',sdk_lib.globalVariable.serial_config['case_fldr']
    # Create case log folder
    sdk_lib.staticMethods.CaseLogSetting.mkCasedir()
    
    # Set system log format and prepare to collect logs
    logging_ins = sdk_lib.collectLogs.CollectSysLoging()
    
    logging_ins.addSysLog(os.path.join(
                    sdk_lib.staticMethods.CaseLogSetting.abs_caselog_dir, 
                    'SDKAT_sys_%s.log' % 
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    logger_obj = logging_ins.getLogger()

    # Get test case info file
    tl_case_file = os.path.join(os.getcwd(), 'TestCaseInfo.txt')
    sdk_lib.globalVariable.serial_config['case_fldr'] = os.getcwd()
    # Parse configure file
    serial_config = sdk_lib.parseConfig.readConfigFile()

    #print serial_config
    # Initial serial port
    conn_ts = sdk_lib.connectSerial.ConnectSerial(serial_config, logger_obj)

    # Parse test case file
    ins_prsTLF = sdk_lib.parseTLfile.ParseTLcaseFile(tl_case_file, logger_obj)
    start_no,end_no = ins_prsTLF.getCaseSection(start_no)


    while True:
        if not start_no or not end_no or \
            end_no == len(serial_config['file_lines'])-1:
            sdk_lib.staticMethods.RecycleResource(logger_obj, tl_case_file)
            break
        else:
            #Get each test case information
            ins_prsTLF.getCaseInfo(start_no, end_no)
            ins_prsTLF.getInOutInfo(start_no, end_no)

            #Execute a group test case
            case_state = sdk_lib.execTestcase.execCase(conn_ts, 
                                                       ins_prsTLF,
                                                       logger_obj, 
                                                       start_no, 
                                                       end_no)

            sdk_lib.StatisticsCaseCount.wirteCaseStateToFile(case_state, 
                            sdk_lib.globalVariable.serial_config['case_name'], 
                            sdk_lib.globalVariable.serial_config['case_title'])

        start_no, end_no = ins_prsTLF.getCaseSection(end_no + 1)
    sdk_lib.staticMethods.StatisticsCaseCount.writeDataToFile()
    sdk_lib.StatisticsCaseCount.HTML_PAGE.printOut(sdk_lib.StatisticsCaseCount.HTML_FILE_NAME)
    sdk_lib.staticMethods.StatisticsCaseCount.sendMail()
    
    logger_obj.info(sdk_lib.staticMethods.LogMsgFormat.setSysLogFmt('[System]',
                                                                    'Finished all test'))
    logging_ins.closeHnadler()
    sys.exit(0)
