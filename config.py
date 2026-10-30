#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# config.py - PRO CHART BOT v23.0 with Volume Accum/Dist Strategy
# Loads secrets from .env file if present, else uses defaults below.
# Create a .env file in same folder as bot.py or set env vars directly.

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current dir and parent
load_dotenv()
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# =============================================================================
# TELEGRAM
# =============================================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8958801360:AAF4kumocS7DbZ7630nbWqSkk5KVVOAbNf4")
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "@hefge")

# =============================================================================
# BYBIT API - for klines (public) + authenticated if you set keys
# =============================================================================
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "CKzEJnYXqjqMDfTicR")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "0eCLeZIs91MXDjA35eOzov9Oy55seKyNzQZi")
BYBIT_TESTNET = os.getenv("BYBIT_TESTNET", "false").lower() in ("1", "true", "yes")

# =============================================================================
# SCANNER SETTINGS
# =============================================================================
# How often the live scanner loops (seconds)
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "120"))

# Cooldown between signals for same pair+tf+direction (minutes)
SIGNAL_COOLDOWN_MINUTES = int(os.getenv("SIGNAL_COOLDOWN_MINUTES", "30"))

# How long a signal stays active before expiry (minutes)
SIGNAL_EXPIRY_MINUTES = int(os.getenv("SIGNAL_EXPIRY_MINUTES", "60"))

# Max active signals across all users/pairs
MAX_ACTIVE_SIGNALS = int(os.getenv("MAX_ACTIVE_SIGNALS", "20"))

# Only one active signal per pair at a time
ONE_ACTIVE_SIGNAL_PER_PAIR = os.getenv("ONE_ACTIVE_SIGNAL_PER_PAIR", "true").lower() in ("1", "true", "yes")

# Minimum confirmation score (used by old engine, kept for compatibility)
MIN_CONFIRMATION_SCORE = int(os.getenv("MIN_CONFIRMATION_SCORE", "70"))

# =============================================================================
# PAYMENTS - Crypto wallets for manual payment approval
# =============================================================================
# You can add your wallets here or via .env as ADMIN_WALLET_BTC, etc.
ADMIN_WALLETS = {
    "BTC": os.getenv("ADMIN_WALLET_BTC", "bc1q...your_btc_wallet"),
    "ETH": os.getenv("ADMIN_WALLET_ETH", "0x...your_eth_wallet"),
    "USDT_TRC20": os.getenv("ADMIN_WALLET_USDT_TRC20", "T...your_trc20"),
    "USDT_ERC20": os.getenv("ADMIN_WALLET_USDT_ERC20", "0x...your_erc20_usdt"),
    "SOL": os.getenv("ADMIN_WALLET_SOL", "your_sol_wallet"),
}

# =============================================================================
# VOLUME STRATEGY INPUTS - override via .env if needed
# =============================================================================
VOLUME_STRATEGY = {
    "VolMAPeriod": int(os.getenv("VOL_MA_PERIOD", "20")),
    "ConsolidationPeriod": int(os.getenv("CONSOL_PERIOD", "12")),
    "ConsolidationATRMult": float(os.getenv("CONSOL_ATR_MULT", "1.8")),
    "VolumeSpikeMult": float(os.getenv("VOL_SPIKE_MULT", "2.5")),
    "VolumeLowMult": float(os.getenv("VOL_LOW_MULT", "1.0")),
    "SpikeBodyATRMult": float(os.getenv("SPIKE_BODY_ATR_MULT", "0.5")),
    "RewardRatio": float(os.getenv("REWARD_RATIO", "1.2")),
}

def validate():
    """Basic validation - raises warning if critical vars missing."""
    warnings = []
    if not BOT_TOKEN or "YOUR_TELEGRAM" in BOT_TOKEN:
        warnings.append("BOT_TOKEN not set - set it in .env or config.py")
    if not BYBIT_API_KEY:
        warnings.append("BYBIT_API_KEY empty - klines will work (public) but no private account calls")
    if warnings:
        # Don't crash, just warn - bot.py will print these
        raise ValueError("; ".join(warnings))
    return True

# For backward compatibility with old bot imports
# old code expects cfg.GOLD_INPUTS etc - we alias
try:
    from dataclasses import dataclass

    @dataclass
    class _GoldInputsCompat:
        Lookback: int = 20
        SwingStrength: int = 2
        OBExtraMarginPips: float = 5.0
        MaxOBAge: int = 30
        RequireEngulfing: bool = True
        RequireLiquidityGrab: bool = True
        RiskPercent: float = 1.0
        RewardRatio: float = VOLUME_STRATEGY["RewardRatio"]
        MaxDailyLossPercent: float = 1.0
        MaxDailyProfitPercent: float = 3.0
        MaxDailyTrades: int = 4
        UseTimeFilter: bool = False
        TradingStartTime: str = "08:00"
        TradingEndTime: str = "19:00"
        AvoidNews: bool = True
        NewsAvoidanceMinutes: int = 30

    GOLD_INPUTS = _GoldInputsCompat()
except Exception:
    GOLD_INPUTS = None

