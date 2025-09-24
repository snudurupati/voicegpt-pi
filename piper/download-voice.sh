sudo mkdir -p /srv/tts/voices && sudo chown -R $(id -un):$(id -gn) /srv/tts
cd /srv/tts/voices

# model + config (both files are required)
#hf download rhasspy/piper-voices en/en_US/norman/medium/en_US-norman-medium.onnx --local-dir .
#hf download rhasspy/piper-voices en/en_US/norman/medium/en_US-norman-medium.onnx.json --local-dir .

#hf download jgkawell/jarvis en/en_GB/jarvis/medium/jarvis-medium.onnx --local-dir .
#hf download jgkawell/jarvis en/en_GB/jarvis/medium/jarvis-medium.onnx.json --local-dir .

#hf download rhasspy/piper-voices en/en_US/ryan/medium/en_US-ryan-medium.onnx --local-dir .
#hf download rhasspy/piper-voices en/en_US/ryan/medium/en_US-ryan-medium.onnx.json --local-dir .

hf download rhasspy/piper-voices  en/en_US/danny/low/en_US-danny-low.onnx --local-dir .
hf download rhasspy/piper-voices  en/en_US/danny/low/en_US-danny-low.onnx.json --local-dir . 
