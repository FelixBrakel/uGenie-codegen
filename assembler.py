from ATA import ATAInstruction
from typing import List


class Assembler:
    def __init__(self):
        self.assembly: List[ATAInstruction] = []

    def add_assembly(self, assembly: List[ATAInstruction]):
        tmp = assembly
        tmp.sort()

        self.assembly = sorted(tmp + self.assembly)

    def compile(self) -> str:
        for inst in self.assembly:
            pass

        return ''
