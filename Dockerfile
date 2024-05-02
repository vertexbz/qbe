FROM debian:latest

ENV container docker
ARG DEBIAN_FRONTEND noninteractive

RUN apt update && \
    apt upgrade -y && \
    apt install -y python3-pystemd libsystemd-dev sudo htop systemd systemd-sysv python3-virtualenv python3-dev python3-dev libffi-dev build-essential libncurses-dev avrdude gcc-avr binutils-avr avr-libc stm32flash dfu-util libnewlib-arm-none-eabi gcc-arm-none-eabi binutils-arm-none-eabi libusb-1.0-0 libusb-1.0-0-dev pkg-config python3-numpy python3-matplotlib libatlas-base-dev git unzip && \
    apt-get clean ; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* ; \
    rm -rf /lib/systemd/system/multi-user.target.wants/* ; \
    rm -rf /etc/systemd/system/*.wants/* ; \
    rm -rf /lib/systemd/system/local-fs.target.wants/* ; \
    rm -rf /lib/systemd/system/sockets.target.wants/*udev* ; \
    rm -rf /lib/systemd/system/sockets.target.wants/*initctl* ; \
    rm -rf /lib/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup* ; \
    rm -rf /lib/systemd/system/systemd-update-utmp* ;

RUN useradd -ms /bin/bash -G sudo,tty printer && \
    mkdir -p /var/opt /etc/network/interfaces.d && \
    chown printer /var/opt && \
    chown printer /opt && \
    ln -sf /opt/qbe `/var/opt/qbe/bin/python -c 'import site; print(site.getsitepackages()[0])'`/qbe && \
    echo "printer ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "source /var/opt/qbe/bin/activate" >> /root/.bashrc && \
    echo "source /var/opt/qbe/bin/activate" >> /home/printer/.bashrc && \
    echo "alias qbe-init='pip install --editable .'" >> /root/.bashrc && \
    echo "alias qbe-init='pip install --editable .'" >> /home/printer/.bashrc

USER printer
COPY --chown=printer . /opt/qbe
RUN virtualenv /var/opt/qbe && \
    . /var/opt/qbe/bin/activate && \
    cd /opt/qbe && \
    pip install --editable .
USER root

VOLUME [ "/opt/qbe", "/var/opt/qbe" ]

CMD ["/lib/systemd/systemd"]
