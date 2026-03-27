
import streamlit as st
import google.generativeai as genai
import math
import os


def load_gemini_api_key():
    """Read API key from Streamlit secrets first, then environment variable."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        key = os.getenv("GEMINI_API_KEY", "")
    return key.strip()


GEMINI_API_KEY = load_gemini_api_key()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_working_gemini_model():
    preferred_models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-flash-lite-preview-06-17",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
    ]
    try:
        available = []
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            if "generateContent" in methods:
                available.append(model.name)
        for name in preferred_models:
            if name in available:
                return genai.GenerativeModel(name), name
        if available:
            return genai.GenerativeModel(available[0]), available[0]
    except Exception:
        pass
    return genai.GenerativeModel("gemini-1.5-flash"), "gemini-1.5-flash"


if GEMINI_API_KEY:
    gemini_model, gemini_model_name = get_working_gemini_model()
else:
    gemini_model, gemini_model_name = None, "not-configured"


st.set_page_config(
    page_title="RupeeMirror",
    page_icon="₹",
    layout="wide",
)


# ─── FULL CSS: matches landing.html's visual identity ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800;900&family=DM+Mono:wght@300;400;500&display=swap');

/* ── VARIABLES (same as landing.html) ── */
:root {
  --void-dark:    #060010;
  --void-mid:     #0d0022;
  --void-purple:  #863BFF;
  --void-violet:  #5B1FCC;
  --hear-green:   #00ff85;
  --hear-mint:    #00cc6a;
  --text-primary: #f0eeff;
  --text-muted:   #7a6a9a;
  --text-dim:     #3d2d5a;
  --gold:         #ffaa00;
  --red-bad:      #ff4455;
}

/* ── BASE ── */
.stApp {
    background: var(--void-dark) !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
}

/* Noise grain overlay */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none; opacity: 0.3;
}

/* Animated purple grid background */
.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
        linear-gradient(rgba(134,59,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(134,59,255,0.06) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 20%, black 20%, transparent 100%);
    pointer-events: none;
    animation: gridPulse 8s ease-in-out infinite;
}
@keyframes gridPulse {
    0%, 100% { opacity: 0.5; }
    50%       { opacity: 1; }
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--void-mid); }
::-webkit-scrollbar-thumb { background: var(--void-purple); border-radius: 3px; }

/* ── HERO HEADER ── */
.rupee-hero {
    text-align: center;
    padding: 60px 20px 20px;
    position: relative;
}
.rupee-eyebrow {
    display: inline-flex; align-items: center; gap: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; letter-spacing: 2.5px;
    color: var(--void-purple); text-transform: uppercase;
    margin-bottom: 20px;
}
.rupee-eyebrow::before, .rupee-eyebrow::after {
    content: ''; display: block; height: 1px; width: 28px;
    background: var(--void-purple); opacity: 0.5;
}
.rupee-title {
    font-size: clamp(2.4rem, 6vw, 5rem);
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -3px;
    margin-bottom: 16px;
}
.rupee-title .green  { color: var(--hear-green); }
.rupee-title .purple { color: var(--void-purple); }
.rupee-sub {
    font-size: 1rem;
    font-weight: 300;
    color: var(--text-muted);
    max-width: 520px;
    margin: 0 auto 8px;
    line-height: 1.7;
    font-family: 'Sora', sans-serif;
}

/* ── STEP BADGE (mono pill like landing nav-pill) ── */
.step-badge {
    display: inline-block;
    background: rgba(134,59,255,0.12);
    border: 1px solid rgba(134,59,255,0.35);
    border-radius: 100px;
    padding: 6px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 2px;
    color: var(--void-purple);
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* ── SECTION HEADING ── */
.section-head {
    font-family: 'Sora', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 18px 0 12px 0;
    letter-spacing: -0.5px;
}
.section-head .g { color: var(--hear-green); }
.section-head .p { color: var(--void-purple); }

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(134,59,255,0.18) !important;
    margin: 28px 0 !important;
}

/* ── METRIC CARDS (glassmorphism, landing card style) ── */
.metric-card {
    background: rgba(13,0,34,0.6);
    border: 1px solid rgba(134,59,255,0.2);
    border-radius: 18px;
    padding: 22px 18px;
    text-align: center;
    backdrop-filter: blur(12px);
    margin: 6px 0;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.metric-card:hover {
    border-color: rgba(134,59,255,0.45);
    box-shadow: 0 0 30px rgba(134,59,255,0.1);
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}
.metric-number {
    font-family: 'Sora', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -1px;
}
.good  { color: var(--hear-green); }
.bad   { color: var(--red-bad); }
.warn  { color: var(--gold); }

/* ── AI RESPONSE CARDS ── */
.ai-card {
    background: rgba(13,0,34,0.5);
    border: 1px solid rgba(134,59,255,0.22);
    border-radius: 18px;
    padding: 24px 28px;
    margin: 14px 0;
    line-height: 1.85;
    color: var(--text-muted);
    font-size: 0.95rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.ai-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--void-purple), transparent);
    border-radius: 18px 0 0 18px;
}
.ai-card-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--void-purple);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.behavior-card {
    background: rgba(13,0,34,0.5);
    border: 1px solid rgba(255,170,0,0.2);
    border-radius: 18px;
    padding: 24px 28px;
    margin: 14px 0;
    line-height: 1.85;
    color: var(--text-muted);
    font-size: 0.95rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.behavior-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--gold), transparent);
}
.action-card {
    background: rgba(0,255,133,0.03);
    border: 1px solid rgba(0,255,133,0.18);
    border-radius: 18px;
    padding: 24px 28px;
    margin: 14px 0;
    line-height: 1.85;
    color: var(--text-muted);
    font-size: 0.95rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.action-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--hear-green), transparent);
}

/* ── WARNING BOX ── */
.warn-box {
    background: rgba(255,170,0,0.08);
    border: 1px solid rgba(255,170,0,0.3);
    border-radius: 12px;
    padding: 14px 20px;
    color: var(--gold);
    font-size: 0.88rem;
    margin: 12px 0;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.3px;
}

/* ── DISCLAIMER ── */
.disclaimer {
    text-align: center;
    color: var(--gold);
    font-size: 0.88rem;
    padding: 24px 28px;
    border: 1.5px solid rgba(255,170,0,0.4);
    background: rgba(255,170,0,0.08);
    border-radius: 12px;
    margin-top: 32px;
    margin-bottom: 32px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.4px;
    line-height: 1.6;
}

/* ── STREAMLIT OVERRIDES ── */
/* Button */
.stButton > button {
    background: var(--hear-green) !important;
    color: #000 !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 13px 32px !important;
    width: 100% !important;
    margin-top: 12px !important;
    letter-spacing: -0.3px !important;
    transition: box-shadow 0.3s, transform 0.2s !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    box-shadow: 0 0 40px rgba(0,255,133,0.4), 0 0 80px rgba(0,255,133,0.15) !important;
    transform: scale(1.02) !important;
}

/* Number inputs */
.stNumberInput input {
    background: rgba(13,0,34,0.7) !important;
    border: 1px solid rgba(134,59,255,0.25) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.95rem !important;
}
.stNumberInput input:focus {
    border-color: var(--void-purple) !important;
    box-shadow: 0 0 0 2px rgba(134,59,255,0.15) !important;
}

/* Labels */
.stNumberInput label, .stSlider label, .stSelectbox label, .stRadio label {
    color: var(--text-muted) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(13,0,34,0.7) !important;
    border: 1px solid rgba(134,59,255,0.25) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
}

/* Slider */
.stSlider .st-emotion-cache-1dp5vir,
[data-testid="stSlider"] > div > div > div > div {
    background: var(--void-purple) !important;
}

/* Radio */
.stRadio > div { gap: 6px !important; }
.stRadio label {
    color: var(--text-muted) !important;
    font-size: 0.88rem !important;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: var(--text-dim) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.3px !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: var(--void-purple) !important; }

/* Markdown body text */
.stMarkdown p, .stWrite p {
    color: var(--text-muted) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.93rem !important;
    line-height: 1.75 !important;
}

/* Bold within markdown */
.stMarkdown strong { color: var(--text-primary) !important; }

/* Columns gap */
[data-testid="stHorizontalBlock"] { gap: 18px !important; }

/* Hide default streamlit header/footer */
#MainMenu, footer, header { visibility: hidden; }

/* ── PROGRESS BAR ── */
.void-progress-wrap {
    background: rgba(134,59,255,0.08);
    border: 1px solid rgba(134,59,255,0.12);
    border-radius: 10px;
    height: 10px;
    margin: 8px 0;
    overflow: hidden;
}
.void-progress-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Orb decorations (fixed, behind everything) */
.void-orb-1 {
    position: fixed; width: 400px; height: 400px;
    background: rgba(134,59,255,0.12);
    border-radius: 50%; filter: blur(80px);
    top: -100px; left: -100px;
    pointer-events: none; z-index: 0;
    animation: orbFloat 14s ease-in-out infinite;
}
.void-orb-2 {
    position: fixed; width: 350px; height: 350px;
    background: rgba(0,255,133,0.06);
    border-radius: 50%; filter: blur(80px);
    bottom: -80px; right: -80px;
    pointer-events: none; z-index: 0;
    animation: orbFloat 12s ease-in-out infinite reverse;
}
@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%       { transform: translate(24px, -18px) scale(1.04); }
    66%       { transform: translate(-16px, 24px) scale(0.96); }
}
</style>

<div class="void-orb-1"></div>
<div class="void-orb-2"></div>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────────────────────────────

def format_rupees(amount):
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.1f} Cr"
    elif amount >= 100_000:
        return f"₹{amount/100_000:.1f} L"
    else:
        return f"₹{amount:,.0f}"


def calculate_finances(age, salary, expenses, sip, insurance, retire_age):
    years_left      = retire_age - age
    months_left     = years_left * 12
    annual_income   = salary * 12
    annual_expenses = expenses * 12
    monthly_saving  = salary - expenses
    retirement_needed = annual_expenses * 25
    monthly_rate = 0.12 / 12
    if months_left > 0:
        sip_corpus = sip * (((1 + monthly_rate) ** months_left - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        sip_corpus = 0
    retirement_gap   = max(0, retirement_needed - sip_corpus)
    insurance_needed = annual_income * 10
    insurance_gap    = max(0, insurance_needed - insurance)
    if annual_income > 1_500_000:
        tax_rate = 0.30
    elif annual_income > 1_000_000:
        tax_rate = 0.20
    else:
        tax_rate = 0.10
    unused_80c   = 150_000
    tax_saving   = unused_80c * tax_rate
    extra_investable = monthly_saving * 0.30
    return {
        "years_left"       : years_left,
        "months_left"      : months_left,
        "annual_income"    : annual_income,
        "annual_expenses"  : annual_expenses,
        "monthly_saving"   : monthly_saving,
        "retirement_needed": retirement_needed,
        "sip_corpus"       : sip_corpus,
        "retirement_gap"   : retirement_gap,
        "insurance_needed" : insurance_needed,
        "insurance_gap"    : insurance_gap,
        "tax_saving"       : tax_saving,
        "extra_investable" : extra_investable,
    }


def simulate_extra_sip(age, sip, extra, retire_age):
    months       = (retire_age - age) * 12
    total_sip    = sip + extra
    monthly_rate = 0.12 / 12
    if months > 0:
        return total_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    return 0


def ask_gemini(prompt_text):
    if not GEMINI_API_KEY or gemini_model is None:
        return (
            "⚠️ Gemini API key is not configured.\n\n"
            "Set GEMINI_API_KEY in .streamlit/secrets.toml or as an environment variable, then restart."
        )
    try:
        response = gemini_model.generate_content(prompt_text)
        return response.text
    except Exception as error:
        return (
            f"⚠️ Could not get AI response. Error: {str(error)}\n\n"
            f"Model in use: {gemini_model_name}"
        )


def progress_bar_html(current, total, color):
    percent = min(100, (current / total) * 100) if total > 0 else 0
    return f"""
<div class="void-progress-wrap">
    <div class="void-progress-fill" style="width:{percent:.0f}%; background:{color};"></div>
</div>
"""


# ─── SESSION STATE ───────────────────────────────────────────────────────────

for key, default in [
    ("step", 0),
    ("finances", None),
    ("user_input", {}),
    ("gap_analysis_text", None),
    ("behavior_text", None),
    ("action_plan_text", None),
    ("risk_profile", "Medium"),
    ("personality", "The Investor"),
    ("market_chat_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─── STEP 0: LANDING PAGE ────────────────────────────────────────────────────

if st.session_state.step == 0:

    st.html("""
<style>
/* Hide streamlit padding on landing */
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }

/* ── LANDING NAV ── */
.land-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 24px 48px;
    background: linear-gradient(to bottom, rgba(6,0,16,0.95), transparent);
    position: sticky; top: 0; z-index: 100;
}
.land-logo { font-size: 1.1rem; font-weight: 700; letter-spacing: -0.5px; color: var(--hear-green); }
.land-logo span { color: var(--text-muted); font-weight: 300; }
.land-pill {
    background: rgba(134,59,255,0.15);
    border: 1px solid rgba(134,59,255,0.3);
    border-radius: 100px; padding: 8px 20px;
    font-size: 0.78rem; color: var(--void-purple);
    letter-spacing: 1px; text-transform: uppercase;
    font-family: 'DM Mono', monospace;
}

/* ── HERO ── */
.land-hero {
    min-height: 88vh;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 60px 24px 80px;
    position: relative; overflow: hidden;
}
.land-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(134,59,255,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(134,59,255,0.07) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black 30%, transparent 100%);
    animation: gridPulse 8s ease-in-out infinite;
    pointer-events: none;
}
.land-orb-a {
    position: absolute; width: 500px; height: 500px;
    background: rgba(134,59,255,0.18); border-radius: 50%;
    filter: blur(80px); top: -120px; left: -120px;
    animation: orbFloat 12s ease-in-out infinite; pointer-events: none;
}
.land-orb-b {
    position: absolute; width: 400px; height: 400px;
    background: rgba(0,255,133,0.08); border-radius: 50%;
    filter: blur(80px); bottom: -80px; right: -80px;
    animation: orbFloat 14s ease-in-out infinite reverse; pointer-events: none;
}
.land-eyebrow {
    position: relative; z-index: 2;
    display: inline-flex; align-items: center; gap: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; letter-spacing: 2px;
    color: var(--void-purple); text-transform: uppercase;
    margin-bottom: 28px;
    animation: fadeUp 0.8s ease 0.3s both;
}
.land-eyebrow::before, .land-eyebrow::after {
    content: ''; display: block; height: 1px; width: 32px;
    background: var(--void-purple); opacity: 0.5;
}
.land-title {
    position: relative; z-index: 2;
    font-size: clamp(3.5rem, 9vw, 8rem);
    font-weight: 900; line-height: 0.92;
    letter-spacing: -4px; margin-bottom: 32px;
    animation: fadeUp 0.9s ease 0.5s both;
}
.land-title .g { color: var(--hear-green); }
.land-title .p { color: var(--void-purple); }
.land-sub {
    position: relative; z-index: 2;
    font-size: clamp(1rem, 2vw, 1.2rem);
    font-weight: 300; color: var(--text-muted);
    max-width: 560px; line-height: 1.7; margin-bottom: 52px;
    animation: fadeUp 0.8s ease 0.8s both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── TICKER ── */
.land-ticker-wrap {
    border-top: 1px solid rgba(134,59,255,0.15);
    border-bottom: 1px solid rgba(134,59,255,0.15);
    background: rgba(134,59,255,0.04);
    padding: 14px 0; overflow: hidden;
}
.land-ticker {
    display: flex; gap: 0;
    animation: tickerScroll 28s linear infinite;
    white-space: nowrap;
}
.land-ticker-item {
    display: inline-flex; align-items: center; gap: 24px;
    padding: 0 40px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem; letter-spacing: 1px;
    color: var(--text-muted); flex-shrink: 0;
}
.land-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--void-purple); display: inline-block; }
.land-green { color: var(--hear-green); }
@keyframes tickerScroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── STATS ── */
.land-stats {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 2px; padding: 80px 48px;
}
.land-stat {
    padding: 48px 40px;
    border: 1px solid rgba(134,59,255,0.1);
    transition: border-color 0.3s;
}
.land-stat:hover { border-color: rgba(134,59,255,0.4); }
.land-stat-num {
    font-size: 4rem; font-weight: 900;
    letter-spacing: -3px; line-height: 1; margin-bottom: 12px;
    background: linear-gradient(135deg, #fff 30%, rgba(255,255,255,0.4));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.land-stat-num .g { color: var(--hear-green); -webkit-text-fill-color: var(--hear-green); }
.land-stat-label { font-size: 0.85rem; color: var(--text-muted); font-weight: 300; line-height: 1.5; }

/* ── FEATURE CARDS ── */
.land-features { padding: 40px 48px 100px; }
.land-feat-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 60px;
}
.land-feat-title { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800; letter-spacing: -2px; }
.land-feat-title .dim { color: var(--text-dim); }
.land-feat-sub { font-size: 0.9rem; color: var(--text-muted); max-width: 260px; text-align: right; line-height: 1.7; }

.land-card {
    background: rgba(13,0,34,0.7);
    border: 1px solid rgba(134,59,255,0.12);
    border-radius: 20px; padding: 40px 44px;
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 40px; align-items: center;
    margin-bottom: 2px;
    transition: border-color 0.3s;
}
.land-card:hover { border-color: rgba(134,59,255,0.35); }
.land-card-num { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--void-purple); letter-spacing: 2px; margin-bottom: 14px; }
.land-card-title { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 12px; line-height: 1.2; }
.land-card-title .g { color: var(--hear-green); }
.land-card-desc { font-size: 0.88rem; color: var(--text-muted); font-weight: 300; line-height: 1.7; }
.land-card-visual { display: flex; align-items: center; justify-content: center; height: 150px; }

/* ── PROCESS ── */
.land-process { padding: 80px 48px; border-top: 1px solid rgba(134,59,255,0.1); }
.land-process-title { font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 800; letter-spacing: -2px; margin-bottom: 60px; text-align: center; }
.land-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: rgba(134,59,255,0.1); }
.land-step { background: var(--void-dark); padding: 40px 28px; position: relative; }
.land-step::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(to right, var(--void-purple), var(--hear-green));
    transform: scaleX(0); transform-origin: left; transition: transform 0.5s;
}
.land-step:hover::after { transform: scaleX(1); }
.land-step-n { font-family: 'DM Mono', monospace; font-size: 2.2rem; font-weight: 500; color: rgba(134,59,255,0.2); margin-bottom: 16px; }
.land-step-head { font-size: 0.95rem; font-weight: 600; margin-bottom: 8px; }
.land-step-body { font-size: 0.8rem; color: var(--text-muted); line-height: 1.7; font-weight: 300; }

/* ── FINAL CTA SECTION ── */
.land-final {
    padding: 120px 48px; text-align: center; position: relative; overflow: hidden;
}
.land-final::before {
    content: ''; position: absolute;
    width: 600px; height: 600px; border-radius: 50%;
    background: radial-gradient(circle, rgba(134,59,255,0.2) 0%, transparent 70%);
    top: 50%; left: 50%; transform: translate(-50%, -50%);
    pointer-events: none;
}
.land-final-title {
    font-size: clamp(2.5rem, 7vw, 5.5rem);
    font-weight: 900; letter-spacing: -3px; line-height: 0.95; margin-bottom: 28px;
    position: relative; z-index: 2;
}
.land-final-title .outline {
    -webkit-text-stroke: 1.5px rgba(255,255,255,0.25); color: transparent;
}
.land-final-sub { font-size: 1rem; color: var(--text-muted); margin-bottom: 48px; position: relative; z-index: 2; }

/* ── FOOTER ── */
.land-footer {
    padding: 28px 48px;
    border-top: 1px solid rgba(134,59,255,0.1);
    display: flex; justify-content: space-between; align-items: center;
}
.land-footer-logo { font-size: 0.9rem; font-weight: 700; color: var(--text-muted); }
.land-footer-logo em { color: var(--hear-green); font-style: normal; }
.land-footer-note { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: var(--text-dim); letter-spacing: 1px; }

/* CTA button override for landing — centered pill */
.stButton > button {
    width: auto !important;
    padding: 16px 44px !important;
    font-size: 1rem !important;
    border-radius: 100px !important;
    display: block; margin: 0 auto !important;
}
</style>

<div class="land-nav">
    <div class="land-logo">Rupee<span>Mirror</span></div>
    <div class="land-pill">India's Financial Mirror</div>
</div>

<div class="land-hero">
    <div class="land-grid"></div>
    <div class="land-orb-a"></div>
    <div class="land-orb-b"></div>
    <div class="land-eyebrow">AI-powered · Personal Finance · for India</div>
    <div class="land-title">
        See Your<br><span class="g">Financial</span><br><span class="p">Truth.</span>
    </div>
    <div class="land-sub">
        Most Indians think they're doing okay with money.<br>
        RupeeMirror shows you the reality — and exactly how to fix it.
    </div>
</div>
""")

    # The CTA button — Streamlit native so it triggers session state
    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        if st.button("⟶ Start Your Analysis"):
            st.session_state.step = 1
            st.rerun()

    st.html("""
<div class="land-ticker-wrap">
  <div class="land-ticker">
    <span class="land-ticker-item"><span class="land-dot"></span><span>50 Crore+ Indians need a financial plan</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">₹1.5 Crore average retirement gap</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>Free AI financial analysis</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>Built for ET AI Hackathon 2026</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">Behavioral Financial Twin</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>No signup required</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">5 minutes to financial clarity</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>India's most honest finance tool</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>50 Crore+ Indians need a financial plan</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">₹1.5 Crore average retirement gap</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>Free AI financial analysis</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>Built for ET AI Hackathon 2026</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">Behavioral Financial Twin</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>No signup required</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span class="land-green">5 minutes to financial clarity</span></span>
    <span class="land-ticker-item"><span class="land-dot"></span><span>India's most honest finance tool</span></span>
  </div>
</div>

<div class="land-stats">
    <div class="land-stat">
        <div class="land-stat-num"><span class="g">50</span>Cr+</div>
        <div class="land-stat-label">salaried Indians with no clear financial plan</div>
    </div>
    <div class="land-stat">
        <div class="land-stat-num">₹<span class="g">1.5</span>Cr</div>
        <div class="land-stat-label">average retirement gap per Indian household</div>
    </div>
    <div class="land-stat">
        <div class="land-stat-num"><span class="g">5</span>min</div>
        <div class="land-stat-label">to get your complete honest financial picture</div>
    </div>
</div>

<div class="land-features">
    <div class="land-feat-header">
        <div class="land-feat-title">What makes us<br><span class="dim">different</span></div>
        <div class="land-feat-sub">Four honest insights no other Indian finance app gives you</div>
    </div>

    <div class="land-card">
        <div>
            <div class="land-card-num">01 — GAP SHOCK</div>
            <div class="land-card-title">Your <span class="g">retirement gap</span> in seconds</div>
            <div class="land-card-desc">Enter your salary, SIP and age. We show exactly how far you are from your retirement goal — with real Indian math, not optimistic guesses.</div>
        </div>
        <div class="land-card-visual">
            <svg width="160" height="140" viewBox="0 0 160 140">
                <defs>
                    <linearGradient id="ag" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stop-color="#863BFF"/>
                        <stop offset="100%" stop-color="#00ff85"/>
                    </linearGradient>
                </defs>
                <circle cx="80" cy="70" r="55" fill="none" stroke="rgba(134,59,255,0.15)" stroke-width="10"/>
                <circle cx="80" cy="70" r="55" fill="none" stroke="url(#ag)" stroke-width="10" stroke-dasharray="310" stroke-dashoffset="30" stroke-linecap="round" transform="rotate(-90 80 70)"/>
                <text x="80" y="62" text-anchor="middle" fill="#00ff85" font-family="Sora" font-size="22" font-weight="900">94%</text>
                <text x="80" y="82" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-family="DM Mono" font-size="9">on track</text>
            </svg>
        </div>
    </div>

    <div class="land-card">
        <div>
            <div class="land-card-num">02 — WHAT-IF SIMULATOR</div>
            <div class="land-card-title">Live <span class="g">simulation</span> of your future</div>
            <div class="land-card-desc">Move a slider. Watch your retirement corpus change in real time. See how ₹2,000 more per month changes everything over 28 years.</div>
        </div>
        <div class="land-card-visual">
            <svg width="180" height="140" viewBox="0 0 180 140">
                <rect x="10" y="90" width="22" height="40" rx="4" fill="rgba(134,59,255,0.3)"/>
                <rect x="42" y="65" width="22" height="65" rx="4" fill="rgba(134,59,255,0.5)"/>
                <rect x="74" y="45" width="22" height="85" rx="4" fill="rgba(134,59,255,0.7)"/>
                <rect x="106" y="20" width="22" height="110" rx="4" fill="#863BFF"/>
                <rect x="138" y="5"  width="22" height="125" rx="4" fill="#00ff85"/>
                <line x1="5" y1="130" x2="170" y2="130" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <text x="90" y="16" text-anchor="middle" fill="#00ff85" font-family="DM Mono" font-size="9">+₹2K/mo = ₹28L more</text>
            </svg>
        </div>
    </div>

    <div class="land-card">
        <div>
            <div class="land-card-num">03 — BEHAVIORAL TWIN</div>
            <div class="land-card-title">The <span class="g">real you</span> vs the ideal you</div>
            <div class="land-card-desc">Every other app assumes you invest perfectly every month. We model your actual behavior — Diwali spending, panic selling, impulse buys. The truth.</div>
        </div>
        <div class="land-card-visual">
            <svg width="180" height="130" viewBox="0 0 180 130">
                <polyline points="10,100 50,70 90,45 130,25 170,10" fill="none" stroke="rgba(134,59,255,0.4)" stroke-width="2" stroke-dasharray="5 3"/>
                <polyline points="10,100 50,80 70,95 90,72 110,88 130,60 170,38" fill="none" stroke="#00ff85" stroke-width="2.5" stroke-linecap="round"/>
                <circle cx="70" cy="95" r="4" fill="rgba(255,100,100,0.8)"/>
                <circle cx="110" cy="88" r="4" fill="rgba(255,100,100,0.8)"/>
                <text x="68" y="112" text-anchor="middle" fill="rgba(255,100,100,0.6)" font-family="DM Mono" font-size="7">Diwali</text>
                <text x="110" y="104" text-anchor="middle" fill="rgba(255,100,100,0.6)" font-family="DM Mono" font-size="7">Crash</text>
                <line x1="10" y1="120" x2="28" y2="120" stroke="rgba(134,59,255,0.4)" stroke-width="2" stroke-dasharray="5 3"/>
                <text x="32" y="123" fill="rgba(255,255,255,0.3)" font-family="DM Mono" font-size="8">Ideal</text>
                <line x1="65" y1="120" x2="83" y2="120" stroke="#00ff85" stroke-width="2"/>
                <text x="87" y="123" fill="rgba(255,255,255,0.3)" font-family="DM Mono" font-size="8">Real you</text>
            </svg>
        </div>
    </div>

    <div class="land-card">
        <div>
            <div class="land-card-num">04 — ACTION PLAN</div>
            <div class="land-card-title">3 steps to <span class="g">start this week</span></div>
            <div class="land-card-desc">No vague advice. Specific Indian products, real apps, exact rupee amounts — a plan built around your actual behavior and your actual gaps.</div>
        </div>
        <div class="land-card-visual">
            <svg width="160" height="130" viewBox="0 0 160 130">
                <rect x="20" y="10" width="120" height="30" rx="8" fill="rgba(0,255,133,0.08)" stroke="rgba(0,255,133,0.3)" stroke-width="1"/>
                <text x="80" y="29" text-anchor="middle" fill="#00ff85" font-family="DM Mono" font-size="9">Step 1: Start ELSS SIP</text>
                <line x1="80" y1="40" x2="80" y2="52" stroke="rgba(134,59,255,0.4)" stroke-width="1.5" stroke-dasharray="4 3"/>
                <rect x="20" y="52" width="120" height="30" rx="8" fill="rgba(134,59,255,0.08)" stroke="rgba(134,59,255,0.3)" stroke-width="1"/>
                <text x="80" y="71" text-anchor="middle" fill="#863BFF" font-family="DM Mono" font-size="9">Step 2: Term Insurance</text>
                <line x1="80" y1="82" x2="80" y2="94" stroke="rgba(134,59,255,0.4)" stroke-width="1.5" stroke-dasharray="4 3"/>
                <rect x="20" y="94" width="120" height="30" rx="8" fill="rgba(255,170,0,0.08)" stroke="rgba(255,170,0,0.3)" stroke-width="1"/>
                <text x="80" y="113" text-anchor="middle" fill="rgba(255,170,0,0.9)" font-family="DM Mono" font-size="9">Step 3: Claim 80C</text>
            </svg>
        </div>
    </div>
</div>

<div class="land-process">
    <div class="land-process-title">How it works</div>
    <div class="land-steps">
        <div class="land-step"><div class="land-step-n">01</div><div class="land-step-head">Enter your basics</div><div class="land-step-body">Salary, expenses, current SIP, insurance cover, retirement age. Takes under 2 minutes.</div></div>
        <div class="land-step"><div class="land-step-n">02</div><div class="land-step-head">See the gap shock</div><div class="land-step-body">Retirement shortfall, insurance gap, and tax you're overpaying — all calculated instantly.</div></div>
        <div class="land-step"><div class="land-step-n">03</div><div class="land-step-head">Answer 4 questions</div><div class="land-step-body">How you behave during festivals, market crashes, and impulse moments. Your real financial personality.</div></div>
        <div class="land-step"><div class="land-step-n">04</div><div class="land-step-head">Get your plan</div><div class="land-step-body">A 3-step action plan built specifically for you — with real Indian apps and real rupee amounts.</div></div>
    </div>
</div>

<div class="land-final">
    <div class="land-final-title">Start today.<br><span class="outline">It's free.</span></div>
    <div class="land-final-sub">Your financial mirror is ready. No sign-up. No credit card. Just the truth.</div>
</div>
""")

    col_l2, col_c2, col_r2 = st.columns([2, 1, 2])
    with col_c2:
        if st.button("⟶ Open RupeeMirror", key="cta_bottom"):
            st.session_state.step = 1
            st.rerun()

    st.markdown("""
<div class="disclaimer">
    ⚠ RupeeMirror provides educational financial information only — not SEBI-registered advice.<br>
    All projections assume 12% annual SIP returns and are estimates only.<br>
    Consult a certified financial planner before investing.
</div>
""", unsafe_allow_html=True)

    st.html("""
<div class="land-footer">
    <div class="land-footer-logo">Rupee<em>Mirror</em> — Built for Bharat</div>
    <div class="land-footer-note">ET AI HACKATHON 2026 · PS9 · FREE TO USE</div>
</div>
""")

    st.stop()  # Don't render anything below when on landing page


# ─── HERO HEADER (shown on steps 1–4) ────────────────────────────────────────

st.markdown("""
<div class="rupee-hero">
  <div class="rupee-eyebrow">India's Honest Financial Mirror</div>
  <div class="rupee-title">
    <span class="green">Rupee</span><span>Mirror</span>
  </div>
  <div class="rupee-sub">See your true financial future — retirement gaps, insurance blind spots, and the plan that actually fits you.</div>
</div>
<hr>
""", unsafe_allow_html=True)


# ─── STEP 1 ──────────────────────────────────────────────────────────────────

if st.session_state.step >= 1:

    st.markdown('<div class="step-badge">01 — Your Basics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">Tell us about <span class="g">yourself</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        age = st.slider("📅 Your current age", 18, 55, 28)
        salary = st.number_input(
            "💰 Monthly salary (₹)",
            min_value=5_000, max_value=500_000, value=50_000, step=1_000,
        )
        expenses = st.number_input(
            "🧾 Monthly expenses (₹)",
            min_value=1_000, max_value=490_000, value=32_000, step=1_000,
            help="Include rent, food, transport, shopping — everything you spend",
        )

    with col2:
        sip = st.number_input(
            "📈 Monthly SIP / investment (₹)",
            min_value=0, max_value=100_000, value=2_000, step=500,
            help="How much you invest in mutual funds every month. Put 0 if you don't invest yet.",
        )
        insurance = st.number_input(
            "🛡️ Life insurance cover (₹)",
            min_value=0, max_value=50_000_000, value=500_000, step=100_000,
            help="Total amount your family gets if something happens to you.",
        )
        retire_age = st.slider("🏖️ I want to retire at age", 45, 70, 60)

    if expenses >= salary:
        st.markdown(
            '<div class="warn-box">⚠ Your expenses are equal to or more than your salary! Please re-check your numbers.</div>',
            unsafe_allow_html=True,
        )
    else:
        if st.button("⟶ Show My Financial Truth"):
            st.session_state.user_input = {
                "age": age, "salary": salary, "expenses": expenses,
                "sip": sip, "insurance": insurance, "retire_age": retire_age,
            }
            st.session_state.finances = calculate_finances(
                age, salary, expenses, sip, insurance, retire_age
            )
            f = st.session_state.finances
            gap_prompt = f"""
You are RupeeMirror — an honest, friendly financial advisor for everyday Indians.
You have zero products to sell. Your only job is to tell the truth simply.

User's details:
- Age: {age}, wants to retire at: {retire_age}
- Monthly salary: ₹{salary:,}, Monthly expenses: ₹{expenses:,}
- Monthly SIP: ₹{sip:,}, Insurance cover: ₹{insurance:,}
- Years to retirement: {f['years_left']}

Calculated results:
- Retirement corpus needed: ₹{f['retirement_needed']:,.0f}
- SIP will build by retirement: ₹{f['sip_corpus']:,.0f}
- Retirement gap (shortfall): ₹{f['retirement_gap']:,.0f}
- Insurance gap: ₹{f['insurance_gap']:,.0f}
- Possible annual tax saving: ₹{f['tax_saving']:,.0f}

Write a SHORT honest paragraph (under 130 words) that:
1. Tells them clearly if they are on track or in trouble
2. Names the single biggest financial risk they have
3. Ends with ONE encouraging sentence about the smallest change that helps most

Rules you MUST follow:
- Use simple English — imagine explaining to a 20-year-old student
- If you use any financial term, immediately explain it in simple words
- Use ₹ symbol for all money amounts
- Be honest but never scary or discouraging
- Do NOT use bullet points — write in flowing sentences
"""
            with st.spinner("🔮 Analysing your finances..."):
                st.session_state.gap_analysis_text = ask_gemini(gap_prompt)
            st.session_state.step = 2
            st.rerun()


# ─── STEP 2 ──────────────────────────────────────────────────────────────────

if st.session_state.step >= 2 and st.session_state.finances:

    f   = st.session_state.finances
    inp = st.session_state.user_input

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="step-badge">02 — Your Financial Truth</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">What the numbers <span class="p">actually</span> say</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        gap_color = "bad" if f['retirement_gap'] > 0 else "good"
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Retirement Gap</div>
    <div class="metric-number {gap_color}">{format_rupees(f['retirement_gap'])}</div>
    <div style="color:var(--text-dim); font-family:'DM Mono',monospace; font-size:0.72rem; margin-top:8px;">
        Need {format_rupees(f['retirement_needed'])} · SIP builds {format_rupees(f['sip_corpus'])}
    </div>
</div>
        """, unsafe_allow_html=True)

    with c2:
        ins_color = "bad" if f['insurance_gap'] > 1_000_000 else "warn"
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Insurance Gap</div>
    <div class="metric-number {ins_color}">{format_rupees(f['insurance_gap'])}</div>
    <div style="color:var(--text-dim); font-family:'DM Mono',monospace; font-size:0.72rem; margin-top:8px;">
        Family needs {format_rupees(f['insurance_needed'])} cover
    </div>
</div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Tax Overpaid / yr</div>
    <div class="metric-number warn">{format_rupees(f['tax_saving'])}</div>
    <div style="color:var(--text-dim); font-family:'DM Mono',monospace; font-size:0.72rem; margin-top:8px;">
        Possible via Section 80C deductions
    </div>
</div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    retirement_pct = (f['sip_corpus'] / f['retirement_needed'] * 100) if f['retirement_needed'] > 0 else 0
    st.markdown(f"<span style='font-family:DM Mono,monospace;font-size:0.78rem;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;'>Retirement Progress</span>", unsafe_allow_html=True)
    st.markdown(progress_bar_html(f['sip_corpus'], f['retirement_needed'], "#863BFF"), unsafe_allow_html=True)
    st.caption(f"On track for {retirement_pct:.0f}% of your retirement goal")

    insurance_pct = (inp['insurance'] / f['insurance_needed'] * 100) if f['insurance_needed'] > 0 else 0
    st.markdown(f"<span style='font-family:DM Mono,monospace;font-size:0.78rem;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;'>Insurance Coverage</span>", unsafe_allow_html=True)
    st.markdown(progress_bar_html(inp['insurance'], f['insurance_needed'], "#ffaa00"), unsafe_allow_html=True)
    st.caption(f"Family is {insurance_pct:.0f}% protected of what they need")

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="ai-card">
    <div class="ai-card-title">✦ RupeeMirror's honest assessment</div>
    {st.session_state.gap_analysis_text}
</div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">The <span class="g">What-If</span> Simulator</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:var(--text-muted);font-size:0.9rem;'>Move the slider to see what happens if you invest a little more each month ↓</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    max_extra = max(int(f['extra_investable'] * 3), 10_000)
    extra_sip = st.slider(
        "Extra monthly investment (₹)",
        min_value=0, max_value=max_extra, value=0, step=500,
        help="ON TOP of your current SIP. See how small additions change everything!",
    )

    new_corpus    = simulate_extra_sip(inp['age'], inp['sip'], extra_sip, inp['retire_age'])
    new_gap       = max(0, f['retirement_needed'] - new_corpus)
    gap_reduction = f['retirement_gap'] - new_gap

    wc1, wc2 = st.columns(2)
    with wc1:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">New Retirement Corpus</div>
    <div class="metric-number good">{format_rupees(new_corpus)}</div>
</div>
        """, unsafe_allow_html=True)
    with wc2:
        remaining_color = "bad" if new_gap > 0 else "good"
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Remaining Gap</div>
    <div class="metric-number {remaining_color}">{format_rupees(new_gap)}</div>
    <div style="color:var(--hear-green); font-family:'DM Mono',monospace; font-size:0.78rem; margin-top:8px;">
        Gap closed: {format_rupees(gap_reduction)} ✓
    </div>
</div>
        """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    if st.session_state.step == 2:
        if st.button("⟶ Analyse My Real Behavior"):
            st.session_state.step = 3
            st.rerun()


# ─── STEP 3 ──────────────────────────────────────────────────────────────────

if st.session_state.step >= 3:

    st.markdown('<div class="step-badge">03 — Money Behavior</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">How do you <span class="p">actually</span> behave with money?</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:var(--text-muted);font-size:0.88rem;font-style:italic;'>Be honest — this is what makes RupeeMirror different from every other app.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)

    with bc1:
        festival = st.radio(
            "🪔 Do you reduce/skip SIP during festivals like Diwali?",
            ["Never — I'm disciplined", "Sometimes (once or twice a year)", "Almost always"],
        )
        crash_reaction = st.radio(
            "📉 If stock market drops 30% tomorrow, what do you do?",
            ["Panic and sell everything", "Stay calm and hold", "Buy more — it's a sale!"],
        )

    with bc2:
        impulse = st.radio(
            "🛍️ How often do you make big unplanned purchases?",
            ["Rarely — I plan my spending", "Sometimes (once a month)", "Often — I shop impulsively"],
        )
        paused = st.radio(
            "⏸️ Have you ever stopped an investment midway before?",
            ["No, never stopped", "Yes, once or twice", "Yes, multiple times"],
        )

    if st.session_state.step == 3:
        if st.button("⟶ Show My Behavioral Financial Twin"):

            f   = st.session_state.finances
            inp = st.session_state.user_input

            behavior_prompt = f"""
You are RupeeMirror. Analyse this person's real money behavior and give honest feedback.

Their ideal financial plan (assuming perfect behavior):
- Monthly SIP: ₹{inp['sip']:,} for {f['years_left']} years
- Would build: ₹{f['sip_corpus']:,.0f} by retirement

Their actual behavior:
- Festival SIP skipping: {festival}
- Market crash reaction: {crash_reaction}
- Impulse spending: {impulse}
- History of stopping investments: {paused}

Write a response with EXACTLY these 4 parts (under 160 words total):

1. "YOUR MONEY PERSONALITY TYPE:" — Give them a fun, specific name like "The Festival Splurger", "The Panic Seller", "The Disciplined Saver", "The Impulse Buyer". One short sentence explaining it.

2. "THE REAL IMPACT:" — Estimate how much less they will actually build vs the ideal ₹{f['sip_corpus']:,.0f}. Be specific with a ₹ number estimate. Explain why.

3. "YOUR BLIND SPOT:" — ONE brutally honest sentence about their biggest money weakness.

4. "THE 1% FIX:" — ONE tiny habit change (takes less than 5 minutes to set up) that fixes 80% of their problem.

5. "RISK_PROFILE: [Low/Medium/High]" — Choose their risk tolerance based on their answers. Must use EXACT format, e.g., RISK_PROFILE: High

Tone: Like a caring, honest best friend. Never preachy. Never scary. Simple English only.
"""

            action_prompt = f"""
You are RupeeMirror. Give this person a SPECIFIC 3-step action plan they can start THIS WEEK.

Their gaps:
- Retirement shortfall: {format_rupees(f['retirement_gap'])}
- Insurance gap: {format_rupees(f['insurance_gap'])}
- Tax saving opportunity: {format_rupees(f['tax_saving'])} per year
- Extra they can invest per month: approximately {format_rupees(f['extra_investable'])}

Their behavior:
- {festival} (festival spending)
- {crash_reaction} (during market crashes)
- {impulse} (impulse shopping)
- {paused} (stopped investments before)

Write EXACTLY 3 steps. Format each as:
Step X: [SHORT TITLE IN CAPS] — [2 sentences: what to do + where/how to do it in India]

Rules:
- Each step must be doable THIS WEEK (not someday)
- Mention real Indian apps/platforms: Groww, Zerodha, PolicyBazaar, ClearTax, HDFC Life, etc.
- Each step must fit within their ₹{f['extra_investable']:,.0f}/month budget
- Account for their behavioral weakness in the plan
- Keep each step under 40 words

End with one line: "Your first step takes less than 10 minutes. Start today."
"""

            with st.spinner("🧠 Building your behavioral financial twin..."):
                behavior_text_raw = ask_gemini(behavior_prompt)
                st.session_state.action_plan_text = ask_gemini(action_prompt)

                import re
                risk_match = re.search(r"RISK_PROFILE:\s*(Low|Medium|High)", behavior_text_raw, re.IGNORECASE)
                if risk_match:
                    st.session_state.risk_profile = risk_match.group(1).capitalize()
                
                try:
                    pers_line = [l for l in behavior_text_raw.split('\n') if 'PERSONALITY' in l.upper()][0]
                    pers_name = re.sub(r'[^a-zA-Z\s]', '', pers_line.split(':')[1] if ':' in pers_line else pers_line).strip()
                    st.session_state.personality = pers_name if pers_name else "The Investor"
                except Exception:
                    st.session_state.personality = "The Investor"
                
                clean_behavior = re.sub(r"5\.\s*\"?RISK_PROFILE.*", "", behavior_text_raw, flags=re.IGNORECASE|re.DOTALL)
                st.session_state.behavior_text = clean_behavior.strip()

            st.session_state.step = 4
            st.rerun()


# ─── STEP 4 ──────────────────────────────────────────────────────────────────

if st.session_state.step >= 4:

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="step-badge">04 — Your Financial Twin</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">The <span class="g">Real You</span> vs the Ideal You</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="behavior-card">
    <div class="ai-card-title" style="color:var(--gold);">✦ Your behavioral money personality</div>
    {st.session_state.behavior_text}
</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-head" style="margin-top:24px;">3 steps to <span class="g">start this week</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="action-card">
    <div class="ai-card-title" style="color:var(--hear-green);">✦ Start this week — not someday</div>
    {st.session_state.action_plan_text}
</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c4_1, c4_2 = st.columns(2)
    with c4_1:
        if st.button("⟶ Explore Market AI for My Profile"):
            st.session_state.step = 5
            st.rerun()
    with c4_2:
        if st.button("↺ Start Over — Analyse a New Profile"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ─── STEP 5: MARKET INTELLIGENCE (PS6) ───────────────────────────────────────

if st.session_state.step >= 5:

    user_risk = st.session_state.risk_profile
    user_personality = st.session_state.personality

    badge_color = "var(--hear-green)" if user_risk == "Low" else ("var(--gold)" if user_risk == "Medium" else "var(--red-bad)")

    st.markdown(f"""
    <style>
    /* Glow effect on hover */
    .market-card-glow {{
        transition: all 0.3s ease;
    }}
    .market-card-glow:hover {{
        box-shadow: 0 0 20px rgba(134,59,255,0.4), inset 0 0 10px rgba(134,59,255,0.1);
        transform: translateY(-2px);
    }}
    /* Risk Badge */
    .risk-badge {{
        display: inline-block;
        background: {badge_color}; color: #000;
        padding: 4px 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);
        font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 700;
        box-shadow: 0 0 10px {badge_color}; margin-left: auto;
    }}
    /* Progress bar override for cards */
    .conf-bar-wrap {{
        width: 100%; height: 4px; border-radius: 2px; margin-top: 4px;
        background: rgba(134,59,255,0.1); overflow: hidden;
    }}
    .conf-bar-fill {{
        height: 100%; border-radius: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="step-badge">05 — Market Intelligence</div>', unsafe_allow_html=True)
    
    col_hd1, col_hd2 = st.columns([3,1])
    with col_hd1:
        st.markdown(f'<div class="section-head">Opportunities for <span class="p">The Real You</span></div>', unsafe_allow_html=True)
    with col_hd2:
        st.markdown(f'<div style="text-align:right; margin-top: 24px;"><div class="risk-badge">{user_risk.upper()} RISK</div></div>', unsafe_allow_html=True)
        
    st.markdown(f"<span style='color:var(--text-muted);font-size:0.95rem;'>Because your risk profile is <b>{user_risk}</b> (and you act like <i>{user_personality}</i>), we filtered out unsuitable noise.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    all_stocks = [
        {"symbol": "TCS", "reason": "Breakout after 3-month resistance + strong US deal wins.", "confidence": 78, "risk": "Low", "success_rate": "72%", "sim_best": 11800, "sim_worst": 9600, "sim_likely": 10900},
        {"symbol": "RELIANCE", "reason": "Positive FII flow sentiment + telecom tariff hike.", "confidence": 74, "risk": "Medium", "success_rate": "68%", "sim_best": 12100, "sim_worst": 9400, "sim_likely": 11100},
        {"symbol": "ZOMATO", "reason": "Volume spike on quick-commerce expansion news.", "confidence": 82, "risk": "High", "success_rate": "61%", "sim_best": 13500, "sim_worst": 7500, "sim_likely": 11400},
        {"symbol": "HDFC BANK", "reason": "Undervalued RSI reversing + strong credit growth.", "confidence": 85, "risk": "Low", "success_rate": "76%", "sim_best": 11500, "sim_worst": 9800, "sim_likely": 10800},
        {"symbol": "SUZLON", "reason": "Momentum play on renewable energy order book.", "confidence": 65, "risk": "High", "success_rate": "42%", "sim_best": 14500, "sim_worst": 5500, "sim_likely": 10200}
    ]
    
    if user_risk == "Low":
        suitable_stocks = [s for s in all_stocks if s["risk"] == "Low"]
        rejected_stocks = [s for s in all_stocks if s["risk"] != "Low"]
    elif user_risk == "Medium":
        suitable_stocks = [s for s in all_stocks if s["risk"] in ["Low", "Medium"]]
        rejected_stocks = [s for s in all_stocks if s["risk"] == "High"]
    else:
        suitable_stocks = all_stocks
        rejected_stocks = []
    
    st.markdown('<div class="section-head" style="font-size: 1.2rem;">🎯 Opportunity Radar</div>', unsafe_allow_html=True)
    
    disp_stocks = suitable_stocks[:3] if len(suitable_stocks) >= 3 else suitable_stocks
    cols = st.columns(len(disp_stocks))
    for i, stock in enumerate(disp_stocks):
        with cols[i]:
            st.markdown(f'''
            <div class="metric-card market-card-glow" style="text-align: left; padding: 18px 14px;">
                <div style="font-family:'DM Mono',monospace;color:var(--void-purple);font-size:0.75rem;">Confidence: {stock["confidence"]}%
                    <div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{stock["confidence"]}%; background:var(--void-purple);"></div></div>
                </div>
                <div style="font-family:'Sora',sans-serif;font-size:1.3rem;font-weight:800;margin:6px 0;">{stock["symbol"]}</div>
                <div style="color:var(--text-muted);font-size:0.85rem;line-height:1.5;height:55px;">{stock["reason"]}</div>
                <div style="margin-top:12px;font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--hear-green);">
                    Pattern Success Rate: {stock["success_rate"]}
                    <div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{stock["success_rate"].replace('%','')}; background:var(--hear-green);"></div></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            with st.expander(f"Deep Analysis: {stock['symbol']}"):
                
                # Behavioral Warning Layer
                if user_risk == "Low" and stock["risk"] != "Low":
                    st.markdown(f"**⚠️ Behavioral Warning:** Because you are *{user_personality}*, this stock may trigger panic selling during short-term dips. **Suggested action:** SIP instead of lump sum.", unsafe_allow_html=True)
                elif "Panic" in user_personality and stock["risk"] == "Medium":
                    st.markdown(f"**⚠️ Behavioral Warning:** This medium-volatility stock may test your *{user_personality}* tendencies during corrections. **Suggested:** Set strict GTT triggers to remove emotion.", unsafe_allow_html=True)
                
                # Mini Simulation
                st.markdown(f"<span style='color:var(--hear-green);font-size:0.9rem;font-weight:600;'>Mini Simulation (₹10,000 Invested)</span>", unsafe_allow_html=True)
                sim_col1, sim_col2, sim_col3 = st.columns(3)
                sim_col1.metric("Best Case", f"₹{stock['sim_best']}")
                sim_col2.metric("Most Likely", f"₹{stock['sim_likely']}")
                sim_col3.metric("Worst Case", f"₹{stock['sim_worst']}")
                
                # Selling insight
                if "Panic" in user_personality:
                    st.caption(f"*Behavior Insight: You are highly likely to panic sell at ₹{(stock['sim_worst']+10000)/2:,.0f} due to your tendency.*")
                elif "Impulse" in user_personality:
                    st.caption(f"*Behavior Insight: You might withdraw this early to fund an impulse purchase before reaching ₹{stock['sim_best']}.*")
                elif "Festival" in user_personality:
                    st.caption(f"*Behavior Insight: Do not skip SIPs on this stock during Diwali to reach the best-case target!*")
                else:
                    st.caption(f"*Behavior Insight: Staying strictly disciplined helps you achieve the ₹{stock['sim_likely']} likely scenario.*")
                
                # WHY NOT
                st.markdown("---")
                st.markdown("**🧠 Why Not Others?**")
                if len(rejected_stocks) > 0:
                    for rej in rejected_stocks[:2]:
                        reason_rej = "Too volatile for your low-risk profile." if rej['risk']=="High" else "Does not match your strict behavioral parameters."
                        st.markdown(f"- **{rej['symbol']}**: {reason_rej}")
                else:
                    st.markdown("- *Your high-risk behavioral profile allows you to view all pattern opportunities.*")

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<div class="section-head">Market <span class="g">GPT</span></div>', unsafe_allow_html=True)
    st.markdown("<span style='color:var(--text-muted);font-size:0.85rem;'>Ask about stocks, your retirement gap, or how these opportunities fit your plan.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    for msg in st.session_state.market_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask Market GPT..."):
        st.session_state.market_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            f = st.session_state.finances
            system_prompt = f"""
            You are Market GPT, part of RupeeMirror.
            The user has a retirement gap of ₹{f['retirement_gap']:,.0f}.
            Their specific behavioral personality is: {user_personality}.
            Their strict risk profile is: {user_risk}.
            
            Answer their query: "{prompt}"
            
            You MUST deeply personalize your response to their behavior. 
            For example: "Since you’re a {user_risk}-risk investor who acts like a {user_personality}, [stock/plan] is suitable because it won't trigger emotional exits and helps close your ₹{f['retirement_gap']:,.0f} gap." 
            Keep it under 100 words. Be empathetic but financially smart.
            """
            with st.spinner("Analysing market..."):
                response = ask_gemini(system_prompt)
                st.markdown(response)
                st.session_state.market_chat_history.append({"role": "assistant", "content": response})

# ─── DISCLAIMER ──────────────────────────────────────────────────────────────

st.markdown("""
<div class="disclaimer">
    ⚠ RupeeMirror provides educational financial information only — not SEBI-registered advice.<br>
    All projections assume 12% annual SIP returns and are estimates only.<br>
    Consult a certified financial planner before investing.
</div>
""", unsafe_allow_html=True)