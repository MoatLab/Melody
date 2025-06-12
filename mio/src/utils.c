#include "utils.h"
#include <stdio.h>
#include <numa.h>
#include <numaif.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <assert.h>
#include <time.h>

#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>

void set_default(header_t* header) {
  header->print = 1;
  header->num_thread = 1;
  header->total_buf_size = (1 << 30);
  header->buf_a_numa_node = 0;
  header->op_iter = 5;
  header->per_thread_size = header->total_buf_size;
  header->starting_core = -1;
  header->random = false;
  header->halt = 0;
  header->num_clear_pipe = 0;
  header->tsc_freq = TSC_FREQ_GHZ;
  header->type = POINTER_CHASING;
  header->num_chase_block = header->per_thread_size / sizeof(chase_t);
  assert(header->num_chase_block > 0);
  header->chase_interval = header->num_chase_block;
}

int parse_arg(int argc, char*argv[], header_t* header) {
  int opt;
  // int thread_num;
  // int read;
  // int write;
  set_default(header);

  while ((opt = getopt(argc, argv, "t:m:i:r:I:T:P:")) != -1) {
    switch (opt) {
      case 't':
        header->num_thread = atoi(optarg);
        assert(header->num_thread > 0);
        break;
      case 'm':
        header->total_buf_size = ((uint64_t)atoi(optarg) * ((1 << 20)));
        // printf("%lu\n", header->total_buf_size);
        header->per_thread_size = header->total_buf_size;
        header->num_chase_block = header->per_thread_size / sizeof(chase_t);
        break;
      case 'i':
        header->op_iter = atoi(optarg);
        break;
      case 'r':
        header->buf_a_numa_node = atoi(optarg);
        break;
      case 'I':
        header->chase_interval = atoi(optarg);
        assert(header->num_chase_block % header->chase_interval == 0);
        break;
      case 'T':
        header->type = atoi(optarg);
        break;
      case 'P':
        header->print = atoi(optarg);
        break;
    }
  }
  return 0;
}

int init_buf(uint64_t size, int node, char** alloc_ptr) {
  char *ptr;
  unsigned long page_size;
  uint64_t page_cnt;
  uint64_t idx;
  if ((ptr = (char *)numa_alloc_onnode(size, node)) == NULL) {
    fprintf(stderr,"ERROR: numa_alloc_onnode\n");
    return -1;
  }
  page_size = (unsigned long)getpagesize();
  page_cnt = (size / page_size);
  idx = 0;
  for (uint64_t i = 0; i < page_cnt; i++) {
    ptr[idx] = 0;
    idx += page_size;
  }
  *alloc_ptr = ptr;
  return 0;
}

void stop_threads(header_t* header_arr, int start_index) {
  int num_thread = header_arr[0].num_thread;
  for (int i = start_index; i < num_thread; i++) {
    header_arr[i].halt = 1;
  }
}
