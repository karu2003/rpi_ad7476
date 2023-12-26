import ad7476
import numpy as np

target_device = "ad7476a"
samples = 1000

sample_rate = 40000.0
ADC = ad7476.ad7476a("local:", target_device, "trigger100")

ADC._rx_data_type = np.int32

ADC.rx_output_type = "SI"

ADC.rx_buffer_size = samples

if sample_rate > ADC.max_sample_rate:
    sample_rate = ADC.max_sample_rate

ADC.hrtimer.sample_rate = sample_rate
data = ADC.rx()
print(data)
