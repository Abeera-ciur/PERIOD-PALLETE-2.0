"""Period Pallete  · Settings"""
import streamlit as st
from datetime import date
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, render_sidebar, render_footer,
    require_auth, get_user_id, get_profile, db_upsert_profile,
    get_supabase,
)

st.set_page_config(page_title="Period Pallete  – Settings", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
inject_global_css()
require_auth()
render_sidebar("Settings")

user_id = get_user_id()
profile = get_profile()

st.markdown("""
<div class="page-header"><h1>Account Settings ⚙️</h1>
<p>Manage your profile and preferences</p></div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

# ════════════════ LEFT ════════════════
with left_col:

    # Profile card
    st.markdown("""<div class="hw-card" style="margin-bottom:16px;"><div class="hw-card-title">Profile Information</div>""",
                unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        name_val  = st.text_input("Full Name", value=profile.get("name",""), key="s_name")
    with p2:
        dob_val   = st.date_input("Date of Birth",
                                   value=date.fromisoformat(profile["dob"]) if profile.get("dob") else date(1995,1,1),
                                   key="s_dob")
    if st.button("Save Profile", key="save_profile"):
        db_upsert_profile(user_id, {"name": name_val, "dob": str(dob_val)})
        st.session_state.profile["name"] = name_val
        st.session_state.profile["dob"]  = str(dob_val)
        st.success("✅ Profile saved!")
    st.markdown("</div>", unsafe_allow_html=True)

    # Health preferences
    st.markdown("""<div class="hw-card" style="margin-bottom:16px;"><div class="hw-card-title">Cycle Preferences</div>""",
                unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        cycle_len = st.number_input("Average Cycle Length (days)", min_value=21, max_value=45,
                                     value=profile.get("cycle_length", 28), key="s_cycle_len")
    with h2:
        period_len = st.number_input("Average Period Length (days)", min_value=2, max_value=10,
                                      value=profile.get("period_length", 5), key="s_period_len")
    if st.button("Save Cycle Settings", key="save_cycle"):
        db_upsert_profile(user_id, {"cycle_length": int(cycle_len), "period_length": int(period_len)})
        st.session_state.profile["cycle_length"]  = int(cycle_len)
        st.session_state.profile["period_length"] = int(period_len)
        st.success("✅ Saved!")
    st.markdown("</div>", unsafe_allow_html=True)

    # Account management
    st.markdown("""<div class="hw-card"><div class="hw-card-title">Account Management</div>""",
                unsafe_allow_html=True)
    sb = get_supabase()   # used for password change and logout
    a1, a2 = st.columns(2)
    with a1:
        lang   = st.selectbox("Language", ["English","Español","Français","Deutsch","اردو"],
                               index=["English","Español","Français","Deutsch","اردو"].index(
                                   profile.get("language","English")) if profile.get("language","English") in ["English","Español","Français","Deutsch","اردو"] else 0,
                               key="s_lang")
        region = st.selectbox("Region", ["United States","United Kingdom","Pakistan","India","Canada"],
                               key="s_region")
        if st.button("Save Preferences", key="save_prefs"):
            db_upsert_profile(user_id, {"language": lang, "region": region})
            st.success("✅ Saved!")
    with a2:
        st.markdown("<div style='font-size:14px;font-weight:600;margin-bottom:8px;'>Change Password</div>",
                    unsafe_allow_html=True)
        npw = st.text_input("New password", type="password", key="s_new_pw")
        if st.button("Update Password", key="update_pw"):
            if npw and len(npw) >= 8:
                try:
                    sb.auth.update_user({"password": npw})
                    st.success("Password updated!")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Password must be at least 8 characters.")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", key="logout"):
        try:
            sb.auth.sign_out()
        except Exception:
            pass
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/Auth.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════ RIGHT ════════════════
with right_col:
    user = st.session_state.get("user", {})
    st.markdown(f"""
    <div class="hw-card" style="margin-bottom:16px;text-align:center;padding:28px 20px;">
        <div style="width:72px;height:72px;border-radius:50%;background:var(--rose-bg);border:3px solid var(--rose-lt);
            display:flex;align-items:center;justify-content:center;font-family:'DM Serif Display',serif;
            font-size:28px;color:var(--rose);margin:0 auto 12px;">
            {(profile.get('name','?') or '?')[0].upper()}
        </div>
        <div style="font-family:'DM Serif Display',serif;font-size:20px;margin-bottom:4px;">
            {profile.get('name','New User')}
        </div>
        <div style="font-size:13px;color:var(--ink-60);">{user.get('email','')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hw-card" style="margin-bottom:16px;">
        <div class="hw-card-title">Notifications</div>
        <div style="font-size:13px;color:var(--ink-60);line-height:1.6;margin-bottom:8px;">
            Configure reminders in your device settings or email client to receive period predictions and phase updates.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hw-card" style="background:linear-gradient(135deg,var(--rose-bg),#fff);">
        <div style="font-family:'DM Serif Display',serif;font-size:15px;font-style:italic;
            color:var(--ink);line-height:1.6;text-align:center;">
            "You're not just tracking your cycle — you're understanding your body's potential."
        </div>
    </div>
    """, unsafe_allow_html=True)

render_footer()
