# RSI Divergence Crypto Trading Bot

A sophisticated cryptocurrency trading bot that uses RSI (Relative Strength Index) divergence analysis to identify potential trading opportunities. Built with Python and designed for modular, secure, and reliable automated trading.

## 🚀 Features

- **RSI Divergence Detection**: Advanced algorithm to detect bullish and bearish divergences
- **Multiple Signal Types**: Strong, medium, and weak signals with confidence levels
- **Risk Management**: Built-in stop loss and take profit mechanisms
- **Simulation Mode**: Test strategies without real money
- **Exchange Support**: Uses ccxt for broad exchange compatibility
- **Comprehensive Logging**: Detailed logs for trading activities and performance tracking
- **Modular Architecture**: Clean, maintainable code structure
- **Configurable Parameters**: Easy customization through environment variables

## 📋 Prerequisites

- Python 3.11 or higher
- Exchange API credentials (for live trading)
- Sufficient funds for trading (or simulation mode for testing)

## 🛠️ Installation

1. **Clone the repository:**
   ```powershell
   git clone <repository-url>
   cd rsi-asia-trading-bot
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```powershell
   copy env.example .env
   ```
   Edit the `.env` file with your settings (see Configuration section).

## ⚙️ Configuration

Copy `env.example` to `.env` and configure the following settings:

### Exchange Configuration
- `EXCHANGE_NAME`: Exchange name (e.g., binance, coinbase)
- `API_KEY`: Your exchange API key
- `API_SECRET`: Your exchange API secret
- `SANDBOX_MODE`: Set to True for sandbox/testnet trading

### Trading Configuration
- `TRADING_PAIRS`: Comma-separated list of trading pairs (e.g., BTC/USDT,ETH/USDT)
- `RSI_PERIOD`: RSI calculation period (default: 14)
- `RSI_OVERSOLD`: RSI oversold threshold (default: 30)
- `RSI_OVERBOUGHT`: RSI overbought threshold (default: 70)
- `MIN_DIVERGENCE_STRENGTH`: Minimum divergence strength to trigger signals (default: 0.7)

### Risk Management
- `MAX_POSITION_SIZE`: Maximum position size as percentage of balance (default: 0.01)
- `STOP_LOSS_PERCENTAGE`: Stop loss percentage (default: 2.0)
- `TAKE_PROFIT_PERCENTAGE`: Take profit percentage (default: 4.0)

### Simulation Mode
- `SIMULATE_TRADING`: Set to True to enable simulation mode
- `INITIAL_BALANCE`: Starting balance for simulation (default: 1000)

## 🏃 Usage

### Run Once
Execute the strategy once and exit:
```powershell
python main.py --once
```

### Run Continuously
Run the bot continuously with hourly execution:
```powershell
python main.py --continuous
```

### Default Mode
Run continuously (default behavior):
```powershell
python main.py
```

### Help
Display help information:
```powershell
python main.py --help
```

## 📊 Trading Strategy

The bot uses a sophisticated RSI divergence strategy:

### Signal Types

1. **STRONG_BUY**: RSI oversold + Bullish divergence
2. **STRONG_SELL**: RSI overbought + Bearish divergence  
3. **BUY**: RSI oversold (confidence >= 70% to execute)
4. **SELL**: RSI overbought (confidence >= 70% to execute)
5. **WEAK_BUY**: Bullish divergence only
6. **WEAK_SELL**: Bearish divergence only

### Risk Management

- **Position Sizing**: Percentage-based position sizing
- **Stop Loss**: Automatic stop loss at configurable percentage
- **Take Profit**: Automatic take profit at configurable percentage
- **One Position Per Symbol**: Prevents over-exposure

## 📁 Project Structure

```
rsi-asia-trading-bot/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging system
│   ├── exchange_handler.py    # Exchange API interactions
│   ├── technical_analysis.py  # RSI and divergence analysis
│   └── trading_strategy.py    # Main trading logic
├── logs/                      # Log files (created automatically)
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── env.example               # Environment configuration template
├── README.md                 # This file
└── OVERVIEW.md              # Project overview
```

## 🔧 Development

### Key Components

- **Config Module**: Centralized configuration management with validation
- **Logger Module**: Structured logging for trades, errors, and system events
- **Exchange Handler**: Unified interface for exchange operations using ccxt
- **Technical Analysis**: RSI calculation and divergence detection algorithms
- **Trading Strategy**: Core trading logic with risk management

### Adding New Indicators

To add new technical indicators:

1. Extend the `TechnicalAnalysis` class in `src/technical_analysis.py`
2. Add indicator parameters to configuration
3. Integrate signals into the `generate_trading_signals` method

### Adding New Exchanges

The bot uses ccxt, which supports 100+ exchanges. Simply:

1. Set `EXCHANGE_NAME` in your `.env` file
2. Ensure you have valid API credentials
3. Test in simulation mode first

## 🚨 Safety & Risk Management

### Important Safety Features

- **Simulation Mode**: Always test strategies in simulation mode first
- **API Key Security**: Never hardcode API keys; use environment variables
- **Error Handling**: Comprehensive error handling and logging
- **Position Limits**: Configurable position size limits
- **Graceful Shutdown**: Proper cleanup on termination

### Risk Warnings

⚠️ **Important**: Cryptocurrency trading involves significant risk. Always:

- Start with simulation mode
- Use small position sizes initially
- Monitor the bot's performance closely
- Set appropriate stop losses
- Never invest more than you can afford to lose

## 📈 Performance Monitoring

The bot provides comprehensive logging:

- **Trade Signals**: All generated signals with reasoning
- **Order Execution**: Details of all placed orders
- **Position Updates**: Real-time position and PnL information
- **Strategy Summary**: Performance statistics and metrics

Logs are saved to `logs/trading_bot.log` and displayed in the console.

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check your API credentials
   - Verify exchange name spelling
   - Ensure API permissions are correct

2. **No Trading Signals**
   - Check if trading pairs are valid
   - Verify RSI parameters are reasonable
   - Ensure sufficient historical data

3. **Position Size Too Small**
   - Increase `MAX_POSITION_SIZE` or account balance
   - Check minimum trade sizes for your exchange

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk and is not suitable for all investors. The authors are not responsible for any financial losses incurred from using this software. Always do your own research and consult with financial advisors before making trading decisions.

## 🆘 Support

For questions, issues, or feature requests:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Provide logs and configuration (without sensitive data)

---

**Happy Trading! 🚀** 