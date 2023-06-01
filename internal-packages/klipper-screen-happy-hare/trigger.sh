#!/bin/sh

sudo usermod -a -G tty $USER

if [ -e /etc/X11/Xwrapper.config ]
then
    sudo sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config
else
    echo 'allowed_users=anybody' | sudo tee /etc/X11/Xwrapper.config
fi
