from pygraphviz import AGraph
from typing import List, Tuple, Dict
from input_mapper import map_input
from datatypes import Instruction, parse_instruction
from math import ceil, log2
import glob, sys

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
    control_signal = '        r_i_FU <= \"'
    wait = '        wait for 50 ns;\n'
    zero = str(Input(0, 0, 0))

    curr_c = 0
    for idx, (c, i) in enumerate(inputs):
        for w in range(c - curr_c):
            out += '        -- {}\n'.format(w + curr_c)
            out += wait
        curr_c = c
        out += control_signal + i + '\";\n'

        if len(inputs) > idx + 1:
            c_tmp, i_tmp = inputs[idx + 1]
            if c_tmp != c + 1:
                out += '        -- {}\n'.format(curr_c)
                out += wait
                out += control_signal + zero + '\";\n'
                curr_c += 1
        else:
            out += '        -- {}\n'.format(curr_c)
            out += wait
            out += control_signal + zero + '\";\n'
            curr_c += 1

    for i in range(end_cycle - curr_c):
        out += '        -- {}\n'.format(i + curr_c)
        out += wait

    return out


def main(architecture):
    # architecture = '148'
    dfg = parser('../dotfiles/Architecture_latency_{}.dot'.format(architecture))
    simplified_dfg = parser('../dotfiles/Architecture_latency_{}_schematic.dot'.format(architecture))
    tot_cycles = 0
    fus: List[AGraph] = dfg.subgraphs()

    subgraphs = {}
    for subgraph in fus:
        subgraphs[subgraph.graph_attr['label'].strip()] = subgraph

    for filename in glob.glob('../out/*.program'):
        fu = filename.split('/')[-1]
        fu = fu.split('.')[0]

        vhdl_body = ''
        with open(filename) as file:
            for line in file:
                if line == '\n':
                    vhdl_body += FU_ADD_MID
                    continue
                if 'TOTAL_WAIT_NS' in line:
                    tot_wait = line.split(' ')[-1].strip()
                    continue
                if 'BITWIDTH' in line:
                    if 'add' in filename:
                        Input.bitwidth = int(line.split('=>')[-1].strip(',\n')) + 1
                    else:
                        Input.bitwidth = int((int(line.split('=>')[-1].strip(',\n')) + 1) / 2)
                if 'INPUT_PORTS' in line:
                    Input.input_ports = int(line.split('=>')[-1].strip(',\n'))
                if 'TOTAL_EXE_CYCLES' in line:
                    tot_cycles = int(line.split('=>')[-1].strip(',\n'))
                if 'RF_DEPTH' in line:
                    rf_depth = int(line.split('=>')[-1].strip(',\n'))

                vhdl_body += line

        i_size = int(ceil(log2(tot_cycles + 1))) + \
                 int(ceil(log2(Input.input_ports))) * 3 + \
                 2 + \
                 int(ceil(log2(rf_depth + 1))) * 4 + \
                 4 - \
                 1

        if 'add' in filename:
            head = FU_ADD_HEAD.format(FU=fu + '_tb', PORTS=str(Input.input_ports), I_SIZE=str(i_size))
            foot = FU_ADD_FOOT
            call = gen_add_input
        else:
            head = FU_MUL_HEAD.format(FU=fu + '_tb', PORTS=str(Input.input_ports), I_SIZE=str(i_size))
            foot = FU_MUL_FOOT
            call = gen_mul_input

        vhdl_out = head + vhdl_body

        input_map, _ = map_input(subgraphs[fu], subgraphs, simplified_dfg)
        inputs, outputs = call(dfg, subgraphs[fu], input_map)
        input_strs = merge_inputs(inputs)
        formatted_input = insert_inputs(input_strs, tot_cycles)
        vhdl_out += formatted_input + foot
        with open('../vhdl_work_dir/' + fu.split('.program')[0] + '_tb.vhd', 'w') as file:
            file.write(vhdl_out)

        with open(filename.split('.program')[0] + '.out', 'w') as file:
            file.write(tot_wait + '\n')
            for out in outputs:
                file.write(str(out) + '\n')


def gen_add_input(dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> Tuple[List[Input], List[Output]]:
    outputs: List[Output] = []
    inputs: List[Input] = []
    nodes: List[Instruction] = []
    for node in fu.nodes():
        nodes.append(parse_instruction(node))

    nodes.sort()
    exp = 0
    for node in nodes:
        preds = dfg.predecessors(node.name)
        parent0 = parse_instruction(preds[0])
        parent1 = parse_instruction(preds[1])

        if parent0.name in input_map:
            label = dfg.get_node(parent0.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i0 = 2**exp
            inputs.append(Input(i0, input_map[parent0.name], parent0.cycle + latency))
        else:
            for output in outputs:
                if output.cycle == parent0.cycle + 1:
                    i0 = output.val
                    break

        if parent1.name in input_map:
            label = dfg.get_node(parent1.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i1 = 2**exp
            inputs.append(Input(i1, input_map[parent1.name], parent1.cycle + latency))
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


def gen_add_input2(dfg: AGraph, fu: AGraph, input_map: Dict[str, int]) -> Tuple[List[Input], List[Output]]:
    outputs: List[Output] = []
    inputs: List[Input] = []
    nodes: List[Instruction] = []
    for node in fu.nodes():
        nodes.append(parse_instruction(node))

    nodes.sort()
    prev_o = 0
    for node in nodes:
        preds = dfg.predecessors(node.name)
        parent0 = parse_instruction(preds[0])
        parent1 = parse_instruction(preds[1])

        if parent0.name in input_map:
            label = dfg.get_node(parent0.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i0 = prev_o + 1
            inputs.append(Input(i0, input_map[parent0.name], parent0.cycle + latency))
        else:
            for output in outputs:
                if output.cycle == parent0.cycle + 1:
                    i0 = output.val
                    break

        if parent1.name in input_map:
            label = dfg.get_node(parent1.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i1 = prev_o + 1
            inputs.append(Input(i1, input_map[parent1.name], parent1.cycle + latency))
        else:
            for output in outputs:
                if output.cycle == parent1.cycle + 1:
                    i1 = output.val
                    break

        expected = i0 + i1
        prev_o = expected
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
            label = dfg.get_node(parent0.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i0 = PRIMES[prime_idx]
            prime_idx += 1
            inputs.append(Input(i0, input_map[parent0.name], parent0.cycle + latency))
        else:
            for output in outputs:
                if output.cycle == parent0.cycle + 2:
                    i0 = output.val
                    break

        if parent1.name in input_map:
            label = dfg.get_node(parent1.name).attr['label']
            if 'mul' in label:
                latency = 2
            else:
                latency = 1

            i1 = PRIMES[prime_idx]
            prime_idx += 1
            inputs.append(Input(i1, input_map[parent1.name], parent1.cycle + latency))
        else:
            for output in outputs:
                if output.cycle == parent1.cycle + 2:
                    i1 = output.val
                    break

        expected = i0 * i1
        outputs.append(Output(expected, node.cycle + 1))

    inputs.sort()
    return inputs, outputs


def parser(architecture_file_path: str) -> AGraph:
    return AGraph(architecture_file_path)


if __name__ == '__main__':
    main(sys.argv[1])
