# Praesidio SDK
> Author: Marno van der Maas

This builds a complete RISC-V cross-compile toolchain for Praesidio enclave system, which physically isolated enclaves on secure cores that are separate from application cores. This skeleton repository is based on a previous version of the SiFive Freedom Unleashed SDK.

## Build Dependencies

### Ubuntu 18.04.5 x86_64 host

- Build dependencies: `autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev libusb-1.0-0-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev device-tree-compiler pkg-config libexpat-dev python3-doit`

### Ubuntu 20.04.1 x86_64 host

- Build dependencies: `autoconf curl libmpc-dev libusb-1.0-0-dev build-essential bison flex texinfo gperf libtool patchutils zlib1g-dev device-tree-compiler pkg-config libexpat-dev python3-doit`

## Build Instructions

Clone this repository and initialize all the submodules with the following commands:

```bash
git clone https://github.com/marnovandermaas/praesidio-sdk.git
cd praesidio-sdk
git submodule update --recursive --init
```

This will take some time and require around 7 GiB of disk space. At the moment the submodule update might skip the `riscv-gnu-toolchain` module. If this is the case for you, please execute the following commands:

```bash
git clone https://github.com/riscv/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
git checkout b4dae89f85bf882852c6186b1284df11065bfcd9
git submodule update --recursive --init
cd ..
```

Once the submodules are initialized, run `make` and the complete toolchain and bbl image will be built, which will take a while.

On Ubuntu 20.04 you will encounter an error asking you to port `freadahead.c` and `fseeko.c` to your platform, this is because they updated in glibc. A current workaround is to make the changes in [this commit](https://github.com/coreutils/gnulib/commit/4af4a4a71827c0bc5e0ec67af23edef4f15cee8e) to the files in `./work/buildroot_initramfs/build/host-m4-1.4.17/lib/` and then running `make` again.

## Booting Linux on Spike

You can boot linux on Spike by running `make sim`. This will build the Spike simulator and Linux. Finally, it will run Linux on Spike. The completed build tree will consume about 14 GiB of disk space.

To log in:
- username: `root`
- password: `root`

And to shutdown the system use the `halt` command.

## Future Features
These are things that still need to be implemented:
- The user API, Linux driver and management shim already have a way to request attestation, but we still need to implement the measurement of the shim and the enclave as well as signing these measurements.
- Install a trap handler in the management shim, which handles scheduling and puts the enclave in an error state if it causes a trap.
- Install a page table for enclaves, so that global variables can be used.
- Tags are currently the same throughout the system. We should implement a prototype of tag translation so that tags in the last-level cache can be compressed compared with those in the tag directory.

## License
This repository is distributed under the MIT license, and it is a combination of numerous sub-repositories, which all have different licenses. For example, riscv-gnu-toolchain, buildroot and Linux are all licensed under GPLv2; riscv-fesvr and riscv-pk under BSD; and praesidio-software under MIT.

## Paper Results
This section is dedicated to instructions on how to replicate the results of the paper title "Protecting Enclaves from Intra-Core Side-Channel Attacks through Physical Isolation."

### Prerequisites
Please make sure you have `python3` installed with the following packages: `csv tabulate matplotlib numpy statistics`.

### Ring Buffer
To get the results in the figure with the caption "Ring buffer performance over shared pages between enclaves. Each packet size is sent 256 times and thegraph shows a line of the median value and error bars fromthe first quartile to the third quartile," please run the following commands:
```bash
cd logs
python3 process.py ring ring20200828.log
cd ..
```

### Page Donation
To get the results from the "Page Donation" of the evaluation run the following commands:
```bash
cd logs
python3 process.py page page20200826.log
cd ..
```

To get the comparable results for Unix pipes run the following commands:
```bash
cd logs
python3 process.py unix unixpipe20200826.log
cd ..
```

Both of these output the array of raw values and then an array of 3 elements; which are the first, second and third quartile used for the calculation in the paper.

### Enclave Creation
To get the results in the table titled "Setup Cost for Creating Enclaves with Proportion ofthe Different Phases of the Process and the Total Cost," please run the following commands:
```bash
cd logs
python3 process.py hello hello20200825_*
cd ..
```

The result should end by printing the following, which corresponds with the values in the table:
```
['Prepare Enclave Pages', 'Setup Driver', 'Setup Enclave']
Instruction percentages:
[(2.7616950031938226, 0.003393724298664136), (95.75768931645021, 0.052721100958777356), (1.4805311651344435, 0.054349226158271424)]
(9465753.285714285, 7467.285714285448)
Cache access percentages:
[(4.098405288399673, 0.07477941320776704), (92.82815436310099, 0.04328939199700699), (3.073440348499327, 0.07366749766401659)]
(80985.28571428571, 313.7142857142899)
```

### Generating Logs
The above instructions all rely on previously generated logs. You may also generate your own logs by following these instructions:
1. Edit line 78 in `riscv-isa-sim/riscv/sim.h` to be `static const size_t INTERLEAVE = 6;`
1. If you've already followed the build instructions please remove the Spike build directory by `rm -rf work/riscv-isa-sim/`
1. Then run `make sim_cache` which will build Spike again and boot up our system with caches enabled (note: this is a lot slower than with caches disabled). If you want to recreate the unix pipes benchmark, use the `make sim_pipe` instead.
1. Once booted up use the login credentials shown in the booting section.
1. Change to the correct directory for the benchmark you would like to run:
    * `cd benchmarks/ring` for the ring buffer benchmark
    * `cd benchmarks/page` for the page donation benchmark
    * `cd benchmarks/unix` for the unix pipe comparison to the page donation benchmark
    * `cd benchmarks/hello` for the enclave creation benchmark
1. Run the benchmark by running `./user.out`
1. Once the benchmark is done running, press control-c twice to exit the simulator
1. Optional: If you want to keep your log do `mv stats.log logs/<log_name>.log` where you replace `<log_name>` to a log name of your choosing
1. Run the python script with `python3 process.py {ring, page, unix, hello} <log_files>` where you must choose what type of benchmark you've run and the log file you want to process.

### Management Shim Size
To calculate the size of the management shim and the lines of code, run the following commands:
```bash
ls -lh praesidio-software/build/managementshim/management.bin
cd praesidio-software/lib
cat ../managementshim/* instructions.* praesidiooutput.h mailbox.* unsignedinteger.h enclaveLibrary.h praesidiopage.h praesidiooutput.* | sed '/^\s*$/d' | wc -l
cd ../..
```
