# Praesidio SDK

This builds a complete RISC-V cross-compile toolchain for Praesidio enclave system. It is based on the SiFive Freedom Unleashed SDK.

## Tested Configurations

### Ubuntu 18.04 x86_64 host

- Build dependencies: `autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev libusb-1.0-0-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev device-tree-compiler pkg-config libexpat-dev python3-doit`

## Build Instructions

Clone this repository and initialize all the submodules with the following commands:

```bash
git clone https://github.com/marnovandermaas/praesidio-sdk.git
cd praesidio-sdk
git submodule update --recursive --init
```

This will take some time and require around 7 GiB of disk space. At the moment the submodule update might skip the `riscv-gnu-toolchain` if this is the case for you please execute the following commands:

```bash
git clone https://github.com/riscv/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
git checkout b4dae89f85bf882852c6186b1284df11065bfcd9
git submodule update --recursive --init
cd ..
```

Once the submodules are initialized, run `make` and the complete toolchain and bbl image will be built, which will take a while.

## Booting Linux on Spike

You can boot linux on Spike by running `make sim`. This will build the Spike simulator and Linux. Finally, it will run Linux on Spike. The completed build tree will consume about 14 GiB of disk space.

To log in:
- username: `root`
- password: `root`

And to shutdown the system use the `halt` command.

## Future Features
These are things that still need to be implemented:
- The user API, Linux driver and management shim already have a way to request attestation, but we still need to implement the measurement of the shim and the enclave as well as signing these measurements.
- Install a trap handler in the management shim.

## Paper Results
This section is dedicated to instructions on how to replicate the results of the paper title "Protecting Enclaves from Intra-Core Side-Channel Attacks through Physical Isolation."

### Ring Buffer

### Page Donation
To get the results from the "Page Donation" of the evaluation run the following commands:
```bash
cd logs
python3 process.py page page20200622_*
```

To get the comparable results for Unix pipes run the following commands:
```bash
cd logs
python3 process.py unix unixpipe20200624.log
```

Both of these output the array of raw values and then an array of 3 elements; which are the first, second and third quartile used for the calculation in the paper.

### Enclave Creation
To get the results in the table titled "Setup Cost for Creating Enclaves with Proportion ofthe Different Phases of the Process and the Total Cost," please run the following commands:
```bash
cd logs
python3 process.py hello hello20200623_*
```

The result should end by printing the following, which corresponds with the values in the table:
```
['Prepare Enclave Pages', 'Setup Driver', 'Setup Enclave']
Instruction percentages:
[(2.670941607132784, 0.0022230164082368553), (96.94716228428898, 0.0008729128092426208), (0.38181063310166724, 0.0030959790463510606)]
(9359412, 5457)
Cache access percentages:
[(4.093558958317874, 0.05345870769130734), (92.93880007388158, 0.06871872311090499), (2.966387389071329, 0.0219654398859479)]
(79771.66666666667, 95.66666666667152)
```
