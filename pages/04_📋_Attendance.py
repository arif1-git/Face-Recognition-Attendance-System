import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time


# PAGE CONFIG 
st.set_page_config(page_title="Attendance Report", page_icon="📋", layout="wide")


# THEME CSS (Premium UI/UX & Dark Sidebar)

def add_custom_css():
    st.markdown("""
    <style>
    /* 🚀 Main Button Styling (Gradient & 3D Effect) */
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
    
    /* Download Button Specific (Greenish) */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        width: 100%;
    }
    
    /* 📝 Text Input aur Select Box ki styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 5px;
        border: 1.5px solid #1CB5E0;
    }
    
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

    /* Custom form background */
    [data-testid="stForm"] {
        border: 1.5px solid rgba(28, 181, 224, 0.3);
        border-radius: 10px;
        background-color: #f8fafc;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- SECURITY LOCK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()

st.title("📋 Attendance Management Dashboard")
st.write("---")


col1, col2 = st.columns([1, 2.5])

# --- Left Column: Data Entry Form ---
with col1:
    st.subheader("📝 Manual Entry")
    
    with st.form("attendance_form"):
        atten_roll = st.text_input("Student ID (Roll No.)")
        atten_name = st.text_input("Full Name")
        atten_dep = st.selectbox("Department", ["Computer Science", "Electronics", "Mechanical", "Civil"])
        
        
        atten_time = st.text_input("Time", value=datetime.now().strftime("%H:%M:%S"))
        atten_date = st.text_input("Date", value=datetime.now().strftime("%d/%m/%Y"))
        
        # Form submit 
        submitted = st.form_submit_button("Update / Add Record", use_container_width=True)
        
        if submitted:
            if not atten_name or not atten_roll:
                st.error("Name aur ID bharna zaroori hai!")
            else:
                # Backend logic: CSV mein data append 
                file_name = "app.csv"
                if not os.path.isfile(file_name):
                    with open(file_name, "w") as f:
                        f.write("Name,ID,Department,Time,Date\n")
                
                with open(file_name, "a") as f:
                    f.write(f"{atten_name},{atten_roll},{atten_dep},{atten_time},{atten_date}\n")
                
                st.success(f"✅ {atten_name} added manually!")
                time.sleep(1) # Taki user success message 
                st.rerun()    

# --- Right Column: Data Table & CSV Viewer ---
with col2:
    st.subheader("📊 Live Attendance Report")
    
    
    uploaded_file = st.file_uploader("Drop an external CSV file (Optional)", type=["csv"])
    
    st.write("") # Spacing
    
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True, height=450)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Uploaded CSV",
            data=csv_data,
            file_name='uploaded_attendance_report.csv',
            mime='text/csv',
        )
        
    else:
        # Default CSV file (app.csv) 
        if os.path.exists("app.csv"):
            df = pd.read_csv("app.csv")
            
            # DataFrame table show 
            st.dataframe(df, use_container_width=True, height=450)
            
            col_a, col_b = st.columns(2)
            with col_a:
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Today's Report",
                    data=csv_data,
                    file_name=f'Attendance_Report_{datetime.now().strftime("%d-%m-%Y")}.csv',
                    mime='text/csv',
                )
        else:
            st.info("📌 The system's default attendance file (app.csv) has not been generated yet.")
            st.warning("⚠️ No attendance data found. Please use the Face Recognition system through the camera or add the attendance manually.")