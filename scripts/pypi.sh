#!/bin/sh

# build
for VERSION in 3.6 3.7 3.8 3.9; do
  # Create and activate environment
  conda create -y -n py$VERSION python=$VERSION wheel=0.34.2
  conda activate py$VERSION

  pip install --no-cache-dir setuptools wheel
  python setup.py bdist_wheel --plat-name manylinux1_x86_64
  python setup.py bdist_wheel --plat-name macosx_10.9_x86_64

# Cleanup
  conda deactivate
  rm -rf build
done