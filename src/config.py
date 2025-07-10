"""
Configuration module for the RSI Divergence Trading Bot.
Handles loading environment variables and bot settings.
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for trading bot settings."""
    
    # Exchange Configuration
    EXCHANGE_NAME: str = os.getenv('EXCHANGE_NAME', 'binance')
    API_KEY: str = os.getenv('API_KEY', '')
    API_SECRET: str = os.getenv('API_SECRET', '')
    SANDBOX_MODE: bool = os.getenv('SANDBOX_MODE', 'True').lower() == 'true'
    
    # Trading Configuration
    TRADING_PAIRS: List[str] = os.getenv('TRADING_PAIRS', 'BTC/USDT').split(',')
    RSI_PERIOD: int = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD: float = float(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT: float = float(os.getenv('RSI_OVERBOUGHT', '70'))
    MIN_DIVERGENCE_STRENGTH: float = float(os.getenv('MIN_DIVERGENCE_STRENGTH', '0.7'))
    
    # Risk Management
    MAX_POSITION_SIZE: float = float(os.getenv('MAX_POSITION_SIZE', '0.01'))
    STOP_LOSS_PERCENTAGE: float = float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0'))
    TAKE_PROFIT_PERCENTAGE: float = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '4.0'))
    
    # Simulation Mode
    SIMULATE_TRADING: bool = os.getenv('SIMULATE_TRADING', 'True').lower() == 'true'
    INITIAL_BALANCE: float = float(os.getenv('INITIAL_BALANCE', '1000'))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/trading_bot.log')
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration settings and return status."""
        errors = []
        warnings = []
        
        # Check required API credentials
        if not cls.API_KEY or not cls.API_SECRET:
            if not cls.SIMULATE_TRADING:
                errors.append("API_KEY and API_SECRET are required for live trading")
            else:
                warnings.append("API credentials not set - running in simulation mode")
        
        # Validate trading pairs
        if not cls.TRADING_PAIRS or cls.TRADING_PAIRS == ['']:
            errors.append("At least one trading pair must be specified")
        
        # Validate RSI parameters
        if not (0 < cls.RSI_OVERSOLD < cls.RSI_OVERBOUGHT < 100):
            errors.append("RSI thresholds must be: 0 < OVERSOLD < OVERBOUGHT < 100")
        
        # Validate risk management
        if cls.MAX_POSITION_SIZE <= 0 or cls.MAX_POSITION_SIZE > 1:
            errors.append("MAX_POSITION_SIZE must be between 0 and 1")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Create global config instance
config = Config() 