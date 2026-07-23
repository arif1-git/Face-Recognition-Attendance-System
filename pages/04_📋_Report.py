import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Arif Khan | Attendance Report", page_icon="📋", layout="wide")
# SECURITY LOCK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Unauthorized Access! Please login from the main page.")
    st.stop()
# THEME — same light "Registry & Recognition" palette as login.py
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root{
  --bg-top:#FDFBF6;
  --bg-bottom:#EFE9DC;
  --panel:#FFFFFF;
  --panel-soft:#FAF7F0;
  --ink:#1F2A3C;
  --muted:#7C879A;
  --brass:#C9A24B;
  --brass-soft:#E4C878;
  --brass-deep:#A9843A;
  --scan:#3FB6AA;
  --coral:#E2725B;
  --line: rgba(201,162,75,0.30);
}

html, body, [class*="css"] { font-family:'Inter', sans-serif; }

[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
}
[data-testid="stHeader"]{ background: transparent; }

/* Hero banner */
.report-hero{
  position: relative;
  background: linear-gradient(120deg, #FFFFFF 0%, var(--panel-soft) 100%);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 26px 30px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(31,42,60,0.06);
  overflow: hidden;
}
.report-hero:before{
  content:"";
  position:absolute; inset:0;
  background: repeating-linear-gradient(90deg, transparent, transparent 38px, rgba(201,162,75,0.05) 39px, transparent 40px);
  pointer-events:none;
}
.report-eyebrow{
  font-family:'JetBrains Mono', monospace;
  color: var(--scan);
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
}
.report-title{
  font-family:'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 2rem;
  color: var(--ink);
  margin: 6px 0 4px 0;
}
.report-sub{ color: var(--muted); font-size: 0.95rem; max-width: 640px; }

/* Stat cards */
.stat-row{ display:flex; gap:16px; margin-bottom: 22px; flex-wrap: wrap; }
.stat-card{
  flex:1;
  min-width: 160px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-left: 3px solid var(--brass);
  border-radius: 10px;
  padding: 16px 18px;
  box-shadow: 0 6px 16px rgba(31,42,60,0.05);
}
.stat-label{
  font-family:'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--scan);
}
.stat-value{
  font-family:'Space Grotesk', sans-serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--ink);
  margin-top: 4px;
}

/* Panel wrapper */
.panel{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 18px;
  box-shadow: 0 6px 16px rgba(31,42,60,0.05);
}
.panel-title{
  font-family:'Space Grotesk', sans-serif;
  font-weight: 600;
  color: var(--ink);
  font-size: 1.05rem;
  margin-bottom: 10px;
}

/* Inputs */
.stTextInput input, .stSelectbox [data-baseweb="select"], .stDateInput input{
  background: #FFFFFF !important;
  color: var(--ink) !important;
  border: 1px solid rgba(31,42,60,0.14) !important;
  border-radius: 8px !important;
}
.stTextInput input:focus{
  border: 1px solid var(--scan) !important;
  box-shadow: 0 0 0 3px rgba(63,182,170,0.16) !important;
}
label { color: var(--muted) !important; font-size: 0.82rem !important; }

/* Buttons */
.stButton>button, .stDownloadButton>button{
  background: linear-gradient(180deg, var(--brass-soft), var(--brass));
  color: #3A2A08;
  border: none;
  border-radius: 8px;
  font-family:'Space Grotesk', sans-serif;
  font-weight: 600;
  padding: 0.55rem 1.1rem;
  box-shadow: 0 4px 12px rgba(201,162,75,0.30);
  transition: box-shadow 0.2s ease, transform 0.15s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover{
  box-shadow: 0 6px 16px rgba(201,162,75,0.40), 0 0 0 3px rgba(63,182,170,0.16);
  transform: translateY(-1px);
}

/* Dataframe */
[data-testid="stDataFrame"]{
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}

/* Alerts */
[data-testid="stAlert"]{ border-radius: 8px; }

/* Tag chip */
.chip{
  display:inline-block;
  font-family:'JetBrains Mono', monospace;
  background: var(--panel-soft);
  border: 1px solid var(--line);
  color: var(--brass-deep);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-right: 6px;
}

.footer-stamp{
  margin-top: 24px;
  font-family:'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 1.5px;
  color: #A9B0BE;
  text-transform: uppercase;
  text-align: center;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
# HERO
st.markdown(f"""
<div class="report-hero">
  <div class="report-eyebrow">Arif Khan · Registry Export</div>
  <div class="report-title">📋 Attendance Report</div>
  <div class="report-sub">Review, filter, and export attendance records — ready to share with faculty, admin, or any external system.</div>
</div>
""", unsafe_allow_html=True)

CSV_PATH = "app.csv"

# LOAD DATA

if not os.path.exists(CSV_PATH):
    st.warning("⚠️ No attendance record found. Please mark your attendance first using the Face Recognition module.")
    st.stop()

skipped_rows = 0
try:
    with st.spinner("Loading attendance ledger..."):
        try:
            df = pd.read_csv(CSV_PATH)
        except pd.errors.ParserError:
            # app.csv has rows with an inconsistent number of columns —
            # fall back to skipping the malformed rows instead of crashing.
            before = sum(1 for _ in open(CSV_PATH, encoding="utf-8", errors="ignore")) - 1
            df = pd.read_csv(CSV_PATH, on_bad_lines="skip", engine="python")
            skipped_rows = max(before - len(df), 0)
except pd.errors.EmptyDataError:
    st.info("ℹ️ The attendance file is currently empty. No records to display.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Could not read the attendance file: {e}")
    st.stop()

if skipped_rows > 0:
    st.warning(
        f"⚠️ {skipped_rows} row(s) in `app.csv` had a different number of columns than the header "
        f"and were skipped so the report could still load. This usually means the script that writes "
        f"attendance to `app.csv` isn't writing the same columns every time — worth checking that "
        f"before it grows into a bigger data-quality issue."
    )

if df.empty:
    st.info("ℹ️ The file has been created, but no one's attendance has been marked yet.")
    st.stop()


# STAT CARDS

total_records = len(df)
name_col = next((c for c in df.columns if c.lower() in ("name", "student_name", "full_name")), None)
id_col = next((c for c in df.columns if "id" in c.lower()), None)
date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)

unique_students = df[name_col].nunique() if name_col else (df[id_col].nunique() if id_col else "—")
last_updated = datetime.fromtimestamp(os.path.getmtime(CSV_PATH)).strftime("%d %b %Y, %I:%M %p")

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="stat-label">Total Records</div><div class="stat-value">{total_records}</div></div>
  <div class="stat-card"><div class="stat-label">Unique Students</div><div class="stat-value">{unique_students}</div></div>
  <div class="stat-card"><div class="stat-label">Last Updated</div><div class="stat-value" style="font-size:1.05rem;">{last_updated}</div></div>
</div>
""", unsafe_allow_html=True)


# FILTERS

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">🔍 Filter Records</div>', unsafe_allow_html=True)

filtered_df = df.copy()
filter_cols = st.columns(3)

with filter_cols[0]:
    if name_col:
        search = st.text_input("Search by name", placeholder="Type a student name...")
        if search:
            filtered_df = filtered_df[filtered_df[name_col].astype(str).str.contains(search, case=False, na=False)]
    elif id_col:
        search = st.text_input("Search by ID", placeholder="Type a student ID...")
        if search:
            filtered_df = filtered_df[filtered_df[id_col].astype(str).str.contains(search, case=False, na=False)]

with filter_cols[1]:
    dep_col = next((c for c in df.columns if c.lower() in ("dep", "department")), None)
    if dep_col:
        options = ["All"] + sorted(df[dep_col].dropna().unique().tolist())
        chosen_dep = st.selectbox("Department", options)
        if chosen_dep != "All":
            filtered_df = filtered_df[filtered_df[dep_col] == chosen_dep]

with filter_cols[2]:
    status_col = next((c for c in df.columns if c.lower() in ("status", "attendance")), None)
    if status_col:
        options = ["All"] + sorted(df[status_col].dropna().unique().tolist())
        chosen_status = st.selectbox("Status", options)
        if chosen_status != "All":
            filtered_df = filtered_df[filtered_df[status_col] == chosen_status]

st.markdown('</div>', unsafe_allow_html=True)


# RESULTS TABLE

st.markdown(
    f'<span class="chip">Showing {len(filtered_df)} of {total_records} records</span>',
    unsafe_allow_html=True,
)
st.write("")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)


# EXPORT / SHARE — multiple formats for external systems
#
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">🔗 Export & Share</div>', unsafe_allow_html=True)
st.caption("Download in the format your recipient needs. All exports respect the filters applied above.")

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    st.download_button(
        "⬇️ Download CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name=f"Attendance_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_col2:
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="Attendance")
        st.download_button(
            "⬇️ Download Excel",
            data=buffer.getvalue(),
            file_name=f"Attendance_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except ImportError:
        st.button("⬇️ Download Excel", disabled=True, use_container_width=True, help="Install openpyxl to enable Excel export")

with exp_col3:
    st.download_button(
        "⬇️ Download JSON",
        data=filtered_df.to_json(orient="records", indent=2).encode("utf-8"),
        file_name=f"Attendance_Report_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-stamp">Arif Khan · Confidential Attendance Ledger</div>', unsafe_allow_html=True)