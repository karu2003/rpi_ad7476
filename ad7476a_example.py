import adi
import numpy as np

import ad7476

target_device = "ad7476a"

ad7476a_dev = ad7476.ad7476a("ip:analog",target_device)

chn = 1
# ad7476a_dev._rx_data_type = np.int32
# ad7476a_dev.rx_output_type = "SI"
ad7476a_dev.rx_enabled_channels = [chn]
ad7476a_dev.rx_buffer_size = 100

data = ad7476a_dev.rx()

print(data)