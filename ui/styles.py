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
    background:
        radial-gradient(circle at 15% 0%, rgba(88,166,255,0.06), transparent 40%),
        radial-gradient(circle at 85% 10%, rgba(63,185,80,0.05), transparent 35%),
        #0d1117;
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
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.metric-card:hover {
    border-color: #58a6ff;
    transform: translateY(-2px);
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.8rem; color: #58a6ff;
    margin: 4px 0 0 0; line-height: 1.1;
}

/* ── Fade-in micro-interaction ─────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.45s ease both;
}

/* ── Start Snowmaking CTA button ──────────────────────────────
   Streamlit renders st.button as a <button> inside
   [data-testid="stButton"]; type="primary" gets a distinct class
   we can target broadly via the wrapper below.                 */
.start-btn-wrap { margin: 0.5rem 0 1.2rem 0; }

.start-btn-wrap [data-testid="stButton"] button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
    color: #ffffff;
    border: 1px solid #58a6ff;
    border-radius: 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.05rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.9rem 1rem;
    box-shadow: 0 4px 18px rgba(31, 111, 235, 0.35);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.start-btn-wrap [data-testid="stButton"] button:hover:enabled {
    transform: translateY(-2px);
    box-shadow: 0 8px 26px rgba(31, 111, 235, 0.5);
    filter: brightness(1.08);
}
.start-btn-wrap [data-testid="stButton"] button:active:enabled {
    transform: translateY(0px);
}
.start-btn-wrap [data-testid="stButton"] button:disabled {
    background: #21262d;
    color: #8b949e;
    border-color: #30363d;
    box-shadow: none;
    opacity: 0.8;
}

/* ── Simulation sequence step text ────────────────────────────*/
.sim-step {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.95rem;
    color: #79c0ff;
    background: #0d1526;
    border: 1px solid #1c2e4a;
    border-radius: 6px;
    padding: 0.85rem 1.1rem;
    margin: 0.6rem 0;
    letter-spacing: 0.03em;
    animation: pulseStep 1.1s ease-in-out infinite;
}
.sim-step-icon { margin-right: 0.5rem; }

@keyframes pulseStep {
    0%, 100% { opacity: 0.75; }
    50%      { opacity: 1; }
}

/* ── Overall status card ──────────────────────────────────────*/
.status-card {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0 1.5rem 0;
    border: 1px solid #30363d;
}
.status-card-icon { font-size: 2.2rem; line-height: 1; }
.status-card-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.15rem;
    letter-spacing: 0.04em;
    margin-bottom: 0.3rem;
}
.status-card-desc {
    font-family: 'Barlow', sans-serif;
    font-size: 0.88rem;
    color: #c9d1d9;
    line-height: 1.4;
}

.status-card-optimal {
    background: linear-gradient(135deg, #0d2b18, #0d4429);
    border-color: #238636;
}
.status-card-optimal .status-card-title { color: #3fb950; }

.status-card-marginal {
    background: linear-gradient(135deg, #241500, #2d1a00);
    border-color: #9e6a03;
}
.status-card-marginal .status-card-title { color: #d29922; }

.status-card-impossible {
    background: linear-gradient(135deg, #240a0a, #2d0d0d);
    border-color: #8b1a1a;
}
.status-card-impossible .status-card-title { color: #f85149; }

/* ── Results dashboard info cards ─────────────────────────────*/
.info-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 1rem;
    min-height: 118px;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.info-card:hover {
    border-color: #58a6ff;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}
.info-card-icon { font-size: 1.4rem; margin-bottom: 0.35rem; }
.info-card-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 0.25rem;
}
.info-card-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.55rem;
    color: #58a6ff;
    line-height: 1.15;
}
.info-card-sub {
    font-family: 'Barlow', sans-serif;
    font-size: 0.76rem;
    color: #8b949e;
    margin-top: 0.3rem;
    line-height: 1.35;
}
</style>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
