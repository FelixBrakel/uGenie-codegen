from __future__ import annotations
from enum import Enum
from typing import Optional
from math import log2, ceil


class MergeException(Exception):
    pass


class ValueOutOfRangeException(Exception):
    pass


class ATMI:
    max_cycle: int = 0
    # TODO: These static variables should be set in the main loop for every FU. At the moment it is not clear if
    #  these can be read from a file or need to be determined at runtime
    # rf_depth: int
    # input_ports: int

    class MuxA(Enum):
        OP = 0
        FU = 1
        RF = 2

    class MuxB(Enum):
        OP = 0
        FU = 1
        RF = 2

    def __init__(self, rf_depth: int, max_port: int):
        self._rf_depth: int = rf_depth
        self._max_port: int = max_port
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
        if cycle > ATMI.max_cycle:
            ATMI.max_cycle = cycle

    @property
    def cbOut0(self):
        return self._cbOut0

    @cbOut0.setter
    def cbOut0(self, cbOut0: int):
        if not 0 <= cbOut0 <= self._max_port:
            raise ValueOutOfRangeException('cbOut0: ' + str(cbOut0) + ', max: ' + str(self._max_port))
        else:
            self._cbOut0 = cbOut0

    @property
    def cbOut1(self):
        return self._cbOut1

    @cbOut1.setter
    def cbOut1(self, cbOut1: int):
        if not 0 <= cbOut1 <= self._max_port:
            raise ValueOutOfRangeException('cbOut1: ' + str(cbOut1) + ', max: ' + str(self._max_port))
        else:
            self._cbOut1 = cbOut1

    @property
    def cbOut2(self):
        return self._cbOut2

    @cbOut2.setter
    def cbOut2(self, cbOut2: int):
        if not 0 <= cbOut2 <= self._max_port:
            raise ValueOutOfRangeException('cbOut2: ' + str(cbOut2) + ', max: ' + str(self._max_port))
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
        if self.muxb is not None:
            raise MergeException('Muxb for Op instruction is already set')

        # NOTE: These should never occur since the muxa and muxb checks should also cover these
        if other.cbOut0 is not None:
            if self.cbOut0 is not None:
                raise MergeException('')
            else:
                self.cbOut0 = other.cbOut0

        # NOTE: We raise an execption because the merge has failed but we still could have possibly set cbOut0,
        #  we might have to unset it if we want to do something else with this ATMI object later.
        if other.cbOut1 is not None:
            if self.cbOut1 is not None:
                raise MergeException('')
            else:
                self.cbOut1 = other.cbOut1

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

    def _debug_str_helper(self, x):
        if x is None:
            return "None"

        return x

    def _str_helper(self, x):
        if x is None:
            return 0

        if type(x) is self.MuxA or type(x) is self.MuxB:
            return x.value

        if type(x) is bool:
            if x:
                return 1

            return 0

        return x

    def __str__(self) -> str:
        cycle = self._debug_str_helper(self.cycle)
        cbOut0 = self._debug_str_helper(self.cbOut0)
        cbOut1 = self._debug_str_helper(self.cbOut1)
        cbOut2 = self._debug_str_helper(self.cbOut2)
        reg0 = self._debug_str_helper(self.reg0)
        reg1 = self._debug_str_helper(self.reg1)
        r_reg0_s = self._debug_str_helper(self.r_reg0_s)
        r_reg1_s = self._debug_str_helper(self.r_reg1_s)
        w_reg0_s = self._debug_str_helper(self.w_reg0_s)
        w_reg1_s = self._debug_str_helper(self.w_reg1_s)
        muxa = self._debug_str_helper(self.muxa)
        muxb = self._debug_str_helper(self.muxb)

        return '{:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8}'.format(cycle,
                                                                                                cbOut0,
                                                                                                cbOut1,
                                                                                                cbOut2,
                                                                                                reg0,
                                                                                                reg1,
                                                                                                r_reg0_s,
                                                                                                r_reg1_s,
                                                                                                w_reg0_s,
                                                                                                w_reg1_s,
                                                                                                muxb,
                                                                                                muxa)

    def to_bitstring(self) -> str:
        rf_bits = max(int(ceil(log2(self._rf_depth + 1))), 1)
        clock_bits = int(ceil(log2(self.max_cycle + 1)))
        fu_bits = int(ceil(log2(self._max_port + 1)))

        return '' \
               '{:0{clk}b}' \
               '{:0{fu}b}' \
               '{:0{fu}b}' \
               '{:0{fu}b}' \
               '{:1b}' \
               '{:1b}' \
               '{:0{rf}b}' \
               '{:0{rf}b}' \
               '{:0{rf}b}' \
               '{:0{rf}b}' \
               '{:02b}' \
               '{:02b}' \
               ''.format(self._str_helper(self.cycle),
                         self._str_helper(self.cbOut0),
                         self._str_helper(self.cbOut1),
                         self._str_helper(self.cbOut2),
                         self._str_helper(self.reg0),
                         self._str_helper(self.reg1),
                         self._str_helper(self.r_reg0_s),
                         self._str_helper(self.r_reg1_s),
                         self._str_helper(self.w_reg0_s),
                         self._str_helper(self.w_reg1_s),
                         self._str_helper(self.muxb),
                         self._str_helper(self.muxa),
                         clk=clock_bits,
                         fu=fu_bits,
                         rf=rf_bits)
