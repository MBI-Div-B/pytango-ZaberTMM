#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/python3 -u
from tango import AttrWriteType, DevState, DispLevel, DeviceProxy
from tango.server import Device, attribute, command, device_property
from zaber_motion.binary import CommandCode

class ZaberTMMAxis(Device):
    """ZaberTMMAxis"""
    
    CtrlDevice = device_property(dtype='str', default_value='domain/family/member')
    Axis = device_property(dtype='int16', default_value=1)
    Mode = device_property(dtype='int', default_value=3)

    position = attribute(
        format='%8d',
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        unit='steps',
        label = 'Position'
    )
    
    def init_device(self):
        Device.init_device(self)
        self.info_stream('Connecting to controller device ...')

        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream('Connected to controller device: {:s}'.format(self.CtrlDevice))
        except DevFailed as df:
            self.error_stream('Failed to create proxy to {:s}!'.format(df))
            sys.exit(255)

        if self.Axis == 0:
            self.error_stream('Axis must be larger than 0!')
            sys.exit(255)

        self.info_stream('Axis set to: {:d}'.format(self.Axis))
        self.info_stream('Mode set to: {:d}'.format(self.Mode))
        self.query(CommandCode.SET_DEVICE_MODE, self.Mode)
            
    def always_executed_hook(self):
        res = self.query(CommandCode.RETURN_STATUS)
        if res == 0:
            self.set_state(DevState.ON)
            self.set_status('Device is ON')
        elif res == 1:
            self.set_state(DevState.MOVING)
            self.set_status('Device is HOMING')
        elif (res > 1) & (res <=23):
            self.set_state(DevState.MOVING)
            self.set_status('Device is MOVING')
        else:
            self. PyTango.DevState.OFF
            self.set_status('Device is OFF') 

    def query(self, cmd_code, data=0):
        return self.ctrl.query([self.Axis, cmd_code.value, data])

    def read_position(self):
        return float(self.query(CommandCode.RETURN_CURRENT_POSITION))
    
    def write_position(self, value):
        self.set_state(DevState.MOVING)
        self.set_status('Device is MOVING')
        self.query(CommandCode.MOVE_ABSOLUTE, int(value))

    @command
    def Reset(self):
        self.set_state(DevState.OFF)
        self.set_status('Device is OFF')  
        self.query(CommandCode.RESET)

    @command
    def Homing(self):
        self.set_state(DevState.MOVING)
        self.set_status('Device is HOMING')  
        self.query(CommandCode.HOME)
    
    @command
    def Stop(self):    
        self.query(CommandCode.STOP)

# start the server
if __name__ == '__main__':
    ZaberTMMAxis.run_server()