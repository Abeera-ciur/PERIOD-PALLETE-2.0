"""Period Pallete  · Notes"""
import streamlit as st
from datetime import date
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id,
    db_get_notes, db_save_note, db_update_note, db_delete_note,
)

st.set_page_config(page_title="Period Pallete  – Notes", page_icon="📝", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Notes")

user_id = get_user_id()

# ── State ─────────────────────────────────────────────────────────────────────
if "selected_note_id" not in st.session_state:
    st.session_state.selected_note_id = None
if "editing_note" not in st.session_state:
    st.session_state.editing_note = False
if "new_note_mode" not in st.session_state:
    st.session_state.new_note_mode = False

# ── Data ──────────────────────────────────────────────────────────────────────
notes = db_get_notes(user_id)
if notes and not st.session_state.selected_note_id:
    st.session_state.selected_note_id = notes[0]["id"]

selected = next((n for n in notes if n["id"] == st.session_state.selected_note_id), None)

CAT_COLORS = {
    "Cycle":    ("var(--rose-lt)", "var(--rose)"),
    "Skincare": ("#DFF0E8",        "#3D8B65"),
    "Symptoms": ("#E8E4F4",        "#6B58B8"),
    "General":  ("#FFF3E0",        "#C07030"),
}

st.markdown("""
<div class="page-header"><h1>Personal Notes 📝</h1>
<p>A private space to capture thoughts, symptoms &amp; discoveries</p></div>
""", unsafe_allow_html=True)

list_col, detail_col = st.columns([2, 3], gap="large")

# ════════════════ LEFT ════════════════
with list_col:
    search = st.text_input("", placeholder="🔍  Search notes…", key="note_search",
                            label_visibility="collapsed")
    if st.button("+ New Note", key="add_note_btn"):
        st.session_state.new_note_mode = True
        st.session_state.editing_note  = False

    if st.session_state.new_note_mode:
        st.markdown("""<div class="hw-card" style="border:2px solid var(--rose);">""",
                    unsafe_allow_html=True)
        nt = st.text_input("Title", placeholder="Morning thoughts…", key="new_note_title")
        nc = st.selectbox("Category", ["Cycle","Skincare","Symptoms","General"], key="new_note_cat")
        nb = st.text_area("Content", height=100, placeholder="What's on your mind?", key="new_note_body")
        s1, s2 = st.columns(2)
        with s1:
            if st.button("Save", key="save_new_note"):
                if nt.strip():
                    saved = db_save_note(user_id, {
                        "title":    nt.strip(),
                        "content":  nb.strip(),
                        "category": nc,
                        "cycle_day": 0,
                        "tags":     [],
                    })
                    if saved:
                        st.session_state.selected_note_id = saved["id"]
                    st.session_state.new_note_mode = False
                    st.rerun()
                else:
                    st.error("Please add a title.")
        with s2:
            if st.button("Cancel", key="cancel_new_note"):
                st.session_state.new_note_mode = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    filtered = [n for n in notes
                if not search or search.lower() in n["title"].lower()
                or search.lower() in (n.get("content") or "").lower()]

    st.markdown(f"<div style='font-size:12px;color:var(--ink-60);margin:8px 0 6px;'>{len(filtered)} note{'s' if len(filtered)!=1 else ''}</div>",
                unsafe_allow_html=True)

    for note in filtered:
        bg, fg = CAT_COLORS.get(note.get("category","General"), ("#F0E4EA","var(--rose)"))
        is_sel = note["id"] == st.session_state.selected_note_id
        border = "border:2px solid var(--rose);" if is_sel else "border:1px solid var(--border);"
        snippet = (note.get("content") or "")[:70]
        created = note.get("created_at","")[:10] if note.get("created_at") else ""

        st.markdown(f"""
        <div style="background:var(--surface);{border}border-radius:var(--radius);
            padding:12px;margin-bottom:6px;cursor:pointer;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;">
                <div style="font-size:13px;font-weight:600;line-height:1.3;">{note['title']}</div>
                <span style="padding:2px 8px;border-radius:20px;font-size:10px;font-weight:500;
                    background:{bg};color:{fg};flex-shrink:0;margin-left:6px;">{note.get('category','')}</span>
            </div>
            <div style="font-size:12px;color:var(--ink-60);line-height:1.4;margin-bottom:4px;">{snippet}{'…' if len(snippet)==70 else ''}</div>
            <div style="font-size:10px;color:var(--ink-30);">{created}</div>
        </div>
        """, unsafe_allow_html=True)

        oc, ec, dc = st.columns([3,1,1])
        with oc:
            if st.button("Open", key=f"open_{note['id']}"):
                st.session_state.selected_note_id = note["id"]
                st.session_state.editing_note = False
                st.rerun()
        with ec:
            if st.button("✏️", key=f"edit_{note['id']}"):
                st.session_state.selected_note_id = note["id"]
                st.session_state.editing_note = True
                st.rerun()
        with dc:
            if st.button("🗑", key=f"del_{note['id']}"):
                db_delete_note(note["id"])
                remaining = [n for n in notes if n["id"] != note["id"]]
                st.session_state.selected_note_id = remaining[0]["id"] if remaining else None
                st.session_state.editing_note = False
                st.rerun()

# ════════════════ RIGHT ════════════════
with detail_col:
    if not selected:
        st.markdown("""
        <div class="hw-card" style="text-align:center;padding:48px 24px;">
            <div style="font-size:48px;margin-bottom:12px;">📝</div>
            <div style="font-family:'DM Serif Display',serif;font-size:18px;margin-bottom:6px;">No note selected</div>
            <div style="font-size:13px;color:var(--ink-60);">Select a note from the list or create a new one.</div>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.editing_note:
        st.markdown("""<div class="hw-card" style="border:2px solid var(--rose);">""",
                    unsafe_allow_html=True)
        et = st.text_input("Title", value=selected["title"], key="edit_title")
        ec = st.selectbox("Category", ["Cycle","Skincare","Symptoms","General"],
                           index=["Cycle","Skincare","Symptoms","General"].index(selected.get("category","General")),
                           key="edit_cat")
        eb = st.text_area("Content", value=selected.get("content",""), height=250, key="edit_body")
        sa, ca = st.columns(2)
        with sa:
            if st.button("Save Changes", key="save_edit"):
                db_update_note(selected["id"], {"title": et, "category": ec, "content": eb})
                st.session_state.editing_note = False
                st.rerun()
        with ca:
            if st.button("Cancel", key="cancel_edit"):
                st.session_state.editing_note = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        bg, fg = CAT_COLORS.get(selected.get("category","General"), ("#F0E4EA","var(--rose)"))
        tags = selected.get("tags") or []
        tags_html = "".join(
            f'<span style="background:#E0F2E9;color:#2D7A50;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;margin:2px;">{t}</span>'
            for t in tags
        )
        st.markdown(f"""
        <div class="hw-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                <div style="font-family:'DM Serif Display',serif;font-size:20px;line-height:1.2;flex:1;margin-right:12px;">
                    {selected['title']}
                </div>
                <span style="padding:3px 10px;border-radius:20px;font-size:11px;background:{bg};color:{fg};white-space:nowrap;">
                    {selected.get('category','')}
                </span>
            </div>
            <div style="font-size:12px;color:var(--ink-60);font-style:italic;margin-bottom:12px;">
                {(selected.get('created_at','')[:10])}
            </div>
            <div style="font-size:14px;line-height:1.75;color:var(--ink);white-space:pre-wrap;margin-bottom:16px;">
                {selected.get('content','') or '<em style="color:var(--ink-60);">No content</em>'}
            </div>
            {f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:14px;">{tags_html}</div>' if tags else ''}
        </div>
        """, unsafe_allow_html=True)

render_footer()
