from typing import List
from atmi import ATMI
from math import log2, ceil
from assembler import Assembler


def insert_signals(insts: List[str]) -> List[str]:
    out = []
    wait = '        wait for 50 ns;'
    if len(insts) > 0:
        out.append('        r_r_LOAD_INST <= \'1\';')
        out.append('        r_r_INPUT_INST <= \"' + insts[0] + '\";')
        out.append(wait)

    iterinsts = iter(insts)
    next(iterinsts)

    for bitstring in iterinsts:
        if bitstring:
            pass

        out.append('        r_r_LOAD_NEXT_INST <= \'1\';')
        out.append('        r_r_LOAD_INST <= \'1\';')
        out.append('        r_r_INPUT_INST <= \"' + bitstring + '\";')
        out.append(wait)

    out.append('        r_r_LOAD_NEXT_INST <= \'0\';')
    out.append('        r_r_LOAD_INST <= \'0\';')
    out.append('        r_r_COMPUTING <= \'1\';')
    # out.append(wait)

    return out


def gen_config(assembler: Assembler, max_rf: int, max_fu: int, max_output: int, label: str) -> List[str]:
    out = []

    im_size = 2**int(ceil(log2(len(assembler.atmc) + 1)))
    rf_size = 2**int(ceil(log2(max_rf + 1)))
    max_cycle = 2**int(ceil(log2(ATMI.max_cycle + 1)))

    if 'add' in label:
        is_mul = 0
        opcode = 0
    else:
        is_mul = 1
        opcode = 1

    out.append('            INSTRUCTIONS => ' + str(im_size))
    out.append('            BITWIDTH => 31')
    out.append('            RF_DEPTH => ' + str(rf_size))
    out.append('            INPUT_PORTS => ' + str(max_fu))
    out.append('            OUTPUT_PORTS => ' + str(max_output))
    out.append('            TOTAL_EXE_CYCLES => ' + str(max_cycle))
    out.append('            OPCODE => ' + str(opcode))
    out.append('            IS_MUL => ' + str(is_mul))


    return out
