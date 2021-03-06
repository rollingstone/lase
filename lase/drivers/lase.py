#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..core import DevMem, Gpio, Xadc, Dac
import numpy as np
from ..signal import Sampling

class Lase(object):
    """
    This class is used as a base class for `Oscillo` and `Spectrum`
    
    args:
        n (int): number of points in the waveform (ex: n = 8192).
        client : instance of KClient class, used to connect to the board.        
    """    
    
    def __init__(self, n, client, map_size=4096, current_mode='pwm'):
         
        self.client = client
        
        # Start core devices 
        self.dvm = DevMem(self.client)
        self._gpio = Gpio(self.client)
        self._xadc = Xadc(self.client)
        self._dac = Dac(self.client, n)
        
        self.n = n # Number of points in the waveform 'ex : n = 8192'
        self.current_mode = current_mode
        self.max_current = 50 # mA

        # \address
        self._const_ip_addr = int('0x43C00000',0)
        #self._dac_addr = int('0x44000000',0)
        # \end

        # \offset
        self._leds_off = 0
        self._pwm_off = 4
        self._trig_start_off = 8
        self._trig_acq_off = 12
        self._bitstream_id_off = 36
        self._n_avg_off = 40
        # \end

        self.sampling = Sampling(n, 125e6)

        # Add memory maps
        self._const_ip = self.dvm.add_memory_map(self._const_ip_addr, 16 * map_size)
        #self._dac      = self.dvm.add_memory_map(self._dac_addr, self.n/1024*map_size)

        self.opened = True

        self.dac = np.zeros((2,self.sampling.n))
        self.get_bitstream_id()

        self.laser_power_channel = 1
        self.laser_current_channel = 8

    def update(self):
        pass # Used in LaseSimu

    def close(self):
        self.reset()
        del self.dvm.client

    def reset(self):
        self._gpio.set_as_output(7, channel=2) # Should be in the initialization
        self._xadc.set_channel(channel_0 = self.laser_power_channel,
                               channel_1 = self.laser_current_channel)
        self._xadc.set_averaging(n_avg = 256)
        self.dvm.write(self._const_ip,self._trig_start_off,0)
        self.dvm.write(self._const_ip,self._trig_acq_off,0)
        self.dvm.write(self._const_ip,self._trig_start_off,1)
        self.stop_laser()
        self.set_laser_current(0)

    def stop_laser(self):
        """
        Stop laser emission
        """
        # Laser enable pin on DIO7_P
        self._gpio.set_bit(7, channel=2)

    def get_laser_current(self):
        return self._xadc.read(self.laser_current_channel)

    def get_laser_power(self):
        return self._xadc.read(self.laser_power_channel)

    def start_laser(self):
        """
        Start laser emission
        """
        # Laser enable pin on DIO7_P
        self._gpio.clear_bit(7, channel = 2)

    def set_laser_current(self, current):
        """
        Set the current bias of the laser diode

        Args:
            - current: The bias in mA
        """
        current = min([current, self.max_current])
        if (self.current_mode=='pwm'):
            voltage = 1.8 / (2.5*100) * current
            self.dvm.write(self._const_ip,self._pwm_off, np.floor(voltage/1.8 * 4096))
        elif (self.current_mode=='dac'):
	        value = np.floor(0.01 * current * 8192)
	        if (0<value<4096):
	            self.dvm.write(self._const_ip,self.dac_off, value)

    def set_dac(self, warning=False, reset=False):
        if warning:
            if np.max(np.abs(self.dac)) >= 1:
                print 'WARNING : dac out of bounds'
        self._dac.set_dac(self.dac[0,:], self.dac[1,:])
        if reset:
            self.reset_acquisition()

    def get_bitstream_id(self):
        self.bitstream_id = self.dvm.read(self._const_ip, self._bitstream_id_off)


    def set_led(self, ip):
        self.dvm.write(self._const_ip, self._leds_off, ip)

    def reset_acquisition(self):
        self.dvm.write(self._const_ip,self._trig_acq_off,1)
        self.dvm.write(self._const_ip,self._trig_acq_off,0)
        
