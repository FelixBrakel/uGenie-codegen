from typing import List, Dict
from datatypes import RFallocation, parse_instruction, Config
from ata import ATAStore, OPInput, FUinput, ATAI
from pygraphviz import AGraph


class AllocException(Exception):
    pass


def gen_alloc_insts(rf_allocs: List[RFallocation], dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> List[ATAI]:
    rf_insts = []

    for rf_alloc in rf_allocs:
        inst = parse_instruction(dfg.get_node(rf_alloc.name))
        if rf_alloc.type == RFallocation.FUTypes.MUL:
            latency = Config.MUL_LATENCY
        elif rf_alloc.type == RFallocation.FUTypes.ADD:
            latency = Config.ADD_LATENCY
        else:
            # TODO: load inst latency?
            latency = 0

        if rf_alloc.name in fu:
            input_type = OPInput()
        else:
            # TODO: map fu input
            input_type = FUinput(input_map[rf_alloc.name])
            if input_type is None:
                raise AllocException('alloc not found in input map')

        cycle = inst.cycle + latency
        rf_insts.append(ATAStore(input_type, rf_alloc.address, cycle))

    return rf_insts
