r'''Connect serial port
  This Classes:
  -- ConnectSerial : connect serial port
'''

import serial
import shlex
import subprocess
import time

#import globalVariable
from staticMethods import *

class ConnectSerial():
    '''ConnectSerial({serial_dict}, logger_ins)
    This functions:
    -- connectSerialTS : Connect target through serial port.
    -- getSerialPro    : Get serial port instance.
    -- rebootTarget    : Reboot target with reset device.
    -- colseSerialCon  : Close serial port.
    -- write           : Package write function of serial.Serial
    -- read            : Package read function of serial.Serial
    -- reSerial        : Get returned result from target after inputting a 
                         message to target
    '''

    def __init__(self,serial_port_dict,logger_obj):

        self.com = serial_port_dict['serial_port']
        self.xonxoff = serial_port_dict['xonxoff']
        self.timeout = serial_port_dict['timeout']
        self.baudrate = serial_port_dict['baudrate']
        self.bl_prompt = serial_port_dict['bl_prompt']
        self.ts_prompt = serial_port_dict['ts_prompt']
        self.lx_prompt = serial_port_dict['lx_prompt']
        self.conn_times = serial_port_dict['conn_times']
        self.case_dir = serial_port_dict['case_fldr']

        self.logger_sys_obj = logger_obj

        self.reset_cmd = os.path.join(self.case_dir,
                                      'reboot.sh')

        self.csts = None

        # Initialize target.
        self.rebootTarget()

    def connectSerialTS(self):
        'connect target with bootload prompt "###>" by serial port'

        times_I = 1
        while times_I <= self.conn_times:
            try:
                self.csts = serial.Serial(self.com, 
                                          baudrate=self.baudrate,
                                          xonxoff=self.xonxoff, 
                                          timeout=1)
                for et in range(0, self.conn_times):
                    self.csts.write('\n\n')
                    #self.csts.flushInput()
                    ts_output = self.readForBSP(time_out=None, 
                                                kw=self.ts_prompt)
                    if not ts_output:
                        self.logger_sys_obj.warn(
                            LogMsgFormat.setSysLogFmt(
                                '[ConnSerial]', 
                                'Failed to connect target,try it again.'))
                        if et == self.conn_times-1:
                            if times_I == self.conn_times:
                                self.logger_sys_obj.error(
                                    LogMsgFormat.setSysLogFmt(
                                        '[ConnSerial]', 
                                        ('There is no way to connect target,'
                                         'timeout')))

                                RecycleResource(self.logger_sys_obj)
                                sys_exitfunc(-30, self.logger_sys_obj)
                            break
                        time.sleep(1)
                        continue

                    if ListandStrOperate.searchStrFromList(self.ts_prompt, 
                                                           ts_output):
                        self.logger_sys_obj.info(
                            LogMsgFormat.setSysLogFmt(
                                '[ConnSerial]', 
                                'Get testshell serial process successfully'))
                        return True
                    elif \
                    ListandStrOperate.searchStrFromList(self.bl_prompt,
                                                        ts_output) or \
                    ListandStrOperate.searchStrFromList(self.lx_prompt,
                                                        ts_output):
                        message = ('[ConnSerial] -- The prompt is in '
                                   'Bootloader or Linux process')
                        if times_I == self.conn_times:
                            self.logger_sys_obj.warn(message)
                            RecycleResource(self.logger_sys_obj)
                            sys_exitfunc(-36, self.logger_sys_obj)
                        break
                    else:
                        if et == self.conn_times - 1:
                            if times_I == self.conn_times:
                                self.logger_sys_obj.warn(
                                    LogMsgFormat.setSysLogFmt(
                                        '[ConnSerial]',
                                        ('TestShell Prompt is incorrect '
                                         '{%s},try again')) % ts_output)
                                RecycleResource(self.logger_sys_obj)
                                sendNagativeMail(
                                    '''Target system is incorrect '''
                                    '''check it by manual\n''')
                                sys_exitfunc(-32, self.logger_sys_obj)
                            break
                        time.sleep(1)

                times_I = times_I + 1
                self.colseSerialCon()
                self.rebootTarget()
        
            except serial.SerialException ,e:
                self.colseSerialCon()
                self.rebootTarget()
                times_I = times_I + 1

                if times_I == self.conn_times:
                    self.logger_sys_obj.error(
                        LogMsgFormat.setSysLogFmt('[ConnSerial]', e))
                    RecycleResource(self.logger_sys_obj)
                    sys_exitfunc(-34, self.logger_sys_obj)
                continue

    def getSerialPro(self):
        if self.connectSerialTS():
            return self.csts
        else:
            self.logger_sys_obj.error(
                LogMsgFormat.setSysLogFmt(
                    '[ConnSerial]',
                    ('Failed to get correct prompt,check '
                     'target status by manual ')))
            return False

    def rebootTarget(self):
        print 'Target is rebooting ....'
        #return  True
        self.colseSerialCon()
        cmd_args = shlex.split(self.reset_cmd, posix=False)
        cmd_exec =  subprocess.Popen(cmd_args, bufsize=0,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)

        output,strrout= cmd_exec.communicate()
        cmd_exec.wait()
        print output,strrout
        if cmd_exec.returncode != 0 or re.search('No device of interest found',
                                                 output,
                                                 re.I):
            self.logger_sys_obj.error(LogMsgFormat.setSysLogFmt('[rebootTarget]',
                        'Failed to reboot target due to %s,%s' %(output,
                                                                 strrout)))
            sys_exitfunc(-48, self.logger_sys_obj)
        else:
            self.logger_sys_obj.info(LogMsgFormat.setSysLogFmt('[rebootTarget]',
                                'Rebooting target'))
            time.sleep(globalVariable.serial_config['reboot_delay'])

    def colseSerialCon(self):
        'close serial connection of bootloader '
        if isinstance(self.csts, serial.Serial):
            if  self.csts.isOpen():
                self.csts.close()


    def write(self,in_msg):
        self.csts.flushInput()
        self.logger_sys_obj.info(LogMsgFormat.setSysLogFmt('[RWMsgTS]',
                                'Input msg {%s}' %repr(in_msg)))
        if globalVariable.serial_config['target_type'] == 'librasd':
            for unit_char in in_msg:
                self.csts.write(unit_char)
                time.sleep(0.01)
        else:
            self.csts.write(in_msg)
        self.csts.write('\n')

    def readForBSP(self, time_out, kw=''):

        def searchKw(kw_list):
            if type(kw_list) == type([]):
                for kw_unit in kw_list:
                    if re.search(kw_unit, output, re.I):
                        return True
                return False
            else:
                if re.search(kw_list, output, re.I):
                    return True
                else:
                    return False

        tmp_output = []
        if not kw:
            exp_result = self.ts_prompt
        else:
            exp_result = kw
        if time_out:
            tmp_time_out = time_out
        else:
            tmp_time_out = 60
        
        #self.csts.flushOutput()
        start_time = time.time()

        output = self.csts.readline()
        tmp_output.append(output)
        while True:
            if time.time()- start_time <= tmp_time_out:
                output = self.csts.readline()
                if (type(exp_result) == type([])):
                    if searchKw(exp_result):
                        tmp_output.append(output)
                        break
                else:
                    if re.search(exp_result, output, re.I):
                        tmp_output.append(output)
                        break
                    else:
                        tmp_output.append(output)
            elif time.time()- start_time > tmp_time_out:
                self.logger_sys_obj.warn(LogMsgFormat.setSysLogFmt('[readForBSP]',
                                          'Reading Timeout\n'))
                break

        if not tmp_output:
            self.logger_sys_obj.info(
                LogMsgFormat.setSysLogFmt('[RWMsgTS]',
                                          'Got returned msg is empty\n'))
        else:
            self.logger_sys_obj.info(
                LogMsgFormat.setSysLogFmt('[RWMsgTS]',
                    'Got returned msg {%s} from target\n' %
                    repr(tmp_output)))
        return tmp_output

    def rwSerial(self, in_msg, time_out=None, kw=None):
        'read all output lines from target serial connection'
        times_I = 1
        for times_I in range(0,self.conn_times):
            try:
                if not isinstance(self.csts, serial.Serial):
                    self.connectSerialTS()
                elif isinstance(self.csts, serial.Serial):
                    if self.csts.isOpen():
                        pass
                    else:
                        self.connectSerialTS()
                self.write(in_msg)
                if kw:
                    out_msg = self.readForBSP(time_out, kw=kw)
                else:
                    out_msg = self.readForBSP(time_out, self.ts_prompt)
                self.csts.flushOutput()

                if not out_msg:
                    self.colseSerialCon()
                    self.rebootTarget()
                    if times_I == self.conn_times-1:
                        self.logger_sys_obj.error(
                            LogMsgFormat.setSysLogFmt(
                                '[RWMsgTS]',
                                'Failed to read message from target,timeout'))
                        RecycleResource(self.logger_sys_obj)
                        sys_exitfunc(-44, self.logger_sys_obj)
                else:
                    return [msg.strip() for msg in out_msg]

            except serial.SerialException,e:
                self.logger_sys_obj.error(LogMsgFormat.setSysLogFmt('[RWMsgTS]',
                                                                    e))
                self.colseSerialCon()
                RecycleResource(self.logger_sys_obj)
                sys_exitfunc(-42, self.logger_sys_obj)
