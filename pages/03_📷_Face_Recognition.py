import streamlit as st
import cv2
import numpy as np
import os
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import threading

# PAGE CONFIG
st.set_page_config(page_title="Live Attendance", page_icon="👁️", layout="wide")

# THEME CSS
def add_custom_css():
    st.markdown("""
    <style>
    h1, h2, h3 { color: #1CB5E0 !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0a1128 !important; border-right: 2px solid #1CB5E0; }
    [data-testid="stSidebarNav"] span { color: #ffffff !important; font-weight: 500; font-size: 16px; }
    .brand-subtitle { color: #888; font-size: 18px; font-style: italic; margin-top: -15px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- EMAIL CONFIGURATION ---
SENDER_EMAIL = "arifwitnes6973@gmail.com"  
APP_PASSWORD = "glxmbvlettiaoubr" 

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()

def send_student_email(student_email, student_name, date, time_str):
    try:
        msg = MIMEText(f"Hello {student_name},\n\nYour attendance has been successfully marked for today ({date}) at {time_str}.")
        msg['Subject'] = f"Attendance Marked: {date}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = student_email
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        pass

def send_email_thread(email, name, date, time_str):
    threading.Thread(target=send_student_email, args=(email, name, date, time_str)).start()

def mark_attendance(roll, name, dep):
    file_name = "app.csv"
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M:%S")

    if not os.path.isfile(file_name):
        with open(file_name, "w") as f:
            f.write("Name,ID,Department,Time,Date\n")

    with open(file_name, "r") as f:
        data_list = f.readlines()

    id_list_today = []
    for line in data_list:
        if current_date in line:
            entry = line.strip().split(',')
            if len(entry) >= 2:
                id_list_today.append(entry[1].strip()) 

    if str(roll).strip() not in id_list_today:
        with open(file_name, "a") as f:
            f.write(f"{name},{roll},{dep},{current_time},{current_date}\n")
        return True, current_date, current_time  
    return False, current_date, current_time     

@st.cache_resource
def load_models():
    cascade_path = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    
    face_cascade = cv2.CascadeClassifier(cascade_path)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    model_loaded = False
    if os.path.exists("classifier.xml"):
        recognizer.read("classifier.xml")
        model_loaded = True
        
    return face_cascade, recognizer, model_loaded

face_cascade, recognizer, is_model_trained = load_models()

st.title("👁️ Live Face Recognition")
st.markdown('<p class="brand-subtitle">Powered by Arif Khan</p>', unsafe_allow_html=True)
st.write("---")

if not is_model_trained:
    st.error("⚠️ Error: 'classifier.xml' file nahi mili! Pehle model train karein.")
    st.stop()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.info("📸 Click 'Take Photo' to scan your face and mark attendance.")
    
    # 🚀 THE BULLETPROOF CLOUD SOLUTION 🚀
    img_file_buffer = st.camera_input("Mark Attendance")

    if img_file_buffer is not None:
        # Convert the image to an OpenCV frame
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        
        if len(faces) == 0:
            st.error("❌ No face detected! Please look straight into the camera and try again.")
        else:
            for (x, y, w, h) in faces:
                try:
                    id, predict = recognizer.predict(gray[y:y+h, x:x+w])
                    
                    if predict < 75:
                        conn = sqlite3.connect("attendance_system.db")
                        my_cursor = conn.cursor()
                        my_cursor.execute(f"SELECT name, student_id, dep, email FROM student WHERE student_id='{id}'")
                        result = my_cursor.fetchone()
                        conn.close()
                        
                        if result:
                            n, r, d, e = result[0], result[1], result[2], result[3]
                            
                            is_new, curr_date, curr_time = mark_attendance(r, n, d)
                            if is_new:
                                st.success(f"✅ Attendance Marked Successfully for {n}!")
                                if e: 
                                    send_email_thread(e, n, curr_date, curr_time)
                            else:
                                st.warning(f"⚠️ {n}, your attendance is already marked for today!")
                            
                            # Draw Boxes
                            cv2.rectangle(cv2_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                            cv2.rectangle(cv2_img, (x, y-40), (x+w, y), (0, 255, 0), cv2.FILLED) 
                            cv2.putText(cv2_img, f"{n}", (x+5, y-10), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
                        else:
                            st.error(f"❌ Student ID {id} found in model but NOT in database!")
                    else:
                        st.error("❌ Unknown Face Detected!")
                        cv2.rectangle(cv2_img, (x, y), (x+w, y+h), (0, 0, 255), 3)
                        cv2.putText(cv2_img, "Unknown", (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                        
                except Exception as e:
                    st.error(f"Database Error: {e}")
            
            # Show the processed image with bounding boxes
            st.image(cv2_img, channels="BGR", use_container_width=True)
