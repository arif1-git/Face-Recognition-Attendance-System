import streamlit as st
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Home | Face Attendance", page_icon="🏠", layout="centered")

# CONFIGURATION & CONSTANTS
SENDER_EMAIL = "arifwitnes6973@gmail.com"  
SENDER_PASSWORD = "glxmbvlettiaoubr"         

# 1. SESSION STATE (Memory) - Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "forgot_mode" not in st.session_state:
    st.session_state.forgot_mode = False

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

# 2. HIDE SIDEBAR IF NOT LOGGED IN
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)


# 3. BASE THEME CSS (Applied to all pages)
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] { font-family:'Inter', sans-serif; }

/* Background setup for the whole page */
[data-testid="stAppViewContainer"] {
    background: #f4f7f6;
}

/* Sidebar styling */
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

/* FIX FOR DARK MODE TEXT DISAPPEARANCE */
/* Force Streamlit markdown text to be dark */
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
    color: #262730 !important; 
}
/* Force Metric (KPI) values and labels to be dark */
[data-testid="stMetricValue"] div {
    color: #000851 !important;
}
[data-testid="stMetricLabel"] label {
    color: #5a6a85 !important;
}
/* Force Dataframe Text to be readable */
[data-testid="stDataFrame"] {
    background-color: #ffffff !important;
}
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    color: #262730 !important;
}

/* Header UI Elements */
.crest-container { text-align: center; margin-bottom: 25px; }

.top-system-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #5a6a85;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 15px;
}

.crest {
    width: 60px; height: 60px;
    margin: 0 auto 15px auto;
    border: 2px solid #1CB5E0;
    border-radius: 50%;
    display:flex; align-items:center; justify-content:center;
    font-size: 26px;
    background: radial-gradient(circle at 35% 30%, #e0f7fa, #b2ebf2);
    box-shadow: 0 0 0 4px rgba(28, 181, 224, 0.1);
}

.eyebrow {
    font-family:'JetBrains Mono', monospace;
    color: #1CB5E0;
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.login-title {
    font-family:'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.8rem;
    color: #000851;
    margin: 2px 0;
}

.login-sub { color: #5a6a85; font-size: 0.95rem; margin-bottom: 15px; }

.brass-rule {
    height: 2px;
    background: linear-gradient(90deg, transparent, #1CB5E0, transparent);
    margin: 15px 0 25px 0;
}

/* Modern Text Inputs */
.stTextInput label {
    color: #5a6a85 !important;
    font-family:'JetBrains Mono', monospace;
    font-size: 0.8rem !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.stTextInput input {
    background: #f8fafc !important;
    color: #000851 !important;
    border: 1.5px solid rgba(28, 181, 224, 0.3) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus {
    border: 1.5px solid #1CB5E0 !important;
    box-shadow: 0 0 0 3px rgba(28, 181, 224, 0.2) !important;
    background: #ffffff !important;
}

/* 3D Gradient Buttons */
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
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 15px rgba(28, 181, 224, 0.4);
    background: linear-gradient(90deg, #22c1ed 0%, #00108a 100%);
}

.stamp {
    text-align: center;
    margin-top: 30px;
    font-family:'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 1.5px;
    color: #94a3b8;
    text-transform: uppercase;
}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)


# DYNAMIC LAYOUT: Slim card for login, Wide layout for Dashboard
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    /* Slim Card Layout for Login */
    .block-container {
        background: #ffffff !important;
        border: 1px solid rgba(28, 181, 224, 0.2) !important;
        border-radius: 16px !important;
        padding: 3rem 3.5rem !important;
        box-shadow: 0 10px 30px rgba(0, 8, 81, 0.08) !important;
        max-width: 500px !important; 
        margin-top: 6vh !important;
        margin-bottom: 6vh !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    /* Wider Layout for Dashboard Charts */
    .block-container {
        max-width: 1100px !important; 
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


# HELPER FUNCTION: SEND OTP EMAIL
def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEText(f"Hello Admin,\n\nYour OTP to reset your Face Attendance System password is: {otp}\n\nPlease keep it secure.")
        msg['Subject'] = 'Password Reset OTP - Face Attendance System'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# 4. DISPLAY LOGIC

if not st.session_state.logged_in:

    # --- FORGOT PASSWORD FLOW ---
    if st.session_state.forgot_mode:
        st.markdown("""
        <div class="crest-container">
            <div class="top-system-name">Face Recognition Based Attendance System</div>
            <div class="crest">🔄</div>
            <div class="eyebrow">Recovery Portal</div>
            <div class="login-title">Reset Password</div>
            <div class="login-sub">Admin Recovery</div>
            <div class="brass-rule"></div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.otp_sent:
            fp_username = st.text_input("Admin Username", placeholder="Enter your username")
            
            st.write("") 
            col1, col2 = st.columns(2)
            with col1:
                send_btn = st.button("Send OTP", use_container_width=True)
            with col2:
                back_btn = st.button("Back to Login", use_container_width=True)

            if send_btn:
                conn = sqlite3.connect("attendance_system.db")
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM admin WHERE username=?", (fp_username,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    user_email = result[0]
                    generated_otp = str(random.randint(100000, 999999))
                    st.session_state['generated_otp'] = generated_otp
                    st.session_state['reset_username'] = fp_username
                    
                    with st.spinner("Sending OTP to your email..."):
                        if send_otp_email(user_email, generated_otp):
                            st.session_state.otp_sent = True
                            st.success("OTP sent successfully to your registered email!")
                            st.rerun()
                        else:
                            st.error("Failed to send email. Check internet or credentials.")
                else:
                    st.error("⚠️ Username not found in the database.")

            if back_btn:
                st.session_state.forgot_mode = False
                st.rerun()

        else:
            # Step 2: Enter OTP & New Password
            entered_otp = st.text_input("Enter 6-Digit OTP", type="password", placeholder="Enter OTP received on email")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            
            st.write("") 
            col1, col2 = st.columns(2)
            with col1:
                verify_btn = st.button("Update Password", use_container_width=True)
            with col2:
                cancel_btn = st.button("Cancel", use_container_width=True)

            if verify_btn:
                if entered_otp == st.session_state.get('generated_otp'):
                    conn = sqlite3.connect("attendance_system.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE admin SET password=? WHERE username=?", 
                                 (new_password, st.session_state['reset_username']))
                    conn.commit()
                    conn.close()

                    st.success("🎉 Password updated successfully! Please login.")
                    st.session_state.otp_sent = False
                    st.session_state.forgot_mode = False
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP. Please try again.")

            if cancel_btn:
                st.session_state.otp_sent = False
                st.session_state.forgot_mode = False
                st.rerun()

    # --- NORMAL LOGIN FORM ---
    else:
        st.markdown("""
        <div class="crest-container">
            <div class="top-system-name">Face Recognition Based Attendance System</div>
            <div class="crest">🔐</div>
            <div class="eyebrow">Secure Access</div>
            <div class="login-title">Face Attendance</div>
            <div class="login-sub">Admin Portal</div>
            <div class="brass-rule"></div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your admin username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.button("Login", use_container_width=True)
        with col2:
            forgot_password_btn = st.button("Forgot Password", use_container_width=True)

        st.markdown('<div class="stamp">Authorized personnel only</div>', unsafe_allow_html=True)

        if login_btn:
            conn = sqlite3.connect("attendance_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        if forgot_password_btn:
            st.session_state.forgot_mode = True
            st.rerun()

else:
    
    #  ANALYTICS DASHBOARD
    
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #000851; font-family: 'Space Grotesk', sans-serif; margin-bottom: 10px;">📊 Admin Dashboard</h1>
        <p style="color: #5a6a85; font-size: 1.1rem; margin-bottom: 30px; line-height: 1.6;">
            Welcome to Face Recognition Based Attendance System. Here is your live overview.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Define attendance file path
    csv_file = "app.csv" 

    if os.path.exists(csv_file):
        try:
            # Read data using Pandas
            df = pd.read_csv(csv_file)
            
            # --- KPI Metrics Row ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Scans", value=len(df))
            with col2:
                # Check for column names (case sensitive)
                if 'Id' in df.columns:
                    unique_students = df['Id'].nunique()
                    st.metric(label="Present Students", value=unique_students)
                elif 'ID' in df.columns:
                    unique_students = df['ID'].nunique()
                    st.metric(label="Present Students", value=unique_students)
                else:
                    st.metric(label="Data Validating", value="N/A")
            with col3:
                today_date = datetime.date.today().strftime("%d-%m-%Y")
                st.metric(label="Today's Date", value=today_date)

            st.markdown("<hr style='border: 1px solid rgba(28, 181, 224, 0.2); margin: 2rem 0;'>", unsafe_allow_html=True)
            
            # --- Interactive Charts Layout ---
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("### 🏢 Department-wise Stats")
                if 'Department' in df.columns:
                    # Count frequency of each department
                    dept_counts = df['Department'].value_counts().reset_index()
                    dept_counts.columns = ['Department', 'Count']
                    
                    # Generate Plotly Bar Chart
                    fig_bar = px.bar(
                        dept_counts, 
                        x='Department', 
                        y='Count', 
                        color='Department',
                        text_auto=True,
                        template='plotly_white'
                    )
                    # Update layout to blend with background
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("Department column not found in CSV to generate chart.")

            with chart_col2:
                st.markdown("### 🕒 Recent Entries")
                # Display the last 10 entries from the CSV
                st.dataframe(df.tail(10), use_container_width=True, hide_index=True)
                
        except Exception as e:
            st.error(f"⚠️ Error processing attendance data: {e}")
    else:
        st.info("ℹ️ No attendance data found yet. Start the Face Recognition module to generate charts!")
    
    st.write("")
    st.write("")
    
    # Secure Logout Button at the bottom
    col_empty, col_btn, col_empty2 = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🔒 Secure Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
