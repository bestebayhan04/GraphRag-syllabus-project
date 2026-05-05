import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx


TRIPLES_FOLDER = "outputs/triples"
OUTPUT_IMAGE = "outputs/graph.png"


def load_all_triples(folder_path: str) -> List[Dict[str, str]]:
    all_triples = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            path = os.path.join(folder_path, filename)

            with open(path, "r", encoding="utf-8") as file:
                triples = json.load(file)

                if isinstance(triples, list):
                    all_triples.extend(triples)

    return all_triples


def build_graph(triples: List[Dict[str, str]]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for triple in triples:
        subject = triple["subject"]
        relation = triple["relation"]
        object_ = triple["object"]

        graph.add_node(subject)
        graph.add_node(object_)
        graph.add_edge(subject, object_, label=relation)

    return graph


def save_graph_image(graph: nx.DiGraph, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(18, 12))

    pos = nx.spring_layout(graph, k=0.8, iterations=80, seed=42)

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=2500,
        font_size=8,
        arrows=True,
        arrowsize=15,
    )

    edge_labels = nx.get_edge_attributes(graph, "label")

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=7,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved graph image: {output_path}")


def main() -> None:
    triples = load_all_triples(TRIPLES_FOLDER)

    print(f"Loaded triples: {len(triples)}")

    graph = build_graph(triples)

    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    save_graph_image(graph, OUTPUT_IMAGE)


if __name__ == "__main__":
    main()