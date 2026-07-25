import streamlit as st
import sqlite3
import pandas as pd
import cv2
import numpy as np
import os
import glob
import time
import random

# PAGE CONFIG
st.set_page_config(page_title="Student Management", page_icon="🎓", layout="wide")

def add_custom_css():
    st.markdown("""
    <style>
    /* Main Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease-in-out;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 15px rgba(0, 181, 224, 0.4);
    }
    
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1.5px solid #1CB5E0;
    }
    .stSelectbox>div>div>div {
        border-radius: 5px;
        border: 1.5px solid #1CB5E0;
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
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- SECURITY LOCK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()

# --- CAMERA SESSION STATES ---
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "current_student_id" not in st.session_state:
    st.session_state.current_student_id = ""

# --- DATABASE SETUP (SQLite) ---
def init_student_db():
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS student 
                 (student_id TEXT PRIMARY KEY, name TEXT, dep TEXT, course TEXT, 
                  year TEXT, semester TEXT, email TEXT)''')
    conn.commit()
    conn.close()

def add_student(student_id, name, dep, course, year, sem, email):
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO student VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (student_id, name, dep, course, year, sem, email))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False 
    conn.close()
    return success

def update_student(student_id, name, dep, course, year, sem, email):
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE student 
            SET name = ?, dep = ?, course = ?, year = ?, semester = ?, email = ?
            WHERE student_id = ?
        """, (name, dep, course, year, sem, email, student_id))
        conn.commit()
        success = True
    except Exception as e:
        success = False
    conn.close()
    return success

def get_all_students():
    conn = sqlite3.connect('attendance_system.db')
    df = pd.read_sql_query("SELECT * FROM student", conn)
    conn.close()
    return df

def delete_student_data(student_id):
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    c.execute("DELETE FROM student WHERE student_id = ?", (student_id,))
    deleted_rows = c.rowcount 
    conn.commit()
    conn.close()

    if deleted_rows > 0:
        if os.path.exists('Data'):
            files_to_delete = glob.glob(f"Data/user.{student_id}.*.jpg")
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass 
        return True
    return False

# --- OPENCV CLOUD-SAFE FACE CAPTURE (DATA AUGMENTATION) ---
def generate_samples_from_image(cv2_img, student_id):
    if not os.path.exists('Data'):
        os.makedirs('Data')
        
    cascade_path = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
    face_classifier = cv2.CascadeClassifier(cascade_path)
    
    if face_classifier.empty():
        st.error("⚠️ Error: Haar Cascade XML file not found.")
        return False
        
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        st.error("❌ No face detected! Please ensure clear lighting and look directly into the camera.")
        return False
        
    for (x, y, w, h) in faces:
        cropped_face = cv2_img[y:y+h, x:x+w]
        face_resized = cv2.resize(cropped_face, (450, 450))
        face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # Generating 100 dynamic samples from a single captured image
        st.info("🔄 Processing image and generating 100 training samples...")
        progress_bar = st.progress(0)
        
        for i in range(1, 101):
            # Using alpha/beta scaling to safely change brightness (Augmentation)
            brightness_shift = random.randint(-40, 40)
            aug_face = cv2.convertScaleAbs(face_gray, alpha=1.0, beta=brightness_shift)
            
            file_name_path = f"Data/user.{student_id}.{i}.jpg"
            cv2.imwrite(file_name_path, aug_face)
            progress_bar.progress(i)
            time.sleep(0.01)
            
        return True
    return False

# --- STREAMLIT UI ---
def student_module():
    st.title("📚 Student Management System")
    init_student_db()
    
    # 4 Tabs: Add, View, Edit, Manage / Delete
    tab1, tab2, tab3, tab4 = st.tabs(["Add New Student", "View All Students", "Edit Student", "Manage / Delete"])
    
    with tab1:
        st.subheader("Enter Student Details")
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID (Roll No)")
            name = st.text_input("Full Name")
            dep = st.selectbox("Department", ["Computer Science", "Electronics", "Mechanical", "Civil","Agriculture","Biotechnology","Chemical","Electrical","Environmental","Food Technology","Geology","Industrial","Information Technology","Instrumentation","Marine","Materials Science","Mathematics","Mechatronics","Metallurgy","Mining","Nanotechnology","Petroleum","Pharmaceuticals"])
            
        with col2:
            course = st.selectbox("Course", ["B.Tech", "Diploma", "MBA","MCA", "BBA", "BCA", "B.Sc", "Nursing", "Pharmacy", "Law", "Architecture"])
            year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
            sem = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"])
            email = st.text_input("Email")
            
        st.write("") 
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Save Details", use_container_width=True):
                if student_id == "" or name == "":
                    st.warning("⚠️ ID and Name are required!")
                else:
                    if add_student(student_id, name, dep, course, year, sem, email):
                        st.success("Data Saved Successfully!")
                    else:
                        st.error("⚠️ This Student ID already exists. (Duplicate Entry!)")
                        
        with col4:
            if st.button("Take Photo Sample", use_container_width=True):
                if student_id == "":
                    st.warning("⚠️ Please enter the Student ID first!")
                else:
                    # Activate Streamlit's native camera instead of OpenCV's
                    st.session_state.current_student_id = student_id
                    st.session_state.camera_active = True
                    st.rerun()

        # Web Camera Section UI
        if st.session_state.camera_active:
            st.markdown("<hr style='border: 1px solid #1CB5E0;'>", unsafe_allow_html=True)
            st.markdown("### 📸 Capture Profile Photo")
            st.caption("Click a clear photo. The system will automatically extract your face and generate dataset samples.")
            
            img_buffer = st.camera_input("Take a photo")
            
            if img_buffer is not None:
                bytes_data = img_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                
                if generate_samples_from_image(cv2_img, st.session_state.current_student_id):
                    st.success(f"✅ Training data generated for ID: {st.session_state.current_student_id}!")
                    st.session_state.camera_active = False
                    st.rerun()
                
            if st.button("Cancel Camera"):
                st.session_state.camera_active = False
                st.rerun()

    with tab2:
        st.subheader("Student Database")
        student_data = get_all_students()
        
        if not student_data.empty:
            st.dataframe(student_data, use_container_width=True)
        else:
            st.info("ℹ️ No data has been added yet. Please add student details first.")

    with tab3:
        st.subheader("Edit Student Details")
        student_df = get_all_students()
        
        if not student_df.empty:
            student_list = student_df['student_id'].tolist()
            selected_id = st.selectbox("Select Student ID to Edit", student_list)
            
            student_info = student_df[student_df['student_id'] == selected_id].iloc[0]
            
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Full Name", value=student_info['name'])
                    
                    deps = ["Computer Science", "Electronics", "Mechanical", "Civil"]
                    dep_idx = deps.index(student_info['dep']) if student_info['dep'] in deps else 0
                    new_dep = st.selectbox("Department", deps, index=dep_idx)
                    
                    courses = ["B.Tech", "Diploma", "MBA"]
                    course_idx = courses.index(student_info['course']) if student_info['course'] in courses else 0
                    new_course = st.selectbox("Course", courses, index=course_idx)
                    
                with col2:
                    years = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                    year_idx = years.index(student_info['year']) if student_info['year'] in years else 0
                    new_year = st.selectbox("Year", years, index=year_idx)
                    
                    sems = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]
                    sem_idx = sems.index(student_info['semester']) if student_info['semester'] in sems else 0
                    new_sem = st.selectbox("Semester", sems, index=sem_idx)
                    
                    new_email = st.text_input("Email", value=student_info['email'])
                
                st.write("")
                submit_update = st.form_submit_button("Update Student Details", use_container_width=True)
                
                if submit_update:
                    if update_student(selected_id, new_name, new_dep, new_course, new_year, new_sem, new_email):
                        st.success(f"✅ The data for Student ID {selected_id} has been successfully updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ An error occurred while updating the data. Please try again.")
        else:
            st.info("ℹ️ No students available for editing in the database.")

    with tab4:
        st.subheader("Remove a Student")
        del_student_id = st.text_input("Enter Student ID to Delete")
        
        st.write("")
        if st.button("Delete Student", type="primary", use_container_width=True): 
            if del_student_id == "":
                st.warning("Please enter a valid Student ID.")
            else:
                if delete_student_data(del_student_id):
                    st.success(f"✅ The data and photos for Student ID {del_student_id} have been successfully deleted!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ This Student ID was not found in the database. Please check and try again.")

if __name__ == '__main__':
    student_module()
