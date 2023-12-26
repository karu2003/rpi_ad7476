from adi.attribute import attribute
from adi.context_manager import context_manager
from adi.rx_tx import rx
import numpy as np

from pyfdt.pyfdt import *
import re

import ad7476_helper
from hrtimer import hrtimer as hrt


class ad7476a(rx, context_manager):
    """AD7476a 12-Bit, 1Msps Serial Sampling ADC

    parameters:
        uri: type=string
            URI of IIO context with AD7476a
    """

    _complex_data = False
    _rx_channel_names = ["voltage0"]
    _rx_data_si_type = float
    _device_name = ""

    def __init__(self, uri="", device_name="", trigger=""):
        self.max_sample_rate = 0
        self.spi_max_frequency = 0
        self.hrtimer = None

        if trigger != "":
            self.spi_max_frequency, self.max_sample_rate = self.spi_max_f()

            if ad7476_helper.chips[device_name] < self.spi_max_frequency:
                raise Exception(
                    f"{device_name} does not support SPI frequency higher than {ad7476_helper.chips[device_name]}."
                )
            self.hrtimer = hrt(trigger)

        context_manager.__init__(self, uri, self._device_name)

        self._ctrl = None

        if device_name not in ad7476_helper.chips.keys():
            raise Exception(f"Not a compatible device: {device_name}")

        # Find the main and trigger devices
        self._ctrl = self._ctx.find_device(device_name)
        self._rxadc = self._ctx.find_device(device_name)

        if not self._ctrl:
            raise Exception(f"Cannot find IIO device {device_name}")

        if not self._rxadc:
            raise Exception(f"Cannot find IIO device {device_name}")

        rx.__init__(self)

    def spi_max_f(self):
        """find maximum SPI frequency in Devicetree"""

        Devicetree = "/sys/firmware/devicetree/base"
        pat = re.compile(r".*ad7476.*spi-max-frequency")
        pat_value = re.compile(r"[0-9a-fA-F]{8}")

        fdt = FdtFsParse(Devicetree)

        for path, node in fdt.resolve_path("/").walk():
            if pat.match(path):
                spi_f = float.fromhex("".join(
                    pat_value.findall(node.dts_represent())))
                max_sr = spi_f / 16.0
        return spi_f, max_sr

    @property
    def lsb_mv(self):
        """Get the LSB in millivolts"""
        return self._get_iio_attr("voltage0", "scale", False, self._ctrl)

    @property
    def voltage(self):
        """Get the voltage reading from the ADC"""
        code = self._get_iio_attr("voltage0", "raw", False, self._ctrl)
        return code * self.lsb_mv / 1000

    @property
    def raw(self):
        """AD7476 channel raw value"""
        return self._get_iio_attr("voltage0", "raw", False)

    def to_volts(self, index, val):
        """Converts raw value to SI"""
        _scale = self.channel[index].scale

        ret = None

        if isinstance(val, np.int16):
            ret = val * _scale

        if isinstance(val, np.ndarray):
            ret = [x * _scale for x in val]

        if ret is None:
            raise Exception("Error in converting to actual voltage")

        return ret


if __name__ == "__main__":
    import ad7476    
    data = []
    target_device = "ad7476a"
    ADC = ad7476.ad7476a("local:", target_device)
    for k in range(10):
        data.append(ADC.voltage)
    print(data)
