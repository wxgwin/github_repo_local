r'''Global variables
This variables:
  -- serial_config['exec_times']   : Running times for a group test case.
                               (Defined in test case step)
  -- serial_config['df_exec_times']: Running times for a group test case.
                               (Defined in configure file)
  -- serial_config['case_name']    : Test case name
  -- serial_config['exec_type']    : Executed type. (Reserved variable)
  -- serial_config['case_fldr']    : Test case folder.
  -- serial_config['in_list']      : All IN info of a group of test case. 
  -- serial_config['out_list']     : All OUT info of a group of test case.
  -- serial_config['file_lines']   : All lines info of test case file.
  -- serial_config['case_num']     : All test cases state info.
  -- serial_config['flag_ifc']     : Boolean value, YES: Ignore failed case;
                                     NO: Sensitive to failed case.
'''
import os


MAIL_LIST = []

SDK_LIB_VER = ''

serial_config = {}

serial_config['target_type'] = ''
serial_config['exec_times'] = 1
serial_config['df_exec_times'] = 1

serial_config['case_name'] = ''
# Add test case title variable
serial_config['case_title'] = ''
serial_config['exec_type'] = 'testshell'
serial_config['case_fldr'] = os.getcwd()

serial_config['in_list']  = []
serial_config['out_list'] = []
#serial_config['act_list'] = []
#serial_config['cmp_result'] = []
serial_config['file_lines'] = []

serial_config['case_num'] = {'total':0,'passed':0,'failed':0,'blocked':0}

serial_config['flag_ifc'] = False