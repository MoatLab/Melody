#!/bin/bash
ulimit -s unlimited

source /mnt/sda4/venv-tf/bin/activate
models_dir="/mnt/sda4/gpt-2/models"
script_path="/mnt/sda4/gpt-2/src/generate_unconditional_samples.py"

python ${script_path} --models_dir=${models_dir} --model_name=124M --length=500 --nsamples=5 --seed=0 2> /dev/null # ignore warnings
