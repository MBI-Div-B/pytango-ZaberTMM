# -*- coding: utf-8 -*-
#
# This file is part of the ZaberTMM project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ZaberTMMController

"""

__all__ = ["ZaberTMM", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt, DeviceProxy
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import class_property, device_property
from PyTango import AttrQuality, AttrWriteType, DispLevel, DevState
# Additional import
# PROTECTED REGION ID(Zaber.additionnal_import) ENABLED START #
from time import sleep
from zaber.serial import BinarySerial, BinaryCommand, BinaryReply
# PROTECTED REGION END #    //  ZaberTMM.additionnal_import

flagDebugIO = 1

class ZaberTMM(Device, metaclass=DeviceMeta):
    """
    """
    #__metaclass__ = DeviceMeta
    # PROTECTED REGION ID(ZaberTMM.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  ZaberTMM.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------
    # name of serial port ('com1' .. (Windows) or '/dev/ttyUSB0' .. (Linux)) 
    
    Port = device_property(
        dtype='str', default_value="com11"
    )
    
    
# some Constants
    __baud      = 9600
    __dev_num   = 1
    
# time to wait after sending a command.
    __cmd_wait_sec = 0.05
    
# Errors codes
    __cannot_home       = 1
    __abs_pos_invalid   = 20    # Move Absolute - Target position out of range.
    __busy              = 255
        
# States from page 27 of the manual
    __idle  = 0     # not currently executing any instructions
    
# Commands
    __dev_mode  = 40    # set device mode
    __dev_cmd   = 3     # change setting of devices, because they are non-volatile
                        # disable auto-reply 1*2^0 = 1
                        # enable backlash correction 1*2^1 = 2
    __dev_state = 54    # read device state
    __dev_fw    = 51    # read firmware version
    __dev_stop  = 23    # stop moving
    __dev_pos   = 60    # read pos
    __dev_mov_abs = 20  # move absolute
    __dev_home  = 1     # homing  
    
# States 
 
    __REPLAY_STATES = (8,9,10,11,12,13,17,50,51,52,53,54,60,63)   
    
# some private variables
    __con      = None
    __port     = ''
    
    __fw             = '' # Firmware version
    
# private status variables, are are updated by "get_state()"
    __Motor_Run   = False
    __Homing      = False
    __Out_Of_Range= False
    __Pos         = 0
    __Idle        = False        
    
    # ----------
    # Attributes
    # ----------

    homing = attribute(
        dtype='bool',
        doc = 'if motor homed this flag is true'
    )
    
    moving = attribute(
        dtype='bool',
        doc = 'if motor in moving this flag is true'
    )
    position = attribute(
        min_value = 0,
        max_value = 16777215,
        format='%8d',
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        unit="steps",
        display_unit="step",
        doc = 'absolute position'
    )
    
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(ZaberTMM.init_device) ENABLED START #
        self.proxy = DeviceProxy(self.get_name())
        
        # read name of serial port
        self.__port  = self.Port
        
        if flagDebugIO:
            print("Get_name: %s" % (self.get_name()))
            print("Connecting to ZaberTMM on %s" %(self.__port))
        
        self.__con = BinarySerial(self.__port, self.__baud)
        # set device mode
        self.write_read(self.__dev_mode, self.__dev_cmd)
        
        if (self.read_controller_info() != ''):
            print('Zaber TMM self.controller Initialization ...')
            print('SUCCESS on port {}'.format(self.__port))
            print('Firmware Version: {}'.format( self.__fw))
            self.get_state()
            self.read_position()
            self.set_state(PyTango.DevState.ON)  
        else:
            self.set_state(PyTango.DevState.OFF)
        # PROTECTED REGION END #    //  ZaberTMM.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(ZaberTMM.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  ZaberTMM.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(ZaberTMM.delete_device) ENABLED START #
        self.__con.close()
        # PROTECTED REGION END #    //  ZaberTMM.delete_device

    def get_position(self):
        # PROTECTED REGION ID(ZaberTMM.get_position) ENABLED START #
        self.__Pos = self.write_read(self.__dev_pos)
        # PROTECTED REGION END #    //  ZaberTMM.get_position
        
    def write_read(self, cmd_number, data = None):
    # PROTECTED REGION ID(ZaberTMM.write_read) ENABLED START #
        if (data is None):
            cmd = BinaryCommand(self.__dev_num, cmd_number)
        else:
            cmd = BinaryCommand(self.__dev_num, cmd_number, int(data))
        
        self.__con.write(cmd)
             
        # Command with responce ?
        if (cmd_number in self.__REPLAY_STATES):
            sleep(self.__cmd_wait_sec)
            reply = self.__con.read()
            while reply.command_number == 255: # 255 is the binary error response code.
                self.__con.write(cmd)
                reply = self.__con.read()
                sleep(self.__cmd_wait_sec)
            return (int(reply.data))
        # PROTECTED REGION END #    //  ZaberTMM.write_read
        
        
    # ------------------
    # Attributes methods
    # ------------------

    def read_homing(self):
        # PROTECTED REGION ID(ZaberTMM.moving_read) ENABLED START #
        return (self.__Homing)
        # PROTECTED REGION END #    //  ZaberTMM.moving_read
        
    def read_moving(self):
        # PROTECTED REGION ID(ZaberTMM.moving_read) ENABLED START #
        return (self.__Motor_Run)
        # PROTECTED REGION END #    //  ZaberTMM.moving_read

    def read_position(self):
        # PROTECTED REGION ID(ZaberTMM.position_read) ENABLED START #
        return self.__Pos
        # PROTECTED REGION END #    //  ZaberTMM.position_read

    def write_position(self, value):
        # PROTECTED REGION ID(ZaberTMM.position_write) ENABLED START #
        self.write_read(self.__dev_mov_abs, value)
        # PROTECTED REGION END #    //  ZaberTMM.position_write

    # --------
    # Commands
    # --------
    @command (polling_period= 200) 
    @DebugIt()
    def get_state(self):
        # PROTECTED REGION ID(TaberTMM.get_state) ENABLED START #
        # read position
        self.get_position()
        # read state
        reply = self.write_read(self.__dev_state)
        if reply == self.__idle:
            self.__Motor_Run = False
        elif (reply >= 1) & (reply <=23):
            self.__Motor_Run = True
        else:
            self. PyTango.DevState.FAULT                  
        # PROTECTED REGION END #    //  TaberTMM.get_state
        
        
    # read version of firmware
    @command(dtype_out=str)
    @DebugIt()
    def read_controller_info(self):
        # read firmware version
        reply = self.write_read(self.__dev_fw)
        # print ('rd  ctrl info:  {}'.format(reply))
        self.__fw = (str(reply))
        self.__fw =  self.__fw[:1] + '.' +  self.__fw[1:]
        return (self.__fw)
   
    # Moves to the home position and resets the device's internal position.
    @command
    @DebugIt()
    def go_home(self):
        # PROTECTED REGION ID(TaberTMM.go_home) ENABLED START #    
        self.write_read(self.__dev_home)
        self.__Homing = True
        # PROTECTED REGION END #    //  TaberTMM.go_home
    
    # Stops the device from moving by preempting any move instruction
    @command
    @DebugIt()
    def stop(self):
        # PROTECTED REGION ID(TaberTMM.stop) ENABLED START #         
        self.write_read(self.__dev_stop)
        # PROTECTED REGION END #    //  TaberTMM.stop
    

    

    
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(ZaberTMM.main) ENABLED START #
    from PyTango.server import run
    return run((ZaberTMM,), args=args, **kwargs)
    # PROTECTED REGION END #    //  ZaberTMM.main

if __name__ == '__main__':
    main()
