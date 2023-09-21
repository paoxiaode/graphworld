# docker run --gpus all --ipc=host --ulimit memlock=-1 --cap-add=SYS_ADMIN --ulimit stack=67108864 -it -v /home/ubuntu/code:/workspace2 nvcr.io/nvidia/pytorch:23.03-py3 bash -c 'pip install ogb && pip install rdkit && echo "export DGL_HOME='/workspace2/dgl'">>/root/.bashrc && echo "export DGL_LIBRARY_PATH='/workspace2/dgl/build'" >> /root/.bashrc && echo "export PYTHONPATH='/workspace2/dgl/python:/workspace2/dgl_sparse_benchmark:/workspace2/python_profiler/'" >> /root/.bashrc && bash'

#!/bin/bash
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

# Build and tag the build image.
PROJECT_NAME="project"
BUILD_NAME="graphworld"

docker run --rm --gpus all --name graph --entrypoint /bin/bash --ipc=host --ulimit memlock=-1 --cap-add=SYS_ADMIN --ulimit stack=67108864 -it -v /home/ubuntu/code:/workspace2 ${BUILD_NAME}:latest
