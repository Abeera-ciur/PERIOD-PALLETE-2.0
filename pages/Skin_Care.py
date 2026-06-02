"""Period Pallete  · Skin Care"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id, get_profile,
    db_log_skin, db_get_skin_logs, get_cycle_phase,
)

st.set_page_config(page_title="Period Pallete  – Skin Care", page_icon="💫", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Skin Care")

user_id = get_user_id()
profile = get_profile()
cycle_len = profile.get("cycle_length", 28)

if "routine_checks" not in st.session_state:
    st.session_state.routine_checks = {}

st.markdown("""
<div class="page-header"><h1>Personalised Skincare 💫</h1>
<p>Tailored to your cycle phase and skin type</p></div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

STEPS = [
    (1, "Cleanse",    "Gentle Honey & Oat Cleanser",       "DIY: Pure Hydrating Cleanser"),
    (2, "Tone",       "Balancing & Brightening Toner",      "DIY: Rosewater & Witch Hazel"),
    (3, "Treatment",  "DIY: Vitamin C & Ferulic Acid",      "Product: Pore-Reducing Toner"),
    (4, "Moisturise", "Nourishing Barrier Cream",           "DIY: Shea + Niacinamide + Jojoba"),
    (5, "Protect",    "Broad Spectrum SPF 30+",             "Oil Control Sunscreen"),
]

# ════════════════ LEFT ════════════════
with left_col:
    st.markdown("""
    <div class="hw-card" style="margin-bottom:16px;">
        <div class="hw-card-title">Step-by-Step Daily Ritual</div>
    """, unsafe_allow_html=True)

    completed = sum(1 for s in STEPS if st.session_state.routine_checks.get(f"step_{s[0]}"))
    pct = int(completed / len(STEPS) * 100)
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--ink-60);margin-bottom:4px;">
            <span>Today's progress</span><span>{completed}/{len(STEPS)} steps</span>
        </div>
        <div style="background:var(--border);border-radius:4px;height:6px;">
            <div style="background:var(--rose);height:6px;border-radius:4px;width:{pct}%;transition:width .3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for num, title, product, diy in STEPS:
        key     = f"step_{num}"
        checked = st.session_state.routine_checks.get(key, False)
        bg      = "var(--rose-bg)" if checked else "var(--bg)"
        border  = "border:2px solid var(--rose);" if checked else "border:1px solid var(--border);"
        check_icon = "✅" if checked else f"<span style='color:var(--rose);font-weight:700;'>{num}</span>"

        st.markdown(f"""
        <div style="background:{bg};{border}border-radius:var(--radius);padding:14px;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <div style="width:26px;height:26px;border-radius:50%;background:{'var(--rose)' if checked else 'var(--rose-bg)'};
                    color:{'white' if checked else 'var(--rose)'};display:flex;align-items:center;
                    justify-content:center;font-size:12px;font-weight:700;flex-shrink:0;">
                    {'✓' if checked else str(num)}
                </div>
                <div style="font-size:14px;font-weight:600;">{title}</div>
            </div>
            <div style="font-size:13px;font-weight:500;margin-bottom:2px;">{product}</div>
            <div style="font-size:12px;color:var(--ink-60);">{diy}</div>
        </div>
        """, unsafe_allow_html=True)

        btn_label = "✓ Done" if not checked else "Undo"
        if st.button(btn_label, key=f"btn_{key}"):
            st.session_state.routine_checks[key] = not checked
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✓ Mark All Complete", key="complete_routine"):
        for num, *_ in STEPS:
            st.session_state.routine_checks[f"step_{num}"] = True
        st.success("🌸 Full routine logged!")
        st.rerun()

# ════════════════ RIGHT ════════════════
with right_col:
    # Skin score from logs
    skin_logs = db_get_skin_logs(user_id, limit=10)
    avg_score = sum(l["rating"] for l in skin_logs) / len(skin_logs) if skin_logs else 7.0

    st.markdown("""<div class="hw-card" style="margin-bottom:16px;">
        <div class="hw-card-title">Your Skin Score</div>""", unsafe_allow_html=True)
    sc, ic = st.columns([1,2])
    with sc:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=avg_score * 10,
            gauge={
                "axis": {"range": [0,100], "visible": False},
                "bar":  {"color": "#A8C5B5", "thickness": 0.35},
                "bgcolor": "#EDF6F1",
            },
            number={"font": {"size": 28, "color": "#2D1F2E", "family": "DM Serif Display"},
                    "suffix": ""},
            domain={"x":[0,1],"y":[0,1]}
        ))
        fig.update_layout(height=130, margin=dict(l=0,r=0,t=8,b=0),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, key="skin_score")
    with ic:
        score_label = "Excellent 🌟" if avg_score >= 8 else "Good 🌿" if avg_score >= 6 else "Needs care 💧"
        st.markdown(f"""
        <div style="padding:10px 0;">
            <div style="font-size:14px;font-weight:600;margin-bottom:4px;">{score_label}</div>
            <div style="font-size:12px;color:var(--ink-60);line-height:1.6;">Based on your last {len(skin_logs)} log{'s' if len(skin_logs)!=1 else ''}.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # AI coach
    st.markdown("""
    <div class="hw-card" style="background:linear-gradient(135deg,var(--rose-bg),#fff);margin-bottom:16px;">
        <div class="hw-card-title">AI Skincare Coach</div>
        <div style="font-size:13px;color:var(--ink-60);line-height:1.6;margin-bottom:10px;">
            Your routine is synced to your cycle phase. Consider adding an evening hydration step for extra nourishment! ✨
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask AI →", key="ai_skin"):
        st.switch_page("pages/AI_ChatBot.py")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Ingredient spotlight
    st.markdown("""
    <div class="hw-card" style="margin-bottom:16px;">
        <div class="hw-card-title">Ingredient Spotlight</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center;">
    """, unsafe_allow_html=True)
    for icon, name_i in [("🧴","Hyaluronic Acid"),("✨","Niacinamide"),("🍊","Vitamin C"),("🌿","Retinol")]:
        st.markdown(f"""
        <div style="padding:8px 4px;">
            <div style="width:44px;height:44px;border-radius:50%;background:var(--rose-bg);
                border:1px solid var(--rose-lt);display:flex;align-items:center;
                justify-content:center;font-size:18px;margin:0 auto 4px;">{icon}</div>
            <div style="font-size:10px;color:var(--ink-60);line-height:1.3;">{name_i}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Log skin
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Log Today's Skin</div>""",
                unsafe_allow_html=True)
    rating = st.slider("Skin rating (1–10)", 1, 10, 7, key="skin_rating")
    notes_in = st.text_area("Notes (breakouts, dryness, improvements…)",
                             height=70, key="skin_notes")
    if st.button("Save Log", key="log_skin"):
        db_log_skin(user_id, {
            "log_date": str(date.today()),
            "rating":   rating,
            "notes":    notes_in or None,
        })
        st.success("✅ Saved!")
        st.rerun()
    if skin_logs:
        import pandas as pd
        df = pd.DataFrame(skin_logs)[["log_date","rating","notes"]].head(5)
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
