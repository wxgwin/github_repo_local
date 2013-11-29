import logging

import parseConfig
from staticMethods import *

class LoadSysfileToTarget():
    
    def __init__(self, *logger_obj):
        self.kermitfd = os.path.join(os.getcwd(), 'kermit_script')
        self.kermitfile = os.path.join(self.kermitfd, 
                                     'auto_update_flash.ker')
        self.reboot_file = os.path.join(os.getcwd(),'reboot.sh')

        if logger_obj and isinstance(logger_obj[0],logging.Logger):
            self.logger_obj = logger_obj[0]
        else:
            class printMsg():
                def info(self,msg):
                    print msg
                    
                def error(self,msg):
                    print msg
                
                def warn(self,msg):
                    print msg

            self.logger_obj = printMsg()
        self.logger_obj.info(LogMsgFormat.setSysLogFmt('[LoadBootloader]',
                        'Loading rootfs and kernel to device'))

    def loadFileToTarget(self, serial_port, nfs_server, rootfs_file, kernel_file):

        cmd_line = '%s %s %s %s %s %s' %(self.kermitfile, 
                                      serial_port, 
                                      nfs_server, 
                                      rootfs_file,
                                      kernel_file,
                                      self.reboot_file)

        return_code, output, strrout = execCLI(cmd_line,shell=False)

        #print return_code, output, strrout

        if re.search('All update successfully', output, re.I):
            self.logger_obj.info(LogMsgFormat.setSysLogFmt('[LoadBootloader]',
                    'Successfully load kernel and rootfs file to target : %s' 
                    % output))
            return True
        else:
            
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[LoadBootloader]',
                        'Failed to load kernel and rootfs file to target %s' 
                        %output))
            print 'Unknown error'
            return False

    def loadShellfileToTarget(self, shell_file, serial_port):

        shell_file_fd = os.path.join(os.getcwd(), 'test_shell')
        abs_file = os.path.join(shell_file_fd, shell_file)
        if not os.path.exists(abs_file):
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[LoadBootloader]',
                        'Shell_file %s does not exist on path %s' %(shell_file,
                                                                shell_file_fd)))
            sys_exitfunc(-62, self.logger_obj)
            return False
        cmd_line = 'ttpmacro.exe %s %s %s %s' %(self.ttlshellfile, 
                                             shell_file_fd, 
                                             shell_file, 
                                             serial_port)
        print cmd_line
        returncode, output, strrout = execCLI(cmd_line, shell=False)
        
        if re.search('error', output, re.I) and returncode != 0:
            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[LoadBootloader]',
                        'Failed to shell_file %s to target' %shell_file))
            sys_exitfunc(-64, self.logger_obj)
            return False
        else:
            return True
    
    def getHeadVersion(self):
        svn_path = 'http://trac/svn/avl_soc/platform/branches/mtos_v2'
        snv_get_ver_cmd = 'svn info %s --username %s --password %s' %(
                                            svn_path, 
                                            globalVariable.SVN_USER,
                                            globalVariable.SVN_PASSWD)
        
        returncode, output, strrout = execCLI(snv_get_ver_cmd,shell=False)
        
        code_version = re.search('Revision: (\d+)', output, re.I).groups()[0]
        #print str(output)
        return code_version


def main():

    load_sysfile_ins = LoadSysfileToTarget()
    load_sysfile_ins.kermitfile =  os.path.join('../kermit_script', 
                                                'auto_update_flash.ker')
    load_sysfile_ins.reboot_file = '../reboot.sh'
    serial_config = parseConfig.ParseConfigFile('../AutoBSPConfig.cfg').readConfigFile()

    if not globalVariable.SVN_CODE_VER:
        globalVariable.SVN_CODE_VER = load_sysfile_ins.getHeadVersion()
    '''
    if sdk_lib.globalVariable.LOAD_BOOT:
        load_sysfile_ins.loadFileToTarget('loader',
                                          sdk_lib.globalVariable.LOAD_BOOT,
                                          serial_config['serial_port'][3:])
    '''
    # Load kernel file to target
    if globalVariable.LOAD_KERNEL and globalVariable.LOAD_ROOTFS:
        for loadsf_i in range(1, 6):
            if load_sysfile_ins.loadFileToTarget(
                                    serial_config['serial_port'],
                                    globalVariable.LOAD_NFS_SERVER,
                                    globalVariable.LOAD_ROOTFS,
                                    globalVariable.LOAD_KERNEL):

                break
            if loadsf_i == 5:
                sendNagativeMail(
                            'Failed to load kernel and rootfs to target\n')
                #sys_exitfunc(-60, 'print')

if __name__ == '__main__':
    main()