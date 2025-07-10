"""
Trading strategy module for the RSI Divergence Trading Bot.
Combines technical analysis, exchange handling, and risk management.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .config import config
from .logger import logger
from .exchange_handler import ExchangeHandler
from .technical_analysis import TechnicalAnalysis

class Position:
    """Represents a trading position."""
    
    def __init__(self, symbol: str, side: str, amount: float, entry_price: float, 
                 stop_loss: float = None, take_profit: float = None):
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.amount = amount
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = datetime.now()
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
        self.is_open = True
    
    def update_pnl(self, current_price: float):
        """Update unrealized PnL based on current price."""
        if self.side == 'long':
            self.unrealized_pnl = (current_price - self.entry_price) * self.amount
        else:  # short
            self.unrealized_pnl = (self.entry_price - current_price) * self.amount
    
    def should_close_position(self, current_price: float) -> Optional[str]:
        """Check if position should be closed based on stop loss or take profit."""
        if self.side == 'long':
            if self.stop_loss and current_price <= self.stop_loss:
                return 'stop_loss'
            if self.take_profit and current_price >= self.take_profit:
                return 'take_profit'
        else:  # short
            if self.stop_loss and current_price >= self.stop_loss:
                return 'stop_loss'
            if self.take_profit and current_price <= self.take_profit:
                return 'take_profit'
        return None

class RSIDivergenceStrategy:
    """Main trading strategy class combining all components."""
    
    def __init__(self):
        self.exchange = ExchangeHandler()
        self.technical_analysis = TechnicalAnalysis()
        self.positions: Dict[str, Position] = {}
        self.balance = config.INITIAL_BALANCE
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        
        # Risk management parameters
        self.max_position_size = config.MAX_POSITION_SIZE
        self.stop_loss_pct = config.STOP_LOSS_PERCENTAGE / 100
        self.take_profit_pct = config.TAKE_PROFIT_PERCENTAGE / 100
        
        logger.log_startup("simulation" if config.SIMULATE_TRADING else "live")
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate position size based on risk management rules."""
        try:
            # Get current balance
            balance_info = self.exchange.get_account_balance()
            available_balance = balance_info.get('USDT', 0)
            
            # Calculate position size (percentage of available balance)
            position_value = available_balance * self.max_position_size
            position_size = position_value / price
            
            # Ensure minimum position size requirements
            if position_size < 0.001:  # Minimum trade size
                return 0.0
            
            return round(position_size, 6)
            
        except Exception as e:
            logger.log_error(e, f"Failed to calculate position size for {symbol}")
            return 0.0
    
    def calculate_stop_loss_take_profit(self, entry_price: float, 
                                       side: str) -> tuple[float, float]:
        """Calculate stop loss and take profit levels."""
        if side == 'long':
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit = entry_price * (1 + self.take_profit_pct)
        else:  # short
            stop_loss = entry_price * (1 + self.stop_loss_pct)
            take_profit = entry_price * (1 - self.take_profit_pct)
        
        return stop_loss, take_profit
    
    def open_position(self, symbol: str, signal: str, current_price: float) -> bool:
        """Open a new position based on trading signal."""
        try:
            # Determine position side
            if signal in ['BUY', 'STRONG_BUY', 'WEAK_BUY']:
                side = 'long'
                order_side = 'buy'
            elif signal in ['SELL', 'STRONG_SELL', 'WEAK_SELL']:
                side = 'short'
                order_side = 'sell'
            else:
                return False
            
            # Calculate position size
            position_size = self.calculate_position_size(symbol, current_price)
            if position_size == 0:
                logger.logger.warning(f"Position size too small for {symbol}")
                return False
            
            # Place order
            order = self.exchange.place_market_order(symbol, order_side, position_size)
            if not order:
                logger.logger.error(f"Failed to place order for {symbol}")
                return False
            
            # Calculate stop loss and take profit
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(current_price, side)
            
            # Create position
            position = Position(
                symbol=symbol,
                side=side,
                amount=position_size,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Store position
            self.positions[symbol] = position
            
            logger.logger.info(f"Opened {side} position for {symbol}")
            logger.logger.info(f"Entry: {current_price:.4f} | Stop Loss: {stop_loss:.4f} | Take Profit: {take_profit:.4f}")
            
            return True
            
        except Exception as e:
            logger.log_error(e, f"Failed to open position for {symbol}")
            return False
    
    def close_position(self, symbol: str, reason: str = "signal") -> bool:
        """Close an existing position."""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            current_price = self.exchange.get_current_price(symbol)
            
            # Determine order side (opposite of position side)
            if position.side == 'long':
                order_side = 'sell'
            else:
                order_side = 'buy'
            
            # Place closing order
            order = self.exchange.place_market_order(symbol, order_side, position.amount)
            if not order:
                logger.logger.error(f"Failed to close position for {symbol}")
                return False
            
            # Calculate final PnL
            if position.side == 'long':
                realized_pnl = (current_price - position.entry_price) * position.amount
            else:
                realized_pnl = (position.entry_price - current_price) * position.amount
            
            position.realized_pnl = realized_pnl
            position.is_open = False
            
            # Update statistics
            self.total_trades += 1
            self.total_pnl += realized_pnl
            
            if realized_pnl > 0:
                self.winning_trades += 1
                logger.logger.info(f"✅ Closed {position.side} position for {symbol} with PROFIT: {realized_pnl:.4f} USDT")
            else:
                self.losing_trades += 1
                logger.logger.info(f"❌ Closed {position.side} position for {symbol} with LOSS: {realized_pnl:.4f} USDT")
            
            logger.logger.info(f"Reason: {reason} | Exit price: {current_price:.4f}")
            
            # Remove position
            del self.positions[symbol]
            
            return True
            
        except Exception as e:
            logger.log_error(e, f"Failed to close position for {symbol}")
            return False
    
    def check_positions(self):
        """Check all open positions for stop loss or take profit triggers."""
        for symbol, position in list(self.positions.items()):
            try:
                current_price = self.exchange.get_current_price(symbol)
                
                # Update unrealized PnL
                position.update_pnl(current_price)
                
                # Check if position should be closed
                close_reason = position.should_close_position(current_price)
                if close_reason:
                    self.close_position(symbol, close_reason)
                
            except Exception as e:
                logger.log_error(e, f"Failed to check position for {symbol}")
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a symbol and generate trading signals."""
        try:
            # Get historical data
            df = self.exchange.get_historical_data(symbol, '1h', 100)
            if df.empty:
                return {'symbol': symbol, 'signal': 'ERROR', 'reason': 'No data available'}
            
            # Generate trading signals
            signal_info = self.technical_analysis.generate_trading_signals(df)
            signal_info['symbol'] = symbol
            
            return signal_info
            
        except Exception as e:
            logger.log_error(e, f"Failed to analyze {symbol}")
            return {'symbol': symbol, 'signal': 'ERROR', 'reason': str(e)}
    
    def execute_strategy(self):
        """Execute the trading strategy for all configured pairs."""
        try:
            logger.logger.info("=== Starting Strategy Execution ===")
            
            # Check existing positions first
            self.check_positions()
            
            # Analyze each trading pair
            for symbol in config.TRADING_PAIRS:
                symbol = symbol.strip()
                
                # Skip if we already have a position
                if symbol in self.positions:
                    logger.logger.info(f"Skipping {symbol} - already have open position")
                    continue
                
                # Analyze symbol
                signal_info = self.analyze_symbol(symbol)
                
                if signal_info['signal'] == 'ERROR':
                    logger.logger.error(f"Analysis failed for {symbol}: {signal_info['reason']}")
                    continue
                
                # Log signal
                logger.log_trade_signal(
                    symbol,
                    signal_info['signal'],
                    signal_info.get('price', 0),
                    signal_info.get('rsi', 0),
                    signal_info.get('confidence', 0)
                )
                
                # Execute trade if signal is strong enough
                if signal_info['signal'] in ['STRONG_BUY', 'STRONG_SELL']:
                    logger.logger.info(f"Strong signal detected for {symbol}: {signal_info['reason']}")
                    self.open_position(symbol, signal_info['signal'], signal_info['price'])
                
                elif signal_info['signal'] in ['BUY', 'SELL']:
                    # Only trade medium signals if confidence is high enough
                    if signal_info.get('confidence', 0) >= 0.7:
                        logger.logger.info(f"Medium signal with high confidence for {symbol}: {signal_info['reason']}")
                        self.open_position(symbol, signal_info['signal'], signal_info['price'])
                
            # Log strategy summary
            self.log_strategy_summary()
            
        except Exception as e:
            logger.log_error(e, "Failed to execute strategy")
    
    def log_strategy_summary(self):
        """Log summary of current strategy state."""
        try:
            # Get current balance
            balance_info = self.exchange.get_account_balance()
            
            logger.logger.info("=== Strategy Summary ===")
            logger.logger.info(f"Current Balance: {balance_info.get('USDT', 0):.2f} USDT")
            logger.logger.info(f"Open Positions: {len(self.positions)}")
            logger.logger.info(f"Total Trades: {self.total_trades}")
            logger.logger.info(f"Winning Trades: {self.winning_trades}")
            logger.logger.info(f"Losing Trades: {self.losing_trades}")
            logger.logger.info(f"Total PnL: {self.total_pnl:.4f} USDT")
            
            if self.total_trades > 0:
                win_rate = (self.winning_trades / self.total_trades) * 100
                logger.logger.info(f"Win Rate: {win_rate:.1f}%")
            
            # Log open positions
            for symbol, position in self.positions.items():
                current_price = self.exchange.get_current_price(symbol)
                position.update_pnl(current_price)
                
                logger.log_position_update(
                    symbol,
                    position.amount,
                    position.unrealized_pnl,
                    position.realized_pnl
                )
            
        except Exception as e:
            logger.log_error(e, "Failed to log strategy summary")
    
    def shutdown(self):
        """Shutdown the strategy and close all positions."""
        try:
            logger.logger.info("Shutting down strategy...")
            
            # Close all open positions
            for symbol in list(self.positions.keys()):
                self.close_position(symbol, "shutdown")
            
            # Final summary
            self.log_strategy_summary()
            
            logger.log_shutdown()
            
        except Exception as e:
            logger.log_error(e, "Error during shutdown") 