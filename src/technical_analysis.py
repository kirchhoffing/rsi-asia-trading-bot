"""
Technical analysis module for the RSI Divergence Trading Bot.
Handles RSI calculation, divergence detection, and signal generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from ta.momentum import RSIIndicator
from scipy.signal import argrelextrema

from .config import config
from .logger import logger

class TechnicalAnalysis:
    """Technical analysis class for RSI and divergence calculations."""
    
    def __init__(self):
        self.rsi_period = config.RSI_PERIOD
        self.rsi_oversold = config.RSI_OVERSOLD
        self.rsi_overbought = config.RSI_OVERBOUGHT
        self.min_divergence_strength = config.MIN_DIVERGENCE_STRENGTH
    
    def calculate_rsi(self, df: pd.DataFrame, period: Optional[int] = None) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index) for price data.
        
        Args:
            df: DataFrame with OHLCV data
            period: RSI period (default from config)
            
        Returns:
            Series with RSI values
        """
        if period is None:
            period = self.rsi_period
        
        try:
            rsi_indicator = RSIIndicator(close=df['close'], window=period)
            rsi = rsi_indicator.rsi()
            return rsi
        except Exception as e:
            logger.log_error(e, "Failed to calculate RSI")
            return pd.Series(dtype=float)
    
    def find_price_peaks_and_valleys(self, df: pd.DataFrame, 
                                    window: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find peaks and valleys in price data.
        
        Args:
            df: DataFrame with OHLCV data
            window: Window size for peak/valley detection
            
        Returns:
            Tuple of (peak_indices, valley_indices)
        """
        try:
            prices = df['close'].values
            
            # Find peaks (local maxima)
            peaks = argrelextrema(prices, np.greater, order=window)[0]
            
            # Find valleys (local minima)
            valleys = argrelextrema(prices, np.less, order=window)[0]
            
            return peaks, valleys
            
        except Exception as e:
            logger.log_error(e, "Failed to find price peaks and valleys")
            return np.array([]), np.array([])
    
    def find_rsi_peaks_and_valleys(self, rsi: pd.Series, 
                                  window: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find peaks and valleys in RSI data.
        
        Args:
            rsi: RSI series
            window: Window size for peak/valley detection
            
        Returns:
            Tuple of (peak_indices, valley_indices)
        """
        try:
            rsi_values = rsi.values
            
            # Find peaks in RSI
            rsi_peaks = argrelextrema(rsi_values, np.greater, order=window)[0]
            
            # Find valleys in RSI
            rsi_valleys = argrelextrema(rsi_values, np.less, order=window)[0]
            
            return rsi_peaks, rsi_valleys
            
        except Exception as e:
            logger.log_error(e, "Failed to find RSI peaks and valleys")
            return np.array([]), np.array([])
    
    def detect_bullish_divergence(self, df: pd.DataFrame, rsi: pd.Series) -> Dict:
        """
        Detect bullish divergence between price and RSI.
        
        Args:
            df: DataFrame with OHLCV data
            rsi: RSI series
            
        Returns:
            Dictionary with divergence information
        """
        try:
            # Find price and RSI valleys
            price_valleys, _ = self.find_price_peaks_and_valleys(df)
            rsi_valleys, _ = self.find_rsi_peaks_and_valleys(rsi)
            
            # Need at least 2 valleys to compare
            if len(price_valleys) < 2 or len(rsi_valleys) < 2:
                return {'detected': False, 'strength': 0.0, 'message': 'Insufficient data'}
            
            # Get recent valleys (last 2)
            recent_price_valleys = price_valleys[-2:]
            recent_rsi_valleys = rsi_valleys[-2:]
            
            # Calculate price and RSI differences
            price_diff = df['close'].iloc[recent_price_valleys[1]] - df['close'].iloc[recent_price_valleys[0]]
            rsi_diff = rsi.iloc[recent_rsi_valleys[1]] - rsi.iloc[recent_rsi_valleys[0]]
            
            # Bullish divergence: price makes lower low, RSI makes higher low
            if price_diff < 0 and rsi_diff > 0:
                # Calculate divergence strength
                strength = abs(rsi_diff) / (abs(price_diff) + 1)  # Normalize
                
                if strength >= self.min_divergence_strength:
                    return {
                        'detected': True,
                        'strength': strength,
                        'message': f'Bullish divergence detected (strength: {strength:.2f})',
                        'recent_rsi': rsi.iloc[recent_rsi_valleys[1]],
                        'recent_price': df['close'].iloc[recent_price_valleys[1]]
                    }
            
            return {'detected': False, 'strength': 0.0, 'message': 'No bullish divergence'}
            
        except Exception as e:
            logger.log_error(e, "Failed to detect bullish divergence")
            return {'detected': False, 'strength': 0.0, 'message': 'Error in analysis'}
    
    def detect_bearish_divergence(self, df: pd.DataFrame, rsi: pd.Series) -> Dict:
        """
        Detect bearish divergence between price and RSI.
        
        Args:
            df: DataFrame with OHLCV data
            rsi: RSI series
            
        Returns:
            Dictionary with divergence information
        """
        try:
            # Find price and RSI peaks
            price_peaks, _ = self.find_price_peaks_and_valleys(df)
            rsi_peaks, _ = self.find_rsi_peaks_and_valleys(rsi)
            
            # Need at least 2 peaks to compare
            if len(price_peaks) < 2 or len(rsi_peaks) < 2:
                return {'detected': False, 'strength': 0.0, 'message': 'Insufficient data'}
            
            # Get recent peaks (last 2)
            recent_price_peaks = price_peaks[-2:]
            recent_rsi_peaks = rsi_peaks[-2:]
            
            # Calculate price and RSI differences
            price_diff = df['close'].iloc[recent_price_peaks[1]] - df['close'].iloc[recent_price_peaks[0]]
            rsi_diff = rsi.iloc[recent_rsi_peaks[1]] - rsi.iloc[recent_rsi_peaks[0]]
            
            # Bearish divergence: price makes higher high, RSI makes lower high
            if price_diff > 0 and rsi_diff < 0:
                # Calculate divergence strength
                strength = abs(rsi_diff) / (abs(price_diff) + 1)  # Normalize
                
                if strength >= self.min_divergence_strength:
                    return {
                        'detected': True,
                        'strength': strength,
                        'message': f'Bearish divergence detected (strength: {strength:.2f})',
                        'recent_rsi': rsi.iloc[recent_rsi_peaks[1]],
                        'recent_price': df['close'].iloc[recent_price_peaks[1]]
                    }
            
            return {'detected': False, 'strength': 0.0, 'message': 'No bearish divergence'}
            
        except Exception as e:
            logger.log_error(e, "Failed to detect bearish divergence")
            return {'detected': False, 'strength': 0.0, 'message': 'Error in analysis'}
    
    def generate_trading_signals(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signals based on RSI and divergence analysis.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with signal information
        """
        try:
            # Calculate RSI
            rsi = self.calculate_rsi(df)
            
            if rsi.empty:
                return {'signal': 'NONE', 'reason': 'RSI calculation failed'}
            
            current_rsi = rsi.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Check for divergences
            bullish_div = self.detect_bullish_divergence(df, rsi)
            bearish_div = self.detect_bearish_divergence(df, rsi)
            
            # Generate signals
            signal_info = {
                'signal': 'NONE',
                'reason': 'No clear signal',
                'rsi': current_rsi,
                'price': current_price,
                'bullish_divergence': bullish_div,
                'bearish_divergence': bearish_div,
                'timestamp': df.index[-1]
            }
            
            # Strong buy signal: RSI oversold + bullish divergence
            if current_rsi <= self.rsi_oversold and bullish_div['detected']:
                signal_info.update({
                    'signal': 'STRONG_BUY',
                    'reason': f'RSI oversold ({current_rsi:.2f}) + Bullish divergence ({bullish_div["strength"]:.2f})',
                    'confidence': min(0.9, 0.5 + bullish_div['strength'])
                })
            
            # Strong sell signal: RSI overbought + bearish divergence
            elif current_rsi >= self.rsi_overbought and bearish_div['detected']:
                signal_info.update({
                    'signal': 'STRONG_SELL',
                    'reason': f'RSI overbought ({current_rsi:.2f}) + Bearish divergence ({bearish_div["strength"]:.2f})',
                    'confidence': min(0.9, 0.5 + bearish_div['strength'])
                })
            
            # Medium buy signal: RSI oversold only
            elif current_rsi <= self.rsi_oversold:
                signal_info.update({
                    'signal': 'BUY',
                    'reason': f'RSI oversold ({current_rsi:.2f})',
                    'confidence': 0.6
                })
            
            # Medium sell signal: RSI overbought only
            elif current_rsi >= self.rsi_overbought:
                signal_info.update({
                    'signal': 'SELL',
                    'reason': f'RSI overbought ({current_rsi:.2f})',
                    'confidence': 0.6
                })
            
            # Weak signals: divergence only
            elif bullish_div['detected']:
                signal_info.update({
                    'signal': 'WEAK_BUY',
                    'reason': f'Bullish divergence ({bullish_div["strength"]:.2f})',
                    'confidence': 0.4
                })
            
            elif bearish_div['detected']:
                signal_info.update({
                    'signal': 'WEAK_SELL',
                    'reason': f'Bearish divergence ({bearish_div["strength"]:.2f})',
                    'confidence': 0.4
                })
            
            return signal_info
            
        except Exception as e:
            logger.log_error(e, "Failed to generate trading signals")
            return {'signal': 'ERROR', 'reason': 'Signal generation failed'}
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """
        Calculate support and resistance levels.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with support/resistance levels
        """
        try:
            # Find peaks and valleys
            peaks, valleys = self.find_price_peaks_and_valleys(df)
            
            if len(peaks) > 0 and len(valleys) > 0:
                # Calculate resistance (average of recent peaks)
                recent_peaks = peaks[-min(3, len(peaks)):]
                resistance = df['close'].iloc[recent_peaks].mean()
                
                # Calculate support (average of recent valleys)
                recent_valleys = valleys[-min(3, len(valleys)):]
                support = df['close'].iloc[recent_valleys].mean()
                
                return {
                    'support': support,
                    'resistance': resistance,
                    'current_price': df['close'].iloc[-1]
                }
            
            return {
                'support': df['close'].min(),
                'resistance': df['close'].max(),
                'current_price': df['close'].iloc[-1]
            }
            
        except Exception as e:
            logger.log_error(e, "Failed to calculate support/resistance")
            return {'support': 0, 'resistance': 0, 'current_price': 0} 