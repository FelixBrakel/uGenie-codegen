#!/bin/bash
#source venv/bin/activate
export PYTHONPATH="$PWD"
echo "PYTHONPATH: $PYTHONPATH"
echo "" > test_output.txt
for i in {146..188}
do
  echo "--------- $i" >&1 | tee -a test_output.txt
  ./tester/cleaner.sh
  python main.py $i >&1 | tee -a test_output.txt
  cd "tester"
  python tb_gen.py $i
  python tcl_gen.py
  cd ..
  ./tester/compile_vhdl.sh
  cd "tester"
  python run_tests.py >&1 | tee -a ../test_output.txt
  cd ..
done