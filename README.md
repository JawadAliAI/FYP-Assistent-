# 🏋️ FitBot AI - AI Fitness Assistant with Voice

> **Intelligent Fitness Coach** powered by AI with natural voice interaction using Piper TTS and Whisper STT

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![Piper](https://img.shields.io/badge/Piper-TTS-FF6B6B)](https://github.com/rhasspy/piper)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **AI-Powered Coaching** - Personalized fitness advice using Groq's Llama 3.3 70B
- 🎙️ **Voice Input** - Speak your questions using OpenAI Whisper STT
- 🔊 **Voice Output** - Natural responses with Piper TTS
- 📺 **YouTube Tutorials** - Curated exercise videos for 25+ exercises
- 💪 **Custom Workout Plans** - Tailored routines based on your goals
- 🌐 **RESTful API** - Easy integration with any frontend
- 🐳 **Docker Ready** - Deploy anywhere with Docker
- ☁️ **Render Optimized** - One-click deployment to Render

---

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)

```bash
# 1. Clone the repository
git clone https://github.com/JawadAliAI/FYP-Assistent-.git
cd FYP-Assistent-

# 2. Run the setup script
start_local.bat
```

The script will:
- Create virtual environment
- Install all dependencies
- Download Piper voice models
- Start the server at http://localhost:8000

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Run the server
uvicorn app:app --reload --port 8000
```

---

## 📋 Prerequisites

- **Python 3.11** or higher
- **FFmpeg** (for audio processing)
- **Groq API Key** - Free tier available at [console.groq.com](https://console.groq.com/keys)
- **2GB RAM** minimum (for Whisper model)

### Installing FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns server status and component health.

### Chat with FitBot
```http
POST /chat
Content-Type: application/json

{
  "message": "I want to build muscle and lose fat",
  "user_id": "user123",
  "chat_history": []
}
```

### Text-to-Speech (Piper)
```http
POST /tts
Content-Type: application/json

{
  "text": "Hello! I am FitBot, your AI fitness trainer.",
  "voice": "en_US-lessac-medium"
}
```
Returns: Audio file (WAV format)

### Speech-to-Text (Whisper)
```http
POST /stt
Content-Type: multipart/form-data

file: <audio.wav>
```
Returns: Transcribed text

### Exercise Tutorials
```http
GET /tutorials                    # List all exercises
GET /tutorials/{exercise_name}    # Get specific exercise
```

---

## 🌐 Deploy to Render

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `fitbot-api`
   - **Runtime**: Docker
   - **Region**: Choose closest to you
   - **Instance**: Free (or paid for better performance)

### Step 3: Set Environment Variable

In Render dashboard, add:
- **Key**: `GROQ_API_KEY`
- **Value**: Your actual Groq API key from [console.groq.com](https://console.groq.com/keys)

### Step 4: Deploy

- Click **"Create Web Service"**
- Wait 10-15 minutes for first build
- Your API will be live at: `https://your-app-name.onrender.com`

### Step 5: Verify Deployment

Visit: `https://your-app-name.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "groq_connected": true,
  "whisper_loaded": true,
  "piper_configured": true,
  "device": "cpu",
  "total_exercises": 25
}
```

**📖 Detailed deployment guide:** See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

## 🧪 Testing

### Interactive API Documentation

Visit http://localhost:8000/docs to test all endpoints interactively.

### Automated Test Suite

```bash
python test_api.py
```

This tests:
- ✅ Server health
- ✅ Chat functionality
- ✅ TTS generation
- ✅ STT transcription
- ✅ Tutorial recommendations

---

## 📁 Project Structure

```
FYP-Assistent-/
├── app.py                       # Main FastAPI application
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .env.example                 # Environment template
├── start_local.bat              # Windows setup script
├── test_api.py                  # API test suite
├── models/                      # Piper voice models (auto-downloaded)
├── RENDER_DEPLOYMENT.md         # Deployment guide
├── LOCAL_TESTING.md             # Local setup guide
└── IMPLEMENTATION_SUMMARY.md    # Technical details
```

---

## 🎯 How It Works

1. **User Input** → Text or voice message
2. **Speech Recognition** → Whisper transcribes voice to text
3. **AI Processing** → Groq's Llama 3.3 70B generates response
4. **Tutorial Matching** → Finds relevant YouTube videos
5. **Voice Synthesis** → Piper converts response to speech
6. **Response Delivery** → Text + audio + tutorials returned

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Groq** - LLM API (Llama 3.3 70B)

### AI/ML
- **Whisper** - OpenAI's speech recognition
- **Piper TTS** - High-quality text-to-speech
- **PyTorch** - ML framework

### Audio Processing
- **FFmpeg** - Audio conversion
- **librosa** - Audio analysis
- **soundfile** - Audio I/O

---

## 📊 Performance

### Local (CPU):
- Chat response: ~2-3 seconds
- Whisper transcription: ~5-10 seconds (30s audio)
- Piper TTS: ~1-2 seconds per sentence

### Local (GPU - CUDA):
- Chat response: ~1-2 seconds
- Whisper transcription: ~1-2 seconds (30s audio)
- Piper TTS: ~1-2 seconds per sentence

### Render Free Tier:
- Cold start: ~30 seconds (first request after idle)
- Warm requests: Similar to local CPU
- Memory: 512MB (may struggle with long audio)

---

## 🔐 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for AI chat | ✅ Yes | - |
| `WHISPER_MODEL_SIZE` | Whisper model size (tiny/base/small) | Optional | `tiny` |
| `PIPER_MODEL_PATH` | Path to Piper voice model | Optional | Auto-detected |
| `PIPER_EXECUTABLE` | Piper binary path | Optional | `piper` |

**Note**: For Render's free tier (512MB RAM), use `tiny` model. For local with more RAM, you can use `base` or `small`.

---

## 🐛 Troubleshooting

### Server won't start
- Check Python version: `python --version` (need 3.11+)
- Verify virtual environment is activated
- Check `.env` file exists with valid API key

### Whisper not loading
- Ensure 2GB+ RAM available
- Check PyTorch installation: `pip install torch`
- Try smaller model: change `base` to `tiny` in app.py

### Piper TTS fails
- Verify Piper binary is installed
- Check voice model exists in `models/` folder
- Run `start_local.bat` to auto-download models

### FFmpeg errors
- Install FFmpeg: `choco install ffmpeg` (Windows)
- Verify: `ffmpeg -version`

**📖 More troubleshooting:** See [LOCAL_TESTING.md](LOCAL_TESTING.md)

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Local setup & testing
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Deployment guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - Whisper speech recognition
- **Rhasspy** - Piper TTS engine
- **Groq** - Fast LLM inference
- **FastAPI** - Excellent web framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JawadAliAI/FYP-Assistent-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JawadAliAI/FYP-Assistent-/discussions)

---

## 🎉 What's Next?

- [ ] Test locally with `start_local.bat`
- [ ] Run test suite: `python test_api.py`
- [ ] Deploy to Render
- [ ] Integrate with your frontend
- [ ] Add custom exercises
- [ ] Implement user authentication
- [ ] Add workout tracking

---

**Made with ❤️ for fitness enthusiasts**

*Get fit with AI! 💪🤖*
