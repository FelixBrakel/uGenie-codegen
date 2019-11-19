from ATA import ATAInstruction
from typing import List


class Assembler:
    assembly: List[ATAInstruction]

    def __init__(self):
        self.assembly = []

    def add_assembly(self, assembly: List[ATAInstruction]):
        tmp = assembly
        tmp.sort()

        self.assembly = sorted(tmp + self.assembly)

    def compile(self) -> str:
        pass
