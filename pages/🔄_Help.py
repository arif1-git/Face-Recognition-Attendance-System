import streamlit as st
import smtplib
from email.mime.text import MIMEText
import os


# SECURITY LOCK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()


# PAGE CONFIG
st.set_page_config(page_title="Help & Support", page_icon="💡", layout="centered")


# CONFIGURATION
ADMIN_EMAIL = "arifwitnes6973@gmail.com"
APP_PASSWORD = "glxmbvlettiaoubr"


# THEME CSS (Matching your Project Flow & Dark Mode Fixes)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family:'Inter', sans-serif; }

/* Background setup */
[data-testid="stAppViewContainer"] {
    background: #f4f7f6;
}

/* 🛠️ SIDEBAR FIXES */
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

/* 🛠️ DARK MODE TEXT FIXES */
/* Force Streamlit markdown text to be dark */
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
    color: #262730 !important; 
}

/* Tabs Styling & Dark Mode Fix */
[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 1.05rem;
    background-color: transparent !important;
}
[data-baseweb="tab"] div {
    color: #000851 !important;
}

/* Main Container Card */
.block-container {
    background: #ffffff !important;
    border: 1px solid rgba(28, 181, 224, 0.2) !important;
    border-radius: 16px !important;
    padding: 3rem !important;
    box-shadow: 0 10px 30px rgba(0, 8, 81, 0.05) !important;
    max-width: 750px !important;
    margin-top: 4vh !important;
    margin-bottom: 4vh !important;
}

/* Header UI Elements */
.help-header { text-align: center; margin-bottom: 30px; }
.help-icon { font-size: 50px; margin-bottom: 10px; }
.help-title {
    color: #000851;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 5px;
}
.help-sub { color: #5a6a85; font-size: 1rem; }

/* Steps Styling */
.step-box {
    background: #f8fafc;
    border-left: 4px solid #1CB5E0;
    padding: 15px 20px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.step-title {
    color: #000851;
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 5px;
}
.step-desc {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* Modern Text Inputs & Text Areas (Consistent with main.py) */
.stTextInput label, .stTextArea label {
    color: #5a6a85 !important;
    font-weight: 600;
}
.stTextInput input, .stTextArea textarea {
    background: #f8fafc !important;
    color: #000851 !important;
    border: 1.5px solid rgba(28, 181, 224, 0.3) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    transition: all 0.3s ease;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border: 1.5px solid #1CB5E0 !important;
    box-shadow: 0 0 0 3px rgba(28, 181, 224, 0.2) !important;
    background: #ffffff !important;
}

/* Form Submit Button */
div.stButton > button {
    background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
    color: white !important;
    border-radius: 8px;
    border: none !important;
    padding: 10px 24px;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0px 4px 10px rgba(0, 8, 81, 0.2);
    transition: all 0.3s ease-in-out;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 15px rgba(28, 181, 224, 0.4);
    background: linear-gradient(90deg, #22c1ed 0%, #00108a 100%);
}
</style>
""", unsafe_allow_html=True)


# HELPER FUNCTION: SEND SUPPORT TICKET
def send_support_email(user_name, user_email, subject, message):
    try:
        
        body = f"""
        New Support Ticket Received!
        
        From: {user_name}
        Email: {user_email}
        
        Problem/Subject: {subject}
        
        Message Details:
        {message}
        """
        
        msg = MIMEText(body)
        msg['Subject'] = f"Support Ticket: {subject}"
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL  
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ADMIN_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False


# UI LAYOUT

st.markdown("""
<div class="help-header">
    <div class="help-icon">💡</div>
    <div class="help-title">Help & Support Desk</div>
    <div class="help-sub">Everything you need to operate the Face Attendance System</div>
</div>
""", unsafe_allow_html=True)

# Streamlit Tabs
tab1, tab2 = st.tabs(["📖 System Guide", "🎧 Contact Support"])

# --- TAB 1: SYSTEM GUIDE (Rules & Steps) ---
with tab1:
    st.write("")
    st.markdown("### How to Use This Project")
    st.write("Follow these exact steps to register a student and mark their attendance successfully.")
    
    st.markdown("""
    <div class="step-box">
        <div class="step-title">Step 1: 📝 Add Student Details</div>
        <div class="step-desc">Go to the <b>Student Details</b> module. Fill out the registration form with the student's exact Name, Department, ID, and Email. Save the data to the database.</div>
    </div>
    
    <div class="step-box">
        <div class="step-title">Step 2: 📸 Capture Face Samples</div>
        <div class="step-desc">In the same Student Details module, click the "Take Photos" button. The camera will open and take 100 sample images of the student's face. Make sure the lighting is good.</div>
    </div>
    
    <div class="step-box">
        <div class="step-title">Step 3: 🧠 Train the AI Model</div>
        <div class="step-desc">Whenever you add a new student or update photos, go to the <b>Train Model</b> page and click the Train button. This updates the `classifier.xml` file so the AI can recognize the new faces.</div>
    </div>
    
    <div class="step-box">
        <div class="step-title">Step 4: 👁️ Live Face Recognition (Attendance)</div>
        <div class="step-desc">Go to the <b>Face Recognition</b> module and start the camera. When a registered student looks at the camera, the system will match their face, mark them as 'Present' in the CSV file, and send them an automated email.</div>
    </div>
    
    <div class="step-box">
        <div class="step-title">Step 5: 📊 View Reports</div>
        <div class="step-desc">Go to the <b>Report/Attendance</b> module to view the daily logs. You can filter the attendance by name, department, or date, and export the final report as an Excel or CSV file.</div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: SUPPORT FORM ---
with tab2:
    st.write("")
    st.markdown("### Face a Bug? Let us know.")
    st.write("Fill out the form below and the system administrator will receive your query immediately.")
    
    with st.form(key='support_form'):
        col1, col2 = st.columns(2)
        with col1:
            u_name = st.text_input("Your Name", placeholder="e.g. Arif khan")
        with col2:
            u_email = st.text_input("Your Email (For reply)", placeholder="example@gmail.com")
            
        u_subject = st.text_input("Problem Subject", placeholder="e.g. Camera not opening in Face Recognition")
        u_message = st.text_area("Describe the Issue", placeholder="Please provide details about the error you are facing...", height=120)
        
        st.write("")
        submit_btn = st.form_submit_button("📨 Send Support Ticket", use_container_width=True)
        
        if submit_btn:
            if u_name == "" or u_email == "" or u_subject == "" or u_message == "":
                st.error("⚠️ Please fill all the fields before submitting.")
            else:
                with st.spinner("Sending message to Administrator..."):
                    success = send_support_email(u_name, u_email, u_subject, u_message)
                    if success:
                        st.success("✅ Message Sent Successfully! Admin will get back to you soon.")
                    else:
                        st.error("❌ Failed to send message. Please check your internet connection.")
