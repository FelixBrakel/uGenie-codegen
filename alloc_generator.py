from typing import List
from datatypes import RFallocation, parse_instruction, Config
from ATA import ATAStore, OPInput, FUinput, ATAInstruction
from pygraphviz import AGraph


def gen_alloc_insts(rf_allocs: List[RFallocation], dfg: AGraph, fu: AGraph) -> List[ATAInstruction]:
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
            input_type = FUinput(1)

        cycle = inst.cycle + rf_alloc.type
        rf_insts.append(ATAStore(input_type, cycle, rf_alloc.address))

    return rf_insts
