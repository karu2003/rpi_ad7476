from adi.attribute import attribute
from adi.context_manager import context_manager
from adi.rx_tx import rx
import iio
import numpy as np
import os
from pyfdt.pyfdt import *
import re
import ad7476_helper
import struct
import time


class ad7476a(rx, context_manager):
    """AD7476a 12-Bit, 1Msps Serial Sampling ADC

    parameters:
        uri: type=string
            URI of IIO context with AD7476a
    """
    _complex_data = False
    # _rx_channel_names = ["voltage0"]
    channel = []
    _rx_data_si_type = float
    _device_name = ""

    def __init__(self, uri="", device_name="", trigger=""):

        self.max_sample_rate = 0
        self.spi_max_frequency = 0
        self.trigger = trigger
        self.tri = None
        hrtimer_dir = "/sys/kernel/config/iio/triggers/hrtimer/"
        iio_dir = "/sys/bus/iio/devices/iio:device0/"
        self.trigger_dir = "/sys/bus/iio/devices/trigger0/sampling_frequency"
        self.current_trigger = "/sys/bus/iio/devices/iio:device0/trigger/current_trigger"
        directory = hrtimer_dir + self.trigger
        pat = re.compile(r".*ad7476.*spi-max-frequency")
        pat_value = re.compile(r"[0-9a-fA-F]{8}")

        fdt = FdtFsParse("/sys/firmware/devicetree/base")

        for (path, node) in fdt.resolve_path('/').walk():
            if pat.match(path):
                self.spi_max_frequency = float.fromhex(''.join(
                    pat_value.findall(node.dts_represent())))
                self.max_sample_rate = self.spi_max_frequency / 16.0

        if os.stat(hrtimer_dir).st_gid not in os.getgroups():
            raise Exception(f"You do not have permission to create a trigger")

        if os.stat(iio_dir).st_gid not in os.getgroups():
            raise Exception(f"You do not have permission to IIO")

        if trigger != "":
            os.makedirs(directory, exist_ok=True)

        context_manager.__init__(self, uri, self._device_name)

        self._ctrl = None

        if device_name not in ad7476_helper.chips.keys():
            raise Exception(f"Not a compatible device: {device_name}")

        if ad7476_helper.chips[device_name] < self.spi_max_frequency:
            raise Exception(
                f"{device_name} does not support SPI frequency higher than {ad7476_helper.chips[device_name]}."
            )

        # Find the main and trigger devices
        self._ctrl = self._ctx.find_device(device_name)
        self._rxadc = self._ctx.find_device(device_name)

        if not self._ctrl:
            raise Exception(f"Cannot find IIO device {device_name}")

        if not self._rxadc:
            raise Exception(f"Cannot find IIO device {device_name}")

        os.system("echo " + self.trigger + " > " + self.current_trigger)

        for ch in self._ctrl.channels:
            name = ch._id
            self._rx_channel_names.append(name)
            self.channel.append(self._channel(self._ctrl, name))

        rx.__init__(self)

        for k in range(10):
            os.access(self.trigger_dir, os.W_OK)
            time.sleep(0.1)

    class _channel(attribute):
        """ AD7476 channel """

        def __init__(self, ctrl, channel_name):
            self.name = channel_name
            self._ctrl = ctrl

        @property
        def raw(self):
            """AD7476 channel raw value"""
            return self._get_iio_attr(self.name, "raw", False)

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
    def sample_rate(self):
        """Sets sampling frequency of the AD7476 use hrtimer"""
        return float(os.read(os.open(self.trigger_dir, os.O_RDWR), 16))

    @sample_rate.setter
    def sample_rate(self, value):
        if value > self.max_sample_rate:
            os.write(os.open(self.trigger_dir, os.O_RDWR), str(self.max_sample_rate).encode())
        else:    
            os.write(os.open(self.trigger_dir, os.O_RDWR), str(value).encode())

    # @property
    # def raw(self):
    #     """AD7476 channel raw value"""
    #     return self._get_iio_attr("voltage0", "raw", False)

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
    target_device = "ad7476a"
    samples = 100
    ad_channel = 1
    ADC = ad7476.ad7476a("local:", target_device, "trigger0")
    ADC._rx_data_type = np.int32
    # ADC._ctx.set_timeout(10000)
    # ADC._rx_data_type = np.int16
    ADC.rx_output_type = "SI"
    ADC.rx_enabled_channels = [ad_channel]
    ADC.rx_buffer_size = samples
    # print(ADC.channel[ad_channel].raw)
    print(ADC.sample_rate)
    ADC.sample_rate = 1000000.0
    data = ADC.rx()
    print(data)
    # print(ADC.voltage)
