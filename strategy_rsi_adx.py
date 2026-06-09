import pandas as pd
import numpy as np

# ===== METADATA =====
NAME = "RSI ADX Reversal"
VERSION = "1.0"

# ===== PARAMETERS =====
PARAMS = {
    "rsi_period":    {"default": 9,    "type": "int",   "label": "RSI Period"},
    "adx_period":    {"default": 9,    "type": "int",   "label": "ADX Period"},
    "oversold":      {"default": 30,   "type": "int",   "label": "RSI Oversold"},
    "overbought":    {"default": 70,   "type": "int",   "label": "RSI Overbought"},
    "di_min":        {"default": 20,   "type": "int",   "label": "DI Minimum"},
    "di_entry":      {"default": 25,   "type": "int",   "label": "DI Entry Threshold"},
    "sl_pips":       {"default": 50,   "type": "int",   "label": "Stop Loss (pips)"},
    "lot_size":      {"default": 0.1,  "type": "float", "label": "Lot Size"},
    "pip_value":     {"default": 0.1,  "type": "float", "label": "Pip Value ($)"},
}

# ===== INDICATORS =====
def calc_rsi(close, period):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_adx(high, low, close, period):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr = tr.ewm(com=period-1, min_periods=period).mean()
    plus_di = 100 * plus_dm.ewm(com=period-1, min_periods=period).mean() / atr
    minus_di = 100 * minus_dm.ewm(com=period-1, min_periods=period).mean() / atr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(com=period-1, min_periods=period).mean()
    return adx, plus_di, minus_di

# ===== MAIN LOGIC =====
def run(df, params):
    rsi_period  = params["rsi_period"]
    adx_period  = params["adx_period"]
    oversold    = params["oversold"]
    overbought  = params["overbought"]
    di_min      = params["di_min"]
    di_entry    = params["di_entry"]
    sl_pips     = params["sl_pips"]
    lot_size    = params["lot_size"]
    pip_value   = params["pip_value"]

    df = df.copy()
    df["rsi"]       = calc_rsi(df["close"], rsi_period)
    df["adx"], df["plus_di"], df["minus_di"] = calc_adx(
        df["high"], df["low"], df["close"], adx_period)

    trades = []
    buy_stage  = 0
    sell_stage = 0

    for i in range(adx_period * 3, len(df)):
        c = df.iloc[i]
        rsi      = c["rsi"]
        plus_di  = c["plus_di"]
        minus_di = c["minus_di"]

        # ── RESET ──
        if buy_stage > 0 and rsi > 65:
            buy_stage = 0
        if sell_stage > 0 and rsi < 35:
            sell_stage = 0

        # ── BUY STAGES ──
        if buy_stage == 0 and rsi < oversold:
            buy_stage = 1

        if buy_stage == 1:
            if plus_di < di_min:
                buy_stage = 2

        if buy_stage == 1 and rsi < oversold and plus_di < di_min:
            buy_stage = 2

        if buy_stage == 2 and plus_di > di_entry:
            entry = c["close"]
            sl    = entry - sl_pips * 0.01
            tp1   = entry + sl_pips * 0.01
            tp2   = entry + sl_pips * 0.02
            pnl   = sl_pips * pip_value * lot_size * 10
            trades.append({
                "time":      c["time"],
                "type":      "BUY",
                "entry":     round(entry, 5),
                "sl":        round(sl, 5),
                "tp1":       round(tp1, 5),
                "tp2":       round(tp2, 5),
                "lot":       lot_size,
                "pnl":       round(pnl, 2),
            })
            buy_stage = 0

        # ── SELL STAGES ──
        if sell_stage == 0 and rsi > overbought:
            sell_stage = 1

        if sell_stage == 1:
            if minus_di < di_min:
                sell_stage = 2

        if sell_stage == 1 and rsi > overbought and minus_di < di_min:
            sell_stage = 2

        if sell_stage == 2 and minus_di > di_entry:
            entry = c["close"]
            sl    = entry + sl_pips * 0.01
            tp1   = entry - sl_pips * 0.01
            tp2   = entry - sl_pips * 0.02
            pnl   = sl_pips * pip_value * lot_size * 10
            trades.append({
                "time":      c["time"],
                "type":      "SELL",
                "entry":     round(entry, 5),
                "sl":        round(sl, 5),
                "tp1":       round(tp1, 5),
                "tp2":       round(tp2, 5),
                "lot":       lot_size,
                "pnl":       round(pnl, 2),
            })
            sell_stage = 0

    return trades
