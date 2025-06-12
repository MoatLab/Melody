#!/bin/bash
EXE_DIR="/mnt/sda4/MERCI"
HOME=/mnt/sda4

cd ${EXE_DIR};
./3_clustering/bin/clustering -d amazon_Home_and_Kitchen -p 8000
cd -;
