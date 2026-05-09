import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def plot_bayes_net(bn):
    """Visualize a given bayesian network by plotting its nodes and edges."""
    G = nx.DiGraph()

    for node in bn.nodes:
        G.add_node(node.name)

    for node in bn.nodes:
        for parent in node.parents:
            G.add_edge(parent.name, node.name)

    plt.figure(figsize=(6, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=3500, font_size=10, arrowsize=20,
            node_color="#A4C8E1", font_weight="bold")
    plt.title("Bayesian Network Structure")
    plt.show()



def plot_cpt_table(node, min_cell_width=0.8, min_cell_height=0.4, font_size=12):
    """
    Visualize a CPT.
    """
    if node.cpt is None:
        print(f"Node {node.name} has no CPT.")
        return

    parents = node.parents
    values = node.values
    cpt = np.array(node.cpt)

    if not parents:
        data = [[round(float(p), 4)] for p in cpt]
        col_labels = [f"P({node.name})"]
        row_labels = [f"{node.name}={v}" for v in values]
        title = f"CPT: {node.name}"
    else:
        parent_shapes = [len(p.values) for p in parents]
        combos = list(np.ndindex(*parent_shapes))

        col_labels = [
            ", ".join(f"{parents[i].name}={combo[i]}" for i in range(len(parents)))
            for combo in combos
        ]
        row_labels = [f"{node.name}={v}" for v in values]
        title = (
            f"CPT: {node.name}  |  Parents: {', '.join(p.name for p in parents)}"
        )

        data = []
        for vi in range(len(values)):
            row = []
            for combo in combos:
                row.append(round(float(cpt[(vi,) + combo]), 4))
            data.append(row)

    longest_col_label = max(len(c) for c in col_labels)
    longest_row_label = max(len(r) for r in row_labels)
    longest_cell_val = max(len(str(v)) for row in data for v in row)

    cell_width = max(min_cell_width, longest_col_label * 0.1, longest_cell_val * 0.1)
    cell_height = max(min_cell_height, longest_row_label * 0.1)

    fig_width = cell_width * len(col_labels) + 3
    fig_height = cell_height * len(row_labels) + 2

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.suptitle(title, fontsize=16, y=0.98, ha="center")

    table = ax.table(
        cellText=data,
        rowLabels=row_labels,
        colLabels=col_labels,
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1.1, 1.3)

    ax.axis("off")
    plt.tight_layout()
    plt.show()



def plot_all_cpt_tables(bn):
    """Plot CPT tables for all nodes with autoscaling."""
    for node in bn.nodes:
        plot_cpt_table(node)

