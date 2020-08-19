# Praesidio SDK

This builds a complete RISC-V cross-compile toolchain for Praesidio enclave system. It is based on the SiFive Freedom Unleashed SDK.

## Tested Configurations

### Ubuntu 18.04 x86_64 host

- Build dependencies: `autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev libusb-1.0-0-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev device-tree-compiler pkg-config libexpat-dev python3-doit`

## Build Instructions

Clone this repository and initialize all the submodules with the following commands:

```
git clone https://github.com/marnovandermaas/praesidio-sdk.git
git submodule update --recursive --init
```

This will take some time and require around 7 GiB of disk space. At the moment the submodule update might skip the `riscv-gnu-toolchain` if this is the case for you please execute the following commands:

```
git clone https://github.com/riscv/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
git checkout b4dae89f85bf882852c6186b1284df11065bfcd9
git submodule update --recursive --init
cd ..
```

Once the submodules are initialized, run `make` and the complete toolchain and bbl image will be built, which will take a while.

## Booting Linux on a simulator

You can boot linux on Spike by running `make sim`. This will build the Spike simulator and Linux. Finally, it will run Linux on Spike. The completed build tree will consume about 14 GiB of disk space.

## Using Linux

To log in:
- username: `root`
- password: `root`

And to shutdown the system use the `halt` command.

## Future Features
These are things that still need to be implemented:
- The user API, Linux driver and management shim already have a way to request attestation, but we still need to implement the measurement of the shim and the enclave as well as signing these measurements.
- Install a trap handler in the management shim.
