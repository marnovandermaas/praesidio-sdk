# Praesidio SDK

This builds a complete RISC-V cross-compile toolchain for Praesidio enclave system. It is based on the SiFive Freedom Unleashed SDK.

## Tested Configurations

### Ubuntu 18.04 x86_64 host
- Build dependencies: `autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev libusb-1.0-0-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev device-tree-compiler pkg-config libexpat-dev python3-doit`

## Build Instructions

Checkout this repository. Then you need to checkout all of the linked submodules using:

`git submodule update --recursive --init`

This will take some time and require around 7 GiB of disk space. At the moment the submodule update might skip the `riscv-gnu-toolchain` if this is the case for you please execute the following command:

```
git clone git@github.com:marnovandermaas/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
git submodule update --recursive --init
cd ..
```

Once the submodules are initialized, run `make` and the complete toolchain and bbl image will be built, which will take a while.

## Booting Linux on a simulator

You can boot linux on Spike by running `make sim`. This will build the Spike simulator and Linux. Finally, it will run Linux on Spike. The completed build tree will consume about 14 GiB of disk space.

## Using Linux
To log in:
- username: `root`
- password: `sifive`
