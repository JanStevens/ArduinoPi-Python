__author__ = 'Fritz'
__name__ = 'ArduinoPi'

import serial
import pprint
#Not really const but lets not change them!
HIGH = 255
LOW = 0
MEGA2560 = 100
UNO = 101
LEONARDO = 102
ADK = 103
SER = serial.Serial('/dev/ttyAMA0', 115200)
# Close the SER connection, so everything else works
SER.close()


class ArPiException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ArduinoPi:
    __arduino = None
    __arName = None

    def __init__(self, device):
        self.__setDevice(device)

    def __isBetween(self, num, range):
        if(len(range) == 2):
            if(num >= range[0] and num <= range[1]): return True
            return False
        elif(num in range): return True

        else:
            return False

    def __convertToGlobal(self, string):
        if(isinstance(string, unicode)):
            if(string.lower() == "high"): return HIGH
            if(string.lower() == "low"): return LOW
            return int(string)
        return string

    def __setDevice(self, name):
        """
        Sets the device name
        Analog pins also can be used as digital pins, pwm can also be digital pins
        @param name: The name of the device
        @return: bool
        @raise: ArPiException
        """
        #Python has no native switch command, if-elsing it
        if(name == MEGA2560):
            PWM = [0, 13]
            DIGITAL = [0, 69]
            ANALOG = [0, 15]
        elif(name == UNO):
            PWM = [3, 5, 6, 9, 10, 11]
            DIGITAL = [0, 20]
            ANALOG = [0, 5]
        elif(name == LEONARDO):
            PWM = [3, 5, 6, 9, 10, 11, 13]
            DIGITAL = [0, 20]
            ANALOG = [4, 6, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19]
        elif(name == ADK):
            PWM = [0, 13]
            DIGITAL = [0, 69]
            ANALOG = [0, 15]
        else:
            raise ArPiException("Your device is not compatible with the ArduinoPi")

        self.__arduino = {'PWM' : PWM, 'DIGITAL' : DIGITAL, 'ANALOG' : ANALOG }
        self.__arName = name
        return True

    def writePWM(self, port, value):
        """
        Wirtes a PWM value to a specific port using the command interface
        @cmd: @<port>,<value>:
        @param port: The value of the port
        @param value: The PWM value
        @return: bool
        @raise: ArPiException
        """
        if(self.__isBetween(port, self.__arduino["PWM"])):
            if(self.__isBetween(value, [0, 255])):
                cmd = "@" + str(port) + "," + str(value) + ":"
                SER.open()
                if(SER.isOpen()):
                    SER.write(str(cmd))
                    SER.close()
                    return True
                else:
                    raise ArPiException("Coudn't open the device")
            else:
                raise ArPiException("writePWM: Wrong value, it must be between 0-255")
        else:
            raise ArPiException("writePWM: Wrong port value")


    def writeDigital(self, port, value):
        """
        Writes to a specific digital port, if PWM ports are needed use the other function!
        @cmd: @<port>,<value>:
        @param port: The port value
        @param value: The value, HIGH or LOW
        @return: bool
        @raise: ArPiException
        """
        if(self.__isBetween(port, self.__arduino["DIGITAL"])):
            if(value == HIGH or value == LOW):
                cmd = "@" + str(port) + "," + str(value) + ":"
                SER.open()
                if(SER.isOpen()):
                    SER.write(str(cmd))
                    SER.close()
                    return True
                else:
                    raise ArPiException("writeDigital: Coudn't open the device")
            else:
                raise ArPiException("writeDigital: Wrong Value must be high, low, 0 or 255")
        else:
            raise ArPiException("writeDigital: Wrong port value")

    def readAnalog(self, port):
        """
        Reads an analog port.
        @cmd: @102,<port>:
        @param port: The port value
        @return val: The analog value
        @raise: ArPiException
        """
        if(self.__isBetween(port, self.__arduino["ANALOG"])):
            cmd = "@102," + str(port) + ":"
            SER.open()
            if(SER.isOpen()):
                SER.setTimeout(10)
                SER.write(str(cmd))
                val = int(SER.readline())
                SER.close()
                return val
            else:
                raise ArPiException("readAnalog: Coudn't open the device")
        else:
            raise ArPiException("readAnalog: Wrong value for the port")


    def writeMultiplePWM(self, port, value):
        """
        Write multiple ports pwm at the same time (no serial transfer delay)
        @cmd @101,<#port>,<port1>,<value1>,<port2>,<value2>,...:

        @param port: The port values in an array
        @param value: The value can be a array
        @return: bool
        @raise: ArPiException
        """
        if(isinstance(port, list) and isinstance(value, list) and (len(port) == len(value))):
            cmd = "@101," + str(len(port))
            for i in range(len(port)):
                if(self.__isBetween(port[i], self.__arduino["PWM"]) and self.__isBetween(value[i], [0, 255])):
                    cmd += "," + str(port[i]) + "," + str(value[i])
            cmd += ":"
            SER.open()
            if(SER.isOpen()):
                SER.write(str(cmd))
                SER.close()
                return True
            else:
                raise ArPiException("writeMultiplePWM: Coudn't open the device")
        else:
            raise ArPiException("Wrong combination of port and value (should be array)")

    def writeMultipleDigital(self, port, value):
        """
        Write multiple ports digital at the same time (no serial transfer delay)
        @cmd @101,<#port>,<port1>,<value1>,<port2>,<value2>,...:

        @param port: The port values in an array
        @param value: The value can be a array
        @return: bool
        @raise: ArPiException
        """
        if(isinstance(port, list) and isinstance(value, list) and (len(port) == len(value))):
            cmd = "@101," + str(len(port))
            for i in range(len(port)):
                if(self.__isBetween(port[i], self.__arduino["DIGITAL"]) and (value[i] == HIGH or value[i] == LOW)):
                    cmd += "," + str(port[i]) + "," + str(value[i])

            cmd += ":"
            SER.open()
            if(SER.isOpen()):
                SER.write(str(cmd))
                SER.close()
                return True
            else:
                raise ArPiException("writeMultipleDigital: Coudn't open the device")
        else:
            raise ArPiException("Wrong combination of port and value (should be array)")


    def process(self, mode, data):
        if(mode == "pwm"):
            if(len(data) < 2):
                raise ArPiException("pwm: no value specified")
            self.writePWM(int(data[0]), self.__convertToGlobal(data[1]))
        elif(mode == "digital"):
            if(len(data) < 2):
                raise ArPiException("digital: no value specified")
            self.writeDigital(int(data[0]), self.__convertToGlobal(data[1]))
        elif(mode == "multiple-pwm"):
            ports = list()
            values = list()
            for i in xrange(0, len(data), 2):
                ports.append(int(data[i]))
                values.append(self.__convertToGlobal(data[i+1]))
            self.writeMultiplePWM(ports, values)
        elif(mode == "multiple-digital"):
            ports = list()
            values = list()
            for i in xrange(0, len(data), 2):
                ports.append(int(data[i]))
                values.append(self.__convertToGlobal(data[i+1]))
            self.writeMultipleDigital(ports, values)
        elif(mode == "analog"):
            val = self.readAnalog(int(data[0]))
            return val

        else:
            raise ArPiException("Something is wrong with your mode")




