# Copyright (C) 2020-2023 Analog Devices, Inc.
#
# SPDX short identifier: ADIBSD

from adi.attribute import attribute
from adi.context_manager import context_manager
from adi.rx_tx import rx
# from typing import List


# class ad7476a(attribute, context_manager):
class ad7476a(rx, context_manager):
    """AD7476a 12-Bit, 1Msps Serial Sampling ADC

    parameters:
        uri: type=string
            URI of IIO context with AD7476a
    """
    _complex_data = False
    _rx_channel_names = ["raw"]
    # _rx_channel_names: List[str] = []
    _device_name = ""

    def __init__(self, uri=""):
        
        context_manager.__init__(self, uri, self._device_name)

        # Find the main and trigger devices
        # self._ctrl = self._ctx.find_device("ad7476a")
        for device in self._ctx.devices:
            if device.name == "ad7476a":
                self._ctrl = device
                self._rxadc = device
                break

        rx.__init__(self)
        # self.rx_buffer_size = 16

        # Raise an exception if the device isn't found
        if not self._ctrl:
            raise Exception("AD7476a device not found")

    @property
    def lsb_mv(self):
        """ Get the LSB in millivolts """
        return self._get_iio_attr("voltage0", "scale", False, self._ctrl)

    @property
    def voltage(self):
        """ Get the voltage reading from the ADC """
        code = self._get_iio_attr("voltage0", "raw", False, self._ctrl)
        return code * self.lsb_mv / 1000
    
    @property
    def raw(self):
        """AD7606 channel raw value"""
        return self._get_iio_attr(self.name, "raw", False)

if __name__ == "__main__":
    import ad7476
    rate = 1000
    samples = 100
    ad_channel = 0 
    ADC = ad7476.ad7476a("ip:analog.local")
    ADC.rx_buffer_size = samples
    ADC.rx_enabled_channels = [ad_channel]
    data = ADC.rx()
    print(ADC.voltage)
    print(data)
