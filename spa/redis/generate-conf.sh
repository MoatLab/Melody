#!/bin/bash
# Generates redis.conf from redis.conf.template by substituting paths and addresses
# defined in paths.sh. Run this once after cloning or after changing paths.sh.

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_PATH}/paths.sh"
export REDIS_DATA_DIR REDIS_SERVER

mkdir -p "${REDIS_DATA_DIR}"

envsubst '${REDIS_DATA_DIR} ${REDIS_SERVER}' \
  < "${SCRIPT_PATH}/redis.conf.template" \
  > "${SCRIPT_PATH}/redis.conf"

echo "Generated redis.conf"
