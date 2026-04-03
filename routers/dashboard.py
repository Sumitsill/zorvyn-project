from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import models
import schemas
from database import get_db
from core.deps import require_any_role

router = APIRouter()

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(get_db), current_user: models.User = Depends(require_any_role)):
    income_sum = db.query(func.sum(models.FinancialRecord.amount)).filter(
        models.FinancialRecord.transaction_type == models.TransactionTypeEnum.INCOME
    ).scalar() or 0
    
    expense_sum = db.query(func.sum(models.FinancialRecord.amount)).filter(
        models.FinancialRecord.transaction_type == models.TransactionTypeEnum.EXPENSE
    ).scalar() or 0
    
    return schemas.DashboardSummary(
        total_income=float(income_sum),
        total_expenses=float(expense_sum),
        net_balance=float(income_sum - expense_sum)
    )

@router.get("/category-totals", response_model=List[schemas.CategoryTotal])
def get_category_totals(db: Session = Depends(get_db), current_user: models.User = Depends(require_any_role)):
    results = db.query(
        models.FinancialRecord.category,
        func.sum(models.FinancialRecord.amount).label("total")
    ).group_by(models.FinancialRecord.category).all()
    
    return [{"category": r.category, "total": float(r.total)} for r in results]

@router.get("/recent-activity", response_model=List[schemas.FinancialRecordResponse])
def get_recent_activity(db: Session = Depends(get_db), current_user: models.User = Depends(require_any_role)):
    records = db.query(models.FinancialRecord).order_by(
        models.FinancialRecord.created_at.desc()
    ).limit(5).all()
    return records

@router.get("/trends", response_model=List[schemas.TrendItem])
def get_trends(period_type: str = "monthly", db: Session = Depends(get_db), current_user: models.User = Depends(require_any_role)):
    # Grouping by month ('%Y-%m') or week ('%Y-%W') in SQLite
    date_format = "%Y-%m" if period_type == "monthly" else "%Y-%W"
    
    results = db.query(
        func.strftime(date_format, models.FinancialRecord.date).label("period"),
        models.FinancialRecord.transaction_type,
        func.sum(models.FinancialRecord.amount).label("total")
    ).group_by(
        "period", models.FinancialRecord.transaction_type
    ).all()
    
    trends = {}
    for r in results:
        period = r.period
        if not period:
            continue
        if period not in trends:
            trends[period] = {"period": period, "income": 0.0, "expense": 0.0}
            
        if r.transaction_type == models.TransactionTypeEnum.INCOME:
            trends[period]["income"] += float(r.total)
        else:
            trends[period]["expense"] += float(r.total)
            
    return sorted(trends.values(), key=lambda x: x["period"])
