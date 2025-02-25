# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import os, pdb

import pickle, torch

import apache_beam as beam
import dgl
import gin
import numpy as np
from tqdm import tqdm

from ..beam.benchmarker import BenchmarkGNNParDo
from ..beam.generator_beam_handler import GeneratorBeamHandler
from ..metrics.graph_metrics import graph_metrics
from ..metrics.node_label_metrics import NodeLabelMetrics
from ..nodeclassification.utils import (
    get_label_masks,
    nodeclassification_data_to_torchgeo_data,
)


class SampleNodeClassificationDatasetDoFn(beam.DoFn):
    def __init__(self, generator_wrapper):
        self._generator_wrapper = generator_wrapper

    def process(self, sample_id):
        """Sample generator outputs."""
        yield self._generator_wrapper.Generate(sample_id)


class WriteNodeClassificationDatasetDoFn(beam.DoFn):
    def __init__(self, output_path):
        self._output_path = output_path

    def process(self, element):
        sample_id = element["sample_id"]
        config = element["generator_config"]
        datas = element["data"]
        print("-----------------sample graph id", sample_id)
        graphs = []
        for data in tqdm(datas, desc="dump subgraph"):
            edge_index = torch.tensor(data.graph.get_edges()).T
            num_vertex = data.graph.num_vertices()
            # num_edge = data.graph.num_edges()
            node_feature = torch.tensor(data.node_features).float()

            g = dgl.graph((edge_index[0], edge_index[1]), num_nodes=num_vertex)
            g.ndata["feat"] = node_feature.to(torch.float)
            graphs.append(g)

            # print("num_vertex", num_vertex)
            # print("node_feature.shape", node_feature.shape)
            # print("num_edge", num_edge)
            # print("edge_index.shape", edge_index.shape)
        batch_graph = dgl.batch(graphs)
        bg_nodes = batch_graph.num_nodes()
        bg_edges = batch_graph.num_edges()
        max_degree = max(batch_graph.out_degrees()).item()

        print("num_vertex", bg_nodes)
        print("node_feature.shape", g.ndata["feat"].shape)
        print("num_edge", bg_edges)
        print("max degree", max_degree)

        config["max_deg"] = max_degree
        config["nvertex"] = bg_nodes

        print("config", config)
        with open(os.path.join(self._output_path, f"{sample_id}.pkl"), "wb") as file:
            pickle.dump(batch_graph, file)
        with open(
            os.path.join(self._output_path, f"{sample_id}_config.pkl"), "ab"
        ) as f:
            pickle.dump(config, f)
        # # TODO skip edge features
        # with open(os.path.join(self._output_path, f"{sample_id}_config.pkl"), "ab") as f:
        #     pickle.dump(config, f)
        # with open(os.path.join(self._output_path, f"{sample_id}.pkl"), "wb") as f:
        #     pickle.dump([num_vertex, edge_index, node_feature], f)
        # pdb.set_trace()
        # graph_object_name = os.path.join(self._output_path, prefix + "_graph.gt")
        # with beam.io.filesystems.FileSystems.create(graph_object_name) as f:
        #     data.graph.save(f)
        #     f.close()

        # graph_memberships_object_name = os.path.join(
        #     self._output_path, prefix + "_graph_memberships.txt"
        # )
        # with beam.io.filesystems.FileSystems.create(
        #     graph_memberships_object_name, text_mime
        # ) as f:
        #     np.savetxt(f, data.graph_memberships)
        #     f.close()

        # node_features_object_name = os.path.join(
        #     self._output_path, prefix + "_node_features.txt"
        # )
        # with beam.io.filesystems.FileSystems.create(
        #     node_features_object_name, text_mime
        # ) as f:
        #     np.savetxt(f, data.node_features)
        #     f.close()

        # feature_memberships_object_name = os.path.join(
        #     self._output_path, prefix + "_feature_membership.txt"
        # )
        # with beam.io.filesystems.FileSystems.create(
        #     feature_memberships_object_name, text_mime
        # ) as f:
        #     np.savetxt(f, data.feature_memberships)
        #     f.close()

        # edge_features_object_name = os.path.join(
        #     self._output_path, prefix + "_edge_features.txt"
        # )
        # with beam.io.filesystems.FileSystems.create(
        #     edge_features_object_name, text_mime
        # ) as f:
        #     for edge_tuple, features in data.edge_features.items():
        #         buf = bytes(
        #             "{0},{1},{2}".format(edge_tuple[0], edge_tuple[1], features),
        #             "utf-8",
        #         )
        #         f.write(buf)
        #     f.close()


class ComputeNodeClassificationMetrics(beam.DoFn):
    def process(self, element):
        try:
            sample_id = element["sample_id"]
            out = element
            out["metrics"] = graph_metrics(element["data"].graph)
            out["metrics"].update(
                NodeLabelMetrics(
                    element["data"].graph,
                    element["data"].graph_memberships,
                    element["data"].node_features,
                )
            )
        except:
            out["skipped"] = True
            print(
                f"Failed to compute node classification metrics for sample id {sample_id}"
            )
            logging.info(
                ("Failed to convert node classification metrics for sample id %d"),
                sample_id,
            )
            return
        yield out


# class ConvertToTorchGeoDataParDo(beam.DoFn):
#     def __init__(self, output_path, num_train_per_class=5, num_val=5):
#         self._output_path = output_path
#         self._num_train_per_class = num_train_per_class
#         self._num_val = num_val

#     def process(self, element):
#         sample_id = element["sample_id"]
#         nodeclassification_data = element["data"]

#         out = {
#             "sample_id": sample_id,
#             "metrics": element["metrics"],
#             "torch_data": None,
#             "masks": None,
#             "skipped": False,
#             "generator_config": element["generator_config"],
#             "marginal_param": element["marginal_param"],
#             "fixed_params": element["fixed_params"],
#         }

#         try:
#             torch_data = nodeclassification_data_to_torchgeo_data(
#                 nodeclassification_data
#             )
#             out["torch_data"] = torch_data
#             out["gt_data"] = nodeclassification_data.graph

#             torchgeo_stats = {
#                 "nodes": torch_data.num_nodes,
#                 "edges": torch_data.num_edges,
#                 "average_node_degree": torch_data.num_edges / torch_data.num_nodes,
#                 # 'contains_isolated_nodes': torchgeo_data.contains_isolated_nodes(),
#                 # 'contains_self_loops': torchgeo_data.contains_self_loops(),
#                 # 'undirected': bool(torchgeo_data.is_undirected())
#             }
#             stats_object_name = os.path.join(
#                 self._output_path, "{0:05}_torch_stats.txt".format(sample_id)
#             )
#             with beam.io.filesystems.FileSystems.create(
#                 stats_object_name, "text/plain"
#             ) as f:
#                 buf = bytes(json.dumps(torchgeo_stats), "utf-8")
#                 f.write(buf)
#                 f.close()
#         except:
#             out["skipped"] = True
#             print(f"failed to convert {sample_id}")
#             logging.info(
#                 (
#                     "Failed to convert nodeclassification_data to torchgeo"
#                     "for sample id %d"
#                 ),
#                 sample_id,
#             )
#             yield out
#             return

#         try:
#             out["masks"] = get_label_masks(
#                 torch_data.y,
#                 num_train_per_class=self._num_train_per_class,
#                 num_val=self._num_val,
#             )

#             masks_object_name = os.path.join(
#                 self._output_path, "{0:05}_masks.txt".format(sample_id)
#             )
#             with beam.io.filesystems.FileSystems.create(
#                 masks_object_name, "text/plain"
#             ) as f:
#                 for mask in out["masks"]:
#                     np.savetxt(f, np.atleast_2d(mask.numpy()), fmt="%i", delimiter=" ")
#                 f.close()
#         except:
#             out["skipped"] = True
#             print(f"failed masks {sample_id}")
#             logging.info(f"Failed to sample masks for sample id {sample_id}")
#             yield out
#             return

#         yield out


@gin.configurable
class NodeClassificationBeamHandler(GeneratorBeamHandler):
    @gin.configurable
    def __init__(
        self,
        benchmarker_wrappers,
        generator_wrapper,
        num_tuning_rounds=1,
        tuning_metric="",
        tuning_metric_is_loss=False,
        num_train_per_class=20,
        num_val=500,
        save_tuning_results=False,
    ):
        self._sample_do_fn = SampleNodeClassificationDatasetDoFn(generator_wrapper)
        self._benchmark_par_do = BenchmarkGNNParDo(
            benchmarker_wrappers,
            num_tuning_rounds,
            tuning_metric,
            tuning_metric_is_loss,
            save_tuning_results,
        )
        self._metrics_par_do = ComputeNodeClassificationMetrics()
        self._num_train_per_class = num_train_per_class
        self._num_val = num_val
        self._save_tuning_results = save_tuning_results

    def GetSampleDoFn(self):
        return self._sample_do_fn

    def GetWriteDoFn(self):
        return self._write_do_fn

    def GetConvertParDo(self):
        return

    def GetBenchmarkParDo(self):
        return self._benchmark_par_do

    def GetGraphMetricsParDo(self):
        return self._metrics_par_do

    def SetOutputPath(self, output_path):
        self._output_path = output_path
        self._write_do_fn = WriteNodeClassificationDatasetDoFn(output_path)
        # self._convert_par_do = ConvertToTorchGeoDataParDo(
        #     output_path, self._num_train_per_class, self._num_val
        # )
        self._benchmark_par_do.SetOutputPath(output_path)
