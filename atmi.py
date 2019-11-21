from __future__ import annotations
from enum import Enum
from typing import Optional


class MergeException(Exception):
    pass


class ValueOutOfRangeException(Exception):
    pass


class ATMI:
    max_cycle: int = 0

    class MuxA(Enum):
        OP = 0
        FU = 1
        RF = 2

    class MuxB(Enum):
        FU = 0
        RF = 1
        OP = 2

    def __init__(self, rf_depth: int, input_ports: int):
        self._rf_depth: int = rf_depth
        self._input_ports: int = input_ports
        # self._total_exe_cycles: int = total_exe_cycles
        self.insts = {'Fetch': 0, 'Store': 0, 'Op': 0}

        self._cycle: int = 0
        self._cbOut0: Optional[int] = None
        self._cbOut1: Optional[int] = None
        self._cbOut2: Optional[int] = None
        self.reg0: bool = False
        self.reg1: bool = False
        self._r_reg0_s: Optional[int] = None
        self._r_reg1_s: Optional[int] = None
        self._w_reg0_s: Optional[int] = None
        self._w_reg1_s: Optional[int] = None
        self.muxa: Optional[ATMI.MuxA] = None
        self.muxb: Optional[ATMI.MuxB] = None

    @property
    def cycle(self):
        return self._cycle

    @cycle.setter
    def cycle(self, cycle: int):
        self._cycle = cycle
        if cycle > self.max_cycle:
            self.max_cycle = cycle

    @property
    def cbOut0(self):
        return self._cbOut0

    @cbOut0.setter
    def cbOut0(self, cbOut0: int):
        if not 0 <= cbOut0 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut0')
        else:
            self._cbOut0 = cbOut0

    @property
    def cbOut1(self):
        return self._cbOut1

    @cbOut1.setter
    def cbOut1(self, cbOut1: int):
        if not 0 <= cbOut1 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut1')
        else:
            self._cbOut1 = cbOut1

    @property
    def cbOut2(self):
        return self._cbOut2

    @cbOut2.setter
    def cbOut2(self, cbOut2: int):
        if not 0 <= cbOut2 <= self._input_ports:
            raise ValueOutOfRangeException('cbOut2')
        else:
            self._cbOut2 = cbOut2

    @property
    def r_reg0_s(self):
        return self._r_reg0_s

    @r_reg0_s.setter
    def r_reg0_s(self, r_reg0_s: int):
        if not 0 <= r_reg0_s <= self._rf_depth:
            raise ValueOutOfRangeException('r_reg0_s')

        self._r_reg0_s = r_reg0_s

    @property
    def r_reg1_s(self):
        return self._r_reg1_s

    @r_reg1_s.setter
    def r_reg1_s(self, r_reg1_s: int):
        if not 0 <= r_reg1_s <= self._rf_depth:
            raise ValueOutOfRangeException('r_reg1_s')

        self._r_reg1_s = r_reg1_s

    @property
    def w_reg0_s(self):
        return self._w_reg0_s

    @w_reg0_s.setter
    def w_reg0_s(self, w_reg0_s: int):
        if not 0 <= w_reg0_s <= self._rf_depth:
            raise ValueOutOfRangeException('w_reg0_s')

        self._w_reg0_s = w_reg0_s

    @property
    def w_reg1_s(self):
        return self._w_reg1_s

    @w_reg1_s.setter
    def w_reg1_s(self, w_reg1_s: int):
        if not 0 <= w_reg1_s <= self._rf_depth:
            raise ValueOutOfRangeException('w_reg1_s')

        self._w_reg1_s = w_reg1_s

    def _merge_op(self, other: ATMI):
        # NOTE: Neither of these should ever happen because we check for it in the merge_into function
        if self.muxa is not None:
            raise MergeException('Muxa for Op instruction is already set')
        elif self.muxb is not None:
            raise MergeException('Muxb for Op instruction is already set')

        self.muxa = other.muxa
        self.muxb = other.muxb

        self.insts['Op'] += 1

    def _merge_fetch(self, other: ATMI):
        if other.r_reg0_s is not None:
            if self.r_reg0_s is not None:
                raise MergeException('r_reg0_s for Fetch instruction is already set')

            self.r_reg0_s = other.r_reg0_s
            self.insts['Fetch'] += 1

        if other.r_reg1_s is not None:
            if self.r_reg1_s is not None:
                raise MergeException('r_reg1_s for Fetch instruction is already set')

            self.r_reg1_s = other.r_reg1_s
            self.insts['Fetch'] += 1

    # TODO: This code looks very error-prone should be able to simplify if needed, it might be easier to merge
    #  an ATAI instead
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

    def str_helper(self, x):
        if x is None:
            return "None"

        return x

    def __str__(self):
        cycle = self.str_helper(self.cycle)
        cbOut0 = self.str_helper(self.cbOut0)
        cbOut1 = self.str_helper(self.cbOut1)
        cbOut2 = self.str_helper(self.cbOut2)
        reg0 = self.str_helper(self.reg0)
        reg1 = self.str_helper(self.reg1)
        r_reg0_s = self.str_helper(self.r_reg0_s)
        r_reg1_s = self.str_helper(self.r_reg1_s)
        w_reg0_s = self.str_helper(self.w_reg0_s)
        w_reg1_s = self.str_helper(self.w_reg1_s)
        muxa = self.str_helper(self.muxa)
        muxb = self.str_helper(self.muxb)

        return '{:7} {:7} {:7} {:7} {:7} {:7} {:7} {:7} {:7} {:7} {:7} {:7}'.format(cycle,
                                                                                    cbOut0,
                                                                                    cbOut1,
                                                                                    cbOut2,
                                                                                    reg0,
                                                                                    reg1,
                                                                                    r_reg0_s,
                                                                                    r_reg1_s,
                                                                                    w_reg0_s,
                                                                                    w_reg1_s,
                                                                                    muxa,
                                                                                    muxb)
