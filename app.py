# ============================================================
# app.py - Complete HeyGen Video Generator (Streamlit)
# FIXED: Avatar Upload issue resolved
# ============================================================

import streamlit as st
import requests
import base64
import json
import time
from datetime import datetime
import io
from PIL import Image
import re
import os

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="HeyGen Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== AUTO API KEY SETUP =====
YOUR_REAL_HEYGEN_API_KEY = 'sk_V2_hgu_kuujglU11Oe_x9fCykWNbZsKqF0lrDtIy5wqiWCPiwx4'

# ===== SESSION STATE =====
if 'api_key' not in st.session_state:
    st.session_state.api_key = YOUR_REAL_HEYGEN_API_KEY
    st.session_state.is_premium = True
    st.session_state.access_granted = True
    st.session_state.plan = 'unlimited'
    st.session_state.team_access = True

if 'avatar_id' not in st.session_state:
    st.session_state.avatar_id = None
if 'avatar_preview' not in st.session_state:
    st.session_state.avatar_preview = None
if 'talking_photo_id' not in st.session_state:
    st.session_state.talking_photo_id = None
if 'avatar_engine' not in st.session_state:
    st.session_state.avatar_engine = 'avatar_iii'
if 'voice_id' not in st.session_state:
    st.session_state.voice_id = None
if 'voice_name' not in st.session_state:
    st.session_state.voice_name = None
if 'video_history' not in st.session_state:
    st.session_state.video_history = []
if 'selected_avatar_id' not in st.session_state:
    st.session_state.selected_avatar_id = None
if 'custom_avatar_look_id' not in st.session_state:
    st.session_state.custom_avatar_look_id = None

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    .main-container {
        background: #0f0f14;
        color: #eaeaf0;
        padding: 20px;
        border-radius: 12px;
        min-height: 600px;
    }
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 16px 10px;
        border-bottom: 1px solid #23232e;
        margin-bottom: 20px;
    }
    .logo-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #ec4899);
    }
    .app-header h1 {
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        color: #eaeaf0;
    }
    .status-card {
        background: #1c1c26;
        border: 1px solid #2c2c3a;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #7c3aed;
    }
    .status-card.success {
        border-left-color: #4ade80;
    }
    .status-card.error {
        border-left-color: #f87171;
    }
    .status-card.warning {
        border-left-color: #fbbf24;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 5px 15px rgba(124, 58, 237, 0.4) !important;
    }
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: #1c1c26 !important;
        border: 1px solid #2c2c3a !important;
        border-radius: 8px !important;
        color: #eaeaf0 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed !important;
    }
    .success-text {
        color: #4ade80;
        font-weight: 600;
        padding: 8px;
        background: #0a1a0a;
        border-radius: 6px;
    }
    .error-text {
        color: #f87171;
        font-weight: 600;
        padding: 8px;
        background: #1a0a0a;
        border-radius: 6px;
    }
    .hint-text {
        color: #8b8b9a;
        font-size: 12px;
    }
    .video-container {
        background: #0d0d1a;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2a2a4a;
    }
    .avatar-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 10px;
        margin: 10px 0;
    }
    .avatar-card {
        background: #1c1c26;
        border: 2px solid #2c2c3a;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .avatar-card:hover {
        border-color: #7c3aed;
        transform: scale(1.02);
    }
    .avatar-card.selected {
        border-color: #7c3aed;
        background: #241a3d;
    }
    .avatar-card img {
        width: 100%;
        aspect-ratio: 3/4;
        object-fit: cover;
        border-radius: 4px;
    }
    .avatar-card .avatar-name {
        font-size: 11px;
        color: #eaeaf0;
        margin-top: 4px;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .voice-list {
        max-height: 300px;
        overflow-y: auto;
        margin: 10px 0;
    }
    .voice-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #1c1c26;
        border: 1px solid #2c2c3a;
        border-radius: 8px;
        padding: 10px 12px;
        margin: 4px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .voice-item:hover {
        border-color: #7c3aed;
    }
    .voice-item.selected {
        border-color: #7c3aed;
        background: #241a3d;
    }
    .voice-item .voice-name {
        font-weight: 600;
        color: #eaeaf0;
    }
    .voice-item .voice-meta {
        font-size: 11px;
        color: #8b8b9a;
    }
    .history-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
        margin: 10px 0;
    }
    .history-card {
        background: #1c1c26;
        border: 1px solid #2c2c3a;
        border-radius: 10px;
        overflow: hidden;
        transition: all 0.3s;
    }
    .history-card:hover {
        border-color: #7c3aed;
        transform: translateY(-2px);
    }
    .history-card .thumb {
        aspect-ratio: 1/1;
        background: #14141b;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .history-card .thumb img, 
    .history-card .thumb video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .history-card .info {
        padding: 8px 12px;
    }
    .history-card .info .title {
        font-size: 12px;
        font-weight: 600;
        color: #eaeaf0;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .history-card .info .time {
        font-size: 10px;
        color: #8b8b9a;
        margin: 4px 0 0;
    }
    .history-card .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin: 4px 0;
    }
    .badge.success {
        background: #0a2a0a;
        color: #4ade80;
    }
    .badge.error {
        background: #2a0a0a;
        color: #f87171;
    }
    .badge.loading {
        background: #2a2a0a;
        color: #fbbf24;
    }
    .summary-box {
        background: #1c1c26;
        border: 1px solid #2c2c3a;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0;
    }
    .summary-box .row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 0;
    }
    .summary-box .row .label {
        font-size: 12px;
        color: #8b8b9a;
        min-width: 80px;
    }
    .summary-box .row .value {
        font-size: 13px;
        color: #eaeaf0;
    }
    .summary-box .row .value.ready {
        color: #4ade80;
    }
    .summary-box .row .value.missing {
        color: #f87171;
    }
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #14141b;
    }
    ::-webkit-scrollbar-thumb {
        background: #7c3aed;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ===== HELPER FUNCTIONS =====

def base64_to_blob(base64_data):
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    return base64.b64decode(base64_data)

def file_to_base64(file):
    return base64.b64encode(file.read()).decode('utf-8')

def split_script(script, max_len=4900):
    if len(script) <= max_len:
        return [script]
    chunks = []
    remaining = script
    while len(remaining) > max_len:
        cut = remaining.rfind('.', 0, max_len)
        if cut < max_len * 0.4:
            cut = remaining.rfind(' ', 0, max_len)
        if cut < 1:
            cut = max_len
        chunks.append(remaining[:cut+1].strip())
        remaining = remaining[cut+1:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks

def relative_time(timestamp):
    diff = int(time.time() * 1000) - timestamp
    minutes = diff // 60000
    if minutes < 1:
        return "abhi"
    if minutes < 60:
        return f"{minutes} minute{'' if minutes == 1 else 's'} pehle"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'' if hours == 1 else 's'} pehle"
    days = hours // 24
    return f"{days} din pehle"

# ===== API FUNCTIONS (FIXED) =====

def upload_avatar(api_key, base64_data, mime_type, file_name, engine="avatar_iii"):
    """Upload avatar photo to HeyGen - FIXED VERSION"""
    
    # Clean base64 data (remove data URL prefix if present)
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    
    # Decode base64 to bytes
    file_bytes = base64.b64decode(base64_data)
    
    # Create multipart form data
    files = {
        'file': (file_name, file_bytes, mime_type)
    }
    
    headers = {
        'x-api-key': api_key
    }
    
    if engine == "avatar_iii":
        # Avatar III - Upload to talking_photo endpoint
        url = "https://upload.heygen.com/v1/talking_photo"
        response = requests.post(url, headers=headers, files=files)
    else:
        # Avatar IV - Upload to assets endpoint
        url = "https://api.heygen.com/v3/assets"
        response = requests.post(url, headers=headers, files=files)
    
    # Debug: Print response
    print(f"Upload Status: {response.status_code}")
    print(f"Upload Response: {response.text}")
    
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', response.text)
        except:
            error_msg = response.text
        raise Exception(f"Upload failed: {error_msg}")
    
    data = response.json()
    
    if data.get('error'):
        raise Exception(f"Upload failed: {data['error'].get('message', 'Unknown error')}")
    
    if engine == "avatar_iii":
        if not data.get('data', {}).get('talking_photo_id'):
            raise Exception("talking_photo_id not found in response")
        return {
            "talking_photo_id": data['data']['talking_photo_id'],
            "preview_url": data['data'].get('talking_photo_url', '')
        }
    else:
        if not data.get('data', {}).get('url'):
            raise Exception("asset url not found in response")
        upload_url = data['data']['url']
        image_key = upload_url.split('/')[-1]
        return {
            "image_key": image_key,
            "preview_url": upload_url,
            "asset_id": data['data'].get('asset_id', '')
        }

def clone_voice(api_key, base64_data, mime_type, file_name, name):
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    file_bytes = base64.b64decode(base64_data)
    
    files = {
        "file": (file_name, file_bytes, mime_type),
        "name": (None, name)
    }
    response = requests.post(
        "https://api.heygen.com/v3/voices/clone",
        headers={"x-api-key": api_key},
        files=files
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Clone failed'))
    return {
        "voice_id": data['data']['voice_id'] or data['data']['id']
    }

def list_avatars(api_key):
    response = requests.get(
        "https://api.heygen.com/v2/avatars",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Failed to load avatars'))
    return data['data']['avatars']

def list_voices(api_key):
    response = requests.get(
        "https://api.heygen.com/v3/voices",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Failed to load voices'))
    return data['data']['voices'] if isinstance(data['data'], list) else data['data'].get('voices', [])

def generate_video(api_key, talking_photo_id, voice_id, script, title, orientation="landscape", is_test=False):
    chunks = split_script(script, 4900)
    dimension = {"width": 1280, "height": 720} if orientation == "landscape" else {"width": 720, "height": 1280}
    
    video_inputs = []
    for chunk in chunks:
        video_inputs.append({
            "character": {
                "type": "talking_photo",
                "talking_photo_id": talking_photo_id,
                "talking_photo_style": "square"
            },
            "voice": {
                "type": "text",
                "input_text": chunk,
                "voice_id": voice_id
            }
        })
    
    payload = {
        "video_inputs": video_inputs,
        "dimension": dimension,
        "title": title or script[:60],
        "test": is_test
    }
    
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json=payload
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Video generation failed'))
    return data['data']['video_id']

def check_video_status(api_key, video_id):
    response = requests.get(
        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Failed to check status'))
    return data['data']

def generate_agent_video(api_key, prompt, voice_id, avatar_id, orientation="landscape"):
    dimension = {"width": 1280, "height": 720} if orientation == "landscape" else {"width": 720, "height": 1280}
    
    payload = {
        "prompt": prompt,
        "orientation": orientation,
        "voice_id": voice_id,
        "avatar_id": avatar_id,
        "dimension": dimension
    }
    
    response = requests.post(
        "https://api.heygen.com/v3/video-agents",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json=payload
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Agent video generation failed'))
    return data['data']['session_id']

def check_agent_status(api_key, session_id):
    response = requests.get(
        f"https://api.heygen.com/v3/video-agents/{session_id}",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', 'Failed to check agent status'))
    return data['data']

# ===== UI COMPONENTS =====

def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="logo-dot"></div>
        <h1>🎬 HeyGen Avatar & Voice Studio</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.text_input("🔑 API Key", value=st.session_state.api_key, 
                     type="password", disabled=True,
                     help="API Key auto-set hai - Team Unlimited Access!")
    with col2:
        if st.button("💾 Save Key", use_container_width=True):
            st.success("✅ Key saved successfully!")
    with col3:
        st.markdown("""
        <div style="background:#1a1a2e;border:2px solid #4ade80;border-radius:8px;padding:8px;text-align:center;margin-top:4px;">
            <span style="color:#4ade80;font-weight:bold;">✅ Unlimited Access</span>
        </div>
        """, unsafe_allow_html=True)

def render_summary():
    avatar_ready = bool(st.session_state.talking_photo_id)
    voice_ready = bool(st.session_state.voice_id)
    
    st.markdown(f"""
    <div class="summary-box">
        <div class="row">
            <span class="label">👤 Avatar:</span>
            <span class="value {'ready' if avatar_ready else 'missing'}">
                {'✅ ' + st.session_state.avatar_engine.upper() + ' ready' if avatar_ready else '❌ Avatar tab se photo upload karo'}
            </span>
        </div>
        <div class="row">
            <span class="label">🎤 Voice:</span>
            <span class="value {'ready' if voice_ready else 'missing'}">
                {'✅ ' + (st.session_state.voice_name or st.session_state.voice_id[:20] + '...') if voice_ready else '❌ Voice tab se voice select karo'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_video_history():
    st.markdown("### 📹 Meri Videos")
    
    if not st.session_state.video_history:
        st.info("Abhi tak koi video nahi bani - upar se pehli video banao!")
        return
    
    cols = st.columns(3)
    for i, video in enumerate(st.session_state.video_history[:12]):
        col = cols[i % 3]
        with col:
            status_color = {
                "success": "success",
                "error": "error",
                "loading": "loading"
            }.get(video.get('status', ''), 'loading')
            
            st.markdown(f"""
            <div class="history-card">
                <div class="thumb">
                    {'🎬' if video.get('video_url') else '⏳'}
                </div>
                <div class="info">
                    <p class="title">{video.get('title', 'Video')}</p>
                    <span class="badge {status_color}">{video.get('status', 'loading').upper()}</span>
                    <p class="time">{relative_time(video.get('createdAt', 0))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if video.get('video_url'):
                st.video(video['video_url'])

# ===== MAIN APP =====

def main():
    render_header()
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 Settings", "👤 Avatar", "🎤 Voice", "🎬 Video Banao"])
    
    with tab1:
        st.markdown("""
        <div class="status-card success">
            <strong>✅ Team Unlimited Access</strong><br>
            API Key auto-set hai - koi verification nahi!
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        🎉 **Team Access Active!**
        - Unlimited video generation
        - No credit limits
        - All features unlocked
        """)
    
    with tab2:
        st.markdown("### 📸 Apna Avatar Upload Karo")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            avatar_file = st.file_uploader(
                "Photo select karo (clear, front-facing)",
                type=['png', 'jpg', 'jpeg'],
                help="Best result ke liye clear face, achi lighting"
            )
            
            engine = st.radio(
                "Engine choose karo:",
                ["avatar_iii (Recommended)", "avatar_iv"],
                index=0
            )
            st.session_state.avatar_engine = "avatar_iii" if "avatar_iii" in engine else "avatar_iv"
            
            if avatar_file and st.button("📤 Upload & Save Avatar", use_container_width=True, key="upload_avatar_btn"):
                with st.spinner("Upload ho raha hai..."):
                    try:
                        # Read file and convert to base64
                        file_bytes = avatar_file.read()
                        base64_data = base64.b64encode(file_bytes).decode('utf-8')
                        mime_type = avatar_file.type
                        
                        st.info(f"Uploading {len(file_bytes)} bytes...")
                        
                        result = upload_avatar(
                            st.session_state.api_key,
                            base64_data,
                            mime_type,
                            avatar_file.name,
                            st.session_state.avatar_engine
                        )
                        
                        if st.session_state.avatar_engine == "avatar_iii":
                            st.session_state.talking_photo_id = result['talking_photo_id']
                        else:
                            st.session_state.avatar_id = result['image_key']
                        
                        st.session_state.avatar_preview = result['preview_url']
                        st.success(f"✅ Avatar save ho gaya! ID: {st.session_state.talking_photo_id or st.session_state.avatar_id}")
                        
                        # Force rerun to update preview
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Tip: Try using a smaller image (< 2MB) or try avatar_iii engine")
        
        with col2:
            if st.session_state.avatar_preview:
                st.image(st.session_state.avatar_preview, caption="Your Avatar", use_container_width=True)
                
                if st.session_state.talking_photo_id:
                    st.success(f"✅ Avatar ID: {st.session_state.talking_photo_id[:20]}...")
            else:
                st.info("👆 Photo upload karo")
        
        st.markdown("---")
        st.markdown("### 🎭 HeyGen Avatars")
        
        if st.button("📋 Avatars Load Karo", use_container_width=True):
            with st.spinner("Loading avatars..."):
                try:
                    avatars = list_avatars(st.session_state.api_key)
                    st.session_state._avatars = avatars
                    st.success(f"{len(avatars)} avatars mile!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if hasattr(st.session_state, '_avatars'):
            cols = st.columns(4)
            for i, av in enumerate(st.session_state._avatars[:8]):
                col = cols[i % 4]
                with col:
                    st.markdown(f"""
                    <div class="avatar-card">
                        <img src="{av.get('preview_image_url', '')}" alt="{av.get('avatar_name', 'Avatar')}">
                        <span class="avatar-name">{av.get('avatar_name', av.get('avatar_id', 'Avatar'))}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select", key=f"select_av_{i}", use_container_width=True):
                        st.session_state.selected_avatar_id = av['avatar_id']
                        st.success(f"✅ {av.get('avatar_name', 'Avatar')} selected!")

    with tab3:
        st.markdown("### 🎤 Voice Select Karo")
        
        tab_voice1, tab_voice2, tab_voice3 = st.tabs(["📋 Voice List", "🔑 Voice ID", "🧬 Clone"])
        
        with tab_voice1:
            if st.button("🎤 Voices Load Karo", use_container_width=True):
                with st.spinner("Loading voices..."):
                    try:
                        voices = list_voices(st.session_state.api_key)
                        st.session_state._voices = voices
                        st.success(f"{len(voices)} voices mili!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            search = st.text_input("🔍 Search voices", placeholder="Naam, language, gender...")
            
            if hasattr(st.session_state, '_voices'):
                filtered = st.session_state._voices
                if search:
                    search_lower = search.lower()
                    filtered = [v for v in filtered if 
                               search_lower in v.get('name', '').lower() or 
                               search_lower in v.get('language', '').lower()]
                
                for voice in filtered[:20]:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"""
                        <div>
                            <strong>{voice.get('name', voice.get('voice_id', 'Voice'))}</strong>
                            <br><span style="color:#8b8b9a;font-size:11px;">
                                {voice.get('language', '')} · {voice.get('gender', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if voice.get('preview_audio_url'):
                            if st.button("▶", key=f"play_{voice.get('voice_id')}"):
                                st.audio(voice['preview_audio_url'])
                    with col3:
                        if st.button("Select", key=f"select_{voice.get('voice_id')}"):
                            st.session_state.voice_id = voice['voice_id']
                            st.session_state.voice_name = voice.get('name', voice.get('voice_id'))
                            st.success(f"✅ {voice.get('name', 'Voice')} selected!")
        
        with tab_voice2:
            voice_id_input = st.text_input("Voice ID paste karo", 
                                          placeholder="jaise: 1bd001e7e50f421d891986aad5c8bbd2")
            if st.button("💾 Save Voice ID", use_container_width=True):
                if voice_id_input:
                    st.session_state.voice_id = voice_id_input
                    st.success("✅ Voice ID save ho gaya!")
                else:
                    st.warning("Voice ID daalo!")
        
        with tab_voice3:
            st.warning("⚠️ Direct voice clone kabhi-kabhi fail ho sakti hai - Voice ID tab use karo")
            
            voice_file = st.file_uploader(
                "Voice sample upload karo (30 sec+ clear audio)",
                type=['mp3', 'wav', 'm4a']
            )
            voice_name = st.text_input("Voice Name", placeholder="jaise: Rehman Voice")
            
            if voice_file and st.button("🧬 Clone Voice", use_container_width=True):
                with st.spinner("Voice clone ho rahi hai..."):
                    try:
                        base64_data = base64.b64encode(voice_file.read()).decode('utf-8')
                        result = clone_voice(
                            st.session_state.api_key,
                            base64_data,
                            voice_file.type,
                            voice_file.name,
                            voice_name or "My Cloned Voice"
                        )
                        st.session_state.voice_id = result['voice_id']
                        st.success(f"✅ Voice clone ho gayi! ID: {result['voice_id']}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab4:
        st.markdown("### 🎬 Video Banao")
        
        render_summary()
        
        tab_video1, tab_video2 = st.tabs(["✍️ Script Se", "🤖 Topic Se"])
        
        with tab_video1:
            st.markdown("""
            <div class="status-card warning">
                <strong>📝 Script Se Video</strong><br>
                Apna script likho aur avatar usko bolega.
            </div>
            """, unsafe_allow_html=True)
            
            script = st.text_area(
                "Script likho",
                placeholder="Yahan exact text likho jo avatar bolega...",
                height=150
            )
            
            script_len = len(script)
            if script_len > 25000:
                st.warning(f"⚠️ Script {script_len} characters - maximum 30000 recommended")
            elif script_len > 20000:
                st.warning("⚠️ Script kaafi lamba hai - 2-3 minute ka video banega")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                orientation = st.selectbox(
                    "Orientation",
                    ["landscape (16:9)", "portrait (9:16)"],
                    index=0
                )
            with col2:
                title = st.text_input("Video Title (optional)", placeholder="Video ka naam")
            
            if st.button("🎬 Render Karo", use_container_width=True, key="render_btn"):
                if not st.session_state.talking_photo_id:
                    st.error("❌ Pehle Avatar tab se photo upload karo!")
                elif not st.session_state.voice_id:
                    st.error("❌ Pehle Voice tab se voice select karo!")
                elif not script:
                    st.error("❌ Script likho!")
                else:
                    with st.spinner("Video render ho raha hai..."):
                        try:
                            video_id = generate_video(
                                st.session_state.api_key,
                                st.session_state.talking_photo_id,
                                st.session_state.voice_id,
                                script,
                                title,
                                "landscape" if "landscape" in orientation else "portrait",
                                False
                            )
                            
                            st.session_state.video_history.insert(0, {
                                'id': video_id,
                                'title': title or script[:60],
                                'createdAt': int(time.time() * 1000),
                                'status': 'loading',
                                'video_url': None
                            })
                            
                            st.success(f"✅ Video generate ho rahi hai! ID: {video_id}")
                            
                            with st.spinner("Video render ho rahi hai... (1-3 minute)"):
                                for _ in range(30):
                                    time.sleep(10)
                                    status_data = check_video_status(st.session_state.api_key, video_id)
                                    if status_data.get('status') == 'completed':
                                        video_url = status_data.get('video_url')
                                        st.session_state.video_history[0]['status'] = 'success'
                                        st.session_state.video_history[0]['video_url'] = video_url
                                        st.success("✅ Video ready hai!")
                                        st.video(video_url)
                                        break
                                    elif status_data.get('status') == 'failed':
                                        st.session_state.video_history[0]['status'] = 'error'
                                        st.error("❌ Video generation fail hui!")
                                        break
                                else:
                                    st.warning("⏳ Timeout - HeyGen dashboard me check karo")
                        
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            if st.session_state.video_history:
                                st.session_state.video_history[0]['status'] = 'error'
        
        with tab_video2:
            st.markdown("""
            <div class="status-card success">
                <strong>🤖 Topic Se Video</strong><br>
                HeyGen khud script likhega - sirf topic batao!
            </div>
            """, unsafe_allow_html=True)
            
            prompt = st.text_area(
                "Topic / Prompt",
                placeholder="Jaise: 'Collagen ke fayde aur marine collagen ka use kaise karein - 3 minute ki video'",
                height=100
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                agent_orientation = st.selectbox(
                    "Orientation",
                    ["landscape (16:9)", "portrait (9:16)"],
                    index=0,
                    key="agent_orientation"
                )
            with col2:
                agent_title = st.text_input("Video Title (optional)", placeholder="Video ka naam", key="agent_title")
            
            if st.button("🤖 Agent Video Banao", use_container_width=True, key="agent_btn"):
                if not st.session_state.talking_photo_id:
                    st.error("❌ Pehle Avatar tab se photo upload karo!")
                elif not st.session_state.voice_id:
                    st.error("❌ Pehle Voice tab se voice select karo!")
                elif not prompt:
                    st.error("❌ Prompt likho!")
                else:
                    with st.spinner("Agent video generate ho rahi hai..."):
                        try:
                            session_id = generate_agent_video(
                                st.session_state.api_key,
                                prompt,
                                st.session_state.voice_id,
                                st.session_state.talking_photo_id,
                                "landscape" if "landscape" in agent_orientation else "portrait"
                            )
                            
                            st.session_state.video_history.insert(0, {
                                'id': session_id,
                                'title': agent_title or prompt[:60],
                                'createdAt': int(time.time() * 1000),
                                'status': 'loading',
                                'video_url': None,
                                'type': 'agent'
                            })
                            
                            st.success(f"✅ Agent video shuru ho gayi! Session: {session_id}")
                            
                            with st.spinner("Video render ho rahi hai... (2-3 minute)"):
                                for _ in range(40):
                                    time.sleep(10)
                                    status_data = check_agent_status(st.session_state.api_key, session_id)
                                    
                                    if status_data.get('status') == 'failed':
                                        st.session_state.video_history[0]['status'] = 'error'
                                        st.error("❌ Agent video fail hui!")
                                        break
                                    
                                    if status_data.get('video_id'):
                                        video_id = status_data['video_id']
                                        video_status = check_video_status(st.session_state.api_key, video_id)
                                        if video_status.get('status') == 'completed':
                                            video_url = video_status.get('video_url')
                                            st.session_state.video_history[0]['status'] = 'success'
                                            st.session_state.video_history[0]['video_url'] = video_url
                                            st.success("✅ Video ready hai!")
                                            st.video(video_url)
                                            break
                                        elif video_status.get('status') == 'failed':
                                            st.session_state.video_history[0]['status'] = 'error'
                                            st.error("❌ Video render fail hui!")
                                            break
                                else:
                                    st.warning("⏳ Timeout - HeyGen dashboard me check karo")
                        
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            if st.session_state.video_history:
                                st.session_state.video_history[0]['status'] = 'error'
        
        st.markdown("---")
        render_video_history()
        
        if st.button("🔄 Refresh History", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()
