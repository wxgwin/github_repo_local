import serial
import time


def connectSerial():
    try:
        ser_ins = serial.Serial('/dev/ttyS0', 
                                baudrate=2400,
                                stopbits=1,
                                xonxoff=0, 
                                timeout=0.5)
        def resetStarus():
            for char in 'AAAAaaaa':
                ser_ins.write(char)
                output = ser_ins.read(4)
                #print output,'reset'
                if output == 'QANG':
                    
                    return True
                    
        def sendChar():
            for char in 'QA42':
                ser_ins.write(char)
                output = ser_ins.read(4)
                #print output,'sendchar'
                if output == 'QAOK':
                    return True
                elif output == 'QANG':
                    return False

        ser_ins.flushInput()
        if sendChar():
            ser_ins.close()
            print 'Reset port 1 is successful'
            return True
        else:
            resetStarus()
            if not sendChar():
                ser_ins.close()
                print 'Reset port 1 is failed'
                return False
            else:
                ser_ins.close()
                print 'Reset port 1 is successful'
                return True
    except Exception, e:
        def isset(v):  
            try:  
                type (eval(v))  
            except:  
                return 0  
            else:  
                return 1  

        if isset('ser_ins') and isinstance(ser_ins, serial.Serial):
            ser_ins.close()
            
        print 'EXCEPT Reset port 1 is failed'
        time.sleep(2)
        return False




def main():
    #print connectSerial()

    while True:
        if connectSerial():
            break
        else:
            pass
            #time.sleep(2)
    print 'Reset finished'

if __name__ == '__main__':
    
    main()
