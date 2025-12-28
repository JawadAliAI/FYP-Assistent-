from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import edge_tts  # Replaced gTTS with Edge TTS
import speech_recognition as sr
import os
import json
import tempfile
import uuid
import asyncio

# Load environment variables
load_dotenv()

# Initialize Groq client
# Fallback to hardcoded key if env var is missing (Temporary Fix for Render)
GROQ_KEY = os.getenv("GROQ_API_KEY", "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")

try:
    groq_client = Groq(api_key=GROQ_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

# Initialize FastAPI
app = FastAPI(title="FitBot API - AI Fitness Assistant (Lightweight)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATA MODELS ====================
class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_history: list = []

class TTSRequest(BaseModel):
    text: str
    # Edge TTS voices: en-US-AriaNeural, en-US-GuyNeural, etc.
    voice: str = "en-US-AriaNeural" 

# ==================== EXERCISE DATABASE (Simplified) ====================
YOUTUBE_TUTORIALS = {
    "bench press": ["https://www.youtube.com/watch?v=rT7DgCr-3pg"],
    "push ups": ["https://www.youtube.com/watch?v=IODxDxX7oi4"],
    "squats": ["https://www.youtube.com/watch?v=ultWZbUMPL8"],
    "deadlift": ["https://www.youtube.com/watch?v=ytGaGIn3SjE"],
    "plank": ["https://www.youtube.com/watch?v=ASdvN_XEl_c"]
}

TRAINER_SYSTEM_PROMPT = """
You are FitBot, an energetic AI Fitness Coach.
Keep responses short, motivating, and focused on fitness.
"""

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {"status": "online", "mode": "lightweight"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_connected": groq_client is not None,
        "mode": "lightweight (EdgeTTS + SpeechRecognition)"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    if not groq_client:
        raise HTTPException(status_code=503, detail="Groq API Key missing")
    
    try:
        # Construct messages
        messages = [{"role": "system", "content": TRAINER_SYSTEM_PROMPT}]
        for msg in request.chat_history[-5:]:
            if "role" in msg and "content" in msg:
                messages.append(msg)
        messages.append({"role": "user", "content": request.message})
        
        # Call Groq
        completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        reply = completion.choices[0].message.content.strip()
        
        # Simple tutorial matching
        tutorials = []
        for ex, links in YOUTUBE_TUTORIALS.items():
            if ex in reply.lower() or ex in request.message.lower():
                tutorials.append({"exercise": ex.title(), "links": links})
        
        return {
            "reply": reply,
            "tutorials": tutorials,
            "chat_history": request.chat_history + [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": reply}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def text_to_speech_edge(req: TTSRequest):
    """Convert text to speech using Edge TTS (Microsoft - Free & Unlimited)"""
    try:
        # Create temp file
        file_name = f"tts_{uuid.uuid4()}.mp3"
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        
        # Generate Audio
        communicate = edge_tts.Communicate(req.text, req.voice)
        await communicate.save(file_path)
        
        return FileResponse(
            file_path, 
            media_type="audio/mpeg", 
            filename="speech.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EdgeTTS Error: {str(e)}")

@app.post("/stt")
async def speech_to_text_google(file: UploadFile = File(...)):
    """Convert speech to text using Google Speech Recognition"""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        # Process with SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            # Use Google's free API
            text = recognizer.recognize_google(audio_data)
            
        os.remove(tmp_path)
        return {"transcript": text}
        
    except sr.UnknownValueError:
        return {"transcript": "", "error": "Could not understand audio"}
    except sr.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Google Speech API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")

@app.get("/tutorials")
def list_tutorials():
    return {"exercises": list(YOUTUBE_TUTORIALS.keys())}
