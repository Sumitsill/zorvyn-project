from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import models
import schemas
from database import get_db
from core.deps import require_admin, require_analyst_or_admin

router = APIRouter()

@router.post("/", response_model=schemas.FinancialRecordResponse)
def create_record(
    record_in: schemas.FinancialRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    db_record = models.FinancialRecord(
        user_id=current_user.id,
        amount=record_in.amount,
        transaction_type=record_in.transaction_type,
        category=record_in.category,
        date=record_in.date,
        description=record_in.description
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=schemas.PaginatedRecords)
def get_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    type: Optional[models.TransactionTypeEnum] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analyst_or_admin)
):
    query = db.query(models.FinancialRecord)
    
    if start_date:
        query = query.filter(models.FinancialRecord.date >= start_date)
    if end_date:
        query = query.filter(models.FinancialRecord.date <= end_date)
    if category:
        query = query.filter(models.FinancialRecord.category == category)
    if type:
        query = query.filter(models.FinancialRecord.transaction_type == type)
        
    total = query.count()
    records = query.order_by(models.FinancialRecord.date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return schemas.PaginatedRecords(
        total=total,
        page=page,
        limit=limit,
        data=records
    )

@router.get("/{id}", response_model=schemas.FinancialRecordResponse)
def get_record(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analyst_or_admin)
):
    record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.put("/{id}", response_model=schemas.FinancialRecordResponse)
def update_record(
    id: str,
    record_in: schemas.FinancialRecordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    update_data = record_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
        
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    db.delete(record)
    db.commit()
    return None
