"""Period Pallete  · AI ChatBot"""
import streamlit as st
import sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id, get_profile,
    db_get_chat_history, db_save_chat, get_ai_response, get_cycle_phase,
    db_get_cycle_logs, db_get_symptoms, compute_cycle_day,
)

st.set_page_config(page_title="Period Pallete – AI Chat", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("AI Chat")

# Extra chat-specific CSS
st.markdown("""
<style>
.chat-outer   { max-width: 760px; margin: 0 auto; padding-bottom: 160px; }
.chat-bubble  { display: flex; gap: 10px; margin-bottom: 14px; align-items: flex-end; }
.chat-bubble.user { flex-direction: row-reverse; }
.bubble-body  { max-width: 76%; padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.65; }
.bubble-body.ai   { background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 4px; }
.bubble-body.user { background: var(--rose); color: white; border-bottom-right-radius: 4px; }
.avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center;
          justify-content: center; font-size: 13px; flex-shrink: 0; }
.avatar.ai   { background: var(--rose-bg); border: 1px solid var(--rose-lt); }
.avatar.user { background: var(--rose); color: white; font-weight: 700; }
.chip-row    { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.chip        { padding: 7px 14px; background: var(--rose-bg); border: 1px solid var(--rose-lt);
               border-radius: 20px; font-size: 12px; color: var(--rose); font-weight: 500; }
@media(max-width:600px) {
    .bubble-body { max-width: 90%; font-size: 13px; }
}
</style>
""", unsafe_allow_html=True)

user_id = get_user_id()
profile = get_profile()
name    = profile.get("name", "there")
cycle_length = profile.get("cycle_length", 28)

# ── Load / init chat history ──────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    history = db_get_chat_history(user_id, limit=50)
    if history:
        st.session_state.chat_messages = [
            {"role": h["role"], "content": h["content"]} for h in history
        ]
    else:
        greeting = (
            f"Hey {name}! 🌸 I'm your Period Pallete  AI companion, here for every phase of your cycle. "
            "I can help with cycle insights, skincare tips, symptom explanations, and wellness guidance — "
            "all tailored to you. What's on your mind today?"
        )
        st.session_state.chat_messages = [{"role": "assistant", "content": greeting}]

# ── System prompt ─────────────────────────────────────────────────────────────
# Compute cycle context
cycle_day, _ = compute_cycle_day(user_id, cycle_length)
display_day  = min(cycle_day, cycle_length)
phase, _, _  = get_cycle_phase(display_day, cycle_length)

recent_sym = db_get_symptoms(user_id, days=7)
sym_list   = ", ".join({s["name"] for s in recent_sym}) or "none logged"

SYSTEM = f"""You are Period Pallete  AI, a warm, knowledgeable, and modern women's health companion.
You specialise in menstrual health, cycle phases, hormonal skincare, nutrition, mood, and general wellness.

User context:
- Name: {name}
- Today: {date.today().strftime("%B %d, %Y")}
- Cycle day: {cycle_day} of {cycle_length}
- Current phase: {phase}
- Recent symptoms (7 days): {sym_list}

Guidelines:
- Be warm, modern, and supportive — never clinical or preachy
- Give specific, actionable advice tailored to her cycle phase
- Keep responses concise (2–4 short paragraphs max) and use markdown formatting
- Use occasional emojis for warmth
- Never recommend stopping prescribed medications
- Always suggest consulting a doctor for serious medical concerns
- Reference her phase or symptoms naturally when relevant"""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:760px;margin:0 auto 20px;">
    <div class="page-header"><h1>AI Health Companion ✦</h1>
    <p>Personalised guidance for every phase of your cycle</p></div>
</div>
""", unsafe_allow_html=True)

# ── Messages ──────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-outer">', unsafe_allow_html=True)
for msg in st.session_state.chat_messages:
    role  = msg["role"]
    cls   = "user" if role == "user" else ""
    avlbl = name[0].upper() if role == "user" else "✦"
    st.markdown(f"""
    <div class="chat-bubble {cls}">
        <div class="avatar {role}">{avlbl}</div>
        <div class="bubble-body {role}">{msg['content']}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get("ai_thinking"):
    st.markdown("""
    <div class="chat-bubble">
        <div class="avatar ai">✦</div>
        <div class="bubble-body ai" style="color:var(--ink-60);font-style:italic;">Thinking… 🌸</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Suggestion chips ──────────────────────────────────────────────────────────
chips = [
    f"What phase am I in?",
    "Why do I have headaches?",
    "Best foods for my cycle",
    "Skincare routine advice",
    "How to reduce cramps",
]
st.markdown('<div style="max-width:760px;margin:0 auto;"><div style="font-size:12px;color:var(--ink-60);margin-bottom:6px;">Quick questions</div><div class="chip-row">', unsafe_allow_html=True)
for c in chips:
    st.markdown(f'<div class="chip">{c}</div>', unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

chip_cols = st.columns(len(chips))
for col, chip in zip(chip_cols, chips):
    with col:
        if st.button(chip[:14] + "…" if len(chip) > 14 else chip, key=f"chip_{chip[:8]}"):
            st.session_state.chat_messages.append({"role": "user", "content": chip})
            db_save_chat(user_id, "user", chip)
            st.session_state.ai_thinking = True
            st.rerun()

# ── Input box ─────────────────────────────────────────────────────────────────
st.markdown("<div style='max-width:760px;margin:8px auto 0;'>", unsafe_allow_html=True)
user_input = st.text_area(
    "Message",
    placeholder="Ask about your cycle, symptoms, skincare, or wellness…",
    height=80, key="chat_input", label_visibility="collapsed"
)
c1, c2 = st.columns([5, 1])
with c1:
    send = st.button("Send ✦", key="send_msg", use_container_width=True)
with c2:
    if st.button("Clear", key="clear_chat"):
        st.session_state.chat_messages = [st.session_state.chat_messages[0]]
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Handle send ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
    db_save_chat(user_id, "user", user_input.strip())
    st.session_state.ai_thinking = True
    st.rerun()

if st.session_state.get("ai_thinking") and st.session_state.chat_messages[-1]["role"] == "user":
    st.session_state.ai_thinking = False
    history_for_api = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages[1:]   # skip greeting
    ]
    reply = get_ai_response(history_for_api, system=SYSTEM)
    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    db_save_chat(user_id, "assistant", reply)
    st.rerun()

render_footer('"Every question you ask is a step toward understanding yourself." 🌸')
