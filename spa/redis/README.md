## Setup

**1. Configure paths and addresses**

Edit `paths.sh` to match your machine (only file you need to touch):
```bash
REDIS_BASE_DIR="/mnt/sda4"   # where Redis is compiled and run
REDIS_DATA_DIR="$REDIS_BASE_DIR/REDIS"  # log and pid file location
YCSB_BASE_DIR="/tdata"       # where YCSB is installed
REDIS_SERVER="10.10.1.1"     # server node IP
REDIS_CLIENT="10.10.1.2"     # client node IP
```

**2. Generate `redis.conf`**

Creates the data directory and fills in paths/addresses from `paths.sh`:
```bash
./generate-conf.sh
```

**3. Install Redis**
```bash
cd install_redis
./install.sh      # clone and compile Redis 6.2 into $REDIS_BASE_DIR
./pkgdep.sh       # install system dependencies
```

**4. Install YCSB**
```bash
cd install_redis
./ycsb.sh         # clone and build YCSB into $YCSB_BASE_DIR
```

**5. Create symlinks** (adds redis-server, redis-cli, etc. to PATH)
```bash
./create-link.sh
```

## Run

```bash
sudo ./run.sh <workload-file>          # run all lines in workload file
sudo ./run.sh <workload-file> <line>   # run a single line
```

Results are written to `rst/`.
