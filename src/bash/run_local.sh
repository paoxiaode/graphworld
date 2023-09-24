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

#
# Utilize docker-compose to run beam-pipeline locally in the same environment
# as the remote workers.
#

RUN_MODE2=false
NUM_SAMPLES=5
NUM_TUNING_ROUNDS=2
# py boolean
SAVE_TUNING_RESULTS=False

TASK="nodeclassification"
GENERATOR="sbm"


function get_task_class_name()
{
  local task=$1
  case $task in
    nodeclassification) echo "NodeClassification";;
    graphregression) echo "GraphRegression";;
    linkprediction) echo "LinkPrediction";;
    noderegression) echo "NodeRegression";;
    *) echo "BAD_BASH_TASK_INPUT_${task}_";;
  esac
}

while getopts t:g: flag
do
    case "${flag}" in
        t) TASK=${OPTARG};;
        g) GENERATOR=${OPTARG};;
    esac
done

echo TASK $TASK
echo GENERATOR $GENERATOR

day=$(date +%m_%d)
OUTPUT_PATH="log/day_${day}/${TASK}_${GENERATOR}"
rm -rf "${OUTPUT_PATH}"
mkdir -p ${OUTPUT_PATH}

# # Add gin file string.
GIN_FILES="/workspace2/graphworld/src/configs/${TASK}.gin "
GIN_FILES="${GIN_FILES} /workspace2/graphworld/src/${TASK}_generators/${GENERATOR}/default_setup.gin"
GIN_FILES="${GIN_FILES} /workspace2/graphworld/src/configs/common_hparams/${TASK}_test.gin"

# # Add gin param string.
TASK_CLASS_NAME=$(get_task_class_name ${TASK})
GIN_PARAMS="GeneratorBeamHandlerWrapper.nsamples=${NUM_SAMPLES}"
            
python3 /workspace2/graphworld/src/beam_benchmark_main.py \
  --runner DirectRunner \
  --gin_files configs/DGL_${TASK}.gin \
  --gin_params ${GIN_PARAMS} \
  --output ${OUTPUT_PATH} --write_intermediat True