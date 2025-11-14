# How to Apply REVA Theme

## Quick Integration (2 minutes)

Add these 3 lines to the top of `app.py`:

```python
from reva_theme import apply_reva_theme, create_score_gauge

# After st.set_page_config(), add:
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

apply_reva_theme(st.session_state.dark_mode)
```

## Add Dark Mode Toggle

In your sidebar or header:

```python
if st.button("🌓 Dark Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
```

## Use Visual Score Gauge

Replace plain score display with:

```python
# Instead of:
st.metric("Score", f"{score}/100")

# Use:
st.markdown(create_score_gauge(score, verdict), unsafe_allow_html=True)
```

## What You Get

✅ Modern research lab aesthetic
✅ Film grain texture overlay
✅ Space Grotesk + Inter + IBM Plex Mono fonts
✅ Dotted/dashed borders everywhere
✅ Gradient verdict cards
✅ Dark mode support
✅ Hidden Streamlit branding
✅ Professional mono labels
✅ Smooth animations

## Full Example

```python
import streamlit as st
from reva_theme import apply_reva_theme, create_score_gauge

st.set_page_config(page_title="REVA", page_icon="⚡", layout="wide")

# Initialize dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Apply theme
apply_reva_theme(st.session_state.dark_mode)

# Header with dark mode toggle
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# ⚡ REVA")
with col2:
    if st.button("🌓 Toggle Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Use score gauge
st.markdown(create_score_gauge(82, "Pass"), unsafe_allow_html=True)

# Your existing code...
```

## Or Use Complete Polished Version

I also created `app_polished.py` with:
- Welcome screen with fake metrics
- Visual score gauges
- Better empty states
- Footer with sponsor credits
- All REVA styling

To use it:
```bash
streamlit run app_polished.py
```

## Customize Colors

Edit `reva_theme.py` to change colors:

```python
# Change these hex values:
"#06D6A0" → Your success color
"#F77F00" → Your warning color
"#EF476F" → Your danger color
"#3A7CFF" → Your primary blue
```

That's it! Your app now looks like a modern research lab interface.
