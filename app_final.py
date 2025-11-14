"""
REVA - CRE Deal Intelligence Platform
Real integrations with auto-flow demo mode
"""
import streamlit as st
import logging
import json
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modules
from cre_agent.config import load_settings
from cre_agent.deepgram_client import DeepgramClient
from cre_agent.merge_client import MergeClient
from cre_agent.scoring import get_default_buybox
from cre_agent.agent_orchestrator import run_deal_agent
from cre_agent.storage import (
    build_evidence_packet, send_to_vanta, send_to_thoropass,
    run_daily_summary_job, get_cluster_health
)
from cre_agent.examples import get_all_examples

# Page config
st.set_page_config(
    page_title="REVA • Deal Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
if 'deal_text' not in st.session_state:
    st.session_state.deal_text = ""
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'auto_run' not in st.session_state:
    st.session_state.auto_run = False
if 'last_run' not in st.session_state:
    st.session_state.last_run = None

# REVA Theme with typewriter font and blue/purple aesthetic
dark_mode = st.session_state.dark_mode
bg_color = '#0B1020' if dark_mode else '#F6F8FF'
text_color = '#F6F8FF' if dark_mode else '#0B1020'
card_bg = 'rgba(58, 124, 255, 0.08)' if dark_mode else 'rgba(246, 248, 255, 0.95)'

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    /* Film grain overlay */
    body {{
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='grain'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23grain)' opacity='0.03'/%3E%3C/svg%3E");
        background-repeat: repeat;
        background-size: 200px 200px;
    }}

    /* Base styling */
    .stApp {{
        background: {bg_color};
        color: {text_color};
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
    }}

    /* Typography - Typewriter style */
    h1, h2, h3 {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    /* Typewriter flicker on main title */
    @keyframes flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.92; }}
    }}

    .main-title {{
        animation: flicker 0.8s infinite;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5em;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: {'#78A7FF' if dark_mode else '#0B5CFF'};
    }}

    /* Blue/purple gradient hero */
    .hero-gradient {{
        background: linear-gradient(135deg, #0B5CFF 0%, #3A7CFF 50%, #7B2CBF 100%);
        padding: 60px 20px;
        border-radius: 0 0 50% 50% / 0 0 20px 20px;
        text-align: center;
        margin-bottom: 40px;
    }}

    /* Verdict cards with blue/purple gradients */
    .verdict-pass {{
        background: linear-gradient(135deg, #0B5CFF, #3A7CFF);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border: 2px dashed rgba(255,255,255,0.4);
    }}

    .verdict-watch {{
        background: linear-gradient(135deg, #7B2CBF, #9D4EDD);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border: 2px dashed rgba(255,255,255,0.4);
    }}

    .verdict-hard-pass {{
        background: linear-gradient(135deg, #3A0CA3, #4361EE);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border: 2px dashed rgba(255,255,255,0.4);
    }}

    /* Status */
    .status-healthy {{color: #3A7CFF; font-family: 'IBM Plex Mono', monospace; font-weight: 600;}}
    .status-unhealthy {{color: #7B2CBF; font-family: 'IBM Plex Mono', monospace; font-weight: 600;}}

    /* Links with dotted underline */
    a {{
        color: #00A3FF;
        text-decoration: underline dotted;
        text-underline-offset: 4px;
        font-family: 'IBM Plex Mono', monospace;
    }}
    a:hover {{text-decoration-style: solid;}}

    /* Buttons */
    .stButton>button {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 4px;
        border: 2px solid #78A7FF;
        background: {card_bg};
        transition: all 0.2s;
    }}
    .stButton>button:hover {{
        border-color: #3A7CFF;
        box-shadow: 0 0 20px rgba(58, 124, 255, 0.3);
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {'#0F1419' if dark_mode else '#FAFBFF'};
        border-right: 2px dashed #78A7FF;
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Dividers - dotted */
    hr {{border: none; border-top: 2px dotted #78A7FF; margin: 30px 0;}}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 2px dashed #78A7FF;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 11px;
        padding: 12px 16px;
    }}

    /* Code/mono */
    code {{
        background: {'rgba(120, 167, 255, 0.15)' if dark_mode else 'rgba(230, 239, 255, 0.6)'};
        padding: 3px 8px;
        border-radius: 3px;
        font-family: 'IBM Plex Mono', monospace;
        border: 1px dotted #78A7FF;
        font-size: 0.85em;
    }}

    /* Max width container */
    .sheet {{
        max-width: 1040px;
        margin: 0 auto;
        padding: 24px;
    }}

    /* Progress indicator */
    .progress-step {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9em;
        color: #78A7FF;
        padding: 8px 16px;
        border-left: 3px solid #3A7CFF;
        margin: 8px 0;
        background: {card_bg};
    }}

    /* Auto-run banner */
    .auto-run-banner {{
        background: linear-gradient(135deg, #0B5CFF, #7B2CBF);
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        text-align: center;
        margin: 20px 0;
        letter-spacing: 0.05em;
    }}

    /* Footer */
    .footer {{
        border-top: 2px dotted #78A7FF;
        padding: 20px;
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75em;
        color: #78A7FF;
        margin-top: 60px;
    }}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown('<div class="main-title">⚡ REVA</div>', unsafe_allow_html=True)
    st.caption("DEAL INTELLIGENCE PLATFORM")
with col2:
    if st.session_state.settings.demo_mode:
        st.warning("⚠️ DEMO MODE - Configure real APIs in .env", icon="⚠️")
    else:
        st.success("✅ PRODUCTION MODE - Real API integrations active", icon="✅")
with col3:
    if st.button("🌓 DARK", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("---")

# Sidebar
st.sidebar.markdown("### ⚙️ BUY-BOX CONFIG")

buybox = {
    "min_cap_rate": st.sidebar.slider("MIN CAP %", 0.0, 15.0, 5.0, 0.25),
    "max_cap_rate": st.sidebar.slider("MAX CAP %", 0.0, 15.0, 8.0, 0.25),
    "max_ltv": st.sidebar.slider("MAX LTV %", 0, 100, 75, 5) / 100.0,
    "min_deal_size": st.sidebar.number_input("MIN SIZE $", value=5_000_000, step=1_000_000),
    "max_deal_size": st.sidebar.number_input("MAX SIZE $", value=50_000_000, step=5_000_000),
}

st.sidebar.markdown("### 📍 MARKETS")
all_markets = ["Austin", "Dallas", "Phoenix", "Atlanta", "Denver"]
buybox["preferred_markets"] = st.sidebar.multiselect("Select", all_markets, default=all_markets)

st.sidebar.markdown("### 🏢 PROPERTY TYPES")
all_types = ["multifamily", "industrial", "office", "retail"]
buybox["preferred_property_types"] = st.sidebar.multiselect("Select", all_types, default=["multifamily", "industrial"])

st.sidebar.markdown("---")
st.sidebar.markdown("**INTEGRATIONS**")
st.sidebar.markdown(f"AWS: {'✅' if st.session_state.settings.has_aws_config else '❌'}")
st.sidebar.markdown(f"Deepgram: {'✅' if st.session_state.settings.has_deepgram_config else '❌'}")
st.sidebar.markdown(f"Merge: {'✅' if st.session_state.settings.has_merge_config else '❌'}")

# Main content
st.markdown("## 📝 INPUT DEAL")

# Input method selector
input_method = st.radio(
    "INPUT METHOD",
    ["🎤 AUDIO FILE", "📄 TEXT", "📋 EXAMPLE"],
    horizontal=True
)

if input_method == "🎤 AUDIO FILE":
    st.markdown("**UPLOAD BROKER CALL RECORDING**")

    uploaded_file = st.file_uploader(
        "Choose audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        help="Upload recording of broker call or deal discussion",
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.audio(uploaded_file)

        if st.button("🎤 TRANSCRIBE WITH DEEPGRAM", type="primary", use_container_width=True):
            with st.spinner("Transcribing audio..."):
                try:
                    deepgram_client = DeepgramClient(
                        api_key=st.session_state.settings.deepgram_api_key,
                        demo_mode=not st.session_state.settings.has_deepgram_config
                    )

                    audio_bytes = uploaded_file.read()
                    transcript = deepgram_client.transcribe_bytes(audio_bytes, uploaded_file.name)

                    st.session_state.deal_text = transcript
                    st.success(f"✅ Transcribed {len(audio_bytes)} bytes → {len(transcript)} chars")
                    st.rerun()

                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    # Show transcript if available
    if st.session_state.deal_text:
        st.markdown("**TRANSCRIPT:**")
        st.session_state.deal_text = st.text_area(
            "Edit if needed",
            value=st.session_state.deal_text,
            height=200,
            label_visibility="collapsed"
        )

elif input_method == "📄 TEXT":
    st.markdown("**PASTE DEAL TEXT**")
    st.session_state.deal_text = st.text_area(
        "Paste broker email, OM, or deal notes",
        value=st.session_state.deal_text,
        height=200,
        placeholder="Paste your deal text here...",
        label_visibility="collapsed"
    )

else:  # EXAMPLE
    st.markdown("**LOAD EXAMPLE DEAL**")
    examples = get_all_examples()
    selected_example = st.selectbox(
        "Choose example",
        options=[""] + list(examples.keys()),
        format_func=lambda x: "Select..." if x == "" else x,
        label_visibility="collapsed"
    )

    if selected_example:
        st.session_state.deal_text = examples[selected_example]
        st.text_area(
            "Deal text",
            value=st.session_state.deal_text,
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )

# Auto-run button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 RUN FULL ANALYSIS", type="primary", use_container_width=True, disabled=not st.session_state.deal_text):
        st.session_state.auto_run = True
        st.rerun()

st.markdown("---")

# Auto-run workflow
if st.session_state.auto_run and st.session_state.deal_text:
    st.markdown('<div class="auto-run-banner">⚡ RUNNING AUTOMATED ANALYSIS PIPELINE</div>', unsafe_allow_html=True)

    progress_container = st.empty()

    # Step 1: Deal Analysis
    with progress_container.container():
        st.markdown('<div class="progress-step">► STEP 1/5: Analyzing deal structure...</div>', unsafe_allow_html=True)

    with st.spinner("Processing..."):
        try:
            run_payload = run_deal_agent(
                raw_text=st.session_state.deal_text,
                buybox=buybox,
                config=st.session_state.settings
            )
            st.session_state.last_run = run_payload
            time.sleep(0.5)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.session_state.auto_run = False
            st.stop()

    # Show results
    st.success("✅ DEAL ANALYZED")

    structured = run_payload.get("structured_deal", {})
    score_data = run_payload.get("score_data", {})

    col1, col2, col3 = st.columns(3)
    with col1:
        verdict = score_data.get("verdict", "Unknown")
        verdict_class = f"verdict-{verdict.lower().replace(' ', '-')}"
        st.markdown(f'<div class="{verdict_class}">VERDICT: {verdict}<br>SCORE: {score_data.get("score", 0)}/100</div>', unsafe_allow_html=True)
    with col2:
        st.metric("CAP RATE", f"{score_data.get('metrics', {}).get('cap_rate', 'N/A')}")
    with col3:
        deal_size = score_data.get('metrics', {}).get('deal_size')
        st.metric("DEAL SIZE", f"${deal_size:,.0f}" if deal_size else "N/A")

    st.markdown("**IC SUMMARY:**")
    st.markdown(run_payload.get("ic_summary", ""))

    time.sleep(1)

    # Step 2: CRM
    with progress_container.container():
        st.markdown('<div class="progress-step">► STEP 2/5: Creating CRM records...</div>', unsafe_allow_html=True)

    with st.spinner("Creating CRM records..."):
        try:
            merge_client = MergeClient(
                api_key=st.session_state.settings.merge_api_key,
                account_token=st.session_state.settings.merge_account_token,
                demo_mode=not st.session_state.settings.has_merge_config
            )

            broker_name = structured.get("broker_name")
            broker_email = structured.get("broker_email")
            broker_company = structured.get("broker_company")

            contact_id = merge_client.upsert_contact(broker_email, broker_name, broker_company)
            note_id = merge_client.create_note(contact_id, f"Deal: {score_data.get('score')}/100 - {score_data.get('verdict')}")
            task_id = merge_client.create_task(contact_id, "Follow up on deal")

            st.session_state.last_run["crm_records"] = {
                "contact_id": contact_id,
                "note_id": note_id,
                "task_id": task_id
            }
            time.sleep(0.5)
            st.success(f"✅ CRM RECORDS CREATED: {contact_id}")
        except Exception as e:
            st.warning(f"CRM creation: {e}")

    # Step 3: Evidence
    with progress_container.container():
        st.markdown('<div class="progress-step">► STEP 3/5: Generating evidence packets...</div>', unsafe_allow_html=True)

    with st.spinner("Building evidence..."):
        try:
            evidence = build_evidence_packet(st.session_state.last_run)
            vanta_ack = send_to_vanta(evidence)
            thoropass_ack = send_to_thoropass(evidence)
            time.sleep(0.5)
            st.success(f"✅ EVIDENCE SENT: Vanta {vanta_ack['evidence_id']}, Thoropass {thoropass_ack['evidence_id']}")
        except Exception as e:
            st.warning(f"Evidence: {e}")

    # Step 4: Daily Job
    with progress_container.container():
        st.markdown('<div class="progress-step">► STEP 4/5: Running daily summary job...</div>', unsafe_allow_html=True)

    with st.spinner("Analyzing pipeline..."):
        try:
            summary = run_daily_summary_job()
            time.sleep(0.5)
            if summary.get("status") == "success":
                st.success(f"✅ PIPELINE SUMMARY: {summary['deal_count']} deals, {summary['avg_score']}/100 avg")
        except Exception as e:
            st.warning(f"Summary job: {e}")

    # Step 5: Security Check
    with progress_container.container():
        st.markdown('<div class="progress-step">► STEP 5/5: Checking infrastructure...</div>', unsafe_allow_html=True)

    with st.spinner("Checking systems..."):
        try:
            health = get_cluster_health()
            time.sleep(0.5)
            st.success(f"✅ CLUSTER STATUS: {health['status'].upper()} - {health['nodes']} nodes, {health['pods']} pods")
        except Exception as e:
            st.warning(f"Health check: {e}")

    st.markdown('<div class="auto-run-banner">✅ ANALYSIS COMPLETE</div>', unsafe_allow_html=True)

    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.auto_run = False
        st.session_state.deal_text = ""
        st.session_state.last_run = None
        st.rerun()

# Footer
st.markdown("""
<div class="footer">
© REVA 2025 • EXPERIMENTAL CIVIC INTERFACE<br>
AWS • DEEPGRAM • MERGE • ISLAND • SPECTRO • VANTA • THOROPASS • DAGSTER • CODER
</div>
""", unsafe_allow_html=True)
