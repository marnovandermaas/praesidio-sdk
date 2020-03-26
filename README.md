# Praesidio SDK

This builds a complete RISC-V cross-compile toolchain for Praesidio enclave system. It is based on the SiFive Freedom Unleashed SDK.

## Tested Configurations

### Ubuntu 16.04 x86_64 host
- Build dependencies: `build-essential git autotools texinfo bison flex libgmp-dev libmpfr-dev libmpc-dev gawk libz-dev libssl-dev device-tree-compiler`

### Ubuntu 18.04 x86_64 host
- Build dependencies: `autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev libusb-1.0-0-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev device-tree-compiler pkg-config libexpat-dev`

## Build Instructions

Checkout this repository. Then you will need to checkout all of the linked submodules using:

`git submodule update --recursive --init`

This will take some time and require around 7 GiB of disk space.

Once the submodules are initialized, run `make` and the complete toolchain and bbl image will be built. The completed build tree will consume about 14 GiB of disk space.

## Booting Linux on a simulator

You can boot linux on Spike by running `make sim`. This will build the Spike simulator and run Linux on it.
