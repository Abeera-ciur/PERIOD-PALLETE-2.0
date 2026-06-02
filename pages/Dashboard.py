"""Period Pallete  · Dashboard"""
import streamlit as st
import sys, os
from datetime import date, timedelta
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id, get_profile,
    db_get_cycle_logs, db_get_symptoms,
    get_cycle_phase, compute_cycle_day,
)

st.set_page_config(page_title="Period Pallete  – Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Dashboard")

profile   = get_profile()
_raw_name = profile.get("name", "") or ""
name      = _raw_name if _raw_name and "@" not in _raw_name else "there"
user_id   = get_user_id()
cycle_len = profile.get("cycle_length", 28)

# ── Cycle data from real logs ─────────────────────────────────
cycle_day, last_period_str = compute_cycle_day(user_id, cycle_len)
# Cap display day at cycle_length; overdue shown differently
display_day  = min(cycle_day, cycle_len)
is_overdue   = cycle_day > cycle_len
phase, phase_icon, phase_color = get_cycle_phase(display_day, cycle_len)
days_until   = cycle_len - cycle_day
next_period  = date.today() + timedelta(days=max(0, days_until))

recent_symptoms = db_get_symptoms(user_id, days=7)
sym_names       = list({s["name"] for s in recent_symptoms})[:6]

# ── If no cycle data logged, prompt onboarding ───────────────
if last_period_str == str(date.today()) and cycle_day == 1:
    st.markdown("""
    <div class="hw-card hw-card-gradient" style="text-align:center;padding:40px 24px;max-width:560px;margin:40px auto;">
        <div style="font-size:48px;margin-bottom:12px;">🌙</div>
        <div style="font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:8px;">
            Welcome to Period Pallete 
        </div>
        <div style="font-size:14px;color:var(--ink-60);line-height:1.7;margin-bottom:20px;">
            Let's set up your cycle history so the AI can give you accurate
            phase predictions and personalised advice from day one.
        </div>
    </div>
    """, unsafe_allow_html=True)
    _, c, _ = st.columns([2,3,2])
    with c:
        if st.button("✦ Set up my cycle →", key="goto_onboarding"):
            st.switch_page("pages/Onboarding.py")
    st.stop()

# ── Header ────────────────────────────────────────────────────
hour = date.today().timetuple().tm_hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
st.markdown(f"""
<div class="page-header">
    <h1>{greeting}, {name} ✦</h1>
    <p>Here's your health summary · {date.today().strftime("%B %d, %Y")}</p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
next_period_str = "Overdue" if is_overdue else next_period.strftime("%b %d")
with m1: st.metric(f"{phase_icon} Cycle Day", f"{display_day} / {cycle_len}")
with m2: st.metric("🌿 Phase", phase)
with m3: st.metric("📅 Next Period", next_period_str)
with m4: st.metric("📋 Symptoms (7d)", len(recent_symptoms))

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    # Phase strip
    phases = [
        ("Menstrual",  "#C8627A", "#fff",  1, 5),
        ("Follicular", "#C8D8E8", "#2A5070", 6, 13),
        ("Ovulation",  "#C8E0D8", "#1A5040", 14, 16),
        ("Luteal",     "#D8C8B8", "#5A3A20", 17, cycle_len),
    ]
    strips = ""
    for p_name, bg, fg, ds, de in phases:
        active  = ds <= display_day <= de
        outline = "box-shadow:inset 0 0 0 3px rgba(180,80,100,.5);" if active else ""
        flex    = max(0.5, (de - ds + 1) / cycle_len)
        weight  = "700" if active else "400"
        strips += f"""<div style="flex:{flex};background:{bg};display:flex;align-items:center;
            justify-content:center;color:{fg};font-weight:{weight};font-size:12px;{outline}
            transition:all .3s;">{p_name}</div>"""

    st.markdown(f"""
    <div class="hw-card">
        <div class="hw-card-title">Cycle Overview</div>
        <div style="display:flex;border-radius:var(--radius);overflow:hidden;height:52px;margin-bottom:12px;">
            {strips}
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--ink-30);">
            <span>Day 1</span><span>Day {cycle_len//2}</span><span>Day {cycle_len}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Symptoms
    st.markdown('<div class="hw-card"><div class="hw-card-title">Recent Symptoms (7 days)</div>',
                unsafe_allow_html=True)
    if sym_names:
        tags = "".join(f'<span class="hw-tag hw-tag-rose">{s}</span>' for s in sym_names)
        st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;">{tags}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:var(--ink-60);font-size:13px;padding:4px 0 10px;">No symptoms logged this week. 🌿</div>',
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Log Today's Symptoms", key="dash_log_sym"):
        st.switch_page("pages/Symptom_Tracker.py")

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🌙 Log Period", key="dash_period"):
            st.switch_page("pages/Cycle_Tracker.py")
    with qa2:
        if st.button("💫 Skin Check", key="dash_skin"):
            st.switch_page("pages/Skin_Care.py")
    with qa3:
        if st.button("📝 Add Note", key="dash_note"):
            st.switch_page("pages/Notes.py")

with right_col:
    phase_tips = {
        "Menstrual":  "Rest and restore. Iron-rich foods like leafy greens help replenish energy. Gentle yoga and light walks are ideal right now.",
        "Follicular": "Energy is rising! Great time for new workouts, creative projects, and social activities. Your skin is naturally more radiant.",
        "Ovulation":  "Peak energy and confidence. Leverage this for important meetings, high-intensity workouts, and socialising.",
        "Luteal":     "Wind down gradually. Magnesium-rich foods ease PMS. Prioritise sleep and reduce caffeine in the second half.",
    }
    overdue_tip = "Your period may be late. Stress, diet, and lifestyle can affect timing. If concerned, consult a doctor."

    st.markdown(f"""
    <div class="hw-card hw-card-gradient" style="margin-bottom:16px;">
        <div style="display:flex;align-items:flex-start;gap:12px;">
            <div style="font-size:38px;line-height:1;">{phase_icon}</div>
            <div>
                <div class="hw-card-title" style="margin-bottom:6px;">
                    {"Period may be late" if is_overdue else f"{phase} Phase · Day {display_day}"}
                </div>
                <div style="font-size:13px;color:var(--ink-60);line-height:1.65;">
                    {overdue_tip if is_overdue else phase_tips.get(phase, "")}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask AI about this phase →", key="dash_ai"):
        st.switch_page("pages/AI_ChatBot.py")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Cycle ring
    st.markdown('<div class="hw-card"><div class="hw-card-title">Cycle Progress</div>',
                unsafe_allow_html=True)
    filled = min(display_day, cycle_len)
    empty  = max(0, cycle_len - filled)
    fig = go.Figure(go.Pie(
        values=[filled, empty],
        hole=0.72,
        marker_colors=["#C8627A", "#EAD8E2"],
        textinfo="none", sort=False,
        direction="clockwise",
    ))
    fig.update_layout(
        height=160, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>Day {display_day}</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#1E1420", family="DM Serif Display"),
        )],
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="dash_ring")
    period_label = "Overdue" if is_overdue else next_period.strftime("%B %d")
    st.markdown(f"""
    <div style="text-align:center;font-size:12px;color:var(--ink-60);margin-top:-6px;padding-bottom:4px;">
        Next period: <strong style="color:var(--rose);">{period_label}</strong>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
