import streamlit as st
from PIL import Image
import os
import base64
from io import BytesIO

# --- SECURITY LOCK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()

st.set_page_config(page_title="Developer Profile", layout="centered", page_icon="👨‍💻")

# EXACT PATH FIX FOR 'pages' FOLDER
current_dir = os.path.dirname(os.path.abspath(__file__))

# (Face Attendance main folder)
root_dir = os.path.dirname(current_dir)

# 3.Face Attendance -> Images -> Images20.png
IMG_PATH = os.path.join(root_dir, "Images", "Images20.png")

# 4. (Safe side) 
if not os.path.exists(IMG_PATH):
    IMG_PATH = os.path.join(root_dir, "Images", "Images20.jpg")

def get_avatar_html():
    """Return an <img> or emoji-fallback HTML snippet for the avatar."""
    if os.path.exists(IMG_PATH):
        img = Image.open(IMG_PATH).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f'<img src="data:images/png;base64,{b64}" class="avatar-img" alt="Arif Khan"/>'
    return '<div class="avatar-fallback">🧑‍💻</div>'

avatar_html = get_avatar_html()
img_missing_note = "" if os.path.exists(IMG_PATH) else \
    '<div class="img-missing-note">⚠️ Profile image not found at Images/Images20.png — showing placeholder.</div>'

# --- CSS (LIGHT & PREMIUM THEME + SIDEBAR FIX) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 720px; }

* { font-family: 'Inter', sans-serif; } 

/* 🛠️ SIDEBAR & BACKGROUND FIXES (Matches Home.py) */
[data-testid="stAppViewContainer"] {
    background: #f4f7f6;
}
[data-testid="stSidebar"] {
    background-color: #0a1128 !important;
    border-right: 2px solid #1CB5E0;
}
[data-testid="stSidebarNav"] span {
    color: #ffffff !important;
    font-weight: 500;
    font-size: 16px;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: rgba(28, 181, 224, 0.2) !important;
    border-radius: 8px;
}

/* --- ANIMATIONS --- */
@keyframes floatCard {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-4px); }
}
@keyframes ringSpin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes pulseDot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
    50%      { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------------- CARD ---------------- */
.profile-card {
    position: relative;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 24px;
    padding: 48px 40px 40px 40px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
    color: #1e293b;
    animation: floatCard 6s ease-in-out infinite;
    overflow: hidden;
}
.profile-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
    background-size: 26px 26px;
    opacity: 0.3;
    pointer-events: none;
}

/* ---------------- AVATAR ---------------- */
.avatar-wrap {
    position: relative;
    width: 138px;
    height: 138px;
    margin: 0 auto 18px auto;
    animation: fadeUp 0.6s ease both;
}
.avatar-ring {
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: 2px dashed #93c5fd;
    animation: ringSpin 14s linear infinite;
}
.avatar-inner {
    position: absolute;
    inset: 5px;
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid #ffffff;
    background: #f1f5f9;
    box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
}
.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.avatar-fallback {
    font-size: 3rem;
}
.img-missing-note {
    color: #d97706;
    font-size: 12px;
    margin-bottom: 8px;
}

/* ---------------- BADGE ---------------- */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    color: #166534;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    animation: fadeUp 0.6s ease 0.05s both;
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #22c55e;
    animation: pulseDot 2s infinite;
}

/* ---------------- NAME / TITLE ---------------- */
.dev-name {
    font-size: 38px;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #0f172a 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 16px 0 6px 0;
    animation: fadeUp 0.6s ease 0.1s both;
}
.dev-title {
    color: #64748b;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 0.5px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 22px;
    animation: fadeUp 0.6s ease 0.15s both;
}

/* ---------------- ABOUT ---------------- */
.about-blurb {
    color: #475569;
    font-size: 15px;
    line-height: 1.7;
    max-width: 480px;
    margin: 0 auto 22px auto;
    animation: fadeUp 0.6s ease 0.2s both;
}

/* ---------------- VENTURES ---------------- */
.venture-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 26px;
    animation: fadeUp 0.6s ease 0.25s both;
}
.venture-badge {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #334155;
    font-size: 12.5px;
    font-weight: 500;
    padding: 7px 15px;
    border-radius: 20px;
    transition: all 0.2s ease;
    white-space: nowrap;
}
.venture-badge:hover {
    border-color: #94a3b8;
    background: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

/* ---------------- SOCIAL BUTTONS ---------------- */
.social-container {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin-bottom: 30px;
    flex-wrap: wrap;
    animation: fadeUp 0.6s ease 0.3s both;
}
.social-btn {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #0f172a !important;
    padding: 10px 22px;
    border-radius: 30px;
    text-decoration: none !important;
    font-size: 14.5px;
    font-weight: 600;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.social-btn:hover {
    background: #f8fafc;
    border-color: #94a3b8;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}

/* ---------------- TECH STACK ---------------- */
.tech-stack {
    padding-top: 22px;
    border-top: 1px solid #e2e8f0;
    animation: fadeUp 0.6s ease 0.35s both;
}
.tech-label {
    color: #94a3b8;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.chip-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 9px;
}
.skill-chip {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #475569;
    font-size: 13px;
    font-weight: 500;
    padding: 7px 15px;
    border-radius: 16px;
    transition: all 0.2s ease;
}
.skill-chip:hover {
    background: #f8fafc;
    border-color: #94a3b8;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.03);
}
</style>
""", unsafe_allow_html=True)

# --- SINGLE, UNBROKEN HTML BLOCK ---
card_html = (
'<div class="profile-card">'
f'{img_missing_note}'
'<div class="avatar-wrap">'
'<div class="avatar-ring"></div>'
f'<div class="avatar-inner">{avatar_html}</div>'
'</div>'
'<div class="status-badge"><span class="status-dot"></span>Actively Building</div>'
'<div class="dev-name">Arif Khan</div>'
'<div class="dev-title">Full Stack Developer &middot; Python Enthusiast</div>'
'<div class="about-blurb">'
'B.Tech CSE student building production-ready web &amp; AI systems &mdash; from this '
'face-recognition attendance platform to freelance and agency work under '
'NexGen Builds and CodeQubit Tech Solutions.'
'</div>'
'<div class="venture-row">'
'<span class="venture-badge">🏗️ NexGen Builds</span>'
'<span class="venture-badge">🚀 CodeQubit Tech Solutions</span>'
'<span class="venture-badge">📄 IEEE Co-Author &middot; Facial Recognition Fairness</span>'
'</div>'
'<div class="social-container">'
'<a href="mailto:arifwitnes6973@gmail.com" target="_blank" class="social-btn">✉️ Email</a>'
'<a href="https://www.linkedin.com/in/arif-khan-1797671b4" target="_blank" class="social-btn">🔗 LinkedIn</a>'
'<a href="https://github.com/arif1-git" target="_blank" class="social-btn">💻 GitHub</a>'
'</div>'
'<div class="tech-stack">'
'<div class="tech-label">Core Stack &mdash; This Project</div>'
'<div class="chip-grid">'
'<span class="skill-chip">🐍 Python</span>'
'<span class="skill-chip">👁️ OpenCV</span>'
'<span class="skill-chip">🎈 Streamlit</span>'
'<span class="skill-chip">🗄️ SQLite</span>'
'<span class="skill-chip">🤖 Machine Learning</span>'
'</div>'
'</div>'
'</div>'
)

st.markdown(card_html, unsafe_allow_html=True)