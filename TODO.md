# RSI Divergence Crypto Bot – TODO

Mark completed tasks with an X inside the brackets, like [x]

## Project Setup
- [ ] Create Python virtual environment (venv)
- [x] Install dependencies (ccxt, pandas, ta, python-dotenv, schedule, scipy)
- [ ] Create .env file and define API keys
- [x] Create config.py and define constants:
  - Symbol: BTC/USDT (default)
  - Timeframe: 5m
  - Risk per trade: 0.5 percent
  - Target risk-reward ratio: 1 to 2

---

## Exchange Integration
- [x] Initialize Binance connection using ccxt
- [x] Fetch 5-minute OHLCV data using fetch_ohlcv
- [x] Validate symbol is supported
- [ ] (Later) Add WebSocket for real-time price updates

---

## Asian Session High/Low Detection
- [ ] Define Asian session hours in UTC (00:00–08:00)
- [ ] Extract high and low levels from that session
- [ ] Detect if current price touches either level

---

## RSI and Divergence Logic
- [x] Compute RSI on 5-minute candles
- [x] Detect local highs and lows using scipy argrelextrema
- [x] Compare price action vs RSI for divergence
- [x] Log bullish or bearish divergence signals

---

## Engulfing Candle Detection
- [ ] Analyze last 2 to 3 candles for engulfing pattern
- [ ] Validate entry only on first engulfing after divergence
- [ ] Support both long and short logic

---

## Order Simulation and Execution
- [x] Create a simulated order function (log to file or console)
- [x] Calculate stop loss and take profit levels dynamically based on RR 1:2
- [x] Use position sizing logic to risk 0.5 percent of account per trade
- [x] (Later) Implement real order via ccxt if LIVE_MODE = True

---

## Risk and Position Management
- [x] Fetch account balance via API
- [x] Determine position size from balance and 0.5 percent risk
- [x] Calculate lot size based on stop loss distance and symbol precision
- [ ] Apply reduce-only or cancel-replace logic if needed

---

## Logging and Monitoring
- [x] Log signals to logs/signals.log
- [x] Log errors to logs/errors.log
- [ ] (Later) Add Telegram or email alerts for trades and exceptions

---

## Code Structure and Refactoring
- [x] config.py – parameters and constants
- [x] indicators.py – RSI, divergence, engulf logic
- [x] strategy.py – strategy combination logic
- [x] executor.py – simulated or real order handling
- [x] main.py – scheduler and orchestrator

---

## Optional Improvements
- [ ] WebSocket support for low-latency execution
- [ ] Backtest module using vectorbt or custom logic
- [x] Multi-symbol watchlist
- [ ] Streamlit UI for signal tracking
- [ ] Docker support for deployment
