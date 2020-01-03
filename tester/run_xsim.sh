#!/usr/bin/bash
set -e
cd ../vhdl_work_dir
make create_snapshot FU=$1
make sim FU=$1
