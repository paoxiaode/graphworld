
TASK="nodeclassification"
GENERATOR="sbm"

echo TASK $TASK
echo GENERATOR $GENERATOR

day=$(date +%m_%d)
OUTPUT_PATH="/workspace2/dataset/graphworld/day_${day}/${TASK}_${GENERATOR}"

python3 /workspace2/graphworld/src/test_pickle.py \
  --output ${OUTPUT_PATH} 