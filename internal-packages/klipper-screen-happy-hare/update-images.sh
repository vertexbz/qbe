#!/bin/sh
src="${QBE_DIRS_PKG}"
for style in `ls -d ${src}/styles/*/images`; do
    for img in `ls ${src}/happy_hare/images`; do
        ln -sf "${src}/happy_hare/images/${img}" "${style}/${img}"
    done
done
