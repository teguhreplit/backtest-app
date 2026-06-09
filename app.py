import streamlit as st
import pandas as pd
import numpy as np
import gdown
import os
import importlib.util
import sys

st.set_page_config(page_title="Backtest App", layout="wide")

# ── FOLDER ID GOOGLE DRIVE ──
FOLDER_ID = "1RrmGgHKF5mLDRg-eFmU6SEO4N8sYJtx2"
DATA_DIR = "data"

TIMEFRAMES = ["M1","M5","M15","M30","H1","H4","D1"]

@st.cache_data(show_spinner="Mengunduh data dari Google Drive...")
def download_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    for tf in TIMEFRAMES:
        fname = f"XAUUSDm_{tf}.csv"
        fpath = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fpath):
            url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
            gdown.download_folder(url, output=DATA_DIR, quiet=True, use_cookies=False)
            break

def load_csv(tf):
    path = os.path.join(DATA_DIR, f"XAUUSDm_{tf}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df

def load_strategy(file):
    spec = importlib.util.spec_from_file_location("strategy", file.name)
    tmp_path = f"/tmp/{file.name}"
    with open(tmp_path, "wb") as f:
        f.write(file.read())
    spec = importlib.util.spec_from_file_location("strategy", tmp_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run_backtest(df, strategy_mod, params, initial_balance=10000):
    trades = []
    try:
        trades = strategy_mod.run(df, params)
    except Exception as e:
        st.error(f"Error saat backtest: {e}")
        return None, None

    if not trades:
        return [], pd.DataFrame()

    trade_df = pd.DataFrame(trades)
    balance = initial_balance
    equity = [balance]
    for _, t in trade_df.iterrows():
        balance += t.get("pnl", 0)
        equity.append(balance)

    return equity, trade_df

def calc_stats(equity, trade_df, initial_balance):
    if trade_df.empty:
        return {}
    total = len(trade_df)
    wins = len(trade_df[trade_df["pnl"] > 0])
    losses = len(trade_df[trade_df["pnl"] <= 0])
    winrate = wins / total * 100 if total > 0 else 0
    gross_profit = trade_df[trade_df["pnl"] > 0]["pnl"].sum()
    gross_loss = abs(trade_df[trade_df["pnl"] <= 0]["pnl"].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else 0
    net_profit = trade_df["pnl"].sum()
    peak = max(equity)
    drawdowns = [peak - e for e in equity if e < peak]
    max_dd = max(drawdowns) if drawdowns else 0
    return {
        "Total Trades": total,
        "Win": wins,
        "Loss": losses,
        "Win Rate": f"{winrate:.1f}%",
        "Profit Factor": f"{pf:.2f}",
        "Net Profit": f"${net_profit:.2f}",
        "Gross Profit": f"${gross_profit:.2f}",
        "Gross Loss": f"${gross_loss:.2f}",
        "Max Drawdown": f"${max_dd:.2f}",
        "Final Balance": f"${equity[-1]:.2f}",
    }

# ── UI ──
st.title("📊 Backtest App")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Settings")

    # Upload strategy
    strat_file = st.file_uploader("Upload Strategy (.py)", type=["py"])
    strategy_mod = None
    params = {}

    if strat_file:
        try:
            strategy_mod = load_strategy(strat_file)
            st.success(f"✅ {strategy_mod.NAME} v{strategy_mod.VERSION}")

            st.markdown("**Parameters:**")
            for key, meta in strategy_mod.PARAMS.items():
                if meta["type"] == "int":
                    params[key] = st.number_input(
                        meta["label"], value=int(meta["default"]), step=1)
                elif meta["type"] == "float":
                    params[key] = st.number_input(
                        meta["label"], value=float(meta["default"]), step=0.01)
                elif meta["type"] == "bool":
                    params[key] = st.checkbox(meta["label"], value=meta["default"])
        except Exception as e:
            st.error(f"Gagal load strategy: {e}")

    st.markdown("**Data:**")
    tf = st.selectbox("Timeframe", TIMEFRAMES, index=2)
    date_from = st.date_input("Dari tanggal", value=pd.Timestamp("2024-01-01"))
    date_to = st.date_input("Sampai tanggal", value=pd.Timestamp("2024-06-30"))
    initial_balance = st.number_input("Initial Balance ($)", value=10000, step=100)

    run_btn = st.button("🚀 Jalankan Backtest", use_container_width=True)

with col2:
    st.subheader("📈 Hasil Backtest")

    if run_btn:
        if not strategy_mod:
            st.warning("Upload strategy dulu!")
        else:
            download_data()
            df = load_csv(tf)
            if df is None:
                st.error(f"Data {tf} tidak ditemukan!")
            else:
                df = df[(df["time"] >= pd.Timestamp(date_from)) &
                        (df["time"] <= pd.Timestamp(date_to))]
                st.info(f"Data loaded: {len(df)} candles ({tf})")

                equity, trade_df = run_backtest(df, strategy_mod, params, initial_balance)

                if equity and not trade_df.empty:
                    stats = calc_stats(equity, trade_df, initial_balance)

                    # Stats grid
                    st.markdown("### 📊 Summary")
                    cols = st.columns(3)
                    for i, (k, v) in enumerate(stats.items()):
                        cols[i % 3].metric(k, v)

                    # Equity curve
                    st.markdown("### 📉 Equity Curve")
                    st.line_chart(equity)

                    # Trade list
                    st.markdown("### 📋 Trade List")
                    st.dataframe(trade_df, use_container_width=True)
                else:
                    st.warning("Tidak ada trade yang terjadi pada periode ini.")
