"""
Exchange handler module for the RSI Divergence Trading Bot.
Handles connection to cryptocurrency exchanges and order management.
"""

import ccxt
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .config import config
from .logger import logger

class ExchangeHandler:
    """Handles exchange connections and trading operations."""
    
    def __init__(self):
        self.exchange = None
        self.exchange_name = config.EXCHANGE_NAME.lower()
        self.initialize_exchange()
    
    def initialize_exchange(self):
        """Initialize exchange connection based on configuration."""
        try:
            # Get exchange class
            exchange_class = getattr(ccxt, self.exchange_name)
            
            # Initialize exchange with API credentials
            self.exchange = exchange_class({
                'apiKey': config.API_KEY,
                'secret': config.API_SECRET,
                'sandbox': config.SANDBOX_MODE,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Use spot trading
                }
            })
            
            # Test connection
            if config.API_KEY and config.API_SECRET:
                markets = self.exchange.load_markets()
                logger.logger.info(f"Successfully connected to {self.exchange_name}")
                logger.logger.info(f"Available markets: {len(markets)}")
            else:
                logger.logger.info(f"Exchange initialized in simulation mode")
                
        except Exception as e:
            logger.log_error(e, f"Failed to initialize {self.exchange_name}")
            raise
    
    def get_historical_data(self, symbol: str, timeframe: str = '1h', 
                           limit: int = 100) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for data (e.g., '1h', '4h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.log_error(e, f"Failed to fetch historical data for {symbol}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.log_error(e, f"Failed to get current price for {symbol}")
            return 0.0
    
    def get_account_balance(self) -> Dict[str, float]:
        """Get account balance."""
        try:
            if config.SIMULATE_TRADING:
                # Return simulated balance
                return {
                    'USDT': config.INITIAL_BALANCE,
                    'total': config.INITIAL_BALANCE
                }
            else:
                balance = self.exchange.fetch_balance()
                return {
                    'USDT': balance['USDT']['free'],
                    'total': balance['total']['USDT']
                }
        except Exception as e:
            logger.log_error(e, "Failed to get account balance")
            return {'USDT': 0.0, 'total': 0.0}
    
    def place_market_order(self, symbol: str, side: str, amount: float) -> Optional[Dict]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            amount: Amount to trade
            
        Returns:
            Order information or None if failed
        """
        try:
            if config.SIMULATE_TRADING:
                # Simulate order execution
                current_price = self.get_current_price(symbol)
                simulated_order = {
                    'id': f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': current_price,
                    'status': 'closed',
                    'filled': amount,
                    'cost': amount * current_price,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.log_order_execution(
                    f"SIMULATED {side.upper()}", 
                    symbol, 
                    amount, 
                    current_price, 
                    simulated_order['id']
                )
                
                return simulated_order
            else:
                # Place real order
                order = self.exchange.create_market_order(symbol, side, amount)
                
                logger.log_order_execution(
                    side.upper(), 
                    symbol, 
                    amount, 
                    order.get('price', 0), 
                    order.get('id')
                )
                
                return order
                
        except Exception as e:
            logger.log_error(e, f"Failed to place {side} order for {symbol}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, amount: float, 
                         price: float) -> Optional[Dict]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
            
        Returns:
            Order information or None if failed
        """
        try:
            if config.SIMULATE_TRADING:
                # Simulate limit order
                simulated_order = {
                    'id': f"sim_limit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'status': 'open',
                    'filled': 0,
                    'cost': 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.log_order_execution(
                    f"SIMULATED {side.upper()} LIMIT", 
                    symbol, 
                    amount, 
                    price, 
                    simulated_order['id']
                )
                
                return simulated_order
            else:
                # Place real limit order
                order = self.exchange.create_limit_order(symbol, side, amount, price)
                
                logger.log_order_execution(
                    f"{side.upper()} LIMIT", 
                    symbol, 
                    amount, 
                    price, 
                    order.get('id')
                )
                
                return order
                
        except Exception as e:
            logger.log_error(e, f"Failed to place {side} limit order for {symbol}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order."""
        try:
            if config.SIMULATE_TRADING:
                logger.logger.info(f"SIMULATED: Cancelled order {order_id} for {symbol}")
                return True
            else:
                self.exchange.cancel_order(order_id, symbol)
                logger.logger.info(f"Cancelled order {order_id} for {symbol}")
                return True
        except Exception as e:
            logger.log_error(e, f"Failed to cancel order {order_id}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get list of open orders."""
        try:
            if config.SIMULATE_TRADING:
                return []  # No open orders in simulation
            else:
                orders = self.exchange.fetch_open_orders(symbol)
                return orders
        except Exception as e:
            logger.log_error(e, "Failed to get open orders")
            return []
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Get status of a specific order."""
        try:
            if config.SIMULATE_TRADING:
                return {
                    'id': order_id,
                    'status': 'closed',
                    'filled': 100,
                    'remaining': 0
                }
            else:
                order = self.exchange.fetch_order(order_id, symbol)
                return order
        except Exception as e:
            logger.log_error(e, f"Failed to get order status for {order_id}")
            return None 