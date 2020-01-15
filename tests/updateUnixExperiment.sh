#!/bin/sh -x
CURDIR=$(pwd)
echo $CURDIR
SIFIVE_DIR=/local/scratch/mv380/riscv/freedom-u-sdk
UNIX_DIR=/local/scratch/mv380/benchmarks/unix-pipes
cd $UNIX_DIR
TARGET=sifive make
sudo cp $UNIX_DIR/*.out $SIFIVE_DIR/work/buildroot_initramfs_sysroot/usr/mv380/
echo "#" >> $SIFIVE_DIR/conf/linux_defconfig 
cd $SIFIVE_DIR
make sim
