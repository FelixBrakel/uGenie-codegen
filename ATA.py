from typing import Union
from enum import Enum


class OPInput:
    pass


class FUinput:
    num: int

    def __init__(self, num: int):
        self.num = num


class RFInput:
    pass


class ATAInstruction:
    cycle: int

    def __lt__(self, other):
        return self.cycle < other.cycle


class ATAFetch(ATAInstruction):
    class REG(Enum):
        REG0 = 0
        REG1 = 1

    addr: int
    reg: REG

    def __init__(self, addr: int, reg: REG, cycle: int):
        self.addr = addr
        self.reg = reg
        self.cycle = cycle


class ATAStore(ATAInstruction):
    input: Union[FUinput, OPInput]
    addr: int

    def __init__(self,
                 inp: Union[FUinput, OPInput],
                 addr: int,
                 cycle: int):
        self.input = inp
        self.addr = addr
        self.cycle = cycle


class ATAOp(ATAInstruction):
    input0: Union[FUinput, OPInput, RFInput]
    input1: Union[FUinput, OPInput, RFInput]

    def __init__(self, input0: Union[FUinput, OPInput, RFInput], input1: Union[FUinput, OPInput, RFInput], cycle: int):
        self.input0 = input0
        self.input1 = input1
        self.cycle = cycle
