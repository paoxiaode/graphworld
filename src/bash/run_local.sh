read -p "number of graphs to generate(default=5): " NUM_SAMPLES

if [ -z "${NUM_SAMPLES}" ]; then
  NUM_SAMPLES=5
fi


TASK="nodeclassification"
GENERATOR="sbm"

echo TASK $TASK
echo GENERATOR $GENERATOR
echo NUM_SAMPLES $NUM_SAMPLES
day=$(date +%m_%d)

# avg_degrees=(2 4 8 16 24 32 48 64)
# avg_degrees=(24 40 48 56)
avg_degrees=(10)


power_exponent=9
for avg_degree in ${avg_degrees[@]}; do

  OUTPUT_PATH="/workspace2/dataset/graphworld/${TASK}_${GENERATOR}/power_ex${power_exponent}/avg_d${avg_degree}"
  rm -rf "${OUTPUT_PATH}"
  mkdir -p ${OUTPUT_PATH}

  GIN_FILES="/workspace2/graphworld/src/configs/${shmoo}/DGL_${TASK}.gin"

  # # Add gin param string.
  GIN_PARAMS="GeneratorBeamHandlerWrapper.nsamples=${NUM_SAMPLES}\
          avg_degree/ParamSamplerSpec.min_val=${avg_degree}.0\
          avg_degree/ParamSamplerSpec.max_val=${avg_degree}.0\
          power_exponent/ParamSamplerSpec.min_val=${power_exponent}.0\
          power_exponent/ParamSamplerSpec.max_val=${power_exponent}.0"

  python3 /workspace2/graphworld/src/beam_benchmark_main.py \
    --runner DirectRunner \
    --gin_files ${GIN_FILES} \
    --gin_params ${GIN_PARAMS} \
    --output ${OUTPUT_PATH}/ --write_intermediat True
done

