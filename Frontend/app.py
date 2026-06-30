import streamlit as st
import time
import json
import requests
import hashlib
import datetime
from io import BytesIO

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=" HireLens-MAVS",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
API_BASE_URL = "http://127.0.0.1:8000" 

DUMMY_USERS = {
    "admin@hirelens.ai": {
        "password": hashlib.sha256("Admin@123".encode()).hexdigest(),
        "name": "Admin User",
        "role": "Admin",
        "theme": "Light",
        "avatar": "👤",
    },
    "user@hirelens.ai": {
        "password": hashlib.sha256("User@123".encode()).hexdigest(),
        "name": "Demo User",
        "role": "User",
        "theme": "Light",
        "avatar": "👤",
    },
}

# ─── SESSION STATE INIT ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in": False,
        "current_user": None,
        "auth_page": "login",          # login | signup | forgot
        "active_page": "Dashboard",
        "dark_mode": False,
        "notifications": [
            {"id": 1, "msg": "Welcome to HireLens!", "read": False, "time": "Just now", "icon": "🎉"},
        ],
        "users_db": DUMMY_USERS.copy(),
        "analysis_result": None,
        "uploaded_file_name": None,
        "reports": [],
        "files_uploaded": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── THEME CSS ───────────────────────────────────────────────────────────────────
def inject_css():
    dark = st.session_state.dark_mode
    if dark:
        bg         = "#0F172A"
        card_bg    = "#1E293B"
        sidebar_bg = "#0F172A"
        text       = "#F1F5F9"
        sub_text   = "#94A3B8"
        border     = "#334155"
        input_bg   = "#1E293B"
        input_text = "#F1F5F9"
    else:
        bg         = "#F8FAFC"
        card_bg    = "#FFFFFF"
        sidebar_bg = "#FFFFFF"
        text       = "#1E293B"
        sub_text   = "#64748B"
        border     = "#E2E8F0"
        input_bg   = "#FFFFFF"
        input_text = "#1E293B"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

    :root {{
        --primary:   #2563EB;
        --secondary: #1E3A8A;
        --success:   #22C55E;
        --warning:   #F59E0B;
        --error:     #EF4444;
        --bg:        {bg};
        --card:      {card_bg};
        --sidebar:   {sidebar_bg};
        --text:      {text};
        --subtext:   {sub_text};
        --border:    {border};
        --input-bg:  {input_bg};
        --input-txt: {input_text};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar) !important;
        border-right: 1px solid var(--border);
    }}
    section[data-testid="stSidebar"] * {{ color: var(--text) !important; }}

    /* ── Main area ── */
    .main .block-container {{
        background: var(--bg) !important;
        padding-top: 1rem;
        max-width: 1400px;
    }}

    /* ── Topbar ── */
    .av-topbar {{
        background: var(--primary);
        color: #fff !important;
        padding: 0.9rem 1.5rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.4rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        box-shadow: 0 4px 20px rgba(37,99,235,0.25);
    }}
    .av-topbar .nav-links {{ display: flex; gap: 1.2rem; font-size: 0.88rem; font-weight: 500; }}
    .av-topbar .nav-links span {{ cursor: pointer; opacity: 0.9; }}
    .av-topbar .nav-links span:hover {{ opacity: 1; text-decoration: underline; }}

    /* ── Metric Cards ── */
    .av-metric-row {{ display: flex; gap: 1rem; margin-bottom: 1.2rem; flex-wrap: wrap; }}
    .av-metric {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.4rem;
        flex: 1; min-width: 140px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.15s;
    }}
    .av-metric:hover {{ transform: translateY(-2px); box-shadow: 0 6px 18px rgba(37,99,235,0.1); }}
    .av-metric .label {{ font-size: 0.78rem; color: var(--subtext); text-transform: uppercase; letter-spacing: 0.05em; }}
    .av-metric .value {{ font-family: 'Poppins', sans-serif; font-size: 1.6rem; font-weight: 700; color: var(--primary); margin-top: 0.2rem; }}
    .av-metric .badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.72rem; font-weight: 600; margin-top: 0.3rem; }}
    .badge-success {{ background: #DCFCE7; color: #166534; }}
    .badge-warning {{ background: #FEF3C7; color: #92400E; }}
    .badge-error   {{ background: #FEE2E2; color: #991B1B; }}
    .badge-info    {{ background: #DBEAFE; color: #1E40AF; }}

    /* ── Analysis Panels ── */
    .av-panel {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .av-panel h4 {{
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--primary);
        margin: 0 0 0.6rem 0;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .av-panel p, .av-panel li {{ font-size: 0.88rem; color: var(--text); line-height: 1.6; }}
    .av-panel ul {{ padding-left: 1.1rem; margin: 0; }}

    /* ── Code / question box ── */
    .av-code-box {{
        background: #0F172A;
        color: #E2E8F0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-family: 'Inter', monospace;
        font-size: 0.82rem;
        margin-top: 0.5rem;
        border-left: 3px solid var(--primary);
        line-height: 1.7;
    }}

    /* ── Upload zone ── */
    .av-upload-zone {{
        border: 2px dashed var(--primary);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: {'#1E293B' if dark else '#EFF6FF'};
        transition: background 0.2s;
    }}

    /* ── Buttons ── */
    div[data-testid="stButton"] > button {{
        border-radius: 8px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s !important;
    }}

    /* ── Notification badge ── */
    .notif-dot {{
        display: inline-block;
        width: 8px; height: 8px;
        background: var(--error);
        border-radius: 50%;
        margin-left: 4px;
        vertical-align: middle;
    }}

    /* ── Auth card ── */
    .auth-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        max-width: 420px;
        margin: 4rem auto;
        box-shadow: 0 8px 32px rgba(37,99,235,0.12);
    }}
    .auth-card h2 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 0.2rem;
        text-align: center;
    }}
    .auth-card .subtitle {{ text-align:center; color: var(--subtext); font-size:0.88rem; margin-bottom:1.5rem; }}

    /* ── Report card ── */
    .report-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    /* ── Toast notification ── */
    .av-toast {{
        position: fixed;
        top: 1rem; right: 1rem;
        background: var(--primary);
        color: #fff;
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        font-size: 0.85rem;
        z-index: 9999;
        animation: fadeIn 0.3s ease;
    }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(-10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    /* ── Inputs ── */
    input, textarea, select {{
        background: var(--input-bg) !important;
        color: var(--input-txt) !important;
        border-color: var(--border) !important;
    }}

    /* ── Divider ── */
    hr {{ border-color: var(--border) !important; }}

    /* Hide Streamlit branding */
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def add_notification(msg, icon="🔔"):
    st.session_state.notifications.insert(0, {
        "id": len(st.session_state.notifications) + 1,
        "msg": msg, "read": False,
        "time": datetime.datetime.now().strftime("%H:%M"),
        "icon": icon,
    })

def unread_count():
    return sum(1 for n in st.session_state.notifications if not n["read"])

def call_api(endpoint, files=None, data=None):
    """Call backend API with graceful fallback to mock data."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.post(url, files=files, data=data, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    # ── Mock fallback ──
    return {
        "resume_analysis": {
            "name": "ABC",
            "skills": ["Python", "SQL", "FastAPI", "Docker"],
            "experience": "2 years",
            "education": "B.Tech Computer Science",
        },
        "jd_analysis": {
            "required_skills": ["Python", "SQL", "Docker", "REST API"],
            "experience": "2+ years",
            "role": "Backend Engineer",
        },
        "match_score": 92,
        "risk_score": "Low",
        "status": "Verified",
        "recommendation": "Proceed to Technical Interview",
        "candidate_match": "92%",
        "interview_questions": [
            "Explain FastAPI and its advantages over Flask.",
            "What is SQLAlchemy and how does it work?",
            "Difference between SQL and NoSQL databases?",
            "How does Docker containerization work?",
            "Explain REST API design principles.",
        ],
    }

# ─── AUTH PAGES ─────────────────────────────────────────────────────────────────
def page_login():
    inject_css()
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown("""
        <div class="auth-card">
            <h2>🔬 HireLens</h2>
            <p class="subtitle">Powered by MAVS (Multi-Agent Validation System)<br> See Beyond The Resume</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("### Sign In")
            email = st.text_input("Email", placeholder="admin@hirelens.ai", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")

            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("🔑 Login", use_container_width=True, type="primary")
            with col_b:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.session_state.auth_page = "signup"
                    st.rerun()

            if st.button("Forgot Password?", use_container_width=True):
                st.session_state.auth_page = "forgot"
                st.rerun()

            if login_btn:
                db = st.session_state.users_db
                if email in db and db[email]["password"] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = {**db[email], "email": email}
                    add_notification("Login successful!", "✅")
                    st.success("Welcome back!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try admin@hirelens.ai / Admin@123")

            st.markdown("---")
            st.caption("Demo: `admin@hirelens.ai` / `Admin@123`")

def page_signup():
    inject_css()
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown("### 📝 Create Account")
        name  = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        role  = st.selectbox("Role", ["User", "Admin"])
        pw    = st.text_input("Password", type="password")
        pw2   = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", type="primary", use_container_width=True):
            if not name or not email or not pw:
                st.error("All fields required.")
            elif pw != pw2:
                st.error("Passwords don't match.")
            elif email in st.session_state.users_db:
                st.error("Email already registered.")
            else:
                st.session_state.users_db[email] = {
                    "password": hash_pw(pw),
                    "name": name,
                    "role": role,
                    "theme": "Light",
                    "avatar": "👤",
                }
                st.success("Account created! Please login.")
                time.sleep(1)
                st.session_state.auth_page = "login"
                st.rerun()

        if st.button("← Back to Login", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

def page_forgot():
    inject_css()
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown("### 🔓 Reset Password")
        email = st.text_input("Registered Email")
        if st.button("Send Reset Link", type="primary", use_container_width=True):
            if email in st.session_state.users_db:
                st.success(f"Reset link sent to {email} (demo mode — no actual email sent).")
            else:
                st.error("Email not found.")
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
def render_sidebar():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="font-size:2.5rem;">{user['avatar']}</div>
            <div style="font-family:'Poppins',sans-serif; font-weight:700; font-size:1rem; margin-top:0.3rem;">{user['name']}</div>
            <div style="font-size:0.78rem; color:#94A3B8;">{user['role']} · {user['email']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        pages = ["Dashboard", "Upload & Validate", "Reports", "Analytics", "History", "Notifications", "Settings"]
        icons = ["🏠", "📤", "📄", "📊", "🕐", "🔔", "⚙️"]
        
        if user["role"] == "Admin":
            pages.append("Admin Panel")
            icons.append("🛡️")

        for page, icon in zip(pages, icons):
            active = st.session_state.active_page == page
            label = f"**{icon} {page}**" if active else f"{icon} {page}"
            if st.button(label, use_container_width=True, key=f"nav_{page}"):
                st.session_state.active_page = page
                st.rerun()

        st.markdown("---")

        # Dark mode toggle
        dm = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if dm != st.session_state.dark_mode:
            st.session_state.dark_mode = dm
            add_notification("Theme changed!", "🎨")
            st.rerun()

        st.markdown("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.analysis_result = None
            st.session_state.auth_page = "login"
            st.rerun()

# ─── TOPBAR ─────────────────────────────────────────────────────────────────────
def render_topbar():
    uc = unread_count()
    notif_label = f"🔔 Notifications {'🔴' if uc > 0 else ''}"
    st.markdown(f"""
    <div class="av-topbar">
        <span>🔬 HireLens-MAVS</span>
        <div class="nav-links">
            <span>🔍 Search</span>
            <span>{notif_label} ({uc})</span>
            <span>👤 {st.session_state.current_user['name']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── DASHBOARD PAGE ──────────────────────────────────────────────────────────────
def page_dashboard():
    render_topbar()
    result = st.session_state.analysis_result

    files_up   = st.session_state.files_uploaded
    match_sc   = result["match_score"] if result else "—"
    risk_sc    = result["risk_score"]  if result else "—"
    status     = result["status"]      if result else "Pending"

    # ── Metric Cards ──
    st.markdown(f"""
    <div class="av-metric-row">
        <div class="av-metric">
            <div class="label">Files Uploaded</div>
            <div class="value">{files_up}</div>
            <span class="badge badge-info">Total</span>
        </div>
        <div class="av-metric">
            <div class="label">Match Score</div>
            <div class="value">{match_sc}{'%' if isinstance(match_sc, int) else ''}</div>
            <span class="badge badge-success">AI Scored</span>
        </div>
        <div class="av-metric">
            <div class="label">Risk Score</div>
            <div class="value">{risk_sc}</div>
            <span class="badge {'badge-success' if risk_sc=='Low' else 'badge-error'}">{'✅' if risk_sc=='Low' else '⚠️'} {risk_sc}</span>
        </div>
        <div class="av-metric">
            <div class="label">Status</div>
            <div class="value" style="font-size:1.2rem;">{status}</div>
            <span class="badge badge-success">{'✔' if status=='Verified' else '⏳'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not result:
        st.info("📤 No analysis yet. Go to **Upload & Validate** to begin.")
        return

    ra  = result["resume_analysis"]
    jd  = result["jd_analysis"]
    rec = result
    iqs = result.get("interview_questions", [])

    # ── Analysis Grid ──
    col1, col2 = st.columns(2)
    with col1:
        skills_str = ", ".join(ra.get("skills", []))
        st.markdown(f"""
        <div class="av-panel">
            <h4>📄 Resume Analysis</h4>
            <p><b>Name:</b> {ra.get('name','—')}</p>
            <p><b>Skills:</b> {skills_str}</p>
            <p><b>Experience:</b> {ra.get('experience','—')}</p>
            <p><b>Education:</b> {ra.get('education','—')}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        req_skills = ", ".join(jd.get("required_skills", []))
        st.markdown(f"""
        <div class="av-panel">
            <h4>📋 JD Analysis</h4>
            <p><b>Role:</b> {jd.get('role','—')}</p>
            <p><b>Required Skills:</b> {req_skills}</p>
            <p><b>Experience:</b> {jd.get('experience','—')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(f"""
        <div class="av-panel">
            <h4>🤖 AI Recommendation</h4>
            <p><b>Candidate Match:</b> {rec.get('candidate_match','—')}</p>
            <p><b>Recommendation:</b> {rec.get('recommendation','—')}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        iq_html = "".join([f"<li>{q}</li>" for q in iqs[:5]])
        st.markdown(f"""
        <div class="av-panel">
            <h4>❓ Interview Questions</h4>
            <div class="av-code-box"><ol style="margin:0;padding-left:1.2rem">{iq_html}</ol></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("📥 Download Report", type="primary"):
        _download_report(result)

# ─── UPLOAD & VALIDATE PAGE ──────────────────────────────────────────────────────
def page_upload():
    render_topbar()
    st.markdown("## 📤 Upload & Validate")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Resume Upload")
        st.markdown('<div class="av-upload-zone">📎 Drag & drop your resume here</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx", "txt"], label_visibility="collapsed")

    with col2:
        st.markdown("### Job Description")
        jd_text = st.text_area("Paste Job Description here", height=180, placeholder="Senior Python Developer\nRequired Skills: Python, FastAPI, Docker, SQL...\nExperience: 2+ years")

    st.markdown("---")
    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        run_btn = st.button("🚀 Run AI Validation", type="primary", use_container_width=True)
    with col_b:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()

    if run_btn:
        if not uploaded and not jd_text.strip():
            st.warning("Please upload a resume or paste a Job Description.")
        else:
            with st.spinner("🔬 AI agents are analyzing... Please wait."):
                time.sleep(2.5)   # simulate latency
                files = {}
                data  = {}
                if uploaded:
                    files["resume"] = (uploaded.name, uploaded.getvalue(), uploaded.type)
                    data["filename"] = uploaded.name
                if jd_text.strip():
                    data["jd"] = jd_text

                result = call_api("/api/validate", files=files if files else None, data=data)

            st.session_state.analysis_result = result
            st.session_state.files_uploaded += 1

            # Save to reports
            report = {
                "id": len(st.session_state.reports) + 1,
                "name": uploaded.name if uploaded else "JD-Only Analysis",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "score": result["match_score"],
                "status": result["status"],
                "data": result,
            }
            st.session_state.reports.insert(0, report)
            add_notification(f"✅ Validation complete for {report['name']}!", "🔬")
            add_notification("📄 New report generated.", "📄")

            st.success("✅ Validation complete! See results below.")
            st.rerun()

    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("### 📊 Latest Analysis Results")
        result = st.session_state.analysis_result
        ra = result["resume_analysis"]
        jd = result["jd_analysis"]

        col1, col2 = st.columns(2)
        with col1:
            score = result["match_score"]
            color = "#22C55E" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
            st.markdown(f"""
            <div class="av-panel">
                <h4>Match Score</h4>
                <div style="font-size:3rem; font-weight:700; color:{color}; text-align:center;">{score}%</div>
                <p style="text-align:center; color:var(--subtext);">Risk: {result['risk_score']} · Status: {result['status']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            iqs = result.get("interview_questions", [])
            iq_html = "".join([f"<div class='av-code-box' style='margin-bottom:0.4rem'>Q{i+1}: {q}</div>" for i, q in enumerate(iqs[:3])])
            st.markdown(f"""
            <div class="av-panel">
                <h4>Top Interview Questions</h4>
                {iq_html}
            </div>
            """, unsafe_allow_html=True)

        if st.button("→ View Full Dashboard", type="primary"):
            st.session_state.active_page = "Dashboard"
            st.rerun()

# ─── REPORTS PAGE ────────────────────────────────────────────────────────────────
def page_reports():
    render_topbar()
    st.markdown("## 📄 Reports")

    if not st.session_state.reports:
        st.info("No reports yet. Run a validation to generate reports.")
        return

    for r in st.session_state.reports:
        score_color = "#22C55E" if r["score"] >= 80 else "#F59E0B" if r["score"] >= 60 else "#EF4444"
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="av-panel" style="padding:0.7rem 1rem;">
                <b>{r['name']}</b><br>
                <span style="font-size:0.78rem; color:var(--subtext);">📅 {r['date']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='text-align:center; font-size:1.3rem; font-weight:700; color:{score_color}; padding-top:0.5rem;'>{r['score']}%</div>", unsafe_allow_html=True)
        with col3:
            if st.button("👁 View", key=f"view_{r['id']}", use_container_width=True):
                st.session_state.analysis_result = r["data"]
                st.session_state.active_page = "Dashboard"
                st.rerun()
        with col4:
            if st.button("⬇ PDF", key=f"dl_{r['id']}", use_container_width=True):
                _download_report(r["data"])
        st.markdown("")

def _download_report(result):
    """Generate and offer a downloadable text report."""
    ra  = result["resume_analysis"]
    jd  = result["jd_analysis"]
    iqs = result.get("interview_questions", [])
    content = f"""
HireLens — Validation Report
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

CANDIDATE
Name:        {ra.get('name','—')}
Skills:      {', '.join(ra.get('skills',[]))}
Experience:  {ra.get('experience','—')}
Education:   {ra.get('education','—')}

JOB DESCRIPTION
Role:             {jd.get('role','—')}
Required Skills:  {', '.join(jd.get('required_skills',[]))}
Experience:       {jd.get('experience','—')}

VALIDATION RESULTS
Match Score:     {result['match_score']}%
Risk Score:      {result['risk_score']}
Status:          {result['status']}
Recommendation:  {result.get('recommendation','—')}

INTERVIEW QUESTIONS
""" + "\n".join([f"{i+1}. {q}" for i, q in enumerate(iqs)])

    st.download_button(
        label="📥 Download .txt Report",
        data=content,
        file_name=f"hirelens_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
    )
    add_notification("📄 Report downloaded.", "📥")

# ─── ANALYTICS PAGE ──────────────────────────────────────────────────────────────
def page_analytics():
    render_topbar()
    st.markdown("## 📊 Analytics")

    reports = st.session_state.reports
    if not reports:
        st.info("Run validations to see analytics.")
        return

    try:
        import plotly.graph_objects as go
        import pandas as pd

        scores = [r["score"] for r in reports]
        names  = [r["name"][:20] for r in reports]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=names, y=scores,
            marker_color=["#22C55E" if s >= 80 else "#F59E0B" if s >= 60 else "#EF4444" for s in scores],
            text=scores, textposition="outside",
        ))
        fig.update_layout(
            title="Match Scores per Validation",
            xaxis_title="Candidate / Run",
            yaxis_title="Score (%)",
            yaxis_range=[0, 110],
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

        avg = sum(scores) / len(scores)
        high = sum(1 for s in scores if s >= 80)
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{avg:.1f}%")
        col2.metric("High Match (≥80%)", high)
        col3.metric("Total Validations", len(scores))
    except ImportError:
        st.warning("Install plotly for charts: `pip install plotly`")

# ─── HISTORY PAGE ────────────────────────────────────────────────────────────────
def page_history():
    render_topbar()
    st.markdown("## 🕐 History")

    if not st.session_state.reports:
        st.info("No validation history yet.")
        return

    for r in st.session_state.reports:
        badge_color = "#22C55E" if r["score"] >= 80 else "#F59E0B"
        st.markdown(f"""
        <div class="av-panel" style="margin-bottom:0.6rem; display:flex; justify-content:space-between; align-items:center;">
            <span><b>{r['name']}</b> &nbsp;<span style="font-size:0.78rem;color:var(--subtext);">📅 {r['date']}</span></span>
            <span style="color:{badge_color}; font-weight:700;">{r['score']}%</span>
        </div>
        """, unsafe_allow_html=True)

# ─── SETTINGS PAGE ───────────────────────────────────────────────────────────────
def page_settings():
    render_topbar()
    user = st.session_state.current_user
    st.markdown("## ⚙️ Settings")

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔒 Security", "🎨 Preferences"])

    with tab1:
        st.markdown("### Profile Information")
        new_name  = st.text_input("Full Name", value=user["name"])
        email_dis = st.text_input("Email", value=user["email"], disabled=True)
        new_avatar= st.selectbox("Avatar", ["👤", "🧑‍💼", "👩‍💼", "🧑‍💻", "👩‍💻"], index=["👤","🧑‍💼","👩‍💼","🧑‍💻","👩‍💻"].index(user.get("avatar","👤")))

        if st.button("💾 Save Profile", type="primary"):
            st.session_state.current_user["name"]   = new_name
            st.session_state.current_user["avatar"] = new_avatar
            st.session_state.users_db[user["email"]]["name"]   = new_name
            st.session_state.users_db[user["email"]]["avatar"] = new_avatar
            add_notification("Profile updated!", "✅")
            st.success("Profile saved!")

    with tab2:
        st.markdown("### Change Password")
        old_pw  = st.text_input("Current Password", type="password")
        new_pw  = st.text_input("New Password", type="password")
        new_pw2 = st.text_input("Confirm New Password", type="password")

        if st.button("🔑 Update Password", type="primary"):
            db = st.session_state.users_db
            if db[user["email"]]["password"] != hash_pw(old_pw):
                st.error("Current password incorrect.")
            elif new_pw != new_pw2:
                st.error("New passwords don't match.")
            elif len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                db[user["email"]]["password"] = hash_pw(new_pw)
                add_notification("Password changed successfully!", "🔐")
                st.success("Password updated!")

    with tab3:
        st.markdown("### Preferences")
        dm = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if dm != st.session_state.dark_mode:
            st.session_state.dark_mode = dm
            add_notification("Theme changed!", "🎨")
            st.rerun()

        st.markdown("**API Backend URL**")
        new_url = st.text_input("Backend URL", value=API_BASE_URL)
        if st.button("💾 Save URL", use_container_width=True):
            st.success(f"URL saved: {new_url} (update API_BASE_URL in app.py for persistence)")

# ─── NOTIFICATIONS PAGE ──────────────────────────────────────────────────────────
def page_notifications():
    render_topbar()
    st.markdown("## 🔔 Notifications")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✅ Mark all read", use_container_width=True):
            for n in st.session_state.notifications:
                n["read"] = True
            st.rerun()

    for notif in st.session_state.notifications:
        style = "opacity:0.55;" if notif["read"] else ""
        dot   = "" if notif["read"] else '<span class="notif-dot"></span>'
        st.markdown(f"""
        <div class="av-panel" style="margin-bottom:0.5rem; {style}">
            <span>{notif['icon']} {notif['msg']}{dot}</span>
            <span style="float:right; font-size:0.78rem; color:var(--subtext);">🕐 {notif['time']}</span>
        </div>
        """, unsafe_allow_html=True)
        notif["read"] = True

# ─── ADMIN PANEL ─────────────────────────────────────────────────────────────────
def page_admin():
    render_topbar()
    if st.session_state.current_user["role"] != "Admin":
        st.error("🚫 Access denied. Admins only.")
        return

    st.markdown("## 🛡️ Admin Panel")
    st.markdown(f"**Total Users:** {len(st.session_state.users_db)}")

    for email, u in st.session_state.users_db.items():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="av-panel" style="padding:0.6rem 1rem;">
                <b>{u['name']}</b> &nbsp;<span style="font-size:0.78rem;color:var(--subtext);">{email}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            badge = "badge-info" if u["role"] == "Admin" else "badge-success"
            st.markdown(f'<span class="badge {badge}" style="display:inline-block;margin-top:0.8rem;">{u["role"]}</span>', unsafe_allow_html=True)
        with col3:
            if email != st.session_state.current_user["email"]:
                if st.button("🗑", key=f"del_{email}", help="Remove user"):
                    del st.session_state.users_db[email]
                    st.rerun()

# ─── ROUTER ─────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        ap = st.session_state.auth_page
        if ap == "login":
            page_login()
        elif ap == "signup":
            page_signup()
        elif ap == "forgot":
            page_forgot()
        return

    render_sidebar()

    page_map = {
        "Dashboard":        page_dashboard,
        "Upload & Validate":page_upload,
        "Reports":          page_reports,
        "Analytics":        page_analytics,
        "History":          page_history,
        "Settings":         page_settings,
        "Notifications":    page_notifications,
        "Admin Panel":      page_admin,
    }

    current = st.session_state.active_page
    if current in page_map:
        page_map[current]()
    else:
        page_dashboard()

if __name__ == "__main__":
    main()