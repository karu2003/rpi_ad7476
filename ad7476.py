from adi.attribute import attribute
from adi.context_manager import context_manager
from adi.rx_tx import rx
import iio



# class ad7476a(attribute, context_manager):
class ad7476a(rx, context_manager):
    """AD7476a 12-Bit, 1Msps Serial Sampling ADC

    parameters:
        uri: type=string
            URI of IIO context with AD7476a
    """
    _complex_data = False
    channel = []
    _rx_data_si_type = float
    _device_name = ""

    def __init__(self, uri="", device_name=""):
        
        context_manager.__init__(self, uri, self._device_name)

        compatible_parts = ["ad7476", "ad7476a"]

        self._ctrl = None

        if not device_name:
            device_name = compatible_parts[0]
        else:
            if device_name not in compatible_parts:
                raise Exception(f"Not a compatible device: {device_name}")

        # Find the main and trigger devices
        self._ctrl = self._ctx.find_device(device_name)
        self._rxadc = self._ctx.find_device(device_name)
 
        if not self._ctrl:
            raise Exception(f"Cannot find IIO device {device_name}")

        if not self._rxadc:
            raise Exception(f"Cannot find IIO device {device_name}")

        for ch in self._ctrl.channels:
            name = ch._id
            self._rx_channel_names.append(name)
            self.channel.append(self._channel(self._ctrl, name))

        rx.__init__(self)

        print(self._rx_channel_names)
        print(self.channel)

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
    
    # @property
    # def raw(self):
    #     """AD7476 channel raw value"""
    #     return self._get_iio_attr(self.name, "raw", False)

if __name__ == "__main__":
    import ad7476
    ctx = iio.Context()
    target_device = "ad7476a"
    samples = 100
    ad_channel = 1 
    ADC = ad7476.ad7476a("ip:analog.local",target_device)
    ADC.rx_enabled_channels = [ad_channel]
    ADC.rx_buffer_size = samples
    data = ADC.rx()
    # dev = ctx.find_device(target_device)
    # buf = iio.Buffer(dev, samples)
    # print(ADC.voltage)
    # print(buf)