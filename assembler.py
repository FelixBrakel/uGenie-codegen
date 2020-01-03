from ata import ATAI
from typing import List

from atmi import ATMI


class Assembler:
    def __init__(self):
        self.assembly: List[ATAI] = []
        self.atmc: List[ATMI] = []

    def add_assembly(self, assembly: List[ATAI]):
        tmp = assembly
        tmp.sort()

        self.assembly = sorted(tmp + self.assembly)

    def compile(self, max_address: int, max_fu: int):
        self.atmc.append(self.assembly[0].to_atmi(max_address, max_fu))
        for inst in self.assembly[1:]:
            atmi = inst.to_atmi(max_address, max_fu)
            if inst.cycle == self.atmc[-1].cycle:
                self.atmc[-1].merge_into(atmi)
            else:
                self.atmc.append(atmi)

    def print(self):
        output = '{:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8} {:8}\n'.format('cycle',
                                                                                        'cbOut0',
                                                                                        'cbOut1',
                                                                                        'cbOut2',
                                                                                        'reg0',
                                                                                        'reg1',
                                                                                        'r_reg0_s',
                                                                                        'r_reg1_s',
                                                                                        'w_reg0_s',
                                                                                        'w_reg1_s',
                                                                                        'muxa',
                                                                                        'muxb')
        for atmi in self.atmc:
            output += str(atmi) + '\n'

        print(output)

    def export(self) -> List[str]:
        out = []

        for atmi in self.atmc:
            out.append(atmi.to_bitstring())

        return out
