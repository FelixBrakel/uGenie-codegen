import networkx as nx
import pygraphviz


def main():
    with open('dotfiles/Architecture_latency_146.dot', 'r') as file:
        data = file.read().replace('\n', '')
    # print(data)
    # tmp = nx.nx_agraph.read_dot('dotfiles/Architecture_latency_146.dot')
    agraph = pygraphviz.AGraph('dotfiles/Architecture_latency_146.dot')
    functional_units = agraph.subgraphs()
    label = functional_units[0].graph_attr['label']

    print(label)

    # tmp = nx.nx_agraph.from_agraph(agraph)
    # tmp2 = nx.nx_agraph.to_agraph(tmp)
    # tmp2.layout(prog='dot')
    # tmp2.draw('file.png')
    # plt.show()


if __name__ == '__main__':
    main()
