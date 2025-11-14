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
    get_cluster_health
)
from cre_agent.examples import get_all_examples

# Page config
st.set_page_config(
    page_title="REVA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* REVA Purple Theme */
    .reva-title {
        color: #9333ea !important;
        font-weight: bold;
        font-size: 2.5rem;
    }
    .reva-subtitle {
        color: #a855f7 !important;
    }
    .verdict-pass { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; font-weight: bold; }
    .verdict-watch { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-weight: bold; }
    .verdict-hard-pass { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; font-weight: bold; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .status-healthy { color: #28a745; font-weight: bold; }
    .status-unhealthy { color: #dc3545; font-weight: bold; }
    .navigation-hint {
        background-color: #1a1a1a;
        color: #ffffff;
        border-left: 4px solid #2196F3;
        padding: 12px;
        margin: 15px 0;
        border-radius: 4px;
        font-size: 14px;
    }
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

# Main title
st.markdown('<h1 class="reva-title">⚡ REVA</h1>', unsafe_allow_html=True)
st.markdown('<p class="reva-subtitle"><em>Powered by AWS Bedrock, Deepgram, Merge</em></p>', unsafe_allow_html=True)

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

# st.sidebar.divider()
# st.sidebar.markdown(f"**Demo Mode:** {'✅ ON' if st.session_state.settings.demo_mode else '❌ OFF'}")
# st.sidebar.markdown(f"**AWS Bedrock:** {'✅' if st.session_state.settings.has_aws_config else '❌'}")
# st.sidebar.markdown(f"**S3 Storage:** {'✅' if st.session_state.settings.has_s3_config else '❌'}")
# st.sidebar.markdown(f"**Deepgram:** {'✅' if st.session_state.settings.has_deepgram_config else '❌'}")
# st.sidebar.markdown(f"**Merge CRM:** {'✅' if st.session_state.settings.has_merge_config else '❌'}")

# Check for tab navigation via query params
query_params = st.query_params
if "tab" in query_params:
    try:
        tab_index = int(query_params["tab"])
        st.session_state.switch_to_tab = tab_index
        # Clear the query param after reading it
        st.query_params.clear()
    except:
        pass

# Main content area - Use a selectbox for tab navigation to allow programmatic control
tab_names = ["Input", "Analyze", "CRM", "Evidence", "Jobs", "Security & Infra", "History"]

# Create tabs
tab_input, tab_analyze, tab_crm, tab_evidence, tab_jobs, tab_security, tab_history = st.tabs(tab_names)

# Handle programmatic tab switching via JavaScript
if st.session_state.switch_to_tab is not None:
    tab_index = st.session_state.switch_to_tab
    st.session_state.switch_to_tab = None  # Reset after use
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            // Try multiple selectors to find tab buttons
            var tabButtons = document.querySelectorAll('[data-testid="stTabs"] button, button[role="tab"], [data-baseweb="tab"]');
            if (tabButtons.length === 0) {{
                // Fallback: find buttons within tab container
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

        if uploaded_file:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.audio(uploaded_file)

            with col2:
                if st.button("🎤 Transcribe with Deepgram", use_container_width=True):
                    with st.spinner("Transcribing..."):
                        deepgram_client = DeepgramClient(
                            api_key=st.session_state.settings.deepgram_api_key,
                            demo_mode=st.session_state.settings.demo_mode
                        )

                        audio_bytes = uploaded_file.read()
                        transcript = deepgram_client.transcribe_bytes(
                            audio_bytes,
                            filename=uploaded_file.name
                        )

                        st.session_state.deal_text = transcript
                        st.success("Transcription complete!")

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
            # Track previous text to detect new paste
            if 'previous_paste_text' not in st.session_state:
                st.session_state.previous_paste_text = ""
            
            # Check if this is a new paste
            is_new_paste = st.session_state.deal_text != st.session_state.previous_paste_text
            
            if is_new_paste:
                # Show progress with spinner
                with st.spinner("📋 Processing pasted text..."):
                    # Show progress bar
                    progress_bar = st.progress(0)
                    status_text = st.caption("Processing...")
                    
                    # Animate progress
                    for i in range(0, 101, 20):
                        progress_bar.progress(i / 100)
                        if i < 100:
                            status_text.caption(f"📋 Processing text... {i}%")
                        time.sleep(0.1)
                    
                    # Complete
                    progress_bar.progress(1.0)
                    status_text.caption("Complete!")
                    time.sleep(0.2)
                
                # Show success message
                st.success("Text loaded successfully!")
                
                # Update previous text
                st.session_state.previous_paste_text = st.session_state.deal_text
            else:
                # Text already processed, just show success
                st.success("Text loaded successfully!")
        else:
            # Reset tracking when text is cleared
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

    # Navigation button
    if st.session_state.deal_text:
        st.divider()
        st.markdown('<div class="navigation-hint">✅ Deal text loaded! Click below to move to the next step.</div>', unsafe_allow_html=True)
        # if st.button("➡️ Next: Analyze Deal", type="primary", use_container_width=True, key="nav_to_analyze"):
        #     st.session_state.switch_to_tab = 1  # Index 1 = Analyze tab
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

            # Verdict banner
            verdict = score_data.get("verdict", "Unknown")
            verdict_class = f"verdict-{verdict.lower().replace(' ', '-')}"

            st.markdown(f'<div class="{verdict_class}">Verdict: {verdict} (Score: {score_data.get("score", 0)}/100)</div>', unsafe_allow_html=True)

            # Key metrics
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                cap_rate = metrics.get("cap_rate") or structured.get("cap_rate")
                if cap_rate:
                    st.metric("Cap Rate", f"{cap_rate:.2f}%")
                else:
                    st.metric("Cap Rate", "N/A")

            with col2:
                deal_size = metrics.get("deal_size")
                if deal_size:
                    st.metric("Deal Size", f"${deal_size:,.0f}")
                else:
                    st.metric("Deal Size", "N/A")

            with col3:
                ppu = metrics.get("price_per_unit")
                if ppu:
                    st.metric("Price/Unit", f"${ppu:,.0f}")
                else:
                    st.metric("Price/Unit", "N/A")

            with col4:
                ppsf = metrics.get("price_per_sf")
                if ppsf:
                    st.metric("Price/SF", f"${ppsf:.2f}")
                else:
                    st.metric("Price/SF", "N/A")

            # Scoring reasons
            st.subheader("Scoring Breakdown")
            reasons = score_data.get("reasons", [])
            for reason in reasons:
                if "✓" in reason:
                    st.markdown(f"✅ {reason}")
                else:
                    st.markdown(f"⚠️ {reason}")

            # Structured data
            st.subheader("Structured Deal Data")
            st.json(structured)

            # IC Summary
            st.subheader("Investment Committee Summary")
            ic_summary = run.get("ic_summary", "")
            st.markdown(ic_summary)

            if st.button("📋 Send IC Summary to Slack"):
                st.code(ic_summary, language=None)
                st.info("Copy the text above to your clipboard")

            # Navigation button
            st.divider()
            st.markdown('<div class="navigation-hint">✅ Deal analyzed! Click below to create CRM records.</div>', unsafe_allow_html=True)
            if st.button("Next: Create CRM Records", type="primary", use_container_width=True, key="nav_to_crm"):
                st.session_state.switch_to_tab = 2  # Index 2 = CRM tab
                st.rerun()

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

        if st.button("📞 Create CRM Records via Merge", type="primary", use_container_width=True):
            with st.spinner("Creating CRM records..."):
                try:
                    merge_client = MergeClient(
                        api_key=st.session_state.settings.merge_api_key,
                        account_token=st.session_state.settings.merge_account_token,
                        base_url=st.session_state.settings.merge_base_url,
                        demo_mode=st.session_state.settings.demo_mode or not st.session_state.settings.has_merge_config
                    )

                    # Create contact
                    contact_id = merge_client.upsert_contact(
                        email=broker_email if broker_email else None,
                        name=broker_name if broker_name else None,
                        company=broker_company if broker_company else None
                    )

                    # Create note
                    note_content = f"Deal Analysis - {structured.get('property_type', 'Property')} in {deal_location}\n\n"
                    note_content += f"Score: {run['score_data']['score']}/100 ({run['score_data']['verdict']})\n"
                    note_content += f"Cap Rate: {run['score_data']['metrics'].get('cap_rate', 'N/A')}\n"
                    note_content += f"Price: ${run['score_data']['metrics'].get('deal_size', 0):,.0f}\n"
                    note_content += f"\nRun ID: {run['run_id']}"

                    note_id = merge_client.create_note(contact_id, note_content)

                    # Create task
                    task_title = f"Follow up on {structured.get('property_type', 'deal')} in {deal_location}"
                    task_id = merge_client.create_task(contact_id, task_title)

                    # Store in run payload
                    st.session_state.last_run["crm_records"] = {
                        "contact_id": contact_id,
                        "note_id": note_id,
                        "task_id": task_id,
                        "created_at": datetime.now().isoformat()
                    }

                    st.success("✅ CRM records created successfully!")

                    st.info(f"**Contact ID:** {contact_id}")
                    st.info(f"**Note ID:** {note_id}")
                    st.info(f"**Task ID:** {task_id}")

                except Exception as e:
                    st.error(f"Error creating CRM records: {e}")
                    logger.exception("CRM creation failed")

        # Show existing CRM records if any
        if "crm_records" in st.session_state.last_run:
            st.subheader("Created CRM Records")
            st.json(st.session_state.last_run["crm_records"])

            # Navigation button
            st.divider()
            st.markdown('<div class="navigation-hint">✅ CRM records created! Click below to generate evidence packets.</div>', unsafe_allow_html=True)
            if st.button("Next: Generate Evidence", type="primary", use_container_width=True, key="nav_to_evidence"):
                st.session_state.switch_to_tab = 3  # Index 3 = Evidence tab
                st.rerun()

# TAB: Evidence
with tab_evidence:
    st.header("Evidence & Compliance")

    if not st.session_state.last_run:
        st.info("Please analyze a deal first")
    else:
        st.markdown("Generate compliance evidence packets for Vanta and Thoropass")

        if st.button("📋 Generate & Send Evidence Packet", use_container_width=True):
            with st.spinner("Generating evidence packet..."):
                try:
                    evidence = build_evidence_packet(st.session_state.last_run)

                    st.subheader("Evidence Packet")
                    st.json(evidence)

                    # Send to Vanta
                    vanta_ack = send_to_vanta(evidence)
                    st.success(f"✅ Sent to Vanta: {vanta_ack['evidence_id']}")

                    # Send to Thoropass
                    thoropass_ack = send_to_thoropass(evidence)
                    st.success(f"✅ Sent to Thoropass: {thoropass_ack['evidence_id']}")

                    # Show acknowledgments
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Vanta ACK")
                        st.json(vanta_ack)

                    with col2:
                        st.subheader("Thoropass ACK")
                        st.json(thoropass_ack)

                    st.info("Evidence logged to: ./runs/evidence_log.jsonl")

                    # Navigation button
                    st.divider()
                    st.markdown('<div class="navigation-hint">✅ Evidence packets sent! Click below to run daily summary job.</div>', unsafe_allow_html=True)
                    if st.button("Next: Run Daily Summary Job", type="primary", use_container_width=True, key="nav_to_jobs"):
                        st.session_state.switch_to_tab = 4  # Index 4 = Jobs tab
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

                    # Show metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Deals", summary["deal_count"])

                    with col2:
                        st.metric("Avg Score", f"{summary['avg_score']}/100")

                    with col3:
                        st.metric("Pass", summary["verdicts"]["pass"])

                    with col4:
                        st.metric("Watch", summary["verdicts"]["watch"])

                    # Top deals
                    st.subheader("Top 3 Deals by Score")

                    for i, deal in enumerate(summary["top_deals"], 1):
                        with st.expander(f"#{i} - {deal['property_type']} in {deal['location']} (Score: {deal['score']})"):
                            st.markdown(f"**Run ID:** {deal['run_id']}")
                            st.markdown(f"**Verdict:** {deal['verdict']}")
                            if deal['price']:
                                st.markdown(f"**Price:** ${deal['price']:,.0f}")

                    # Navigation button
                    st.divider()
                    st.markdown('<div class="navigation-hint">✅ Daily summary complete! Click below to check security & infrastructure.</div>', unsafe_allow_html=True)
                    if st.button("Next: Security & Infra", type="primary", use_container_width=True, key="nav_to_security"):
                        st.session_state.switch_to_tab = 5  # Index 5 = Security & Infra tab
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
        st.subheader("🏝️ Island Browser Trust")

        st.markdown("""
        Island provides zero-trust browser security with real-time telemetry.
        This shim simulates Island's trust signals.
        """)

        # Simulate receiving Island signal
        island_signal = {
            "url": "streamlit://localhost:8501",
            "timestamp": datetime.now().isoformat(),
            "session_id": "demo_session",
            "sso_verified": True,
            "dlp_enabled": True,
            "threat_level": "low"
        }

        st.markdown('<div class="status-healthy">✅ Trust Signal Active</div>', unsafe_allow_html=True)
        st.json(island_signal)

    with col2:
        st.subheader("☁️ Spectro Cloud Cluster Health")

        st.markdown("""
        Spectro Cloud manages Kubernetes infrastructure.
        In production, this would query the actual cluster status.
        """)

        if st.button("🔄 Check Cluster Health"):
            with st.spinner("Checking cluster..."):
                health = get_cluster_health()

                if health["status"] == "healthy":
                    st.markdown('<div class="status-healthy">✅ Cluster Healthy</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-unhealthy">❌ Cluster Unhealthy</div>', unsafe_allow_html=True)

                st.json(health)

                # Navigation button
                st.divider()
                st.markdown('<div class="navigation-hint">🎉 Demo complete! View deal history or start over.</div>', unsafe_allow_html=True)
                if st.button("View Deal History", type="primary", use_container_width=True, key="nav_to_history"):
                    st.session_state.switch_to_tab = 6  # Index 6 = History tab
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


# Island signal endpoint (if using Streamlit's experimental features)
# Note: Streamlit doesn't support custom routes directly, but this shows the structure
# In production, you'd use a Flask/FastAPI backend alongside Streamlit

def handle_island_signal():
    """Handler for Island trust signals (conceptual - would need custom server)"""
    # This would be implemented as a separate endpoint
    # For demo purposes, we're simulating the telemetry loop
    pass
