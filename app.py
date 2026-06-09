import streamlit as st
import pandas as pd
import numpy as np
import gdown
import os
import importlib.util

st.set_page_config(
    page_title="BacktestPro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1220 50%, #0a0e1a 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #111827 100%);
    border-right: 1px solid #1e2d45;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Header */
.main-header {
    background: linear-gradient(90deg, #0d1220 0%, #1a2744 50%, #0d1220 100%);
    border-bottom: 1px solid #1e3a5f;
    padding: 1.2rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.main-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-header .subtitle {
    font-size: 0.75rem;
    color: #4a6080;
    font-family: 'JetBrains Mono', monospace;
    margin: 0;
}

/* Stat cards */
.stat-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}

.stat-card:hover { border-color: #2d4a6e; }

.stat-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: #4a6080;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.3rem;
}

.stat-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
}

.stat-value.positive { color: #34d399; }
.stat-value.negative { color: #f87171; }
.stat-value.neutral  { color: #38bdf8; }

/* Section headers */
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e2d45;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #2563eb, #6366f1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(79,70,229,0.4) !important;
}

/* Inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: #111827 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #111827 !important;
    border: 1px dashed #1e3a5f !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
}

/* Strategy badge */
.strategy-badge {
    background: linear-gradient(90deg, #064e3b, #065f46);
    border: 1px solid #059669;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #34d399;
}

/* Trade table */
.trade-row-win  { color: #34d399 !important; }
.trade-row-loss { color: #f87171 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 2px; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Metric override */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 1rem;
}

[data-testid="stMetricLabel"] { color: #4a6080 !important; font-size: 0.7rem !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-family: 'JetBrains Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──
FOLDER_ID  = "1RrmGgHKF5mLDRg-eFmU6SEO4N8sYJtx2"
DATA_DIR   = "data"
TIMEFRAMES = ["M1","M5","M15","M30","H1","H4","D1"]

# ── HEADER ──
st.markdown("""
<div class="main-header">
    <div>
        <h1>📊 BacktestPro</h1>
        <p class="subtitle">XAUUSD · Offline Backtesting Engine · v1.0</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── DATA FUNCTIONS ──
@st.cache_data(show_spinner="⏳ Mengunduh data dari Google Drive...")
def download_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    for tf in TIMEFRAMES:
        if not os.path.exists(os.path.join(DATA_DIR, f"XAUUSDm_{tf}.csv")):
            url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
            gdown.download_folder(url, output=DATA_DIR, quiet=True, use_cookies=False)
            break

def load_csv(tf):
    path = os.path.join(DATA_DIR, f"XAUUSDm_{tf}.csv")
    if not os.path.exists(path): return None
    df = pd.read_csv(path, parse_dates=["time"])
    return df.sort_values("time").reset_index(drop=True)

def load_strategy(file):
    tmp = f"/tmp/{file.name}"
    with open(tmp, "wb") as f: f.write(file.read())
    spec = importlib.util.spec_from_file_location("strategy", tmp)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run_backtest(df, mod, params, initial_balance):
    try:
        trades = mod.run(df, params)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None, None
    if not trades: return [], pd.DataFrame()
    trade_df = pd.DataFrame(trades)
    bal = initial_balance
    equity = [bal]
    for _, t in trade_df.iterrows():
        bal += t.get("pnl", 0)
        equity.append(bal)
    return equity, trade_df

def calc_stats(equity, trade_df, initial_balance):
    if trade_df.empty: return {}
    total = len(trade_df)
    wins  = len(trade_df[trade_df["pnl"] > 0])
    loss  = total - wins
    wr    = wins / total * 100
    gp    = trade_df[trade_df["pnl"] > 0]["pnl"].sum()
    gl    = abs(trade_df[trade_df["pnl"] <= 0]["pnl"].sum())
    pf    = gp / gl if gl > 0 else 0
    net   = trade_df["pnl"].sum()
    peak  = max(equity)
    dd    = max([peak - e for e in equity if e < peak], default=0)
    dd_pct = dd / peak * 100 if peak > 0 else 0
    ret_pct = net / initial_balance * 100
    return {
        "Total Trades":   (total,   "neutral"),
        "Win Rate":       (f"{wr:.1f}%", "positive" if wr >= 50 else "negative"),
        "Win / Loss":     (f"{wins} / {loss}", "neutral"),
        "Net Profit":     (f"${net:,.2f}", "positive" if net > 0 else "negative"),
        "Return":         (f"{ret_pct:.1f}%", "positive" if ret_pct > 0 else "negative"),
        "Profit Factor":  (f"{pf:.2f}", "positive" if pf >= 1 else "negative"),
        "Gross Profit":   (f"${gp:,.2f}", "positive"),
        "Gross Loss":     (f"${gl:,.2f}", "negative"),
        "Max Drawdown":   (f"${dd:,.2f} ({dd_pct:.1f}%)", "negative" if dd > 0 else "neutral"),
        "Final Balance":  (f"${equity[-1]:,.2f}", "positive" if equity[-1] > initial_balance else "negative"),
    }

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div class="section-title">Strategy</div>', unsafe_allow_html=True)
    strat_file = st.file_uploader("Upload .py", type=["py"], label_visibility="collapsed")

    strategy_mod = None
    params = {}

    if strat_file:
        try:
            strategy_mod = load_strategy(strat_file)
            st.markdown(f"""
            <div class="strategy-badge">
                ✅ {strategy_mod.NAME}<br>
                <span style="color:#6ee7b7;font-size:0.7rem">v{strategy_mod.VERSION}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-title">Parameters</div>', unsafe_allow_html=True)
            for key, meta in strategy_mod.PARAMS.items():
                if meta["type"] == "int":
                    params[key] = st.number_input(meta["label"], value=int(meta["default"]), step=1)
                elif meta["type"] == "float":
                    params[key] = st.number_input(meta["label"], value=float(meta["default"]), step=0.01, format="%.2f")
                elif meta["type"] == "bool":
                    params[key] = st.checkbox(meta["label"], value=meta["default"])
        except Exception as e:
            st.error(f"Gagal load: {e}")

    st.markdown('<div class="section-title">Data</div>', unsafe_allow_html=True)
    tf         = st.selectbox("Timeframe", TIMEFRAMES, index=2)
    date_from  = st.date_input("Dari", value=pd.Timestamp("2024-01-01"))
    date_to    = st.date_input("Sampai", value=pd.Timestamp("2024-06-30"))

    st.markdown('<div class="section-title">Capital</div>', unsafe_allow_html=True)
    initial_balance = st.number_input("Initial Balance ($)", value=5000, step=100)

    # % dari balance
    bal_pct = st.selectbox("Risk per Trade (% Balance)",
        ["Custom", "1%", "2%", "5%", "10%", "20%", "50%"])
    if bal_pct != "Custom":
        pct_val = float(bal_pct.replace("%","")) / 100
        st.info(f"💡 {bal_pct} dari ${initial_balance:,} = **${initial_balance * pct_val:,.0f}**")

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🚀 JALANKAN BACKTEST")

# ── MAIN AREA ──
if not run_btn:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #2d4a6e;">
        <div style="font-size:4rem; margin-bottom:1rem">📊</div>
        <div style="font-size:1.1rem; color:#38bdf8; font-weight:600; margin-bottom:0.5rem">
            Siap untuk backtest
        </div>
        <div style="font-size:0.85rem; color:#2d4a6e">
            Upload strategy → Atur parameter → Klik Jalankan
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    if not strategy_mod:
        st.warning("⚠️ Upload strategy dulu!")
    else:
        with st.spinner("⚡ Running backtest..."):
            download_data()
            df = load_csv(tf)

        if df is None:
            st.error(f"❌ Data {tf} tidak ditemukan!")
        else:
            df = df[(df["time"] >= pd.Timestamp(date_from)) &
                    (df["time"] <= pd.Timestamp(date_to))]

            equity, trade_df = run_backtest(df, strategy_mod, params, initial_balance)

            if equity and not trade_df.empty:
                stats = calc_stats(equity, trade_df, initial_balance)

                # Stats grid
                st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
                cols = st.columns(5)
                for i, (label, (val, cls)) in enumerate(stats.items()):
                    with cols[i % 5]:
                        color = "#34d399" if cls == "positive" else "#f87171" if cls == "negative" else "#38bdf8"
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-label">{label}</div>
                            <div class="stat-value" style="color:{color}">{val}</div>
                        </div>""", unsafe_allow_html=True)

                # Equity curve
                st.markdown('<div class="section-title">Equity Curve</div>', unsafe_allow_html=True)
                eq_df = pd.DataFrame({"Equity": equity})
                st.line_chart(eq_df, color="#38bdf8", height=280)

                # Trade list
                st.markdown('<div class="section-title">Trade List</div>', unsafe_allow_html=True)
                display_df = trade_df.copy()
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=350,
                    hide_index=True
                )

                # Download hasil
                csv = trade_df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Trade List (CSV)",
                    csv,
                    f"backtest_{tf}_{date_from}_{date_to}.csv",
                    "text/csv"
                )
            else:
                st.markdown("""
                <div style="text-align:center; padding:3rem; color:#4a6080">
                    <div style="font-size:2rem">🔍</div>
                    <div>Tidak ada trade pada periode ini</div>
                </div>""", unsafe_allow_html=True)
