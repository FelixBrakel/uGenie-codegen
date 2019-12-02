from datatypes import RFallocation, Instruction, DoubleUnidenticalOPInputException, parse_instruction, Config
from ata import ATAI, ATAFetch, ATAOp, RFInput, OpInput, FUinput
from pygraphviz import AGraph, Node
from typing import List, Union, Type, Optional, Dict


class FUinputException(Exception):
    pass


def find_rf_alloc(rf_allocs: List[RFallocation], instruction: Instruction) -> Optional[RFallocation]:
    for rf_alloc in rf_allocs:
        if rf_alloc.name == instruction.name:
            return rf_alloc

    return None


# Returns an unsorted list of assembly
def gen_op_insts(rf_allocs: List[RFallocation], dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> List[ATAI]:
    assembly = []
    instructions: List[Instruction] = []

    for instruction in fu.nodes():
        instructions.append(parse_instruction(instruction))

    for instruction in instructions:
        n = dfg.get_node(instruction.name)
        nodes = dfg.predecessors(n)

        input_type0 = inst_input_type(rf_allocs, fu, nodes[0])
        if len(nodes) > 1:
            input_type1 = inst_input_type(rf_allocs, fu, nodes[1])
        else:
            input_type1 = input_type0

        # This should never occur but we check for it anyways
        if input_type0 == OpInput and input_type1 == OpInput:
            if nodes[0] != nodes[1]:
                raise DoubleUnidenticalOPInputException

        # TODO: find shceduling for fetch ops might need to be swapped to fit?
        if input_type0 == RFInput:
            # If the data is in the RF we need to generate fetch instructions
            assembly.append(generate_fetch(rf_allocs, instruction, nodes[0], ATAFetch.REG.REG0))
            input0 = RFInput()
        elif input_type0 == OpInput:
            input0 = OpInput()
        else:
            # TODO: DETERMINE FU INPUT NUMBER
            n = input_map[nodes[0].get_name()]
            if n is None:
                raise FUinputException('Cannot find FU from which predecessing node originates in map')

            input0 = FUinput(n)

        if input_type1 == RFInput:
            assembly.append(generate_fetch(rf_allocs, instruction, nodes[1], ATAFetch.REG.REG1))
            input1 = RFInput()
        elif input_type1 == OpInput:
            input1 = OpInput()
        else:
            # TODO: DETERMINE FU INPUT NUMBER
            n = input_map[nodes[1].get_name()]
            if n is None:
                raise FUinputException('Cannot find FU from which predecessing node originates in map')

            input1 = FUinput(n)

        assembly.append(ATAOp(input0, input1, instruction.cycle))

    return assembly


def generate_fetch(rf_allocs: List[RFallocation],
                   instruction: Instruction,
                   pred: Node,
                   reg: ATAFetch.REG) -> ATAI:
    cycle = instruction.cycle - Config.FETCH_LATENCY
    address = find_rf_alloc(rf_allocs, Instruction(pred.get_name(), pred.attr['label'])).address

    return ATAFetch(address, reg, cycle)


def inst_input_type(rf_allocs: List[RFallocation],
                    fu: AGraph,
                    pred: Node) -> Union[Type[RFInput], Type[OpInput], Type[FUinput]]:
    for rf_alloc in rf_allocs:
        if rf_alloc.name == pred.get_name():
            return RFInput

    if pred in fu:
        return OpInput
    else:
        return FUinput
