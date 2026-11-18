"""BTC race bot: 60-minute momentum trend follower for cbBTC/USDC.

Reads one 1-minute bar per batch (agent-fun/bars-replay/v1) and trades the
single asset CBBTC long-only, in full size, against $1,000 of paper USDC.

Strategy
--------
- Enter long when the close has risen more than 0.5% over the last 60 bars
  (a sustained multi-hour move, not 1-minute noise: a full round trip costs
  about 26 bps in fees, slippage and price impact, so a trade must catch a
  move larger than that).
- Exit when the 60-bar return turns below -0.5% (the trend has reversed) or
  when the close falls more than 0.8% below the highest close since entry
  (trailing stop, to lock in a rally and cap a reversal).
- Otherwise stay flat. Cash earns nothing, so the bot only holds the asset
  while the trend is with it.

All decisions use exact integer arithmetic on the bar closes (price_scale 5),
so two runs on the same data give byte-identical orders. No network, no wall
clock, no files outside the repository, no randomness. The hello, batch and
orders flow is handled by the vendored SDK shim (vendor/makefun_bars.py).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# Strategy parameters (basis points; 10000 bps = 100%).
LOOKBACK = 60            # bars of closes behind the entry signal
ENTRY_BPS = 45           # buy when the 60-bar return exceeds +0.45%
EXIT_BPS = 50            # sell when the 60-bar return falls below -0.5%
TRAIL_BPS = 80           # sell when the close is 0.8% under its peak since entry
MAX_SLIPPAGE_BPS = 500   # 5%: wide enough to rarely reject a fill, a guard only

# History of closes (ints at price_scale 5), oldest first.
closes = []
# Highest close seen while a position is open; None while flat.
trail_peak = None


def _return_bps(now, then):
    """The return from `then` to `now` in basis points, truncated toward zero."""
    return (now - then) * 10000 // then


def on_batch(state, batch):
    global trail_peak
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    closes.append(close)

    held = state.positions.get(SYMBOL)
    held_qty = held.qty if held is not None else 0

    if held_qty > 0:
        # In a position: keep the trailing peak at the best close so far.
        trail_peak = close if trail_peak is None else max(trail_peak, close)
        ret60 = None
        if len(closes) > LOOKBACK:
            ret60 = _return_bps(closes[-1], closes[-1 - LOOKBACK])
        fell = close * 10000 < trail_peak * (10000 - TRAIL_BPS)
        reversed_ = ret60 is not None and ret60 < -EXIT_BPS
        if fell or reversed_:
            trail_peak = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held_qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    # Flat: look for a sustained up-move to enter.
    trail_peak = None
    if len(closes) > LOOKBACK:
        ret60 = _return_bps(closes[-1], closes[-1 - LOOKBACK])
        if ret60 > ENTRY_BPS:
            room = state.weight_room(SYMBOL)
            notional = state.cash if state.cash < room else room
            if notional >= 1_000_000:  # at least $1, the minimum notional
                return [{"side": "buy", "symbol": SYMBOL,
                         "notional_quote_units": notional,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)
