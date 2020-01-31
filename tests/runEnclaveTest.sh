set -e
set -x
cd ..
cd riscv-isa-sim/benchmarks
make
cd ../..
cp riscv-isa-sim/benchmarks/hello.out tests/praesidioDriverTest/e.out
cd tests/praesidioDriverTest/
riscv64-unknown-linux-gnu-objcopy -O binary e.out e.bin 
riscv64-unknown-linux-gnu-gcc -I../../riscv-isa-sim/benchmarks/include -I../../riscv-isa-sim/managementenclave linuxEnclaveTest.c
cp a.out ../../work/buildroot_initramfs_sysroot/root
cp e.bin ../../work/buildroot_initramfs_sysroot/root
cd ../../
echo "#" >> conf/linux_defconfig
make sim
