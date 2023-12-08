ARG BASE_IMAGE="ubuntu"
ARG TAG="22.04"
FROM ${BASE_IMAGE}:${TAG}
WORKDIR /rpi

ARG DEBIAN_FRONTEND=noninteractive
ARG USER_NAME=rpi
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd ${USER_NAME} --gid ${USER_GID}\
    && useradd -l -m ${USER_NAME} -u ${USER_UID} -g ${USER_GID} -s /bin/bash

RUN apt-get update && apt-get install --no-install-recommends -y \
    lsb-release ca-certificates apt-file \
    sudo git bc bison flex libssl-dev make nano vim kmod cpio rsync fakeroot zsh-common \
    libc6-dev libncurses5-dev \
    bash-completion crossbuild-essential-arm64 gcc-aarch64-linux-gnu build-essential 
    
# Create non root user for pip
ENV USER=${USER_NAME}

RUN echo "rpi ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER_NAME}
RUN chmod 0440 /etc/sudoers.d/${USER_NAME}

RUN chown -R ${USER_NAME}:${USER_NAME} /${USER_NAME}

ENV KERNEL=kernel8 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-


USER ${USER_NAME}

#RUN git clone --depth=1 https://github.com/raspberrypi/linux /rpi/linux 

CMD ["/bin/bash"]

# make oldconfig ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- deb-pkg -j$(nproc)
# make oldconfig ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) Image.gz modules dtbs

# make-kpkg --rootcmd fakeroot kernel_image

# make-kpkg --rootcmd fakeroot --arch arm --cross-compile /usr/bin/arm-linux-gnueabihf- --revision=1.0 --jobs 5 --overlay-dir ~/overlay-dir kernel_image &
