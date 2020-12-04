#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/python3 -u
from tango import AttrWriteType, DevState, DispLevel, DevVarLongArray
from tango.server import Device, attribute, command, device_property
from time import sleep
from zaber_motion.binary import Connection, CommandCode

class ZaberTMMCtrl(Device):
    """ZaberTMMCtrl"""
    
    Port = device_property(dtype='str', default_value='/dev/ttyUSB0')
    Device = device_property(dtype='int', default_value='0')
   
    # States with reply
    __REPLAY_STATES = (8, 9, 10, 11, 12, 13, 17, 50, 51, 52, 53, 54, 60, 63)   
    # wait time for reading serial after write
    __cmd_wait_sec = 0.05

    def init_device(self):
        Device.init_device(self)
        self.info_stream('Connecting to serial port {:s} ...'.format(self.Port))
        try:
            self.con = Connection.open_serial_port(self.Port, 9600)
            self.info_stream('Connection established.')
            devices = self.con.detect_devices()
            self.info_stream('Found {:d} devices:'.format(len(devices)))
            for i, device in enumerate(devices):
                self.info_stream('{:d}: Name {:s} - ID {:d} - Serial {:d}'.format(i+1,
                                                                                  device.name,
                                                                                  device.device_id,
                                                                                  device.serial_number))
            self.set_state(DevState.ON)
        except:
            self.error_stream('Cannot connect!')
            self.set_state(DevState.OFF)

    def delete_device(self):
        self.info_stream('Connection closed for port {:s}'.format(self.Port))
        self.con.close()

    @command(dtype_in=DevVarLongArray, dtype_out=int)
    def query(self, binary_command):        
        axis = int(binary_command[0])
        cmd_code = int(binary_command[1])
        data = int(binary_command[2])

        cmd = CommandCode(cmd_code)

        if (cmd_code in self.__REPLAY_STATES):            
            self.debug_stream('query: {:d} {:d} {:d}'.format(axis, cmd_code, data))
            res = self.con.generic_command(axis, cmd, data)
            return int(res.data)
        else:
            self.debug_stream('sendcmd: {:d} {:d} {:d}'.format(axis, cmd_code, data))
            self.con.generic_command_no_response(axis, cmd, data)
            return 0

# start the server
if __name__ == '__main__':
    ZaberTMMCtrl.run_server()