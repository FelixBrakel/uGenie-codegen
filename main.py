import pygraphviz
from pygraphviz import AGraph
import os.path
import csv
import op_generator
import alloc_generator
import input_mapper
from typing import List, Dict
from assembler import Assembler
from atmi import ATMI
from datatypes import RFallocation


def main():
    # agraph: AGraph = AGraph('dotfiles/Architecture_latency_146.dot')
    dfg = parser('dotfiles/Architecture_latency_146.dot')
    simplified_dfg = parser('dotfiles/Architecture_latency_146_schematic.dot')

    fus: List[AGraph] = dfg.subgraphs()
    # instructions: List[Instruction] = []

    subgraphs = {}
    for subgraph in fus:
        subgraphs[subgraph.graph_attr['label'].strip()] = subgraph

    for fu in fus:
        ATMI.max_cycle = 0
        assembler = Assembler()

        label = fu.graph_attr['label'].strip()
        # NOTE: handle load FUs
        if 'load' in label:
            continue

        if label == 'add_1':
            input_map = input_mapper.map_input(fu, subgraphs, simplified_dfg)
            rf_alloc_path = 'dotfiles/Architecture_latency_146_' + label + '_rf_allocation.csv'
            rf_allocs: List[RFallocation] = rf_alloc_parser(rf_alloc_path)

            assembler.add_assembly(op_generator.gen_op_insts(rf_allocs, dfg, fu, input_map))
            assembler.add_assembly(alloc_generator.gen_alloc_insts(rf_allocs, dfg, fu, input_map))

            assembler.compile()
            assembler.print()
            break


def rf_alloc_parser(rf_alloc_path) -> List[RFallocation]:
    rf_allocs = []

    if not os.path.exists(rf_alloc_path):
        return rf_allocs

    with open(rf_alloc_path) as rf_alloc_file:
        rf_alloc_data = csv.reader(rf_alloc_file)

        next(rf_alloc_data)
        for row in rf_alloc_data:
            rf_allocs.append(RFallocation(row))

        return rf_allocs


def parser(architecture_file_path: str) -> AGraph:
    return AGraph(architecture_file_path)


if __name__ == '__main__':
    main()
