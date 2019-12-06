from typing import Union
from enum import Enum
from abc import ABC, abstractmethod
from atmi import ATMI


class OpInput:
    pass


class FUinput:
    # TODO: make sure this num value doesn't go out of range
    def __init__(self, num: int):
        self.num: int = num


class RFInput:
    pass


class ATAI(ABC):
    def __init__(self, cycle: int):
        self.cycle: int = cycle

    def __lt__(self, other):
        return self.cycle < other.cycle

    @abstractmethod
    def to_atmi(self, rf_depth: int, input_ports: int) -> ATMI:
        pass


class ATAFetch(ATAI):
    class REG(Enum):
        REG0 = 0
        REG1 = 1

    def __init__(self, addr: int, reg: REG, cycle: int):
        super().__init__(cycle)
        self.addr: int = addr
        self.reg: ATAFetch.REG = reg

    def to_atmi(self, rf_depth: int, input_ports: int) -> ATMI:
        # TODO: Don't hardcode these parameters
        atmi = ATMI(rf_depth, input_ports)
        atmi.cycle = self.cycle

        if self.reg == ATAFetch.REG.REG0:
            atmi.r_reg0_s = self.addr
        else:
            atmi.r_reg1_s = self.addr

        atmi.insts['Fetch'] = 1

        return atmi


class ATAStore(ATAI):
    def __init__(self,
                 inp: Union[FUinput, OpInput],
                 addr: int,
                 cycle: int):
        super().__init__(cycle)
        self.input: Union[FUinput, OpInput] = inp
        self.addr: int = addr

    def to_atmi(self, rf_depth: int, input_ports: int) -> ATMI:
        # TODO: Don't hardcode these parameters
        atmi = ATMI(rf_depth, input_ports)
        atmi.cycle = self.cycle

        if type(self.input) == FUinput:
            atmi.cbOut2 = self.input.num
            atmi.reg0 = True
            atmi.w_reg0_s = self.addr
        else:
            atmi.reg1 = True
            atmi.w_reg1_s = self.addr

        atmi.insts['Store'] = 1

        return atmi


class ATAOp(ATAI):
    def __init__(self, input0: Union[FUinput, OpInput, RFInput], input1: Union[FUinput, OpInput, RFInput], cycle: int):
        super().__init__(cycle)
        self.input0: Union[FUinput, OpInput, RFInput] = input0
        self.input1: Union[FUinput, OpInput, RFInput] = input1

    def to_atmi(self, rf_depth: int, input_ports: int) -> ATMI:
        # TODO: Don't hardcode these parameters
        atmi = ATMI(rf_depth, input_ports)
        atmi.cycle = self.cycle

        type0 = type(self.input0)
        type1 = type(self.input1)

        if type0 == FUinput:
            atmi.muxa = atmi.MuxA.FU
            atmi.cbOut0 = self.input0.num
        elif type0 == OpInput:
            atmi.muxa = atmi.MuxA.OP
        else:
            atmi.muxa = atmi.MuxA.RF

        if type1 == FUinput:
            atmi.muxb = atmi.MuxB.FU
            atmi.cbOut1 = self.input1.num
        elif type1 == OpInput:
            atmi.muxb = atmi.MuxB.OP
        else:
            atmi.muxb = atmi.MuxB.RF

        atmi.insts['Op'] = 1

        return atmi
