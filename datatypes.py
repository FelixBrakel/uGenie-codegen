from enum import Enum
from pygraphviz import AGraph, Node
from typing import List


class Config:
    FETCH_LATENCY = 1
    STORE_LATENCY = 1
    MUL_LATENCY = 2
    ADD_LATENCY = 1


class RFallocation:
    class FUTypes(Enum):
        ADD, MUL, LOAD = range(3)

    def __init__(self, csvrow: List[str]):
        self.address: int = int(csvrow[0])
        tmp = csvrow[1].split(' ')
        self.name: str = tmp[0][1]
        label = tmp[1]

        if 'mul' in label:
            self.type: RFallocation.FUTypes = self.FUTypes.MUL
        elif 'add' in label:
            self.type: RFallocation.FUTypes = self.FUTypes.ADD
        else:
            self.type: RFallocation.FUTypes = self.FUTypes.LOAD

    def get_node(self, graph: AGraph):
        return graph.get_node(self.name)


class DoubleUnidenticalOPInputException(Exception):
    pass


class Instruction:
    def __init__(self, name: str, cycle: int):
        self.name: str = name
        self.cycle: int = cycle


def parse_instruction(n: Node):
    inst_label = n.attr['label']
    inst_label.strip()
    inst_attr: List[str] = inst_label.split('.')
    cycle: int = int(inst_attr[len(inst_attr) - 1].split(':')[1])
    return Instruction(n.get_name(), cycle)
