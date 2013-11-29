r'''Parse configure file
This functions:
  --  readConfigFile ()
'''

import ConfigParser
import os,sys

import globalVariable


class ParseConfigFile(object):

    def __init__(self,cfg_file_name='AutoBSPConfig.cfg'):
        self.cfg_file_name = cfg_file_name
        cfg_file_abspath = os.path.join(globalVariable.serial_config['case_fldr'],
                                        self.cfg_file_name)
        #print cfg_file_abspath
        self.config = ConfigParser.ConfigParser()
    
        try:
            self.cfg_fp = open(cfg_file_abspath,"r")
            self.config.readfp(self.cfg_fp)
        except Exception,e:
            print 'ParseConfigFile:',e
            sys.exit(-1)

    def parseConfigItem(self, section, item, item_type='get'):
        if self.config.has_section(section):
            if self.config.has_option(section, item):
                    return getattr(self.config, item_type)('platform', 
                                                           'target_type')
            else:
                return False
        else:
            False

    def readConfigFile(self):
        '''Parse configure file
        Get global user-defined argument through parsing configure file,
        configure file absolute path C:\TL_AUTO\AutoSDKself.config.cfg
        Content of configure file:
        -- [serial] : All variables about serial connection.
        -- [connection] : Connection times
        -- [prompt] : Prompt characters of OS, (bootloader is "Libra>", 
                      testshell is "###>", linux is "/.*#").
        -- [test_case] : All variables about test case running.
        -- [log_info] : Log path. (system log path is C:\SDKAT_sys_log.txt
                                   case log path is C:\TL_AUTO\CASE_LOG)
        '''

        if self.config.has_section('platform'):
            if self.config.has_option('platform', 'target_type'):
                globalVariable.serial_config['target_type'] = \
                self.config.get('platform', 'target_type')
            else:
                globalVariable.serial_config['df_exec_times'] = 1
        if self.config.has_section('serial'):
            if self.config.has_option('serial', 'serial_port'):
                globalVariable.serial_config['serial_port'] = \
                self.config.get('serial','serial_port')
            else:
                raise RuntimeError("Argument serial_port is missing")

            if self.config.has_option('serial', 'baudrate'):
                globalVariable.serial_config['baudrate'] = \
                self.config.getint('serial', 'baudrate')
            else:
                raise RuntimeError("Argument baudrate is missing")

            if self.config.has_option('serial', 'xonxoff'):
                globalVariable.serial_config['xonxoff'] = \
                self.config.getint('serial', 'xonxoff')
            else:
                raise RuntimeError("Argument xonxoff is missing")

            if self.config.has_option('serial', 'timeout'):
                globalVariable.serial_config['timeout'] = \
                self.config.getint('serial', 'timeout')
            else:
                raise RuntimeError("[Exception] : Argument timeout is missing")
            
            if self.config.has_option('serial', 'reboot_delay'):
                globalVariable.serial_config['reboot_delay'] = \
                self.config.getint('serial', 'reboot_delay')
            else:
                raise RuntimeError("[Exception] : Argument reboot_delay is missing")

        if self.config.has_section('connection'):
            if self.config.has_option('connection', 'conn_times'):
                globalVariable.serial_config['conn_times'] = \
                self.config.getint('connection', 'conn_times')
            else:
                globalVariable.serial_config['conn_times'] = 3

            if self.config.has_option('connection', 'reboot_switch'):
                globalVariable.REBOOT_SWITCH = \
                self.config.getboolean('connection', 'reboot_switch')
            else:
                globalVariable.REBOOT_SWITCH = True

        if self.config.has_section('prompt'):
                globalVariable.serial_config['bl_prompt'] = \
                self.config.get('prompt', 'bl_prompt')
                globalVariable.serial_config['ts_prompt'] = \
                self.config.get('prompt', 'ts_prompt')
                globalVariable.serial_config['lx_prompt'] = \
                self.config.get('prompt', 'lx_prompt')
        else:
            raise RuntimeError("[Exception] : Section prompt is missing")

        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'df_exec_times'):
                globalVariable.serial_config['df_exec_times'] = \
                self.config.getint('test_case', 'df_exec_times')
            else:
                globalVariable.serial_config['df_exec_times'] = 1
        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'ignore_failed_case'):
                globalVariable.serial_config['flag_ifc'] = \
                self.config.getboolean('test_case', 'ignore_failed_case')
        
        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'failed_case_exec_times'):
                globalVariable.FAILED_CASE_EXEC_TIMES =  \
                self.config.getint('test_case', 'failed_case_exec_times')
            else:
                globalVariable.FAILED_CASE_EXEC_TIMES = 0
        else:
            globalVariable.FAILED_CASE_EXEC_TIMES = 0

        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'reboot_during_case'):
                globalVariable.CASE_REBOOT_SWITCH = \
                self.config.getboolean('test_case', 'reboot_during_case')

        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'max_execute_time'):
                globalVariable.MAX_EXEC_TIME = \
                self.config.getint('test_case', 'max_execute_time')
                
        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'execution_module'):
                globalVariable.EXECUTION_MODULE = \
                self.config.get('test_case', 'execution_module').split(',')

        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'execution_priority'):
                globalVariable.EXECUTION_PRIORITY = \
                self.config.get('test_case', 'execution_priority').split(',')
                globalVariable.EXECUTION_PRIORITY = map(
                                            lambda kw:kw.split(),
                                            globalVariable.EXECUTION_PRIORITY)

        if self.config.has_section('test_case'):
            if self.config.has_option('test_case', 'sorted_keyword'):
                globalVariable.CASE_SORTED_KEY = \
                self.config.get('test_case', 'sorted_keyword')

        #Parse section [loadfile]
        if self.config.has_section('loadfile'):
            if self.config.has_option('loadfile', 'load_nfs_server'):
                globalVariable.LOAD_NFS_SERVER = \
                self.config.get('loadfile', 'load_nfs_server')

        if self.config.has_section('loadfile'):
            if self.config.has_option('loadfile', 'load_bootloader'):
                globalVariable.LOAD_BOOT = \
                self.config.get('loadfile', 'load_bootloader')

        if self.config.has_section('loadfile'):
            if self.config.has_option('loadfile', 'load_kernel'):
                globalVariable.LOAD_KERNEL = \
                self.config.get('loadfile', 'load_kernel')

        if self.config.has_section('loadfile'):
            if self.config.has_option('loadfile', 'load_rootfs'):
                globalVariable.LOAD_ROOTFS = \
                self.config.get('loadfile', 'load_rootfs')
        #Parse section [svn_account]
        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_server'):
                globalVariable.SVN_SERVER = \
                self.config.get('svn_info', 'svn_server')
        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_user'):
                globalVariable.SVN_USER = \
                self.config.get('svn_info', 'svn_user')

        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_passwd'):
                globalVariable.SVN_PASSWD = \
                self.config.get('svn_info', 'svn_passwd')
                
        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_code_version'):
                globalVariable.SVN_CODE_VER = \
                self.config.get('svn_info', 'svn_code_version')

        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'linux_user'):
                globalVariable.LU_USER = \
                self.config.get('svn_info', 'linux_user')

        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'linux_passwd'):
                globalVariable.LU_PASSWD = \
                self.config.get('svn_info', 'linux_passwd')

        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_path'):
                globalVariable.SVN_PATH = \
                self.config.get('svn_info', 'svn_path')

        if self.config.has_section('svn_info'):
            if self.config.has_option('svn_info', 'svn_rltv_path'):
                globalVariable.SVN_RLTV_PATH = \
                self.config.get('svn_info', 'svn_rel_path')

        if self.config.has_section('mail_pool'):
            if self.config.has_option('mail_pool', 'mail_list'):
                globalVariable.MAIL_LIST = \
                self.config.get('mail_pool', 'mail_list')

        return globalVariable.serial_config

