"""
Brand Guardian – ComplianceQA Streamlit Frontend
AI-powered video compliance auditing system.
"""

import uuid
import os
import requests
import json
import logging
import re
import streamlit as st

from dotenv import load_dotenv
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brand-guardian-ui")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/audit")

# ─── Page Config ───
st.set_page_config(
    page_title="Brand Guardian AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit elements (keep header for sidebar toggle) */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Hero header */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem 1rem;
    margin-bottom: 1rem;
}
.hero-icon {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    display: block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -1px;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #A3A3A3;
    margin-top: 0.5rem;
    font-weight: 400;
}

/* Glass card */
.glass-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    border-color: #525252;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

/* Status badges */
.status-pass {
    display: inline-block;
    background: #10B981;
    color: white;
    padding: 0.6rem 2rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: 2px;
}
.status-fail {
    display: inline-block;
    background: #EF4444;
    color: white;
    padding: 0.6rem 2rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: 2px;
}

/* Severity badges */
.severity-critical {
    display: inline-block;
    background: #7F1D1D;
    color: #FECACA;
    padding: 0.2rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.severity-high {
    display: inline-block;
    background: #78350F;
    color: #FDE68A;
    padding: 0.2rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.severity-medium {
    display: inline-block;
    background: #713F12;
    color: #FEF08A;
    padding: 0.2rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.severity-low {
    display: inline-block;
    background: #262626;
    color: #A3A3A3;
    padding: 0.2rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: 1px solid #404040;
}

/* Violation card */
.violation-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.violation-card:hover {
    transform: translateX(4px);
    border-color: #525252;
}
.violation-category {
    font-size: 1rem;
    font-weight: 600;
    color: #EDEDED;
    margin-bottom: 0.4rem;
}
.violation-desc {
    font-size: 0.9rem;
    color: #A3A3A3;
    line-height: 1.6;
}

/* Metric cards */
.metric-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #FFFFFF;
}
.metric-label {
    font-size: 0.8rem;
    color: #A3A3A3;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.2rem;
}

/* Sidebar styling */
.sidebar-step {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #EDEDED;
}
.sidebar-step-num {
    display: inline-block;
    background: #262626;
    color: #FFFFFF;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
    font-weight: 700;
    font-size: 0.75rem;
    margin-right: 0.6rem;
}

/* Input area */
.stTextInput > div > div > input {
    background: #0A0A0A !important;
    border: 1px solid #262626 !important;
    border-radius: 8px !important;
    color: #EDEDED !important;
    padding: 0.8rem 1rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #525252 !important;
    box-shadow: none !important;
}

/* Button */
.stButton > button {
    background: #FAFAFA !important;
    color: #0A0A0A !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #D4D4D4 !important;
    transform: translateY(-1px) !important;
}

/* Divider */
.section-divider {
    border: none;
    height: 1px;
    background: #262626;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ───
def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pat in patterns:
        match = re.search(pat, url)
        if match:
            return match.group(1)
    return None


def get_severity_badge(severity: str) -> str:
    """Return HTML for a colored severity badge."""
    s = severity.upper()
    css_class = {
        "CRITICAL": "severity-critical",
        "HIGH": "severity-high",
        "MEDIUM": "severity-medium",
        "LOW": "severity-low",
    }.get(s, "severity-low")
    return f'<span class="{css_class}">{s}</span>'


def count_by_severity(results: list) -> dict:
    """Count violations by severity level."""
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        sev = r.get("severity", "LOW").upper()
        if sev in counts:
            counts[sev] += 1
        else:
            counts["LOW"] += 1
    return counts


# ─── Sidebar ───
with st.sidebar:
    st.markdown("### 🛡️ Brand Guardian")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("#### How It Works")
    steps = [
        ("1", "Paste a YouTube URL"),
        ("2", "Video is downloaded & indexed"),
        ("3", "Azure AI extracts transcript & OCR"),
        ("4", "RAG retrieves compliance rules"),
        ("5", "LLM audits content for violations"),
    ]
    for num, text in steps:
        st.markdown(
            f'<div class="sidebar-step">'
            f'<span class="sidebar-step-num">{num}</span>{text}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("#### Tech Stack")
    st.markdown("""
    - 🧠 **LLM** — Groq (Llama 3.3 70B)
    - 🔍 **Search** — Azure AI Search
    - 🎥 **Video** — Azure Video Indexer
    - 📐 **Embeddings** — Azure OpenAI
    - ⚙️ **Orchestration** — LangGraph
    """)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.caption("Built with Streamlit • v1.0.0")


# ─── Hero ───
st.markdown("""
<div class="hero-container">
    <span class="hero-icon">🛡️</span>
    <h1 class="hero-title">Brand Guardian AI</h1>
    <p class="hero-subtitle">AI-Powered Video Compliance Auditing — Analyze YouTube content for regulatory violations in minutes.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─── Input Section ───
col_input, col_spacer = st.columns([3, 1])

with col_input:
    video_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://youtu.be/dT7S75eYhcQ",
        label_visibility="visible",
    )

run_audit = st.button("🚀  Run Compliance Audit", use_container_width=True)

# ─── Video Preview ───
if video_url:
    yt_id = extract_video_id(video_url)
    if yt_id:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("#### 🎥 Video Preview")
        st.video(f"https://www.youtube.com/watch?v={yt_id}")

# ─── Audit Execution ───
if run_audit:
    if not video_url or not video_url.strip():
        st.error("⚠️ Please enter a valid YouTube URL to begin the audit.")
        st.stop()

    yt_id = extract_video_id(video_url)
    if not yt_id:
        st.error("⚠️ Could not parse a valid YouTube video ID from the URL. Please check the link.")
        st.stop()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    initial_inputs = {
        "video_url": video_url.strip(),
        "video_id": video_id_short,
        "compliance_results": [],
        "errors": [],
    }

    # Run the workflow with progress tracking
    with st.status("🔍 Running Compliance Audit...", expanded=True) as status:
        try:
            st.write("⬇️  **Step 1/3** — Downloading & indexing video with Azure Video Indexer...")
            st.caption("This may take a few minutes while Azure processes the video.")

            # Send HTTP request to FastAPI backend
            response = requests.post(API_URL, json={"video_url": video_url.strip()})
            response.raise_for_status()
            final_state = response.json()

            st.write("📜  **Step 2/3** — Extracting transcript & OCR data...")
            st.write("🧠  **Step 3/3** — Analyzing content with LLM...")

            # Check for errors
            errors = final_state.get("errors", [])
            final_status = final_state.get("status", "UNKNOWN")

            if errors and final_status == "FAIL":
                status.update(label="❌ Audit Failed", state="error", expanded=True)
                st.error(f"The audit pipeline encountered an error:\n\n`{'; '.join(errors)}`")
                st.info("💡 **Tip:** Check that the YouTube URL is valid and accessible, and that your Azure credentials are configured correctly.")
                st.stop()

            status.update(label="✅ Audit Complete!", state="complete", expanded=False)

        except Exception as e:
            status.update(label="❌ Audit Failed", state="error", expanded=True)
            logger.error(f"Workflow failed: {e}")
            st.error(f"An unexpected error occurred:\n\n`{str(e)}`")
            st.info("💡 **Tip:** Ensure all Azure services are configured and the `.env` file has valid credentials.")
            st.stop()

    # ─── Results Dashboard ───
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    compliance_results = final_state.get("compliance_results", [])
    final_report = final_state.get("final_report", "No report generated.")
    final_status = final_state.get("status", "UNKNOWN")
    session_id = final_state.get("session_id", session_id)
    video_id_short = final_state.get("video_id", video_id_short)

    # Status Badge
    st.markdown("### 📊 Audit Results")
    st.markdown("")

    if final_status == "PASS":
        st.markdown('<div style="text-align:center; margin: 1.5rem 0;"><span class="status-pass">✅ PASS</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center; margin: 1.5rem 0;"><span class="status-fail">❌ FAIL</span></div>', unsafe_allow_html=True)

    st.markdown("")

    # Metrics Row
    severity_counts = count_by_severity(compliance_results)
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(compliance_results)}</div>
            <div class="metric-label">Total Violations</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #FCA5A5;">{severity_counts['CRITICAL']}</div>
            <div class="metric-label">Critical</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #FCD34D;">{severity_counts['HIGH']}</div>
            <div class="metric-label">High</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #FDE68A;">{severity_counts['MEDIUM']}</div>
            <div class="metric-label">Medium</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #67E8F9;">{severity_counts['LOW']}</div>
            <div class="metric-label">Low</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Violations List
    if compliance_results:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("### 🚨 Violations Detected")
        for i, issue in enumerate(compliance_results):
            cat = issue.get("category", "Unknown")
            sev = issue.get("severity", "LOW")
            desc = issue.get("description", "No description.")
            badge = get_severity_badge(sev)

            st.markdown(f"""
            <div class="violation-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span class="violation-category">#{i+1} — {cat}</span>
                    {badge}
                </div>
                <div class="violation-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card" style="text-align:center;">'
                    '<p style="font-size:1.2rem; color:#10B981; font-weight:600;">🎉 No violations detected!</p>'
                    '<p style="color:#8B949E;">This video appears to be fully compliant with all regulatory rules.</p>'
                    '</div>', unsafe_allow_html=True)

    # Full Report
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    with st.expander("📝 Full Compliance Report", expanded=True):
        st.markdown(f"""
        <div class="glass-card">
            <p style="color: #C9D1D9; line-height: 1.8; font-size: 0.95rem;">{final_report}</p>
        </div>
        """, unsafe_allow_html=True)

    # Session Info & Raw JSON
    with st.expander("🔧 Session Details & Raw Output"):
        st.markdown(f"**Session ID:** `{session_id}`")
        st.markdown(f"**Video ID:** `{video_id_short}`")
        st.markdown(f"**Status:** `{final_status}`")
        st.markdown("---")
        st.json({
            "session_id": session_id,
            "video_id": video_id_short,
            "status": final_status,
            "final_report": final_report,
            "compliance_results": compliance_results,
        })
