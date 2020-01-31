#include <stdint.h>
#include <asm-generic/unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include "praesidio.h"

long create_enclave(void *enclave_memory)
{
  return syscall(__NR_create_enclave, enclave_memory);
}

int main(void)
{
  FILE *fp = fopen("e.bin", "r");
  int c;
  size_t i = 0;
  char *enclave_memory_buffer = malloc(NUMBER_OF_ENCLAVE_PAGES << PAGE_BIT_SHIFT);

  for(i = 0; i < (NUMBER_OF_ENCLAVE_PAGES << PAGE_BIT_SHIFT); i++) {
    c = fgetc(fp);
    if( feof(fp) ) {
       break ;
    }
    enclave_memory_buffer[i] = (char) c;
  }
  printf("Copied %lu bytes to enclave memory buffer.\n", i);
  for(; i < (NUMBER_OF_ENCLAVE_PAGES << PAGE_BIT_SHIFT); i++) {
    enclave_memory_buffer[i] = 0;
  }

  printf("Got Enclave ID: %d\n", create_enclave((void*) enclave_memory_buffer));
  fclose(fp);
}
