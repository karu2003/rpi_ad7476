import pytest
import ad7476

hardware = "ad7476a"
# classname = "adi.ad7476a"
classname = "ad7476.ad7476a"


#########################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
def test_ad74764_rx_data(test_dma_rx, iio_uri, classname, channel):
    test_dma_rx(iio_uri, classname, channel)