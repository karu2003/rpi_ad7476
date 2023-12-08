# Copyright (C) 2020-2023 Analog Devices, Inc.
#
# SPDX short identifier: ADIBSD

from adi.attribute import attribute
from adi.context_manager import context_manager


class ad7476a(attribute, context_manager):
    """AD7476a 12-Bit, 1Msps Serial Sampling ADC

    parameters:
        uri: type=string
            URI of IIO context with AD7476a
    """

    _device_name = ""

    def __init__(self, uri=""):
        context_manager.__init__(self, uri, self._device_name)

        # Find the main and trigger devices
        self._ctrl = self._ctx.find_device("ad7476")

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

if __name__ == "__main__":
    import ad7476
    ADC = ad7476.ad7476a(uri="ip:analog")

    raw = ADC.raw

    print(raw)
