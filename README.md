## Build driver AD7476 for Raspberry Pi x64.

    git clone https://github.com/karu2003/rpi_ad7476
    cd rpi_ad7476
    git clone --depth=1 https://github.com/raspberrypi/linux

### Build Docker

    docker build . -t rpi
    docker run --rm -it -v `pwd`:/rpi rpi:latest bash

### in Docker

    cd linux
    make bcm2711_defconfig
    sed -i 's/# CONFIG_AD7476 is not set/CONFIG_AD7476=m/g' .config
    make oldconfig -j$(nproc) Image.gz modules dtbs
    make oldconfig -j$(nproc) modules_install INSTALL_MOD_PATH=deploy
    exit

### on PC

    cd linux/
    sudo cp arch/arm64/boot/Image.gz /media/andrew/bootfs/kernel8.img 
    sudo cp arch/arm64/boot/dts/broadcom/*.dtb /media/andrew/bootfs/
    sudo cp arch/arm64/boot/dts/overlays/*.dtb* /media/andrew/bootfs/overlays/
    sudo cp -ar deploy/lib/modules/6.1.65-v8+/ /media/andrew/rootfs/lib/modules/

    copy rpi-ad7476a-overlay.dts to RPi

### on RPi

    find /lib/modules | grep ad74
    sudo modprobe ad7476
    lsmod | grep ad74
    echo ad7476 | sudo tee -a /etc/modules
    echo iio-trig-hrtimer | sudo tee -a /etc/modules
    sudo depmod

    dtc -I dts -O dtb rpi-ad7476a-overlay.dts -o rpi-ad7476a-overlay.dtbo
    sudo cp rpi-ad7476a-overlay.dtbo /boot/overlays/

    sudo update-initramfs -c -k $(uname -r)

    add to config.txt

    dtoverlay=rpi-ad7476a-overlay
    initramfs initrd.img-6.1.65-v8+ followkernel

    sudo cp 87-iio-noroot.rules /etc/udev/rules.d/

    sudo groupadd iio
    sudo usermod -a -G iio $USER
    sudo udevadm control --reload-rules

    tree -ifFpugsh '/sys/bus/iio/devices/iio:device0/'
    tree -ifFpugsh '/sys/kernel/config/iio/triggers/'

    pip install pyqtgraph
    git clone https://github.com/karu2003/rpi_ad7476
    git clone https://github.com/analogdevicesinc/pyadi-iio.git
    cd pyadi-iio
    pip install .

    sudo reboot

### ADC testing

    cat /sys/bus/iio/devices/iio\:device0/name
    cat /sys/bus/iio/devices/iio\:device0/in_voltage0_raw 
    cat /sys/bus/iio/devices/iio\:device0/in_voltage_scale

### Build IIO from git

    git clone https://github.com/analogdevicesinc/libiio.git --branch v0.25
    cd libiio
    mkdir build && cd build && cmake ../ && make && sudo make install



