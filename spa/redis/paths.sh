#!/bin/bash
# Machine-specific configuration.
# Edit these variables once to match your environment; all scripts source this file.

REDIS_BASE_DIR="/mnt/sda4"
REDIS_INSTALL_DIR="${REDIS_BASE_DIR}/redis"
REDIS_SRC_DIR="${REDIS_INSTALL_DIR}/src"
REDIS_DATA_DIR="${REDIS_BASE_DIR}/REDIS"

YCSB_BASE_DIR="/tdata"
YCSB_DIR="${YCSB_BASE_DIR}/YCSB"

BIN_DIR="/usr/local/bin"

REDIS_SERVER="10.10.1.1"
REDIS_CLIENT="10.10.1.2"
