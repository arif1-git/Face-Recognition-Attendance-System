import streamlit as st
import cv2
import os
import numpy as np
from PIL import Image


# PAGE CONFIG (Model Training)

st.set_page_config(page_title="Model Training", page_icon="⚙️", layout="wide")


# THEME CSS (Premium UI/UX)

def add_custom_css():
    st.markdown("""
    <style>
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease-in-out;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 15px rgba(0, 181, 224, 0.4);
    }
    
    
    h1, h2, h3 {
        color: #1CB5E0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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


    .status-text {
        font-size: 18px;
        font-weight: 600;
        color: #000851;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- SECURITY LOCK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop() 

def train_classifier():
    data_dir = "Data"
    
    
    if not os.path.exists(data_dir) or len(os.listdir(data_dir)) == 0:
        st.error("⚠️ No data found! Please capture student photos first before training.")
        return

    path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

    faces = []
    ids = []

    
    st.markdown('<p class="status-text">⚙️ Processing Image Data...</p>', unsafe_allow_html=True)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, image in enumerate(path):
        img = Image.open(image).convert('L')  
        imageNp = np.array(img, 'uint8')      
        
        
        id = int(os.path.split(image)[1].split('.')[1])

        faces.append(imageNp)
        ids.append(id)
        
        
        progress = (i + 1) / len(path)
        progress_bar.progress(progress)
        status_text.text(f"Extracting features from image {i+1} of {len(path)}...")

    ids = np.array(ids)

    status_text.text("Training Model... Please wait, this might take a moment.")

    
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier.xml")
    
    
    progress_bar.empty()
    status_text.empty()
    st.success("✅ Model Trained Successfully! 'classifier.xml' has been generated and is ready for Face Recognition.")
    st.balloons() 


if __name__ == "__main__":
    st.title("🧠 AI Model Training")
    st.write("Train the Face Recognition model using the photos collected in the Student Management module. This step is mandatory whenever you add a new student or delete an existing one.")
    
    st.write("---") # Divider
    
    col1, col2, col3 = st.columns([1, 2, 1]) # Center alignment ke liye columns
    
    with col2:
        if st.button("Start Training Data", use_container_width=True):
            train_classifier()