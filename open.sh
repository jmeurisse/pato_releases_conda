#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory
hdiutil attach -mountpoint local_volume pato_releases_conda.sparsebundle
