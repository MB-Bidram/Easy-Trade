"""
Calculation utilities for P&L and trading statistics
"""

from typing import List, Tuple, Optional
from backend.utils.helpers import round_to_decimals


def calculate_pnl(entry_price: float, exit_price: float, quantity: float) -> float:
    """
    Calculate profit/loss in currency units.
    
    Args:
        entry_price: Entry price per unit
        exit_price: Exit price per unit
        quantity: Number of units
    
    Returns:
        P&L value (positive for profit, negative for loss)
    """
    if entry_price <= 0 or quantity <= 0:
        return 0.0
    
    return round_to_decimals((exit_price - entry_price) * quantity)


def calculate_pnl_percentage(entry_price: float, exit_price: float) -> float:
    """
    Calculate profit/loss as percentage.
    
    Args:
        entry_price: Entry price per unit
        exit_price: Exit price per unit
    
    Returns:
        P&L percentage
    """
    if entry_price <= 0:
        return 0.0
    
    percentage = ((exit_price - entry_price) / entry_price) * 100
    return round_to_decimals(percentage)


def is_winning_trade(entry_price: float, exit_price: float) -> bool:
    """
    Determine if trade is profitable.
    """
    return exit_price > entry_price


def calculate_win_rate(winning_trades: int, total_trades: int) -> float:
    """
    Calculate win rate percentage.
    
    Returns:
        Win rate as percentage (0-100)
    """
    if total_trades <= 0:
        return 0.0
    
    return round_to_decimals((winning_trades / total_trades) * 100)


def calculate_average_win_loss(trades: List[dict]) -> Tuple[float, float]:
    """
    Calculate average win and average loss from trades.
    
    Args:
        trades: List of trade dictionaries with 'pnl' key
    
    Returns:
        Tuple of (average_win, average_loss)
    """
    wins = [t['pnl'] for t in trades if t.get('pnl', 0) > 0]
    losses = [t['pnl'] for t in trades if t.get('pnl', 0) < 0]
    
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    
    return round_to_decimals(avg_win), round_to_decimals(avg_loss)


def calculate_profit_factor(wins: List[float], losses: List[float]) -> float:
    """
    Calculate profit factor (sum of wins / abs(sum of losses)).
    
    Returns:
        Profit factor value
    """
    total_wins = sum(wins) if wins else 0
    total_losses = abs(sum(losses)) if losses else 1  # Avoid division by zero
    
    if total_losses == 0:
        return 0.0
    
    return round_to_decimals(total_wins / total_losses)


def calculate_expectancy(
    average_win: float,
    average_loss: float,
    win_rate: float
) -> float:
    """
    Calculate trade expectancy.
    
    Formula: (avg_win * win_rate) - (avg_loss * loss_rate)
    
    Returns:
        Expected value per trade
    """
    if win_rate < 0 or win_rate > 100:
        return 0.0
    
    win_rate_decimal = win_rate / 100
    loss_rate_decimal = 1 - win_rate_decimal
    
    expectancy = (average_win * win_rate_decimal) - (abs(average_loss) * loss_rate_decimal)
    return round_to_decimals(expectancy)


def calculate_risk_reward_ratio(average_win: float, average_loss: float) -> float:
    """
    Calculate risk/reward ratio.
    
    Returns:
        Risk/reward ratio (win:loss)
    """
    if average_loss == 0:
        return 0.0
    
    return round_to_decimals(abs(average_win / average_loss))


def calculate_drawdown(peak_value: float, trough_value: float) -> float:
    """
    Calculate drawdown from peak to trough.
    
    Returns:
        Drawdown percentage
    """
    if peak_value <= 0:
        return 0.0
    
    drawdown = ((trough_value - peak_value) / peak_value) * 100
    return round_to_decimals(drawdown)


def calculate_recovery_factor(
    total_profit: float,
    max_drawdown: float
) -> float:
    """
    Calculate recovery factor (profit / max_drawdown).
    
    Returns:
        Recovery factor value
    """
    if max_drawdown == 0:
        return 0.0
    
    return round_to_decimals(total_profit / abs(max_drawdown))
