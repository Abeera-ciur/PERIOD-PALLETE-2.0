"""Period Pallete  · Insights"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys, os
from collections import Counter
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id,
    db_get_symptoms, db_get_cycle_logs, db_get_skin_logs,
)

st.set_page_config(page_title="Period Pallete  – Insights", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Insights")

user_id = get_user_id()

# ── Load data ─────────────────────────────────────────────────────────────────
symptoms_90  = db_get_symptoms(user_id, days=90)
skin_logs_30 = db_get_skin_logs(user_id, limit=30)
cycle_logs   = db_get_cycle_logs(user_id, days=180)

C = {"rose":"#E8547A","mauve":"#C9A0B8","sage":"#A8C5B5","lav":"#B8A9D4","peach":"#F2C6A0"}

st.markdown("""
<div class="page-header"><h1>Comprehensive Insights 📈</h1>
<p>Your health patterns at a glance</p></div>
""", unsafe_allow_html=True)

# ── Row 1 ─────────────────────────────────────────────────────────────────────
r1a, r1b = st.columns(2, gap="large")

with r1a:
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Top Symptoms (90 days)</div>""",
                unsafe_allow_html=True)
    if symptoms_90:
        counts = Counter(s["name"] for s in symptoms_90)
        top_sym, top_vals = zip(*counts.most_common(6))
        colors = [C["rose"], C["mauve"], C["sage"], C["lav"], C["peach"], C["rose"]]
        fig = go.Figure(go.Bar(
            x=list(top_sym), y=list(top_vals),
            marker_color=colors[:len(top_sym)], width=0.5
        ))
        fig.update_layout(
            height=220, margin=dict(l=0,r=0,t=0,b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#7A6078")),
            yaxis=dict(showgrid=True, gridcolor="#F0E4EA", tickfont=dict(size=10, color="#7A6078"))
        )
        st.plotly_chart(fig, use_container_width=True, key="top_sym_chart")
    else:
        st.markdown("<div style='color:var(--ink-60);font-size:13px;padding:16px 0;'>Log symptoms to see patterns here.</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r1b:
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Mood Distribution (90 days)</div>""",
                unsafe_allow_html=True)
    moods     = [s for s in symptoms_90 if s["category"] == "Mood"]
    if moods:
        mc = Counter(s["name"] for s in moods)
        fig2 = go.Figure(go.Pie(
            labels=list(mc.keys()), values=list(mc.values()), hole=0.4,
            marker_colors=[C["rose"], C["sage"], C["mauve"], C["lav"], C["peach"]],
            textinfo="label+percent", textfont=dict(size=11)
        ))
        fig2.update_layout(
            height=220, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True, key="mood_pie")
    else:
        st.markdown("<div style='color:var(--ink-60);font-size:13px;padding:16px 0;'>Log moods to see your distribution.</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────
r2a, r2b = st.columns(2, gap="large")

with r2a:
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Skin Score Trend</div>""",
                unsafe_allow_html=True)
    if skin_logs_30:
        sl_dates  = [l["log_date"] for l in reversed(skin_logs_30)]
        sl_scores = [l["rating"] for l in reversed(skin_logs_30)]
        fig3 = go.Figure(go.Scatter(
            x=sl_dates, y=sl_scores,
            mode="lines+markers",
            line=dict(color=C["rose"], width=2, shape="spline"),
            marker=dict(size=6, color=C["rose"]),
            fill="tozeroy", fillcolor="rgba(232,84,122,0.08)"
        ))
        fig3.update_layout(
            height=200, margin=dict(l=0,r=0,t=0,b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#7A6078"), tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="#F0E4EA", tickfont=dict(size=9), range=[0,10])
        )
        st.plotly_chart(fig3, use_container_width=True, key="skin_trend")
    else:
        st.markdown("<div style='color:var(--ink-60);font-size:13px;padding:16px 0;'>Log your skin to track progress.</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2b:
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Symptom Category Breakdown</div>""",
                unsafe_allow_html=True)
    if symptoms_90:
        cat_counts = Counter(s["category"] for s in symptoms_90)
        fig4 = go.Figure(go.Bar(
            x=list(cat_counts.keys()), y=list(cat_counts.values()),
            marker_color=[C["rose"], C["peach"], C["lav"]][:len(cat_counts)],
            width=0.45, text=list(cat_counts.values()), textposition="outside"
        ))
        fig4.update_layout(
            height=200, margin=dict(l=0,r=0,t=20,b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#7A6078")),
            yaxis=dict(showgrid=True, gridcolor="#F0E4EA", tickfont=dict(size=10))
        )
        st.plotly_chart(fig4, use_container_width=True, key="cat_breakdown")
    else:
        st.markdown("<div style='color:var(--ink-60);font-size:13px;padding:16px 0;'>No data yet.</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── AI Insights ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hw-card" style="background:linear-gradient(135deg,var(--rose-bg),#fff);">
    <div class="hw-card-title">AI Insights Summary</div>
    <div style="font-size:13px;color:var(--ink-60);line-height:1.7;margin-bottom:14px;">
        Based on your logged data, patterns are starting to emerge. The more you log,
        the more personalised your insights become! Keep tracking to unlock deeper connections
        between your cycle, mood, skin, and symptoms.
    </div>
""", unsafe_allow_html=True)
if symptoms_90:
    top3 = Counter(s["name"] for s in symptoms_90).most_common(3)
    for sym, cnt in top3:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ink-60);margin-bottom:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:var(--rose);flex-shrink:0;display:inline-block;"></span>
            <span><strong style="color:var(--ink);">{sym}</strong> logged {cnt}× in the last 90 days</span>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
if st.button("Ask AI for personalised insights →", key="ai_insights"):
    st.switch_page("pages/AI_ChatBot.py")

render_footer()
