#define _GNU_SOURCE

#include "utils.h"
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sched.h>
#include <errno.h>
#include <time.h>

#include <numa.h>
#include <numaif.h>

#include <stdint.h>
#include <stdbool.h>

#include <assert.h>
#include <immintrin.h>

pthread_barrier_t barrier;

void read_loop(void *array, size_t size) {
	size_t* carray = (size_t*) array;
	size_t val = 0;
	size_t i;
	for (i = 0; i < size / sizeof(size_t); i++) {
		val += carray[i];
	}
	assert(val != 0xdeadbeef);
}

void read_avx(void* array, size_t size) {
	__m256* varray = (__m256*) array;
	__m256 accum = _mm256_set1_ps((float) 0xDEADBEEF);
	size_t i;
	for (i = 0; i < size / sizeof(__m256i); i++) {
		 _mm_prefetch(&varray[i+2], _MM_HINT_NTA);
		accum = _mm256_add_ps(varray[i], accum);
	}
	assert(!_mm256_testz_ps(accum, accum));
}

void write_avx(void* array, size_t size) {
	__m256i* varray = (__m256i*) array;
	__m256i vals = _mm256_set1_epi32(0xDEADBEEF);
	size_t i;
	for (i = 0; i < size / sizeof(__m256i); i++) {
		_mm256_store_si256(&varray[i], vals);
	}
}

void op_ld(char* addr, long size){
  if(size < 512){
    fprintf(stderr, "ERROR buffer size is too small");
    exit(1);
  }
  size = size - (size % 512);
  asm volatile(
    "mov %[addr], %%r9 \n"
    "xor %%r10, %%r10 \n"
    "LOOP_LD: \n"
    SIZELD_1024_AVX512
    "cmp %[size], %%r10 \n"
    "jl LOOP_LD \n"
    : /* output */
    :[size]"r"(size), [addr]"r"(addr) 
    :"%r9", "%r10" 
  );
}

void op_st(char* addr, long size){
  if(size < 512){
    fprintf(stderr, "ERROR buffer size is too small");
    exit(1);
  }
  size = size - (size % 512);
  asm volatile(
    "mov %[addr], %%r9 \n"
    "xor %%r10, %%r10 \n"
    "LOOP_ST: \n"
    SIZEST_1024_AVX512
    "cmp %[size], %%r10 \n"
    "jl LOOP_ST \n"
    : /* output */
    :[size]"r"(size), [addr]"r"(addr) 
    :REGISTERS, "%r10" 
  );
}

void swap(chase_t* n1, chase_t* n2) {
  chase_t* temp;
  temp = n1->ptr_arr[0];
  n1->ptr_arr[0] = n2->ptr_arr[0];
  n2->ptr_arr[0] = temp;

  n1->ptr_arr[0]->ptr_arr[1] = n1;
  n2->ptr_arr[0]->ptr_arr[1] = n2;

  temp = n1->ptr_arr[1];
  n1->ptr_arr[1] = n2->ptr_arr[1];
  n2->ptr_arr[1] = temp;

  n1->ptr_arr[1]->ptr_arr[0] = n1;
  n2->ptr_arr[1]->ptr_arr[0] = n2;
}

void shuffle(header_t* header) {
  srand(time(NULL));
  chase_t* curr_ptr = (chase_t*)header->start_addr_a;
  uint64_t i = 0;
  uint64_t k = 0;
  int interval = 1048576;
  // int interval = 524288;
  // int interval = 4194304;
  while (i < header->num_chase_block) {
    uint64_t start = i;
    for (k = 0; k < interval; k += 1) {
      uint64_t j = (uint64_t)(rand()%interval);
      swap((chase_t*) &(curr_ptr[start+k]), (chase_t*) &(curr_ptr[(start+j)]));
    }
    i += k;
  }
}

void verify(header_t* header) {
  chase_t* curr_ptr;
  chase_t* next_ptr;
  curr_ptr = (chase_t*)header->start_addr_a;
  uint64_t i = 0;
  while (i < header->num_chase_block) {
    if ((int)(curr_ptr->ptr_arr[3]) != 0) {
      printf("ERROR %lu, %lu\n", i, curr_ptr->ptr_arr[3]);
      break;
    }
    curr_ptr->ptr_arr[3] = (int)curr_ptr->ptr_arr[3] + 1;
    next_ptr = curr_ptr->ptr_arr[0];
    i += 1;
    curr_ptr = next_ptr;
  }
}

uint64_t init_ptr_buf(header_t* header) {
  chase_t* curr_ptr;
  chase_t* next_ptr;
  curr_ptr = (chase_t*)header->start_addr_a;
  for (uint64_t i = 0; i < header->num_chase_block - 1; i++) {
    next_ptr = &(curr_ptr[1]);
    curr_ptr->ptr_arr[0] = next_ptr;
    next_ptr->ptr_arr[1] = curr_ptr;
    curr_ptr = next_ptr;
  }
  curr_ptr->ptr_arr[0] = (chase_t*)header->start_addr_a;
  curr_ptr->ptr_arr[0]->ptr_arr[1] = curr_ptr;

  // shuffle(header);
  verify(header);
  return 0;
}

uint64_t op_ptr_chase(char* addr, uint64_t num_chase_block) {
  uint64_t t_start = 0, t_end = 0;
  asm volatile(
    "mov %[addr], %%r11 \n"
    "xor %%r10, %%r10 \n"
    TIMING_BEGIN
    "LOOP_CHASE: \n"
    "mov (%%r11), %%r11 \n"
    "inc %%r10 \n"
    "cmp %[num_chase_block], %%r10 \n"
    "jl LOOP_CHASE \n"
    TIMING_END
    :[t_start] "=r" (t_start), [t_end] "=r" (t_end)
    :[addr] "r" (addr), [num_chase_block] "r" (num_chase_block)
    :REGISTERS, "%r10", "%r11"
  );
  return (t_end - t_start);
}

uint64_t rdtscp_time(uint64_t count) {
  uint64_t t_start = 0, t_end = 0, start = 0, end = 0;
  asm volatile(
    TIMING_BEGIN
    TIMING_END
    :[t_start] "=r" (t_start), [t_end] "=r" (t_end)
  );
  start = t_start;
  for (int i = 0; i < count; i += 1) {
    // asm volatile(
    //   TIMING_BEGIN
    //   TIMING_END
    // );
    asm volatile(
      "rdtscp \n" \
      "rdtscp \n" \
      );
  }
  asm volatile(
    TIMING_BEGIN
    TIMING_END
    :[t_start] "=r" (t_start), [t_end] "=r" (t_end)
  );
  end = t_end;
  return ((end - start)/(1+count*2));
}

void pointer_chasing(header_t* header) {
  uint64_t result, latency_sum = 0; uint64_t avg_cycle = 0;
  uint64_t cnt = 0;
  uint64_t start[2], end[2];
  int *records_buf = (int *) header->records_buf;
  if (header->start_addr_a == NULL) {
    printf("ERROR header->start_addr_a == NULL\n");
    return;
  }
  init_ptr_buf(header);
  uint64_t interval = header->chase_interval;
  pthread_barrier_wait(&barrier);

  op_ptr_chase(header->start_addr_a, header->num_chase_block);
  
  for (int i = 0; i < header->op_iter; i += 1) {
    for (uint64_t j = 0; j < header->num_chase_block; j += interval) {
      result = op_ptr_chase(((chase_t*)(header->start_addr_a))+j, interval);
      latency_sum += result;
      if (header->print) {
        records_buf[cnt] = (1.0 / header->tsc_freq) * (result / interval);
      }
      cnt += 1;
    }
  }
  avg_cycle = latency_sum / header->op_iter;
}

void bandwidth(header_t* header) {
  char* src = header->start_addr_a;
  uint64_t fixed_step = 512 << 6;
  // uint64_t fixed_step = header->per_thread_size;
  int counter = 0;

  pthread_barrier_wait(&barrier);
  while (1) {
    if(counter + fixed_step >= header->per_thread_size){
      counter = 0;
      src = header->start_addr_a;
    }
    if (header->type == LOADED_POINTER_CHASING || header->type == RD_BW) {
      // op_ld(src, fixed_step);
      //read_loop(src, fixed_step);
      read_avx(src, fixed_step);
    } else if (header->type == LOADED_POINTER_CHASING_WR || header->type == WR_BW) {
      // op_st(src, fixed_step);
      write_avx(src, fixed_step);
    }
    header->curr_op_cnt += fixed_step;
    counter += fixed_step;
    src += fixed_step;
    if (header->halt == 1) {
      break;
    }
  }
}

int stick_this_thread_to_core(int core_id) {
  int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
  if (core_id < 0 || core_id >= num_cores)
    return EINVAL;
  cpu_set_t cpuset;
  CPU_ZERO(&cpuset);
  CPU_SET(core_id, &cpuset);
  pthread_t current_thread = pthread_self();
  return pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
}

void* thread_wrapper(void* arg) {
  header_t* header = (header_t*)arg;
  int ret = 0;
  ret = stick_this_thread_to_core(header->thread_idx);
  if(ret != 0){
    printf("ERROR stick_this_thread_to_core\n");
    return NULL;
  }

  ret = init_buf(header->total_buf_size, header->buf_a_numa_node, &(header->buf_a));
  if (ret < 0) {
    fprintf(stderr, "ERROR init_buf in thread %d.\n", header->thread_idx);
    numa_free(header->buf_a, header->total_buf_size);
    return NULL;
  }
  int alloc_node = 0;
  if (header->buf_a_numa_node == 0) {
	  alloc_node = 1;
  }
  if (header->print) {
    ret = init_buf((header->num_chase_block/header->chase_interval)*header->op_iter*sizeof(int), alloc_node, &(header->records_buf));
    if (ret < 0) {
      fprintf(stderr, "ERROR init_buf (records) in thread %d.\n", header->thread_idx);
      numa_free(header->buf_a, header->total_buf_size);
      return NULL;
    }
  }

  // pthread_barrier_wait(&barrier);
  header->start_addr_a = &(header->buf_a[0]);
  if (header->type == POINTER_CHASING) {
    pointer_chasing(header);
  } else if (header->type == LOADED_POINTER_CHASING || header->type == LOADED_POINTER_CHASING_WR || header->type == RD_BW || header->type == WR_BW) {
    if (header->thread_idx == 0 && (header->type == LOADED_POINTER_CHASING || header->type == LOADED_POINTER_CHASING_WR)) {
      pointer_chasing(header);
    } else {
      memset(header->buf_a, 0xFF, header->total_buf_size);
      bandwidth(header);
    }
  }
  numa_free(header->buf_a, header->total_buf_size);
  return NULL;
}

int run(header_t* header) {
  pthread_t* thread_arr;
  header_t* header_arr;
  header_t* curr_header;
  int ret, num_thread;
  ret = 0;

  num_thread = header->num_thread;
  thread_arr = malloc(num_thread * sizeof(pthread_t));
  header_arr = malloc(num_thread * sizeof(header_t));
  memset(header_arr, 0, num_thread * sizeof(header_t));

  pthread_barrier_init(&barrier, NULL, num_thread);

  for (int i = 0; i < num_thread; i++) {
    curr_header = &(header_arr[i]);
    memcpy(curr_header, header, sizeof(header_t));
    curr_header->thread_idx = i;
    curr_header->halt = 0;
    curr_header->curr_op_cnt = 0;

    // curr_header->start_addr_a = &(curr_header->buf_a[i * curr_header->per_thread_size]);
    ret = pthread_create(&thread_arr[i], NULL, thread_wrapper, (void*)curr_header);
  }

  if (header->type == LOADED_POINTER_CHASING || header->type == LOADED_POINTER_CHASING_WR || header->type == RD_BW || header->type == WR_BW) {
    pthread_join(thread_arr[0], NULL);
    stop_threads(header_arr, 1);
    for (int i = 1; i < num_thread; i++) {
      ret = pthread_join(thread_arr[i], NULL);
    }
  } else if (header->type == POINTER_CHASING) {
    for (int i = 0; i < num_thread; i++) {
      ret = pthread_join(thread_arr[i], NULL);
    }
  }

  pthread_barrier_destroy(&barrier);
  // print memory latency
  if (header->print) {
    if (header->type == POINTER_CHASING) {
      for (int i = 0; i < num_thread; i++) {
        int *records_buf = (int *) header_arr[i].records_buf;
        for (uint64_t k = 0; k < (header->num_chase_block/header->chase_interval)*header->op_iter; k += 1) {
          printf("%d\n", records_buf[k]);
        }
      }
    } else if (header->type == LOADED_POINTER_CHASING || header->type == LOADED_POINTER_CHASING_WR) {
      int num_threads = 1;
      for (int i = 0; i < num_threads; i++) {
        int *records_buf = (int *) header_arr[i].records_buf;
        for (uint64_t k = 0; k < (header->num_chase_block/header->chase_interval)*header->op_iter; k += 1) {
          printf("%d\n", records_buf[k]);
        }
      }
    }
  }
  free(thread_arr);
  return ret;
}

int main(int argc, char*argv[]) {
  int ret;
  header_t* header;
  header = malloc(sizeof(header_t));
  ret = parse_arg(argc, argv, header);
  if (ret < 0) {
    printf("ERROR parse_arg\n");
    return 0;
  }
  run(header);
  return 0;
}
