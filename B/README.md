# Sakhi — A Pocket Friend

Two-way, near-real-time voice translation between English and Indian languages (Hindi, Telugu, Tamil, Kannada).

## Features

- **Languages**: English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn)
- **Speech-to-Text**: OpenAI Whisper (local, no API)
- **Translation**: Facebook MBART-50 (free, open-source)
- **Text-to-Speech**: pyttsx3 (offline) with gTTS fallback
- **LangChain Integration**: Custom LLM wrapper for translation
- **Caching**: Repeated translations cached for speed
- **Real-time**: Configurable audio chunks (default 3s)

## Installation

```bash
# Install PortAudio (required for sounddevice)
# Windows: Download from http://www.portaudio.com/download.html
# Linux: sudo apt-get install portaudio19-dev python3-pyaudio
# macOS: brew install portaudio

# Install Python dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# English to Hindi translation
python run_sakhi.py --src en --tgt hi

# Auto-detect source language
python run_sakhi.py --src auto --tgt ta

# Use smaller models for low memory
python run_sakhi.py --src en --tgt hi --whisper-model tiny --mbart-model facebook/mbart-large-50-one-to-many-mmt

# Custom chunk length (5 seconds)
python run_sakhi.py --src en --tgt kn --chunk-sec 5
```

## Usage

The application listens to your microphone, transcribes speech, translates it, and speaks the translation.

**Controls**:
- Speak into your microphone
- Press `Ctrl+C` to stop

**Arguments**:
- `--src`: Source language (en, hi, te, ta, kn, auto)
- `--tgt`: Target language (en, hi, te, ta, kn)
- `--chunk-sec`: Audio chunk length in seconds (default: 3)
- `--whisper-model`: Whisper model size (tiny, base, small, medium, large; default: base)
- `--mbart-model`: MBART model (default: facebook/mbart-large-50-many-to-many-mmt)

## Model Selection

### Whisper Models (STT)

| Model  | Size  | Memory | Speed | Accuracy |
|--------|-------|--------|-------|----------|
| tiny   | 39M   | ~1GB   | Fast  | Good     |
| base   | 74M   | ~1GB   | Fast  | Better   |
| small  | 244M  | ~2GB   | Medium| Good     |
| medium | 769M  | ~5GB   | Slow  | Better   |
| large  | 1550M | ~10GB  | Slowest| Best   |

**Recommendation**: Use `base` for CPU, `small` or `medium` for GPU.

### MBART Models (Translation)

| Model | Size | Memory | Languages |
|-------|------|--------|-----------|
| facebook/mbart-large-50-many-to-many-mmt | 611M | ~2.5GB | 50 languages (bidirectional) |
| facebook/mbart-large-50-one-to-many-mmt  | 611M | ~2.5GB | English to 50 languages |

**Recommendation**: Use `many-to-many` for full bidirectional support.

## GPU Acceleration

Models automatically use GPU if available (CUDA/MPS). To force CPU:

```python
# Edit sakhi/translator.py and sakhi/stt.py
# Change device="cuda" to device="cpu"
```

## Troubleshooting

### PortAudio Error
```
Error: PortAudio library not found
```
**Solution**: Install PortAudio (see Installation section)

### Out of Memory
```
RuntimeError: CUDA out of memory
```
**Solution**: Use smaller models:
```bash
python run_sakhi.py --src en --tgt hi --whisper-model tiny --mbart-model facebook/mbart-large-50-one-to-many-mmt
```

### TTS Language Not Supported
If pyttsx3 doesn't support your target language, the app will:
1. Print the translated text to console
2. Optionally save MP3 using gTTS (requires internet)

### No Microphone Detected
```
Error: No input device found
```
**Solution**: Check microphone connection and permissions

### Slow Translation
- Use GPU if available
- Reduce `--chunk-sec` to process smaller audio chunks
- Use smaller Whisper model (`tiny` or `base`)
- Translation cache helps with repeated phrases

## Architecture

```
run_sakhi.py          # CLI entrypoint
├── sakhi/
│   ├── realtime.py   # Main loop: record → transcribe → translate → speak
│   ├── stt.py        # Whisper speech-to-text
│   ├── translator.py # MBART translation + caching
│   ├── langchain_llm.py # LangChain LLM wrapper
│   └── tts.py        # Text-to-speech (pyttsx3/gTTS)
```

## License

Open-source. Uses pretrained models from Hugging Face (licensed under their respective licenses).

## Models Used

- **Whisper**: OpenAI (MIT License)
- **MBART**: Facebook AI (CC-BY-NC 4.0)
- **pyttsx3**: Mozilla Public License 2.0
- **gTTS**: MIT License
