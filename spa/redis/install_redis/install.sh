#!/bin/bash

sudo apt update >/dev/null 2>&1

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_PATH}/../paths.sh"

cd "${REDIS_BASE_DIR}"

echo "Check redis ..."
[[ -d redis ]] && rm -rf redis && echo "redis removed"

echo "Install redis ..."
git clone https://github.com/redis/redis.git > /dev/null 2>&1
cd redis
git checkout 6.2
make

cd ${SCRIPT_PATH}


