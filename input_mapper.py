from pygraphviz.agraph import AGraph
from typing import Dict, Tuple


def map_input(fu: AGraph, subgraphs: Dict[str, AGraph], simplified_dfg: AGraph) -> Tuple[Dict[str, int], int]:
    label = fu.graph_attr['label'].strip()
    preds = simplified_dfg.predecessors(label)

    tmp = []
    for pred in preds:
        pred_label = pred.attr['label'].strip()
        if pred_label != label:
            tmp.append(pred.attr['label'])

    tmp.sort()

    out = {}

    i = 0
    for string in tmp:
        for node in subgraphs[string].nodes():
            out[node.get_name()] = i
        i += 1

    return out, i
