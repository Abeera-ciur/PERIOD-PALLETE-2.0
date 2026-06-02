"""Period Pallete  · Cycle Tracker"""
import streamlit as st
import plotly.graph_objects as go
import calendar
from datetime import date, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id, get_profile,
    db_log_cycle, db_get_cycle_logs, get_cycle_phase, compute_cycle_day,
)

st.set_page_config(page_title="Period Pallete  – Cycle Tracker", page_icon="🌙", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Cycle Tracker")

user_id   = get_user_id()
profile   = get_profile()
cycle_len = profile.get("cycle_length", 28)

# ── Load cycle data ───────────────────────────────────────────────────────────
cycle_logs   = db_get_cycle_logs(user_id, days=180)
period_dates = {l["log_date"] for l in cycle_logs if l["type"] == "period"}

today = date.today()
cycle_day, last_period_str = compute_cycle_day(user_id, cycle_len)
last_period  = date.fromisoformat(last_period_str)
display_day  = min(cycle_day, cycle_len)
is_overdue   = cycle_day > cycle_len
phase, phase_icon, _ = get_cycle_phase(display_day, cycle_len)
next_period  = last_period + timedelta(days=cycle_len)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header"><h1>Your Cycle 🌙</h1>
<p>Understanding your body's rhythm</p></div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

# ════════════════ LEFT ════════════════
with left_col:
    # Phase timeline
    phases_data = [
        ("Menstrual",  "#E8547A", "#fff",    1,   5),
        ("Follicular", "#DDD0F4", "#5A3D8A", 6,  13),
        ("Ovulation",  "#B8D8C8", "#2D6B4A", 14, 16),
        ("Luteal",     "#A8C8B0", "#1D5A3A", 17, cycle_len),
    ]
    strips = ""
    for p_name, bg, fg, ds, de in phases_data:
        active = ds <= cycle_day <= de
        w = (de - ds + 1) / cycle_len
        outline = "outline:3px solid rgba(232,84,122,.5);outline-offset:-3px;" if active else ""
        strips += f"""<div style="flex:{w};background:{bg};display:flex;align-items:center;
                     justify-content:center;color:{fg};font-size:12px;
                     font-weight:{'700' if active else '500'};{outline}">{p_name}</div>"""

    st.markdown(f"""
    <div class="hw-card">
        <div class="hw-card-title">Cycle Phases</div>
        <div style="display:flex;border-radius:var(--radius);overflow:hidden;height:52px;margin-bottom:10px;">
            {strips}
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--ink-30);">
            <span>Day 1</span><span>Day 14</span><span>Day {cycle_len}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calendar
    year, month = today.year, today.month
    cal = calendar.monthcalendar(year, month)
    ovulation_day = cycle_day + (14 - cycle_day) if cycle_day < 14 else 14

    # Calculate which calendar days are period days
    period_cal_days = set()
    for pd_str in period_dates:
        pd = date.fromisoformat(pd_str)
        if pd.year == year and pd.month == month:
            period_cal_days.add(pd.day)

    days_html = "<div style='display:grid;grid-template-columns:repeat(7,1fr);gap:3px;margin-bottom:6px;'>"
    for d in ["S","M","T","W","T","F","S"]:
        days_html += f"<div style='text-align:center;font-size:11px;font-weight:600;color:var(--ink-60);padding:4px 0;'>{d}</div>"
    days_html += "</div><div style='display:grid;grid-template-columns:repeat(7,1fr);gap:3px;'>"

    for week in cal:
        for day in week:
            if day == 0:
                days_html += "<div></div>"
            else:
                is_today   = (day == today.day)
                is_period  = day in period_cal_days
                is_ov      = (day == ovulation_day)
                if is_period:
                    bg,fg = "#E8547A","white"
                elif is_today:
                    bg,fg = "var(--rose-bg)","var(--rose)"
                elif is_ov:
                    bg,fg = "#E8E4F4","#6B58B8"
                else:
                    bg,fg = "transparent","var(--ink)"
                border = "border:2px solid var(--rose);" if is_today and not is_period else ""
                dot = "<div style='width:4px;height:4px;border-radius:50%;background:#6B58B8;margin:1px auto 0;'></div>" if is_ov else ""
                days_html += f"""<div style="text-align:center;padding:5px 2px;border-radius:8px;
                    background:{bg};{border}cursor:pointer;">
                    <span style="font-size:12px;font-weight:{'600' if is_period or is_today else '400'};
                    color:{fg};">{day}</span>{dot}
                </div>"""
    days_html += "</div>"

    st.markdown(f"""
    <div class="hw-card">
        <div class="hw-card-title">{today.strftime("%B %Y")}</div>
        {days_html}
        <div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink-60);">
                <div style="width:10px;height:10px;border-radius:50%;background:#E8547A;"></div>Period
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink-60);">
                <div style="width:10px;height:10px;border-radius:50%;background:#6B58B8;"></div>Ovulation
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink-60);">
                <div style="width:10px;height:10px;border-radius:50%;background:var(--rose-bg);border:2px solid var(--rose);"></div>Today
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════ RIGHT ════════════════
with right_col:
    days_until = (next_period - today).days
    st.markdown(f"""
    <div class="hw-card" style="margin-bottom:16px;">
        <div class="hw-card-title">Next Period</div>
        <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:6px;">
            <div style="font-family:'DM Serif Display',serif;font-size:44px;color:var(--ink);line-height:1;">
                {days_until}
            </div>
            <div style="font-size:14px;color:var(--ink-60);">days away</div>
        </div>
        <div style="font-size:13px;color:var(--ink-60);">
            Expected: <strong style="color:var(--ink);">{next_period.strftime('%B %d, %Y')}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🩸 Log Period Start", key="log_period"):
            ok = db_log_cycle(user_id, {"log_date": str(today), "type": "period"})
            if ok:
                st.success("Period logged! ✅")
                st.rerun()
    with b2:
        if st.button("✨ Log Symptoms", key="log_sym_ct"):
            st.switch_page("pages/Symptom_Tracker.py")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # AI coach
    phase_tips = {
        "Follicular": "Energy is rising! Great time for new workouts and creative projects.",
        "Ovulation":  "Peak energy and confidence — leverage this for important tasks.",
        "Luteal":     "Wind down and prioritise rest. Magnesium-rich foods will help.",
        "Menstrual":  "Rest and restore. Gentle movement and iron-rich foods are key.",
    }
    st.markdown(f"""
    <div class="hw-card" style="background:linear-gradient(135deg,var(--rose-bg),#fff);margin-bottom:16px;">
        <div class="hw-card-title">AI Cycle Coach</div>
        <div style="font-size:13px;color:var(--ink-60);line-height:1.6;margin-bottom:10px;">
            {phase_icon} You're in your <strong style="color:var(--ink);">{phase} phase</strong> — Day {cycle_day}.
            {phase_tips.get(phase, '')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask AI Anything →", key="ai_cycle"):
        st.switch_page("pages/AI_ChatBot.py")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Log a specific date
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Log a Specific Date</div>""",
                unsafe_allow_html=True)
    log_date = st.date_input("Date", value=today, key="cycle_log_date")
    log_type = st.selectbox("Type", ["period", "ovulation", "spotting"], key="cycle_log_type")
    log_notes = st.text_input("Notes (optional)", key="cycle_log_notes")
    if st.button("Save Log", key="save_cycle_log"):
        db_log_cycle(user_id, {
            "log_date": str(log_date),
            "type": log_type,
            "notes": log_notes or None,
        })
        st.success("Saved!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
