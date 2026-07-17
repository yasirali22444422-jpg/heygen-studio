import streamlit as st
import requests
import json
import time

# ============================================================
# HEYGEN BY YASIR - STREAMLIT APP
# ============================================================

# ✅ تمہاری HeyGen API Key (Student کو نہیں دکھے گی)
HEYGEN_API_KEY = 'sk_V2_hgu_kuujglU11Oe_x9fCykWNbZsKqF0lrDtIy5wqiWCPiwx4'

# ✅ Access Codes (یہاں Student Codes Manage کرو)
ACCESS_CODES = {
    "ABC123": "active",
    "XYZ789": "active",
    "Y69SW9": "active",
    "QE7WGD": "active",
    "DEMO001": "active",
    "DEMO002": "inactive"  # اس کا Access ختم
}

# ============================================================
# FUNCTIONS
# ============================================================

def generate_video(script, voice_id, avatar_id):
    """HeyGen API ko Call kare"""
    url = "https://api.heygen.com/v2/video/av4/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HEYGEN_API_KEY}"
    }
    data = {
        "script": script,
        "voice_id": voice_id,
        "avatar_id": avatar_id
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_voices():
    """HeyGen se Voices Fetch kare"""
    url = "https://api.heygen.com/v1/voices/list"
    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('voices', [])
    except:
        return []

def get_avatars():
    """HeyGen se Avatars Fetch kare"""
    url = "https://api.heygen.com/v1/avatars/list"
    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('avatars', [])
    except:
        return []

# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="HeyGen by Yasir", 
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .main { background-color: #0a0a0a; }
        .stApp { background-color: #0a0a0a; color: #e0e0e0; }
        .stTextInput > div > div > input { background-color: #1a1a1a; color: white; border-color: #ff1a1a; }
        .stTextArea > div > div > textarea { background-color: #1a1a1a; color: white; border-color: #ff1a1a; }
        h1, h2, h3 { color: #ff1a1a; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div style='text-align: center; border-bottom: 2px solid #ff1a1a; padding-bottom: 10px; margin-bottom: 20px;'>
        <h1 style='color: #ff1a1a; margin: 0;'>
            🎬 HeyGen <span style='font-size: 16px; color: #ff1a1a;'>by Yasir</span>
        </h1>
    </div>
""", unsafe_allow_html=True)

# ===== ACCESS CODE CHECK =====
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
    st.session_state.code = ""
    st.session_state.voice_id = ""
    st.session_state.avatar_id = ""

# Access Code Input
if not st.session_state.access_granted:
    st.subheader("🔒 Enter Your Access Code")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code = st.text_input("Access Code:", type="password", placeholder="e.g. ABC123")
        
        if st.button("🔓 Verify Access", use_container_width=True):
            if code in ACCESS_CODES and ACCESS_CODES[code] == "active":
                st.session_state.access_granted = True
                st.session_state.code = code
                st.success("✅ Access Granted! Welcome!")
                st.rerun()
            elif code in ACCESS_CODES and ACCESS_CODES[code] == "inactive":
                st.error("❌ Your access has been removed. Contact Yasir.")
            else:
                st.error("❌ Invalid Code! Please check and try again.")
    
    # WhatsApp Support
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center;'>
            <p style='color: #888;'>🤝 Need help? Contact me on WhatsApp</p>
            <a href='https://wa.me/923284568281' target='_blank' style='
                display: inline-block;
                background: #25D366;
                color: white;
                padding: 10px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                font-size: 16px;
                transition: all 0.3s;
            '>💬 Chat on WhatsApp</a>
            <p style='font-size: 11px; color: #666; margin-top: 8px;'>👤 Yasir - Your Instructor</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ===== MAIN APP (Access Granted) =====
st.success(f"✅ Access Granted! Welcome! (Code: {st.session_state.code})")
st.info("ℹ️ Upload your avatar, select voice, and create videos!")

# Tabs
tab1, tab2, tab3 = st.tabs(["🧑 Avatar", "🎤 Voice", "🎥 Create Video"])

# ===== TAB 1: AVATAR =====
with tab1:
    st.subheader("📸 Your Avatar")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Avatar Upload
        uploaded_file = st.file_uploader("Upload Photo:", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, width=150)
            st.success("✅ Photo uploaded!")
            # Save to session
            st.session_state.avatar_uploaded = True
    
    with col2:
        st.markdown("""
            **💡 Tips for best results:**
            - Clear face, good lighting
            - Front-facing photo
            - High resolution
        """)
    
    # Avatar List
    if st.button("📋 Load Avatars", use_container_width=True):
        with st.spinner("Loading avatars..."):
            avatars = get_avatars()
            if avatars:
                for av in avatars[:6]:
                    cols = st.columns([1, 3])
                    with cols[0]:
                        if av.get('preview_image_url'):
                            st.image(av.get('preview_image_url'), width=60)
                    with cols[1]:
                        st.write(f"**{av.get('avatar_name', 'Avatar')}**")
                        if st.button(f"Select {av.get('avatar_id', '')[:8]}", key=av.get('avatar_id', 'av')):
                            st.session_state.avatar_id = av.get('avatar_id', '')
                            st.success(f"✅ Avatar selected!")
            else:
                st.warning("⚠️ No avatars found. Check your API key.")

# ===== TAB 2: VOICE =====
with tab2:
    st.subheader("🎤 Your Voice")
    
    # Voice ID Input
    voice_id = st.text_input("Voice ID:", placeholder="e.g. 1bd001e7e50f421d891986aad5c8bbd2", 
                            value=st.session_state.get('voice_id', ''))
    if voice_id:
        st.session_state.voice_id = voice_id
        st.success("✅ Voice saved!")
    
    # Voice List
    if st.button("📋 Load Voices", use_container_width=True):
        with st.spinner("Loading voices..."):
            voices = get_voices()
            if voices:
                for v in voices[:10]:
                    cols = st.columns([1, 3, 1])
                    with cols[0]:
                        st.write("🎤")
                    with cols[1]:
                        st.write(f"**{v.get('name', 'Voice')}** - {v.get('language', '')}")
                    with cols[2]:
                        if st.button(f"Select", key=v.get('voice_id', 'v')):
                            st.session_state.voice_id = v.get('voice_id', '')
                            st.success(f"✅ Voice selected!")
                            st.rerun()
            else:
                st.warning("⚠️ No voices found. Check your API key.")

# ===== TAB 3: CREATE VIDEO =====
with tab3:
    st.subheader("🎥 Create Your Video")
    
    # Check if avatar and voice are selected
    if not st.session_state.get('avatar_id'):
        st.warning("⚠️ Please select an avatar from the Avatar tab first!")
    if not st.session_state.get('voice_id'):
        st.warning("⚠️ Please select a voice from the Voice tab first!")
    
    # Script
    script = st.text_area("✍️ Write Script:", height=150, 
                          placeholder="Write the text your avatar will say...",
                          help="Max 30000 characters")
    
    # Orientation
    orientation = st.selectbox("📐 Orientation:", ["Landscape (16:9)", "Portrait (9:16)"])
    
    # Generate Button
    if st.button("🎬 Generate Video", use_container_width=True, 
                disabled=not (st.session_state.get('avatar_id') and st.session_state.get('voice_id'))):
        if not script:
            st.error("❌ Please write a script first!")
        elif not st.session_state.get('voice_id'):
            st.error("❌ Please select a voice from Voice tab!")
        elif not st.session_state.get('avatar_id'):
            st.error("❌ Please select an avatar from Avatar tab!")
        else:
            with st.spinner("🎬 Generating video... This may take 1-3 minutes."):
                try:
                    result = generate_video(
                        script, 
                        st.session_state.voice_id,
                        st.session_state.avatar_id
                    )
                    
                    if result and result.get('code') == 200:
                        video_url = result.get('data', {}).get('video_url')
                        if video_url:
                            st.success("✅ Video generated successfully!")
                            st.video(video_url)
                            st.download_button("⬇️ Download Video", video_url, 
                                             file_name=f"video_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
                        else:
                            st.info("⏳ Video is processing... Check back in a few minutes.")
                            st.json(result.get('data', {}))
                    else:
                        error_msg = result.get('message', 'Unknown error') if result else 'No response'
                        st.error(f"❌ Error: {error_msg}")
                        if result:
                            st.json(result)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Tip: Make sure your API key is valid and you have credits.")

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        <p>Made with ❤️ by <strong style='color: #ff1a1a;'>Yasir</strong></p>
        <p style='font-size: 10px; color: #444;'>© 2024 HeyGen by Yasir. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
