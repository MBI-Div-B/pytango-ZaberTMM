#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/python3 -u
from tango import AttrWriteType, DevState, DispLevel, DevVarLongArray
from tango.server import Device, attribute, command, device_property
from time import sleep
from zaber.serial import BinarySerial, BinaryCommand

class ZaberTMMCtrl(Device):
    """ZaberTMMCtrl"""
    
    Port = device_property(dtype='str', default_value="/dev/ttyUSB0")
   
    # States with reply
    __REPLAY_STATES = (8, 9, 10, 11, 12, 13, 17, 50, 51, 52, 53, 54, 60, 63)   
    # wait time for reading serial after write
    __cmd_wait_sec = 0.05

    def init_device(self):
        Device.init_device(self)
        self.info_stream('Connecting to serial port {:s} ...'.format(self.Port))
        try:
            self.serial = BinarySerial(self.Port, 9600)
            
            self.info_stream('Connection established.')
            self.set_state(DevState.ON)
        except:
            self.error_stream('Cannot connect!')
            self.set_state(DevState.OFF)

    def delete_device(self):
        if self.serial.isOpen():
            self.serial.close()    
            self.info_stream('Connection closed for port {:s}'.format(self.Port))

    @command(dtype_in=DevVarLongArray, dtype_out=int)
    def query(self, binary_command):
        
        axis = binary_command[0]
        cmd_num = binary_command[1]
        data = binary_command[2]
        cmd = BinaryCommand(axis, cmd_num, int(data))
        self.debug_stream('query: {:d} {:d} {:d}'.format(axis, cmd_num, data))

        self.serial.write(cmd)

        # Command with responce ?
        if (cmd_num in self.__REPLAY_STATES):
            sleep(self.__cmd_wait_sec)
            reply = self.serial.read()
            while reply.command_number == 255: # 255 is the binary error response code.
                self.serial.write(cmd)
                reply = self.serial.read()
                sleep(self.__cmd_wait_sec)
            return (int(reply.data))
        else:
            return 0

# start the server
if __name__ == '__main__':
    ZaberTMMCtrl.run_server()