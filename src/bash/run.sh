day=$(date +%m_%d)
Time=$(date +%H_%M_%S)
mkdir log/day_${day}

set -e

python3 beam_benchmark_main.py \
  --output "log/day_${day}" \
  --gin_files configs/DGL_nodeclassification.gin \
  --runner DirectRunner --write_intermediat True