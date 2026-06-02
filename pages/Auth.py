"""
Period Pallete  · Auth.py
Login / Sign-up with SMTP email verification.
"""
import streamlit as st
import sys, os, random, string, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import inject_global_css, get_supabase, db_upsert_profile, db_get_profile

st.set_page_config(
    page_title="Period Pallete  – Welcome",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_global_css()

# If already logged in, redirect to dashboard
if st.session_state.get("user"):
    st.switch_page("pages/Dashboard.py")

# ── State ─────────────────────────────────────────────────────
for k, v in [("auth_tab", "login"), ("otp_sent", False), ("otp_code", ""),
              ("otp_expiry", None), ("pending_email", ""), ("pending_password", ""),
              ("pending_name", ""), ("auth_error", ""), ("auth_success", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── SMTP helper ───────────────────────────────────────────────
def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def send_verification_email(to_email: str, code: str) -> bool:
    host     = os.getenv("SMTP_HOST") or _secret("SMTP_HOST") or "smtp.gmail.com"
    port     = int(os.getenv("SMTP_PORT") or _secret("SMTP_PORT") or "587")
    user     = os.getenv("SMTP_USER") or _secret("SMTP_USER") or ""
    password = os.getenv("SMTP_PASSWORD") or _secret("SMTP_PASSWORD") or ""
    from_    = os.getenv("SMTP_FROM") or _secret("SMTP_FROM") or user

    if not user or not password:
        # Dev mode: show code on screen instead
        st.session_state.auth_success = f"📧 [DEV MODE] Your code: **{code}** (configure SMTP to send real emails)"
        return True

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px;">
        <div style="font-family:Georgia,serif;font-size:28px;color:#2D1F2E;margin-bottom:4px;">Period Pallete  ✦</div>
        <div style="font-size:13px;color:#7A6078;margin-bottom:28px;">understand. care. thrive.</div>
        <p style="font-size:15px;color:#2D1F2E;">Your verification code:</p>
        <div style="font-size:40px;font-weight:700;color:#E8547A;letter-spacing:6px;margin:16px 0;text-align:center;">
            {code}
        </div>
        <p style="font-size:13px;color:#7A6078;">This code expires in 10 minutes.<br>
        If you didn't request this, you can ignore this email.</p>
        <hr style="border:none;border-top:1px solid #F0E4EA;margin:24px 0;">
        <div style="font-size:11px;color:#C4B8C8;">Period Pallete  · your wellness companion</div>
    </div>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Period Pallete  verification code"
    msg["From"] = from_
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port) as s:
            s.ehlo()
            s.starttls(context=context)
            s.login(user, password)
            s.sendmail(user, to_email, msg.as_string())
        return True
    except Exception as e:
        st.session_state.auth_error = f"Email send failed: {e}"
        return False


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


# ── UI ────────────────────────────────────────────────────────
st.markdown("""
<div class="auth-container">
    <div class="auth-logo">
        <div class="brand">Period Pallete  ✦</div>
        <div class="tagline">understand. care. thrive.</div>
    </div>
</div>
""", unsafe_allow_html=True)

_, center_col, _ = st.columns([1, 4, 1])
with center_col:

    # ── Tab selector ──────────────────────────────
    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    # ════════════════ SIGN IN ════════════════
    with tab_login:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        email_in = st.text_input("Email address", placeholder="you@example.com", key="login_email")
        pass_in  = st.text_input("Password", type="password", placeholder="Your password", key="login_pass")

        if st.session_state.auth_error and st.session_state.auth_tab == "login":
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = ""

        if st.button("Sign In →", key="btn_login"):
            if not email_in or not pass_in:
                st.error("Please fill in both fields.")
            else:
                sb = get_supabase()
                if not sb:
                    st.error("Database not configured. Check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
                else:
                    try:
                        resp = sb.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                        user = resp.user
                        session = resp.session
                        # Persist user in session state
                        st.session_state.user = {
                            "id": user.id,
                            "email": user.email,
                        }
                        st.session_state.sb_access_token  = session.access_token
                        st.session_state.sb_refresh_token = session.refresh_token
                        # Load profile
                        st.session_state.profile = db_get_profile(user.id)
                        st.session_state.auth_tab = "login"
                        st.switch_page("pages/Dashboard.py")
                    except Exception as e:
                        st.error(f"Sign in failed: {e}")

        st.markdown("""
        <div style="text-align:center;font-size:12px;color:var(--ink-60);margin-top:12px;">
            Forgot password? Use <em>Reset via Email</em> below.
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Reset password via email"):
            reset_email = st.text_input("Enter your email", key="reset_email")
            if st.button("Send reset link", key="btn_reset"):
                sb = get_supabase()
                if sb and reset_email:
                    try:
                        sb.auth.reset_password_email(reset_email)
                        st.success("Reset link sent! Check your inbox.")
                    except Exception as e:
                        st.error(str(e))

    # ════════════════ SIGN UP ════════════════
    with tab_signup:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        if not st.session_state.otp_sent:
            # Step 1 – collect details
            su_name  = st.text_input("Your name", placeholder="Ananya", key="su_name")
            su_email = st.text_input("Email address", placeholder="you@example.com", key="su_email")
            su_pass  = st.text_input("Password (min 8 chars)", type="password", key="su_pass")
            su_pass2 = st.text_input("Confirm password", type="password", key="su_pass2")

            if st.session_state.auth_error and st.session_state.auth_tab == "signup":
                st.error(st.session_state.auth_error)
                st.session_state.auth_error = ""
            if st.session_state.auth_success:
                st.success(st.session_state.auth_success)
                st.session_state.auth_success = ""

            if st.button("Continue →", key="btn_signup_step1"):
                if not su_name or not su_email or not su_pass:
                    st.error("Please fill in all fields.")
                elif su_pass != su_pass2:
                    st.error("Passwords don't match.")
                elif len(su_pass) < 8:
                    st.error("Password must be at least 8 characters.")
                elif "@" not in su_email:
                    st.error("Please enter a valid email.")
                else:
                    otp = generate_otp()
                    st.session_state.otp_code      = otp
                    st.session_state.otp_expiry     = datetime.utcnow() + timedelta(minutes=10)
                    st.session_state.pending_email  = su_email
                    st.session_state.pending_password = su_pass
                    st.session_state.pending_name   = su_name
                    st.session_state.auth_tab       = "signup"
                    if send_verification_email(su_email, otp):
                        st.session_state.otp_sent = True
                        st.rerun()

        else:
            # Step 2 – verify OTP
            st.markdown(f"""
            <div class="hw-card" style="text-align:center;padding:24px;">
                <div style="font-size:28px;margin-bottom:8px;">📧</div>
                <div style="font-family:'DM Serif Display',serif;font-size:18px;margin-bottom:6px;">Check your email</div>
                <div style="font-size:13px;color:var(--ink-60);">
                    We sent a 6-digit code to<br>
                    <strong style="color:var(--ink);">{st.session_state.pending_email}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.auth_success:
                st.info(st.session_state.auth_success)
                st.session_state.auth_success = ""

            entered_otp = st.text_input(
                "Verification code", placeholder="123456",
                max_chars=6, key="otp_input"
            )

            if st.button("Verify & Create Account →", key="btn_verify"):
                if not entered_otp:
                    st.error("Please enter the code.")
                elif datetime.utcnow() > st.session_state.otp_expiry:
                    st.error("Code expired. Please go back and try again.")
                    st.session_state.otp_sent = False
                elif entered_otp.strip() != st.session_state.otp_code:
                    st.error("Incorrect code. Please try again.")
                else:
                    # Create user in Supabase
                    sb = get_supabase()
                    if not sb:
                        st.error("Database not configured.")
                    else:
                        try:
                            # Sign up — we already verified email ourselves via OTP
                            resp = sb.auth.sign_up({
                                "email": st.session_state.pending_email,
                                "password": st.session_state.pending_password,
                                "options": {"data": {"name": st.session_state.pending_name}},
                            })
                            user = resp.user

                            if user is None:
                                st.error("Signup failed — please try again.")
                                st.stop()

                            # Sign in immediately to get authenticated session
                            # (RLS requires auth before profile insert)
                            try:
                                login_resp = sb.auth.sign_in_with_password({
                                    "email": st.session_state.pending_email,
                                    "password": st.session_state.pending_password,
                                })
                            except Exception:
                                st.error(
                                    "\u26a0\ufe0f **Supabase email confirmation must be disabled.** "
                                    "Go to: Supabase Dashboard \u2192 Authentication \u2192 Providers "
                                    "\u2192 Email \u2192 turn OFF **Confirm email** \u2192 Save. Then try again."
                                )
                                st.stop()

                            st.session_state.user = {
                                "id": login_resp.user.id,
                                "email": login_resp.user.email,
                            }
                            # Store tokens NOW so get_supabase() sends auth header
                            st.session_state.sb_access_token  = login_resp.session.access_token
                            st.session_state.sb_refresh_token = login_resp.session.refresh_token
                            st.session_state.profile = {"name": st.session_state.pending_name}

                            # Profile upsert — RLS passes because token is now set
                            db_upsert_profile(login_resp.user.id, {"name": st.session_state.pending_name})

                            # Cleanup OTP state
                            for k in ["otp_sent", "otp_code", "otp_expiry",
                                      "pending_email", "pending_password", "pending_name"]:
                                st.session_state[k] = "" if isinstance(st.session_state[k], str) else False
                            # New users go through onboarding to log cycle history
                            st.session_state["is_new_user"] = True
                            st.switch_page("pages/Onboarding.py")
                        except Exception as e:
                            err = str(e)
                            if "Email not confirmed" in err:
                                st.error(
                                    "\u26a0\ufe0f **Fix needed in Supabase Dashboard:** "
                                    "Authentication \u2192 Providers \u2192 Email \u2192 "
                                    "turn OFF **'Confirm email'** \u2192 Save. Then try again."
                                )
                            else:
                                st.error(f"Account creation failed: {e}")

            if st.button("← Back", key="btn_back_otp"):
                st.session_state.otp_sent = False
                st.rerun()

    st.markdown("""
    <div style="text-align:center;font-size:11px;color:var(--ink-30);margin-top:20px;padding-bottom:20px;">
        By continuing you agree to Period Pallete 's Terms &amp; Privacy Policy.
    </div>
    """, unsafe_allow_html=True)
