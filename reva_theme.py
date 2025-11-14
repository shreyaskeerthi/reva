"""
REVA Theme - Modern Research Lab Interface
Import and call apply_reva_theme() in your app.py
"""
import streamlit as st

def apply_reva_theme(dark_mode=False):
    """Apply REVA modern research lab theme with optional dark mode"""

    dark_bg = '#0B1020' if dark_mode else '#F6F8FF'
    dark_text = '#F6F8FF' if dark_mode else '#0B1020'
    card_bg = 'rgba(246, 248, 255, 0.05)' if dark_mode else 'white'
    grain_opacity = '0.015' if dark_mode else '0.025'

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">

    <style>
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display: none;}}

        /* Base styling - REVA colors */
        .stApp {{
            background: {dark_bg};
            color: {dark_text};
            font-family: 'Inter', sans-serif;
            font-weight: 400;
        }}

        /* Film grain overlay */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
            opacity: {grain_opacity};
            z-index: 9999;
        }}

        /* Typography */
        h1, h2, h3, .font-display {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}

        code, .mono {{
            font-family: 'IBM Plex Mono', monospace;
        }}

        /* Verdict cards with gradient + dashed borders */
        .verdict-pass {{
            background: linear-gradient(135deg, #06D6A0 0%, #00A896 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 2px dashed rgba(255,255,255,0.3);
        }}

        .verdict-watch {{
            background: linear-gradient(135deg, #F77F00 0%, #FF9E00 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 2px dashed rgba(255,255,255,0.3);
        }}

        .verdict-hard-pass {{
            background: linear-gradient(135deg, #EF476F 0%, #D90429 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 2px dashed rgba(255,255,255,0.3);
        }}

        /* Status indicators - mono font */
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

        /* Navigation hints with dashed bottom border */
        .navigation-hint {{
            background: {'rgba(58, 124, 255, 0.1)' if dark_mode else 'rgba(230, 239, 255, 1)'};
            border-left: 4px solid #3A7CFF;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            border-bottom: 1px dashed #78A7FF;
        }}

        /* Metric cards */
        .metric-card {{
            background: {card_bg};
            padding: 20px;
            border-radius: 8px;
            border: 1px solid {'rgba(120, 167, 255, 0.2)' if dark_mode else 'rgba(11, 32, 32, 0.06)'};
            box-shadow: 0 1px 2px rgba(0,0,0,{'0.1' if dark_mode else '0.04'});
            margin: 10px 0;
        }}

        /* Links with dotted underline */
        a {{
            color: #00A3FF;
            text-decoration: underline;
            text-decoration-style: dotted;
            text-underline-offset: 4px;
            transition: all 0.2s;
        }}

        a:hover {{
            text-decoration-style: solid;
            color: #3A7CFF;
        }}

        /* Buttons */
        .stButton>button {{
            border-radius: 6px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.02em;
            transition: all 0.3s;
            border: 1px solid {'rgba(120, 167, 255, 0.3)' if dark_mode else 'rgba(11, 32, 32, 0.1)'};
        }}

        .stButton>button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(58, 124, 255, 0.2);
        }}

        /* Sidebar with dashed border */
        [data-testid="stSidebar"] {{
            background: {'#0F1419' if dark_mode else '#FAFBFF'};
            border-right: 1px dashed #78A7FF;
        }}

        /* Section dividers - dashed */
        hr {{
            border: none;
            border-top: 1px dashed #78A7FF;
            margin: 24px 0;
        }}

        /* Code blocks */
        code {{
            background: {'rgba(120, 167, 255, 0.1)' if dark_mode else 'rgba(230, 239, 255, 0.5)'};
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.9em;
            border: 1px solid #78A7FF;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 2px dashed #78A7FF;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 12px 20px;
            border-radius: 6px 6px 0 0;
        }}

        /* Expanders with dotted borders */
        .streamlit-expanderHeader {{
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            border-bottom: 1px dotted #78A7FF;
        }}

        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div {{
            border: 1px solid #78A7FF;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
        }}

        /* Utility classes */
        .u-dotted {{
            border-top: 1px dotted #78A7FF;
            padding-top: 16px;
            margin-top: 16px;
        }}

        .sheet {{
            max-width: 1040px;
            margin: 0 auto;
            padding: 24px;
        }}

        /* Score gauge visualization */
        .score-gauge {{
            position: relative;
            width: 200px;
            height: 200px;
            margin: 20px auto;
        }}

        .score-gauge svg {{
            transform: rotate(-90deg);
        }}

        .score-gauge .score-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .score-gauge .score-number {{
            font-size: 3em;
            font-weight: 800;
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
        }}

        .score-gauge .score-label {{
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-family: 'IBM Plex Mono', monospace;
            margin: 0;
            color: #78A7FF;
        }}

        /* Typewriter animation */
        @keyframes typewriter-flicker {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.9; }}
        }}

        .typewriter {{
            animation: typewriter-flicker 0.8s infinite;
        }}
    </style>
    """, unsafe_allow_html=True)


def create_score_gauge(score, verdict):
    """Create a visual circular score gauge"""
    color_map = {
        "Pass": "#06D6A0",
        "Watch": "#F77F00",
        "Hard Pass": "#EF476F"
    }
    color = color_map.get(verdict, "#78A7FF")
    circumference = 2 * 3.14159 * 90
    dash_offset = circumference - (score / 100 * circumference)

    return f"""
    <div class="score-gauge">
        <svg viewBox="0 0 200 200" width="200" height="200">
            <!-- Background circle -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="#E6EFFF" stroke-width="20"/>
            <!-- Progress circle -->
            <circle cx="100" cy="100" r="90" fill="none"
                    stroke="{color}" stroke-width="20"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    stroke-linecap="round"/>
        </svg>
        <div class="score-text">
            <h1 class="score-number">{score}</h1>
            <p class="score-label">{verdict}</p>
        </div>
    </div>
    """
