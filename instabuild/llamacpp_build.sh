# 0) Prep
sudo apt update
sudo apt install -y git build-essential cmake libopenblas-dev

# 1) Put code & models on NVMe (root is already NVMe, but keep it tidy)
sudo mkdir -p /srv/llm/models
sudo chown -R $USER:$USER /srv/llm

# 2) Get llama.cpp and build with OpenBLAS (fastest on Pi)
cd /srv/llm
git reset --hard HEAD
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# BLAS Build
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DLLAMA_CURL=OFF
cmake --build build --config Release

