# 🏋️ FitBot API - AI Fitness Assistant Backend

A conversational AI fitness coaching API powered by Groq's LLaMA model. Provides personalized workout plans, nutrition guidance, and YouTube tutorial recommendations through a RESTful API.

## 🚀 Features

- **Conversational AI Coach** - Natural, friendly fitness coaching conversations
- **Dynamic Workout Plans** - Generates plans based on user's training days (3, 4, 5+ days)
- **YouTube Tutorial Integration** - Automatic exercise tutorial recommendations
- **Voice Support** - Text-to-Speech (TTS) and Speech-to-Text (STT) endpoints
- **Personalized Guidance** - Adapts to user's goals, experience level, and equipment
- **CORS Enabled** - Ready for frontend integration from any domain

---

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and documentation |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `POST` | `/chat` | Main AI fitness chat endpoint |
| `GET` | `/tutorials` | List all available exercises |
| `GET` | `/tutorials/{exercise}` | Get tutorials for specific exercise |
| `POST` | `/tts` | Text-to-speech conversion |
| `POST` | `/stt` | Speech-to-text conversion |

---

## 🔧 Installation & Setup

### Prerequisites

- Python 3.11+
- FFmpeg (for audio processing)
- Groq API Key ([Get one here](https://console.groq.com/keys))

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd assistent
   ```

2. **Install FFmpeg:**
   
   **Windows:**
   ```bash
   choco install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux:**
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg portaudio19-dev
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   GROQ_API_KEY=your_groq_api_key_here
   ```

6. **Run the server:**
   ```bash
   uvicorn app:app --reload --port 8000
   ```

7. **Test the API:**
   - Open http://localhost:8000 - API info
   - Open http://localhost:8000/docs - Interactive documentation

---

## 🌐 Deploy to Render

### Quick Deploy (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Blueprint**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Add environment variable: `GROQ_API_KEY=your_key_here`
   - Click **Apply**

3. **Your API is live!**
   - URL: `https://fitbot-api.onrender.com`
   - Test: `https://fitbot-api.onrender.com/health`

### Manual Deploy

If you prefer manual configuration:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your repository
4. Configure:
   - **Name:** `fitbot-api`
   - **Environment:** Python 3
   - **Build Command:**
     ```bash
     apt-get update && apt-get install -y ffmpeg portaudio19-dev && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     sh start.sh
     ```
5. Add environment variable: `GROQ_API_KEY`
6. Deploy!

---

## 📡 API Usage Examples

### Chat Endpoint

**Request:**
```bash
curl -X POST "https://your-api.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to lose weight",
    "user_id": "user123",
    "chat_history": []
  }'
```

**Response:**
```json
{
  "reply": "That's awesome! Losing weight is a great goal. Where will you be working out - at home or do you have access to a gym?",
  "tutorials": [],
  "chat_history": [
    {"role": "user", "content": "I want to lose weight"},
    {"role": "assistant", "content": "That's awesome! ..."}
  ],
  "message_count": 2
}
```

### Get Exercise Tutorials

**Request:**
```bash
curl "https://your-api.onrender.com/tutorials/squats"
```

**Response:**
```json
{
  "exercise": "Squats",
  "tutorials": [
    "https://www.youtube.com/watch?v=ultWZbUMPL8",
    "https://www.youtube.com/watch?v=gcNh17Ckjgg"
  ],
  "count": 2
}
```

### Text-to-Speech

**Request:**
```bash
curl -X POST "https://your-api.onrender.com/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Great job on your workout!",
    "language_code": "en"
  }' \
  --output speech.wav
```

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key for AI chat | ✅ Yes |
| `PORT` | Server port (auto-set by Render) | ❌ No (default: 8000) |

---

## 🎯 Conversation Flow

The AI follows a natural conversation pattern:

1. **Greeting** - Welcomes the user
2. **Goal** - Asks about fitness goal (weight loss, muscle gain, performance)
3. **Location** - Home or gym?
4. **Days** - How many days per week?
5. **Injuries** - Any limitations?
6. **Experience** - Beginner or experienced?
7. **Plan** - Provides personalized workout plan matching their days

**Example:**
```
User: "I want to build muscle"
AI: "That's awesome! Where will you be working out?"
User: "at home"
AI: "Perfect! How many days per week can you commit?"
User: "5 days"
AI: "Wow, 5 days! Any injuries?"
User: "no"
AI: "Excellent! Are you a beginner or experienced?"
User: "beginner"
AI: *Provides 5-day workout plan with exercises and YouTube links*
```

---

## 📁 Project Structure

```
assistent/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── start.sh                # Production start script
├── render.yaml             # Render deployment config
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── frontend-standalone.html # Optional: Standalone frontend
```

---

## 🐛 Troubleshooting

### Build Fails on Render

**Issue:** FFmpeg installation fails  
**Solution:** Ensure build command includes:
```bash
apt-get update && apt-get install -y ffmpeg portaudio19-dev && pip install -r requirements.txt
```

### API Returns 503

**Issue:** Groq client not initialized  
**Solution:** Check that `GROQ_API_KEY` environment variable is set correctly in Render dashboard

### CORS Errors

**Issue:** Frontend can't access API  
**Solution:** The API allows all origins by default. If you need to restrict, update CORS settings in `app.py`

### Voice Features Not Working

**Issue:** TTS/STT endpoints fail  
**Solution:** Ensure FFmpeg is installed. On Render, it's installed via the build command.

---

## 🔗 Frontend Integration

This is a backend-only API. To use it, you need a frontend. Options:

1. **Use the included standalone frontend:**
   - Deploy `frontend-standalone.html` to Netlify/Vercel
   - Configure it to point to your Render API URL

2. **Build your own frontend:**
   - Connect to the `/chat` endpoint
   - Display responses and tutorials
   - Handle conversation state

3. **Mobile app:**
   - Use the API endpoints in your iOS/Android app
   - Implement chat UI
   - Integrate voice features

---

## 📊 API Rate Limits

- **Groq Free Tier:** Check [Groq Console](https://console.groq.com/) for current limits
- **Render Free Tier:** 
  - Sleeps after 15 minutes of inactivity
  - First request after sleep takes ~30 seconds

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

---

## 📝 License

This project is for educational purposes.

---

## 🔗 Links

- **Groq Console:** https://console.groq.com/
- **Render Dashboard:** https://dashboard.render.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **API Documentation:** `/docs` endpoint on your deployed API

---

## ✨ Features in Detail

### Conversational AI
- Natural language understanding
- Context-aware responses
- Remembers conversation history
- Friendly, motivating tone

### Dynamic Workout Plans
- Adapts to user's available training days
- Customizes based on equipment (home/gym)
- Adjusts for experience level
- Considers injuries and limitations

### YouTube Integration
- Automatic tutorial recommendations
- Exercise-specific video links
- Form guidance resources

### Voice Support
- Text-to-Speech for AI responses
- Speech-to-Text for voice input
- Multiple language support (TTS)

---

**Happy Coding! 💪🚀**

For questions or issues, check the `/docs` endpoint for interactive API documentation.
