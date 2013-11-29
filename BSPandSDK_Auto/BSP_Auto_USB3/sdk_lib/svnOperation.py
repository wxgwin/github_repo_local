
from staticMethods import *

class SVNOperation(object):
    
    def __init__(self, logger_obj):
        self.svn_co_folder = os.path.join(os.getcwd(), 'test_shell')
        self.svn_server = globalVariable.SVN_PATH
        self.logger_obj = logger_obj

    def checkoutFile(self, file_name=''):
        self.logger_obj.info(LogMsgFormat.setSysLogFmt('[SVNOperation]',
                        'Checkout file %s to localhost' \
                        %os.path.join(self.svn_server, file_name)))
        '''
        if file_name:
            abs_file_path = os.path.join(self.svn_server, file_name)
        else:
        '''
        abs_file_path = self.svn_server
        if os.path.exists(self.svn_co_folder):
            co_cmd = 'svn up --username %s --password %s %s' \
                    %(globalVariable.SVN_USER,
                      globalVariable.SVN_PASSWD,
                      os.path.join(self.svn_co_folder, file_name))
        else:
            co_cmd = 'svn co --username %s --password %s %s %s' \
                     %(globalVariable.SVN_USER,
                       globalVariable.SVN_PASSWD,
                       str(abs_file_path),
                       self.svn_co_folder)

        return_code, output, strrout = execCLI(co_cmd)

        if re.search('error', output, re.I) \
        or re.search('error', strrout, re.I) :

            self.logger_obj.error(LogMsgFormat.setSysLogFmt('[SVNOperation]',
                        'Failed to co file %s to localhost' \
                        %os.path.join(self.svn_server, file_name)))
            return False
        else:
            if os.path.exists(os.path.join(self.svn_co_folder, file_name)): 
                return True
            else:
                return False

    def updateFile(self, file_name=''):
        self.logger_obj.info(LogMsgFormat.setSysLogFmt('[SVNOperation]',
                        'Update file %s to localhost' \
                        %os.path.join(self.svn_server, file_name)))
    
