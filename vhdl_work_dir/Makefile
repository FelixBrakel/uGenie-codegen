SHELL=/usr/bin/bash -O extglob -c
#.SHELLFLAGS=""
VHDL_SRC:= $(wildcard *.vhd)
VHDL_SRC:= $(patsubst %, ../%,$(VHDL_SRC))
FU?=fallback
BUILD_DIR=build
SIM_TIME="30"

all: analyze_vhdl create_snapshot

sim:
	cd ${BUILD_DIR};xsim work.${FU}_tb -tclbatch ${FU}.tcl
#	rm ${BUILD_DIR}/run.tcl

create_snapshot:
	cd ${BUILD_DIR};xelab ${FU}_tb -debug typical

analyze_vhdl:
	cd ${BUILD_DIR};xvhdl ${VHDL_SRC}

clean:
	cd ${BUILD_DIR};rm -rf *

very_clean:
	rm -f !("FU_instruction_memory.vhd"|"FU_register_file.vhd"|"FU_template.vhd"|"Makefile"|"build")
	cd build; rm -rf *