## Install
* Install phoronix-test-suite:
	```
	./install.sh
	```
* Setup phoronix (go to the installed directory, `/mnt/sda4` is the default one):
	```
	sudo ./phoronix-test-suite batch-setup
	```

	> Save test results when in batch mode (Y/n): n

	> Run all test options (Y/n): n

## Run Workloads
* Two sets of workloads: some are in `w.txt`, the others are in `w_noop.txt`. For example, run the first workload in `w.txt`:
	```
	sudo ./run.sh w.txt 1
	```
	Run the first workload in `w_noop.txt`:
	```
	sudo ./run_noop.sh w_noop.txt 1
	```
