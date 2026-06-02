from __future__ import annotations
"""Period Pallete · shared.py — design system, DB helpers, sidebar"""
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

# ══════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Light theme tokens ──────────────────────────────────── */
:root {
    --rose:        #C8627A;
    --rose-lt:     #EEC4CE;
    --rose-bg:     #FDF0F3;
    --mauve:       #A87898;
    --sage:        #7BA898;
    --lavender:    #8878B4;
    --peach:       #C89878;
    --ink:         #1E1420;
    --ink-60:      #6A5068;
    --ink-30:      #B8A8BC;
    --surface:     #FFFFFF;
    --surface-2:   #F8F2F5;
    --bg:          #FAF5F7;
    --border:      #EAD8E2;
    --shadow-clr:  rgba(180,80,100,.07);
    --radius:      14px;
    --radius-sm:   8px;
    --shadow:      0 2px 16px var(--shadow-clr);
    --shadow-md:   0 4px 28px var(--shadow-clr);
}

/* ── Dark theme tokens ───────────────────────────────────── */
[data-theme="dark"], .dark-mode {
    --rose:        #D4788A;
    --rose-lt:     #6A3040;
    --rose-bg:     #2A1820;
    --mauve:       #B888A8;
    --sage:        #88B8A8;
    --lavender:    #9888C4;
    --peach:       #C8A878;
    --ink:         #F0E8EC;
    --ink-60:      #A898A8;
    --ink-30:      #584858;
    --surface:     #1E1420;
    --surface-2:   #281828;
    --bg:          #180E18;
    --border:      #382438;
    --shadow-clr:  rgba(0,0,0,.3);
}

/* ── Base ────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main,
[data-testid="block-container"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

[data-testid="stAppViewContainer"] > .main .block-container {
    padding: 1.5rem 1.5rem 5rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* Hide ONLY the auto-generated Streamlit page-list nav links.
   WARNING: do NOT hide stSidebarNav itself — in Streamlit 1.44+ it wraps
   ALL sidebar content, so hiding it blanks the entire sidebar. */
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display: none !important; }

/* Sidebar collapse/expand arrow */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
}

/* ── ALL buttons: rose pill ──────────────────────────────── */
[data-testid="stButton"] > button {
    background: var(--rose) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 9px 22px !important;
    cursor: pointer !important;
    transition: opacity .18s, transform .18s, box-shadow .18s !important;
    box-shadow: 0 2px 10px rgba(180,80,100,.22) !important;
    min-height: 44px !important;
    width: 100%;
}
[data-testid="stButton"] > button:hover {
    opacity: .87 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(180,80,100,.32) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
    opacity: .95 !important;
}

/* ── Sidebar page_link nav items ─────────────────────────── */
/* st.page_link renders as <a data-testid="stPageLink"> inside a div */
[data-testid="stSidebar"] [data-testid="stPageLink"],
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    background: transparent !important;
    border-radius: var(--radius) !important;
    margin: 1px 4px !important;
    padding: 0 !important;
    border: none !important;
    text-decoration: none !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 10px 16px !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--ink-60) !important;
    text-decoration: none !important;
    transition: background .15s, color .15s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: var(--rose-bg) !important;
    color: var(--rose) !important;
    text-decoration: none !important;
}
/* Active page: disabled link */
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-disabled="true"] a,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-disabled="true"] {
    background: var(--rose-bg) !important;
    color: var(--rose) !important;
    font-weight: 600 !important;
    cursor: default !important;
    pointer-events: none !important;
}
/* Hide the external link icon that page_link adds */
[data-testid="stSidebar"] [data-testid="stPageLink"] svg {
    display: none !important;
}

/* ── Sidebar buttons override: transparent nav style ─────── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: transparent !important;
    color: var(--ink-60) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transform: none !important;
    min-height: 44px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: var(--rose-bg) !important;
    color: var(--rose) !important;
    opacity: 1 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Inputs ──────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border) !important;
    background: var(--surface) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: var(--ink) !important;
    min-height: 44px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--rose) !important;
    box-shadow: 0 0 0 3px var(--rose-lt) !important;
    outline: none !important;
}

/* ── Metrics ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface);
    border-radius: var(--radius);
    padding: 16px 20px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}
[data-testid="stMetricValue"] { color: var(--ink) !important; }
[data-testid="stMetricLabel"] { color: var(--ink-60) !important; }

/* ── Tabs ────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--ink-60) !important;
    min-height: 44px !important;
    padding: 8px 20px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--rose) !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 4px;
}

/* ── Slider ──────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--rose) !important;
    border: 2px solid var(--surface) !important;
    box-shadow: 0 0 0 2px var(--rose) !important;
}

/* ── Toggle ──────────────────────────────────────────────── */
[data-testid="stToggle"] input:checked + div {
    background: var(--rose) !important;
}

/* ── Expander ────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 8px 0 !important; }

/* ── Plotly ──────────────────────────────────────────────── */
.js-plotly-plot .plotly,
.js-plotly-plot .plotly .svg-container { background: transparent !important; }

/* ── Hide Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ══════════════════════════════════════════════════════════
   COMPONENT CLASSES
══════════════════════════════════════════════════════════ */

/* Cards */
.hw-card {
    background: var(--surface);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    padding: 20px;
    margin-bottom: 16px;
}
.hw-card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 16px;
    margin: 0 0 14px;
    color: var(--ink);
    line-height: 1.2;
}
.hw-card-gradient {
    background: linear-gradient(135deg, var(--rose-bg) 0%, var(--surface) 70%);
}

/* Tags */
.hw-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin: 2px;
    line-height: 1.4;
}
.hw-tag-rose     { background: var(--rose-lt);  color: var(--rose); }
.hw-tag-sage     { background: #C8E8DC;          color: #3A7A5A; }
.hw-tag-lavender { background: #D8D0F0;          color: #5848A0; }
.hw-tag-peach    { background: #F0DCC8;          color: #906040; }

/* Page header */
.page-header { margin-bottom: 24px; }
.page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(22px, 4vw, 30px);
    color: var(--ink);
    margin: 0 0 4px;
    line-height: 1.2;
}
.page-header p { font-size: 14px; color: var(--ink-60); margin: 0; }

/* Sidebar logo */
.sidebar-logo {
    padding: 24px 16px 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}
.sidebar-logo .brand {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: var(--ink);
    line-height: 1;
}
.sidebar-logo .tagline {
    font-size: 11px;
    color: var(--ink-60);
    letter-spacing: .5px;
    margin-top: 4px;
}
.nav-section {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
    color: var(--ink-30);
    text-transform: uppercase;
    padding: 10px 16px 3px;
}
.nav-active {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: var(--radius);
    margin: 1px 4px;
    font-size: 14px;
    font-weight: 600;
    background: var(--rose-bg);
    color: var(--rose);
    line-height: 1.4;
}

/* Footer */
.hw-footer {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 100;
    gap: 12px;
}
.hw-footer-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 16px;
    color: var(--ink);
    white-space: nowrap;
}
.hw-footer-brand span {
    font-size: 10px;
    font-family: 'DM Sans', sans-serif;
    color: var(--rose);
    font-weight: 600;
    margin-left: 4px;
}
.hw-footer-quote {
    font-size: 12px;
    color: var(--ink-60);
    font-style: italic;
    max-width: 440px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.hw-spacer { height: 72px; }

/* Theme toggle button */
.theme-toggle {
    position: fixed;
    top: 12px;
    right: 16px;
    z-index: 999;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 6px 14px;
    font-size: 13px;
    color: var(--ink-60);
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: all .2s;
}
.theme-toggle:hover { background: var(--rose-bg); color: var(--rose); }

/* ── Mobile ──────────────────────────────────────────────── */
@media (max-width: 768px) {
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding: 1rem 0.75rem 5rem !important;
    }
    .hw-card { padding: 14px; }
    .hw-footer-quote { display: none; }
    [data-testid="stSidebar"] { min-width: 200px !important; }
}
@media (max-width: 480px) {
    .page-header h1 { font-size: 20px; }
}
</style>
"""

DARK_MODE_CSS = """
<style>
/* Dark mode: override CSS variables on :root so they cascade everywhere */
:root {
    --rose:        #D4788A !important;
    --rose-lt:     #6A3040 !important;
    --rose-bg:     #2A1820 !important;
    --mauve:       #B888A8 !important;
    --sage:        #88B8A8 !important;
    --lavender:    #9888C4 !important;
    --peach:       #C8A878 !important;
    --ink:         #F0E8EC !important;
    --ink-60:      #A898A8 !important;
    --ink-30:      #584858 !important;
    --surface:     #1E1420 !important;
    --surface-2:   #281828 !important;
    --bg:          #180E18 !important;
    --border:      #382438 !important;
    --shadow-clr:  rgba(0,0,0,.35) !important;
}
/* Force backgrounds that Streamlit hardcodes */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main,
[data-testid="block-container"] {
    background: #180E18 !important;
}
[data-testid="stSidebar"] {
    background: #1E1420 !important;
    border-right: 1px solid #382438 !important;
}
[data-testid="stMetric"] {
    background: #1E1420 !important;
    border-color: #382438 !important;
}
</style>
"""


def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    # Apply dark mode if toggled
    if st.session_state.get("dark_mode"):
        st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SUPABASE — authenticated per-request client
# ══════════════════════════════════════════════════════════════
def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _sb_url() -> str:
    return os.getenv("SUPABASE_URL") or _secret("SUPABASE_URL") or ""


def _sb_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY") or _secret("SUPABASE_ANON_KEY") or ""


def get_supabase():
    """Authenticated Supabase client — injects user JWT so RLS works."""
    from supabase import create_client
    url = _sb_url()
    key = _sb_key()
    if not url or not key:
        return None
    client = create_client(url, key)
    access  = st.session_state.get("sb_access_token",  "")
    refresh = st.session_state.get("sb_refresh_token", "") or access
    if access:
        try:
            client.auth.set_session(access, refresh)
        except Exception:
            pass
        client.postgrest.auth(access)
    return client


# ══════════════════════════════════════════════════════════════
#  AUTH HELPERS
# ══════════════════════════════════════════════════════════════
def is_logged_in() -> bool:
    return bool(st.session_state.get("user"))


def require_auth():
    if not is_logged_in():
        st.switch_page("pages/Auth.py")


def get_user():
    return st.session_state.get("user")


def get_user_id() -> str | None:
    u = get_user()
    return u.get("id") if u else None


def get_profile() -> dict:
    return st.session_state.get("profile", {})


# ══════════════════════════════════════════════════════════════
#  DB HELPERS
# ══════════════════════════════════════════════════════════════
def db_get_profile(user_id: str) -> dict:
    sb = get_supabase()
    if not sb: return {}
    try:
        r = sb.table("profiles").select("*").eq("id", user_id).single().execute()
        return r.data or {}
    except Exception:
        return {}


def db_upsert_profile(user_id: str, data: dict):
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("profiles").upsert({"id": user_id, **data}).execute()
    except Exception as e:
        st.error(f"Profile save failed: {e}")


def db_get_notes(user_id: str) -> list:
    sb = get_supabase()
    if not sb: return []
    try:
        r = sb.table("notes").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data or []
    except Exception:
        return []


def db_save_note(user_id: str, data: dict):
    sb = get_supabase()
    if not sb: return None
    try:
        r = sb.table("notes").insert({"user_id": user_id, **data}).execute()
        return r.data[0] if r.data else None
    except Exception as e:
        st.error(f"Note save failed: {e}")
        return None


def db_update_note(note_id: str, data: dict):
    sb = get_supabase()
    if not sb: return
    try:
        import datetime
        sb.table("notes").update({**data, "updated_at": datetime.datetime.utcnow().isoformat()}).eq("id", note_id).execute()
    except Exception as e:
        st.error(f"Note update failed: {e}")


def db_delete_note(note_id: str):
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("notes").delete().eq("id", note_id).execute()
    except Exception as e:
        st.error(f"Note delete failed: {e}")


def db_log_symptom(user_id: str, data: dict):
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("symptom_logs").insert({"user_id": user_id, **data}).execute()
    except Exception as e:
        st.error(f"Symptom log failed: {e}")


def db_get_symptoms(user_id: str, days: int = 30) -> list:
    sb = get_supabase()
    if not sb: return []
    try:
        import datetime
        since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        r = sb.table("symptom_logs").select("*").eq("user_id", user_id).gte("log_date", since).order("log_date", desc=True).execute()
        return r.data or []
    except Exception:
        return []


def db_log_cycle(user_id: str, data: dict) -> bool:
    sb = get_supabase()
    if not sb: return False
    try:
        sb.table("cycle_logs").insert({"user_id": user_id, **data}).execute()
        return True
    except Exception as e:
        st.error(f"Cycle log failed: {e}")
        return False


def db_get_cycle_logs(user_id: str, days: int = 180) -> list:
    sb = get_supabase()
    if not sb: return []
    try:
        import datetime
        since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        r = sb.table("cycle_logs").select("*").eq("user_id", user_id).gte("log_date", since).order("log_date", desc=True).execute()
        return r.data or []
    except Exception:
        return []


def db_log_skin(user_id: str, data: dict):
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("skin_logs").insert({"user_id": user_id, **data}).execute()
    except Exception as e:
        st.error(f"Skin log failed: {e}")


def db_get_skin_logs(user_id: str, limit: int = 30) -> list:
    sb = get_supabase()
    if not sb: return []
    try:
        r = sb.table("skin_logs").select("*").eq("user_id", user_id).order("log_date", desc=True).limit(limit).execute()
        return r.data or []
    except Exception:
        return []


def db_save_chat(user_id: str, role: str, content: str):
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("chat_messages").insert({"user_id": user_id, "role": role, "content": content}).execute()
    except Exception:
        pass


def db_get_chat_history(user_id: str, limit: int = 50) -> list:
    sb = get_supabase()
    if not sb: return []
    try:
        r = sb.table("chat_messages").select("*").eq("user_id", user_id).order("created_at").limit(limit).execute()
        return r.data or []
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
#  CYCLE PHASE
# ══════════════════════════════════════════════════════════════
def get_cycle_phase(cycle_day: int, cycle_length: int = 28) -> tuple[str, str, str]:
    """Returns (phase_name, phase_icon, hex_colour)."""
    if cycle_day <= 5:
        return "Menstrual",  "🌙", "#C8627A"
    elif cycle_day <= 13:
        return "Follicular", "🌱", "#7BA898"
    elif cycle_day <= 16:
        return "Ovulation",  "⭐", "#8878B4"
    else:
        return "Luteal",     "🍂", "#C89878"


def compute_cycle_day(user_id: str, cycle_length: int = 28) -> tuple[int, str]:
    """
    Returns (cycle_day, last_period_iso).
    Uses real logged period data — falls back to day 1 if no data.
    """
    import datetime
    logs = db_get_cycle_logs(user_id, days=180)
    period_logs = [l for l in logs if l["type"] == "period"]
    if period_logs:
        last_period = max(datetime.date.fromisoformat(l["log_date"]) for l in period_logs)
        cycle_day = (datetime.date.today() - last_period).days + 1
        # If we're past the cycle length, they may not have logged the new period yet
        # Keep counting (don't clamp at cycle_length so we show overdue state)
        cycle_day = max(1, cycle_day)
        return cycle_day, str(last_period)
    return 1, str(datetime.date.today())


# ══════════════════════════════════════════════════════════════
#  NVIDIA AI
# ══════════════════════════════════════════════════════════════
def get_ai_response(messages: list[dict], system: str = "") -> str:
    from openai import OpenAI
    api_key = os.getenv("NVIDIA_API_KEY") or _secret("NVIDIA_API_KEY")
    if not api_key:
        return "⚠️ AI not configured — add NVIDIA_API_KEY to your .env file."
    try:
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
        full = []
        if system:
            full.append({"role": "system", "content": system})
        full.extend(messages)
        resp = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=full,
            max_tokens=600,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"I'm having trouble connecting right now 🌸 Please try again. ({e})"


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("track",    "📊", "Dashboard",     "pages/Dashboard.py"),
    ("track",    "🌙", "Cycle Tracker", "pages/Cycle_Tracker.py"),
    ("track",    "✨", "Symptoms",      "pages/Symptom_Tracker.py"),
    ("track",    "💫", "Skin Care",     "pages/Skin_Care.py"),
    ("track",    "📝", "Notes",         "pages/Notes.py"),
    ("insights", "📈", "Insights",      "pages/Insights.py"),
    ("ai",       "🤖", "AI Chat",       "pages/AI_ChatBot.py"),
    ("account",  "⚙️", "Settings",      "pages/Settings.py"),
]
SECTION_LABELS = {
    "track": "TRACK", "insights": "INSIGHTS",
    "ai": "ASSISTANT", "account": "ACCOUNT",
}


def render_sidebar(active_page: str = "Dashboard"):
    profile  = get_profile()
    _nm      = profile.get("name", "") or ""
    name     = _nm if _nm and "@" not in _nm else "there"

    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div class="sidebar-logo">
            <div class="brand">Period Pallete ✦</div>
            <div class="tagline">understand. care. thrive.</div>
        </div>
        <div style="padding:8px 16px 6px;font-size:13px;color:var(--ink-60);">
            Hey, <strong style="color:var(--ink);">{name}</strong> 👋
        </div>
        """, unsafe_allow_html=True)

        # Dark mode toggle
        dark = st.session_state.get("dark_mode", False)
        if st.button("☀️  Light mode" if dark else "🌙  Dark mode",
                     key="_theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # Nav items — real st.buttons styled via CSS
        current_section = None
        for section, icon, label, page in NAV_ITEMS:
            if section != current_section:
                current_section = section
                st.markdown(
                    f'<div class="nav-section">{SECTION_LABELS[section]}</div>',
                    unsafe_allow_html=True,
                )
            if label == active_page:
                # Active: styled HTML div (no click needed)
                st.markdown(
                    f'<div class="nav-active">{icon}&nbsp;&nbsp;{label}</div>',
                    unsafe_allow_html=True,
                )
                # Invisible zero-height placeholder so Streamlit keeps sidebar open
                st.markdown(
                    '<div style="height:0;overflow:hidden;margin:0;padding:0;"></div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}",
                             key=f"_nav_{label}",
                             use_container_width=True):
                    st.switch_page(page)

        st.markdown("<hr>", unsafe_allow_html=True)

        # AI promo
        st.markdown("""
        <div style="margin:4px 8px 8px;background:var(--rose-bg);
             border:1px solid var(--rose-lt);border-radius:var(--radius);padding:12px 14px;">
            <div style="font-size:11px;background:var(--rose);color:#fff;padding:2px 8px;
                 border-radius:20px;display:inline-block;margin-bottom:5px;font-weight:500;">
                ✦ AI
            </div>
            <div style="font-size:12px;color:var(--ink-60);line-height:1.5;margin-top:2px;">
                Your personalised guide for every phase.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖  Chat with AI →", key="_sidebar_ai",
                     use_container_width=True):
            st.switch_page("pages/AI_ChatBot.py")


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
def render_footer(quote: str = '"Understanding your cycle is understanding yourself."'):
    st.markdown(f"""
    <div class="hw-spacer"></div>
    <div class="hw-footer">
        <div class="hw-footer-brand">Period Pallete<span>✦</span></div>
        <div class="hw-footer-quote">{quote}</div>
        <div style="color:var(--rose);font-size:18px;">♥</div>
    </div>
    """, unsafe_allow_html=True)