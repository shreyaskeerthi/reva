"""
REVA - Real Estate Voice Agent - Main Streamlit Application
"""
import streamlit as st
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from cre_agent.config import load_settings
from cre_agent.deepgram_client import DeepgramClient
from cre_agent.merge_client import MergeClient
from cre_agent.scoring import get_default_buybox
from cre_agent.agent_orchestrator import run_deal_agent
from cre_agent.storage import (
    build_evidence_packet,
    send_to_vanta,
    send_to_thoropass,
    run_daily_summary_job,
    get_cluster_health,
    upload_evidence_to_s3
)
from cre_agent.examples import get_all_examples

# Page config
st.set_page_config(
    page_title="REVA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# REVA Aesthetic - Dark mode only with typewriter font and blue/purple gradient
bg_color = '#0B1020'
text_color = '#F6F8FF'
card_bg = 'rgba(246, 248, 255, 0.05)'

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap" rel="stylesheet">

<style>
    /* Global variables */
    .stApp {{
        background: {bg_color};
        color: {text_color};
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Film grain effect */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
        opacity: 0.03;
        z-index: 9999;
    }}

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    /* Headers */
    h1, h2, h3 {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        color: {text_color};
    }}

    /* Flickering main title */
    @keyframes flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.92; }}
    }}
    .main-title {{
        animation: flicker 0.8s infinite;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5em;
        letter-spacing: 0.15em;
        color: #78A7FF;
        font-weight: 700;
        margin-bottom: 0;
    }}

    /* Subtitle with gradient */
    .reva-subtitle {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9em;
        letter-spacing: 0.1em;
        background: linear-gradient(135deg, #0B5CFF 0%, #3A7CFF 50%, #7B2CBF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Verdict cards with gradient + dashed borders */
    .verdict-pass {{
        background: linear-gradient(135deg, #0B5CFF, #3A7CFF);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        border: 2px dashed rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }}
    .verdict-watch {{
        background: linear-gradient(135deg, #7B2CBF, #9D4EDD);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        border: 2px dashed rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }}
    .verdict-hard-pass {{
        background: linear-gradient(135deg, #3A0CA3, #4361EE);
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        border: 2px dashed rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }}

    /* Status indicators */
    .status-healthy {{
        color: #06D6A0;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
    }}
    .status-unhealthy {{
        color: #EF476F;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Navigation hints */
    .navigation-hint {{
        background: rgba(58, 124, 255, 0.1);
        border-left: 4px solid #3A7CFF;
        padding: 16px 20px;
        margin: 20px 0;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        border-bottom: 1px dashed #78A7FF;
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Buttons with glow */
    .stButton>button {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-radius: 4px;
        border: 2px solid #78A7FF;
        background: {card_bg};
        transition: all 0.2s;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        border-color: #3A7CFF;
        box-shadow: 0 0 20px rgba(58, 124, 255, 0.3);
        transform: translateY(-1px);
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: #0F1419;
        border-right: 2px dashed #78A7FF;
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Link styles */
    a {{
        color: #00A3FF;
        text-decoration: underline dotted;
        text-underline-offset: 4px;
    }}
    a:hover {{
        text-decoration-style: solid;
        color: #3A7CFF;
    }}

    /* Dotted dividers */
    hr {{
        border: none;
        border-top: 2px dotted #78A7FF;
        margin: 30px 0;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 2px dotted #78A7FF;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'IBM Plex Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 11px;
        padding: 12px 16px;
        font-weight: 600;
    }}

    /* Code blocks */
    code {{
        background: rgba(120, 167, 255, 0.15);
        padding: 3px 8px;
        border-radius: 3px;
        border: 1px dotted #78A7FF;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9em;
    }}

    /* Input fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {{
        border: 1px solid #78A7FF;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
    }}

    /* Metric cards */
    .metric-box {{
        background: {card_bg};
        padding: 20px;
        border-radius: 4px;
        border: 1px dashed #78A7FF;
        margin: 10px 0;
    }}
</style>
""", unsafe_allow_html=True)

# Load Island shim (JavaScript for browser trust telemetry)
st.markdown("""
<script src="/static/island-shim.js"></script>
""", unsafe_allow_html=True)

# Initialize session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

if 'last_run' not in st.session_state:
    st.session_state.last_run = None

if 'island_signals' not in st.session_state:
    st.session_state.island_signals = []

if 'deal_text' not in st.session_state:
    st.session_state.deal_text = ""

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

if 'switch_to_tab' not in st.session_state:
    st.session_state.switch_to_tab = None

if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

# Main title - Dark mode only
st.markdown('<h1 class="main-title">⚡ REVA</h1>', unsafe_allow_html=True)
st.markdown('<p class="reva-subtitle">POWERED BY AWS BEDROCK & S3 • DEEPGRAM • MERGE</p>', unsafe_allow_html=True)

# Sidebar: Buy-box Settings
st.sidebar.header("⚙️ Buy-Box Settings")

buybox = {
    "min_cap_rate": st.sidebar.slider(
        "Min Cap Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=5.0,
        step=0.25
    ),
    "max_cap_rate": st.sidebar.slider(
        "Max Cap Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=8.0,
        step=0.25
    ),
    "max_ltv": st.sidebar.slider(
        "Max LTV (%)",
        min_value=0,
        max_value=100,
        value=75,
        step=5
    ) / 100.0,
    "min_deal_size": st.sidebar.number_input(
        "Min Deal Size ($)",
        min_value=0,
        max_value=100_000_000,
        value=5_000_000,
        step=1_000_000,
        format="%d"
    ),
    "max_deal_size": st.sidebar.number_input(
        "Max Deal Size ($)",
        min_value=0,
        max_value=500_000_000,
        value=50_000_000,
        step=5_000_000,
        format="%d"
    ),
}

# Preferred markets
st.sidebar.subheader("Preferred Markets")
all_markets = ["Austin", "Dallas", "Phoenix", "Atlanta", "Denver", "Miami", "Los Angeles", "Seattle"]
selected_markets = st.sidebar.multiselect(
    "Select markets",
    options=all_markets,
    default=["Austin", "Dallas", "Phoenix", "Atlanta", "Denver"]
)
buybox["preferred_markets"] = selected_markets

# Preferred property types
st.sidebar.subheader("Preferred Property Types")
all_types = ["multifamily", "industrial", "office", "retail", "mixed_use"]
selected_types = st.sidebar.multiselect(
    "Select types",
    options=all_types,
    default=["multifamily", "industrial"]
)
buybox["preferred_property_types"] = selected_types

# Integration status with REVA styling
st.sidebar.divider()
st.sidebar.markdown("**INTEGRATIONS**")
st.sidebar.markdown(f"**AWS Bedrock:** {'✅' if st.session_state.settings.has_aws_config else '❌'}")
st.sidebar.markdown(f"**Deepgram:** {'✅' if st.session_state.settings.has_deepgram_config else '❌'}")
st.sidebar.markdown(f"**Merge CRM:** {'✅' if st.session_state.settings.has_merge_config else '❌'}")

# Check for tab navigation via query params
query_params = st.query_params
if "tab" in query_params:
    try:
        tab_index = int(query_params["tab"])
        st.session_state.switch_to_tab = tab_index
        st.query_params.clear()
    except:
        pass

# Main content area tabs
tab_names = ["Input", "Analyze", "CRM", "Evidence", "Jobs", "Security & Infra", "History"]
tab_input, tab_analyze, tab_crm, tab_evidence, tab_jobs, tab_security, tab_history = st.tabs(tab_names)

# Handle programmatic tab switching via JS
if st.session_state.switch_to_tab is not None:
    tab_index = st.session_state.switch_to_tab
    st.session_state.switch_to_tab = None
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            var tabButtons = document.querySelectorAll('[data-testid="stTabs"] button, button[role="tab"], [data-baseweb="tab"]');
            if (tabButtons.length === 0) {{
                var tabContainer = document.querySelector('[data-testid="stTabs"]');
                if (tabContainer) {{
                    tabButtons = tabContainer.querySelectorAll('button');
                }}
            }}
            if (tabButtons.length > {tab_index}) {{
                tabButtons[{tab_index}].click();
            }}
        }}, 150);
    </script>
    """, unsafe_allow_html=True)

# TAB: Input
with tab_input:
    st.header("Deal Input")

    input_method = st.radio("Input Method", ["Voice (Deepgram)", "Paste Text", "Load Example"])

    if input_method == "Voice (Deepgram)":
        st.subheader("Upload Audio File")

        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["wav", "mp3", "m4a", "flac"],
            help="Upload a recording of a broker call or deal discussion"
        )

        # Clear transcript if a new file is uploaded
        if uploaded_file:
            current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.last_uploaded_file != current_file_id:
                st.session_state.deal_text = ""
                st.session_state.last_uploaded_file = current_file_id

        if uploaded_file:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.audio(uploaded_file)

            with col2:
                if st.button("🎤 Transcribe with Deepgram", use_container_width=True):
                    with st.spinner("Transcribing..."):
                        deepgram_client = DeepgramClient(
                            api_key=st.session_state.settings.deepgram_api_key,
                            demo_mode=not st.session_state.settings.has_deepgram_config
                        )
                        audio_bytes = uploaded_file.read()
                        transcript = deepgram_client.transcribe_bytes(
                            audio_bytes,
                            filename=uploaded_file.name
                        )
                        st.session_state.deal_text = transcript
                        st.success("Transcription complete!")
                        st.rerun()

        if st.session_state.deal_text:
            st.subheader("Transcript")
            st.session_state.deal_text = st.text_area(
                "Edit transcript if needed:",
                value=st.session_state.deal_text,
                height=300,
                key="transcript_editor"
            )

    elif input_method == "Paste Text":
        st.subheader("Paste Deal Text")
        st.session_state.deal_text = st.text_area(
            "Paste broker email, OM, or deal notes:",
            value=st.session_state.deal_text,
            height=300,
            placeholder="Paste your deal text here...",
            key="paste_editor"
        )

        # Show progress indicator when text is entered
        if st.session_state.deal_text and st.session_state.deal_text.strip():
            if 'previous_paste_text' not in st.session_state:
                st.session_state.previous_paste_text = ""
            is_new_paste = st.session_state.deal_text != st.session_state.previous_paste_text
            if is_new_paste:
                with st.spinner("📋 Processing pasted text..."):
                    progress_bar = st.progress(0)
                    status_text = st.caption("Processing...")
                    for i in range(0, 101, 20):
                        progress_bar.progress(i / 100)
                        if i < 100:
                            status_text.caption(f"📋 Processing text... {i}%")
                        time.sleep(0.1)
                    progress_bar.progress(1.0)
                    status_text.caption("Complete!")
                    time.sleep(0.2)
                st.success("Text loaded successfully!")
                st.session_state.previous_paste_text = st.session_state.deal_text
            else:
                st.success("Text loaded successfully!")
        else:
            if 'previous_paste_text' in st.session_state:
                st.session_state.previous_paste_text = ""

    else:  # Load Example
        st.subheader("Load Example Deal")
        examples = get_all_examples()
        selected_example = st.selectbox(
            "Choose an example:",
            options=list(examples.keys())
        )

        if st.button("Load Example"):
            st.session_state.deal_text = examples[selected_example]
            st.success(f"Loaded: {selected_example}")

        if st.session_state.deal_text:
            st.text_area(
                "Deal text:",
                value=st.session_state.deal_text,
                height=300,
                disabled=True,
                key="example_viewer"
            )

    if st.session_state.deal_text:
        st.divider()
        st.markdown('<div class="navigation-hint"> Deal text loaded! Ready for analysis.</div>', unsafe_allow_html=True)
        # optional auto-nav:
        # if st.button("➡️ Next: Analyze Deal", type="primary", use_container_width=True, key="nav_to_analyze"):
        #     st.session_state.switch_to_tab = 1
        #     st.rerun()

# TAB: Analyze
with tab_analyze:
    st.header("Deal Analysis")

    if not st.session_state.deal_text:
        st.info("Please input deal text in the Input tab first")
    else:
        if st.button("Run CRE Deal Agent", type="primary", use_container_width=True):
            with st.spinner("Analyzing deal..."):
                try:
                    run_payload = run_deal_agent(
                        raw_text=st.session_state.deal_text,
                        buybox=buybox,
                        config=st.session_state.settings
                    )
                    st.session_state.last_run = run_payload
                    st.success(f"Analysis complete! Run ID: {run_payload['run_id']}")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                    logger.exception("Analysis failed")

        if st.session_state.last_run:
            run = st.session_state.last_run
            structured = run.get("structured_deal", {})
            score_data = run.get("score_data", {})
            metrics = score_data.get("metrics", {})

            verdict = score_data.get("verdict", "Unknown")
            verdict_class = f"verdict-{verdict.lower().replace(' ', '-')}"

            st.markdown(
                f'<div class="{verdict_class}">Verdict: {verdict} (Score: {score_data.get("score", 0)}/100)</div>',
                unsafe_allow_html=True
            )

            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                cap_rate = metrics.get("cap_rate") or structured.get("cap_rate")
                st.metric("Cap Rate", f"{cap_rate:.2f}%" if cap_rate else "N/A")

            with col2:
                deal_size = metrics.get("deal_size")
                st.metric("Deal Size", f"${deal_size:,.0f}" if deal_size else "N/A")

            with col3:
                ppu = metrics.get("price_per_unit")
                st.metric("Price/Unit", f"${ppu:,.0f}" if ppu else "N/A")

            with col4:
                ppsf = metrics.get("price_per_sf")
                st.metric("Price/SF", f"${ppsf:.2f}" if ppsf else "N/A")

            st.subheader("Scoring Breakdown")
            reasons = score_data.get("reasons", [])
            for reason in reasons:
                if "✓" in reason:
                    st.markdown(f"✅ {reason}")
                else:
                    st.markdown(f"⚠️ {reason}")

            st.subheader("Structured Deal Data")
            st.json(structured)

            st.subheader("Investment Committee Summary")
            ic_summary = run.get("ic_summary", "")
            st.markdown(ic_summary)

            if st.button("📋 Send IC Summary to Slack"):
                st.code(ic_summary, language=None)
                st.info("Copy the text above to your clipboard")

            st.divider()
            st.markdown('<div class="navigation-hint"> Deal analyzed!  CRM records Viewable.</div>', unsafe_allow_html=True)


# TAB: CRM
with tab_crm:
    st.header("CRM Actions (Merge)")

    if not st.session_state.last_run:
        st.info("Please analyze a deal first")
    else:
        run = st.session_state.last_run
        structured = run.get("structured_deal", {})

        st.subheader("Contact Information")
        col1, col2 = st.columns(2)

        with col1:
            broker_name = st.text_input(
                "Broker Name",
                value=structured.get("broker_name", "")
            )
            broker_email = st.text_input(
                "Broker Email",
                value=structured.get("broker_email", "")
            )

        with col2:
            broker_company = st.text_input(
                "Broker Company",
                value=structured.get("broker_company", "")
            )
            location = structured.get("location", {})
            deal_location = f"{location.get('city', '')}, {location.get('state', '')}" if isinstance(location, dict) else ""

        if st.button(" Create CRM Records via Merge", type="primary", use_container_width=True):
            with st.spinner("Creating CRM records..."):
                try:
                    merge_client = MergeClient(
                        api_key=st.session_state.settings.merge_api_key,
                        account_token=st.session_state.settings.merge_account_token,
                        base_url=st.session_state.settings.merge_base_url,
                        demo_mode=st.session_state.settings.demo_mode or not st.session_state.settings.has_merge_config
                    )

                    contact_id = merge_client.upsert_contact(
                        email=broker_email or None,
                        name=broker_name or None,
                        company=broker_company or None
                    )

                    note_content = f"Deal Analysis - {structured.get('property_type', 'Property')} in {deal_location}\n\n"
                    note_content += f"Score: {run['score_data']['score']}/100 ({run['score_data']['verdict']})\n"
                    note_content += f"Cap Rate: {run['score_data']['metrics'].get('cap_rate', 'N/A')}\n"
                    note_content += f"Price: ${run['score_data']['metrics'].get('deal_size', 0):,.0f}\n"
                    note_content += f"\nRun ID: {run['run_id']}"

                    note_id = merge_client.create_note(contact_id, note_content)

                    task_title = f"Follow up on {structured.get('property_type', 'deal')} in {deal_location}"
                    task_id = merge_client.create_task(contact_id, task_title)

                    st.session_state.last_run["crm_records"] = {
                        "contact_id": contact_id,
                        "note_id": note_id,
                        "task_id": task_id,
                        "created_at": datetime.now().isoformat()
                    }

                    st.success(" CRM records created successfully!")
                    st.info(f"**Contact ID:** {contact_id}")
                    st.info(f"**Note ID:** {note_id}")
                    st.info(f"**Task ID:** {task_id}")

                except Exception as e:
                    st.error(f"Error creating CRM records: {e}")
                    logger.exception("CRM creation failed")

        if "crm_records" in st.session_state.last_run:
            st.subheader("Created CRM Records")
            st.json(st.session_state.last_run["crm_records"])

            st.divider()
            st.markdown('<div class="navigation-hint"> CRM records created! Click below to generate evidence packets.</div>', unsafe_allow_html=True)
            if st.button("Next: Generate Evidence", type="primary", use_container_width=True, key="nav_to_evidence"):
                st.session_state.switch_to_tab = 3
                st.rerun()

# TAB: Evidence
with tab_evidence:
    st.header("Evidence & Compliance")

    if not st.session_state.last_run:
        st.info("Please analyze a deal first")
    else:
        st.markdown("Generate compliance evidence packets for Vanta and Thoropass")

        if st.button(" Generate & Send Evidence Packet", use_container_width=True):
            with st.spinner("Generating evidence packet..."):
                try:
                    evidence = build_evidence_packet(st.session_state.last_run)

                    st.subheader("Evidence Packet")
                    st.json(evidence)

                    # Upload to S3 if configured
                    s3_uri = None
                    if st.session_state.settings.has_s3_config and st.session_state.settings.s3_bucket:
                        with st.spinner("Uploading evidence to S3..."):
                            s3_uri = upload_evidence_to_s3(
                                evidence,
                                st.session_state.settings.s3_bucket,
                                st.session_state.settings.aws_region
                            )
                            if s3_uri:
                                evidence["s3_uri"] = s3_uri
                                st.success(f"✅ Uploaded to S3: {s3_uri}")
                            else:
                                st.warning("⚠️ Failed to upload to S3, but continuing with local storage")
                    else:
                        st.info("ℹ️ S3 not configured. Evidence will be stored locally only.")

                    vanta_ack = send_to_vanta(evidence)
                    st.success(f"✅ Sent to Vanta: {vanta_ack['evidence_id']}")

                    thoropass_ack = send_to_thoropass(evidence)
                    st.success(f"✅ Sent to Thoropass: {thoropass_ack['evidence_id']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Vanta ACK")
                        st.json(vanta_ack)
                    with col2:
                        st.subheader("Thoropass ACK")
                        st.json(thoropass_ack)

                    # Show storage locations
                    storage_locations = ["Evidence logged to: ./runs/evidence_log.jsonl"]
                    if s3_uri:
                        storage_locations.append(f"S3 URI: {s3_uri}")
                    st.info(" | ".join(storage_locations))

                    st.divider()
                    st.markdown('<div class="navigation-hint">✅ Evidence packets sent! Click below to run daily summary job.</div>', unsafe_allow_html=True)
                    if st.button("Next: Run Daily Summary Job", type="primary", use_container_width=True, key="nav_to_jobs"):
                        st.session_state.switch_to_tab = 4
                        st.rerun()

                except Exception as e:
                    st.error(f"Error generating evidence: {e}")
                    logger.exception("Evidence generation failed")

# TAB: Jobs
with tab_jobs:
    st.header("Dagster-Style Daily Summary Job")

    st.markdown("""
    This simulates a Dagster orchestration job that would run daily to summarize all deal activity.
    In production, this would be scheduled via Dagster to run automatically.
    """)

    if st.button("Run Daily Summary Job", use_container_width=True):
        with st.spinner("Running daily summary job..."):
            try:
                summary = run_daily_summary_job()

                if summary["status"] == "success":
                    st.success(f"✅ Job completed at {summary['job_run_time']}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Deals", summary["deal_count"])
                    with col2:
                        st.metric("Avg Score", f"{summary['avg_score']}/100")
                    with col3:
                        st.metric("Pass", summary["verdicts"]["pass"])
                    with col4:
                        st.metric("Watch", summary["verdicts"]["watch"])

                    st.subheader("Top 3 Deals by Score")
                    for i, deal in enumerate(summary["top_deals"], 1):
                        with st.expander(f"#{i} - {deal['property_type']} in {deal['location']} (Score: {deal['score']})"):
                            st.markdown(f"**Run ID:** {deal['run_id']}")
                            st.markdown(f"**Verdict:** {deal['verdict']}")
                            if deal['price']:
                                st.markdown(f"**Price:** ${deal['price']:,.0f}")

                    st.divider()
                    st.markdown('<div class="navigation-hint">✅ Daily summary complete! Click below to check security & infrastructure.</div>', unsafe_allow_html=True)
                    if st.button("Next: Security & Infra", type="primary", use_container_width=True, key="nav_to_security"):
                        st.session_state.switch_to_tab = 5
                        st.rerun()
                else:
                    st.warning(f"{summary['message']}")
            except Exception as e:
                st.error(f"Error running job: {e}")
                logger.exception("Daily summary job failed")

# TAB: Security & Infra
with tab_security:
    st.header("Security & Infrastructure")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Island Browser Trust")
        st.markdown("""
        Island provides zero-trust browser security with real-time telemetry.
        This shim simulates Island's trust signals.
        """)

        island_signal = {
            "url": "streamlit://localhost:8501",
            "timestamp": datetime.now().isoformat(),
            "session_id": "demo_session",
            "sso_verified": True,
            "dlp_enabled": True,
            "threat_level": "low"
        }

        st.markdown('<div class="status-healthy">Trust Signal Active</div>', unsafe_allow_html=True)
        st.json(island_signal)

    with col2:
        st.subheader("Spectro Cloud Cluster Health")
        st.markdown("""
        Spectro Cloud manages Kubernetes infrastructure.
        In production, this would query the actual cluster status.
        """)

        if st.button("Check Cluster Health"):
            with st.spinner("Checking cluster..."):
                health = get_cluster_health()
                if health["status"] == "healthy":
                    st.markdown('<div class="status-healthy">✅ Cluster Healthy</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-unhealthy">❌ Cluster Unhealthy</div>', unsafe_allow_html=True)
                st.json(health)

                st.divider()
                st.markdown('<div class="navigation-hint">🎉 Demo complete! View deal history or start over.</div>', unsafe_allow_html=True)
                if st.button("View Deal History", type="primary", use_container_width=True, key="nav_to_history"):
                    st.session_state.switch_to_tab = 6
                    st.rerun()

# TAB: History
with tab_history:
    st.header("Recent Deal Runs")

    runs_dir = Path("./runs")

    if runs_dir.exists():
        run_files = sorted(
            [f for f in runs_dir.glob("*.json") if f.name != "evidence_log.jsonl"],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:10]

        if run_files:
            for run_file in run_files:
                try:
                    with open(run_file) as f:
                        run_data = json.load(f)

                    structured = run_data.get("structured_deal", {})
                    score_data = run_data.get("score_data", {})
                    location = structured.get("location", {})
                    city = location.get("city", "Unknown") if isinstance(location, dict) else "Unknown"

                    with st.expander(
                        f"{run_data.get('run_id')} - {structured.get('property_type', 'Unknown')} "
                        f"in {city} - Score: {score_data.get('score', 0)}/100"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Timestamp:** {run_data.get('timestamp')}")
                            st.markdown(f"**Verdict:** {score_data.get('verdict')}")
                            if 'cap_rate' in score_data.get('metrics', {}):
                                st.markdown(f"**Cap Rate:** {score_data['metrics']['cap_rate']:.2f}%")
                        with col2:
                            if 'deal_size' in score_data.get('metrics', {}):
                                st.markdown(f"**Deal Size:** ${score_data['metrics']['deal_size']:,.0f}")
                            if 'local_path' in run_data:
                                st.markdown(f"**File:** {run_data['local_path']}")
                            if 's3_uri' in run_data:
                                st.markdown(f"**S3:** {run_data['s3_uri']}")
                except Exception as e:
                    st.error(f"Error loading {run_file.name}: {e}")
        else:
            st.info("No deal runs found yet")
    else:
        st.info("No runs directory found. Analyze a deal to get started!")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    REVA v1.0 | Powered by AWS Bedrock, Deepgram, Merge
</div>
""", unsafe_allow_html=True)
