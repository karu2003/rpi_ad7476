import os
import time


class hrtimer():
    """hrtimer initialization
    parameters:
        trigger: type=string
    """

    def __init__(self, trigger=""):

        self.trigger = trigger
        hrtimer_dir = "/sys/kernel/config/iio/triggers/hrtimer/"
        iio_dir = "/sys/bus/iio/devices/iio:device0/"
        self.trigger_dir = "/sys/bus/iio/devices/trigger0/sampling_frequency"
        self.current_trigger = "/sys/bus/iio/devices/iio:device0/trigger/current_trigger"
        directory = hrtimer_dir + self.trigger

        if not self.trigger:
            raise Exception(f"You did not specify a timer name")

        if os.stat(hrtimer_dir).st_gid not in os.getgroups():
            raise Exception(f"You do not have permission to create a trigger")

        if os.stat(iio_dir).st_gid not in os.getgroups():
            raise Exception(f"You do not have permission to IIO")

        os.makedirs(directory, exist_ok=True)

        for k in range(10):
            if not (os.access(self.trigger_dir, os.W_OK)):
                print(".")
                time.sleep(0.1)
            else:
                break

        os.system("echo " + self.trigger + " > " + self.current_trigger)

    @property
    def sample_rate(self):
        """Get sampling frequency of the AD7476 use hrtimer"""
        return float(os.read(os.open(self.trigger_dir, os.O_RDWR), 16))

    @sample_rate.setter
    def sample_rate(self, value):
        """Sets sampling frequency of the AD7476 use hrtimer"""
        os.write(os.open(self.trigger_dir, os.O_RDWR), str(value).encode())
