from typing import Union


class OPInput:
    pass


class FUinput:
    num: int

    def __init__(self, num: int):
        self.num = num


class RFInput:
    pass


class ATAdefinition:
    pass


class ATALoad(ATAdefinition):
    addr0: int
    addr1: int
    cycle: int

    def __init__(self, addr0, addr1, cycle):
        self.addr0 = addr0
        self.addr1 = addr1
        self.cycle = cycle


class ATAStore(ATAdefinition):
    input1: Union[FUinput, OPInput]
    input2: Union[FUinput, OPInput]
    addr0: int
    addr1: int
    cycle: int

    def __init__(self,
                 input1: Union[FUinput, OPInput], input2: Union[FUinput, OPInput],
                 addr0: int, addr1: int,
                 cycle: int):
        self.input1 = input1
        self.input2 = input2
        self.addr0 = addr0
        self.addr1 = addr1
        self.cycle = cycle


class ATAOp(ATAdefinition):
    input1: Union[FUinput, OPInput, RFInput]
    input2: Union[FUinput, OPInput, RFInput]

    def __init__(self, input1, input2):
        self.input1 = input1
        self.input2 = input2
