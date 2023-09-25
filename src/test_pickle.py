import argparse
import os, pickle


def main(args):
    for g_id in range(args.graph_range):
        print("g id", g_id)
        try:
            with open(os.path.join(args.output, f"{g_id}_config.pkl"), "rb") as f:
                config = pickle.load(f)
                print(config)
            with open(os.path.join(args.output, f"{g_id}.pkl"), "rb") as f:
                graphs = pickle.load(f)
                num_vertex, edge_index, node_feature = graphs
                print("num_vertex", num_vertex)
                print(edge_index.shape)
                print(node_feature.shape)
        except IOError:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str)
    parser.add_argument("--graph-range", type=int, default=100)
    args = parser.parse_args()
    main(args)
