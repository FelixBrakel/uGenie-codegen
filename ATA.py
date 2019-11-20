from __future__ import annotations
from typing import Union, Optional, List
from enum import Enum


class ValueOutOfRangeException(Exception):
    pass


class MergeException(Exception):
    pass


class ATMI:
    class MuxA(Enum):
        OP = 0
        FU = 1
        RF = 2

    class MuxB(Enum):
        FU = 0
        RF = 1
        OP = 2

    def __init__(self, rf_depth: int, input_ports: int, total_exe_cycles: int):
        self._rf_depth: int = rf_depth
        self._input_ports: int = input_ports
        self._total_exe_cycles: int = total_exe_cycles
        self.insts = {'Fetch': 0, 'Store': 0, 'Op': 0}

        self.cycle: int = 0
        self.cbOut0: Optional[int] = None
        self.cbOut1: Optional[int] = None
        self.cbOut2: Optional[int] = None
        self.reg0: bool = False
        self.reg1: bool = False
        self.r_reg0_s: Optional[int] = None
        self.r_reg1_s: Optional[int] = None
        self.w_reg0_s: Optional[int] = None
        self.w_reg1_s: Optional[int] = None
        self.muxa: Optional[ATMI.MuxA] = None
        self.muxb: Optional[ATMI.MuxB] = None

    @property
    def cycle(self):
        return self.cycle

    @cycle.setter
    def cycle(self, cycle: int):
        if 0 <= cycle <= self._total_exe_cycles:
            raise ValueOutOfRangeException('cycle')
        else:
            self.cycle = cycle

    @property
    def cbOut0(self):
        return self.cbOut0

    @cbOut0.setter
    def cbOut0(self, cbOut0: int):
        if 0 <= cbOut0 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut0')
        else:
            self.cbOut0 = cbOut0

    @property
    def cbOut1(self):
        return self.cbOut1

    @cbOut1.setter
    def cbOut1(self, cbOut1: int):
        if 0 <= cbOut1 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut1')
        else:
            self.cbOut1 = cbOut1

    @property
    def cbOut2(self):
        return self.cbOut2

    @cbOut2.setter
    def cbOut2(self, cbOut2: int):
        if 0 <= cbOut2 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut2')
        else:
            self.cbOut2 = cbOut2

    @property
    def r_reg0_s(self):
        return self.r_reg0_s

    @r_reg0_s.setter
    def r_reg0_s(self, r_reg0_s: int):
        if 0 <= r_reg0_s <= self._rf_depth:
            raise ValueOutOfRangeException('r_reg0_s')

    @property
    def r_reg1_s(self):
        return self.r_reg1_s

    @r_reg1_s.setter
    def r_reg1_s(self, r_reg1_s: int):
        if 0 <= r_reg1_s <= self._rf_depth:
            raise ValueOutOfRangeException('r_reg1_s')

    @property
    def w_reg0_s(self):
        return self.w_reg0_s

    @w_reg0_s.setter
    def w_reg0_s(self, w_reg0_s: int):
        if 0 <= w_reg0_s <= self._rf_depth:
            raise ValueOutOfRangeException('w_reg0_s')

    @property
    def w_reg1_s(self):
        return self.w_reg1_s

    @w_reg1_s.setter
    def w_reg1_s(self, w_reg1_s: int):
        if 0 <= w_reg1_s <= self._rf_depth:
            raise ValueOutOfRangeException('w_reg1_s')

    def _merge_op(self, other: ATMI):
        pass

    def _merge_fetch(self, other: ATMI):
        pass

    # TODO: This code looks very error-prone should be able to simplify if needed
    def _merge_store(self, other: ATMI):
        # NOTE: This should never happen, we checked for this in the 'mergo_into' function
        if self.reg0 and self.reg1:
            raise MergeException('Cannot merge more than 2 store instructions')

        if other.reg0:
            if self.reg0:
                raise MergeException('Cannot merge 2 store ops for reg0')
            else:
                # NOTE: This should never happen, if reg0 is not set, neither should cbOut2
                if self.cbOut2 is not None:
                    raise MergeException('Cannot merge 2 store ops which both take input from FUs')

                self.cbOut2 = other.cbOut2
                self.reg0 = True
                self.w_reg0_s = other.w_reg0_s
                self.insts['Store'] += 1

        if other.reg1:
            if self.reg1:
                raise MergeException('Cannot merge 2 store ops for reg1')
            else:
                self.reg1 = True
                self.w_reg1_s = other.w_reg1_s
                self.insts['Store'] += 1

    def merge_into(self, other: ATMI):
        if self.cycle != other.cycle:
            raise MergeException('Instructions do not occur at the same cycle')

        n_fetch = self.insts['Fetch'] + other.insts['Fetch']
        n_store = self.insts['Store'] + other.insts['Store']
        n_ops = self.insts['Op'] + other.insts['Op']

        if n_fetch > 2:
            raise MergeException('Cannot merge more than 2 fetch instructions')
        if n_store > 2:
            raise MergeException('Cannot merge more than 2 store instructions')
        if n_ops > 1:
            raise MergeException('Cannot merge more than 1 op instructions')

        if other.insts['Fetch'] > 0:
            self._merge_fetch(other)
        if other.insts['Store'] > 0:
            self._merge_store(other)
        if other.insts['Op'] > 0:
            self._merge_op(other)


class OPInput:
    pass


class FUinput:
    # TODO: make sure this num value doesn't go out of range
    def __init__(self, num: int):
        self.num: int = num


class RFInput:
    pass


class ATAInstruction:
    def __init__(self, cycle: int):
        self.cycle: int = cycle

    def __lt__(self, other):
        return self.cycle < other.cycle


class ATAFetch(ATAInstruction):
    class REG(Enum):
        REG0 = 0
        REG1 = 1

    def __init__(self, addr: int, reg: REG, cycle: int):
        super().__init__(cycle)
        self.addr: int = addr
        self.reg: ATAFetch.REG = reg
        # super.cycle = cycle


class ATAStore(ATAInstruction):
    def __init__(self,
                 inp: Union[FUinput, OPInput],
                 addr: int,
                 cycle: int):
        super().__init__(cycle)
        self.input: Union[FUinput, OPInput] = inp
        self.addr: int = addr


class ATAOp(ATAInstruction):
    def __init__(self, input0: Union[FUinput, OPInput, RFInput], input1: Union[FUinput, OPInput, RFInput], cycle: int):
        super().__init__(cycle)
        self.input0: Union[FUinput, OPInput, RFInput] = input0
        self.input1: Union[FUinput, OPInput, RFInput] = input1
