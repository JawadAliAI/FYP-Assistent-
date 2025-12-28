from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import whisper
import subprocess
import os
import json
import tempfile
from datetime import datetime
import re
import torch

# Load environment variables
load_dotenv()

# ==================== ENVIRONMENT VALIDATION ====================
def validate_environment():
    """Validate required environment variables"""
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ WARNING: GROQ_API_KEY not found in environment variables.")

validate_environment()

# ==================== INITIALIZE SERVICES ====================
# Initialize Groq client
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

import gc

# Initialize Whisper Global Variable
whisper_model = None
whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "tiny")

def get_whisper_model():
    """Lazy load Whisper model and ensure it fits in memory"""
    global whisper_model
    if whisper_model is None:
        print(f"Loading Whisper '{whisper_model_size}' model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Force garbage collection before loading
            gc.collect()
            whisper_model = whisper.load_model(whisper_model_size, device=device)
            print(f"✓ Whisper model loaded on {device}")
        except Exception as e:
            print(f"Error loading Whisper: {e}")
            return None
    return whisper_model

def unload_whisper_model():
    """Unload Whisper model to free up RAM"""
    global whisper_model
    if whisper_model:
        del whisper_model
        whisper_model = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("✓ Whisper model unloaded to free RAM")

# Piper TTS settings
# Auto-detect correct path based on environment
if os.path.exists("models/en_US-lessac-medium.onnx"):
    # Local development (Windows/Mac/Linux)
    default_model_path = "models/en_US-lessac-medium.onnx"
elif os.path.exists("/app/models/en_US-lessac-medium.onnx"):
    # Docker/Render deployment
    default_model_path = "/app/models/en_US-lessac-medium.onnx"
else:
    # Fallback
    default_model_path = "models/en_US-lessac-medium.onnx"

PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", default_model_path)
PIPER_EXECUTABLE = os.getenv("PIPER_EXECUTABLE", "piper")

# Initialize FastAPI
app = FastAPI(title="FitBot API - AI Fitness Assistant")

# CORS - Allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================
class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_history: list = []

class TTSRequest(BaseModel):
    text: str
    voice: str = "en_US-lessac-medium"  # Piper voice model

# ==================== YOUTUBE EXERCISE DATABASE ====================
YOUTUBE_TUTORIALS = {
    # Chest Exercises
    "bench press": [
        "https://www.youtube.com/watch?v=rT7DgCr-3pg",
        "https://www.youtube.com/watch?v=gRVjAtPip0Y"
    ],
    "push ups": [
        "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "https://www.youtube.com/watch?v=_l3ySVKYVJ8"
    ],
    "chest fly": [
        "https://www.youtube.com/watch?v=eozdVDA78K0",
        "https://www.youtube.com/watch?v=Z56EYFZemhk"
    ],
    
    # Back Exercises
    "pull ups": [
        "https://www.youtube.com/watch?v=eGo4IYlbE5g",
        "https://www.youtube.com/watch?v=fLw3i7FiXsE"
    ],
    "deadlift": [
        "https://www.youtube.com/watch?v=ytGaGIn3SjE",
        "https://www.youtube.com/watch?v=r4MzxtBKyNE"
    ],
    "rows": [
        "https://www.youtube.com/watch?v=roCP6wCXPqo",
        "https://www.youtube.com/watch?v=9efgcAjQe7E"
    ],
    
    # Leg Exercises
    "squats": [
        "https://www.youtube.com/watch?v=ultWZbUMPL8",
        "https://www.youtube.com/watch?v=gcNh17Ckjgg"
    ],
    "lunges": [
        "https://www.youtube.com/watch?v=QOVaHwm-Q6U",
        "https://www.youtube.com/watch?v=wrwwXE_x-pQ"
    ],
    "leg press": [
        "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
        "https://www.youtube.com/watch?v=z7eQq-GN-Nc"
    ],
    
    # Shoulder Exercises
    "shoulder press": [
        "https://www.youtube.com/watch?v=qEwKCR5JCog",
        "https://www.youtube.com/watch?v=M2rwvNhTOu0"
    ],
    "lateral raises": [
        "https://www.youtube.com/watch?v=3VcKaXpzqRo",
        "https://www.youtube.com/watch?v=kDqklk1ZESo"
    ],
    
    # Arm Exercises
    "bicep curls": [
        "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
        "https://www.youtube.com/watch?v=av7-8igSXTs"
    ],
    "tricep dips": [
        "https://www.youtube.com/watch?v=6kALZikXxLc",
        "https://www.youtube.com/watch?v=0326dy_-CzM"
    ],
    
    # Core Exercises
    "plank": [
        "https://www.youtube.com/watch?v=ASdvN_XEl_c",
        "https://www.youtube.com/watch?v=pvIjsG5Svck"
    ],
    "crunches": [
        "https://www.youtube.com/watch?v=Xyd_fa5zoEU",
        "https://www.youtube.com/watch?v=MKmrqcoCZ-M"
    ],
    "russian twists": [
        "https://www.youtube.com/watch?v=wkD8rjkodUI",
        "https://www.youtube.com/watch?v=JyUqwkVpsi8"
    ],
    
    # Cardio
    "hiit": [
        "https://www.youtube.com/watch?v=ml6cT4AZdqI",
        "https://www.youtube.com/watch?v=cZnsLVArIt8"
    ],
    "running": [
        "https://www.youtube.com/watch?v=brFHyOtTwH4",
        "https://www.youtube.com/watch?v=_kGESn8ArrU"
    ],
    "burpees": [
        "https://www.youtube.com/watch?v=TU8QYVW0gDU",
        "https://www.youtube.com/watch?v=JZQA08SlJnM"
    ],
    
    # Full Body
    "full body workout": [
        "https://www.youtube.com/watch?v=UBMk30rjy0o",
        "https://www.youtube.com/watch?v=Yz6PmHcYbN0"
    ],
    "abs workout": [
        "https://www.youtube.com/watch?v=DHD1-2P94DI",
        "https://www.youtube.com/watch?v=1919eTCoESo"
    ],
    
    # Weight Loss Specific
    "weight loss workout": [
        "https://www.youtube.com/watch?v=2MicE75thDQ",
        "https://www.youtube.com/watch?v=kZDvg92tTMc"
    ],
    "fat burning": [
        "https://www.youtube.com/watch?v=ml6cT4AZdqI",
        "https://www.youtube.com/watch?v=cZnsLVArIt8"
    ],
    "home workout": [
        "https://www.youtube.com/watch?v=UBMk30rjy0o",
        "https://www.youtube.com/watch?v=Yz6PmHcYbN0"
    ],
    "beginner workout": [
        "https://www.youtube.com/watch?v=oAPCPjnU1wA",
        "https://www.youtube.com/watch?v=2MicE75thDQ"
    ],
}

def find_relevant_tutorials(text: str) -> list:
    """Find relevant YouTube tutorials based on text content"""
    text_lower = text.lower()
    found_tutorials = []
    
    for exercise, links in YOUTUBE_TUTORIALS.items():
        if exercise in text_lower:
            found_tutorials.append({
                "exercise": exercise.title(),
                "links": links
            })
    
    return found_tutorials

# ==================== SYSTEM PROMPT ====================
TRAINER_SYSTEM_PROMPT = """
You are FitBot, a friendly and energetic AI Fitness Coach who loves helping people achieve their fitness goals.

🎯 YOUR PERSONALITY:
- Conversational and friendly (like chatting with a personal trainer friend)
- Enthusiastic and motivating
- Patient and understanding
- Ask ONE question at a time
- Build rapport naturally through conversation

🚨 IMPORTANT RULES:
- ONLY discuss fitness, workouts, nutrition, wellness topics
- For off-topic questions: "I'm your fitness coach! Let's focus on getting you in shape 💪"
- NEVER dump all information at once
- Have a natural conversation, not an interrogation

📋 CONVERSATION FLOW - FOLLOW THIS EXACTLY:

**PHASE 1: INITIAL GREETING & GOAL (Questions 1-2)**
When user first messages:
1. Greet them warmly
2. Ask about their PRIMARY goal (weight loss, muscle gain, or athletic performance)
3. Wait for their answer

**PHASE 2: UNDERSTANDING THEIR SITUATION (Questions 3-6)**
Ask ONE question at a time. Wait for each answer before asking the next:

Question 3: "Got it! And where will you be working out - do you have a gym membership or will you be training at home?"

Question 4: "Perfect! How many days per week can you realistically commit to working out? Be honest - consistency is key!"

Question 5: "Awesome! Do you have any injuries or physical limitations I should know about?"

Question 6: "Great! One last thing - what's your current experience level: beginner, intermediate, or have you been training for a while?"

**PHASE 3: PROVIDE RECOMMENDATIONS (Only after gathering 5-6 details)**
Once you have enough information, provide a personalized workout plan matching their requested number of days.

🎯 KEY PRINCIPLES:
1. **ONE QUESTION AT A TIME** - Never ask multiple questions in one message
2. **CONVERSATIONAL TONE** - Talk like a friend, not a robot
3. **BUILD GRADUALLY** - Gather info slowly through natural conversation
4. **MATCH THEIR DAYS** - If they say 3 days, give 3 days. If 5 days, give 5 days!
5. **SIMPLE ANSWERS** - Understand "yes", "home", "gym", "3 days", "5 days", etc.
6. **DON'T REPEAT** - If you already know something, don't ask again
7. **BE BRIEF** - Keep responses short and focused
8. **ENCOURAGE** - Use motivating language throughout
"""

# ==================== HELPER FUNCTIONS ====================
def remove_emojis(text: str) -> str:
    """Remove all emojis from a string."""
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF"
        "\U00002B00-\U00002BFF"
        "\U0001FA70-\U0001FAFF"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def clean_text_for_tts(text: str) -> str:
    """Clean text for TTS: remove emojis and Markdown formatting."""
    text = remove_emojis(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'[\*_]+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'`+', '', text)
    return text.strip()

# ==================== ROOT ENDPOINT ====================
@app.get("/")
async def root():
    """API information endpoint"""
    return JSONResponse({
        "status": "healthy", 
        "service": "FitBot API - AI Fitness Assistant",
        "version": "3.0",
        "description": "Backend API with Piper TTS and Whisper STT",
        "features": [
            "AI-Powered Fitness Coaching",
            "Personalized Workout Plans",
            "Nutrition Guidance", 
            "YouTube Tutorial Recommendations",
            "Piper TTS (High-Quality Voice)",
            "Whisper STT (Accurate Transcription)"
        ],
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "tutorials": "GET /tutorials",
            "tts": "POST /tts - Piper Text-to-Speech",
            "stt": "POST /stt - Whisper Speech-to-Text"
        }
    })

# ==================== CHAT ENDPOINT ====================
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not groq_client:
            raise HTTPException(status_code=503, detail="Groq Client not initialized. Check API Key.")

        user_id = request.user_id
        user_message = request.message.strip()
        chat_history = request.chat_history if request.chat_history else []
        
        # Prepare messages for Groq
        messages = [{"role": "system", "content": TRAINER_SYSTEM_PROMPT}]
        
        for msg in chat_history[-10:]:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_message})
        
        # Call Groq AI
        try:
            completion = groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1500,
            )
            reply_text = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API Error: {e}")
            raise HTTPException(status_code=502, detail=f"Groq API Error: {str(e)}")
        
        # Find relevant YouTube tutorials
        tutorials = find_relevant_tutorials(reply_text + " " + user_message)
        
        updated_history = chat_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": reply_text}
        ]
        
        return JSONResponse({
            "reply": reply_text,
            "tutorials": tutorials,
            "chat_history": updated_history,
            "message_count": len(updated_history)
        })
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PIPER TTS ====================
@app.post("/tts")
async def text_to_speech_piper(req: TTSRequest):
    """Convert text to speech using Piper TTS"""
    try:
        # Prevent OOM by cleaning garbage before spawning subprocess
        gc.collect()
        
        clean_text = clean_text_for_tts(req.text)
        
        # Get absolute path to model
        model_path = os.path.abspath(PIPER_MODEL_PATH)
        
        # Verify model exists
        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=503, 
                detail=f"Piper model not found at: {model_path}. Please download the model first."
            )
        
        # Create temporary output file
        output_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        # Run Piper TTS
        # Piper command: echo "text" | piper --model model.onnx --output_file output.wav
        process = subprocess.Popen(
            [PIPER_EXECUTABLE, "--model", model_path, "--output_file", output_wav.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=clean_text.encode('utf-8'))
        
        if process.returncode != 0:
            raise Exception(f"Piper TTS failed: {stderr.decode()}")
        
        return FileResponse(
            output_wav.name, 
            media_type="audio/wav", 
            filename="speech.wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Piper TTS Error: {str(e)}")

# ==================== WHISPER STT ====================
# ==================== WHISPER STT ====================
@app.post("/stt")
async def speech_to_text_whisper(file: UploadFile = File(...)):
    """Convert speech to text using Whisper"""
    try:
        # Lazy load Whisper model on first request
        model = get_whisper_model()
        if not model:
            raise HTTPException(status_code=503, detail="Whisper model failed to load")
        
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        # Transcribe with Whisper
        result = model.transcribe(tmp_path)
        
        # Extract transcript
        full_text = result["text"]
        
        # Clean up
        os.remove(tmp_path)
        
        # Unload model to free RAM
        unload_whisper_model()
        
        return JSONResponse({
            "transcript": full_text.strip(),
            "language": result.get("language", "en")
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper STT Error: {str(e)}")

# ==================== EXERCISE TUTORIALS ====================
@app.get("/tutorials/{exercise}")
async def get_exercise_tutorials(exercise: str):
    """Get YouTube tutorials for a specific exercise"""
    try:
        exercise_lower = exercise.lower().strip()
        
        if exercise_lower in YOUTUBE_TUTORIALS:
            return JSONResponse({
                "exercise": exercise.title(),
                "tutorials": YOUTUBE_TUTORIALS[exercise_lower],
                "count": len(YOUTUBE_TUTORIALS[exercise_lower])
            })
        
        matches = []
        for ex_name, links in YOUTUBE_TUTORIALS.items():
            if exercise_lower in ex_name or ex_name in exercise_lower:
                matches.append({
                    "exercise": ex_name.title(),
                    "tutorials": links
                })
        
        if matches:
            return JSONResponse({"matches": matches, "count": len(matches)})
        
        return JSONResponse({
            "message": f"No tutorials found for '{exercise}'",
            "available_exercises": list(YOUTUBE_TUTORIALS.keys())
        }, status_code=404)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tutorials")
async def list_all_exercises():
    """List all available exercises"""
    try:
        all_exercises = []
        for exercise, links in YOUTUBE_TUTORIALS.items():
            all_exercises.append({
                "exercise": exercise.title(),
                "tutorial_count": len(links),
                "links": links
            })
        
        return JSONResponse({
            "total_exercises": len(all_exercises),
            "exercises": all_exercises
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "FitBot AI Fitness Assistant",
        "groq_connected": groq_client is not None,
        "whisper_loaded": whisper_model is not None,
        "piper_configured": os.path.exists(PIPER_MODEL_PATH),
        "device": device,
        "total_exercises": len(YOUTUBE_TUTORIALS)
    })
