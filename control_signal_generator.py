from typing import List, Tuple
from atmi import ATMI
from math import log2, ceil
from assembler import Assembler


def insert_signals(insts: List[str]) -> Tuple[List[str], int]:
    out = []
    wait = '        wait for 50 ns;'
    tot_wait = 0
    if len(insts) > 0:
        out.append('        r_r_LOAD_INST <= \'1\';')
        out.append('        r_r_INPUT_INST <= \"' + insts[0] + '\";')
        # out.append('        r_r_LOAD_NEXT_INST <= \'1\';')
    #     out.append(wait)
    #     tot_wait += 50
    #
    iterinsts = iter(insts)
    next(iterinsts)

    for bitstring in iterinsts:
        # if bitstring:
        #     pass

        out.append('        r_r_LOAD_NEXT_INST <= \'1\';')
        out.append(wait)
        tot_wait += 50
        out.append('        r_r_LOAD_INST <= \'1\';')
        out.append('        r_r_INPUT_INST <= \"' + bitstring + '\";')

    out.append('        r_r_LOAD_NEXT_INST <= \'0\';')
    out.append(wait)
    tot_wait += 50
    out.append('        r_r_LOAD_INST <= \'0\';')
    out.append('        r_r_COMPUTING <= \'1\';')
    # out.append(wait)

    return out, tot_wait


def gen_config(assembler: Assembler, max_rf: int, max_fu: int, max_output: int, label: str) -> List[str]:
    out = []

    im_size = 2**int(ceil(log2(len(assembler.atmc)))) - 1
    rf_size = max(2**int(ceil(log2(max_rf + 1))) - 1, 1)
    max_cycle = 2**int(ceil(log2(ATMI.max_cycle + 1))) - 1

    if 'add' in label:
        bitwidth = 31
        is_mul = 0
        opcode = 0
    else:
        bitwidth = 63
        is_mul = 1
        opcode = 1

    out.append('            INSTRUCTIONS => ' + str(im_size) + ',')
    out.append('            BITWIDTH => ' + str(bitwidth) + ',')
    out.append('            RF_DEPTH => ' + str(rf_size) + ',')
    out.append('            INPUT_PORTS => ' + str(max_fu + 1) + ',')
    out.append('            OUTPUT_PORTS => ' + str(max_output) + ',')
    out.append('            TOTAL_EXE_CYCLES => ' + str(max_cycle) + ',')
    out.append('            OPCODE => ' + str(opcode) + ',')
    out.append('            IS_MUL => ' + str(is_mul))

    return out
