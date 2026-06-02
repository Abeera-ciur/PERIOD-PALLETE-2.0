"""Period Pallete  · Onboarding — first-time cycle history setup"""
import streamlit as st
import sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.shared import (
    inject_global_css, require_auth, get_user_id,
    db_log_cycle, db_upsert_profile,
)

st.set_page_config(
    page_title="Period Pallete  – Setup",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_global_css()
require_auth()

user_id = get_user_id()

# ── State ─────────────────────────────────────────────────────
for k, v in [
    ("ob_step",       1),
    ("ob_cycle_len",  28),
    ("ob_period_len", 5),
    ("ob_last_period", date.today() - timedelta(days=14)),
    ("ob_past_periods", []),
]:
    if k not in st.session_state:
        st.session_state[k] = v

step = st.session_state.ob_step

# ── Shared header ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:28px 0 6px;">
    <div style="font-family:'DM Serif Display',serif;font-size:30px;color:var(--ink);">Period Pallete  ✦</div>
    <div style="font-size:12px;color:var(--ink-60);margin-top:4px;letter-spacing:.5px;">
        understand. care. thrive.
    </div>
</div>
""", unsafe_allow_html=True)

# Progress bar
pct = int(step / 3 * 100)
step_labels = ["Cycle basics", "Last period", "Period history"]
st.markdown(f"""
<div style="max-width:500px;margin:0 auto 24px;">
    <div style="display:flex;justify-content:space-between;font-size:12px;
                color:var(--ink-60);margin-bottom:6px;">
        <span>Step {step} of 3</span>
        <span>{step_labels[step-1]}</span>
    </div>
    <div style="background:var(--border);border-radius:4px;height:4px;">
        <div style="background:var(--rose);height:4px;border-radius:4px;
                    width:{pct}%;transition:width .4s;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

_, col, _ = st.columns([1, 6, 1])

# ══════════════ STEP 1 — Cycle basics ════════════════
if step == 1:
    with col:
        st.markdown("""
        <div class="hw-card">
            <div style="font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:8px;">
                Let's understand your cycle 🌙
            </div>
            <div style="font-size:14px;color:var(--ink-60);line-height:1.65;margin-bottom:4px;">
                These two numbers help the AI predict your phases accurately
                and personalise every recommendation from day one.
            </div>
        </div>
        """, unsafe_allow_html=True)

        cycle_len = st.number_input(
            "Average cycle length (days from one period start to the next)",
            min_value=21, max_value=45, value=st.session_state.ob_cycle_len,
            step=1, key="ob_in_cycle"
        )
        st.caption("Most cycles are 21–35 days. Not sure? Start with 28.")

        period_len = st.number_input(
            "How many days does your period typically last?",
            min_value=1, max_value=10, value=st.session_state.ob_period_len,
            step=1, key="ob_in_period"
        )
        st.caption("Typically 3–7 days.")

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        if st.button("Continue →", key="ob1_next"):
            st.session_state.ob_cycle_len  = int(cycle_len)
            st.session_state.ob_period_len = int(period_len)
            # Pre-fill past periods as estimates
            base = st.session_state.ob_last_period
            c    = int(cycle_len)
            st.session_state.ob_past_periods = [
                base - timedelta(days=c * i) for i in range(1, 6)
            ]
            st.session_state.ob_step = 2
            st.rerun()

# ══════════════ STEP 2 — Last period ════════════════
elif step == 2:
    with col:
        st.markdown("""
        <div class="hw-card">
            <div style="font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:8px;">
                When did your last period start? 📅
            </div>
            <div style="font-size:14px;color:var(--ink-60);line-height:1.65;">
                The first day of bleeding — this sets your current cycle day and phase.
            </div>
        </div>
        """, unsafe_allow_html=True)

        last_period = st.date_input(
            "First day of your most recent period",
            value=st.session_state.ob_last_period,
            max_value=date.today(),
            key="ob_in_last"
        )

        # Live phase preview
        cycle_day  = max(1, (date.today() - last_period).days + 1)
        cycle_len  = st.session_state.ob_cycle_len
        display_day = min(cycle_day, cycle_len)
        is_overdue  = cycle_day > cycle_len

        if display_day <= 5:      phase, icon = "Menstrual",  "🌙"
        elif display_day <= 13:   phase, icon = "Follicular", "🌱"
        elif display_day <= 16:   phase, icon = "Ovulation",  "⭐"
        else:                     phase, icon = "Luteal",     "🍂"

        next_period = last_period + timedelta(days=cycle_len)
        days_until  = (next_period - date.today()).days

        st.markdown(f"""
        <div style="background:var(--rose-bg);border:1px solid var(--rose-lt);border-radius:var(--radius);
                    padding:16px 20px;margin-top:10px;">
            <div style="font-size:13px;color:var(--ink-60);margin-bottom:6px;">Based on this date:</div>
            <div style="font-size:15px;font-weight:600;color:var(--ink);margin-bottom:4px;">
                {icon} <strong style="color:var(--rose);">{phase}</strong> phase
                {"· Day " + str(display_day) if not is_overdue else "· Period may be late"}
            </div>
            <div style="font-size:13px;color:var(--ink-60);">
                {"Next period: <strong style='color:var(--ink);'>" + next_period.strftime('%B %d, %Y') + "</strong>"
                 if days_until >= 0 else
                 "<strong style='color:var(--rose);'>Period overdue by " + str(-days_until) + " days</strong>"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        bc, nc = st.columns(2)
        with bc:
            if st.button("← Back", key="ob2_back"):
                st.session_state.ob_step = 1
                st.rerun()
        with nc:
            if st.button("Continue →", key="ob2_next"):
                st.session_state.ob_last_period = last_period
                c = st.session_state.ob_cycle_len
                st.session_state.ob_past_periods = [
                    last_period - timedelta(days=c * i) for i in range(1, 6)
                ]
                st.session_state.ob_step = 3
                st.rerun()

# ══════════════ STEP 3 — History ════════════════
elif step == 3:
    with col:
        st.markdown("""
        <div class="hw-card">
            <div style="font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:8px;">
                Your last 5 period start dates 📋
            </div>
            <div style="font-size:14px;color:var(--ink-60);line-height:1.65;">
                We've estimated these from your cycle length.
                Adjust any you remember — the AI uses this to spot patterns.
            </div>
            <div style="font-size:12px;color:var(--ink-30);margin-top:6px;">
                Can't remember? The estimates are fine to leave as-is.
            </div>
        </div>
        """, unsafe_allow_html=True)

        cycle = st.session_state.ob_cycle_len
        past_dates = []
        for i, est in enumerate(st.session_state.ob_past_periods):
            picked = st.date_input(
                f"Period {i+1} · approx. {(i+1)*cycle} days before your last",
                value=est,
                max_value=st.session_state.ob_last_period - timedelta(days=1),
                key=f"ob_past_{i}",
            )
            past_dates.append(picked)

        # Avg cycle preview
        all_dates = [st.session_state.ob_last_period] + past_dates
        if len(all_dates) >= 2:
            gaps     = [(all_dates[i] - all_dates[i+1]).days for i in range(len(all_dates)-1)]
            avg_gap  = round(sum(gaps) / len(gaps))
            match    = "✓ matches your setting!" if avg_gap == cycle else f"(you entered {cycle} days)"
            st.markdown(f"""
            <div style="background:var(--surface-2);border:1px solid var(--border);
                        border-radius:var(--radius);padding:12px 16px;margin:12px 0;">
                <div style="font-size:13px;color:var(--ink-60);">
                    📊 Calculated average cycle: <strong style="color:var(--ink);">{avg_gap} days</strong>
                    <span style="color:var(--ink-30);"> {match}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        bc2, fc = st.columns(2)
        with bc2:
            if st.button("← Back", key="ob3_back"):
                st.session_state.ob_step = 2
                st.rerun()
        with fc:
            if st.button("✦ Finish setup", key="ob_finish"):
                with st.spinner("Saving your cycle history…"):
                    db_upsert_profile(user_id, {
                        "cycle_length":  st.session_state.ob_cycle_len,
                        "period_length": st.session_state.ob_period_len,
                    })
                    st.session_state.profile = st.session_state.get("profile", {})
                    st.session_state.profile["cycle_length"]  = st.session_state.ob_cycle_len
                    st.session_state.profile["period_length"] = st.session_state.ob_period_len

                    # Save last period
                    db_log_cycle(user_id, {
                        "log_date": str(st.session_state.ob_last_period),
                        "type": "period",
                        "notes": "Entered during onboarding",
                    })
                    # Save historical periods
                    for d in past_dates:
                        db_log_cycle(user_id, {
                            "log_date": str(d),
                            "type": "period",
                            "notes": "Historical — entered during onboarding",
                        })

                st.success("All set! 🌸")
                st.session_state.is_new_user = False
                st.switch_page("pages/Dashboard.py")
