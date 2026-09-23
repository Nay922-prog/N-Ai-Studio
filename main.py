from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS ချိတ်ဆက်ရန်
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserSignup(BaseModel):
    name: str
    email: str

class UserApproval(BaseModel):
    user_email: str
    action: str
    days_granted: int

class ChatRequest(BaseModel):
    user_email: str
    message: str

class ScriptRequest(BaseModel):
    user_email: str
    movie_title: str
    voice_style: str

class VoiceRequest(BaseModel):
    user_email: str
    script_text: str
    voice_name: str
    emotion: str
    speed: float

class VideoRequest(BaseModel):
    user_email: str
    script_text: str
    aspect_ratio: str
    quality: str
    auto_caption: bool

# Root Endpoint (ဆာဗာအလုပ်လုပ်ခြင်း ရှိမရှိ စစ်ဆေးရန်)
@app.get("/")
def read_root():
    return {"message": "NAY-Ai-Studio Backend Server is running successfully!"}

# API Endpoints တွေ
@app.post("/api/signup")
def signup(data: UserSignup):
    return {"status": "success", "message": f"User {data.email} registered successfully."}

@app.post("/api/admin/approve-user")
def approve_user(data: UserApproval):
    return {"status": "success", "message": f"User {data.user_email} approved for {data.days_granted} days."}

@app.post("/api/chat")
def chat_with_ai(data: ChatRequest):
    return {"reply": f"AI Assistant ရဲ့ တုံ့ပြန်ချက် - '{data.message}' ကို လက်ခံရရှိပါတယ်။"}

@app.post("/api/generate-script")
def generate_script(data: ScriptRequest):
    script_text = f"ခေါင်းစဉ်: {data.movie_title}\nစတိုင်: {data.voice_style}\n\n[ဇာတ်လမ်းအစ]\nဤသည်မှာ AI မှ အလိုအလျောက် ထုတ်လုပ်ပေးထားသော ဇာတ်ညွှန်းဖြစ်ပါသည်။"
    return {"script": script_text}

@app.post("/api/generate-voice")
def generate_voice(data: VoiceRequest):
    return {"audio_url": "https://www.w3schools.com/html/horse.ogg"}

@app.post("/api/render-video")
def render_video(data: VideoRequest):
    return {"message": "Video rendering completed!", "download_url": "https://www.w3schools.com/html/mov_bbb.mp4"}

@app.get("/api/agents")
def get_agents():
    return {
        "agents": [
            {
                "name": "Mg Mg",
                "role": "Support Lead",
                "description": "ဖောက်သည်များအား နည်းပညာအကူအညီပေးမည့် ကိုယ်စားလှယ်",
                "phone": "+95912345678",
                "avatar": "https://www.w3schools.com/howto/img_avatar.png"
            }
        ]
    }

@app.get("/api/user-profile/{email}")
def get_user_profile(email: str):
    return {
        "name": email.split('@')[0],
        "email": email,
        "status": "active",
        "days_remaining": 30
    }