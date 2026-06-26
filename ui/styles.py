"""
ui/styles.py
Injects the global CSS for the Snow Maker Simulator.
Call inject() once at the top of app.py.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

h1, h2, h3 {
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.05em;
}

[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 1rem 1.2rem;
}

[data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #58a6ff !important;
}

[data-testid="stMetricLabel"] {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #58a6ff;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.status-optimal {
    background: #0d4429; border: 1px solid #238636; color: #3fb950;
    padding: 0.4rem 1rem; border-radius: 4px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; display: inline-block;
}
.status-marginal {
    background: #2d1a00; border: 1px solid #9e6a03; color: #d29922;
    padding: 0.4rem 1rem; border-radius: 4px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; display: inline-block;
}
.status-impossible {
    background: #2d0d0d; border: 1px solid #8b1a1a; color: #f85149;
    padding: 0.4rem 1rem; border-radius: 4px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; display: inline-block;
}

hr { border-color: #21262d !important; }

[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
}

.grade-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.5rem; font-weight: bold; line-height: 1;
}
.grade-A    { color: #3fb950; }
.grade-B    { color: #d29922; }
.grade-C    { color: #f0883e; }
.grade-none { color: #8b949e; }

.mono {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem; color: #8b949e;
}

/* ── Tooltip system ─────────────────────────────────────────── */
.info-wrap {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 0.6rem;
}

.info-icon {
    position: relative;
    display: inline-flex;
    align-items: center;
    cursor: help;
}

.info-icon svg {
    width: 14px; height: 14px;
    fill: #30363d; stroke: #58a6ff; stroke-width: 1.5;
    transition: fill 0.15s; flex-shrink: 0;
}

.info-icon:hover svg { fill: #1c2e4a; }

.info-bubble {
    display: none;
    position: absolute;
    left: 20px; top: 50%; transform: translateY(-50%);
    z-index: 9999; width: 260px;
    background: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 10px 13px;
    font-family: 'Barlow', sans-serif; font-size: 0.78rem; line-height: 1.5;
    color: #c9d1d9; text-transform: none; letter-spacing: 0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5); pointer-events: none;
}

.info-bubble strong {
    display: block;
    font-size: 0.72rem; font-family: 'Share Tech Mono', monospace;
    color: #58a6ff; letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 5px;
}

.info-icon:hover .info-bubble { display: block; }

/* ── Metric card ────────────────────────────────────────────── */
.metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 6px; padding: 1rem 1.2rem;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.8rem; color: #58a6ff;
    margin: 4px 0 0 0; line-height: 1.1;
}
</style>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
