# QBE

> NOTE: it assumes user has NOPASSWD sudo access

## Installation

```shell
sudo apt update
sudo apt install -y git python3-dev python3-virtualenv libffi-dev libxml2-dev libxslt-dev libsystemd-dev libssl-dev gcc rustc musl-dev

sudo groupadd qbe-manager
sudo usermod -a -G qbe-manager `whoami`
newgrp qbe-manager

sudo mkdir -p /opt /var/opt
sudo chown root:qbe-manager /opt /var/opt
sudo chmod g+w /opt /var/opt

pip install --upgrade pip

cd /opt
git clone https://github.com/vertexbz/qbe.git

cp ./qbe/qbe.template.yml ~/qbe.yml

virtualenv -p python3 /var/opt/qbe

/var/opt/qbe/bin/pip install --upgrade pip
/var/opt/qbe/bin/pip install --editable /opt/qbe
ln -sf /opt/qbe `/var/opt/qbe/bin/python -c 'import site; print(site.getsitepackages()[0])'`/qbe


sudo ln -sf /var/opt/qbe/bin/qbe /usr/local/bin/qbe
```

## Printer definition file

Update `~/qbe.yml`

## Run it!

```shell
qbe update
```

If your setup requires system changes it may be worth to reboot after run

# TODO

* [ ] Moonraker db interactions?
* [ ] Support multiple providers of the same type
* [ ] Config (qbefile, manifest, lockfile?) validation
* [ ] More info in cli status
* [ ] Nice Moonraker sudo
* [ ] Docs