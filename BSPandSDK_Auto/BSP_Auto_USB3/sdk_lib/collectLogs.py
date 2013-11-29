r'''CollectSysLoging ,Collect system log
  This functions:
  -- Initial setting for system log.
  -- Set system level. 
'''

import os
import logging


class CollectSysLoging():
    '''CollectSysLoging
    Colloect system log; Add all log with level under logging.NOTSET to file
    '''

    def __init__(self):
        self.logger = logging.getLogger()
        self.sys_handler = None
        self.case_handler = None

    def addSysLog(self, sys_filename):
        'Add system level log'
        if os.path.exists(sys_filename):
            try:
                fp = open(sys_filename, 'w+')
                fp.truncate()
            except Exception,e:
                print 'addSysLog', e
            finally:
                fp.close()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)-8s] : %(message)s',
            '%a, %d %b %Y %H:%M:%S',)
        self.sys_handler=logging.FileHandler(sys_filename)
        self.sys_handler.setFormatter(formatter)
        self.logger.addHandler(self.sys_handler)
        self.logger.setLevel(logging.NOTSET)

    def getLogger(self):
        return self.logger

    def closeHnadler(self):
        self.sys_handler.close()
