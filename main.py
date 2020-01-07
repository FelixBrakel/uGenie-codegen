import pygraphviz
from pygraphviz import AGraph
import os.path
import csv
import op_generator
import alloc_generator
import input_mapper
import control_signal_generator
from typing import List, Tuple
from assembler import Assembler
from atmi import ATMI, MergeException
from datatypes import RFallocation
import sys

def main(architecture):
    # architecture = '148'
    dfg = parser('dotfiles/Architecture_latency_{}.dot'.format(architecture))
    simplified_dfg = parser('dotfiles/Architecture_latency_{}_schematic.dot'.format(architecture))

    fus: List[AGraph] = dfg.subgraphs()

    subgraphs = {}
    for subgraph in fus:
        subgraphs[subgraph.graph_attr['label'].strip()] = subgraph

    for fu in fus:
        ATMI.max_cycle = 0
        assembler = Assembler()

        label = fu.graph_attr['label'].strip()
        # NOTE: handle load FUs
        if 'load' in label or 'store' in label:
            continue

        input_map, max_fu = input_mapper.map_input(fu, subgraphs, simplified_dfg)
        rf_alloc_path = 'dotfiles/Architecture_latency_{}_'.format(architecture) + label + '_rf_allocation.csv'
        rf_allocs, max_address = rf_alloc_parser(rf_alloc_path)

        assembler.add_assembly(op_generator.gen_op_insts(rf_allocs, dfg, fu, input_map))
        assembler.add_assembly(alloc_generator.gen_alloc_insts(rf_allocs, dfg, fu, input_map))

        try:
            assembler.compile(max_address, max_fu)
            config = control_signal_generator.gen_config(assembler, max_address, max_fu, 1, label)
            vhdl, tot_wait = control_signal_generator.insert_signals(assembler.export())

            with open('out/' + label + '.program', 'w') as f:
                f.write('TOTAL_WAIT_NS ' + str(tot_wait) + '\n')
                for line in config:
                    f.write(line + '\n')
                f.write('\n')
                for line in vhdl:
                    f.write(line + '\n')

        except MergeException as merge:
            print("ERROR COMPILING INSTRUCTIONS FOR " + label + " : " + merge.args[0])

        # assembler.print()

        # for code in vhdl:
        #     print(code)

        # for line in config:
        #     print(line)


def rf_alloc_parser(rf_alloc_path) -> Tuple[List[RFallocation], int]:
    rf_allocs = []
    max_address = 0

    if not os.path.exists(rf_alloc_path):
        return rf_allocs, max_address

    with open(rf_alloc_path) as rf_alloc_file:
        rf_alloc_data = csv.reader(rf_alloc_file)

        next(rf_alloc_data)
        for row in rf_alloc_data:
            tmp = RFallocation(row)
            rf_allocs.append(tmp)

            if tmp.address > max_address:
                max_address = tmp.address

        return rf_allocs, max_address


def parser(architecture_file_path: str) -> AGraph:
    return AGraph(architecture_file_path)


if __name__ == '__main__':
    architecture = sys.argv[1]
    main(architecture)
