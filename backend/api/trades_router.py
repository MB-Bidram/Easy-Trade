"""
Trade API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.database import Trade as TradeModel, get_db
from backend.models import TradeCreate, TradeUpdate, Trade
from backend.utils.calculations import calculate_pnl, calculate_pnl_percentage

router = APIRouter()

def add_pnl_fields(trade: TradeModel) -> dict:
    """Add calculated P&L fields to trade"""
    pnl = None
    pnl_percentage = None
    
    if trade.exit_price is not None:
        pnl = calculate_pnl(trade.entry_price, trade.exit_price, trade.quantity)
        pnl_percentage = calculate_pnl_percentage(trade.entry_price, trade.exit_price)
    
    return {
        **{key: getattr(trade, key) for key in trade.__table__.columns.keys()},
        "pnl": pnl,
        "pnl_percentage": pnl_percentage
    }

@router.post("/", response_model=Trade)
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade"""
    db_trade = TradeModel(
        ticker=trade.ticker.upper(),
        entry_price=trade.entry_price,
        quantity=trade.quantity,
        notes=trade.notes,
        entry_date=datetime.utcnow()
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return Trade(**add_pnl_fields(db_trade))

@router.get("/", response_model=List[Trade])
def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ticker: str = None,
    is_closed: bool = None,
    db: Session = Depends(get_db)
):
    """Get all trades with optional filtering"""
    query = db.query(TradeModel)
    
    if ticker:
        query = query.filter(TradeModel.ticker == ticker.upper())
    
    if is_closed is not None:
        query = query.filter(TradeModel.is_closed == is_closed)
    
    trades = query.order_by(TradeModel.entry_date.desc()).offset(skip).limit(limit).all()
    return [Trade(**add_pnl_fields(t)) for t in trades]

@router.get("/{trade_id}", response_model=Trade)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a specific trade by ID"""
    db_trade = db.query(TradeModel).filter(TradeModel.id == trade_id).first()
    
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return Trade(**add_pnl_fields(db_trade))

@router.put("/{trade_id}", response_model=Trade)
def update_trade(trade_id: int, trade_update: TradeUpdate, db: Session = Depends(get_db)):
    """Update a trade (close it with exit price)"""
    db_trade = db.query(TradeModel).filter(TradeModel.id == trade_id).first()
    
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if db_trade.is_closed:
        raise HTTPException(status_code=400, detail="Trade is already closed")
    
    if trade_update.exit_price is not None:
        db_trade.exit_price = trade_update.exit_price
        db_trade.exit_date = datetime.utcnow()
        db_trade.is_closed = True
    
    if trade_update.notes is not None:
        db_trade.notes = trade_update.notes
    
    db.commit()
    db.refresh(db_trade)
    
    return Trade(**add_pnl_fields(db_trade))

@router.delete("/{trade_id}")
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """Delete a trade"""
    db_trade = db.query(TradeModel).filter(TradeModel.id == trade_id).first()
    
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db.delete(db_trade)
    db.commit()
    
    return {"message": "Trade deleted successfully", "id": trade_id}
