# Copyright 2022 Google LLC
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

# FROM continuumio/miniconda3
FROM nvcr.io/nvidia/pytorch:23.03-py3


RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o ~/miniconda.sh \
    && sh ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh


ENV PATH /opt/conda/bin:$PATH
RUN conda update conda
# RUN conda update -n base -c defaults conda
RUN conda create --name gt -c conda-forge graph-tool python=3.8 
# RUN conda update conda -y \
	# && conda create --name gt -c conda-forge graph-tool python=3.8 
RUN conda init bash
SHELL ["conda", "run", "-n", "gt", "/bin/bash", "-c"]
# RUN conda activate gt
RUN /opt/conda/envs/gt/bin/pip install torch torchvision torchaudio
RUN echo "conda activate gt" >> ~/.bashrc

RUN /opt/conda/envs/gt/bin/pip install ogb \
        && /opt/conda/envs/gt/bin/pip install rdkit \
        && /opt/conda/envs/gt/bin/pip install cython \
        && /opt/conda/envs/gt/bin/pip install networkit \
        && /opt/conda/envs/gt/bin/pip install pandas \
        && /opt/conda/envs/gt/bin/pip install psutil \
        && /opt/conda/envs/gt/bin/pip install seaborn \
        && /opt/conda/envs/gt/bin/pip install apache-beam \
        && /opt/conda/envs/gt/bin/pip install gin-config \
        && /opt/conda/envs/gt/bin/pip install torch_geometric


ENV DGL_HOME=/workspace2/dgl
ENV DGL_LIBRARY_PATH=/workspace2/dgl/build
ENV PYTHONPATH="/workspace2/dgl/python:$PYTHONPATH"

RUN echo "cd /workspace2/cabam-graph-generation" >> ~/.bashrc
RUN echo "pip install ." >> ~/.bashrc
RUN echo "cp /usr/lib/x86_64-linux-gnu/libgomp.so.1 /opt/conda/envs/gt/lib/python3.8/site-packages/torch/lib/libgomp-a34b3233.so.1" >> ~/.bashrc

COPY --from=apache/beam_python3.8_sdk /opt/apache/beam /opt/apache/beam

# Set the entrypoint to Apache Beam SDK worker launcher.
ENTRYPOINT [ "/opt/apache/beam/boot" ]