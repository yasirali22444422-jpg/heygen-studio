# ============================================================
# app.py - EXACT SAME AS CHROME EXTENSION (Python Version)
# No changes - just converted from JavaScript to Python
# ============================================================

import streamlit as st
import requests
import base64
import json
import time
from datetime import datetime
import os

# ===== AUTO API KEY =====
YOUR_REAL_HEYGEN_API_KEY = 'sk_V2_hgu_kuujglU11Oe_x9fCykWNbZsKqF0lrDtIy5wqiWCPiwx4'

# ===== SESSION STATE =====
if 'api_key' not in st.session_state:
    st.session_state.api_key = YOUR_REAL_HEYGEN_API_KEY
    st.session_state.talking_photo_id = None
    st.session_state.avatar_preview_url = None
    st.session_state.voice_id = None
    st.session_state.voice_name = None
    st.session_state.avatar_engine = 'avatar_iii'
    st.session_state.video_history = []
    st.session_state.avatar_upload_state = None
    st.session_state.voice_clone_state = None

# ===== EXACT SAME FUNCTIONS AS BACKGROUND.JS =====

def base64_to_blob(base64_data):
    """EXACT same as background.js base64ToBlob"""
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    return base64.b64decode(base64_data)

def file_to_base64(file_bytes):
    """EXACT same as popup.js fileToBase64"""
    return base64.b64encode(file_bytes).decode('utf-8')

def upload_avatar(api_key, base64_data, mime_type, file_name, engine="avatar_iii"):
    """
    EXACT same as background.js uploadAvatar
    """
    blob = base64_to_blob(base64_data)
    
    # Register Avatar Look (EXACT same as background.js)
    # This runs in parallel - we'll do it synchronously here
    try:
        register_avatar_look(api_key, base64_data, mime_type, file_name)
    except Exception as e:
        print(f"Avatar look registration failed: {e}")
    
    if engine == "avatar_iii":
        # EXACT same as Avatar III upload
        url = "https://upload.heygen.com/v1/talking_photo"
        files = {
            'file': (file_name, blob, mime_type)
        }
        headers = {
            'x-api-key': api_key
        }
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        
        if response.status_code != 200 or data.get('error'):
            raise Exception(data.get('error', {}).get('message', f'Upload fail hua (HTTP {response.status})'))
        
        talking_photo_id = data['data']['talking_photo_id']
        preview_url = data['data']['talking_photo_url']
        
        if not talking_photo_id:
            raise Exception("talking_photo_id response me nahi mila")
        
        return {
            "talking_photo_id": talking_photo_id,
            "preview_url": preview_url,
            "engine": "avatar_iii"
        }
    else:
        # EXACT same as Avatar IV upload
        url = "https://api.heygen.com/v3/assets"
        files = {
            'file': (file_name, blob, mime_type)
        }
        headers = {
            'x-api-key': api_key
        }
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        
        if response.status_code != 200 or data.get('error'):
            raise Exception(data.get('error', {}).get('message', f'Upload fail hua (HTTP {response.status})'))
        
        upload_url = data['data']['url']
        image_key = upload_url.split('/')[-1]
        
        return {
            "image_key": image_key,
            "preview_url": upload_url,
            "engine": "avatar_iv"
        }

def register_avatar_look(api_key, base64_data, mime_type, name):
    """EXACT same as background.js registerAvatarLook"""
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    
    payload = {
        "type": "photo",
        "name": name or "My Avatar",
        "file": {
            "type": "base64",
            "media_type": mime_type,
            "data": base64_data
        }
    }
    
    response = requests.post(
        "https://api.heygen.com/v3/avatars",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Avatar look register nahi hua (HTTP {response.status})'))
    
    look_id = data['data']['avatar_item']['id']
    preview_url = data['data']['avatar_item']['preview_image_url']
    
    return {"look_id": look_id, "preview_url": preview_url}

def clone_voice(api_key, base64_data, mime_type, file_name, name):
    """EXACT same as background.js cloneVoice"""
    blob = base64_to_blob(base64_data)
    
    url = "https://api.heygen.com/v3/voices/clone"
    files = {
        'file': (file_name, blob, mime_type),
        'name': (None, name or "My Cloned Voice")
    }
    headers = {
        'x-api-key': api_key
    }
    
    response = requests.post(url, headers=headers, files=files)
    data = response.json()
    
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Clone fail hua (HTTP {response.status})'))
    
    voice_id = data['data']['voice_id'] or data['data']['id']
    if not voice_id:
        raise Exception("voice_id response me nahi mila")
    
    return {"voice_id": voice_id}

def list_avatars(api_key):
    """EXACT same as background.js listAvatars"""
    response = requests.get(
        "https://api.heygen.com/v2/avatars",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Avatars load nahi hue (HTTP {response.status})'))
    return data['data']['avatars']

def list_voices(api_key):
    """EXACT same as background.js listVoices"""
    response = requests.get(
        "https://api.heygen.com/v3/voices",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Voices load nahi hui (HTTP {response.status})'))
    
    voices = data['data'] if isinstance(data['data'], list) else data['data'].get('voices', [])
    return voices

def split_script(script, max_len=4900):
    """EXACT same as background.js splitScript"""
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

def generate_video(api_key, talking_photo_id, voice_id, script, title, orientation="landscape"):
    """EXACT same as background.js startRenderScene"""
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
        "title": title or "Render Scene"
    }
    
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Render fail hui (HTTP {response.status})'))
    
    video_id = data['data']['video_id']
    if not video_id:
        raise Exception("video_id response me nahi mila")
    
    return video_id

def check_video_status(api_key, video_id):
    """EXACT same as background.js checkVideoStatus"""
    response = requests.get(
        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Status check fail hui (HTTP {response.status})'))
    return data['data']

def generate_agent_video(api_key, prompt, voice_id, avatar_id, orientation="landscape"):
    """EXACT same as background.js startAgentVideo"""
    payload = {
        "prompt": prompt,
        "orientation": orientation or "landscape"
    }
    if voice_id:
        payload["voice_id"] = voice_id
    if avatar_id:
        payload["avatar_id"] = avatar_id
    
    response = requests.post(
        "https://api.heygen.com/v3/video-agents",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Agent request fail hui (HTTP {response.status})'))
    
    session_id = data['data']['session_id']
    if not session_id:
        raise Exception("session_id response me nahi mila")
    
    return session_id

def check_agent_status(api_key, session_id):
    """EXACT same as background.js checkSingleSession"""
    response = requests.get(
        f"https://api.heygen.com/v3/video-agents/{session_id}",
        headers={"x-api-key": api_key}
    )
    data = response.json()
    if response.status_code != 200 or data.get('error'):
        raise Exception(data.get('error', {}).get('message', f'Session check fail hui (HTTP {response.status})'))
    return data['data']

# ===== STREAMLIT UI =====

st.set_page_config(
    page_title="HeyGen Avatar & Voice Studio",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .main { padding: 20px; background: #0f0f14; }
    .stButton button { width: 100%; background: linear-gradient(135deg, #7c3aed, #ec4899); color: white; border: none; border-radius: 8px; padding: 10px; font-weight: bold; }
    .stButton button:hover { transform: scale(1.02); }
    .status-box { padding: 10px; border-radius: 8px; margin: 10px 0; }
    .success { background: #0a2a0a; border: 1px solid #4ade80; color: #4ade80; }
    .error { background: #2a0a0a; border: 1px solid #f87171; color: #f87171; }
    .info { background: #1a1a3a; border: 1px solid #7c3aed; color: #7c3aed; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #23232e;margin-bottom:20px;">
    <div style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#ec4899);"></div>
    <h1 style="color:#eaeaf0;font-size:20px;">🎬 HeyGen Avatar & Voice Studio</h1>
</div>
""", unsafe_allow_html=True)

# ===== TABS =====
tab1, tab2, tab3, tab4 = st.tabs(["🔑 Settings", "👤 Avatar", "🎤 Voice", "🎬 Video Banao"])

# ===== TAB 1: SETTINGS =====
with tab1:
    st.markdown("""
    <div style="background:#1a1a2e;border:2px solid #4ade80;border-radius:10px;padding:15px;margin:10px 0;">
        <strong style="color:#4ade80;">✅ Team Unlimited Access</strong><br>
        <span style="color:#8b8b9a;">API Key auto-set hai - koi verification nahi!</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.text_input("🔑 API Key", value=st.session_state.api_key, type="password", disabled=True)
    st.info("🎉 Unlimited Access Active! No credit limits!")

# ===== TAB 2: AVATAR =====
with tab2:
    st.markdown("### 📸 Apna Avatar Upload Karo")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        avatar_file = st.file_uploader("Photo select karo", type=['png', 'jpg', 'jpeg'])
        
        engine = st.radio(
            "Engine:",
            ["avatar_iii (Recommended)", "avatar_iv"],
            index=0
        )
        st.session_state.avatar_engine = "avatar_iii" if "avatar_iii" in engine else "avatar_iv"
        
        if avatar_file and st.button("📤 Upload & Save Avatar"):
            with st.spinner("Upload ho raha hai..."):
                try:
                    file_bytes = avatar_file.read()
                    base64_data = file_to_base64(file_bytes)
                    
                    result = upload_avatar(
                        st.session_state.api_key,
                        base64_data,
                        avatar_file.type,
                        avatar_file.name,
                        st.session_state.avatar_engine
                    )
                    
                    if result['engine'] == "avatar_iii":
                        st.session_state.talking_photo_id = result['talking_photo_id']
                    else:
                        st.session_state.avatar_id = result['image_key']
                    
                    st.session_state.avatar_preview_url = result['preview_url']
                    st.session_state.avatar_upload_state = "success"
                    
                    st.success("✅ Avatar save ho gaya!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.session_state.avatar_preview_url:
            st.image(st.session_state.avatar_preview_url, caption="Your Avatar", use_column_width=True)
            if st.session_state.talking_photo_id:
                st.info(f"🆔 ID: {st.session_state.talking_photo_id[:30]}...")
        else:
            st.info("👆 Photo upload karo")

# ===== TAB 3: VOICE =====
with tab3:
    st.markdown("### 🎤 Voice Select Karo")
    
    tab_v1, tab_v2, tab_v3 = st.tabs(["📋 Voice List", "🔑 Voice ID", "🧬 Clone"])
    
    with tab_v1:
        if st.button("🎤 Voices Load Karo"):
            with st.spinner("Loading voices..."):
                try:
                    voices = list_voices(st.session_state.api_key)
                    st.session_state._voices = voices
                    st.success(f"{len(voices)} voices mili!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if hasattr(st.session_state, '_voices'):
            search = st.text_input("🔍 Search")
            filtered = st.session_state._voices
            if search:
                search_lower = search.lower()
                filtered = [v for v in filtered if 
                           search_lower in v.get('name', '').lower() or 
                           search_lower in v.get('language', '').lower()]
            
            for voice in filtered[:20]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{voice.get('name', voice.get('voice_id'))}**")
                    st.caption(f"{voice.get('language', '')} · {voice.get('gender', '')}")
                with col2:
                    if voice.get('preview_audio_url'):
                        if st.button("▶", key=f"play_{voice.get('voice_id')}"):
                            st.audio(voice['preview_audio_url'])
                with col3:
                    if st.button("Select", key=f"sel_{voice.get('voice_id')}"):
                        st.session_state.voice_id = voice['voice_id']
                        st.session_state.voice_name = voice.get('name', voice.get('voice_id'))
                        st.success("✅ Selected!")
    
    with tab_v2:
        voice_id_input = st.text_input("Voice ID paste karo")
        if st.button("💾 Save Voice ID"):
            if voice_id_input:
                st.session_state.voice_id = voice_id_input
                st.success("✅ Voice ID save ho gaya!")
    
    with tab_v3:
        st.warning("⚠️ Direct clone kabhi-kabhi fail ho sakti hai")
        voice_file = st.file_uploader("Voice sample", type=['mp3', 'wav', 'm4a'])
        voice_name = st.text_input("Voice Name")
        
        if voice_file and st.button("🧬 Clone Voice"):
            with st.spinner("Clone ho rahi hai..."):
                try:
                    file_bytes = voice_file.read()
                    base64_data = file_to_base64(file_bytes)
                    result = clone_voice(
                        st.session_state.api_key,
                        base64_data,
                        voice_file.type,
                        voice_file.name,
                        voice_name
                    )
                    st.session_state.voice_id = result['voice_id']
                    st.success(f"✅ Clone ho gayi! ID: {result['voice_id']}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ===== TAB 4: VIDEO =====
with tab4:
    st.markdown("### 🎬 Video Banao")
    
    # Summary
    avatar_ready = bool(st.session_state.talking_photo_id)
    voice_ready = bool(st.session_state.voice_id)
    
    st.markdown(f"""
    <div style="background:#1c1c26;border:1px solid #2c2c3a;border-radius:10px;padding:12px;margin:10px 0;">
        <div>👤 Avatar: <span style="color:{'#4ade80' if avatar_ready else '#f87171'}">
            {'✅ Ready' if avatar_ready else '❌ Upload karo'}
        </span></div>
        <div>🎤 Voice: <span style="color:{'#4ade80' if voice_ready else '#f87171'}">
            {'✅ Ready' if voice_ready else '❌ Select karo'}
        </span></div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_vid1, tab_vid2 = st.tabs(["✍️ Script Se", "🤖 Topic Se"])
    
    with tab_vid1:
        script = st.text_area("Script likho", height=150)
        orientation = st.selectbox("Orientation", ["landscape", "portrait"])
        title = st.text_input("Title (optional)")
        
        if st.button("🎬 Render Karo"):
            if not st.session_state.talking_photo_id:
                st.error("❌ Pehle Avatar upload karo!")
            elif not st.session_state.voice_id:
                st.error("❌ Pehle Voice select karo!")
            elif not script:
                st.error("❌ Script likho!")
            else:
                with st.spinner("Video render ho rahi hai..."):
                    try:
                        video_id = generate_video(
                            st.session_state.api_key,
                            st.session_state.talking_photo_id,
                            st.session_state.voice_id,
                            script,
                            title,
                            orientation
                        )
                        
                        st.success(f"✅ Video generate ho rahi hai! ID: {video_id}")
                        
                        # Poll
                        with st.spinner("1-3 minute wait karo..."):
                            for _ in range(30):
                                time.sleep(10)
                                status = check_video_status(st.session_state.api_key, video_id)
                                if status.get('status') == 'completed':
                                    st.success("✅ Video ready!")
                                    st.video(status['video_url'])
                                    break
                                elif status.get('status') == 'failed':
                                    st.error("❌ Video fail hui!")
                                    break
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab_vid2:
        prompt = st.text_area("Topic / Prompt", height=100)
        agent_orientation = st.selectbox("Orientation", ["landscape", "portrait"], key="agent_ori")
        
        if st.button("🤖 Agent Video Banao"):
            if not st.session_state.talking_photo_id:
                st.error("❌ Pehle Avatar upload karo!")
            elif not st.session_state.voice_id:
                st.error("❌ Pehle Voice select karo!")
            elif not prompt:
                st.error("❌ Prompt likho!")
            else:
                with st.spinner("Agent video bana raha hai..."):
                    try:
                        session_id = generate_agent_video(
                            st.session_state.api_key,
                            prompt,
                            st.session_state.voice_id,
                            st.session_state.talking_photo_id,
                            agent_orientation
                        )
                        
                        st.success(f"✅ Agent video shuru! Session: {session_id}")
                        
                        with st.spinner("2-3 minute wait karo..."):
                            for _ in range(40):
                                time.sleep(10)
                                status = check_agent_status(st.session_state.api_key, session_id)
                                if status.get('status') == 'failed':
                                    st.error("❌ Agent video fail hui!")
                                    break
                                if status.get('video_id'):
                                    video_id = status['video_id']
                                    video_status = check_video_status(st.session_state.api_key, video_id)
                                    if video_status.get('status') == 'completed':
                                        st.success("✅ Video ready!")
                                        st.video(video_status['video_url'])
                                        break
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
