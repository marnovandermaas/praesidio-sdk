#include<linux/unistd.h>
#include<stdio.h>

#define __NR_create_enclave 292

long create_enclave(int i)
{
  return syscall(__NR_create_enclave, i);
}

int main(void)
{
  printf("%d\n", create_enclave(15));
}
