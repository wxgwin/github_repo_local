r'''Parse configure file
This functions:
  --  readConfigFile ()
'''

import ConfigParser
import os,sys

import globalVariable

def readConfigFile():
    '''Parse configure file
    Get global user-defined argument through parsing configure file,
    configure file absolute path C:\TL_AUTO\AutoSDKConfig.cfg
    Content of configure file:
    -- [serial] : All variables about serial connection.
    -- [connection] : Connection times
    -- [prompt] : Prompt characters of OS, (bootloader is "Libra>", 
                  testshell is "###>", linux is "/.*#").
    -- [test_case] : All variables about test case running.
    -- [log_info] : Log path. (system log path is C:\SDKAT_sys_log.txt
                               case log path is C:\TL_AUTO\CASE_LOG)
    '''

    cfg_file_name = 'AutoSDKConfig.cfg'

    cfg_file_abspath = os.path.join(globalVariable.serial_config['case_fldr'],cfg_file_name)
    config = ConfigParser.ConfigParser()

    try:
        cfg_fp = open(cfg_file_abspath,"r")
        config.readfp(cfg_fp)
        
        if config.has_section('platform'):
            if config.has_option('platform', 'target_type'):
                globalVariable.serial_config['target_type'] = \
                config.get('platform', 'target_type')
            else:
                globalVariable.serial_config['df_exec_times'] = 1
        if config.has_section('serial'):
            if config.has_option('serial', 'serial_port'):
                globalVariable.serial_config['serial_port'] = \
                config.get('serial','serial_port')
            else:
                raise RuntimeError("Argument serial_port is missing")

            if config.has_option('serial', 'baudrate'):
                globalVariable.serial_config['baudrate'] = \
                config.getint('serial', 'baudrate')
            else:
                raise RuntimeError("Argument baudrate is missing")

            if config.has_option('serial', 'xonxoff'):
                globalVariable.serial_config['xonxoff'] = \
                config.getint('serial', 'xonxoff')
            else:
                raise RuntimeError("Argument xonxoff is missing")

            if config.has_option('serial', 'timeout'):
                globalVariable.serial_config['timeout'] = \
                config.getint('serial', 'timeout')
            else:
                raise RuntimeError("[Exception] : Argument timeout is missing")
            
            if config.has_option('serial', 'reboot_delay'):
                globalVariable.serial_config['reboot_delay'] = \
                config.getint('serial', 'reboot_delay')
            else:
                raise RuntimeError("[Exception] : Argument reboot_delay is missing")

        if config.has_section('connection'):
            if config.has_option('connection', 'conn_times'):
                globalVariable.serial_config['conn_times'] = \
                config.getint('connection', 'conn_times')
            else:
                globalVariable.serial_config['conn_times'] = 3

        if config.has_section('prompt'):
                globalVariable.serial_config['bl_prompt'] = \
                config.get('prompt', 'bl_prompt')
                globalVariable.serial_config['ts_prompt'] = \
                config.get('prompt', 'ts_prompt')
                globalVariable.serial_config['lx_prompt'] = \
                config.get('prompt', 'lx_prompt')
        else:
            raise RuntimeError("[Exception] : Section prompt is missing")

        if config.has_section('test_case'):
            if config.has_option('test_case', 'df_exec_times'):
                globalVariable.serial_config['df_exec_times'] = \
                config.getint('test_case', 'df_exec_times')
            else:
                globalVariable.serial_config['df_exec_times'] = 1
        if config.has_section('test_case'):
            if config.has_option('test_case', 'ignore_failed_case'):
                globalVariable.serial_config['flag_ifc'] = \
                config.getboolean('test_case', 'ignore_failed_case')
                
        if config.has_section('mail_list'):
            if config.has_option('mail_list', 'mail_addr'):
                globalVariable.MAIL_LIST = \
                config.get('mail_list', 'mail_addr').strip()
        if config.has_section('test_case'):
            if config.has_option('test_case', 'lib_version'):
                globalVariable.SDK_LIB_VER = \
                config.get('test_case', 'lib_version').strip()

        return globalVariable.serial_config

    except Exception,e:
        print e
        sys.exit(-1)
