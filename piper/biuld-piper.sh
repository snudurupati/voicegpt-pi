sudo mkdir -p /srv/tts && sudo chown -R $(id -un):$(id -gn) /srv/tts
cd /srv/tts
git clone https://github.com/rhasspy/piper
cd piper
git submodule update --init --recursive
make -j"$(nproc)"

