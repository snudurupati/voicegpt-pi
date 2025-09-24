sudo mkdir -p /srv/asr && sudo chown -R $(id -un):$(id -gn) /srv/asr
cd /srv/asr
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
cmake -B build -DWHISPER_BLAS=ON -DWHISPER_BLAS_VENDOR=OpenBLAS
cmake --build build --config Release -j$(nproc)
ls build/bin

