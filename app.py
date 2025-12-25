from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import speech_recognition as sr
import os
import json
import tempfile
import subprocess
from datetime import datetime
import re

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

# ==================== IN-MEMORY SESSION STORAGE ====================
# Store chat history in memory (resets on server restart)
chat_sessions = {}

# ==================== MODELS ====================
class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_history: list = []  # Client sends their own history

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en"

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

Example:
User: "Hi"
You: "Hey there! I'm FitBot, your AI fitness coach. I'm pumped to help you on your fitness journey! What brings you here today - are you looking to lose weight, build muscle, or improve your athletic performance?"

**PHASE 2: UNDERSTANDING THEIR SITUATION (Questions 3-6)**
Ask ONE question at a time. Wait for each answer before asking the next:

Question 3: "Got it! And where will you be working out - do you have a gym membership or will you be training at home?"

Question 4: "Perfect! How many days per week can you realistically commit to working out? Be honest - consistency is key!"

Question 5: "Awesome! Do you have any injuries or physical limitations I should know about?"

Question 6: "Great! One last thing - what's your current experience level: beginner, intermediate, or have you been training for a while?"

**PHASE 3: PROVIDE RECOMMENDATIONS (Only after gathering 5-6 details)**
Once you have enough information, say:
"Alright, I've got everything I need! Let me put together a personalized plan for you. Give me a sec..."

Then provide a plan based on THEIR REQUESTED NUMBER OF DAYS:

**WORKOUT PLAN - MATCH THEIR DAYS:**
- If they said "3 days" → Create a 3-day plan (Day 1, Day 2, Day 3)
- If they said "4 days" → Create a 4-day plan (Day 1, Day 2, Day 3, Day 4)
- If they said "5 days" → Create a 5-day plan (Day 1, Day 2, Day 3, Day 4, Day 5)
- And so on...

For each day, list 3-4 exercises with sets/reps:

Example for 3 days:
"Here's your 3-day workout plan:

**Day 1 - Full Body:**
- Push-ups: 3 sets of 10 reps
- Squats: 3 sets of 15 reps
- Plank: 3 sets of 30 seconds

**Day 2 - Lower Body:**
- Lunges: 3 sets of 12 reps each leg
- Squats: 4 sets of 15 reps
- Crunches: 3 sets of 15 reps

**Day 3 - Upper Body & Cardio:**
- Push-ups: 3 sets of 12 reps
- Plank: 3 sets of 45 seconds
- Burpees: 3 sets of 8 reps

Check the YouTube tutorial links below for proper form!"

Example for 5 days:
"Here's your 5-day workout plan:

**Day 1 - Chest & Triceps:**
- Push-ups: 3 sets of 12 reps
- Tricep dips: 3 sets of 10 reps
- Plank: 3 sets of 30 seconds

**Day 2 - Back & Biceps:**
- Pull-ups: 3 sets of 8 reps (or rows if no bar)
- Bicep curls: 3 sets of 12 reps
- Plank: 3 sets of 30 seconds

**Day 3 - Legs:**
- Squats: 4 sets of 15 reps
- Lunges: 3 sets of 12 reps each leg
- Calf raises: 3 sets of 20 reps

**Day 4 - Shoulders & Core:**
- Shoulder press: 3 sets of 12 reps
- Lateral raises: 3 sets of 12 reps
- Russian twists: 3 sets of 20 reps

**Day 5 - Cardio & Full Body:**
- HIIT workout: 20 minutes
- Burpees: 3 sets of 10 reps
- Plank: 3 sets of 45 seconds

Check the YouTube tutorial links below for proper form!"

**NUTRITION TIP:**
One simple nutrition tip (1-2 sentences max)

Example:
"For weight loss, aim to eat 300-500 calories below your maintenance level. Drink 2-3 liters of water daily!"

**FOLLOW-UP:**
End with: "How does this sound? Ready to get started, or do you have any questions?"

🎯 KEY PRINCIPLES:

1. **ONE QUESTION AT A TIME** - Never ask multiple questions in one message
2. **CONVERSATIONAL TONE** - Talk like a friend, not a robot
3. **BUILD GRADUALLY** - Gather info slowly through natural conversation
4. **MATCH THEIR DAYS** - If they say 3 days, give 3 days. If 5 days, give 5 days!
5. **SIMPLE ANSWERS** - Understand "yes", "home", "gym", "3 days", "5 days", etc.
6. **DON'T REPEAT** - If you already know something, don't ask again
7. **BE BRIEF** - Keep responses short and focused
8. **ENCOURAGE** - Use motivating language throughout

RESPONSE STYLE:
- Use casual, friendly language
- Short sentences and paragraphs
- NO EMOJIS in your text (system adds them)
- Reference what they told you earlier
- Show you're listening and care

EXAMPLE CONVERSATION:

User: "I want to lose weight"
You: "That's awesome! Losing weight is a great goal. Where will you be working out - at home or do you have access to a gym?"

User: "at home"
You: "Perfect! Home workouts are super effective. How many days per week can you commit to training? 3 days? 4 days? More?"

User: "5 days"
You: "Wow, 5 days! That's fantastic commitment. Any injuries or physical limitations I should know about?"

User: "no"
You: "Excellent! Last question - are you a complete beginner, or have you worked out before?"

User: "beginner"
You: "Awesome! I love working with beginners. Alright, let me create your personalized 5-day plan... 

Here's your 5-day workout plan:

**Day 1 - Full Body:**
- Push-ups: 3 sets of 8-10 reps
- Squats: 3 sets of 12 reps
- Plank: 3 sets of 20-30 seconds

**Day 2 - Lower Body:**
- Lunges: 3 sets of 10 reps each leg
- Squats: 4 sets of 12 reps
- Crunches: 3 sets of 15 reps

**Day 3 - Upper Body:**
- Push-ups: 3 sets of 10 reps
- Plank: 3 sets of 30 seconds
- Burpees: 3 sets of 8 reps

**Day 4 - Core & Cardio:**
- Russian twists: 3 sets of 20 reps
- Plank: 3 sets of 45 seconds
- HIIT: 15 minutes

**Day 5 - Full Body:**
- Squats: 3 sets of 15 reps
- Push-ups: 3 sets of 10 reps
- Burpees: 3 sets of 10 reps

For nutrition: Aim for a 300-calorie deficit and drink plenty of water!

Check the YouTube links below for form tips. Ready to crush it?"

SAFETY:
- Always recommend warm-up before workouts
- Emphasize proper form over quantity
- Suggest doctor consultation for serious health concerns
"""

# ==================== HELPER FUNCTIONS ====================
def remove_emojis(text: str) -> str:
    """Remove all emojis from a string."""
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U00002600-\U000026FF"  # Misc symbols
        "\U00002B00-\U00002BFF"  # Misc symbols & arrows
        "\U0001FA70-\U0001FAFF"  # Extended Pictographic
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
        "version": "2.0",
        "description": "Backend API for FitBot fitness coaching application",
        "features": [
            "AI-Powered Fitness Coaching",
            "Personalized Workout Plans",
            "Nutrition Guidance", 
            "YouTube Tutorial Recommendations",
            "Voice Input/Output Support (TTS/STT)",
            "Conversational AI Interface"
        ],
        "endpoints": {
            "health": "GET /health - Health check",
            "chat": "POST /chat - AI fitness chat",
            "tutorials": "GET /tutorials - List all exercises",
            "tutorial_by_exercise": "GET /tutorials/{exercise} - Get specific exercise tutorials",
            "tts": "POST /tts - Text to speech",
            "stt": "POST /stt - Speech to text"
        },
        "documentation": "/docs",
        "note": "This is an API-only service. Connect your frontend to these endpoints."
    })

@app.get("/ping")
async def ping():
    return {"message": "pong", "service": "FitBot Fitness Assistant"}

# ==================== CHAT ENDPOINT ====================
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not groq_client:
            raise HTTPException(status_code=503, detail="Groq Client not initialized. Check API Key.")

        user_id = request.user_id
        user_message = request.message.strip()
        
        # Use chat history from client (they manage their own state)
        chat_history = request.chat_history if request.chat_history else []
        
        # Prepare messages for Groq
        messages = [{"role": "system", "content": TRAINER_SYSTEM_PROMPT}]
        
        # Add recent chat history (last 10 messages for context)
        for msg in chat_history[-10:]:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
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
        
        # Find relevant YouTube tutorials based on AI response and user message
        tutorials = find_relevant_tutorials(reply_text + " " + user_message)
        
        # Build updated history
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

# ==================== EXERCISE TUTORIALS ENDPOINT ====================
@app.get("/tutorials/{exercise}")
async def get_exercise_tutorials(exercise: str):
    """Get YouTube tutorials for a specific exercise"""
    try:
        exercise_lower = exercise.lower().strip()
        
        # Direct match
        if exercise_lower in YOUTUBE_TUTORIALS:
            return JSONResponse({
                "exercise": exercise.title(),
                "tutorials": YOUTUBE_TUTORIALS[exercise_lower],
                "count": len(YOUTUBE_TUTORIALS[exercise_lower])
            })
        
        # Partial match
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
            "message": f"No tutorials found for '{exercise}'. Try: squats, push ups, deadlift, etc.",
            "available_exercises": list(YOUTUBE_TUTORIALS.keys())
        }, status_code=404)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tutorials")
async def list_all_exercises():
    """List all available exercises with tutorial links"""
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

# ==================== TTS & STT ====================
@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    """Convert text to speech"""
    try:
        clean_text = clean_text_for_tts(req.text)
        tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(text=clean_text, lang=req.language_code)
        tts.save(tmp_mp3.name)

        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3.name, "-ar", "44100", "-ac", "2", tmp_wav.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        os.remove(tmp_mp3.name)
        return FileResponse(tmp_wav.name, media_type="audio/wav", filename="speech.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")

recognizer = sr.Recognizer()
@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """Convert speech to text"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
        
        os.remove(tmp_path)
        return JSONResponse({"transcript": transcript})
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand audio")
    except sr.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Speech recognition service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")

# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "FitBot AI Fitness Assistant",
        "groq_connected": groq_client is not None,
        "total_exercises": len(YOUTUBE_TUTORIALS),
        "storage": "Client-side (no server storage)",
        "features": [
            "Personalized Workout Plans",
            "Nutrition Guidance", 
            "YouTube Tutorial Recommendations",
            "Voice Input/Output Support",
            "Fitness-Only Focus"
        ]
    })