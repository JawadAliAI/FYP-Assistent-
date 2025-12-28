# Models Directory

This directory will contain Piper TTS voice models.

## Auto-Downloaded Models

When you run `start_local.bat` or build the Docker image, the following model will be downloaded automatically:

- `en_US-lessac-medium.onnx` - English (US) voice model
- `en_US-lessac-medium.onnx.json` - Model configuration

## Manual Download

If you need to download manually:

```bash
# Create this directory if it doesn't exist
mkdir models

# Download voice model
curl -L -o models/en_US-lessac-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx

# Download config
curl -L -o models/en_US-lessac-medium.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

## Other Available Voices

Browse more voices at: https://huggingface.co/rhasspy/piper-voices

Popular options:
- `en_US-amy-medium` - Female voice
- `en_US-danny-low` - Male voice (faster)
- `en_GB-alan-medium` - British English

To use a different voice, update `PIPER_MODEL_PATH` in your `.env` file.
