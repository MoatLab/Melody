#!/bin/bash
EXE_DIR="/mnt/sda4/MERCI"
HOME=/mnt/sda4

cd ${EXE_DIR};
./3_clustering/bin/clustering -d amazon_Sports_and_Outdoors -p 6340
cd -;
