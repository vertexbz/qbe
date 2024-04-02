#!/usr/bin/env bash
set -euo pipefail

# Config
readonly IMAGE='2023-05-03-raspios-bullseye-armhf-lite'
readonly DTB='bcm2710-rpi-3-b-plus.dtb'
readonly KERNEL='kernel8.img'


# Script
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly QEMU_DIR="${SCRIPT_DIR}/.qemu"
readonly KERNEL_FILE="${QEMU_DIR}/${KERNEL}"
readonly DTB_FILE="${QEMU_DIR}/${DTB}"

readonly IMAGE_FILE="${QEMU_DIR}/${IMAGE}.img"
if [ ! -f "${IMAGE_FILE}" ]; then
  >&2 echo "No image to run, expected ${IMAGE_FILE}!"
  exit 1
fi

if [ ! -f "${KERNEL_FILE}" ] || [ ! -f "${DTB_FILE}" ]; then
  boot_partition="$(hdiutil attach "${IMAGE_FILE}" | grep Windows_FAT_32 | cut -f3)"

  cp "${boot_partition}/${DTB}" "${DTB_FILE}"
  cp "${boot_partition}/${KERNEL}" "${KERNEL_FILE}"

  echo 'pi:$6$rBoByrWRKMY1EHFy$ho.LISnfm83CLBWBE/yqJ6Lq1TinRlxw/ImMTPcvvMuUfhQYcMmFnpFXUPowjy2br1NA0IACwF9JKugSNuHoe0' > "${boot_partition}/userconf"
  touch "${boot_partition}/ssh"

  hdiutil detach "${boot_partition}"

  qemu-img resize "${IMAGE_FILE}" 32G
fi

exec qemu-system-aarch64 \
    -m 1G \
    -M raspi3b \
    -cpu cortex-a72 \
    -smp 4 \
    -usb \
    -device 'usb-net,netdev=net0' \
    -netdev 'user,id=net0,hostfwd=tcp::5022-:22,hostfwd=tcp::8080-:80' \
    -drive "file=${IMAGE_FILE},index=0,format=raw" \
    -dtb "${DTB_FILE}" \
    -kernel "${KERNEL_FILE}" \
    -append 'rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1' \
    -no-reboot \
    -nographic
