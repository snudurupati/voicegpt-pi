# run piper again (use your source-built binary)
cd /srv/tts/piper
ESPEAKNG_DATA_PATH=/usr/lib/aarch64-linux-gnu/espeak-ng-data \
LD_LIBRARY_PATH=/srv/tts/piper/build:$LD_LIBRARY_PATH \
echo "Siya! are you still sleepy cop?" | \
  ./build/piper \
    -m /srv/tts/voices/en/en_US/danny/low/en_US-danny-low.onnx \
    -c /srv/tts/voices/en/en_US/danny/low/en_US-danny-low.onnx.json \
    -s 0 

#aplay /tmp/tts.wav

