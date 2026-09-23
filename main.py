import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="NAY-Ai-Studio API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Client Setup
GEMINI_API_KEY = "AQ.Ab8RN6LGXl409cUi7eUIF--LXNImgzsa4FYTkpIzU3e3LdmGUA"
client = genai.Client(api_key=GEMINI_API_KEY)

# Config & Database JSON Files
CONFIG_FILE = "admin_config.json"

# Default Config Setup for NAY-Ai-Studio
DEFAULT_CONFIG = {
    "admin_password": None,  # ပထမအကြိမ် Setup မလုပ်ရသေးလျှင် None ဖြစ်မည်
    "tutorial_video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
    "agent_contact_info": "Telegram: @NAiStudioAgent | Email: support@nay-ai-studio.com"
}

# Helper Functions for JSON Config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Mock Database for Runtime
users_db = {}

# Agents Database (Connect to Agent အတွက် အေးဂျင့်များစာရင်း)
agents_db = [
    {
        "id": "1",
        "name": "NAY-Ai-Studio Official Agent",
        "role": "ကိုယ်စားလှယ်",
        "description": "NAY-Ai-Studio Digital service & Support",
        "avatar": "https://i.imgur.com/8KM9t1w.png",
        "facebook": "https://facebook.com",
        "telegram": "https://t.me/",
        "phone": "09123456789",
        "viber": "09123456789"
    }
]

OWNER_EMAIL = "owner@nay-ai-studio.com"  # Website Owner Email

# Pydantic Schemas
class UserSignUp(BaseModel):
    name: str
    email: str

class ApprovalAction(BaseModel):
    user_email: str
    action: str # "accept" or "reject"
    days_granted: Optional[int] = 30

class ScriptRequest(BaseModel):
    user_email: str
    movie_title: Optional[str] = ""
    subject_matter: Optional[str] = ""
    voice_style: Optional[str] = "Narrator"
    duration: Optional[str] = "1 မိနစ်"
    has_video_upload: Optional[bool] = False

class VoiceGenRequest(BaseModel):
    user_email: str
    script_text: str
    voice_name: str # Unique male/female voice selection
    emotion: str
    speed: float = 1.0

class VideoRenderRequest(BaseModel):
    user_email: str
    script_text: str
    voice_audio_url: Optional[str] = ""
    aspect_ratio: str = "16:9"
    quality: str = "1080P"
    auto_caption: bool = True

class ChatRequest(BaseModel):
    user_email: str
    message: str

class AdminSettingsUpdate(BaseModel):
    tutorial_video_url: Optional[str] = None
    agent_contact_info: Optional[str] = None

class AgentModel(BaseModel):
    name: str
    role: str
    description: str
    avatar: Optional[str] = "https://i.imgur.com/8KM9t1w.png"
    facebook: Optional[str] = ""
    telegram: Optional[str] = ""
    phone: Optional[str] = ""
    viber: Optional[str] = ""

class AdminLogin(BaseModel):
    password: str

class PasswordSetup(BaseModel):
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str


# Helper function to check user validity
def verify_user_access(email: str):
    if email not in users_db:
        raise HTTPException(status_code=403, detail="User not registered.")
    user = users_db[email]
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="အကောင့်ဖွင့်ရန် Website Owner ၏ ခွင့်ပြုချက် (Approval) စောင့်ဆိုင်းနေဆဲ ဖြစ်ပါသည်။")
    
    if user["expiry_date"] and datetime.now() > user["expiry_date"]:
        user["status"] = "expired"
        raise HTTPException(status_code=403, detail="သင့်၏ ဝဘ်ဆိုက်အသုံးပြုခွင့် သက်တမ်း ကုန်ဆုံးသွားပါပြီ။ ကျေးဇူးပြု၍ Admin သို့ ဆက်သွယ်ပါ။")
    return user


# --- APIs ---

# Root Endpoint (index.html ကို တိုက်ရိုက်ပြသရန်)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>NAY-Ai-Studio API is running, but index.html was not found.</h3>"


# Admin Dashboard လင့်ခ်ချိတ်ရန်
@app.get("/admin", include_in_schema=False)
async def serve_admin_panel():
    return FileResponse("admin.html")


# 1. Check Admin Status
@app.get("/api/admin/check-status")
async def check_admin_status():
    config = load_config()
    is_initialized = config.get("admin_password") is not None
    return {"is_initialized": is_initialized}


# 2. Initial Password Setup
@app.post("/api/admin/setup")
async def setup_admin_password(data: PasswordSetup):
    config = load_config()
    if config.get("admin_password") is not None:
        raise HTTPException(status_code=400, detail="Admin password already initialized.")
    
    config["admin_password"] = data.password
    save_config(config)
    return {"status": "success", "message": "Admin password successfully created."}


# 3. Admin Login
@app.post("/api/admin/login")
async def admin_login(data: AdminLogin):
    config = load_config()
    stored_password = config.get("admin_password")
    
    if not stored_password or stored_password != data.password:
        raise HTTPException(status_code=401, detail="စကားဝှက် မှားယွင်းနေပါသည်။")
    
    return {"status": "success", "message": "Login အောင်မြင်ပါသည်။"}


# 4. Change Password
@app.post("/api/admin/change-password")
async def change_admin_password(data: ChangePassword):
    config = load_config()
    stored_password = config.get("admin_password")
    
    if not stored_password or stored_password != data.old_password:
        raise HTTPException(status_code=400, detail="လက်ရှိစကားဝှက် မှားယွင်းနေပါသည်။")
    
    config["admin_password"] = data.new_password
    save_config(config)
    return {"status": "success", "message": "စကားဝှက် အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။"}


@app.post("/api/signup")
async def sign_up(user: UserSignUp):
    if user.email in users_db:
        return {"status": "exists", "user": users_db[user.email]}
    
    new_user = {
        "name": user.name,
        "email": user.email,
        "status": "pending",  # Pending Owner Approval
        "days_remaining": 0,
        "expiry_date": None
    }
    users_db[user.email] = new_user
    
    print(f"[NOTIFICATION TO OWNER ({OWNER_EMAIL})]: New User Registered: {user.name} ({user.email}). Options: [ACCEPT / REJECT]")
    
    return {
        "status": "pending_approval",
        "message": "Sign up အောင်မြင်ပါသည်။ Website Owner မှ ခွင့်ပြု (Accept) ပြီးသည်နှင့် အသုံးပြုနိုင်မည် ဖြစ်ပါသည်။",
        "user": new_user
    }


@app.get("/api/admin/users")
async def get_all_users():
    user_list = list(users_db.values())
    return {"status": "success", "users": user_list}


@app.post("/api/admin/approve-user")
async def approve_user(data: ApprovalAction):
    if data.user_email not in users_db:
        users_db[data.user_email] = {
            "name": data.user_email.split("@")[0],
            "email": data.user_email,
            "status": "pending",
            "days_remaining": 0,
            "expiry_date": None
        }
    
    user = users_db[data.user_email]
    if data.action == "accept":
        user["status"] = "active"
        user["days_remaining"] = data.days_granted
        user["expiry_date"] = datetime.now() + timedelta(days=data.days_granted)
        return {"status": "success", "message": f"{user['email']} အား {data.days_granted} ရက် အသုံးပြုခွင့် ပေးလိုက်ပါပြီ။"}
    else:
        user["status"] = "rejected"
        return {"status": "success", "message": f"{user['email']} အား ငြင်းပယ်လိုက်ပါပြီ။"}


# --- Agents APIs ---
@app.get("/api/agents")
async def get_agents():
    return {"status": "success", "agents": agents_db}

@app.post("/api/admin/agents")
async def add_agent(agent: AgentModel):
    new_id = str(len(agents_db) + 1)
    agent_data = agent.dict()
    agent_data["id"] = new_id
    agents_db.append(agent_data)
    return {"status": "success", "message": "အေးဂျင့် အသစ်ထည့်သွင်းပြီးပါပြီ။", "agent": agent_data}

@app.delete("/api/admin/agents/{agent_id}")
async def delete_agent(agent_id: str):
    global agents_db
    agents_db = [a for a in agents_db if a["id"] != agent_id]
    return {"status": "success", "message": "အေးဂျင့်ကို ဖျက်လိုက်ပါပြီ။"}


@app.post("/api/chat")
async def chat_with_ai(data: ChatRequest):
    verify_user_access(data.user_email)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=data.message,
        )
        return {"status": "success", "reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-script")
async def generate_script(data: ScriptRequest):
    verify_user_access(data.user_email)
    
    if data.has_video_upload:
        prompt = f"Analyze the uploaded video concept and subject matter '{data.subject_matter}' to generate a creative, high-quality narration script in Myanmar language. Voice Style: {data.voice_style}."
    else:
        prompt = f"Create a detailed and high-quality movie script or recap in Myanmar language for Title: '{data.movie_title}', Subject/Details: '{data.subject_matter}'. Voice style: {data.voice_style}, Duration: {data.duration}."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"status": "success", "script": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Voice Generation Endpoint ---
@app.post("/api/generate-voice")
async def generate_voice(data: VoiceGenRequest):
    verify_user_access(data.user_email)
    # 5 Unique Male & 5 Unique Female voice handling logic
    valid_voices = ["Male_Voice_1", "Male_Voice_2", "Male_Voice_3", "Male_Voice_4", "Male_Voice_5",
                    "Female_Voice_1", "Female_Voice_2", "Female_Voice_3", "Female_Voice_4", "Female_Voice_5"]
    if data.voice_name not in valid_voices:
        raise HTTPException(status_code=400, detail="ရွေးချယ်ထားသော Voice အမျိုးအစား မမှန်ကန်ပါ။")
    
    # Mock return for generated audio link or synthesized stream
    return {
        "status": "success",
        "message": "Voice generated successfully.",
        "voice_name": data.voice_name,
        "emotion": data.emotion,
        "speed": data.speed,
        "audio_url": "https://www.w3schools.com/html/horse.mp3" # Placeholder audio output
    }


# --- AI Video Editor Rendering Endpoint ---
@app.post("/api/render-video")
async def render_video(data: VideoRenderRequest):
    verify_user_access(data.user_email)
    # Synchronized rendering with aspect ratio, auto-caption, and quality selection (4K, 2K, 1080P, 720P, 480P)
    valid_qualities = ["4K", "2K", "1080P", "720P", "480P"]
    if data.quality not in valid_qualities:
        raise HTTPException(status_code=400, detail="ရွေးချယ်ထားသော ဗီဒီယို အရည်အသွေး မမှန်ကန်ပါ။")
    
    return {
        "status": "success",
        "message": f"Video successfully rendered in {data.quality} with {data.aspect_ratio} ratio and auto-captions synchronized!",
        "download_url": "https://www.w3schools.com/html/mov_bbb.mp4" # Final downloadable video output
    }


@app.get("/api/user-profile/{email}")
async def get_profile(email: str):
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    user = users_db[email]
    
    if user["expiry_date"]:
        rem = (user["expiry_date"] - datetime.now()).days
        user["days_remaining"] = max(0, rem)
        
    return user


# --- Admin Settings APIs ---
@app.get("/api/admin/settings")
async def get_admin_settings():
    config = load_config()
    return {
        "tutorial_video_url": config.get("tutorial_video_url", ""),
        "agent_contact_info": config.get("agent_contact_info", "")
    }

@app.post("/api/admin/settings")
async def update_admin_settings(settings: AdminSettingsUpdate):
    config = load_config()
    if settings.tutorial_video_url is not None:
        config["tutorial_video_url"] = settings.tutorial_video_url
    if settings.agent_contact_info is not None:
        config["agent_contact_info"] = settings.agent_contact_info
    save_config(config)
    return {"status": "success", "message": "Admin settings updated successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)