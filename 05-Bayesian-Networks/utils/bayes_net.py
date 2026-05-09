import numpy as np


class Node:
    """Discrete variable/node for a Bayes net."""
    def __init__(self, name, values=None):
        self.name = name
        self.values = [0, 1] if values is None else list(values)
        self.parents = []
        self.children = []
        self.cpt = None

    def set_parents(self, parents):
        self.parents = list(parents)
        for p in parents:
            if self not in p.children:
                p.children.append(self)

    def set_cpt(self, table, tol=1e-9):
        """Set CPT for the node."""
        arr = np.array(table, dtype=float)
        expected = (len(self.values),) + tuple(len(p.values) for p in self.parents)

        if arr.shape != expected:
            raise ValueError(
                f"Shape error in CPT for {self.name}: expected {expected}, got {arr.shape}"
            )

        axis = tuple(range(1, arr.ndim)) if len(self.parents) > 0 else None

        if axis is None:
            # Root node — single axis sum check
            total = np.sum(arr)
            if not np.isclose(total, 1.0, atol=tol):
                raise ValueError(
                    f"CPT for root {self.name} not normalized: sum={total:.2f}"
                )
        else:
            # Conditional node — verify each parent value configuration
            sum_probs = np.sum(arr, axis=0)
            errors = np.where(~np.isclose(sum_probs, 1.0, atol=tol))

            if errors[0].size > 0:
                msg = f"CPT rows do not sum to 1 for node {self.name}.\n"
                for idx in zip(*errors):
                    parent_info = ", ".join(
                        f"{self.parents[j].name}={idx[j]}"
                        for j in range(len(self.parents))
                    )
                    msg += f"  Parent assignment ({parent_info}) -> sum={sum_probs[idx]:.2f}\n"

                raise ValueError(msg)

        self.cpt = arr


    def __repr__(self):
        return f"Node({self.name}, values={self.values})"


class BayesNet:
    """A Bayesian network (directed acyclic graph of Node objects)."""
    def __init__(self, nodes):
        self.nodes = list(nodes)
        self.name_map = {n.name: n for n in self.nodes}

    def get_node(self, name):
        return self.name_map.get(name)

    def topological_order(self):
        in_degree = {n: len(n.parents) for n in self.nodes}
        queue = [n for n, d in in_degree.items() if d == 0]
        order = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for c in n.children:
                in_degree[c] -= 1
                if in_degree[c] == 0:
                    queue.append(c)
        if len(order) != len(self.nodes):
            raise ValueError("Graph has cycles or disconnected nodes")
        return order

    def __repr__(self):
        return f"BayesNet(nodes={[n.name for n in self.nodes]})"
