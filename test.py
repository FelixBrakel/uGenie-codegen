import pygraphviz
import os.path
import csv
from enum import Enum
from typing import List
from ATA import ATAdefinition, ATALoad, ATAOp, ATAStore, RFInput, OPInput, FUinput


class RF_allocation:
    address: int
    name: str
    label: str

    def __init__(self, csvrow: List[str]):
        self.address = int(csvrow[0])
        tmp = csvrow[1].split(' ')
        self.name = tmp[0][1]
        self.label = tmp[1]

    def get_node(self, graph: pygraphviz.AGraph):
        return graph.get_node(self.name)


class FUTypeNotImplementedException(Exception):
    pass


class FU_Types(Enum):
    ADD, MUL = range(2)


class Instruction:
    number: str
    cycle: int

    def __init__(self, number: str, cycle: int):
        self.number = number
        self.cycle = cycle


def parse_instruction(name: str, inst_label: str):
    inst_label.strip()
    inst_attr: List[str] = inst_label.split('.')
    cycle: int = int(inst_attr[len(inst_attr) - 1].split(':')[1])
    return Instruction(name, cycle)


def main():
    # agraph: pygraphviz.AGraph = pygraphviz.AGraph('dotfiles/Architecture_latency_146.dot')
    DFG = parser('dotfiles/Architecture_latency_146.dot')
    FUs: List[pygraphviz.AGraph] = DFG.subgraphs()

    # instructions: List[Instruction] = []

    for FU in FUs:
        label = FU.graph_attr['label'].strip()
        # NOTE: handle load FUs
        if 'load' in label:
            continue

        rf_alloc_path = 'dotfiles/Architecture_latency_146_' + label + '_rf_allocation.csv'
        rf_allocs: List[RF_allocation] = rf_alloc_parser(rf_alloc_path)

        input_mapper(rf_allocs, FU, DFG)


def rf_alloc_parser(rf_alloc_path) -> List[RF_allocation]:
    rf_allocs = []

    if not os.path.exists(rf_alloc_path):
        return rf_allocs

    with open(rf_alloc_path) as rf_alloc_file:
        rf_alloc_data = csv.reader(rf_alloc_file)

        next(rf_alloc_data)
        for row in rf_alloc_data:
            rf_allocs.append(RF_allocation(row))

        return rf_allocs


def parser(architecture_file_path: str) -> pygraphviz.AGraph:
    return pygraphviz.AGraph(architecture_file_path)


# Returns an unsorted list of assembly
def input_mapper(rf_allocs: List[RF_allocation], FU: pygraphviz.AGraph, DFG: pygraphviz.AGraph) -> List[ATAdefinition]:
    assembly = []
    instructions: List[Instruction] = []

    for instruction in FU.nodes():
        inst_label = instruction.attr['label']
        instructions.append(parse_instruction(instruction.get_name(), inst_label))

    for instruction in instructions:
        n = DFG.get_node(instruction.number)
        nodes = DFG.predecessors(n)

        if nodes[0] in FU:
            input0 = OPInput
            # TODO determine FU input port
            input1 = FUinput
        elif nodes[1] in FU:
            input0 = FUinput
            # TODO determine FU input port
            input1 = OPInput
        else:
            # TODO determine FU input ports
            input0 = FUinput
            input1 = FUinput

        for rf_alloc in rf_allocs:
            if rf_alloc.name == nodes[0].get_name():
                input0 = RFInput
                # TODO: Create load ATAI
            if rf_alloc.name == nodes[1].get_name():
                input1 = RFInput
                # TODO: Create load ATAI

            if input1 == RFInput and input0 == RFInput:
                break


def alloc_compiler(rf_allocs: List[RF_allocation], DFG: pygraphviz.AGraph):
    pass


if __name__ == '__main__':
    main()
