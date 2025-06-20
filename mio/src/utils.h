#ifndef UTIL_H
#define UTIL_H

#include <stdint.h>
#include <stdbool.h>

#define TSC_FREQ_GHZ  2.1
#define DELAY_MSEC    3000000
#define PAGESZ        1 << 12

#define TIMING_BEGIN \
  "rdtscp \n" \
  "lfence \n" \
  "mov %%edx, %%r9d \n" \
  "mov %%eax, %%r8d \n"

#define TIMING_POINT_START \
  "lfence \n"

#define TIMING_END \
  "mfence \n" \
  "rdtscp \n" \
  "lfence \n" \
  "shl $32, %%rdx \n" \
  "or  %%rax, %%rdx \n" \
  "mov %%r9d, %%eax \n" \
  "shl $32, %%rax \n" \
  "or  %%r8, %%rax \n" \
  "mov %%rax, %[t_start] \n" \
  "mov %%rdx, %[t_end] \n"

#define TIMING_POINT_END \
  "mfence \n" \
  "lfence \n"

#define SIZELD_1024_AVX512 \
  "vmovdqa64  0x0(%%r9, %%r10), %%zmm0 \n" \
  "vmovdqa64  0x40(%%r9, %%r10), %%zmm1 \n" \
  "vmovdqa64  0x80(%%r9, %%r10), %%zmm2 \n" \
  "vmovdqa64  0xc0(%%r9, %%r10), %%zmm3 \n" \
  "vmovdqa64  0x100(%%r9, %%r10), %%zmm4 \n" \
  "vmovdqa64  0x140(%%r9, %%r10), %%zmm5 \n" \
  "vmovdqa64  0x180(%%r9, %%r10), %%zmm6 \n" \
  "vmovdqa64  0x1c0(%%r9, %%r10), %%zmm7 \n" \
  "vmovdqa64  0x200(%%r9, %%r10), %%zmm8 \n" \
  "vmovdqa64  0x240(%%r9, %%r10), %%zmm9 \n" \
  "vmovdqa64  0x280(%%r9, %%r10), %%zmm10 \n" \
  "vmovdqa64  0x2c0(%%r9, %%r10), %%zmm11 \n" \
  "vmovdqa64  0x300(%%r9, %%r10), %%zmm12 \n" \
  "vmovdqa64  0x340(%%r9, %%r10), %%zmm13 \n" \
  "vmovdqa64  0x380(%%r9, %%r10), %%zmm14 \n" \
  "vmovdqa64  0x3c0(%%r9, %%r10), %%zmm15 \n" \
  "add $0x400, %%r10 \n"

#define SIZEST_1024_AVX512  \
  "vmovdqa64  %%zmm0,  0x0(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x40(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x80(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0xc0(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x100(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x140(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x180(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x1c0(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x200(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x240(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x280(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x2c0(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x300(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x340(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x380(%%r9, %%r10) \n" \
  "vmovdqa64  %%zmm0,  0x3c0(%%r9, %%r10) \n" \
  "add $0x400, %%r10 \n"

#define REGISTERS "rsi", "rax", "rdx", "rcx", "r8", "r9", "ymm0"

typedef enum types {
  POINTER_CHASING,
  LOADED_POINTER_CHASING,
  LOADED_POINTER_CHASING_WR,
  RD_BW,
  WR_BW,
} types_t;

typedef struct chase_struct chase_t;

struct chase_struct {
  // 64-bit addr, 64 * 8 = 512 bit (64bytes) per cacheline
  chase_t* ptr_arr[8];
};

typedef struct header_struct {
  int print;
  uint64_t num_thread; // number of threads
  uint64_t total_buf_size; // buffer size
  int buf_a_numa_node; // which numa node for buffer
  char* buf_a;
  char* records_buf;

  double tsc_freq;
  int thread_idx;

  char* start_addr_a;
  uint64_t per_thread_size;

  int op_iter;
  int starting_core;
  bool random;

  uint64_t num_chase_block;
  uint64_t chase_interval;

  types_t type;

  volatile uint64_t curr_op_cnt;

  volatile int halt;
} header_t;

int parse_arg(int argc, char*argv[], header_t* header);

int init_buf(uint64_t size, int node, char** alloc_ptr);

void stop_threads(header_t* header_arr, int start_index);

#endif // UTIL_H
