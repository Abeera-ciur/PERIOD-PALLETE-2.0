"""Period Pallete  · Symptom Tracker"""
import streamlit as st
from datetime import datetime, date
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id,
    db_log_symptom, db_get_symptoms,
)

st.set_page_config(page_title="Period Pallete  – Symptoms", page_icon="✨", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Symptoms")

user_id = get_user_id()

# ── State ─────────────────────────────────────────────────────────────────────
if "selected_symptoms" not in st.session_state:
    st.session_state.selected_symptoms = set()
if "daily_logs" not in st.session_state:
    st.session_state.daily_logs = []

st.markdown("""
<div class="page-header"><h1>Log &amp; Track Symptoms ✨</h1>
<p>Personalised insights based on your cycle</p></div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

# ════════════════ LEFT ════════════════
with left_col:

    def symptom_grid(title: str, items: list, icons: dict, category: str):
        st.markdown(f"""
        <div style="font-family:'DM Serif Display',serif;font-size:18px;color:var(--ink);margin:0 0 10px;">{title}</div>
        """, unsafe_allow_html=True)
        cols = st.columns(4)
        for i, item in enumerate(items):
            with cols[i % 4]:
                is_sel  = item in st.session_state.selected_symptoms
                border  = "border:2px solid var(--rose);" if is_sel else "border:1px solid var(--border);"
                check   = "✓" if is_sel else "+"
                icon    = icons.get(item, "✨")
                st.markdown(f"""
                <div style="background:var(--surface);{border}border-radius:var(--radius);
                    padding:12px 6px;text-align:center;margin-bottom:4px;">
                    <div style="font-size:24px;margin-bottom:4px;">{icon}</div>
                    <div style="font-size:11px;font-weight:500;color:var(--ink);line-height:1.3;">{item}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(check, key=f"sym_{category}_{item}", use_container_width=True):
                    if item in st.session_state.selected_symptoms:
                        st.session_state.selected_symptoms.discard(item)
                    else:
                        st.session_state.selected_symptoms.add(item)
                        entry = {"time": datetime.now().strftime("%H:%M"),
                                 "category": category, "name": item}
                        st.session_state.daily_logs.append(entry)
                        db_log_symptom(user_id, {
                            "log_date": str(date.today()),
                            "log_time": entry["time"],
                            "category": category,
                            "name":     item,
                        })
                    st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)

    symptom_grid("Common Symptoms", [
        "Headache","Bloating","Mood Swings","Cramps",
        "Acne","Low Energy","Insomnia","Back Pain"
    ], {
        "Headache":"🤕","Bloating":"🎈","Mood Swings":"🌊","Cramps":"⚡",
        "Acne":"💧","Low Energy":"🔋","Insomnia":"😴","Back Pain":"🔙"
    }, "Symptoms")

    symptom_grid("Sickness", [
        "Cold","Flu","Fever","Stomach Bug",
        "Infection","Allergies","Injury","Digestive Issues"
    ], {
        "Cold":"🤧","Flu":"🦠","Fever":"🌡️","Stomach Bug":"🤢",
        "Infection":"🩹","Allergies":"🌼","Injury":"🩼","Digestive Issues":"🫃"
    }, "Sickness")

    # Mood
    st.markdown("""
    <div style="font-family:'DM Serif Display',serif;font-size:18px;color:var(--ink);margin:0 0 10px;">Mood &amp; Energy</div>
    """, unsafe_allow_html=True)
    moods = [("😊","Happy"),("😐","Neutral"),("😔","Sad"),("😡","Irritable"),("😰","Anxious")]
    mood_cols = st.columns(5)
    for col, (icon, label) in zip(mood_cols, moods):
        with col:
            is_sel = label in st.session_state.selected_symptoms
            border = "border:2px solid var(--rose);" if is_sel else "border:1px solid var(--border);"
            st.markdown(f"""
            <div style="background:var(--surface);{border}border-radius:var(--radius);
                padding:10px 4px;text-align:center;margin-bottom:4px;">
                <div style="font-size:26px;margin-bottom:4px;">{icon}</div>
                <div style="font-size:11px;font-weight:500;">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(label, key=f"mood_{label}", use_container_width=True):
                if label in st.session_state.selected_symptoms:
                    st.session_state.selected_symptoms.discard(label)
                else:
                    st.session_state.selected_symptoms.add(label)
                    st.session_state.daily_logs.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "category": "Mood", "name": label,
                    })
                    db_log_symptom(user_id, {
                        "log_date": str(date.today()),
                        "log_time": datetime.now().strftime("%H:%M"),
                        "category": "Mood", "name": label,
                    })
                st.rerun()

# ════════════════ RIGHT ════════════════
with right_col:

    # Daily log card
    st.markdown("""
    <div class="hw-card" style="margin-bottom:14px;">
        <div class="hw-card-title">Today's Log</div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px;color:var(--ink-60);margin-bottom:10px;'>{date.today().strftime('%B %d, %Y')}</div>",
                unsafe_allow_html=True)

    if st.session_state.daily_logs:
        color_map = {"Symptoms":"var(--rose)","Sickness":"#E07B2A","Mood":"#6B58B8"}
        for log in reversed(st.session_state.daily_logs[-8:]):
            dot = color_map.get(log["category"], "var(--rose)")
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                padding:7px 0;border-bottom:1px solid var(--border);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:{dot};flex-shrink:0;"></div>
                    <div style="font-size:13px;font-weight:500;">{log['name']}</div>
                    <span class="hw-tag hw-tag-{'rose' if log['category']=='Symptoms' else 'lavender' if log['category']=='Mood' else 'peach'}"
                          style="font-size:10px;padding:1px 8px;">{log['category']}</span>
                </div>
                <div style="font-size:11px;color:var(--ink-60);">{log['time']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:20px 0;color:var(--ink-60);">
            <div style="font-size:32px;margin-bottom:8px;">📋</div>
            <div style="font-size:13px;">No logs yet today.<br>Tap any symptom above.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    qn_col, cl_col = st.columns(2)
    with qn_col:
        if st.button("📝 Quick Note", key="sym_note"):
            st.switch_page("pages/Notes.py")
    with cl_col:
        if st.button("🗑 Clear Today", key="clear_sym"):
            st.session_state.daily_logs = []
            st.session_state.selected_symptoms = set()
            st.rerun()

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Trends card (from DB)
    recent_all = db_get_symptoms(user_id, days=7)
    if recent_all:
        from collections import Counter
        counts = Counter(s["name"] for s in recent_all)
        top3   = counts.most_common(3)
        st.markdown("""<div class="hw-card" style="margin-bottom:14px;"><div class="hw-card-title">This Week's Trends</div>""",
                    unsafe_allow_html=True)
        for sym, cnt in top3:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                padding:8px 0;border-bottom:1px solid var(--border);">
                <span style="font-size:13px;font-weight:500;">{sym}</span>
                <span class="hw-tag hw-tag-rose">{cnt}×</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # AI card
    st.markdown("""
    <div class="hw-card" style="background:linear-gradient(135deg,var(--rose-bg),#fff);">
        <div class="hw-card-title">AI Symptom Analysis</div>
        <div style="font-size:13px;color:var(--ink-60);line-height:1.6;margin-bottom:10px;">
            Get personalised insights on your symptoms and what they mean for your cycle phase.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask AI →", key="ai_sym"):
        st.switch_page("pages/AI_ChatBot.py")

render_footer()
