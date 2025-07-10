# RSI Divergence Crypto Trading Bot - OVERVIEW

## Tech Stack

| Layer        | Technology                 | Notes                                   |
|--------------|----------------------------|-----------------------------------------|
| Language     | Python 3.11+               | Primary scripting language              |
| API Access   | ccxt                       | Unified exchange API access             |
| Data         | pandas, numpy              | Historical price manipulation           |
| Indicators   | ta, scipy                  | RSI and pattern detection               |
| Scheduling   | schedule or apscheduler    | Periodic strategy execution             |
| Env Config   | python-dotenv              | Securely load API keys                  |
| Deployment   | Local for now              | VPS or Docker planned later             |
| Logging      | Standard file logging      | Extendable to Telegram alerts           |

## Cursor Instructions

### Cursor should

- Suggest modular, readable, and well-structured Python code  
- Use dotenv for all secrets and environment configs  
- Default to simulated trading mode  
- Follow Python best practices and naming conventions  

### Cursor should not

- Hardcode API keys or secrets  
- Send live orders unless explicitly enabled  
- Combine multiple responsibilities in a single script  
- Suggest infinite loops without proper error handling  

## Project Structure

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
├── README.md                 # Project documentation
└── OVERVIEW.md              # Project overview
```

## Usage

### Basic Usage

```powershell
# Install dependencies
pip install -r requirements.txt

# Configure environment (copy env.example to .env)
copy env.example .env

# Run once
python main.py --once

# Run continuously
python main.py --continuous
```

### Configuration

The bot uses environment variables for configuration. Key settings include:

- **SIMULATE_TRADING**: Set to True for simulation mode (recommended for testing)
- **EXCHANGE_NAME**: Exchange to use (binance, coinbase, etc.)
- **TRADING_PAIRS**: Comma-separated list of pairs to trade
- **RSI_PERIOD**: RSI calculation period (default: 14)
- **MAX_POSITION_SIZE**: Maximum position size as percentage of balance

