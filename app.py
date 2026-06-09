import streamlit as st
import pandas as pd
import numpy as np
import gdown
import os
import importlib.util

st.set_page_config(
    page_title="BacktestPro",
    page_icon="📊",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0f1117; }

.app-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.app-sub {
    font-size: 0.75rem;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 2rem;
}

.divider {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 1.5rem 0;
}

.section-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.6rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.7rem;
    margin-bottom: 1rem;
}

.stat-box {
    background: #1e293b;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    border: 1px solid #263548;
}

.stat-box .lbl {
    font-size: 0.62rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stat-box .val {
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.2rem;
}

.positive { color: #34d399; }
.negative { color: #f87171; }
.neutral  { color: #38bdf8; }

.strat-badge {
    background: #0f2720;
    border: 1px solid #065f46;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #34d399;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    margin-bottom: 1rem;
}

.stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stFileUploader"] {
    border: 1px dashed #1e3a5f !important;
    border-radius: 10px !important;
    background: #111827 !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──
FOLDER_ID  = "1RrmGgHKF5mLDRg-eFmU6SEO4N8sYJtx2"
DATA_DIR   = "data"
TIMEFRAMES = ["M1","M5","M15","M30","H1","H4","D1"]

# ── FUNCTIONS ──
@st.cache_data(show_spinner="Mengunduh data...")
def download_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    for tf in TIMEFRAMES:
        if not os.path.exists(os.path.join(DATA_DIR, f"XAUUSDm_{tf}.csv")):
            gdown.download_folder(
                f"https://drive.google.com/drive/folders/{FOLDER_ID}",
                output=DATA_DIR, quiet=True, use_cookies=False)
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
        st.error(f"Error: {e}")
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
    dd_pct   = dd / peak * 100 if peak > 0 else 0
    ret_pct  = net / initial_balance * 100
    return {
        "Total Trades":  (str(total),              "neutral"),
        "Win Rate":      (f"{wr:.1f}%",             "positive" if wr >= 50 else "negative"),
        "Win / Loss":    (f"{wins} / {loss}",       "neutral"),
        "Net Profit":    (f"${net:,.2f}",           "positive" if net > 0 else "negative"),
        "Return":        (f"{ret_pct:.1f}%",        "positive" if ret_pct > 0 else "negative"),
        "Profit Factor": (f"{pf:.2f}",              "positive" if pf >= 1 else "negative"),
        "Gross Profit":  (f"${gp:,.2f}",            "positive"),
        "Gross Loss":    (f"${gl:,.2f}",            "negative"),
        "Max Drawdown":  (f"${dd:,.2f} ({dd_pct:.1f}%)", "negative" if dd > 0 else "neutral"),
        "Final Balance": (f"${equity[-1]:,.2f}",    "positive" if equity[-1] > initial_balance else "negative"),
    }

# ── UI ──
st.markdown('<div class="app-title">📊 BacktestPro</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">XAUUSD · Offline Engine · v1.0</div>', unsafe_allow_html=True)

# STRATEGY
st.markdown('<div class="section-label">Strategy</div>', unsafe_allow_html=True)
strat_file   = st.file_uploader("Upload file .py", type=["py"])
strategy_mod = None
params       = {}

if strat_file:
    try:
        strategy_mod = load_strategy(strat_file)
        st.markdown(f'<div class="strat-badge">✅ {strategy_mod.NAME} &nbsp;·&nbsp; v{strategy_mod.VERSION}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-label">Parameters</div>', unsafe_allow_html=True)
        for key, meta in strategy_mod.PARAMS.items():
            if meta["type"] == "int":
                params[key] = st.number_input(meta["label"], value=int(meta["default"]), step=1)
            elif meta["type"] == "float":
                params[key] = st.number_input(meta["label"], value=float(meta["default"]),
                                               step=0.01, format="%.2f")
            elif meta["type"] == "bool":
                params[key] = st.checkbox(meta["label"], value=meta["default"])
    except Exception as e:
        st.error(f"Gagal load strategy: {e}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# DATA SETTINGS
st.markdown('<div class="section-label">Data</div>', unsafe_allow_html=True)
tf        = st.selectbox("Timeframe", TIMEFRAMES, index=2)
col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("Dari", value=pd.Timestamp("2024-01-01"))
with col2:
    date_to   = st.date_input("Sampai", value=pd.Timestamp("2024-06-30"))

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# CAPITAL
st.markdown('<div class="section-label">Capital</div>', unsafe_allow_html=True)
initial_balance = st.number_input("Initial Balance ($)", value=5000, step=100)

pct_options = ["—", "1%", "2%", "5%", "10%", "20%", "50%"]
bal_pct = st.selectbox("Lihat % dari Balance", pct_options)
if bal_pct != "—":
    pct_val = float(bal_pct.replace("%", "")) / 100
    amount  = initial_balance * pct_val
    st.info(f"**{bal_pct}** dari ${initial_balance:,} = **${amount:,.0f}**")

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("🚀 Jalankan Backtest")

# RESULTS
if run_btn:
    if not strategy_mod:
        st.warning("⚠️ Upload strategy dulu!")
    else:
        with st.spinner("⚡ Running..."):
            download_data()
            df = load_csv(tf)

        if df is None:
            st.error(f"Data {tf} tidak ditemukan!")
        else:
            df = df[(df["time"] >= pd.Timestamp(date_from)) &
                    (df["time"] <= pd.Timestamp(date_to))]
            equity, trade_df = run_backtest(df, strategy_mod, params, initial_balance)

            if equity and not trade_df.empty:
                stats = calc_stats(equity, trade_df, initial_balance)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)

                items = list(stats.items())
                html = '<div class="stat-grid">'
                for label, (val, cls) in items:
                    html += f"""
                    <div class="stat-box">
                        <div class="lbl">{label}</div>
                        <div class="val {cls}">{val}</div>
                    </div>"""
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

                st.markdown('<div class="section-label">Equity Curve</div>', unsafe_allow_html=True)
                st.line_chart(pd.DataFrame({"Equity ($)": equity}), color="#38bdf8", height=250)

                st.markdown('<div class="section-label">Trade List</div>', unsafe_allow_html=True)
                st.dataframe(trade_df, use_container_width=True, hide_index=True, height=300)

                csv = trade_df.to_csv(index=False)
                st.download_button("⬇️ Download Trade List", csv,
                    f"backtest_{tf}_{date_from}_{date_to}.csv", "text/csv")
            else:
                st.info("Tidak ada trade pada periode ini.")
