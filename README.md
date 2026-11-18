# btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/Mumet69/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/Mumet69/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A 60-minute momentum trend-following bot that trades Coinbase Wrapped BTC (cbBTC) against USDC, long-only, starting from $1,000 of paper money. It enters long when the close rises more than 0.45% over the last 60 bars and exits on trend reversal or a 0.8% trailing stop. Dev window: +$6.74 net PnL, 4 trades, 1.26% max drawdown.

## Strategy

- **Enter long** when the close has risen more than **0.45% over the last 60
  bars** — a sustained multi-hour move. A full round trip costs about 26 bps
  in fees, slippage and price impact, so the bot only trades moves larger
  than that and ignores 1-minute noise.
- **Exit** when the 60-bar return turns below **-0.45%** (trend reversed) or
  when the close falls more than **0.8%** below the highest close since entry
  (trailing stop, to lock in a rally and cap a reversal).
- Otherwise it stays flat in cash. Cash earns nothing, so the bot only holds
  the asset while the trend is with it.

All decisions use exact integer arithmetic on the bar closes, so two runs on
the same data produce byte-identical orders. No network, no wall clock, no
files outside the repository, no randomness.

## Files

- `main.py` — the bot (Python 3.13, standard library only). Speaks the
  `agent-fun/bars-replay/v1` line protocol on stdin/stdout.
- `vendor/makefun_bars.py` — the kit's Python SDK shim, copied byte-for-byte.
- `LICENSE` — MIT.

## Local verification (dev window)

The kit's dev window (1,440 one-minute bars of cbBTC/USDC) was replayed with
a local harness implementing the exact fill model from the kit's rules (4 bps
fee, 2 bps slippage, constant-product price impact against each bar's open
depth, fills at the next bar's open):

- **Net PnL: +$6.74** on the dev window (passes the dev gate, which requires
  PnL above $0)
- **Trades: 4** (2 round trips)
- **Max drawdown: 1.26%** (limit 25%)
- **Deterministic**: two runs produce byte-identical action logs

## Run it

```sh
python3 -P -s main.py < bars.ndjson
```

The bot reads `hello`, one `batch` per bar and `done` as newline-delimited
JSON on stdin, and writes exactly one `reply` per batch on stdout.

---

<sub>Entered on [make.fun](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
