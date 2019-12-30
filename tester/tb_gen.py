from pygraphviz import AGraph
from typing import List, Tuple, Dict
from input_mapper import map_input
from datatypes import Instruction, parse_instruction
import glob

with open('../vhdl_template/FU_ADD_HEAD') as f:
    FU_ADD_HEAD = f.read()

with open('../vhdl_template/FU_ADD_MID') as f:
    FU_ADD_MID = f.read()

with open('../vhdl_template/FU_ADD_FOOT') as f:
    FU_ADD_FOOT = f.read()

with open('../vhdl_template/FU_MUL_HEAD') as f:
    FU_MUL_HEAD = f.read()

with open('../vhdl_template/FU_MUL_MID') as f:
    FU_MUL_MID = f.read()

with open('../vhdl_template/FU_MUL_FOOT') as f:
    FU_MUL_FOOT = f.read()

with open('primes') as f:
    PRIMES: List[int] = [int(i) for i in f.read().split(',')]


class MergeException(Exception):
    pass


class Output:
    def __init__(self, val, cycle):
        self.val = val
        self.cycle = cycle

    def __str__(self) -> str:
        return '{},{}'.format(self.val, self.cycle)


class Input:
    input_ports = 0
    bitwidth = 0

    def __init__(self, val: int, port: int, cycle: int):
        self.vals: List[int] = [0] * Input.input_ports
        self.vals[port] = val
        # NOTE: super weird way to store this value since it can actually hold multilpe ports, should be fine as long
        #  as it is only used for unmerged inputs
        self.port = port
        self.cycle: int = cycle

    def __lt__(self, other):
        return self.cycle < other.cycle

    def __str__(self) -> str:
        field = ''
        for val in self.vals:
            field += '{:0{bits}b}'.format(val, bits=Input.bitwidth)

        return field


def merge_inputs(inputs: List[Input]) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []

    tmp: List[Input] = [inputs[0]]

    for i in inputs[1:]:
        t = tmp[-1]
        if t.cycle == i.cycle:
            if t.vals[i.port] != 0:
                raise MergeException('Cannot merge input occuring at same port: ' + str(t.port))
            else:
                t.vals[i.port] = i.vals[i.port]
        else:
            tmp.append(i)

    for i in tmp:
        out.append((i.cycle, str(i)))

    return out


def insert_inputs(inputs: List[Tuple[int, str]], end_cycle) -> str:
    out: str = ''
    control_signal = '        r_i_FU <= '
    wait = '        wait 50 ns;\n'

    curr_c = 1
    for (c, i) in inputs:
        for w in range(c - curr_c):
            out += wait
        curr_c = c
        out += control_signal + i + '\n'

    for i in range(end_cycle - curr_c):
        out += wait

    return out


def main():
    dfg = parser('../dotfiles/Architecture_latency_146.dot')
    simplified_dfg = parser('../dotfiles/Architecture_latency_146_schematic.dot')
    tot_cycles = 0
    fus: List[AGraph] = dfg.subgraphs()

    subgraphs = {}
    for subgraph in fus:
        subgraphs[subgraph.graph_attr['label'].strip()] = subgraph

    for filename in glob.glob('../out/*.program'):
        vhdl_out = ''
        if 'add' in filename:
            head = FU_ADD_HEAD
            mid = FU_ADD_MID
            foot = FU_ADD_FOOT
            call = gen_add_input
        else:
            continue
            head = FU_MUL_HEAD
            mid = FU_MUL_MID
            foot = FU_MUL_FOOT
            call = gen_mul_input

        vhdl_out += head

        with open(filename) as file:
            for line in file:
                if line == '\n':
                    vhdl_out += mid
                    continue
                if 'BITWIDTH' in line:
                    Input.bitwidth = int(line.split('=>')[-1].strip()) + 1
                if 'INPUT_PORTS' in line:
                    Input.input_ports = int(line.split('=>')[-1].strip())
                if 'TOTAL_EXE_CYCLES' in line:
                    tot_cycles = int(line.split('=>')[-1].strip())
                vhdl_out += line

        fu = filename.split('/')[-1]
        fu = fu.split('.')[0]
        input_map, _ = map_input(subgraphs[fu], subgraphs, simplified_dfg)
        inputs, outputs = call(dfg, subgraphs[fu], input_map)
        input_strs = merge_inputs(inputs)
        formatted_input = insert_inputs(input_strs, tot_cycles)
        vhdl_out += formatted_input + foot
        with open(filename + '_tb.vhd', 'w') as file:
            file.write(vhdl_out)

        with open(filename + '.out', 'w') as file:
            for out in outputs:
                file.write(str(out) + '\n')
        # print(vhdl_out)
        # exit(2)

    # build_dir = '../BSc_Project_Material/vhdl/build/'
    #
    # xsim = subprocess.Popen(['xsim', build_dir + 'work.FU_template_tb', '-tclbatch', 'tmp.tcl'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # out = xsim.communicate()
    # print(out)
    #
    # if xsim.poll() is None:
    #     print('terminating')
    #     xsim.terminate()


def gen_add_input(dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> Tuple[List[Input], List[Output]]:
    outputs: List[Output] = []
    inputs: List[Input] = []
    nodes: List[Instruction] = []
    for node in fu.nodes():
        nodes.append(parse_instruction(node))

    nodes.sort()
    exp = 1
    for node in nodes:
        preds = dfg.predecessors(node.name)
        parent0 = parse_instruction(preds[0])
        parent1 = parse_instruction(preds[1])

        if parent0.name in input_map:
            i0 = 2**exp
            inputs.append(Input(i0, input_map[parent0.name], parent0.cycle))
        else:
            for output in outputs:
                if output.cycle == parent0.cycle + 1:
                    i0 = output.val
                    break

        if parent1.name in input_map:
            i1 = 2**exp
            inputs.append(Input(i1, input_map[parent1.name], parent1.cycle))
        else:
            for output in outputs:
                if output.cycle == parent1.cycle + 1:
                    i1 = output.val
                    break

        exp += 1

        expected = i0 + i1
        outputs.append(Output(expected, node.cycle + 1))

    inputs.sort()
    return inputs, outputs


def gen_mul_input(dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> Tuple[List[Input], List[Output]]:
    outputs: List[Output] = []
    inputs: List[Input] = []
    nodes: List[Instruction] = []

    for node in fu.nodes():
        nodes.append(parse_instruction(node))

    nodes.sort()
    prime_idx = 0
    for node in nodes:
        preds = dfg.predecessors(node.name)
        parent0 = parse_instruction(preds[0])
        parent1 = parse_instruction(preds[1])

        if parent0.name in input_map:
            i0 = PRIMES[prime_idx]
            prime_idx += 1
            inputs.append(Input(i0, input_map[parent0.name], parent0.cycle))
        else:
            for output in outputs:
                if output.cycle == parent0.cycle + 2:
                    i0 = output.val
                    break

        if parent1.name in input_map:
            i1 = PRIMES[prime_idx]
            prime_idx += 1
            inputs.append(Input(i1, input_map[parent1.name], parent1.cycle))
        else:
            for output in outputs:
                if output.cycle == parent1.cycle + 2:
                    i1 = output.val
                    break

        expected = i0 * i1
        outputs.append(Output(expected, node.cycle + 2))

    inputs.sort()
    return inputs, outputs


def parser(architecture_file_path: str) -> AGraph:
    return AGraph(architecture_file_path)


if __name__ == '__main__':
    main()
