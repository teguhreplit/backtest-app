import streamlit as st
import pandas as pd
import numpy as np
import gdown
import os
import importlib.util

st.set_page_config(page_title="BacktestPro", page_icon="📊", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif !important; box-sizing: border-box; }

.stApp { background: #080c14 !important; }

/* Top bar */
.topbar {
    background: linear-gradient(90deg, #0d1526, #111d35);
    border-bottom: 1px solid #1a2d4a;
    padding: 1rem 0;
    margin-bottom: 2rem;
}
.topbar-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
}
.topbar-title span { color: #3b82f6; }
.topbar-sub {
    font-size: 0.72rem;
    color: #3b5270;
    font-family: 'JetBrains Mono', monospace !important;
    margin-top: 2px;
}

/* Cards */
.card {
    background: #0d1526;
    border: 1px solid #1a2d4a;
    border-radius: 14px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 0.65rem;
    font-weight: 700;
    color: #3b82f6;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.card-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #3b82f6;
    border-radius: 2px;
}

/* Strategy loaded badge */
.strat-loaded {
    background: #071a12;
    border: 1px solid #166534;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 0.5rem;
}
.strat-dot {
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    flex-shrink: 0;
}
.strat-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #22c55e;
}
.strat-ver {
    font-size: 0.7rem;
    color: #166534;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Param inputs label */
label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stCheckbox label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    letter-spacing: 0.2px !important;
}

/* Input fields */
input, [data-baseweb="input"] input,
[data-baseweb="select"] div {
    background: #111d35 !important;
    border: 1px solid #1e3452 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-size: 0.9rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Run button */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.75rem 1rem !important;
    letter-spacing: 0.5px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(59,130,246,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Stats */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 1rem;
}
.stat-tile {
    background: #0d1526;
    border: 1px solid #1a2d4a;
    border-radius: 12px;
    padding: 1rem;
    position: relative;
    overflow: hidden;
}
.stat-tile::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 12px 0 0 12px;
}
.stat-tile.pos::after { background: #22c55e; }
.stat-tile.neg::after { background: #ef4444; }
.stat-tile.neu::after { background: #3b82f6; }

.stat-tile .lbl {
    font-size: 0.62rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
}
.stat-tile .val {
    font-size: 1.3rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace !important;
    line-height: 1;
}
.stat-tile.pos .val { color: #22c55e; }
.stat-tile.neg .val { color: #ef4444; }
.stat-tile.neu .val { color: #60a5fa; }

/* File uploader */
[data-testid="stFileUploader"] section {
    background: #0d1526 !important;
    border: 1.5px dashed #1e3452 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] span {
    color: #475569 !important;
    font-size: 0.8rem !important;
}

/* Info box */
.info-pill {
    background: #0c1e38;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: #60a5fa;
    font-family: 'JetBrains Mono', monospace !important;
    margin-top: 0.4rem;
}

/* Divider */
.div { border: none; border-top: 1px solid #111d35; margin: 0.5rem 0 1.2rem; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──
FOLDER_ID  = "1RrmGgHKF5mLDRg-eFmU6SEO4N8sYJtx2"
DATA_DIR   = "data"
TIMEFRAMES = ["M1","M5","M15","M30","H1","H4","D1"]

# ── FUNCTIONS ──
@st.cache_data(show_spinner="Mengunduh data dari Google Drive...")
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
    dd_pct  = dd / peak * 100 if peak > 0 else 0
    ret_pct = net / initial_balance * 100
    return {
        "Total Trades":  (str(total),                      "neu"),
        "Win Rate":      (f"{wr:.1f}%",                    "pos" if wr >= 50 else "neg"),
        "Win / Loss":    (f"{wins} / {loss}",              "neu"),
        "Net Profit":    (f"${net:,.2f}",                  "pos" if net > 0 else "neg"),
        "Return %":      (f"{ret_pct:+.1f}%",              "pos" if ret_pct > 0 else "neg"),
        "Profit Factor": (f"{pf:.2f}",                     "pos" if pf >= 1 else "neg"),
        "Gross Profit":  (f"${gp:,.2f}",                   "pos"),
        "Gross Loss":    (f"${gl:,.2f}",                   "neg"),
        "Max Drawdown":  (f"{dd_pct:.1f}%",                "neg" if dd > 0 else "neu"),
        "Final Balance": (f"${equity[-1]:,.2f}",           "pos" if equity[-1] > initial_balance else "neg"),
    }

# ── TOPBAR ──
st.markdown("""
<div class="topbar">
    <div class="topbar-title">Backtest<span>Pro</span></div>
    <div class="topbar-sub">XAUUSD · Offline Engine · v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── STRATEGY CARD ──
st.markdown('<div class="card"><div class="card-title">Strategy</div>', unsafe_allow_html=True)
strat_file   = st.file_uploader("Upload file strategy (.py)", type=["py"])
strategy_mod = None
params       = {}

if strat_file:
    try:
        strategy_mod = load_strategy(strat_file)
        st.markdown(f"""
        <div class="strat-loaded">
            <div class="strat-dot"></div>
            <div>
                <div class="strat-name">{strategy_mod.NAME}</div>
                <div class="strat-ver">version {strategy_mod.VERSION}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Gagal load: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ── PARAMETERS CARD ──
if strategy_mod:
    st.markdown('<div class="card"><div class="card-title">Parameters</div>', unsafe_allow_html=True)
    for key, meta in strategy_mod.PARAMS.items():
        if meta["type"] == "int":
            params[key] = st.number_input(meta["label"], value=int(meta["default"]), step=1)
        elif meta["type"] == "float":
            params[key] = st.number_input(meta["label"], value=float(meta["default"]),
                                           step=0.01, format="%.2f")
        elif meta["type"] == "bool":
            params[key] = st.checkbox(meta["label"], value=meta["default"])
    st.markdown('</div>', unsafe_allow_html=True)

# ── DATA CARD ──
st.markdown('<div class="card"><div class="card-title">Data</div>', unsafe_allow_html=True)
tf = st.selectbox("Timeframe", TIMEFRAMES, index=2)
c1, c2 = st.columns(2)
with c1: date_from = st.date_input("Dari", value=pd.Timestamp("2024-01-01"))
with c2: date_to   = st.date_input("Sampai", value=pd.Timestamp("2024-06-30"))
st.markdown('</div>', unsafe_allow_html=True)

# ── CAPITAL CARD ──
st.markdown('<div class="card"><div class="card-title">Capital</div>', unsafe_allow_html=True)
initial_balance = st.number_input("Initial Balance ($)", value=5000, step=100)
pct_opts = ["—", "0.5%", "1%", "2%", "5%", "10%", "20%", "50%"]
bal_pct  = st.selectbox("Simulasi % dari Balance", pct_opts)
if bal_pct != "—":
    pct_val = float(bal_pct.replace("%","")) / 100
    st.markdown(f'<div class="info-pill">💰 {bal_pct} × ${initial_balance:,} = <b>${initial_balance*pct_val:,.0f}</b></div>',
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("⚡ JALANKAN BACKTEST")

# ── RESULTS ──
if run_btn:
    if not strategy_mod:
        st.warning("Upload strategy dulu!")
    else:
        with st.spinner("Menghitung..."):
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

                st.markdown('<div class="card"><div class="card-title">Summary</div>', unsafe_allow_html=True)
                html = '<div class="stats-grid">'
                for label, (val, cls) in stats.items():
                    html += f'<div class="stat-tile {cls}"><div class="lbl">{label}</div><div class="val">{val}</div></div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-title">Equity Curve</div>', unsafe_allow_html=True)
                st.line_chart(pd.DataFrame({"Equity ($)": equity}), color="#3b82f6", height=220)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-title">Trade List</div>', unsafe_allow_html=True)
                st.dataframe(trade_df, use_container_width=True, hide_index=True, height=280)
                csv = trade_df.to_csv(index=False)
                st.download_button("⬇️ Download CSV", csv,
                    f"backtest_{tf}_{date_from}_{date_to}.csv", "text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Tidak ada trade pada periode ini.")
