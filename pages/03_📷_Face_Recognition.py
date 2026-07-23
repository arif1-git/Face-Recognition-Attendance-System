import streamlit as st
import cv2
import numpy as np
import os
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import time
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av

# PAGE CONFIG (Live Attendance with Face Recognition)
st.set_page_config(page_title="Live Attendance", page_icon="👁️", layout="wide")

# THEME CSS (Premium UI/UX & Dark Sidebar)
def add_custom_css():
    st.markdown("""
    <style>
    /* 🎨 Headers ko color karna */
    h1, h2, h3 {
        color: #1CB5E0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 🛠️ SIDEBAR FIXES (Dark Mode + White Text) */
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
    
    /* Custom Subtitle */
    .brand-subtitle {
        color: #888;
        font-size: 18px;
        font-style: italic;
        margin-top: -15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- EMAIL CONFIGURATION ---
SENDER_EMAIL = "arifwitnes6973@gmail.com"  
APP_PASSWORD = "glxmbvlettiaoubr" 

# --- SECURITY LOCK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()

# --- Email sending Function ---
def send_student_email(student_email, student_name, date, time_str):
    try:
        subject = f"Attendance Marked: {date}"
        body = f"Hello {student_name},\n\nYour attendance has been successfully marked for today ({date}) at {time_str}.\n\nRegards,\n Face Recognition System"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = student_email
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

# --- Attendance Save Function ---
def mark_attendance(roll, name, dep):
    file_name = "app.csv"
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M:%S")

    print(f"\n--- Checking Attendance for: {name} (ID: {roll}) ---")

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

    print(f"IDs marked today in app.csv: {id_list_today}")

    if str(roll).strip() not in id_list_today:
        with open(file_name, "a") as f:
            f.write(f"{name},{roll},{dep},{current_time},{current_date}\n")
        print(f"✅ SUCCESS: Attendance written in CSV for {name}")
        return True, current_date, current_time  
    
    print(f"⚠️ SKIPPED: {name} (ID {roll}) already marked today!")
    return False, current_date, current_time     

# --- Streamlit Web App UI ---
st.title("👁️ Live Face Recognition")
st.markdown('<p class="brand-subtitle">Powered by Arif Khan</p>', unsafe_allow_html=True)
st.write("---")

col1, col2, col3 = st.columns([1, 2, 1])

# --- Safe Haar Cascade Loading ---
cascade_path = 'haarcascade_frontalface_default.xml'
if not os.path.exists(cascade_path):
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

try:
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        st.error(f"⚠️ Failed to load cascade classifier from {cascade_path}")
        st.stop()
except Exception as e:
    st.error(f"⚠️ OpenCV Error loading cascade: {e}")
    st.stop()


# --- WebRTC Configuration for Cloud Camera ---
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

if not os.path.exists("classifier.xml"):
    with col2:
        st.error("⚠️ Error: 'classifier.xml' file nahi mili! Pehle model train karein.")
else:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("classifier.xml")

    # Cloud Camera Processing Function
    def video_frame_callback(frame_obj):
        frame = frame_obj.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        for (x, y, w, h) in faces:
            id, predict = recognizer.predict(gray[y:y+h, x:x+w])
            print(f"Detected ID: {id}, Predict Score: {predict}")
            
            # Confidence threshold set to 75 for better accuracy
            if predict < 75:
                try:
                    # check_same_thread=False added for Cloud Threading Safety
                    conn = sqlite3.connect("attendance_system.db", check_same_thread=False)
                    my_cursor = conn.cursor()
                    my_cursor.execute(f"SELECT name, student_id, dep, email FROM student WHERE student_id='{id}'")
                    result = my_cursor.fetchone()
                    conn.close()
                    
                    if result:
                        n, r, d, e = result[0], result[1], result[2], result[3]
                        
                        is_new, curr_date, curr_time = mark_attendance(r, n, d)
                        
                        if is_new:
                            print(f"✅ Attendance marked in system for {n}!")
                            if e: 
                                send_student_email(e, n, curr_date, curr_time)
                                print(f"Email successfully sent to {n} at {e}")
                        
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        
                        cv2.rectangle(frame, (x, y-75), (x+w, y), (0, 255, 0), cv2.FILLED) 
                        cv2.putText(frame, f"{n}", (x+5, y-50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
                        cv2.putText(frame, f"ID: {r}", (x+5, y-25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                        cv2.putText(frame, "Present", (x+5, y-5), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                        
                        # Confidence Formula updated so it doesn't go below 0
                        confidence = int(max(0, 100 - predict))
                        cv2.putText(frame, f"Match: {confidence}%", (x, y+h+25), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 1)
                        
                        # ✨ NEW DEBUGGING TRICK ADDED HERE: Raw Score for Known Face
                        cv2.putText(frame, f"Raw Score: {int(predict)}", (x, y+h+50), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 2)

                except Exception as err:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Database Error", (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                    print(f"DB Error: {err}")
                    
            else:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                cv2.putText(frame, "Unknown Face", (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                
                # ✨ NEW DEBUGGING TRICK ADDED HERE: Raw Score for Unknown Face
                cv2.putText(frame, f"Raw Score: {int(predict)}", (x, y+h+25), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(frame, format="bgr24")

    with col2:
        st.info("System is ready. Click 'START' below to turn on the Cloud Camera.")
        webrtc_streamer(
            key="face-recognition",
            video_frame_callback=video_frame_callback,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": True, "audio": False}
        )
