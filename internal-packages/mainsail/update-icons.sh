#!/bin/sh
if [ ! -d ${QBE_PATHS_MOONRAKER_THEME} ]; then
  exit 0
fi
if ls ${QBE_PATHS_MOONRAKER_THEME}/*.png >/dev/null 2>&1; then
    cp ${QBE_PATHS_MOONRAKER_THEME}/*.png "${QBE_DIRS_PKG}/img/icons/"
fi
