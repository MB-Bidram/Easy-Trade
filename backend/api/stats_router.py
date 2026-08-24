"""
Statistics API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.database import Trade as TradeModel, get_db
from backend.models import StatsResponse, MonthlyStats
from backend.utils.calculations import calculate_pnl, calculate_pnl_percentage, is_winning_trade
from backend.utils.helpers import calculate_average, round_to_decimals, get_month_string

router = APIRouter()

@router.get("/summary", response_model=StatsResponse)
def get_stats_summary(db: Session = Depends(get_db)):
    """Get overall trading statistics"""
    trades = db.query(TradeModel).all()
    closed_trades = [t for t in trades if t.is_closed]
    open_trades = [t for t in trades if not t.is_closed]
    
    # Calculate P&L metrics
    total_pnl = 0
    total_value = 0
    wins = []
    losses = []
    
    for trade in closed_trades:
        pnl = calculate_pnl(trade.entry_price, trade.exit_price, trade.quantity)
        total_pnl += pnl
        total_value += abs(pnl)
        
        if is_winning_trade(trade.entry_price, trade.exit_price):
            wins.append(pnl)
        else:
            losses.append(pnl)
    
    # Calculate statistics
    winning_trades = len(wins)
    losing_trades = len(losses)
    total_trades = len(trades)
    closed_count = len(closed_trades)
    
    win_rate = (winning_trades / closed_count * 100) if closed_count > 0 else 0
    average_win = calculate_average(wins) if wins else 0
    average_loss = calculate_average(losses) if losses else 0
    largest_win = max(wins) if wins else 0
    largest_loss = min(losses) if losses else 0
    
    # Calculate total P&L percentage
    total_invested = sum(t.entry_price * t.quantity for t in closed_trades)
    total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    return StatsResponse(
        total_trades=total_trades,
        closed_trades=closed_count,
        open_trades=len(open_trades),
        total_pnl=round_to_decimals(total_pnl),
        total_pnl_percentage=round_to_decimals(total_pnl_percentage),
        win_rate=round_to_decimals(win_rate),
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        average_win=round_to_decimals(average_win),
        average_loss=round_to_decimals(average_loss),
        largest_win=round_to_decimals(largest_win),
        largest_loss=round_to_decimals(largest_loss)
    )

@router.get("/monthly", response_model=List[MonthlyStats])
def get_monthly_stats(db: Session = Depends(get_db)):
    """Get monthly trading statistics"""
    trades = db.query(TradeModel).all()
    closed_trades = [t for t in trades if t.is_closed]
    
    # Group by month
    monthly_data = {}
    
    for trade in closed_trades:
        month = get_month_string(trade.entry_date)
        
        if month not in monthly_data:
            monthly_data[month] = {
                "trades": [],
                "wins": 0,
                "total_trades": 0
            }
        
        pnl = calculate_pnl(trade.entry_price, trade.exit_price, trade.quantity)
        monthly_data[month]["trades"].append(pnl)
        monthly_data[month]["total_trades"] += 1
        
        if is_winning_trade(trade.entry_price, trade.exit_price):
            monthly_data[month]["wins"] += 1
    
    # Format response
    result = []
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        monthly_pnl = sum(data["trades"])
        win_rate = (data["wins"] / data["total_trades"] * 100) if data["total_trades"] > 0 else 0
        
        result.append(MonthlyStats(
            month=month,
            trades_count=data["total_trades"],
            pnl=round_to_decimals(monthly_pnl),
            win_rate=round_to_decimals(win_rate)
        ))
    
    return result

@router.get("/performance")
def get_performance_metrics(db: Session = Depends(get_db)):
    """Get detailed performance metrics"""
    stats = get_stats_summary(db)
    
    return {
        "summary": stats,
        "metrics": {
            "profit_factor": round_to_decimals(
                abs(sum([stats.average_win * stats.winning_trades]) / 
                    (sum([stats.average_loss * stats.losing_trades]) or 1))
            ),
            "expectancy": round_to_decimals(
                (stats.average_win * (stats.win_rate / 100)) - 
                (abs(stats.average_loss) * ((100 - stats.win_rate) / 100))
            ) if stats.closed_trades > 0 else 0,
            "risk_reward_ratio": round_to_decimals(
                abs(stats.average_win / stats.average_loss) if stats.average_loss != 0 else 0
            )
        }
    }
